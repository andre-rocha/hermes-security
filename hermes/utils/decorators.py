from hermes import config

def register_module(token):
    class Wrapper(object):
        def __init__(self, module):
            """
            """
            config["registry"][token] = module
            self.module = module
        def __getattr__(self, name):
            return getattr(self.module, name)
        def __call__(self, *args, **kwargs):
            return self.module(*args, **kwargs)
    return Wrapper
