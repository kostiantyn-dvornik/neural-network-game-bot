from PIL import ImageGrab
import pygetwindow as gw
import time
import os

import globals
import playutils
import tensorflow as tf
import numpy as np

params = {
    "posx" : 464,
    "posy" : 149,
    "grabsize" : 512,
    "nnsize" : 128
}

prev_general_time = time.time()
prev_time = time.time()

script_directory = os.path.dirname(__file__)

model = playutils.load_model_safe(os.path.join(script_directory, "hit_enemy.h5"))

#
playback_current = ""
playback_recordings = []

action_lines = ""
current_action_index = 0

def on_transit_in():
    global current_action_index
    current_action_index = 0

    global prev_time
    prev_time = time.time()

    global prev_general_time
    prev_general_time = time.time()

def on_stop():
    print(os.path.basename(__file__) + " stopped")

def start():    
    global playback_recordings, playback_current, action_lines
    
    playback_recordings = playutils.initialize_playbacks(script_directory)
    action_lines, playback_current = playutils.load_playback(playback_recordings, playback_current)


def is_trainsitin():

    window = gw.getWindowsWithTitle('Skyrim')[0]
    winRect = [window.left+2, window.top+2, window.right-2, window.bottom-2]

    img = ImageGrab.grab(winRect)

    if 'grabsize' in params:
        crop_area = (params['posx'], params['posy'], params['posx'] + params['grabsize'], params['posy'] + params['grabsize'])
        cropped_img = img.crop(crop_area)
        #cropped_img.show()
        resize = tf.image.resize(np.array(cropped_img), (params['nnsize'], params['nnsize']))
    else:
        resize = tf.image.resize(np.array(img), (256,256))

    np.expand_dims(resize,0)

    # print('Start ' + str(round(time.time() * 1000)))        
    yhat = model.predict(np.expand_dims(resize/255,0), verbose = 0)        
    # print('End ' + str(round(time.time() * 1000)))

    # print(yhat)

    res = yhat[0]        
    ind = np.argmax(res)

    print("Hit enemy " + str(ind))

    return ind == 1

def process_playback():
    global action_lines, current_action_index, prev_time

    if current_action_index < (len(action_lines) - 1):
        current_action = action_lines[current_action_index]
        playutils.process_action(current_action) 

        current_action_index += 1
    else:
        current_action_index = 0
        playutils.keys_up()

def update():
        
    process_playback()

    global prev_time
    elapsed_time = time.time() - prev_time
    if elapsed_time > 10:
        if  not is_trainsitin():
            globals.CURRENT_STATE = "find_enemy"
            playutils.keys_up()
            
        prev_time = time.time()

    global prev_general_time
    elapsed_general_time = time.time() - prev_general_time
    if elapsed_general_time > 20:      
        globals.CURRENT_STATE = "walk"
        playutils.keys_up()
            
        prev_general_time = time.time()