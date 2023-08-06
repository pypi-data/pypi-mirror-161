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
import json as _json
import shlex as _shlex
import sqlparse as _sqlparse
import yaml
from typing import Union as _Union

from pyparsing import And, Suppress,Dict, Word, Literal, Group, Optional, ZeroOrMore, OneOrMore, Regex, restOfLine, alphanums,nums, printables, string, CaselessKeyword,nestedExpr,ParseException,quotedString,removeQuotes,originalTextFor,delimitedList,QuotedString

import utils.dict_utils as _obj
import utils.list_utils as _lu
import utils.string_utils as _csu
import utils.file_utils as _f
import utils.sql_utils as _sql
import utils.console_utils as _console
# import config as _config
_log = _console.log


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


def is_valid_mysql_data_type(value:str):
    data = mysql_parse_type_data(value)
    if data is False or data['type'] is None:
        return False
    value = data['type']

    if value in _sql_data_types:
        return data

    value_lower = value.lower()
    if value_lower in _sql_data_types:
        data['type'] = value_lower
        return data

    varis = _csu.variations(value)
    for var in varis:
        if var in _sql_data_types:
            data["type"] = var
            return data
    return False

def mysql_parse_type_data(value:str):
    if isinstance(value,(str)) is False:
        return False
    value = value.lower()
    data = {
        "type":None,
        "size":None,
    }

    pat = _re.compile(r"([A-Za-z]*)(?:\(([0-9]*)\))?")
    match = _re.findall(pat,value)
    if match is not None:
        if len(match) > 0:
            type_name = match[0][0]
            type_size = match[0][1]
            # print(f"match[0]:{match[0]}")
            # print(f"    type_name:{type_name}")
            data['type'] = type_name
            if len(type_size) > 0:
                data['size'] = int(type_size)

    return data

def gen_mysql_type(name:str,size:int=None):
    name = name.lower()
    if size is not None:
        if name in _sql_types_with_sizes:
            return f"{name}({size})"
    if size is None:
        if name in _sql_data_types:
            return f"{name}"


def sql_type_to_python(value):
    '''
        Attempts to convert an sql type to its python equivalent.

        Keep in mind this is not exact.. at fucking all..
        This is attempting to predict how the value will need to be stored in the SQL file.

        ----------

        Arguments
        -------------------------
        `value` {str}
            The SQL type to convert.

        Return {list}
        ----------------------
        A list of similar types

        Meta
        ----------
        `author`: Colemen Atwood
        `created`: 06-02-2022 07:20:35
        `memberOf`: parse_sql
        `version`: 1.0
        `method_name`: sql_type_to_python
        * @xxx [06-02-2022 07:22:30]: documentation for sql_type_to_python
    '''

    if value in _sql_data_types:
        return _sql_data_types[value]
    return None






def _parse_statement_comment(value):
    '''
        A utility method used to parse the SQL COMMENT 'beepBoopBleepBlorp' portion of a string.

        This is intended for general use on table, column and index statements.

        ----------

        Arguments
        -------------------------
        `value` {str}
            The SQL statement to parse the comment from.

        Return {tuple}
        ----------------------
        A tuple containing the value with the comment removed and the comment itself.

        if no comment is found the second indice of the tuple is None: (value,None)

        `example`:\n
        SQL: \`modified_timestamp\`               int NULL DEFAULT NULL COMMENT 'description: The unix timestamp of when this was last modified, null otherwise.',\n
        result = ("\`modified_timestamp\`               int NULL DEFAULT NULL","description: The unix timestamp of when this was last modified, null otherwise.")


        SQL: ") COMMENT='description: Defines a registration association entity.';"\n
        result = (")","description: Defines a registration association entity.")


        Meta
        ----------
        `author`: Colemen Atwood
        `created`: 07-21-2022 08:59:41
        `memberOf`: sql_parse
        `version`: 1.0
        `method_name`: _parse_statement_comment
        * @xxx [07-21-2022 09:03:45]: documentation for _parse_statement_comment
    '''

    # @Mstep [] capture the comment if it is found in the line.
    comment_value = None
    match = _re.findall(r"(comment(?:=|\s)\'(.*)$)",value,_re.IGNORECASE)
    # match = _re.findall(r"(?:(comment(?:=|\s)\'(.*)$)|(\s+comment\s+\'(.*)$))",value,_re.IGNORECASE)
    # match = _re.findall(r"(comment(?:=|\s)\'(.*)$)",value,_re.IGNORECASE)
    if match is not None and len(match) > 0:
        match = list(match[0])
        comment_value = str(match[1])
        comment_value = _csu.strip(comment_value,["'",'"',","," ",";"])
        # print(f"table comment found: {comment_value}")
        value = value.replace(match[0],"")

    return (value,comment_value)




