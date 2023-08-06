# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=line-too-long
# pylint: disable=unused-import
'''
    A module of utility methods used manipulating lists.

    ----------

    Meta
    ----------
    `author`: Colemen Atwood
    `created`: 06-03-2022 10:22:15
    `memberOf`: list_utils
'''

from typing import Iterable as _Iterable
import utils.dict_utils as _obj

from utils.string_utils.string_conversion import array_to_string_list as to_string_list
from utils.string_utils.string_format import array_replace_string as replace_from_list
from utils.string_utils.string_format import array_in_string as find_in_string



def append(base=None,value=None,**kwargs):
    '''
        Append an item to the base list.
        This is a lazy way of merging lists or appending a single item.

        ----------

        Arguments
        -------------------------
        `base` {list}
            The list to append an item to.
        `value` {any}
            The value to append to the base.

        Keyword Arguments
        -------------------------
        [`skip_null`=True] {bool}
            if True and the value is None, it will not append it.

        Return {type}
        ----------------------
        return_description

        Meta
        ----------
        `author`: Colemen Atwood
        `created`: 06-01-2022 08:45:33
        `memberOf`: objectUtils
        `version`: 1.0
        `method_name`: append
        # @TODO []: documentation for append
    '''

    if base is None:
        base = []

    skip_null = _obj.get_kwarg(["skip_null"],True,(bool),**kwargs)
    if skip_null is True:
        if value is None:
            return base

    if isinstance(value,(list)):
        base = base + value
    else:
        base.append(value)
    return base

def strip_list_nulls(value:list)->list:
    '''
        Strip None values from a list.

        ----------

        Arguments
        -------------------------
        `value` {list}
            The list to filter None values from.

        Return {list}
        ----------------------
        The list with all None values removed.

        Meta
        ----------
        `author`: Colemen Atwood
        `created`: 06-03-2022 08:38:50
        `memberOf`: objectUtils
        `version`: 1.0
        `method_name`: strip_list_nulls
        * @xxx [06-03-2022 08:39:37]: documentation for strip_list_nulls
    '''


    if isinstance(value,(list)) is False:
        return value
    return [x for x in value if x is not None]

def find_list_diff(list_one, list_two):
    '''
        find elements in list_one that do not exist in list_two.
        @param {list} list_one the primary list for comparison
        @param {list} list_two
        @function findListDiff
    '''
    return [x for x in list_one if x not in list_two]

def force_list(value)->list:
    '''
        Confirm that the value is a list, if not wrap it in a list.

        ----------

        Arguments
        -------------------------
        `value` {any}
            The value to test.

        Return {list}
        ----------------------
        The value as a list 

        Meta
        ----------
        `author`: Colemen Atwood
        `created`: 06-03-2022 09:13:57
        `memberOf`: object_utils
        `version`: 1.0
        `method_name`: force_list
        * @xxx [06-03-2022 09:14:52]: documentation for force_list
    '''


    if isinstance(value,(tuple)) is True:
        return list(value)
    if isinstance(value,(list)) is False:
        return [value]
    return value

def count(subj:list,value:any)->int:
    '''
        Count how many times a value occurs in a list.
        This is case sensitive, it will only count exact matches.

        ----------

        Arguments
        -------------------------
        `subj` {list}
            The list to search.

        `value` {any}
            The value to search for.

        Return {int}
        ----------------------
        The number of times the value occurs in the list.

        Meta
        ----------
        `author`: Colemen Atwood
        `created`: 06-07-2022 15:43:26
        `memberOf`: list_utils
        `version`: 1.0
        `method_name`: count
        * @xxx [06-07-2022 15:44:46]: documentation for count
    '''


    return len([x for x in subj if x == value])

def longest_string(arr:_Iterable[str])->tuple:
    '''
        Get the longest string in a list.

        ----------

        Arguments
        -------------------------
        `arr` {list}
            The list of strings to search within.

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
        `memberOf`: list_utils
        `version`: 1.0
        `method_name`: longest_string
        * @xxx [06-10-2022 06:19:29]: documentation for longest_string
    '''


    longest_len = 0
    longest_val = None
    for val in arr:
        if isinstance(val,(str)):
            val_len = len(val)
            if val_len > longest_len:
                longest_len = val_len
                longest_val = val
    return (longest_len,longest_val)

def remove_duplicates(arr:list)->_Iterable:
    '''
        Remove duplicate indices from a list.

        ----------

        Arguments
        -------------------------
        `arr` {list}
            The list to filter

        Return {list}
        ----------------------
        The list with duplicates removed.

        Meta
        ----------
        `author`: Colemen Atwood
        `created`: 07-04-2022 11:07:51
        `memberOf`: list_utils
        `version`: 1.0
        `method_name`: remove_duplicates
        * @xxx [07-04-2022 11:08:44]: documentation for remove_duplicates
    '''


    new_list = []
    for val in arr:
        if val not in new_list:
            new_list.append(val)
    return new_list

def lists_to_dict(keys:list,values:list):
    data = {}

    for idx,key in enumerate(keys):
        if idx <= len(values):
            data[key] = values[idx]
        else:
            data[key] = None
    return data
