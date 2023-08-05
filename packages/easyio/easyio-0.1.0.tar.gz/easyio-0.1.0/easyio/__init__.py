'''
Helper functions for easy input and output.

This package contains a variety of helper functions that 
make input and output in python easier.

NOTE: If you import this package using 
"from easyio import *", the built-in input() function will 
be overwritten with the input() function from this package.
'''

# Copyright 2022 Casey Devet
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# This module provides some useful functions that make
# teaching Python a bit easier.  To make these functions 
# available in your program, import them using the command:
# from easyio import *

_submodules = [
    "inp",
    "out",
    "types"
]

import importlib as _imp

__all__ = []

for _modname in _submodules:
    _mod = _imp.import_module(f".{_modname}", package="easyio")
    for _objname in _mod.__all__:
        globals()[_objname] = getattr(_mod, _objname)
        __all__.append(_objname)
    del globals()[_modname]

del _objname
del _mod
del _modname
del _submodules
del _imp
