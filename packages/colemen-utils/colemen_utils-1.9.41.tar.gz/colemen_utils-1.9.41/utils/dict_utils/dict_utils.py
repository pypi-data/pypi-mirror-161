# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=line-too-long
'''
    A module of utility methods used for manipulating dictionaries.

    ----------

    Meta
    ----------
    `author`: Colemen Atwood
    `created`: 06-03-2022 10:22:15
    `memberOf`: dict_utils
'''

# import re
from types import SimpleNamespace
from typing import Union as _Union
# from typing import Iterable as _Iterable
from typing import TypeVar as _TypeVar
from colorama import Fore as _Fore
from colorama import Style as _Style
import utils.list_utils as _lu
import utils.string_utils as _csu
import collections

def set_defaults(default_vals, obj,**kwargs):
    '''
        Sets default values on the dict provided, if they do not already exist or 
        if the value is None.

        ----------

        Arguments
        -------------------------
        `default_vals` {dict}
            The default values to set on the obj.
        `obj` {dict}
            The object to assign default values to.

        Keyword Arguments
        -------------------------
        [`replace_null`=False] {bool}
            If True, None values in the obj dict are overwritten by the defaults.

        Return {dict}
        ----------------------
        The obj with default values applied

        Meta
        ----------
        `author`: Colemen Atwood
        `created`: 12-09-2021 08:04:03
        `memberOf`: object_utils
        `version`: 1.0
        `method_name`: set_defaults
    '''
    replace_null = get_kwarg(['replace null'],False,(bool),**kwargs)
    
    for k, v in default_vals.items():
        if replace_null:
            if k in obj:
                if obj[k] is None:
                    obj[k] = v

        if k not in obj:
            obj[k] = v
        # print(f"k: {k} - v: {v}")
    return obj

def merge(dict_one:dict,dict_two:dict)->dict:
    '''
        Merge two dictionaries into one.

        ----------

        Arguments
        -------------------------
        `dict_one` {dict}
            The first dict to merge.
        `dict_two` {dict}
            The second dict to merge.

        Return {dict}
        ----------------------
        The merged dictionary

        Meta
        ----------
        `author`: Colemen Atwood
        `created`: 06-05-2022 14:19:19
        `memberOf`: dict_utils
        `version`: 1.0
        `method_name`: merge
        * @xxx [06-05-2022 14:20:44]: documentation for merge
    '''
    return {**dict_one,**dict_two}

def keys_to_lower(dictionary):
    '''
        Converts all keys in a dictionary to lowercase.
    '''
    return {k.lower(): v for k, v in dictionary.items()}

def keys_to_snake_case(data:dict)->dict:
    '''
        Convert all keys in the dictionary to snake_case

        ----------

        Arguments
        -------------------------
        `data` {dict}
            The dictionary to format.

        Return {dict}
        ----------------------
        The dictionary with snake case keys.

        Meta
        ----------
        `author`: Colemen Atwood
        `created`: 06-11-2022 08:53:09
        `memberOf`: dict_utils
        `version`: 1.0
        `method_name`: keys_to_snake_case
        * @xxx [06-11-2022 08:54:03]: documentation for keys_to_snake_case
    '''


    return {_csu.to_snake_case(k): v for k, v in data.items()}

def keys_to_list(data:dict)->list:
    '''
        return all keys in a dictionary as a list.

        ----------

        Arguments
        -------------------------
        `data` {dict}
            The dictionary to parse.

        Return {list|None}
        ----------------------
        A list of the keys in the dictionary.
        returns an empty list if it fails or a non-dictionary was provided.

        Meta
        ----------
        `author`: Colemen Atwood
        `created`: 06-03-2022 07:49:21
        `memberOf`: objectUtils
        `version`: 1.0
        `method_name`: keys_to_list
        * @xxx [06-03-2022 07:50:27]: documentation for keys_to_list
    '''
    if isinstance(data,(dict)) is False:
        return []

    return list(data.keys())

