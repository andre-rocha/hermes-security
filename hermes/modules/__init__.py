import os

from hermes import config

config['registry'] = {}

for module in os.listdir(os.path.dirname(__file__)):
    if module == '__init__.py' or module[-3:] != '.py':
        continue
    __import__("hermes.modules."+module[:-3], locals(), globals())
del module