def parse_column_data(value=None):



    # @Mstep [] capture the comment if it is found in the line.
    value, comment_value = _parse_statement_comment(value)
    # match = _re.findall(r"(\s+comment\s+\'(.*)$)",value,_re.IGNORECASE)
    # # match = _re.findall(r"(\s+COMMENT\s+([\'\"][^\']*[\'\"]|[0-9\.]))",value,_re.IGNORECASE)
    # if match is not None and len(match) > 0:
    #     match = list(match[0])
    #     comment_value = str(match[1])
    #     comment_value = _csu.strip(comment_value,["'",'"',","," "])
    #     value = value.replace(match[0],"")


    # @Mstep [] capture the default value if it is found in the line.
    default_value = None
    match = _re.findall(r"(\s+default\s+(.*)$)",value,_re.IGNORECASE)
    if match is not None and len(match) > 0:
        match = list(match[0])
        default_value = _csu.strip(match[1]," ")
        
        if _re.match(r"^[0-9\+-\.]*$",default_value) is not None:
            default_value = int(default_value)
        value = value.replace(match[0],"")

    # print(f"value: {value}")





    # print(f"value: {value}")


    # value = "`timestamp`       int NULL DEFAULT NULL COMMENT 'Timestamp of when the task was created.' ,"
    _tick,_double_quote,_single_quote,_comma = [Suppress(x) for x in list('`"\',')]
    _quote = (_tick|_double_quote|_single_quote)
    _open_paren,_close_paren = [Suppress(x) for x in list('()')]
    # paren_word = _open_paren + Optional(_quote) + Word(alphanums + "_") + Optional(_quote) + _close_paren
    quoted_word = _quote + Word(alphanums + "_") + _quote


    column_name = quoted_word.setResultsName('name')


    ctypes = CaselessKeyword("mediumtext") | CaselessKeyword("mediumblob") | CaselessKeyword("varbinary") | CaselessKeyword("timestamp") | CaselessKeyword("mediumint") | CaselessKeyword("tinytext") | CaselessKeyword("tinyblob") | CaselessKeyword("smallint") | CaselessKeyword("longtext") | CaselessKeyword("longblob") | CaselessKeyword("datetime") | CaselessKeyword("varchar") | CaselessKeyword("tinyint") | CaselessKeyword("integer") | CaselessKeyword("decimal") | CaselessKeyword("boolean") | CaselessKeyword("double") | CaselessKeyword("double") | CaselessKeyword("binary") | CaselessKeyword("bigint") | CaselessKeyword("float") | CaselessKeyword("float") | CaselessKeyword("year") | CaselessKeyword("time") | CaselessKeyword("text") | CaselessKeyword("enum") | CaselessKeyword("date") | CaselessKeyword("char") | CaselessKeyword("bool") | CaselessKeyword("blob") | CaselessKeyword("set") | CaselessKeyword("int") | CaselessKeyword("dec") | CaselessKeyword("bit")
    ctype_len = Optional(_open_paren + Word(nums) + _close_paren)
    column_type = ctypes.setResultsName('type') + ctype_len.setResultsName('size')

    null_vals = CaselessKeyword("NULL") | CaselessKeyword("NOT NULL")
    null_type = null_vals.setResultsName('null_type')

    # def_k = Suppress(CaselessKeyword('DEFAULT'))
    # default = Optional(def_k + Word(alphanums))
    # quote = QuotedString("'", esc_quote="''",unquote_results=False).search_string(value)
    # if len(quote) > 0:
    #     # print(f"parse_column_data. quote found in column. {quote}")
    #     quote = quote[0][0]
    #     default = Optional(default|def_k + quote).setResultsName('default')
    #     # print(f"    default:{default}")

    # com_k = Suppress(CaselessKeyword('COMMENT'))
    # comment = Optional(com_k + Word(alphanums))
    # quote = QuotedString("'", esc_quote="''",unquote_results=False).search_string(value)
    # if len(quote) > 0:
    #     quote = quote[0][0]
    #     comment = Optional(com_k + quote).setResultsName('comment')



    # grammar = column_name + column_type + null_type + default + comment
    grammar = column_name + column_type + null_type
    res = ZeroOrMore(Group(grammar).setResultsName('data')).parseString(value)

    output = None

    if len(res) > 0:
        data = res.as_dict()['data']
        # print(data)
        defaults = {
            "name":None,
            "type":None,
            "allow_nulls":None,
            "default":default_value,
            "comment":comment_value,
        }
        new_data = {}
        for k,v in data.items():
            if k == "size":
                new_data[k] = int(v[0])
                continue
            if k == "null_type":
                if v.upper() == 'NOT NULL':
                    new_data['allow_nulls'] = False
                    continue
                if v.upper() == 'NULL':
                    new_data['allow_nulls'] = True
                    continue
            if isinstance(v,(list)):
                v = _csu.strip(v[0],["'",'"'])
                new_data[k] = v
                continue
            new_data[k] = v

        # print(new_data)
        new_data = _obj.set_defaults(defaults,new_data)
        output = new_data
    return output

def parse_schema_statement(value=None):

    # value = "CREATE SCHEMA IF NOT EXISTS `idealech_Equari_Content_Database`;"


    _tick,_double_quote,_single_quote,_period = [Suppress(x) for x in list('`"\'.')]
    _quote = (_tick|_double_quote|_single_quote)
    _open_paren,_close_paren = [Suppress(x) for x in list('()')]
    # paren_word = _open_paren + Optional(_quote) + Word(alphanums + "_") + Optional(_quote) + _close_paren
    quoted_word = _quote + Word(alphanums + "_") + _quote

    keys = CaselessKeyword("schema")
    create_statement = CaselessKeyword("create").setResultsName('action') + keys
    drop_statement = CaselessKeyword("drop").setResultsName('action') + keys
    action = drop_statement | create_statement


    exists = Optional(CaselessKeyword("if exists") | CaselessKeyword("if not exists")).setResultsName('test')
    schema_name = quoted_word.setResultsName('schema_name')


    grammar = action + exists + schema_name
    res = ZeroOrMore(Group(grammar).setResultsName('data')).parseString(value)

    output = None

    if len(res) > 0:
        data = res.as_dict()['data']
        # print(data)
        defaults = {
            "action":None,
            "test":None,
            "schema_name":None,
            "raw_statement":value,
        }
        new_data = {}
        for k,v in data.items():
            if isinstance(v,(list)):
                new_data[k] = v[0]
                continue
            new_data[k] = v
        new_data = _obj.set_defaults(defaults,new_data)
        # print(new_data)
        output = new_data
    return output







