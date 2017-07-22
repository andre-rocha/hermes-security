import uuid
import os

class TempImage:
    def __init__(self, basepath="./media", ext='.jpg'):
        #
        self.path = "%(base_path)s/%(rand)s%(ext)s" % {
            "base_path": basepath,
            "rand": str(uuid.uuid4()),
            "ext": ext,
        }

    def set_path(self, path):
        self.path = path

    def get_file(self):
        return open(self.path)

    def cleanup(self):
        os.remove(self.path)
