from PIL import ImageGrab
import pygetwindow as gw
import time
import os

import threading
import playutils
import globals
import tensorflow as tf
import numpy as np

from globals import logging as log

import win32api
import win32con

from states.hit_enemy import state_hit_enemy
from states.horizont import state_horizont
from states.road import state_road
from states.horizont import state_horizont

params = {    
    "nnsize" : 256
}

prev_time = 0
prev_time_state = 0
prev_time_road = 0
prev_time_turn = 0
prev_time_nocheck = 0

script_directory = os.path.dirname(__file__)

model = playutils.load_model_safe(os.path.join(script_directory, "follow_road.h5"))

state = "normal"

nnresult = 0

playback_current = ""
playback_recordings = []

action_lines = ""
current_action_index = 0

stop_check_road_state_thread = False
lock = threading.Lock()

def reset_timers():
    global prev_time
    prev_time = time.time()

    global prev_time_state
    prev_time_state = time.time()
    
    global prev_time_turn
    prev_time_turn = time.time()  

    global prev_time_nocheck
    prev_time_nocheck = time.time()

def on_transit_in():    
    global current_action_index, action_lines, playback_current
    current_action_index = 0
    action_lines, playback_current = playutils.load_playback(playback_recordings, playback_current)

    global prev_time_road
    prev_time_road = time.time() 

    reset_timers()

    global stop_check_road_state_thread
    stop_check_road_state_thread = False

    global nnresult
    nnresult = 0

    global is_trainsitin_thread
    is_trainsitin_thread = threading.Thread(target=check_road_state)
            
    is_trainsitin_thread.start()

def on_stop():
    global stop_check_road_state_thread
    stop_check_road_state_thread = True

    global is_trainsitin_thread
    is_trainsitin_thread.join()

    log.info(os.path.basename(__file__) + " stopped")
    
def is_trainsitin():    
    
    window = gw.getWindowsWithTitle('Skyrim')[0]
    winRect = [window.left+2, window.top+2, window.right-2, window.bottom-2]

    img = ImageGrab.grab(winRect)

    if 'grabsize' in params:
        crop_area = (params['posx'], params['posy'], params['posx'] + params['grabsize'], params['posy'] + params['grabsize'])
        cropped_img = img.crop(crop_area)
        resize = tf.image.resize(np.array(cropped_img), (params['nnsize'], params['nnsize']))
    else:
        resize = tf.image.resize(np.array(img), (256,256))

    np.expand_dims(resize,0)

    # print('Start ' + str(round(time.time() * 1000)))        
    yhat = model.predict(np.expand_dims(resize/255,0), verbose = 0)        
    # print('End ' + str(round(time.time() * 1000)))

    res = yhat[0]        
    ind = np.argmax(res)

    global nnresult
    nnresult = ind
    
    log.info(f"Follow road {ind} {time.time()}")

    return ind == 1 or ind == 2

def check_road_state():
    global stop_check_road_state_thread
    while not stop_check_road_state_thread:
        is_trainsitin()
        time.sleep(0.001)

is_trainsitin_thread = threading.Thread(target=check_road_state)

def start():
    global playback_recordings, playback_current, action_lines
    
    playback_recordings = playutils.initialize_playbacks(script_directory)
    action_lines, playback_current = playutils.load_playback(playback_recordings, playback_current)

def set_state(in_state):
    global state
    state = in_state

    global current_action_index
    current_action_index = 0

    playutils.keys_up()

    reset_timers()

def process_playback():
    global action_lines, current_action_index, prev_time, playback_current

    if current_action_index < (len(action_lines) - 1):
        current_action = action_lines[current_action_index]
        playutils.process_action(current_action) 

        current_action_index += 1
    else:
        action_lines, playback_current = playutils.load_playback(playback_recordings, playback_current)
        print(playback_current)
        current_action_index = 0
        playutils.keys_up()

def process_walk_state():
    global prev_time_road

    elapsed_time_road = time.time() - prev_time_road
    if elapsed_time_road > 3:
        prev_time_road = time.time()

        if not state_road.is_trainsitin():
            globals.CURRENT_STATE = "walk"
            return

def update():
    
    global prev_time, prev_time_state, state, nnresult, prev_time_nocheck

    if state == "normal":

        process_playback()
        
        elapsed_time_nocheck = time.time() - prev_time_nocheck
        if elapsed_time_nocheck > 1:

            elapsed_time = time.time() - prev_time_state
            if elapsed_time > 0.05:
                prev_time_state = time.time()                
                res = nnresult                                    
                if res == 1:
                    log.debug("Transit turn left")
                    set_state("turn_left")
                    return
                elif res == 2:
                    log.debug("Transit turn right")
                    set_state("turn_right")
                    return
                
            process_walk_state()
                
        state_horizont.update()

    elif state == "turn_left":
                
        win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, -5, 0)
        time.sleep(0.01)

        elapsed_time_state = time.time() - prev_time_state
        if elapsed_time_state > 0.05:
            prev_time_state = time.time()            
            
            res = nnresult                                    
            if res == 0:
                log.debug("Transit Move forward state")
                set_state("normal")
            elif res == 2:
                set_state("turn_right")

        process_walk_state()

        state_horizont.update()

    elif state == "turn_right":
        
        win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 5, 0)
        time.sleep(0.01)

        elapsed_time_state = time.time() - prev_time_state
        if elapsed_time_state > 0.05:
            prev_time_state = time.time()            
            
            res = nnresult                                    
            if res == 0:
                log.debug("Transit move forward state")
                set_state("normal")
            elif res == 1:
                set_state("turn_left")
                
        process_walk_state()

        state_horizont.update()


       