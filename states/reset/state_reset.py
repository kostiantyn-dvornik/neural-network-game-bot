import time
import os
import globals
import playutils

params = {    
    
}

prev_time = 0

script_dir = os.path.dirname(os.path.realpath(__file__))

playback_current = ""
playback_recordings = []

action_lines = ""
current_action_index = 0

def on_transit_in():
    global current_action_index, action_lines, playback_current, prev_time
    current_action_index = 0
    action_lines, playback_current = playutils.load_playback(playback_recordings, playback_current)
    prev_time = time.time()

def on_stop():
    print(os.path.basename(__file__) + " stopped")

def start():
    global playback_recordings, playback_current, action_lines
    
    playback_recordings = playutils.initialize_playbacks(script_dir)
    action_lines, playback_current = playutils.load_playback(playback_recordings, playback_current)

    global prev_time
    prev_time = time.time()
           
def is_transit_in():
    if time.time() - prev_time > 5 * 60:
        return True
    else:
        return False

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