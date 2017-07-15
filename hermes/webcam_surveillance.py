# OpenCV 3.2.0
from .pyimage.tmpimage import TempImage

import datetime
import json
import time
import sys
import cv2

from . import config

cap = cv2.VideoCapture(0)

# # Use when writting a video output or create a tmpvideo class for multiple outs
# fourcc = cv2.VideoWriter_fourcc(*'XVID')
# out = cv2.VideoWriter('output.avi',fourcc, 20.0, (640,480))


def send_frame(path):
    config["SEND_PIC"]["SEND"] = False
    from . import botman
    botman.send_picture(path)

def start():
    # Initialize the average frame, last uploaded timestamp and frame motion counter
    avg = None
    lastUploaded = datetime.datetime.now()
    motionCounter = 0

    while True:

        timestamp = datetime.datetime.now()
        text = "Unoccupied"

        ret, frame = cap.read()

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)

        if avg is None:
            print("[INFO] starting background model...")
            avg = gray.copy().astype("float")
            continue

        cv2.accumulateWeighted(gray, avg, 0.5)
        frameDelta = cv2.absdiff(gray, cv2.convertScaleAbs(avg))

        thresh = cv2.threshold(frameDelta, config["DELTA_THRESH"], 255, cv2.THRESH_BINARY)[1]
        thresh = cv2.dilate(thresh, None, iterations=2)
        _, cnts, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # loop over the contours
        for c in cnts:
            # if the contour is too small, ignore it
            if cv2.contourArea(c) < config["MIN_AREA"]:
                    continue

            # compute the bounding box for the contour, draw it on the frame,
            # and update the text
            (x, y, w, h) = cv2.boundingRect(c)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            text = "Occupied"

	# draw the text and timestamp on the frame
        ts = timestamp.strftime("%A %d %B %Y %I:%M:%S%p")
        cv2.putText(frame, "Room Status: {}".format(text), (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        cv2.putText(frame, ts, (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)

	# check to see if the room is occupied
        if text == "Occupied":
            # check to see if enough time has passed between uploads
            if (timestamp - lastUploaded).seconds >= config["MIN_UPLOAD_SECONDS"]:
                # increment the motion counter
                motionCounter += 1

                # check to see if the number of frames with consistent motion is high enough
                if motionCounter >= config["MIN_MOTION_FRAMES"]:
                    # check to see if dropbox sohuld be used
                    # write the image to temporary file
                    t = TempImage()
                    cv2.imwrite(t.path, frame)
                    # TODO : upload picture
                    if config["SEND_PIC"]["SEND"]:
                        send_frame(t.path)
                    if config.get("CLEAN_FEED", False):
                        t.cleanup()

                    lastUploaded = timestamp
                    motionCounter = 0
        else:
            motionCounter = 0

        if config['SHOW_VIDEO']:
            cv2.imshow("Security Feed", frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
