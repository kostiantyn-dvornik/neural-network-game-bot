from PIL import ImageGrab
import pygetwindow as gw
import time
import os

import playutils
import globals
import tensorflow as tf
import numpy as np

import win32api
import win32con

from states.hit_enemy import state_hit_enemy
from states.horizont import state_horizont

params = {    
    "posx" : 584,
    "posy" : 23,
    "grabsize" : 256,
    "nnsize" : 128
}

prev_time = 0
prev_time_move = 0
prev_time_walk = 0

script_dir = os.path.dirname(os.path.realpath(__file__))

model = playutils.load_model_safe(os.path.join(script_dir, "find_enemy.h5"))

def on_transit_in():
    global prev_time
    prev_time = time.time()

    global prev_time_move
    prev_time_move = time.time()

    global prev_time_walk
    prev_time_walk = time.time()

def on_stop():
    print(os.path.basename(__file__) + " stopped")

def is_transit_in():

    img = globals.SCREENSHOT

    if 'grabsize' in params:
        crop_area = (params['posx'], params['posy'], params['posx'] + params['grabsize'], params['posy'] + params['grabsize'])
        cropped_img = img.crop(crop_area)
        #cropped_img.show()
        resize = tf.image.resize(np.array(cropped_img), (params['nnsize'], params['nnsize']))
    else:
        resize = tf.image.resize(np.array(img), (256,256))

    np.expand_dims(resize,0)

    # print('Start ' + str(round(time.time() * 1000)))        
    yhat = model.predict(np.expand_dims(resize/255,0), verbose = 0)        
    # print('End ' + str(round(time.time() * 1000)))

    # print(yhat)

    res = yhat[0]        
    ind = np.argmax(res)

    print("Find enemy " + str(ind))

    return ind == 1

def start():
    on_transit_in()
           
def update():
    
    global prev_time_move        
    elapsed_time_move = time.time() - prev_time_move
    if elapsed_time_move > 0.01:        
        # win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 10, int(math.sin(time.time() / 10.0) * 3 ))            
        win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 10, 0)            
        prev_time_move = time.time()
    
    global prev_time
    elapsed_time = time.time() - prev_time
    if elapsed_time > 0.5:
        prev_time = time.time()
        if state_hit_enemy.is_transit_in(): 
            globals.CURRENT_STATE = "hit_enemy"

    global prev_time_walk
    elapsed_time__walk = time.time() - prev_time_walk
    if elapsed_time__walk > 1:
        if  not is_transit_in():
            globals.CURRENT_STATE = "walk"
            playutils.keys_up()
            
        prev_time_walk = time.time()   

    state_horizont.update()              