def get_kwarg(key_name:_Union[list,str], default_val=False, value_type=None, **kwargs):
    '''
        Get a kwarg argument that optionally matches a type check or
        return the default value.

        ----------

        Arguments
        -------------------------
        `key_name` {list|string}
            The key name or a list of key names to search kwargs for.

        [`default_val`=False] {any}
            The default value to return if the key is not found or fails
            the type check (if provided.)

        [`value_type`=None] {any}
            The type or tuple of types.
            The kwarg value must match at least one of these.
            Leave as None to ignore type checking.
        `kwargs` {dict}
            The kwargs dictionary to search within.

        Return {any}
        ----------------------
        The value of the kwarg key if it is found.
        The default value if the key is not found or its value fails type checking.

        Meta
        ----------
        `author`: Colemen Atwood
        `created`: 06-03-2022 08:33:36
        `memberOf`: objectUtils
        `version`: 1.0
        `method_name`: get_kwarg
        * @xxx [06-03-2022 08:38:33]: documentation for get_kwarg
    '''
    from utils.random_utils.rand_generation import gen_variations


    kwargs = keys_to_lower(kwargs)
    if isinstance(key_name, list) is False:
        key_name = [key_name]

    for name in key_name:
        # generate basic variations of the name
        varis = gen_variations(name)
        for v_name in varis:
            if v_name in kwargs:
                if value_type is not None:
                    if isinstance(kwargs[v_name], value_type) is True:
                        return kwargs[v_name]
                else:
                    return kwargs[v_name]
    return default_val

def get_arg(args:dict,key_name:_Union[list,str],default_val=False, value_type=None)->any:
    '''
        Get a key's value from a dictionary.

        ----------

        Arguments
        -------------------------
        `args` {dict}
            The dictionary to search within.

        `key_name` {str|list}
            The key or list of keys to search for.

        [`default_val`=False] {any}
            The value to return if the key is not found.

        [`value_type`=None] {any}
            The type the value should have. This can be a tuple of types.

        Return {any}
        ----------------------
        The key's value if it is found and matches the value_type (if provided.)
        The default value otherwise.

        Meta
        ----------
        `author`: Colemen Atwood
        `created`: 06-02-2022 07:43:12
        `memberOf`: object_utils
        `version`: 1.0
        `method_name`: get_arg
        * @xxx [06-02-2022 07:46:35]: documentation for get_arg
    '''
    from utils.random_utils.rand_generation import gen_variations

    if isinstance(args,(dict)) is False:
        return default_val
    if len(args.keys()) == 0:
        return default_val

    args = keys_to_lower(args)
    # if defaults is not None:
    #     defaults = keys_to_lower(defaults)
    #     args = set_defaults(defaults,args)

    if isinstance(key_name, list) is False:
        key_name = [key_name]

    # @Mstep [] first check to see if there is an exact match in the args.
    # @Mstep [LOOP] iterate the key names
    for name in key_name:
        if name in args:
            if value_type is not None:
                if isinstance(args[name], value_type) is True:
                    return args[name]
            else:
                return args[name]

    # @Mstep [] if no exact matches were found, now we generate variations to test for.
    for name in key_name:
        # generate basic variations of the name
        varis = gen_variations(name)
        for v_name in varis:
            if v_name in args:
                if value_type is not None:
                    if isinstance(args[v_name], value_type) is True:
                        return args[v_name]
                else:
                    return args[v_name]
    return default_val

def get_unique_keys(obj, **kwargs):
    '''
        Gets all unique keys in the object provided.

        @param {dict|list} obj - The object or list to search for keys within.
        @param {boolean} [**sort_list=True] - Sort the list alphabetically.
        @param {boolean} [**case_sensitive=True] - If True the case of the key is ignored.
        @param {boolean} [**force_lowercase=True] - Convert all keys to lowercase.
        @param {boolean} [**recursive=True] - Recurse into nested objects to find keys.
        @param {int} [**max_depth=500] - The maximum recursions it is allowed to make.
        @return {list} A list of unique keys from the object, if none are found the list is empty.
        @function get_unique_keys
    '''

    __current_depth = get_kwarg(['__current_depth'], 0, int, **kwargs)
    sort_list = get_kwarg(['sort_list'], False, bool, **kwargs)
    case_sensitive = get_kwarg(['case_sensitive'], True, bool, **kwargs)
    force_lowercase = get_kwarg(['force_lowercase'], True, bool, **kwargs)
    recursive = get_kwarg(['recursive'], True, bool, **kwargs)
    max_depth = get_kwarg(['max_depth'], 500, int, **kwargs)
    kwargs['__current_depth'] = __current_depth + 1

    keys = []

    if recursive is True and __current_depth < max_depth:
        if isinstance(obj, (list, tuple, set)):
            for element in obj:
                if isinstance(element, (list, dict)):
                    keys = keys + get_unique_keys(element, **kwargs)

    if isinstance(obj, dict):
        keys = list(obj.keys())

        if recursive is True and __current_depth < max_depth:
            # pylint: disable=unused-variable
            for k, value in obj.items():
                # find nested objects
                if isinstance(value, (list, dict, tuple, set)):
                    keys = keys + get_unique_keys(value, **kwargs)

    if case_sensitive is True:
        output = []
        lkkeys = []
        for key in keys:
            low_key = key.lower()
            if low_key not in lkkeys:
                output.append(key)
                lkkeys.append(low_key)
        keys = output

    if force_lowercase is True:
        keys = [x.lower() for x in keys]

    keys = list(set(keys))

    if sort_list is True:
        keys = sorted(keys, key=lambda x: int("".join([i for i in x if i.isdigit()])))
    return keys

