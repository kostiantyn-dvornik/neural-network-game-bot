import globals
import playutils
import sys
import keyboard
import pydirectinput
from PIL import Image
import pygetwindow as gw
import time
import threading
import mss

from globals import logging as log

#[gen]
from states.hit_enemy import state_hit_enemy
from states.horizont import state_horizont
from states.walk import state_walk
from states.stuck import state_stuck
from states.stuck_walk import state_stuck_walk
from states.find_enemy import state_find_enemy
from states.road import state_road
from states.follow_road import state_follow_road
from states.reset import state_reset

#[gen]
states = {
    "hit_enemy" : state_hit_enemy, 
    "horizont" : state_horizont,
    "walk" : state_walk,
    "stuck" : state_stuck, 
    "stuck_walk" : state_stuck_walk,
    "find_enemy" : state_find_enemy,
    "road" : state_road,
    "follow_road" : state_follow_road,
    "reset" : state_reset,
}

paused = False
local_state = ""
prev_time_screenshot = time.time()

window = None
winRect = None

def on_stop():
    states[local_state].on_stop()
        
    log.info("Stopped")
    playutils.keys_up() 

    global stop_grab_screen_thread_func
    stop_grab_screen_thread_func = True

    global grab_screen_thread
    grab_screen_thread.join()

    sys.exit()

def stop():
    global paused

    if keyboard.is_pressed("f4"):        
        on_stop()

    if keyboard.is_pressed("f7"):
        if not paused:
            log.info("Paused")
            playutils.keys_up()
            paused = True
        else:        
            log.info("Continue")        
            paused = False

def grab_screenshot():    
    global winRect
    with mss.mss() as sct:
        screenshot = sct.grab(winRect)

        # Convert the raw bytes to a Pillow Image
        img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)

        with globals.SCREENSHOT_LOCK:
            globals.SCREENSHOT = img
        # log.info(f"Grab {time.time()}")

def start(): 
    global window, winRect
    window = gw.getWindowsWithTitle('Skyrim')[0]
    winRect = {"top": window.top + 2, "left": window.left + 2, "width": window.right - window.left - 4, "height": window.bottom - window.top - 4}
    
    grab_screenshot() 
    grab_screen_thread.start()

    for state in states.values():
        state.start()

def transit_in():
    global local_state

    if local_state != "":
        states[local_state].on_stop()

    states[globals.CURRENT_STATE].on_transit_in()
    
    local_state = globals.CURRENT_STATE

    log.info("")

def update():
    if globals.CURRENT_STATE != local_state:
        log.info(f"Transit to {globals.CURRENT_STATE}")
        transit_in()
    
    states[globals.CURRENT_STATE].update()
    time.sleep(0.01)   

stop_grab_screen_thread_func = False
def grab_screen_thread_func():
    global stop_grab_screen_thread_func
    while not stop_grab_screen_thread_func:                
        grab_screenshot()
        time.sleep(0.02)
grab_screen_thread = threading.Thread(target=grab_screen_thread_func, daemon=True)

def main():
    local_state = globals.CURRENT_STATE
    start()
    

    while True:
        stop()

        if not paused:
            update()

pydirectinput.FAILSAFE = False

log.info("\nPress ENTER to begin\nPress F7 to Play/Pause\nPress F4 to stop")
keyboard.wait("enter")

main()