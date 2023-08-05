'''
Helper functions for easy input.

This module contains helper functions that make input in 
python easier.

NOTE: If you import this package using 
"from easyio.inp import *", the built-in input() function 
will be overwritten with the input() function from this 
package.
'''

# Copyright 2022 Casey Devet
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


# This variable holds the built-in input() function that we
# are replacing
py_input = input


def input (prompt=None, /, *, sep=' ', file=None, type=str):
    '''
    Read a line of input.

    The prompt string, if given, is printed to the console 
    before reading input.

    The sep parameter, which defaults to a single space is 
    what is printed after the prompt, but before the input 
    is retrieved.  If no prompt is given, this is not 
    printed.

    The file can be any file-like object that has a 
    .readline() method.  If no file is given, input is 
    retrieved from the standard input stream (stuff typed 
    into the console).  If a file is given, the prompt and 
    sep are not printed.

    The input value can be converted to any type using the 
    type parameter.  This needs to be a function that takes 
    a string and converts it to the desired type (e.g. int, 
    float, number, etc.)
    '''

    if not callable(type):
        if hasattr(type, "__name__"):
            raise TypeError(f"Invalid type: {type.__name__}")
        else:
            raise TypeError(f"Invalid type: {type}")
    try:
        if file is None:
            if prompt:
                string = py_input(f"{prompt}{sep}")
            else:
                string = py_input()
        else:
            string = file.readline()
    except EOFError:
        raise EOFError("The source has no more data!") from None
    except:
        raise IOError("There was an error trying to get input!") from None
    if string == '':
        return None
    try:
        return type(string)
    except ValueError:
        raise ValueError(f"This input is not a valid {type.__name__}: {string}") from None
    except TypeError:
        raise ValueError(f"Invalid type: {type.__name__}") from None
    except:
        raise IOError(f"There was an issue converting '{string}' to type {type.__name__}") from None


def inputs (prompt=None, /, **kwargs):
    '''
    Read multiple lines of input, ending with a blank line.

    The prompt string, if given, is printed to the console 
    before reading each line of input.

    Any keyword arguments (e.g. file, sep, type) will be
    forwarded to the input() function.

    When reading from a file, the end of the inputs is the
    end of the file, not a blank line.
    '''

    while True:
        value = input(prompt, **kwargs)
        if value is None or value == '':
            break
        yield value


__all__ = [
    "input",
    "inputs"
]