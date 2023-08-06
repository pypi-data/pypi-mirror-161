# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=line-too-long
# pylint: disable=unused-wildcard-import
# pylint: disable=wildcard-import
# pylint: disable=unused-import
# pylint: disable=import-outside-toplevel
# pylint: disable=fixme
'''
    A class used to manage the rows of a diagram table.

    ----------

    Meta
    ----------
    `author`: Colemen Atwood
    `created`: 07-05-2022 08:54:14
    `memberOf`: database_utils.drawio
    `name`: Row
    * @xxx [07-05-2022 08:55:08]: documentation for Row
'''

import re
import time
import json


from config import _db_dio_table,_mxcell_type,_Iterable,_db_dio_parser_type,_db_dio_foreign_key_type
import utils.string_utils as _csu
import utils.type_utils as _types
import utils.list_utils as _arr
import utils.database_utils.drawio.entity_utils as _entity_utils
import utils.dict_utils as _obj
import utils.file_utils as _f
import utils.console_utils as _con
log = _con.log


# _ROW_SQL_TEMPLATE = """`__COLUMN_NAME__`__INDENT____DATA_TYPE__ __NULL__ __DEFAULT_REP__ __AUTO_INC__ __COMMENT_SQL__"""

class Schema:

    def __init__(self,main:_db_dio_parser_type,args=None):
        self.args = {} if args is None else args
        self.main = main

        self.settings = {}
        self.data = {
            "name":None,
            "tables":None,
            "drop_sql":None,
            "create_sql":None,
        }

        self.data = _obj.set_defaults(self.data,self.args)
        main.register('schema',self)

    @property
    def summary(self):
        '''
            Get this Schema's summary


            `default`:None


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-06-2022 08:27:07
            `@memberOf`: Schema
            `@property`: summary
        '''
        _entity_utils.trigger_attributes(self)
        data = self.data.copy()
        data['tables'] = [x.name for x in self.tables]
        return data

    @property
    def name(self):
        '''
            Get this Schema's name


            `default`:None


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-06-2022 08:33:16
            `@memberOf`: Schema
            `@property`: name
        '''
        return self.data['name']

    @property
    def tables(self):
        '''
            Get this Schema's table instances.


            `default`:None


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-06-2022 08:28:13
            `@memberOf`: Schema
            `@property`: tables
        '''
        return self.data['tables']

    @property
    def create_sql(self):
        '''
            Get this Schema's create_sql


            `default`:None


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-06-2022 08:45:16
            `@memberOf`: Schema
            `@property`: create_sql
        '''
        value = _obj.get_arg(self.data,['sql'],None,(str))
        # @Mstep [IF] if the property is not currenty set
        if value is None:
            value = _gen_create_sql(self)
            self.data['sql'] = value
        return value

    @property
    def sql(self):
        '''
            Get this Schema's sql


            `default`:None


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-06-2022 09:17:16
            `@memberOf`: Schema
            `@property`: sql
        '''
        value = _gen_create_sql(self)
        self.data['create_sql'] = value
        return value
        

def generate_schemas(main)->_Iterable[Schema]:
    schemas = {}
    for table in main.tables:
        schema = table.schema
        if schema is None:
            continue
        if _csu.to_snake_case(schema) not in schemas:
            schemas[schema] = {
                "name":schema,
                "tables":[table]
            }
        else:
            schemas[schema]['tables'].append(table)

    instances = []

    for _,schema in schemas.items():
        instances.append(Schema(main,schema))
    return instances
    
    
def _gen_create_sql(schema:Schema)->str:
    qc = schema.main.sql_quote_char
    sql = ""
    if isinstance(schema.name,(str)) and len(schema.name) > 0:
        sql = f"CREATE SCHEMA IF NOT EXISTS {qc}{schema.name}{qc};"
    return sql

