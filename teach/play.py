import sys
import os
script_directory = os.path.dirname(os.path.abspath(sys.argv[0]))

global_dir = os.path.join(script_directory, "..")
sys.path.append(global_dir)

import pydirectinput
import keyboard
import playutils

current_actionindex = 0

def stop_script():
    if keyboard.is_pressed("f4"):
        print("Stopped")        
        playutils.keys_up()    
        sys.exit()

def process_record(actions):                    
    for i in range(len(actions)):        
        stop_script()

        current_action = actions[i]

        playutils.process_action(current_action)  

def main():            
    playback_current = os.path.join(script_directory,"state_test_1.gamerec")
    
    with open(playback_current, 'r') as file:
        lines = file.readlines()

    # Remove newline characters from each line
    lines = [line.strip() for line in lines]

    print("Readed")
    process_record(lines)
                        
# Disable the fail-safe feature
pydirectinput.FAILSAFE = False

print("Press ENTER to start")
keyboard.wait("enter")
print("Started. Press F4 to stop")
main()
print("Completed")