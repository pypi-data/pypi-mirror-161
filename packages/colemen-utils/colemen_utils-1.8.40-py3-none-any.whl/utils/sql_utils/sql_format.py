# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=line-too-long
# pylint: disable=unused-wildcard-import
# pylint: disable=wildcard-import
# pylint: disable=unused-import
'''
    A module of utility methods used for parsing SQL code.

    ----------

    Meta
    ----------
    `author`: Colemen Atwood
    `created`: 06-03-2022 10:04:06
    `memberOf`: parse_sql
    `version`: 1.0
    `method_name`: parse_sql
'''


import re as _re
import shlex as _shlex
import sqlparse as _sqlparse
from pyparsing import And, Suppress,Dict, Word, Literal, Group, Optional, ZeroOrMore, OneOrMore, Regex, restOfLine, alphanums,nums, printables, string, CaselessKeyword,nestedExpr,ParseException,quotedString,removeQuotes,originalTextFor,delimitedList,QuotedString

import utils.dict_utils as _obj
import utils.list_utils as _lu
import utils.string_utils as _csu
import utils.file_utils as _f


_sql_data_types = [
    "mediumtext",
    "mediumblob",
    "varbinary",
    "timestamp",
    "mediumint",
    "tinytext",
    "tinyblob",
    "smallint",
    "longtext",
    "longblob",
    "datetime",
    "varchar",
    "tinyint",
    "integer",
    "decimal",
    "boolean",
    "double",
    "double",
    "binary",
    "bigint",
    "float",
    "float",
    "year",
    "time",
    "text",
    "enum",
    "date",
    "char",
    "bool",
    "blob",
    "set",
    "int",
    "dec",
    "bit",
]

_sql_types_with_sizes = [
    "varbinary",
    "mediumint",
    "timestamp",
    "smallint",
    "datetime",
    "varchar",
    "decimal",
    "integer",
    "tinyint",
    "binary",
    "double",
    "double",
    "bigint",
    "float",
    "float",
    "text",
    "char",
    "time",
    "blob"
    "dec",
    "int",
    "bit",
]


def strip_comments(value:str):
    '''
        Strips single line SQL comments from a string

        ----------

        Arguments
        -------------------------
        `value` {string}
            The string to parse

        Return {string}
        ----------------------
        The formatted string

        Meta
        ----------
        `author`: Colemen Atwood
        `created`: 03-21-2022 12:28:55
        `memberOf`: parse_sql
        `version`: 1.0
        `method_name`: strip_comments
        @xxx [03-21-2022 12:29:07]: documentation for strip_comments
    '''

    value = _re.sub(r'--[^\n]*\n','',value)
    return value
    if value in _sql_data_types:
        return _sql_data_types[value]
    return None

def strip_sql_quotes(sql:str):
    '''
        Remove all quotes from an sql string.
        This includes these characters:
        - Double Quote - "
        - Single Quote - '
        - Accent/Tick  - `

        ----------

        Arguments
        -------------------------
        `value` {str}
            The string to strip of quotes.

        Return {str}
        ----------------------
        The string without quotations.

        Meta
        ----------
        `author`: Colemen Atwood
        `created`: 05-31-2022 11:56:37
        `memberOf`: parse_sql
        `version`: 1.0
        `method_name`: strip_sql_quotes
        @xxx [05-31-2022 11:58:02]: documentation for strip_sql_quotes
    '''


    sql = sql.replace("'",'')
    sql = sql.replace('"','')
    sql = sql.replace('`','')
    return sql

def escape_quoted_commas(value:str,escape_value:str="__ESCAPED_COMMA__",reverse:bool=False):
    '''
        Escape commas that are located within quotes.

        ----------

        Arguments
        -------------------------
        `value` {str}
            The string to search within
        [`escape_value`='__ESCAPED_COMMA__] {str}
            The value to replace commas with.
        `reverse` {bool}
            if True it will replace the escaped commas with actual commas.

        Return {str}
        ----------------------
        The string with escaped commas.

        Meta
        ----------
        `author`: Colemen Atwood
        `created`: 06-01-2022 06:54:48
        `memberOf`: parse_sql
        `version`: 1.0
        `method_name`: escape_quoted_commas
        @xxx [06-01-2022 06:57:45]: documentation for escape_quoted_commas
    '''

    if reverse is True:
        return value.replace(escape_value,",")

    sql_qs = QuotedString("'", esc_quote="''")
    quote = sql_qs.search_string(value)
    if len(quote) > 0:
        quote = quote.asList()
        # print(f"quote: {quote}")
        for q in quote:
            if len(q) == 1:
                q = q[0]
            esc = q.replace(",",escape_value)
            value = value.replace(q,esc)

    # print(sql_qs.search_string(value))
    return value

def escape_quoted_chars(value:str,reverse:bool=False):
    '''
        Escape characters that can effect parsing which are located within quotes.

        ----------

        Arguments
        -------------------------
        `value` {str}
            The string to search within

        `reverse` {bool}
            if True it will reverse the escaped chars with their actual chars.

        Return {str}
        ----------------------
        The string with escaped chars.

        Meta
        ----------
        `author`: Colemen Atwood
        `created`: 06-01-2022 06:54:48
        `memberOf`: parse_sql
        `version`: 1.0
        `method_name`: escape_quoted_chars
        @xxx [06-01-2022 06:57:45]: documentation for escape_quoted_chars
    '''

    escapes = [
        [",","__&#44__"],
        [";","__&#59__"],
        ["(","__&#40__"],
        [")","__&#41__"],
        ["`","__&#96__"],
        ['"',"__&#34__"],
        ["'","__&#39__"],
    ]


    if reverse is True:
        for e in escapes:
            value = value.replace(e[1],e[0])
        return value

    for e in escapes:
        sql_qs = QuotedString("'", esc_quote="''")
        quote = sql_qs.search_string(value)
        if len(quote) > 0:
            quote = quote.asList()
            # print(f"quote: {quote}")
            for q in quote:
                if len(q) == 1:
                    q = q[0]
                esc = q.replace(e[0],e[1])
                value = value.replace(q,esc)
    # print(sql_qs.search_string(value))
    return value

def format_sql_string(sql:str):
    '''
        Format an SQL string to a consistent indentation.

        ----------

        Arguments
        -------------------------
        `sql` {string}
            The sql string to mod.

        Return {string}
        ----------------------
        The formatted SQL

        Meta
        ----------
        `author`: Colemen Atwood
        `created`: 03-21-2022 12:38:32
        `version`: 1.0
        `method_name`: format_sql_string
        @xxx [03-21-2022 12:38:41]: documentation for format_sql_string
    '''
    if _f.exists(sql):
        sql = _f.readr(sql)

    sql = _csu.strip_empty_lines(sql)

    raw = sql
    # raw = _re.sub(r'^[\n]*','',raw)
    statements = _sqlparse.split(raw)
    new_contents = []
    for state in statements:
        state = _re.sub(r'^[\s\n]*','',state)
        new_state = _sqlparse.format(state, reindent=True, keyword_case='upper')
        new_contents.append(new_state)
    if len(new_contents) > 0:
        return "\n".join(new_contents)
    return False










