from PIL import ImageGrab
import pygetwindow as gw
import time
import os

import tensorflow as tf
import numpy as np
import playutils

import win32api
import win32con

params = {    
    "nnsize" : 256
}

prev_time = 0

script_directory = os.path.dirname(__file__)

model = playutils.load_model_safe(os.path.join(script_directory, "horizont.h5"))

prev_time_move = 0

state = "normal"
nnresult = 0

def on_transit_in():
    global prev_time, prev_time_move
    prev_time = time.time()
    prev_time_move = time.time()

def on_stop():
    print(os.path.basename(__file__) + " stopped")

def start():
    on_transit_in()
           
def set_state(current_state):
    global state, prev_time, prev_time_move

    state = current_state
    prev_time = time.time()
    prev_time_move = time.time()

def is_trainsitin():
    window = gw.getWindowsWithTitle('Skyrim')[0]
    winRect = [window.left+2, window.top+2, window.right-2, window.bottom-2]

    img = ImageGrab.grab(winRect)

    if 'grabsize' in params:
        crop_area = (params['posx'], params['posy'], params['posx'] + params['grabsize'], params['posy'] + params['grabsize'])
        cropped_img = img.crop(crop_area)
        #cropped_img.show()
        resize = tf.image.resize(np.array(cropped_img), (params['nnsize'],params['nnsize']))
    else:
        resize = tf.image.resize(np.array(img), (256,256))

    np.expand_dims(resize,0)

    # print('Start ' + str(round(time.time() * 1000)))        
    yhat = model.predict(np.expand_dims(resize/255,0), verbose = 0)        
    # print('End ' + str(round(time.time() * 1000)))

    # print(yhat)

    res = yhat[0]        
    ind = np.argmax(res)

    print('Horizont ' + str(ind))

    global nnresult
    nnresult = ind
    
    return ind == 1 or ind == 2

def update():
    global prev_time, prev_time_move, nnresult

    if state == "normal":
        elapsed_time = time.time() - prev_time
        if elapsed_time > 2:
            prev_time = time.time()
            
            is_trainsitin()

            if nnresult == 1:
                set_state("up")
            elif nnresult == 2:
                set_state("down")
            
    elif state == "up":        
        elapsed_time_move = time.time() - prev_time_move
        if elapsed_time_move > 0.01:        
            win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 0, 5)            
            prev_time_move = time.time()
        
        elapsed_time = time.time() - prev_time
        if elapsed_time > 0.5:
            prev_time = time.time()
            is_trainsitin()
            if nnresult == 0:
                set_state("normal")
            elif nnresult == 2:
                set_state("down")                      

    elif state == "down":
        elapsed_time_move = time.time() - prev_time_move
        if elapsed_time_move > 0.01:        
            win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 0, -5)            
            prev_time_move = time.time()

        elapsed_time = time.time() - prev_time
        if elapsed_time > 0.5:
            prev_time = time.time()
            is_trainsitin()
            if nnresult == 0:
                set_state("normal")
            elif nnresult == 1:
                set_state("up")            