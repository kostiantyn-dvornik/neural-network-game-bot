import time
import os
import playutils

import globals
import threading

from globals import logging as log

from states.find_enemy import state_find_enemy
from states.horizont import state_horizont
from states.stuck import state_stuck
from states.road import state_road
from states.reset import state_reset

params = {
    
}

prev_time = time.time()

script_dir = os.path.dirname(os.path.realpath(__file__))

playback_current = ""
playback_recordings = []

action_lines = ""
current_action_index = 0

def on_transit_in():
    global current_action_index, action_lines, playback_current
    current_action_index = 0
    action_lines, playback_current = playutils.load_playback(playback_recordings, playback_current)

    #
    global stop_playback_thread_func
    stop_playback_thread_func = False
    
    global pause_playback_thread_func
    pause_playback_thread_func = False

    global playback_thread
    playback_thread = threading.Thread(target=playback_thread_func, daemon=True)
    playback_thread.start() 

def on_stop():

    #
    global stop_playback_thread_func
    stop_playback_thread_func = True

    global pause_playback_thread_func
    pause_playback_thread_func = True

    playutils.keys_up()

    global playback_thread
    playback_thread.join()

    log.info(os.path.basename(__file__) + " stopped")    

def start():  
    global playback_recordings, playback_current, action_lines
    
    playback_recordings = playutils.initialize_playbacks(script_dir)
    action_lines, playback_current = playutils.load_playback(playback_recordings, playback_current)

stop_playback_thread_func = False
pause_playback_thread_func = False
def playback_thread_func():
    global stop_playback_thread_func
    while not stop_playback_thread_func:
        global pause_playback_thread_func
        if not pause_playback_thread_func:                
            process_playback()
        else:
            playutils.keys_up()
        # time.sleep(0.0001)

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

def process_transitions():
    global prev_time
    elapsed_time = time.time() - prev_time
    if elapsed_time > 1:        
        
        if state_find_enemy.is_transit_in():            
            globals.CURRENT_STATE = "find_enemy"
            playutils.keys_up()
            return
        
        if state_stuck.is_transit_in():            
            globals.CURRENT_STATE = "stuck"
            playutils.keys_up()
            return
        
        if state_road.is_transit_in():            
            globals.CURRENT_STATE = "follow_road"
            playutils.keys_up()
            return
        
        if state_reset.is_transit_in():            
            globals.CURRENT_STATE = "reset"
            playutils.keys_up()
            return
        
        prev_time = time.time()

def update():    

    process_transitions()

    state_horizont.update()    
    
    