def has_keys(data:dict,keys:list,**kwargs):
    '''
        confirm that a dictionary has all keys in the key list.

        ----------

        Arguments
        -------------------------
        `data` {dict}
            The dictionary to validate.

        `keys` {list}
            A list of keys that the data dict must contain.

        Keyword Arguments
        -------------------------
        [`message_template`=None] {str}
            The message to print to the console log if a key is missing.
            The string __KEY__ will be replaced with the missing key name.

        Return {bool}
        ----------------------
        True if the dict contains all the keys, False otherwise.

        Meta
        ----------
        `author`: Colemen Atwood
        `created`: 06-03-2022 09:15:17
        `memberOf`: object_utils
        `version`: 1.0
        `method_name`: has_keys
        * @xxx [06-03-2022 09:18:47]: documentation for has_keys
    '''


    message_template = get_kwarg(['message_template'], None, (str), **kwargs)
    missing_keys = []
    keys = _lu.force_list(keys)
    for k in keys:
        if k not in data:
            if message_template is not None:
                msg = message_template.replace("__KEY__",k)
                print(_Fore.RED + msg + _Style.RESET_ALL)
            missing_keys.append(k)
    if len(missing_keys) > 0:
        return False
    return True

def remove_keys(data:dict,keys:_Union[list,str],**kwargs)->dict:
    '''
        Remove matching keys from a dictionary or keep only the matching keys.

        ----------

        Arguments
        -------------------------
        `data` {dict}
            The dictionary to filter.

        `keys` {list|str}
            A key or list of keys that will be removed from the dictionary.

        Keyword Arguments
        -------------------------
        [`reverse`=False] {bool}
            If True, all keys except the ones provided will be removed.

        [`comp_values`=False] {bool}
            If True, remove keys based on their values

        Return {dict}
        ----------------------
        The dict with keys filtered.

        Meta
        ----------
        `author`: Colemen Atwood
        `created`: 06-04-2022 10:15:45
        `memberOf`: dict_utils
        `version`: 1.0
        `method_name`: remove_keys
        * @xxx [06-04-2022 10:23:17]: documentation for remove_keys
    '''
    reverse = get_kwarg(['reverse'], False, (bool), **kwargs)
    comp_values = get_kwarg(['comp_values'], False, (bool), **kwargs)
    keys = _lu.force_list(keys)


    output = {}
    for k,v in data.items():
        if comp_values is False:
            if reverse is True:
                if k in keys:
                    output[k] = v
            else:
                if k not in keys:
                    output[k] = v
        else:
            if reverse is True:
                if v in keys:
                    output[k] = v
            else:
                if v not in keys:
                    output[k] = v

    return output

def strip_nulls(data:dict)->dict:
    '''
        Remove all keys with a None value in the dictionary.

        ----------

        Arguments
        -------------------------
        `data` {dict}
            The dictionary to filter.

        Keyword Arguments
        -------------------------
        `arg_name` {type}
                arg_description

        Return {type}
        ----------------------
        return_description

        Meta
        ----------
        `author`: Colemen Atwood
        `created`: 06-08-2022 08:10:41
        `memberOf`: dict_utils
        `version`: 1.0
        `method_name`: def strip_nulls(data:dict)->dict:
        * @TODO []: documentation for def strip_nulls(data:dict)->dict:
    '''


    new_data = {}
    for k,v in data.items():
        if v is not None:
            new_data[k] = v
    return new_data

