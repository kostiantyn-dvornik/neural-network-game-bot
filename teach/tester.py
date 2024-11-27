import os
import sys
script_dir = os.path.dirname(os.path.realpath(__file__))
global_dir = os.path.join(script_dir, "..")
sys.path.append(global_dir)

import time
import keyboard
import pygetwindow as gw
import tensorflow as tf
import numpy as np
import playutils
from PIL import ImageGrab

#[use]
state = "road"

script_directory = os.path.dirname(os.path.abspath(sys.argv[0]))
state_dir = os.path.join(script_directory, "..", "States", state)
sys.path.append(state_dir)

global_dir = os.path.join(script_directory, "..")
sys.path.append(global_dir)

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

execution_period = 1 

def set_global_params():
    global model_path

    for file_name in os.listdir(state_dir):

        if ".h5" in file_name:            
            model_path = os.path.join(state_dir, file_name)                        
            print(file_name) 
            break
                                                                                            
def stop_script():
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
    yhat = new_model.predict(np.expand_dims(resize/255,0), verbose = 1)        
    # print('End ' + str(round(time.time() * 1000)))

    print(yhat)

    res = yhat[0]        
    ind = np.argmax(res)
                
    print('Result ' + str(ind))    

def update():
    global previous_NNTime
    
    stop_script()

    elapsed_time = time.time() - previous_NNTime
    if elapsed_time > execution_period:
        previous_NNTime = time.time()
        process_NN()

def main():        
    while True:
        update()

#Main flow
set_global_params()
print("Loading model...")
new_model = playutils.load_model_safe(model_path)

print("Press ENTER to start")
keyboard.wait("enter")
print("Started. Press F4 to stop")
main()