def parse_table_statement(value:_Union[None,str]=None)->_Union[dict,None]:
    '''
        Parse a table SQL statement.

        ----------

        Arguments
        -------------------------
        `value` {str,None}
            The SQL string to parse.

        Return {dict,None}
        ----------------------
        The statement data dictionary if it can be parsed, None otherwise.

        {
            `action`: "create",
            `test`: "if not exists",
            `schema_name`: "idealech_Equari_Management_Database",
            `table_name`: "faq_categories",
            `raw_statement`: "Original and Unmodified Create Statement Goes here.",
            `columns`: [
                {
                    "name": "faq_category_id",
                    "type": "int",
                    "allow_nulls": false,
                    "default": null,
                    "comment": null,
                    "is_primary_key": false,
                    "primary_key": true
                },
                ...
            ],
            `primary_keys`: [
                "faq_category_id"
            ],
            `keys`: [
                {
                    "key_name": "FK_FaqCategories_FaqCategoryID",
                    "foreign_col_name": [
                        "parent_faq_category_id"
                    ]
                }
            ],
            `constraints`: [
                {
                    "constraint_name": "FK_FaqCategory_Parent_FaqCategory",
                    "foreign_key": "FK_FaqCategories_FaqCategoryID",
                    "local_col_name": "parent_faq_category_id",
                    "schema_name": "idealech_Equari_Management_Database",
                    "table_name": "faq_categories",
                    "foreign_col_name": "faq_category_id",
                    "on_delete": "CASCADE",
                    "on_update": "CASCADE"
                }
            ],
            `name`: "faq_categories"
        }



        Meta
        ----------
        `author`: Colemen Atwood
        `created`: 06-05-2022 20:30:22
        `memberOf`: sql_parse
        `version`: 1.0
        `method_name`: parse_table_statement
        * @xxx [06-05-2022 20:34:11]: documentation for parse_table_statement
    '''
    # _log("sql_parse.parse_table_statement")

    # @Mstep [] capture the comment if it is found in the line.
    value,comment_value = _parse_statement_comment(value)
    # match = _re.findall(r"(comment=\'(.*)$)",value,_re.IGNORECASE)
    # if match is not None and len(match) > 0:
    #     match = list(match[0])
    #     comment_value = str(match[1])
    #     comment_value = _csu.strip(comment_value,["'",'"',","," ",";"])
    #     # print(f"table comment found: {comment_value}")
    #     value = value.replace(match[0],"")


    _tick,_double_quote,_single_quote,_period = [Suppress(x) for x in list('`"\'.')]
    _quote = (_tick|_double_quote|_single_quote)
    # _open_paren,_close_paren = [Suppress(x) for x in list('()')]
    # paren_word = _open_paren + Optional(_quote) + Word(alphanums + "_") + Optional(_quote) + _close_paren
    quoted_word = _quote + Word(alphanums + "_") + _quote


    keys = CaselessKeyword("table")
    create_statement = CaselessKeyword("create").setResultsName('action') + keys
    drop_statement = CaselessKeyword("drop").setResultsName('action') + keys
    action = drop_statement | create_statement


    exists = Optional(CaselessKeyword("if exists") | CaselessKeyword("if not exists")).setResultsName('test')
    table_name = Optional(quoted_word.setResultsName('schema_name') + _period) + quoted_word.setResultsName('table_name')


    grammar = action + exists + table_name
    res = ZeroOrMore(Group(grammar).setResultsName('data')).parseString(value)

    output = None

    if len(res) > 0:
        data = res.as_dict()['data']
        defaults = {
            "raw_statement":value,
            "action":None,
            "test":None,
            "schema_name":None,
            "table_name":None,
            "comment":comment_value,
        }
        new_data = {}
        for k,v in data.items():
            if isinstance(v,(list)):
                new_data[k] = v[0]
                continue
            new_data[k] = v
        new_data = _obj.set_defaults(defaults,new_data)

        if new_data['action'] == "create":
            cols = capture_create_table_columns(value)
            # new_data['column_data'] = _obj.strip_list_nulls([parse_column_data(x) for x in cols])
            d = _parse_table_column_lines(cols)
            new_data = {**new_data,**d}
            # new_data["columns"] = d['columns']
            # new_data["primary_keys"] = d['primary_keys']
            # new_data["unique_keys"] = d['unique_keys']
            # new_data["keys"] = d['keys']
            # new_data["constraints"] = d['constraints']
            new_data["comment"] = comment_value
        # print(new_data)
        output = new_data

    return output

def _parse_table_column_lines(lines):
    data = {
        "columns":[],
        "primary_keys":[],
        "indexes":[],
        "unique_keys":[],
        "keys":[],
        "constraints":[],
    }
    # keys = []

    for line in lines:
        # print(f"line: {line}")
        if is_line_key(line):
            # print(f"key found: {line} {parse_key(line)}")
            data['keys'] = _lu.append(data['keys'],parse_key(line))

            ft = parse_fulltext_key(line)
            if ft is not None:
                data['indexes'].append(ft)

            uk = parse_unique_key(line)
            if uk is not None:
                # print(f"Unique Key Found: {uk}")
                data['indexes'].append(uk)
                data['unique_keys'].append(uk)
                # data['unique_keys'] = _lu.append(data['unique_keys'],uk['unique_key'])

            pk = parse_primary_key(line)
            if pk is not None:
                data['indexes'].append(pk)
                data['primary_keys'] = _lu.append(data['primary_keys'],pk['primary_key'])
            # data['primary_keys'] = _lu.append(data['primary_keys'],parse_primary_key(line))

        if is_line_constraint(line):
            data['constraints'] = _lu.append(data['constraints'],parse_constraint(line))


        data['columns'] = _lu.append(data['columns'],parse_column_data(line))

        # parse_column_data(line)
    # data['keys'] = keys
    for c in data['columns']:
        c['is_primary_key'] = False
        if c['name'] in data['primary_keys']:
            c['is_primary_key'] = True



    return data

