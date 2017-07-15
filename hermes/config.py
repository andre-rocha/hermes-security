# coding: utf-8
'''Loads and stores configuration'''

import os
import sys
from . import default_settings
from importlib.machinery import SourceFileLoader

# Load default settings
config = {k: getattr(default_settings, k)
          for k in dir(default_settings)
          if not k.startswith('_') and k.isupper()}

# Load local settings
local_settings_file = os.getenv('HERMES_SETTINGS', None)
if local_settings_file is None:
    default_local_settings = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'local_settings.py'))
    if os.path.isfile(default_local_settings):
        local_settings_file = default_local_settings

if local_settings_file is not None:
    local_settings = SourceFileLoader('captiveportal.local_settings',
        local_settings_file).load_module()

    config.update((k, getattr(local_settings, k))
                  for k in dir(local_settings)
                  if not k.startswith('_') and k.isupper())
else:
    print('[!!]', 'local_settings.py not found. Have you configured the project yet?')

sys.modules[__name__] = config
