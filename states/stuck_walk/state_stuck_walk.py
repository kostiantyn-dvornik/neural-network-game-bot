import time
import os

import globals
import playutils
from states.horizont import state_horizont

params = {        
}

prev_time = 0

script_dir = os.path.dirname(os.path.realpath(__file__))

playback_current = ""
playback_recordings = []

action_lines = ""
current_action_index = 0

def on_transit_in():
    global prev_time, current_action_index, action_lines, playback_current    
    prev_time = time.time()
    current_action_index = 0
    action_lines, playback_current = playutils.load_playback(playback_recordings, playback_current)

def on_stop():
    print(os.path.basename(__file__) + " stopped")

def is_transit_in():
    return False
    
def start():
    global playback_recordings    
    playback_recordings = playutils.initialize_playbacks(script_dir)
    on_transit_in()

def process_playback():
    global action_lines, current_action_index, prev_time, playback_current

    if current_action_index < (len(action_lines) - 1):
        current_action = action_lines[current_action_index]
        playutils.process_action(current_action) 

        current_action_index += 1
    else:
        globals.CURRENT_STATE = "walk"
        

def update():
    process_playback()

    state_horizont.update()               