def capture_create_table_columns(sql):
    '''
        Used by parse_table_statement to capture the column area of the statement.

        ----------

        Arguments
        -------------------------
        `sql` {str}
            The create table statement to parse.

        Return {list}
        ----------------------
        A list of column declarations upon success.
        The list is empty if nothing is found.

        Meta
        ----------
        `author`: Colemen Atwood
        `created`: 06-01-2022 08:48:11
        `memberOf`: parse_sql
        `version`: 1.0
        `method_name`: capture_create_table_columns
        @xxx [06-01-2022 08:50:01]: documentation for capture_create_table_columns
    '''

    output = []
    scanner = originalTextFor(nestedExpr('(',')'))
    for match in scanner.searchString(sql):
        val = _csu.strip(match[0],["(",")"])
        val = _sql.escape_quoted_chars(val,True,['__%0A__'])
        # print(f"val: {val}")
        output = val.split("\n")
        # newlist = [_log(x,"blue") for x in output]
        # output = [_sql.escape_quoted_chars(x,True) for x in output]
        # newlist = [_log(x,"yellow") for x in output]
    return output


def _parse_list(value:str)->str:
    '''
        A utility function used for parsing an SQL string list into a more formatted version.

        ----------

        Arguments
        -------------------------
        `arg_name` {type}
                arg_description

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
        `created`: 06-05-2022 20:27:02
        `memberOf`: sql_parse
        `version`: 1.0
        `method_name`: _parse_list
        * @xxx [06-05-2022 20:28:56]: documentation for _parse_list
    '''


    value = value.asList()
    value = _sql.strip_sql_quotes(value[0])
    vals = value.split(",")
    vals = [_csu.strip(x,[" "]) for x in vals]
    return ','.join(vals)

def parse_key(value=None):
    if 'key' not in value.lower():
        return None
    # value ="KEY `FK_ActivityLogs_ActivityTypeID` (`activity_type_id`, `activity_type_hash_id`),"
    _tick,_double_quote,_single_quote,_comma = [Suppress(x) for x in list('`"\',')]
    _quote = (_tick|_double_quote|_single_quote)
    _open_paren,_close_paren = [Suppress(x) for x in list('()')]
    # paren_word = _open_paren + Optional(_quote) + Word(alphanums + "_") + Optional(_quote) + _close_paren
    quoted_word = _quote + Word(alphanums + "_") + _quote

    paren_word_list = _open_paren + Word(alphanums + "_,'\"` ") + _close_paren

    # KEY `FK_ActivityLogs_RequestLogID`
    key_name = Optional(CaselessKeyword('unique')) + Suppress(CaselessKeyword('KEY')) + quoted_word.setResultsName('key_name')

    foreign_col_name = paren_word_list.setResultsName('foreign_col_name').setParseAction(_parse_list)

    grammar = key_name + foreign_col_name
    res = ZeroOrMore(Group(grammar).setResultsName('data')).parseString(value)

    output = None

    if len(res) > 0:
        data = res.as_dict()['data']
        new_data = {}
        for k,v in data.items():
            if k == "foreign_col_name":
                new_data[k] = v.split(",")
                continue
            if isinstance(v,(list)):
                new_data[k] = v[0]
                continue
            new_data[k] = v

        # print(new_data)
        output = new_data
    return output

def parse_primary_key(value=None):
    if 'primary key' not in value.lower():
        return None
    # value = "PRIMARY KEY (`activity_log_id`)"
    # value = "PRIMARY KEY (`activity_type_id`, `activity_type_hash_id`),"
    _tick,_double_quote,_single_quote,_period = [Suppress(x) for x in list('`"\'.')]
    _quote = (_tick|_double_quote|_single_quote)
    _open_paren,_close_paren = [Suppress(x) for x in list('()')]
    # paren_word = _open_paren + Optional(_quote) + Word(alphanums + "_") + Optional(_quote) + _close_paren
    # quoted_word = _quote + Word(alphanums + "_") + _quote
    paren_word_list = _open_paren + Word(alphanums + "_,'\"` ") + _close_paren
    primary_key = paren_word_list.setResultsName('primary_key').setParseAction(_parse_list)
    grammar = Suppress(CaselessKeyword('primary key')) + primary_key
    res = ZeroOrMore(Group(grammar).setResultsName('data')).parseString(value)

    output = None

    if len(res) > 0:
        data = res.as_dict()['data']
        new_data = {
            "index_type":"primary_key"
        }
        for k,v in data.items():
            if k == "primary_key":
                new_data[k] = v.split(",")
                continue
            if isinstance(v,(list)):
                new_data[k] = v[0]
                continue
            new_data[k] = v

        # print(new_data)
        output = new_data
    return output


def parse_unique_key(value=None):

    if 'unique key' not in value.lower():
        return None
# UNIQUE KEY `Unique_barnBlocks_barnID_userID_3006` (`user_id`, `barn_id`) COMMENT 'Unique constraint to ensure a barn cannot block the same user multiple times.',

    _tick,_double_quote,_single_quote,_period = [Suppress(x) for x in list('`"\'.')]
    _quote = (_tick|_double_quote|_single_quote)
    _open_paren,_close_paren = [Suppress(x) for x in list('()')]
    # paren_word = _open_paren + Optional(_quote) + Word(alphanums + "_") + Optional(_quote) + _close_paren
    quoted_word = _quote + Word(alphanums + "_") + _quote


    paren_word_list = _open_paren + Word(alphanums + "_,'\"` ") + _close_paren
    unique_key = paren_word_list.setResultsName('columns').setParseAction(_parse_list)
    key_name = quoted_word.setResultsName('constraint_name')

    comment = None
    match = _re.findall(r"comment\s*'([^']*)",value,_re.IGNORECASE)
    if isinstance(match,(list)) and len(match) > 0:
        comment = match[0]

    grammar = Suppress(CaselessKeyword('unique key')) + key_name + unique_key
    res = ZeroOrMore(Group(grammar).setResultsName('data')).parseString(value)

    output = None

    if len(res) > 0:
        data = res.as_dict()['data']

        new_data = {
            "index_type":"unique",
            "comment":comment,
        }
        for k,v in data.items():
            if k == "columns":
                new_data[k] = v.split(",")
                continue
            if isinstance(v,(list)):
                new_data[k] = v[0]
                continue
            new_data[k] = v
        # print(f"Unique Key Data: {new_data}")
        # print(new_data)
        output = new_data
    return output

