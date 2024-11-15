import sys
import os
script_directory = os.path.dirname(os.path.abspath(sys.argv[0]))

global_dir = os.path.join(script_directory, "..")
sys.path.append(global_dir)

import ctypes
import win32api
import win32gui
import win32con
from ctypes import wintypes

import keyboard
import pydirectinput
import time
import playutils
import threading

lock = threading.Lock()

action_list = []

keys_states = []

last_input_time = time.time()

# Define constants
RIDEV_INPUTSINK = 0x00000100
RID_INPUT = 0x10000003
RIM_TYPEMOUSE = 0
WM_INPUT = 0x00FF  # Define the missing WM_INPUT constant

# Mouse button flag constants
RI_MOUSE_LEFT_BUTTON_DOWN = 0x0001
RI_MOUSE_LEFT_BUTTON_UP = 0x0002
RI_MOUSE_RIGHT_BUTTON_DOWN = 0x0004
RI_MOUSE_RIGHT_BUTTON_UP = 0x0008
RI_MOUSE_MIDDLE_BUTTON_DOWN = 0x0010
RI_MOUSE_MIDDLE_BUTTON_UP = 0x0020

# Define RAWINPUTDEVICE structure
class RAWINPUTDEVICE(ctypes.Structure):
    _fields_ = [
        ('usUsagePage', ctypes.c_ushort),
        ('usUsage', ctypes.c_ushort),
        ('dwFlags', ctypes.c_ulong),
        ('hwndTarget', ctypes.wintypes.HWND)
    ]

# Define RAWINPUTHEADER structure
class RAWINPUTHEADER(ctypes.Structure):
    _fields_ = [
        ('dwType', ctypes.c_ulong),
        ('dwSize', ctypes.c_ulong),
        ('hDevice', ctypes.wintypes.HANDLE),
        ('wParam', ctypes.wintypes.WPARAM)
    ]

# Define RAWMOUSE structure
class RAWMOUSE(ctypes.Structure):
    _fields_ = [
        ('usFlags', ctypes.c_ushort),
        ('ulButtons', ctypes.c_ulong),
        ('usButtonFlags', ctypes.c_ushort),
        ('usButtonData', ctypes.c_ushort),
        #('ulRawButtons', ctypes.c_ulong),
        ('lLastX', ctypes.c_long),  # This is the delta X
        ('lLastY', ctypes.c_long)   # This is the delta Y
    ]    

# Define RAWINPUT structure
class RAWINPUT(ctypes.Structure):
    _fields_ = [
        ('header', RAWINPUTHEADER),
        ('data', RAWMOUSE)
    ]

# Register Raw Input devices
def register_raw_input(hwnd):
    rid = RAWINPUTDEVICE()
    rid.usUsagePage = 1
    rid.usUsage = 2  # Mouse
    rid.dwFlags = RIDEV_INPUTSINK
    rid.hwndTarget = hwnd

    ctypes.windll.user32.RegisterRawInputDevices(
        ctypes.byref(rid), 1, ctypes.sizeof(rid))

# Process Raw Input messages (WM_INPUT)
def process_raw_input(lParam, last_input_time = 0, debounce_time = 0.01):
    global action_list, prev_time

    current_time = time.time()
    # Debounce by checking if enough time has passed since last input
    if current_time - last_input_time < debounce_time:
        return last_input_time  # Don't process if debounced

    input_size = ctypes.c_uint(ctypes.sizeof(RAWINPUT))
    raw_input = RAWINPUT()

    # Get the raw input data
    ctypes.windll.user32.GetRawInputData(
        lParam, RID_INPUT, ctypes.byref(raw_input), ctypes.byref(input_size), ctypes.sizeof(RAWINPUTHEADER)
    )

    # Check if the input is a mouse event
    if raw_input.header.dwType == RIM_TYPEMOUSE:
        delta_x = raw_input.data.lLastX
        delta_y = raw_input.data.lLastY
        flags = raw_input.data.usFlags
        
        wait_registered = False

        if delta_x != 0 or delta_y != 0:
            elapsed_time = time.time() - prev_time
            if elapsed_time > 0:
                wait_registered = True                
                action_list.append("wait " + str(elapsed_time))
                prev_time = time.time()            
            
            action_list.append("mouse_move " + str(delta_x) + " " + str(delta_y))    
            # print(f"Flags: {flags}, Mouse Delta - X: {delta_x}, Y: {delta_y}")
        
        #Register button
        if raw_input.data.ulButtons:
            if not wait_registered:
                elapsed_time = time.time() - prev_time
                if elapsed_time > 0:                   
                    action_list.append("wait " + str(elapsed_time))
                    prev_time = time.time()

            if raw_input.data.ulButtons & RI_MOUSE_LEFT_BUTTON_DOWN:                
                action_list.append("mouse_button_state left True")

            if raw_input.data.ulButtons & RI_MOUSE_LEFT_BUTTON_UP:                
                action_list.append("mouse_button_state left False")

            if raw_input.data.ulButtons & RI_MOUSE_RIGHT_BUTTON_DOWN:                
                action_list.append("mouse_button_state right True")

            if raw_input.data.ulButtons & RI_MOUSE_RIGHT_BUTTON_UP:                
                action_list.append("mouse_button_state right False")
        
    return current_time  # Update last input time

