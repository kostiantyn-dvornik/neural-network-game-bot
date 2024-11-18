import time
import os
import playutils

import globals
from states.find_enemy import state_find_enemy
from states.horizont import state_horizont
from states.stuck import state_stuck
from states.road import state_road
from states.reset import state_reset

params = {
    
}

prev_time = time.time()

script_directory = os.path.dirname(__file__)

playback_current = ""
playback_recordings = []

action_lines = ""
current_action_index = 0

def on_transit_in():
    global current_action_index, action_lines, playback_current
    current_action_index = 0
    action_lines, playback_current = playutils.load_playback(playback_recordings, playback_current)

def on_stop():
    print(os.path.basename(__file__) + " stopped")

def start():  
    global playback_recordings, playback_current, action_lines
    
    playback_recordings = playutils.initialize_playbacks(script_directory)
    action_lines, playback_current = playutils.load_playback(playback_recordings, playback_current)
    
    state_horizont.start()

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
        
        if state_find_enemy.is_trainsitin():            
            globals.CURRENT_STATE = "find_enemy"
            playutils.keys_up()
            return
        
        if state_stuck.is_trainsitin():            
            globals.CURRENT_STATE = "stuck"
            playutils.keys_up()
            return
        
        if state_road.is_trainsitin():            
            globals.CURRENT_STATE = "follow_road"
            playutils.keys_up()
            return
        
        if state_reset.is_trainsitin():            
            globals.CURRENT_STATE = "reset"
            playutils.keys_up()
            return
        
        prev_time = time.time()

def update():    
    
    process_playback()

    process_transitions()

    state_horizont.update()    
    
    