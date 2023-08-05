# EasyIO

This module provides easy-to-use functions for input and output in Python.

## Installation

```
pip install easyio
```

## Usage

This package is meant to supplement the IO functions built in to python for beginner programmers.

We recommend that you import using `import *` to add the functions to the global namespace:

```
from easyio import *
```

NOTE: When importing using `import *`, the built-in `input()` function will be overwritten with the `input()` function from this 
package.

### Input

The following functions are provided to aid in user input:

```
input(prompt=None, /, *, sep=' ', file=None, type=<class 'str'>)
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

inputs(prompt=None, /, **kwargs)
    Read multiple lines of input, ending with a blank line.
    
    The prompt string, if given, is printed to the console 
    before reading each line of input.
    
    Any keyword arguments (e.g. file, sep, type) will be
    forwarded to the input() function.
    
    When reading from a file, the end of the inputs is the
    end of the file, not a blank line.
```

### Output

The following functions are provided to aid in output to the user:

```
error(message, status=0)
    Print an error message to the console and end the 
    program.
    
    An optional status code can be provided.
```

### Types

The following functions are provided to convert strings to other useful types.  These are meant to be used as the `type` argument for the `input()` function.

```
number(value)
    Convert to a numerical value.
    
    Whole numbers will be returned as int objects and 
    decimal numbers will be returned as float objects.
```

## License

This package is licensed under the MIT License, making it free for you to use, change and profit from.
