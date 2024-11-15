import pydirectinput
import time
import win32api
import win32con
import os
import random
from tensorflow.keras.models import load_model

keys  = ["d", "z", "a", "w", "s", "space", "alt", "e", "c", "f", "q", "esc", "enter", "`", "b", "t", "n"]

def keys_up():    
    for key in keys:
        pydirectinput.keyUp(key)

    pydirectinput.mouseUp(button="left")
    pydirectinput.mouseUp(button="right")

def process_sleep(action):    
    delay = float(action.split()[1])        
    time.sleep(delay)

def process_mousemove(action):
    
    splits = action.split()
    
    x_offset = int(splits[1])
    y_offset = int(splits[2])

    #print(str(x_offset) + " " + str(y_offset))
    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, x_offset, y_offset)

def process_keyboard(action):

    split = action.split()

    key = split[1]
    state = split[2]

    if "True" in state:
        pydirectinput.keyDown(key)
    else:
        pydirectinput.keyUp(key)

def process_mouse_button(action):
        
    split = action.split()

    mouse_button = split[1]
    state = split[2]

    if "True" in state:
        pydirectinput.mouseDown(button=mouse_button)
    else:
        pydirectinput.mouseUp(button=mouse_button)

def process_action(action):    
    if "wait" in action:        
        process_sleep(action)

    if "mouse_move" in action:
        process_mousemove(action)

    if "key_state" in action:
        process_keyboard(action)

    if "mouse_button_state" in action:
        process_mouse_button(action)
              
#states
def initialize_playbacks(script_directory):

    playback_recordings = []

    for file_name in os.listdir(script_directory):
        file_path = os.path.join(script_directory, file_name)
        if os.path.isfile(file_path):
            file_name, file_extension = os.path.splitext(file_name)
            if file_extension == ".gamerec":
                playback_recordings.append(file_path)

    return playback_recordings

def load_playback(playback_recordings, playback_current):    
    
    rnd_index = random.randint(0, len(playback_recordings) - 1)
    
    action_lines = []
    
    playback_current = playback_recordings[rnd_index]

    with open(playback_current, 'r') as file:
        action_lines = file.readlines()

    # Remove newline characters from each line
    action_lines = [line.strip() for line in action_lines]
    
    return action_lines, playback_current

def load_model_safe(path):
    if os.path.exists(path):
        return load_model(path)
    else:
        return None