def replace_key(data:dict,find:str,replace:str,**kwargs)->dict:
    '''
        Find and rename a key in a dictionary.

        ----------

        Arguments
        -------------------------
        `data` {dict}
            The dictionary to search within.

        `find` {str}
            The key to replace.

        `replace` {str}
            The new key to rename `find` to.

        Keyword Arguments
        -------------------------
        [`case`=True] {bool}
            if False, casing is ignored.

        Return {dict}
        ----------------------
        The formatted dict with the find key renamed.

        If the find key is not found, the dictionary is unaltered.

        Meta
        ----------
        `author`: Colemen Atwood
        `created`: 06-11-2022 08:42:18
        `memberOf`: dict_utils
        `version`: 1.0
        `method_name`: replace_key
        * @xxx [06-11-2022 08:53:03]: documentation for replace_key
    '''
    case_sensitive = get_kwarg(['case','case_sensitive'],True,(bool),**kwargs)

    if case_sensitive is True:
        return {replace if k == find else k:v for k,v in data.items()}
    else:
        return {replace if k.lower() == find.lower() else k:v for k,v in data.items()}

def longest_key(data:dict)->tuple:
    '''
        Get the longest key in a dictionary.

        ----------

        Arguments
        -------------------------
        `data` {dict}
            The dictionary of strings to search within.


        Return {tuple}
        ----------------------
        If all strings are the same length, it will return the first one.
        A tuple containing the longest length and its value.\n
        (19,"kitties and titties")

        If no strings are found in the list it will return this tuple:\n
        (0,None)


        Meta
        ----------
        `author`: Colemen Atwood
        `created`: 06-10-2022 06:16:30
        `memberOf`: dict_utils
        `version`: 1.0
        `method_name`: longest_string
        * @xxx [06-10-2022 06:19:29]: documentation for longest_string
    '''
    longest_len = 0
    longest_val = None
    for val in data.keys():
        if isinstance(val,(str)):
            val_len = len(val)
            if val_len > longest_len:
                longest_len = val_len
                longest_val = val
    return (longest_len,longest_val)

def reorder_keys(data:dict,**kwargs)->dict:
    '''
        Reorder the keys in a dictionary.

        If a `keys` list/dict is provided it will sort the `data` keys to match it.
        Any keys are exit in `data` but NOT in `keys` will be appended to the end
        in alphabetical order.
        
        If `alpha` is True, it will sort the dictionary alphabetically.

        ----------

        Arguments
        -------------------------
        `data` {dict}
            The dictionary to reorder.


        Keyword Arguments
        -------------------------
        [`keys`=None] {list|dict}
            The list of keys or a dict to match the order of.

        [`alpha`=False] {bool}
            If True, the dictionary's keys will be sorted alphabetically.
            This is also the default if the `keys` arg is not provided.

        [`case`=False] {bool}
            Only applies if `alpha` is True
            If True, keys that start with lower case letters will be sorted first.

        Return {type}
        ----------------------
        return_description

        Meta
        ----------
        `author`: Colemen Atwood
        `created`: 06-11-2022 09:21:30
        `memberOf`: dict_utils
        `version`: 1.0
        `method_name`: reorder_keys
        * @TODO []: documentation for reorder_keys
    '''
    # keys:_Union[list,dict]
    keys = get_kwarg(['keys'],None,(dict,list,tuple),**kwargs)
    alphabetically = _lu.force_list(get_kwarg(['alpha'],False,(bool),**kwargs))
    case_sensitive = _lu.force_list(get_kwarg(['case','case_sensitive'],False,(bool),**kwargs))

    if keys is None:
        if alphabetically:
            # @Mstep [] get all keys from the dictionary
            dkeys = list(data.keys())
            if case_sensitive is False:
                # @Mstep [] sort the keys alphabetically.
                keys = sorted(dkeys, key=str.lower)
            if case_sensitive is True:
                keys = sorted(dkeys)



    if keys is not None:
        if isinstance(keys,(dict)):
            keys = list(keys.keys())

        new_data = {}
        # @Mstep [] find keys that exist in the data but not in the keys list.
        missing_keys = _lu.find_list_diff(keys_to_list(data),keys)
        if len(missing_keys) > 0:
            missing_keys = sorted(missing_keys, key=str.lower)

        # @Mstep [loop] iterate the keys list.
        for k in keys:
            # @Mstep [if] if the key exists in the data dictionary
            if k in data:
                # @Mstep [] add the key to the new_data dict
                new_data[k] = data[k]

        # @Mstep [LOOP] iterate the missing keys list.
        for m in missing_keys:
            # @Mstep [] add the missing keys to the end of the new_data dict
            new_data[m] = data[m]

        return new_data

