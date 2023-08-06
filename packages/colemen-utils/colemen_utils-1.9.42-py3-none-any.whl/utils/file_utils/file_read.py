# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=line-too-long
'''
    A module of utility methods used for reading files.

    ----------

    Meta
    ----------
    `author`: Colemen Atwood
    `created`: 06-04-2022 10:58:25
    `memberOf`: file_utils
'''

from typing import Union as _Union
import json as _json
# import os as _os
import re as _re
import io as _io
import gzip as _gzip

import utils.dict_utils as _obj
import utils.string_utils as _csu
import utils.file_utils as _f


def readr(file_path:str, **kwargs):
    '''
        reads a file.

        @param {string} file_path - The path to the file to read.
        @param {boolean} [**json] - Read the file as json
        @param {boolean} [**array] - Read the file into an array of lines.
        @param {boolean} [**data_array] - Read the file into an array of line data dictionaries.

    '''
    as_type = _obj.get_kwarg(['as', 'as type'], [], (list, str), **kwargs)
    if isinstance(as_type, (str)):
        as_type = [as_type]
    read_as_json = _obj.get_kwarg(['json', 'as json'], False, bool, **kwargs)
    read_to_array = _obj.get_kwarg(['array', 'to_array'], False, bool, **kwargs)
    read_to_data_array = _obj.get_kwarg(['data_array'], False, bool, **kwargs)
    # data_array = _obj.get_kwarg(['data array'], False, bool, **kwargs)

    if read_as_json is True:
        return as_json(file_path)

    if read_to_array is True:
        return to_array(file_path)

    if read_to_data_array is True:
        return data_array(file_path)

    if "duf" in as_type:
        return duf(file_path)

    if _f.exists(file_path) is True:
        with open(file_path, 'r', encoding='utf-8') as file:
            try:
                return file.read()
            except UnicodeDecodeError:
                print(f"read_file - file_path UnicodeDecodeError: {file_path}")
    else:
        print(f"read_file - file_path does not exist: {file_path}")
        return False


def to_array(file_path:str):
    '''
        Reads a file into an array with each indice being one line.
    '''
    if _f.exists(file_path) is True:
        with open(file_path, 'r', encoding='utf-8') as file:
            try:
                file_array = file.read().splitlines()
                return file_array
            except UnicodeDecodeError:
                print(f"UnicodeDecodeError - file_path: {file_path}")
    return False


def as_json(file_path:str):
    '''
        Read a json file into a dictionary.
        strips all comments from file before reading.
    '''
    file_path = _csu.file_path(file_path)
    if _f.exists(file_path) is True:
        file_path = file_path.replace("\\", "/")
        file_contents = __parse_json_comments(file_path)
        try:
            return _json.loads(file_contents)
        except _json.decoder.JSONDecodeError as error:
            error_message = str(error)
            if "decode using utf-8-sig" in error_message:
                decoded_data = file_contents.encode().decode('utf-8-sig')
                return _json.loads(decoded_data)

            # _json.decoder.JSONDecodeError: Unexpected UTF-8 BOM(decode using utf-8-sig)
    return False


def as_template(file_path:str,replacements:dict)->_Union[str,None]:
    '''
        Read a file as a string and replace all keys with their values from the replacements dict.

        ----------

        Arguments
        -------------------------
        `file_path` {string}
            The path to the template file.
        `replacements` {dict}
            A dictionary to replace placeholders in the template file with.

        Return {str|None}
        ----------------------
        The string if successful, None otherwise.

        Meta
        ----------
        `author`: Colemen Atwood
        `created`: 06-29-2022 05:10:19
        `memberOf`: file_read
        `version`: 1.0
        `method_name`: as_template
        * @xxx [06-29-2022 05:18:17]: documentation for as_template
    '''

    contents = readr(file_path)
    contents = _csu.dict_replace_string(contents,replacements)
    return contents

def __parse_json_comments(file_path:str):
    '''
        strips comments from a json file.

        @return The contents of the file as a string.
    '''
    contents = readr(file_path)
    # file_array = data_array(file_path)
    # output_array = []
    # for file in file_array:
    #     match = _re.search(r'^\s*\/\/', file['raw_content'])
    #     if match is None:
    #         output_array.append(file)
    # contents = file_content_data_to_string(output_array)
    # strip single line comments
    # _re.findall(r'"\s*(.*\/.*?)\s*"')
    contents = _re.sub(r'^\s*\/\/[^\n\r]+',"",contents,0,_re.MULTILINE)
    # contents = _re.sub(r'\/\/[^\n\r]+',"",contents,0,_re.MULTILINE)
    # strip multiline comments
    contents = _re.sub(r'(\/\*[\s\S]*?\*\/)',"",contents,0,_re.MULTILINE)
    return contents


def data_array(file_path:str):
    final_data = []
    file_content = to_array(file_path)
    for i, line in enumerate(file_content):
        data = {}
        data['line_number'] = i
        data['raw_content'] = line
        final_data.append(data)
    return final_data


def file_content_data_to_string(file_content, **kwargs):
    """Takes an array of file content and returns the raw_content as a string"""

    strip_empty_lines = False
    if 'STRIP_EMPTY_LINES' in kwargs:
        strip_empty_lines = kwargs['STRIP_EMPTY_LINES']

    final_string = ""
    if isinstance(file_content, str):
        return file_content
    # print(f"-------file_content: {file_content}")
    for content in file_content:
        # print(f"x: {x}")
        if len(content['raw_content']) != 0 and strip_empty_lines is True or strip_empty_lines is False:
            final_string += f"{content['raw_content']}\n"
    return final_string


def duf(file_path:str):
    contents = None
    if isinstance(file_path, (dict)):
        file_path = file_path['file_path']
    try:
        with _gzip.open(file_path, 'rb') as stuff:
            with _io.TextIOWrapper(stuff, encoding='utf-8') as decoder:
                # print(f"File is compressed. - {file_path}")
                contents = _json.loads(decoder.read())
    except _gzip.BadGzipFile:
        # print(f"File is not compressed. - {file_path}")
        contents = as_json(file_path)

    return contents