# Window Procedure to handle messages
def wnd_proc(hwnd, msg, wparam, lparam):
    if msg == WM_INPUT:
        global last_input_time
        last_input_time  = process_raw_input(lparam, last_input_time, debounce_time=0)
    return win32gui.DefWindowProc(hwnd, msg, wparam, lparam)

# Create a window to capture raw input
def create_window():
    
    global last_input_time
    last_input_time = time.time()  # Track the last time an input was processed

    wc = win32gui.WNDCLASS()
    wc.lpfnWndProc = wnd_proc
    wc.lpszClassName = 'RawInputWindow'
    wc.hInstance = win32api.GetModuleHandle(None)
    wc.hCursor = win32api.LoadCursor(0, win32con.IDC_ARROW)
    
    class_atom = win32gui.RegisterClass(wc)
    hwnd = win32gui.CreateWindow(
        class_atom, 'RawInputCapture', 0, 0, 0, 100, 100, 0, 0, wc.hInstance, None
    )
    
    register_raw_input(hwnd)
    
    return hwnd

def keys_up():    
    for key in playutils.keys:
        pydirectinput.keyUp(key)

def stop_script():
    if keyboard.is_pressed("f4"):

        # for thread in threads:
        #     thread.join() 

        # Open the file in write mode and save the list
        with open(os.path.join(script_directory,"state_test_1.gamerec"), 'w') as file:
            for line in action_list:
                file.write(line + '\n')  # Write each line followed by a newline character

        print("Stopped")                
        keys_up()   
        
        sys.exit()

def check_keyboard():

    global keys_states, prev_time, action_list
                
    state_changed = False

    for i, key in enumerate(playutils.keys):
        state = keyboard.is_pressed(key)   
        if keys_states[i] != state:
            state_changed = True
            break
    
    if state_changed:
        elapsed_time = time.time() - prev_time
        if elapsed_time > 0:            
            action_list.append("wait " + str(elapsed_time))
            prev_time = time.time()

        for i, key in enumerate(playutils.keys):
            state = keyboard.is_pressed(key)   
            if keys_states[i] != state:                
                action_list.append("key_state " + key + " " + str(state))
                keys_states[i] = state
        

# Main message loop
def check_mouse():
    hwnd = create_window()
    win32gui.PumpMessages()
    # while True:
    #     win32gui.PumpWaitingMessages()  # Alternatively, you can use PumpMessages()  
    #     if keyboard.is_pressed("f4"):
    #         return              

threads = []

def main():
    global threads

    thread = threading.Thread(target=check_mouse)
    thread.daemon = True
    threads.append(thread)
    thread.start()

    while True:
        
        # Process any pending messages
        # win32gui.PumpWaitingMessages()  # Alternatively, you can use PumpMessages()

        stop_script()    
        check_keyboard()

        time.sleep(0.001)
              
def fill_initial_states():
    global keys_states
    
    for key in playutils.keys:
        keys_states.append(False) 

if __name__ == '__main__':
    print("Press ENTER to start")
    keyboard.wait("enter")
    print("Started. Press F4 to stop")
    time.sleep(0.5) #prevent ENTER to be part of recording
    fill_initial_states()
    prev_time = time.time()
    main()
