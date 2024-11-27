from PIL import ImageGrab
import pygetwindow as gw
import time
import os
import globals

import tensorflow as tf
import numpy as np
import playutils

params = {    
    "nnsize" : 256
}

prev_time = 0
prev_time_road = 0

script_dir = os.path.dirname(os.path.realpath(__file__))

model = playutils.load_model_safe(os.path.join(script_dir, "road.h5"))

state = "normal"
nnresult = 0

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
    global nnresult

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
    nnresult = ind

    print ("Detect road " + str(ind))

    return ind == 1 or ind == 2

def start():
    on_transit_in()
           
def update():
    pass

       