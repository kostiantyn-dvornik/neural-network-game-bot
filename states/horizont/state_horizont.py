import time
import os
import globals
import threading

import tensorflow as tf
import numpy as np
import playutils

import win32api
import win32con

params = {    
    "nnsize" : 256
}

prev_time = 0

script_dir = os.path.dirname(os.path.realpath(__file__))

model = playutils.load_model_safe(os.path.join(script_dir, "horizont.h5"))

prev_time_move = 0

state = "normal"
nnresult = 0

def on_transit_in():
    global prev_time, prev_time_move
    prev_time = time.time()
    prev_time_move = time.time()

def on_stop():
    global stop_detect_thread_func
    stop_detect_thread_func = True

    global detect_thread
    detect_thread.join()

    print(os.path.basename(__file__) + " stopped")

def start():

    on_transit_in()

    global detect_thread
    detect_thread = threading.Thread(target=detect_thread_func, daemon=True)
    detect_thread.start()

    global stop_detect_thread_func
    stop_detect_thread_func = False
           
def set_state(current_state):
    global state, prev_time, prev_time_move

    state = current_state
    prev_time = time.time()
    prev_time_move = time.time()

stop_detect_thread_func = False
def detect_thread_func():
    global stop_detect_thread_func
    while not stop_detect_thread_func:                
        is_transit_in()
        time.sleep(0.5)

def is_transit_in():
    
    img = globals.SCREENSHOT

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

    # print('Horizont ' + str(ind))

    global nnresult
    nnresult = ind
    
    return ind == 1 or ind == 2

def update():
    global prev_time, prev_time_move, nnresult

    if state == "normal":        
        if (time.time() - prev_time) > 2:
            prev_time = time.time()
            if nnresult == 1:
                set_state("up")
            elif nnresult == 2:
                set_state("down")
            
    elif state == "up":                
        if (time.time() - prev_time_move) > 0.01:        
            win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 0, 5)            
            prev_time_move = time.time()
        
        if (time.time() - prev_time) > 0.5:
            prev_time = time.time()
            if nnresult == 0:
                set_state("normal")
            elif nnresult == 2:
                set_state("down")                      

    elif state == "down":        
        if (time.time() - prev_time_move) > 0.01:        
            win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 0, -5)            
            prev_time_move = time.time()
        
        if (time.time() - prev_time) > 0.5:
            prev_time = time.time()            
            if nnresult == 0:
                set_state("normal")
            elif nnresult == 1:
                set_state("up")            