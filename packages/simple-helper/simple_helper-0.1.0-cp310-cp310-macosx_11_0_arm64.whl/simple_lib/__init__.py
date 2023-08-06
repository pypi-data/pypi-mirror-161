from .simple_lib import *

__doc__ = simple_lib.__doc__
if hasattr(simple_lib, "__all__"):
    __all__ = simple_lib.__all__