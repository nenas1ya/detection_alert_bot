import os
from os.path import join, dirname
from dotenv import load_dotenv
import time

from stk_parser import get_awaiting_detections
detects = get_awaiting_detections()

print(len(detects))



