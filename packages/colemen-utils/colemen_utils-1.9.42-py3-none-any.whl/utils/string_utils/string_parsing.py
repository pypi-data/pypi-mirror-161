# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=line-too-long
# pylint: disable=line-too-long
# pylint: disable=unused-import

'''
    A module of utility methods used for parsing strings

    ----------

    Meta
    ----------
    `author`: Colemen Atwood
    `created`: 06-04-2022 10:44:23
    `memberOf`: string_utils
'''


import json
# import hashlib
# import string
import re
from typing import Union as _Union
from pyparsing import QuotedString
import utils.sql_utils as sql

def determine_gender(value:str)->str:
    '''
        Use synonyms to determine the gender of a word.

        ----------

        Arguments
        -------------------------
        `value` {str}
            The word to test

        Return {str|None}
        ----------------------
        Either "male", "female" or None

        Meta
        ----------
        `author`: Colemen Atwood
        `created`: 06-04-2022 09:00:38
        `memberOf`: string_parsing
        `version`: 1.0
        `method_name`: determine_gender
        * @xxx [06-04-2022 09:02:44]: documentation for determine_gender
    '''


    female_synonyms = ['girl','female','woman','lady','miss','chica','lass','chick','grandmother','grandma','mom','mother','daughter','wife']
    male_synonyms = ['boy','male','man','dude','guy','husband','bro','grandfather','grandpa','dad','father','brother']

    value = value.lower()
    if value in female_synonyms:
        return "female"
    if value in male_synonyms:
        return "male"
    return None

def get_quoted_substrings(value:str,quote_char:str='"',esc_quote:str=None)->_Union[list,None]:
    '''
        Capture all sub strings that are quoted in the quote_char.

        ----------

        Arguments
        -------------------------
        `value` {str}
            The string to search within.
            
        [`quote_char`="] {str}
            The character to treat as the quote character
            
        [`esc_quote`=""] {str}
            The escape sequence for the quote char, if not provided, it is set to the quote char doubled.

        Return {list|None}
        ----------------------
        A list of quoted sub strings found in the value.
        If no substrings are found, it returns None

        Meta
        ----------
        `author`: Colemen Atwood
        `created`: 06-20-2022 10:47:30
        `memberOf`: string_parsing
        `version`: 1.0
        `method_name`: get_quoted_substrings
        * @xxx [06-20-2022 10:50:07]: documentation for get_quoted_substrings
    '''


    if esc_quote is None:
        esc_quote = f"{quote_char}{quote_char}"
    sql_qs = QuotedString(quote_char, esc_quote=esc_quote)
    quote = sql_qs.search_string(value)
    output = []
    if len(quote) > 0:
        qlist = quote.asList()
        q_output = []
        for q in qlist:
            if isinstance(q,(list)):
                q_output.append(q[0])
        output = q_output
        # print(f"output: {output}")
        # for q in quote:
        #     if len(q) == 1:
        #         q = q[0]
        #     esc = q.replace(e[0],e[1])
        #     value = value.replace(q,esc)
    result = output if len(output) > 0 else None
    return result




def safe_load_json(value):
    result = False
    try:
        result = json.loads(value)
    except json.decoder.JSONDecodeError as e:
        # print(e)
        # print(f"    value: {value}")
        return False

    return result