def parse_fulltext_key(value=None):
    # value = "FULLTEXT KEY `FullText_regAss_name_3079` (`name`) COMMENT 'A fullText Index on the registration association name for searching.'"

    value = _re.sub(r'full[^a-z]*text[^a-z]*key','fulltext key',value,_re.IGNORECASE)
    if 'fulltext key' not in value.lower():
        return None

    value,comment_value = _parse_statement_comment(value)
    # print(f"after comment: {value}")

    # FULLTEXT KEY `FullText_regAss_name_3079` (`name`) COMMENT 'A fullText Index on the registration association name for searching.'

    _tick,_double_quote,_single_quote,_period = [Suppress(x) for x in list('`"\'.')]
    _quote = (_tick|_double_quote|_single_quote)
    _open_paren,_close_paren = [Suppress(x) for x in list('()')]
    # paren_word = _open_paren + Optional(_quote) + Word(alphanums + "_") + Optional(_quote) + _close_paren

    # matches : `FullText_regAss_name_3079`
    quoted_word = _quote + Word(alphanums + "_") + _quote


    paren_word_list = _open_paren + Word(alphanums + "_,'\"` ") + _close_paren
    column_list = paren_word_list.setResultsName('columns').setParseAction(_parse_list)
    key_name = quoted_word.setResultsName('constraint_name')

    # comment = None
    # match = _re.findall(r"comment\s*'([^']*)",value,_re.IGNORECASE)
    # if isinstance(match,(list)) and len(match) > 0:
    #     comment = match[0]

    grammar = Suppress(CaselessKeyword('fulltext key')) + key_name + column_list
    res = ZeroOrMore(Group(grammar).setResultsName('data')).parseString(value)

    output = None

    if len(res) > 0:
        data = res.as_dict()['data']

        new_data = {
            "index_type":"fulltext",
            "comment":comment_value,
        }

        for k,v in data.items():
            if k == "columns":
                new_data[k] = v.split(",")
                continue
            if isinstance(v,(list)):
                new_data[k] = v[0]
                continue
            new_data[k] = v
        # print(f"fulltext Key Data: {new_data}")
        # print(new_data)
        output = new_data
    return output

def parse_constraint(value:str):
    '''
        Parse constraint data from the string.

        ----------

        Arguments
        -------------------------
        `value` {str}
            The string to parse.

        Return {dict,None}
        ----------------------
        The constraint data dictionary if successful, None otherwise.

        Meta
        ----------
        `author`: Colemen Atwood
        `created`: 06-05-2022 20:20:57
        `memberOf`: sql_parse
        `version`: 1.0
        `method_name`: parse_constraint
        * @xxx [06-05-2022 20:26:05]: documentation for parse_constraint
    '''


    _tick,_double_quote,_single_quote,_period = [Suppress(x) for x in list('`"\'.')]
    _quote = (_tick|_double_quote|_single_quote)
    _open_paren,_close_paren = [Suppress(x) for x in list('()')]
    paren_word = _open_paren + Optional(_quote) + Word(alphanums + "_") + Optional(_quote) + _close_paren
    quoted_word = _quote + Word(alphanums + "_") + _quote


    constraint_conditions = (CaselessKeyword('RESTRICT') | CaselessKeyword('CASCADE') | CaselessKeyword('SET NULL') | CaselessKeyword('NO ACTION') | CaselessKeyword('SET DEFAULT'))


    constraint_name = Suppress(CaselessKeyword('CONSTRAINT')) + quoted_word.setResultsName('constraint_name')


    foreign_key_name = Suppress(CaselessKeyword('FOREIGN KEY')) + quoted_word.setResultsName('foreign_key')
    local_col_name = paren_word.setResultsName('local_col_name')
    foreign_table = Suppress(CaselessKeyword('REFERENCES')) + Optional(quoted_word.setResultsName('schema_name') + _period) + quoted_word.setResultsName('table_name')
    foreign_col_name = paren_word.setResultsName('foreign_col_name')

    on_delete = Suppress(CaselessKeyword('ON DELETE')) + constraint_conditions.setResultsName('on_delete')
    on_update = Suppress(CaselessKeyword('ON UPDATE')) + constraint_conditions.setResultsName('on_update')
    constraints = ZeroOrMore(on_delete | on_update)

    grammar = constraint_name + foreign_key_name + local_col_name + foreign_table + foreign_col_name + constraints
    res = ZeroOrMore(Group(grammar).setResultsName('data')).parseString(value)

    output = None

    comment = None
    match = _re.findall(r"comment\s*'([^']*)",value,_re.IGNORECASE)
    if isinstance(match,(list)) and len(match) > 0:
        comment = match[0]

    if len(res) > 0:
        data = res.as_dict()['data']
        new_data = {
            "comment":comment
        }
        for k,v in data.items():
            if isinstance(v,(list)):
                new_data[k] = v[0]
                continue
            new_data[k] = v

        # print(new_data)
        output = new_data
    return output


# def parse_allow_null(col_data):
#     '''
#         Determines if the column is allowed to be null.

#         ----------

#         Arguments
#         -------------------------
#         `col_data` {dict}
#             The column_data dictionary produced by parse_table_columns
#             Must include the shlexed property.

