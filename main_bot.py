import globals
import playutils
import sys
import keyboard
import pydirectinput

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

def stop():
    global paused

    if keyboard.is_pressed("f4"):        
        states[local_state].on_stop()
        
        log.info("Stopped")
        playutils.keys_up()    
        sys.exit()

    if keyboard.is_pressed("f7"):
        if not paused:
            log.info("Paused")
            playutils.keys_up()
            paused = True
        else:        
            log.info("Continue")        
            paused = False

def start():    
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