def find_dict_key_diff(dict_one:dict,dict_two:dict,**kwargs)->list:
    '''
        Find keys in dict_one do that do not exist in dict_two

        ----------

        Arguments
        -------------------------
        `dict_one` {dict}
            The first dict, the primary list for comparison
        `dict_two` {dict}
            The dict to find missing keys in.

        Keyword Arguments
        -------------------------
        [`reverse`=False] {bool}
            If True, Find keys in dict_two do that do not exist in dict_one

        Return {list}
        ----------------------
        A list of keys that exist in dict_one but not dict_two

        if reverse is True,\n
        A list of keys that exist in dict_two but not dict_one


        Meta
        ----------
        `author`: Colemen Atwood
        `created`: 06-11-2022 09:16:58
        `memberOf`: dict_utils
        `version`: 1.0
        `method_name`: find_dict_key_diff
        * @xxx [06-11-2022 09:20:49]: documentation for find_dict_key_diff
    '''
    reverse = get_kwarg(['reverse'],False,(bool),**kwargs)
    if reverse is False:
        return _lu.find_list_diff(list(dict_one.keys()),list(dict_two.keys()))
    else:
        return _lu.find_list_diff(list(dict_two.keys()),list(dict_one.keys()))


def flatten(d, parent_key='', sep='.'):
    '''
        Flatten a dictionary with dot_notation.

        ----------

        Arguments
        -------------------------
        `data` {dict}
            The dictionary to flatten.

        Return {dict}
        ----------------------
        The flattened dictionary.

        Meta
        ----------
        `author`: Colemen Atwood
        `created`: 06-14-2022 13:16:43
        `memberOf`: dict_utils
        `version`: 1.0
        `method_name`: flatten
        * @xxx [06-14-2022 13:17:42]: documentation for flatten
    '''


    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, collections.MutableMapping):
            items.extend(flatten(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

class NestedNamespace(SimpleNamespace):
    def __init__(self, dictionary, **kwargs):
        # _server_type = _TypeVar('_server_type', bound=self)
        super().__init__(**kwargs)
        for key, value in dictionary.items():
            if isinstance(value, dict):
                self.__setattr__(key, NestedNamespace(value))
            else:
                self.__setattr__(key, value)


def has_method(class_instance,method_name):
    '''
        Check to see if the class has a method.

        ----------

        Arguments
        -------------------------
        `class_instance` {class}
            The class to test.
            
        `method_name` {str}
            The name of the method to search for


        Return {bool}
        ----------------------
        True if the method exists on the class, False otherwise.

        Meta
        ----------
        `author`: Colemen Atwood
        `created`: 07-04-2022 10:50:58
        `memberOf`: dict_utils
        `version`: 1.0
        `method_name`: has_method
        * @xxx [07-04-2022 10:52:26]: documentation for has_method
    '''


    result = getattr(class_instance, method_name, None)
    if result is not None:
        if callable(result):
            return True
    return False

def has_attr(class_instance,keys):
    '''
        Check if the class provided has an attribute matching a key.
        
        This is identical to calling "hasattr" except it accepts a list of keys and returns the matching one.

        ----------

        Arguments
        -------------------------
        `class_instance` {any}
            The class to search within.
            
        `keys` {list,str}
            The key or list of keys to search for.


        Return {str|bool}
        ----------------------
        The matching attribute key, if it is found, False otherwise.

        Meta
        ----------
        `author`: Colemen Atwood
        `created`: 07-11-2022 08:52:06
        `memberOf`: dict_utils
        `version`: 1.0
        `method_name`: has_attr
        * @xxx [07-11-2022 08:54:14]: documentation for has_attr
    '''


    keys = _lu.force_list(keys)
    
    
    for key in keys:
        if hasattr(class_instance,key):
            return key
        
    return False