#         Return {dict}
#         ----------------------
#         The col_data dictionary with an updated allow_nulls property.

#         Meta
#         ----------
#         `author`: Colemen Atwood
#         `created`: 05-31-2022 07:29:36
#         `memberOf`: TableManager
#         `version`: 1.0
#         `method_name`: parse_allow_null
#         @xxx [05-31-2022 07:31:12]: documentation for parse_allow_null
#     '''

#     nn_found = False
#     for s in col_data['shlexed']:
#         if _csu.array_in_string(["not null","NOT NULL"],s,False):
#             nn_found = True
#     if nn_found is False:
#         col_data['allow_nulls'] = True
#     return col_data

# def parse_col_comment(col_data):
#     '''
#         Captures a comment related to the column.

#         ----------

#         Arguments
#         -------------------------
#         `col_data` {dict}
#             The column_data dictionary produced by parse_table_columns
#             Must include the shlexed property.


#         Return {dict}
#         ----------------------
#         The col_data dictionary with an updated comment property.

#         Meta
#         ----------
#         `author`: Colemen Atwood
#         `created`: 05-31-2022 07:52:33
#         `memberOf`: TableManager
#         `version`: 1.0
#         `method_name`: parse_col_comment
#         @xxx [05-31-2022 07:53:42]: documentation for parse_col_comment
#     '''


#     for s in col_data['shlexed']:
#         # s = s.lower()
#         # print(f"s: {s}")
#         if s.lower().startswith('comment'):
#             # _re.replace(r'^comment\s*')
#             cmt = s.replace('comment','')
#             cmt = _sql.escape_quoted_chars(cmt,True)
#             col_data['comment'] = _csu.strip(cmt,[" "])
#             break

#     return col_data

# def parse_col_type(col_data):
#     '''
#         Parses the SQL column type from the column data.

#         ----------

#         Arguments
#         -------------------------
#         `col_data` {dict}
#             The column_data dictionary produced by parse_table_columns
#             Must include the shlexed property.

#         Return {dict}
#         ----------------------
#         The col_data dictionary with an updated data_type property.


#         Meta
#         ----------
#         `author`: Colemen Atwood
#         `created`: 05-31-2022 07:54:14
#         `memberOf`: TableManager
#         `version`: 1.0
#         `method_name`: parse_col_type
#         @xxx [05-31-2022 07:54:59]: documentation for parse_col_type
#     '''

#     for t in col_data['shlexed']:
#         for sql_type in _sql_data_types:
#             if sql_type in t.lower():
#                 col_data['data_type'] = sql_type
#                 break

#         col_data['size'] = parse_column_size(t)
#         break
#     # lower_raw = col_data['raw_type'].lower()
#     # for t in _sql_data_types:
#     #     if lower_raw.startswith(t):
#     #         # print(f"data type: {t}")
#     #         col_data['data_type'] = t
#     #         break
#     return col_data

# def parse_column_size(type_string):
#     '''
#         Called by parse_col_type
#         This will capture the column size if the type supports it.

#         ----------

#         Arguments
#         -------------------------
#         `type_string` {str}
#             The type of the column, example: "varchar(500)"

#         Return {int|None}
#         ----------------------
#         The integer size of the column upon success, None otherwise.

#         Meta
#         ----------
#         `author`: Colemen Atwood
#         `created`: 05-31-2022 07:26:51
#         `memberOf`: TableManager
#         `version`: 1.0
#         `method_name`: parse_column_size
#         @xxx [05-31-2022 07:28:25]: documentation for parse_column_size
#     '''


#     lower_raw = type_string.lower()
#     for sc in _sql_types_with_sizes:
#         if sc in lower_raw:
#             pat = _re.compile(sc+r"\(([0-9]*)\)")
#             match = _re.findall(pat,lower_raw)
#             if match is not None:
#                 if len(match) > 0:
#                     return int(match[0])
#     return None

# def strip_keys_constraints(sql):
#     output = {
#         "sql":[],
#         "keys":[],
#         "constraints":[],
#     }
#     lines = sql.split("\n")
#     for line in lines:
#         if len(line) == 0 or is_line_comment(line):
#             continue
#         line = _sql.escape_quoted_commas(line)
#         # print(f"line: {line}")
#         if is_line_key(line):
#             output['keys'].append(line)
#             continue
#         if is_line_constraint(line):
#             output['constraints'].append(line)
#             continue
#         # match = _re.findall(r'^(\w+\s*)?key',line,_re.IGNORECASE)
#         # match = _re.findall(r'^((\w+\s*)?key|constraint)',line,_re.IGNORECASE)
#         output['sql'].append(line)
#     output['sql'] = '\n'.join(output['sql'])

#     if len(output['keys']) > 0:
#         primary_keys = []
#         unique_keys = []
#         for k in output['keys']:
#             data = parse_primary_keys(k)
#             if len(data) > 0:
#                 primary_keys = data
#                 continue

#             uk_data = parse_unique_key(k)
#             if uk_data is not None:
#                 print(f"Unique Key successfully parsed.")
#                 unique_keys.append(uk_data)
#                 continue
#         output['primary_keys'] = primary_keys
#         output['unique_keys'] = unique_keys

#     if len(output['constraints']) > 0:
#         foreign_keys = []
#         for k in output['constraints']:
#             data = parse_constraint(k)
#             if data is not None:
#                 foreign_keys.append(data)
#                 continue

#             data = parse_key(k)
#             if data is not None:
#                 foreign_keys.append(data)
#                 continue

#         output['foreign_keys'] = foreign_keys

#     return output

