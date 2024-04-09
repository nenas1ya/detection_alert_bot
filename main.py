import os
from os.path import join, dirname
from dotenv import load_dotenv
import time

from stk_parser import get_detections
detects = get_detections()
print(len(detects))

#while True:
    # connect to stk
        # checking 
            # reqst detections, calc count
            # if no msg -> send detections count
            # if msg exist -> edit msg or delete and send new
        # commands
            # refresh - send new msg with actual count now
            # stat - some statistic
        

    #TODO 
        # inchat validating with img+buttons

#   pass




