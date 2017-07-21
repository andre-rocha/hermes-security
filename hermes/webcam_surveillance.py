# OpenCV 3.2.0
from .pyimage.tmpimage import TempImage

import datetime
import json
import time
import sys
import cv2

from . import config
#from hermes.detection.movement_module import MovementModule
import hermes.modules

# MovementModule = config["registry"]["move"]

cap = cv2.VideoCapture(0)

# # Use when writting a video output or create a tmpvideo class for multiple outs
# fourcc = cv2.VideoWriter_fourcc(*'XVID')
# out = cv2.VideoWriter('output.avi',fourcc, 20.0, (640,480))


def start():
    # initialize the average frame, last uploaded timestamp and frame motion counter
    # XXX
    cmod = config.get("module", "none")
    module = config["registry"][cmod]("security feed")
    while True:

        if cmod != config.get("module", "none"):
            module.cleanup()
            cmod = config["module"]
            print("[*] Changing Module to : "+cmod)
            module = config["registry"][cmod]("security feed")

        ret, frame = cap.read()
        module.run(frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            module.cleanup()
            break

    cap.release()
    cv2.destroyAllWindows()
