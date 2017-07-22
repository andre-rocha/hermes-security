from . import config, webcam_surveillance, botman


config["SEND_PIC"] = False


botman.start()
webcam_surveillance.start()
