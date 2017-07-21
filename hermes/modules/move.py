import datetime

import cv2

from .. import config
from ..pyimage.tmpimage import TempImage
from hermes.utils.decorators import register_module

@register_module("move")
class MovementModule:
    def __init__(self, feedname):
        self.feedname = feedname
        self.avg = None
        self.lastUploaded = datetime.datetime.now()
        self.motionCounter = 0
        self.text = "Unoccupied"

    def send_frame(self, path):
        config['SEND_PIC'] = False
        from hermes import botman
        botman.send_picture(path)

    def cleanup(self):
        # TODO : Cleanup
        print('[-] Cleaning up Movement Module...')

    def run(self, frame):
        self.text = "Unoccupied"
        timestamp = datetime.datetime.now()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)

        if self.avg is None:
            print("[INFO] starting background model...")
            self.avg = gray.copy().astype("float")
            return

        cv2.accumulateWeighted(gray, self.avg, 0.5)
        frameDelta = cv2.absdiff(gray, cv2.convertScaleAbs(self.avg))

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
            self.text = "Occupied"

	# draw the text and timestamp on the frame
        ts = timestamp.strftime("%A %d %B %Y %I:%M:%S%p")
        cv2.putText(frame, "Room Status: {}".format(self.text), (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        cv2.putText(frame, ts, (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)

	# check to see if the room is occupied
        if self.text == "Occupied":
            # check to see if enough time has passed between uploads
            if (timestamp - self.lastUploaded).seconds >= config["MIN_UPLOAD_SECONDS"]:
                # increment the motion counter
                self.motionCounter += 1

                # check to see if the number of frames with consistent motion is high enough
                if self.motionCounter >= config["MIN_MOTION_FRAMES"]:
                    # write the image to temporary file
                    t = TempImage()
                    cv2.imwrite(t.path, frame)
                    # TODO : upload picture
                    if config["SEND_PIC"]:
                        self.send_frame(t.path)
                    if config.get("CLEAN_FEED", False):
                        t.cleanup()

                    self.lastUploaded = timestamp
                    self.motionCounter = 0
        else:
            self.motionCounter = 0

        if config['SHOW_VIDEO']:
            cv2.imshow(self.feedname, frame)
