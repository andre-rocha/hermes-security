import datetime

import cv2

from hermes import config
from hermes.pyimage.tmpimage import TempImage
from hermes.utils.decorators import register_module

@register_module("face")
class FaceModule:
    def __init__(self, feedname):
        self.feedname = feedname
        res = config['RESOURCE_DIR']
        if res[-1] == '/':
            res = res[:-1]
        cascPath = "%s/%s" % (res, 'haarcascade_frontalface_default.xml')
        print(cascPath)
        self.faceCascade = cv2.CascadeClassifier(cascPath)
        self.lastUploaded = datetime.datetime.now()

    def send_frame(self, path, caption=''):
        config['SEND_PIC'] = False
        from .. import botman
        botman.send_picture(path, caption=caption)

    def cleanup(self):
        # TODO : Cleanup
        print('[-] Cleaning up Face Module...')

    def run(self, frame):
        self.detected = False
        timestamp = datetime.datetime.now()

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = self.faceCascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30),
            flags=cv2.CASCADE_SCALE_IMAGE
        )

        # Draw a rectangle around the faces
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

        ts = timestamp.strftime("%A %d %B %Y %I:%M:%S%p")
        cv2.putText(frame, ts, (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

        if len(faces) > 0:
            self.detected = True
            cv2.putText(frame, 'Face Detected!', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            # check to see if enough time has passed between uploads
            if (timestamp - self.lastUploaded).seconds >= config["MIN_UPLOAD_SECONDS"]:
                # write the image to temporary file
                t = TempImage()
                cv2.imwrite(t.path, frame)
                # TODO : upload picture
                if config.get("CLEAN_FEED", False):
                    t.cleanup()

                self.lastUploaded = timestamp
        else:
            cv2.putText(frame, '', (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

        if config["SEND_PIC"]:
            t = TempImage()
            cv2.imwrite(t.path, frame)
            self.send_frame(t.path)

        # Display the resulting frame
        if config['SHOW_VIDEO']:
            cv2.imshow(self.feedname, frame)



