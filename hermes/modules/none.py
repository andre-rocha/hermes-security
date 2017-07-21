import cv2

from hermes.utils.decorators import register_module

@register_module("none")
class no_module:
    def __init__(self, feedname):
        self.feedname = feedname

    def cleanup(self):
        # TODO : Cleanup
        print('[-] Cleaning up Movement Module...')

    def run(self, frame):
        cv2.imshow(self.feedname, frame)
