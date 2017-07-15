from . import config

config["HAHA"] = None

def do(foo="BLABLA"):
    print("[-] %s" % str(config["HAHA"]))
    config["HAHA"] = foo
    print("[+] %s" % str(config["HAHA"]))
