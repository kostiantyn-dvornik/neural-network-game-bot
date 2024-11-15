import sys
import os
import logging

# logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logging.basicConfig(level=logging.INFO, format="%(message)s")

script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
sys.path.append(script_dir)

CURRENT_STATE = "walk"