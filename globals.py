import sys
import os
import logging
import threading

# logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logging.basicConfig(level=logging.DEBUG, format="%(message)s")

script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
sys.path.append(script_dir)

SCREENSHOT = None
SCREENSHOT_LOCK = threading.Lock()

CURRENT_STATE = "follow_road"