def is_line_key(line:str)->bool:
    '''
        Test if the line contains a key constraint or statement.

        ----------

        Arguments
        -------------------------
        `line` {str}
            The string to parse.

        Return {bool}
        ----------------------
        True upon success, false otherwise.

        Meta
        ----------
        `author`: Colemen Atwood
        `created`: 06-05-2022 20:16:42
        `memberOf`: sql_parse
        `version`: 1.0
        `method_name`: is_line_key
        * @xxx [06-05-2022 20:17:55]: documentation for is_line_key
    '''

    match = _re.match(r'^(\w+\s*)?key',line,_re.IGNORECASE)
    if match is not None:
        return True
    return False

def is_line_comment(line:str)->bool:
    '''
        Determine if the line is commented.

        ----------

        Arguments
        -------------------------
        `line` {str}
            The string to parse.

        Return {bool}
        ----------------------
        True if the line is commented, False otherwise.

        Meta
        ----------
        `author`: Colemen Atwood
        `created`: 06-05-2022 20:13:33
        `memberOf`: sql_parse
        `version`: 1.0
        `method_name`: is_line_comment
        * @xxx [06-05-2022 20:14:45]: documentation for is_line_comment
    '''

    match = _re.match(r'^--',line,_re.IGNORECASE)
    if match is not None:
        return True
    return False

def is_line_constraint(line:str)->bool:
    '''
        Determine if the line provided contains a constraint.
        This is used to quickly test the strings before actually parsing, just to save time.

        ----------

        Arguments
        -------------------------
        `line` {str}
            The string to parse.

        Return {bool}
        ----------------------
        True if it contains a constraint, False otherwise.

        Meta
        ----------
        `author`: Colemen Atwood
        `created`: 06-05-2022 20:11:27
        `memberOf`: sql_parse
        `version`: 1.0
        `method_name`: is_line_constraint
        * @xxx [06-05-2022 20:13:17]: documentation for is_line_constraint
    '''


    match = _re.match(r'^constraint',line,_re.IGNORECASE)
    if match is not None:
        return True
    return False

# def parse_primary_keys(sql:str)->list:
#     '''
#         Parse the primary keys from a SQL string.

#         ----------

#         Arguments
#         -------------------------
#         `sql` {str}
#             The SQL string to parse.

#         Return {list}
#         ----------------------
#         A list of primary keys.

#         Meta
#         ----------
#         `author`: Colemen Atwood
#         `created`: 06-05-2022 20:18:46
#         `memberOf`: sql_parse
#         `version`: 1.0
#         `method_name`: parse_primary_keys
#         * @xxx [06-05-2022 20:20:08]: documentation for parse_primary_keys
#     '''


#     primary_keys = []
#     match = _re.findall(r'primary\s*key\s*\(([a-zA-Z0-9_,\`\'\"\s]*)\)',sql,_re.IGNORECASE)
#     if match is not None:
#         if len(match) > 0:
#             keys = _sql.strip_sql_quotes(match[0])
#             keys = keys.split(",")
#             keys = [_csu.strip(x,[" "]) for x in keys]
#             primary_keys = keys
#         # print(match)
#     return primary_keys

# def format_sql_string(sql:str):
#     '''
#         Format an SQL string to a consistent indentation.

#         ----------

#         Arguments
#         -------------------------
#         `sql` {string}
#             The sql string to mod.

#         Return {string}
#         ----------------------
#         The formatted SQL

#         Meta
#         ----------
#         `author`: Colemen Atwood
#         `created`: 03-21-2022 12:38:32
#         `version`: 1.0
#         `method_name`: format_sql_string
#         @xxx [03-21-2022 12:38:41]: documentation for format_sql_string
#     '''
#     if _f.exists(sql):
#         sql = _f.readr(sql)

#     sql = _csu.strip_empty_lines(sql)

#     raw = sql
#     # raw = _re.sub(r'^[\n]*','',raw)
#     statements = _sqlparse.split(raw)
#     new_contents = []
#     for state in statements:
#         state = _re.sub(r'^[\s\n]*','',state)
#         new_state = _sqlparse.format(state, reindent=True, keyword_case='upper')
#         new_contents.append(new_state)
#     if len(new_contents) > 0:
#         return "\n".join(new_contents)
#     return False


# def _parse_table_comment(table:Table):
#     '''
#         Parse the Columns YAML comment into the Column's data dictionary.

#         ----------

#         Arguments
#         -------------------------
#         `col` {Column}
#             The instance of the column to parse.

#         Meta
#         ----------
#         `author`: Colemen Atwood
#         `created`: 07-03-2022 11:22:39
#         `memberOf`: Column
#         `version`: 1.0
#         `method_name`: _parse_col_data
#         * @xxx [07-03-2022 11:23:39]: documentation for _parse_col_data
#     '''

#     comment = table.comment
#     if isinstance(comment,(str)) is False:
#         comment = ""

#     if comment is None:
#         return None
#     try:
#         result = _parse_comment_yaml(comment)
#     except yaml.scanner.ScannerError:
#         c.con.log(f"Failed to parse comment for table: {table.name}","error")
#         return False

#     if isinstance(result,(dict)):
#         if 'hash_id_prefix' in result:
#             result['is_hash_id'] = True
#         table.data = {**table.data,**result}
#         # table.data['raw_yaml'] = result

