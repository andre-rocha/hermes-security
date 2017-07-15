from . import config, webcam_surveillance, botman

config["SEND_PIC"] = {"SEND": False, "USERS": []}

botman.start()
webcam_surveillance.start()
