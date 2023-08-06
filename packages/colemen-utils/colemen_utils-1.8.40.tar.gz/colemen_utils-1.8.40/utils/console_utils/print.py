# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=line-too-long
# pylint: disable=global-statement
'''
    A module of utility methods used for generating console log messages.

    ----------

    Meta
    ----------
    `author`: Colemen Atwood
    `created`: 06-03-2022 10:22:15
    `memberOf`: random_utils
'''

import random as _random
import hashlib as _hashlib
import time as _time
import string as _string
from typing import Union as _Union


from colorama import Fore as _Fore
from colorama import Style as _Style
from colorama import Back as _Back



import utils.dict_utils as _obj
import utils.string_utils as _csu





def _prepend(message,fore):
    if fore is not None:
        return fore + message
    return message



def log(message,style=None,**kwargs):
    '''
        Print shit to the console with a little style.

        ----------

        Arguments
        -------------------------
        `message` {string}
            The message to print.
        [`style`=None] {string}
            The style string, same as the keyword argument, this is required for backward compatibility.

        Keyword Arguments
        -------------------------
        `style` {string}
            The style to use on the message:
            - error, red
            - success, green
            - warn, yellow
            - cyan, info
            - magenta, pink
            - blue
            
            You can also provide "invert" which will make the background the primary color and the text black.
            
        [`return`=False] {bool}
            if True, the message is not printed, but returned.
            
        [`same_line`=False] {bool}
            if True, the message is printed to the same line and the cursor is set back to the beginning.

        Return {string|None}
        ----------------------
        if return_string is False or not provided, it will return nothing, otherwise is returns the string.

        Meta
        ----------
        `author`: Colemen Atwood
        `created`: 06-28-2022 08:59:11
        `memberOf`: log
        `version`: 1.0
        `method_name`: log
        * @xxx [06-28-2022 09:21:49]: documentation for log
    '''


    
    return_string = _obj.get_kwarg(['return','return string','no print'],False,(bool),**kwargs)
    style = _obj.get_kwarg(['style'],style,(str),**kwargs)
    same_line = _obj.get_kwarg(['same_line'],False,(bool),**kwargs)
    # bg = _obj.get_kwarg(['bg','back','back ground'],None,(str),**kwargs)
    # fg = _obj.get_kwarg(['fg','fore','fore ground'],None,(str),**kwargs)


    colors = [
        {
            "styles":["error","red"],
            "colors":{
                "fore":_Fore.RED,
                "back":None
            },
            "invert":{
                "back":_Back.RED,
                "fore":_Fore.BLACK
            },
        },
        {
            "styles":["success","green"],
            "colors":{
                "fore":_Fore.GREEN,
                "back":None
            },
            "invert":{
                "back":_Back.GREEN,
                "fore":_Fore.BLACK
            },
        },
        {
            "styles":["warn","warning","yellow"],
            "colors":{
                "fore":_Fore.YELLOW,
                "back":None
            },
            "invert":{
                "back":_Back.YELLOW,
                "fore":_Fore.BLACK
            },
        },
        {
            "styles":["cyan","info"],
            "colors":{
                "fore":_Fore.CYAN,
                "back":None
            },
            "invert":{
                "back":_Back.CYAN,
                "fore":_Fore.BLACK
            },
        },
        {
            "styles":["magenta","pink"],
            "colors":{
                "fore":_Fore.MAGENTA,
                "back":None
            },
            "invert":{
                "back":_Back.MAGENTA,
                "fore":_Fore.BLACK
            },
        },
        {
            "styles":["blue"],
            "colors":{
                "fore":_Fore.BLUE,
                "back":None
            },
            "invert":{
                "back":_Back.BLUE,
                "fore":_Fore.BLACK
            },
        }
    ]

    output = message


    if style is None:
        print(message)



    if style is not None:
        ais = _csu.array_in_string
        style = style.lower()

        for sty in colors:
            # print(f"style: {sty['styles']}")
            if ais(sty['styles'],style):
                if ais(["invert","inv"],style):
                    output = _prepend(output,sty['invert']['fore'])
                    output = _prepend(output,sty['invert']['back'])
                else:
                    output = _prepend(output,sty['colors']['fore'])
                    output = _prepend(output,sty['colors']['back'])

        output = output + _Style.RESET_ALL


        # if style in ["cyan"]:
        #     print(_Fore.CYAN + message + _Style.RESET_ALL)

        # if style in ["magenta"]:
        #     print(_Fore.MAGENTA + message + _Style.RESET_ALL)

        # if style in ["black"]:
        #     print(_Fore.BLACK + message + _Style.RESET_ALL)

        # if style in ["white"]:
        #     print(_Fore.WHITE + message + _Style.RESET_ALL)

        # if style in ["blue"]:
        #     print(_Fore.BLUE + message + _Style.RESET_ALL)
    
    if return_string is False:
        if same_line:
            print(output,end="\r",flush=True)
        else:
            print(output)
    return output