def _parse_comment_yaml(contents):
    if len(contents) == 0:
        return None
    if isinstance(contents,(str)) is False:
        contents = ""

    # contents = contents.replace("\n","   ")
    contents = contents.replace("desc:","description:")
    contents = contents.replace("opts:","options:")
    contents = contents.replace("o:","options:")

    # contents = contents.replace("options:","options:\n")



    if len(contents) > 0:
        if contents.startswith("description:") is False:
            contents = f"description: {contents}"

        if "description:" not in contents:
            contents = f"description: {contents}"
    else:
        return None
    # @Mstep [] force a space between a dash and alphanum characters.
    contents = _re.sub(r"\n-([a-zA-Z0-9])",r"\n- \1",contents)
    # @Mstep [] force a space between a key's colon and the value following it.
    contents = _re.sub(r"(\n-\s*[a-zA-Z0-9_ ]*:\s*)",r"\1 ",contents)

    try:
        # result = _parse_comment_yaml(comment)
        data = yaml.safe_load(contents)
    except yaml.scanner.ScannerError:
        return None
    # c.con.log(f"contents: {contents}","red")
    output = {}
    if "description" in data:
        output['description'] = data['description']

    if "options" in data:
        if data['options'] is not None:
            for opt in data['options']:
                if isinstance(opt,(str)):
                    output[_csu.to_snake_case(opt)] = True
                if isinstance(opt,(dict)):
                    for k,value in opt.items():
                        output[_csu.to_snake_case(k)] = value
    # print(output)
    return output





def get_statements(sql:str):
    '''
        Parses the SQL statements from the string.

        ----------

        Arguments
        -------------------------
        `sql` {string}
            The sql string to parse.

        Return {list}
        ----------------------
        A list of SQL statements.

        Meta
        ----------
        `author`: Colemen Atwood
        `created`: 03-21-2022 12:40:52
        `version`: 1.0
        `method_name`: get_statements
        @xxx [03-21-2022 12:40:58]: documentation for get_statements
    '''


    raw = sql
    if isinstance(sql,(str)):
        if _f.exists(sql):
            raw = _f.readr(sql)
    # @Mstep [] remove single line comments from the sql.
    raw = _sql.strip_comments(raw)
    # @Mstep [] escape special characters that are within quotes.
    raw = _sql.escape_quoted_chars(raw)
    # raw = format_sql_string(raw)
    statements = [x for x in _sqlparse.parse(raw)]
    return statements

def determine_statement_purpose(statement:str):
    '''
        Determine the purpose of the SQL statement.

        ----------

        Arguments
        -------------------------
        `statement` {str}
            The SQL statement to parse.

        Return {str|None}
        ----------------------
        The statement's purpose or None

        Meta
        ----------
        `author`: Colemen Atwood
        `created`: 06-05-2022 20:08:22
        `memberOf`: sql_parse
        `version`: 1.0
        `method_name`: determine_statement_purpose
        * @xxx [06-05-2022 20:10:56]: documentation for determine_statement_purpose
    '''

    # _log("sql_parse.determine_statement_purpose")
    statement_types = ["CREATE DATABASE","ALTER DATABASE","CREATE SCHEMA","CREATE INDEX","CREATE TABLE","ALTER TABLE","INSERT INTO","DROP INDEX","DROP TABLE","DELETE","UPDATE","SELECT",]
    for s in statement_types:
        if s in statement.upper():
            return s

    return None

def parse(sql):
    _log("sql_parse.parse")
    if _f.exists(sql):
        _log(f"    Reading SQL file: {sql}")
        sql = _f.readr(sql)

    if len(sql)== 0:
        return None

    sql = _csu.strip_empty_lines(sql)
    raw_statements = get_statements(sql)
    # print(f"raw_statements: {raw_statements}")
    data = {
        "schemas":[],
        "tables":[],
        "statements":[],
    }

    for s in raw_statements:
        s = s.value
        # print(f"s: {s}")
        state = {
            "raw":s,
            "purpose":determine_statement_purpose(s),
            "data":None,
        }
        if state['purpose'] is None:
            _log(f"    Failed to determine purpose of statement:\n {s}","error")
            continue

        if state['purpose'] == "CREATE TABLE":
            # _log(f"    Create Table Statement found statement:\n {s}","success")
            state['data'] = parse_table_statement(state['raw'])
            _lu.append(data['tables'],state['data'])
            continue

        if state['purpose'] == "CREATE SCHEMA":
            state['data'] = parse_schema_statement(state['raw'])
            _lu.append(data['schemas'],state['data'])
            continue

        data['statements'].append(state)

    data = _parse_data_comments(data)
    return data

def _parse_json_yaml(comment):
    if comment is not None:
        if isinstance(comment,(str)):
            comment = _sql.escape_quoted_chars(comment,True)
            json = _csu.parse.safe_load_json(comment)
            if json:
                return (comment,json)
            else:
                json = _parse_comment_yaml(comment)
                if json:
                    return (comment,json)
    return (comment,{})

def _parse_data_comments(data):
    new_tables = []
    for tb in data['tables']:
        # print(f"tb['comment']:{tb['comment']}")
        tb['comment'],json = _parse_json_yaml(tb['comment'])
        tb['orig_comment'] = tb['comment']
        tb['comment'] = json
        # tb = {**tb,**json}
        new_tables.append(tb)
        # if tb['comment'] is not None:
        #     tb['comment'] = _sql.escape_quoted_chars(tb['comment'],True)
        #     json = _parse_comment_yaml(tb['comment'])
        #     if json:
        #         tb = {**tb,**json}

        if 'columns' in tb:
            new_cols = []
            for col in tb['columns']:
                col['comment'],json = _parse_json_yaml(col['comment'])
                col = {**col,**json}
                new_cols.append(col)

                # col['comment']
                # if col['comment'] is not None:
                #     if isinstance(col['comment'],(str)):
                #         col['comment'] = _sql.escape_quoted_chars(col['comment'],True)
                #         json = _csu.parse.safe_load_json(col['comment'])
                #         if json:
                #             col = {**col,**json}
                #             col['json_comment_found'] = True
                #             new_cols.append(col)
                #         else:
                #             json = _parse_comment_yaml(col['comment'])
                #             if json:
                #                 col = {**col,**json}
                #                 col['yaml_comment_found'] = True
                #                 new_cols.append(col)
                # else:
                    # new_cols.append(col)
            tb['columns'] = new_cols
        # new_tables.append(tb)
    data['tables'] = new_tables
    return data







