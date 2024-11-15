import sys
import os
script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))

global_dir = os.path.join(script_dir, "..")
sys.path.append(global_dir)

import time
import keyboard
from datetime import datetime

import pygetwindow as gw
import tensorflow as tf
import numpy as np
import playutils
import sys
from PIL import ImageGrab

execution_period = 1

#[use]
state = "road"

state_dir = os.path.join(script_dir, "..", "states", state)
sys.path.append(state_dir)

#[gen]
import state_road as st

params = st.params

nnsize = params.get('nnsize', 256)
nn_outputs = 0
posx = params.get('posx', 0)
posy = params.get('posy', 0)
grabsize = params.get('grabsize', 0)

model_path = ""

previous_NNTime = time.time()

user_folder = os.path.expanduser("~")
savedfiles_count = 0

def set_nn_params():
    global model_path

    for file_name in os.listdir(state_dir):

        if ".h5" in file_name:            
            model_path = os.path.join(state_dir, file_name)                        
            print(file_name) 
            break
                                                                                            
def stop():
    if keyboard.is_pressed("f4"):
        print("Stopped")            
        sys.exit()

def process_NN():
    window = gw.getWindowsWithTitle('Skyrim')[0]

    # Get the window position and size
    print(f"Window '{window.title}' Position: {window.topleft}, Size: {window.size}")

    winRect = [window.left+2, window.top+2, window.right-2, window.bottom-2]

    if grabsize != 0:
        winRect[0] += posx
        winRect[1] += posy
        winRect[2] = winRect[0] + grabsize
        winRect[3] = winRect[1] + grabsize

    img = ImageGrab.grab(winRect)

    #img.show()

    resize = tf.image.resize(np.array(img), (nnsize, nnsize))        
    
    np.expand_dims(resize,0)

    # print('Start ' + str(round(time.time() * 1000)))        
    yhat = new_model.predict(np.expand_dims(resize/255,0))        
    # print('End ' + str(round(time.time() * 1000)))

    print(yhat)

    res = yhat[0]        
    ind = np.argmax(res)
                
    print('Result ' + str(ind))

    current_datetime = datetime.now()
    current_datetime_filename = current_datetime.strftime("%Y%m%d_%H%M%S")

    img.save( user_folder + "/Videos/Captures/" + str(ind) + "/" + str(current_datetime_filename) + ".png" )

    savedfiles_count =+ 1

    if savedfiles_count > 100:
        print("Saved files limit reached")
        sys.exit()


def update():
    global previous_NNTime
    
    stop()

    elapsed_time = time.time() - previous_NNTime
    if elapsed_time > execution_period:
        previous_NNTime = time.time()
        process_NN()

def main():        
    while True:
        update()

#Main flow
set_nn_params()

# Create the directory if it doesn't exist
os.makedirs(user_folder + "/Videos/Captures/0", exist_ok=True)
os.makedirs(user_folder + "/Videos/Captures/1", exist_ok=True)
os.makedirs(user_folder + "/Videos/Captures/2", exist_ok=True)

print("Loading model...")
new_model = playutils.load_model_safe(model_path)

print("Press ENTER to start")
keyboard.wait("enter")
print("Started. Press F4 to stop")
main()