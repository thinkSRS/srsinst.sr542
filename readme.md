# srsinst.sr542

`srsinst.sr542` is a Python package to control the 
[SR542 Precision Optical Chopper](https://thinksrs.com/products/sr542.html)
from [Stanford Research Systems (SRS)](https://thinksrs.com/).

`srsinst.sr542` is based on [srsgui](https://pypi.org/project/srsgui/),
which you do not need to install separately, 
but is included with this install. 

## Installation
You need a working Python 3.7 or later with `pip` (Python package installer) installed. 
If you don't, [install Python](https://www.python.org/) to your system.

To install `srsinst.sr542` as an instrument driver , use Python package installer `pip` from the command line.

    python -m pip install srsinst.sr542

To use it as a GUI application, create a virtual environment, 
if necessary, and install:

    python -m pip install srsinst.sr542[full]


## Run `srsinst.sr542` as GUI application
If the Python Scripts directory is in your PATH environment variable,
start the application by typing from the command line:

    sr542

If not,

    python -m srsinst.sr542

will start the GUI application.

Once running the GUI, you can:
- Connect to an SR542 from the Instruments menu.
- Select a task from the Task menu.
- Press the green arrow to run the selected task. 

You can write your own task(s) or modify an existing one and run it from the GUI application, too.

## Use `srsinst.sr542` as instrument driver
* Start a Python interpreter, a Jupyter notebook, or an editor of your choice 
to write a Python script.
* Import the **SR542** class from `srsinst.sr542` package.
* Create an instance of the **SR542** and establish a remote connection.

|

    C:\>python
    Python 3.11.0 (main, Oct 24 2022, 18:26:48) [MSC v.1933 64 bit (AMD64)] on win32
    Type "help", "copyright", "credits" or "license" for more information. 
    >>>
    >>> from srsinst.sr542 import SR542
    >>> chopper = SR542('serial', 'COM4', '115200')
    >>> chopper.check_id()
    ('SR542', 's/n00001005', 'v1.0.5')
    

**SR542** is comprised of multiple **Component**s, 
which provides groupings of related commands and class methods.
 The **Component** class has a convenience attribute `dir` to show  available attributes and methods in the Python dictionary format.

    >>> chopper.dir.keys()
    dict_keys(['components', 'commands', 'methods'])

**SR542** has 5 components that contain remote commands and methods
as organized in the [Remote Operation chapter](https://www.thinksrs.com/downloads/pdfs/manuals/SR542m.pdf#page=44) 
of the *SR542 Operating Manual and Programming Reference*.

    >>> chopper.dir['components'].keys()
    dict_keys(['config', 'operate', 'setup', 'interface', 'status'])

## Configure SR542 components
Let's set the chopper Configuration.

    >>> chopper.config.dir
    {'components': {}, 
     'commands': {'source': ('DictCommand', 'SRCE'), 
                  'sync_edge': ('DictCommand', 'EDGE'), 
                  'control_target': ('DictCommand', 'CTRL'),
                  'internal_freq': ('FloatCommand', 'IFRQ'), 
                  'phase': ('FloatCommand', 'PHAS'), 
                  'relative_phase': ('BoolCommand', 'RELP'), 
                  'multiplier': ('IntCommand', 'MULT'), 
                  'divisor': ('IntCommand', 'DIVR'), 
                  'vco_frequency': ('FloatCommand', 'VCOS')}, 
      'methods': ['jump_to_internal_frequency']
    }
    
    
If a command is a `DictCommand` instance, it uses mapped keys and values. 
Use `get_command_info()` to find out the mapping dictionary information.

    >>> chopper.config.get_command_info('source')
    {'command class': 'DictCommand', 
     'raw remote command': 'SRCE', 
     'set_dict': {'internal': 0, 'vco': 1, 'line': 2, 'external': 3},
     'get_dict': {'internal': 0, 'vco': 1, 'line': 2, 'external': 3}, 
     'index_dict': None
    }

The command `chopper.config.source` encapsulates the raw command 'SRCE' 
explained in the [Setion 3.4.4 of the manual](https://www.thinksrs.com/downloads/pdfs/manuals/SR542m.pdf#page=51). 
The token integers (0, 1, 2, and 3) are mapped to the strings (`'internal'`, `'vco'`, `'line'`, and `'external'`)

    >>> chopper.config.source
    'internal'
    >>> chopper.config.source = 'external'    
    >>> print(chopper.config.source)
    external    

You can configure other parameters in the similar way.

    >>> chopper.config.internal_freq
    100.0    
    >>> chopper.config.multiplier = 3
    >>> chopper.config.get_command_info('sync_edge')   
    {'command class': 'DictCommand', 
     'raw remote command': 'EDGE', 
     'set_dict': {'rise': 0, 'fall': 1, 'sine': 2}, 
     'get_dict': {'rise': 0, 'fall': 1, 'sine': 2}, 
     'index_dict': None
    }  
    >>> chopper.config.sync_edge = 'rise'



