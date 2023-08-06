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

from multiprocessing.sharedctypes import Value
import re
import time
import json


from config import _db_dio_table,_mxcell_type,_Iterable,_db_dio_parser_type,_db_dio_foreign_key_type,_Union
import utils.string_utils as _csu
import utils.type_utils as _types
import utils.list_utils as _arr
import utils.database_utils.drawio.entity_utils as _entity_utils
import utils.dict_utils as _obj
import utils.file_utils as _f
import utils.console_utils as _con
import utils.sql_utils as _sql
log = _con.log




# _ROW_SQL_TEMPLATE = """`__COLUMN_NAME__`__INDENT____DATA_TYPE__ __NULL__ __DEFAULT_REP__ __AUTO_INC__ __COMMENT_SQL__"""

class Row:
    '''
        This class represents a row in a database table's node.

        In the actual database, this is a COLUMN.

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
        `created`: 07-04-2022 12:32:11
        `memberOf`: Row
        `version`: 1.0
        `method_name`: Row
        * @TODO []: documentation for Row
    '''


    def __init__(self,main:_db_dio_parser_type,table:_db_dio_table,row=None,args=None):
        self.args = {} if args is None else args
        self.main = main
        # self._node = row
        self._node = _obj.get_arg(self.args,['row','element'],row)
        self.args = _obj.remove_keys(self.args,['row','element'])
        
        # A reference to the table entity
        self._table:_db_dio_table = table

        self._target_connectors:_Iterable[_db_dio_foreign_key_type] = []
        self._source_connectors:_Iterable[_db_dio_foreign_key_type] = []
        # self._connectors:_Iterable[_db_dio_foreign_key_type] = []
        self.settings = {
            "missing_name":False,
            "missing_type":False,
        }
        self.data = {
            "table_name":None,
            "schema_name":None,
            "column_key":None,
            "column_name":None,
            "column_type":None,
            "column_default_value":None,
            "column_allow_null":None,
            "column_extra":None,
            "column_comment":None,
            "column_unique":None,
            "size":None,
            "name":None,
            "is_primary_key":None,
            "is_foreign_key":None,
            "allow_nulls":None,
            "is_unique":None,
            "is_auto_increment":None,
            "null":None,
            "data_type":None,
            "default":None,
            "comment":None,
            "default_rep":None,
            "comment_sql":None,
            "sql":None,
        }

        # _parse_data(self)
        
        self.data = _obj.set_defaults(self.data,self.args)
        print(f"self.data: {self.data}")
        self.main.register('row',self)
        # _entity_utils.trigger_attributes(self)
        # print(json.dumps(self.data,indent=4))

    @property
    def missing_data(self):
        '''
            Get this Row's missing_data


            `default`:None


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-06-2022 08:04:10
            `@memberOf`: Row
            `@property`: missing_data
        '''
        missing_data = False
        if self.data['name'] is None:
            self.settings['missing_name'] = True
            log(f"Column missing name in {self.table.name}","error")
            missing_data = True
        if self.data['data_type'] is None:
            self.settings['data_type'] = True
            log(f"Column missing type in {self.table.name}","error")
            missing_data = True

        return missing_data

    @property
    def node_id(self):
        '''
            Get this DrawioColumn's node_id


            `default`:None


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-04-2022 11:24:29
            `@memberOf`: DrawioColumn
            `@property`: node_id
        '''
        return self._node.get_id()

    @property
    def node(self)->_mxcell_type:
        '''
            Get this DrawioColumn's node


            `default`:None


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-04-2022 11:59:50
            `@memberOf`: DrawioColumn
            `@property`: node
        '''
        return self._node

    @property
    def summary(self):
        '''
            Get this Row's summary


            `default`:None


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-05-2022 09:28:34
            `@memberOf`: Row
            `@property`: summary
        '''
        _entity_utils.trigger_attributes(self)
        return self.data




    @property
    def table(self)->_db_dio_table:
        '''
            Get the instance of the table that this row belongs to.


            `default`:None


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-05-2022 09:21:41
            `@memberOf`: Row
            `@property`: table
        '''
        return self._table

    @property
    def data_type(self):
        '''
            Get this Row's data_type


            `default`:None


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-04-2022 14:36:37
            `@memberOf`: Row
            `@property`: data_type
        '''
        value = _obj.get_arg(self.data,['data_type'],None,(str))
        # @Mstep [IF] if the property is not currenty set
        if value is None:
            
            # size = _sql.parse_column_size(self.data['column_type'])
            
            
            # if _sql.is_valid_mysql_data_type(self.data['column_type']):
                # raise ValueError(f"Unknown column type: {column_type}")
            
            result = _sql.is_valid_mysql_data_type(self.data['column_type'])
            if isinstance(result,(dict)) is False:
                raise ValueError(f"{value} is not a recognized data type.")
            # TODO []: add custom types [unix_timestamp]
            value = result['type']
            self.size = result['size']
            self.data['data_type'] = value
        return value

    @data_type.setter
    def data_type(self,value:_Union[int,str]):
        '''
            Set this Row's data_type


            `default`:None


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-04-2022 14:36:37
            `@memberOf`: Row
            `@property`: data_type
        '''
        result = _sql.is_valid_mysql_data_type(value)
        if isinstance(result,(dict)) is False:
            raise ValueError(f"{value} is not a recognized data type.")

        # TODO []: add custom types [unix_timestamp]
        self.data['column_type'] = result['type']
        self.data['data_type'] = result['type']
        self.size = result['size']

    @property
    def default(self):
        '''
            Get this Row's default


            `default`:None


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-04-2022 15:23:59
            `@memberOf`: Row
            `@property`: default
        '''
        value = _obj.get_arg(self.data,['column_default_value'],None,(str))
        # @Mstep [IF] if the property is not currenty set
        if value is None:
            value = None
        if isinstance(value,(str)) and  len(value) == 0:
            value = None

        self.data['default'] = value
        return value

    @property
    def sql(self):
        '''
            Get this Row's sql


            `default`:None


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-04-2022 14:33:31
            `@memberOf`: Row
            `@property`: sql
        '''
        value = _obj.get_arg(self.data,['sql'],None,(str))
        # @Mstep [IF] if the property is not currenty set
        if value is None:
            # self.data['indent'] = " " *
            # column_name = _gen_sql_col_name(self)
            # indent = _csu.rightPad(column_name,len(self.table.longest_row_name)," ")


            # f"{column_name}{indent}{data_type}{allow_null}{default_value}{auto_inc}{comment}"
            # replacements = _entity_utils.gen_replacements(self.data)
            # value = _csu.dict_replace_string(_ROW_SQL_TEMPLATE,replacements)
            # value = _csu.strip(value," ")
            self.data['sql'] = _gen_sql(self)
        return value

    @property
    def comment(self):
        '''
            Get this Row's comment


            `default`:None


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-04-2022 15:21:28
            `@memberOf`: Row
            `@property`: comment
        '''
        value = _obj.get_arg(self.data,['comment'],None,(str))
        # @Mstep [IF] if the property is not currenty set
        if value is None:
            value = self.data['column_comment']
            value = value.replace("{table_name}",self.table.singular_name)
            self.data['comment'] = value
            self.data['comment_sql'] = f"COMMENT '{value}'"
        return value

    @property
    def size(self):
        '''
            Get this Row's size


            `default`:None


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-04-2022 14:30:35
            `@memberOf`: Row
            `@property`: size
        '''
        value = _obj.get_arg(self.data,['column_size'],None,(int))
        # @Mstep [IF] if the property is not currenty set
        if value is None:
            # TODO []: parse table size
            value = self.data['size']
            self.data['column_size'] = value
        return value

    @size.setter
    def size(self,value):
        '''
            set this Row's size


            `default`:None


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-04-2022 14:30:35
            `@memberOf`: Row
            `@property`: size
        '''
        if isinstance(value,(str)):
            value = int(value)
        
        if isinstance(value,(int)):
            self.data['size'] = value
        

    @property
    def is_auto_increment(self):
        '''
            Get this Row's is_auto_increment


            `default`:None


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-04-2022 14:25:29
            `@memberOf`: Row
            `@property`: is_auto_increment
        '''
        value = _obj.get_arg(self.data,['is_auto_increment'],None,(bool))
        # @Mstep [IF] if the property is not currently set
        if value is None:
            value = False
            self.data['auto_inc'] = ""
            if _arr.find_in_string(['auto_increment','ai'],self.data['column_extra'].lower(),False):
                self.data['auto_inc'] = "AUTO_INCREMENT"
                value = True
            self.data['is_auto_increment'] = value
        return value

    @property
    def is_primary_key(self):
        '''
            Get this Row's is_primary_key


            `default`:None


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-04-2022 13:59:11
            `@memberOf`: Row
            `@property`: is_primary_key
        '''
        value = _obj.get_arg(self.data,['is_primary_key'],None,(bool))
        # @Mstep [IF] if the property is not currenty set
        if value is None:
            value = False
            if 'pk' in self.data['column_key'].lower():
                value = True

            self.data['is_primary_key'] = value
        return value

    @property
    def is_foreign_key(self):
        '''
            Get this Row's is_foreign_key


            `default`:None


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-04-2022 14:00:54
            `@memberOf`: Row
            `@property`: is_foreign_key
        '''
        value = _obj.get_arg(self.data,['is_foreign_key'],None,(bool))
        # @Mstep [IF] if the property is not currenty set
        if value is None:
            value = False

            cons = self.target_connectors
            if len(cons) > 0:
                value = True
            if 'fk' in self.data['column_key'].lower():
                value = True

            self.data['is_foreign_key'] = value
        return value

    @property
    def target_connectors(self):
        '''
            Get this Row's target_connectors


            `default`:None


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-05-2022 12:22:20
            `@memberOf`: Row
            `@property`: target_connectors
        '''
        connectors = self.main.drawing.diagram.get_connectors(self.node_id)

    @property
    def source_connectors(self):
        '''
            Get this Row's source_connectors


            `default`:None


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-05-2022 12:23:35
            `@memberOf`: Row
            `@property`: source_connectors
        '''
        # cons = self.node.diagram.get_connectors(None,self.node_id)
        # self._source_connectors = cons
        # return cons



    @property
    def is_unique(self):
        '''
            Get this Row's is_unique


            `default`:None

            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-04-2022 14:17:21
            `@memberOf`: Row
            `@property`: is_unique
        '''
        value = _obj.get_arg(self.data,['is_unique'],None,(bool))
        # @Mstep [IF] if the property is not currenty set
        if value is None:
            value = False
            if self.unique_key is not None:
                value = True
            self.data['is_unique'] = value
        return value

    @property
    def unique_key(self):
        '''
            Get this Row's unique_key

            valid unique keys = ["unique","uq","uniq"]

            This is id used to identify the unique constraint.
            If the column_unique value constains a string that is not a "valid_unique_key" (VUK)
            That string will be used as the id.

            If the column_unique string is a VUK it will generate a random key to use.

            if the column is empty (excludeing spaces), no unique constraint is created.

            `default`:None

            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-05-2022 11:08:48
            `@memberOf`: Row
            `@property`: unique_key
        '''
        
        vuk = self.main.valid_unique_keys
        value = _obj.get_arg(self.data,['unique_key'],None,(str))
        # @Mstep [IF] if the property is not currenty set
        if value is None:
            value = _csu.strip(self.data['column_unique']," ")
            if len(value) > 0:
                if value.lower() in vuk:
                    value = _gen_unique_rand_id()
            else:
                value = None
            self.data['unique_key'] = value
        return value

    @property
    def allow_nulls(self):
        '''
            Get this Row's allow_nulls


            `default`:None


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-04-2022 14:02:54
            `@memberOf`: Row
            `@property`: allow_nulls
        '''
        value = _obj.get_arg(self.data,['column_allow_null',],None,(bool))
        # value = _obj.get_arg(self.data,['allow_nulls',],None,(bool))
        # @Mstep [IF] if the property is not currenty set
        if value is None:
            value = True
            self.data['null'] = "NULL"
            column_allow_null = self.data['column_allow_null']
            if column_allow_null is None:
                value = False
                self.data['null'] = "NOT NULL"
            if isinstance(column_allow_null,(str,int)):
                value = _csu.to_bool(column_allow_null)
            self.data['allow_nulls'] = value
        return value

    @allow_nulls.setter
    def allow_nulls(self,value:bool):
        '''
            set this Row's allow_nulls value.


            `default`:None


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-04-2022 14:02:54
            `@memberOf`: Row
            `@property`: allow_nulls
        '''
        if isinstance(value,(bool)) is False:
            if isinstance(value,(str,int)):
                value = _csu.to_bool(value,None)

        if isinstance(value,(bool)) is False:
            raise ValueError("allow_nulls must be a boolean or boolean synonym.")

        self.data['allow_nulls'] = value

    @property
    def major_type(self):
        '''
            Get this Row's major_type


            `default`:None


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-04-2022 13:59:48
            `@memberOf`: Row
            `@property`: major_type
        '''
        value = _obj.get_arg(self.data,['major_type'],None,(str))
        # @Mstep [IF] if the property is not currenty set
        if value is None:
            value = ""
            if self.is_primary_key is True:
                value = "PRIMARY_KEY"
            if self.is_foreign_key is True:
                value = "FOREIGN_KEY"
            self.data['major_type'] = value
        return value

    @property
    def table_name(self):
        '''
            Get this Row's table_name


            `default`:None

            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-04-2022 13:54:15
            `@memberOf`: Row
            `@property`: table_name
        '''
        value = _obj.get_arg(self.data,['table_name'],None,(str))
        # @Mstep [IF] if the property is not currenty set
        if value is None:
            value = self.table.name
            self.data['table_name'] = value
        return value

    @property
    def name(self)->str:
        '''
            Get this DrawioColumn's name


            `default`:None


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-04-2022 11:47:52
            `@memberOf`: DrawioColumn
            `@property`: name
        '''
        value = _obj.get_arg(self.data,['name'],None,(str))
        # @Mstep [IF] if the property is not currenty set
        if value is None:
            value = self.data['column_name']
            self.data['name'] = value
        return value

    @property
    def php_type(self):
        '''
            Get this Row's php_type


            `default`:None


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-04-2022 16:34:59
            `@memberOf`: Row
            `@property`: php_type
        '''
        value = _obj.get_arg(self.data,['php_type'],None,(str))
        # @Mstep [IF] if the property is not currenty set
        if value is None:
            value = _types.type_to_php(self.data_type)
            self.data['php_type'] = value
        return value

    @property
    def singular_table_name(self):
        '''
            Get this Row's singular_table_name


            `default`:None


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-04-2022 16:55:34
            `@memberOf`: Row
            `@property`: singular_table_name
        '''
        value = _obj.get_arg(self.data,['singular_table_name'],None,(str))
        # @Mstep [IF] if the property is not currenty set
        if value is None:
            value = True

            self.data['singular_table_name'] = value
        return value

    @property
    def missing_columns(self):
        '''
            Get this Row's missing_columns


            `default`:None


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-06-2022 07:35:21
            `@memberOf`: Row
            `@property`: missing_columns
        '''
        value = _obj.get_arg(self.settings,['missing_columns'],None,(bool))
        # @Mstep [IF] if the property is not currenty set
        if value is None:
            value = False
            self.settings['missing_columns'] = value
        return value

    @property
    def headers(self):
        '''
            Get this Row's headers
            
            This is a list of all headers in the table in the order they appear in.


            `default`:None


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-06-2022 07:37:44
            `@memberOf`: Row
            `@property`: headers
        '''
        value = _obj.get_arg(self.data,['headers'],None,(list))
        # @Mstep [IF] if the property is not currenty set
        if value is None:
            value = True
            self.data['headers'] = value
        return value


# TODO []: capture fulltext from extra column


def generate_rows(table:_db_dio_table)->_Iterable[Row]:
    # children = table.node.diagram.get_nodes_by_parent(table.node_id)
    
    # # @Mstep [IF] if there is at least one row found.
    # if len(children) > 0:
    #     # @Mstep [] remove the first row, this is the header row.
    #     children = children[1:]

    # rows = []
    # # @Mstep [LOOP] iterate the rows found.
    # for child in children:
    #     # @Mstep [] instantiate a Row entity and append to the rows list.
    #     rows.append(Row(table.main,table,child))
    # # @Mstep [] set the rows list on the table that called this method.
    # table.rows = rows
    
    row_dicts = _rows_to_dictionaries(table)
    rows = []
    for row in row_dicts:
        if _missing_critical_columns(table,row) is True:
            continue
        row_entity = Row(table.main,table,row['element'],row)
        rows.append(row_entity)
    return rows
    # table.rows = rows

def _missing_critical_columns(table:_db_dio_table,data:dict)->bool:
    '''
        Confirm that the row has a name and a data type.

        ----------

        Arguments
        -------------------------
        `table` {Table}
            A reference to the table instance.
        `data` {dict}
            The row's data dictionary.


        Return {bool}
        ----------------------
        True if the row is missing data, False otherwise

        Meta
        ----------
        `author`: Colemen Atwood
        `created`: 07-06-2022 08:16:38
        `memberOf`: Row
        `version`: 1.0
        `method_name`: _missing_critical_columns
        * @xxx [07-06-2022 08:17:56]: documentation for _missing_critical_columns
    '''


    missing_data = False
    if data['column_name'] is None or data['column_name'] == "":
        missing_data = True
        log(f"Column is missing a name in the table '{table.name}'","error")
        raise ValueError(f"Column is missing a name in the table '{table.name}'")

    result = _sql.is_valid_mysql_data_type(data['column_type'])
    if result is False:
        log(f"Invalid data type for column {data['column_name']} {data['column_type']} in the table '{table.name}'","error")
        data['column_type'] = None
        raise ValueError(f"Invalid data type for column {data['column_name']} {data['column_type']} in the table '{table.name}'")
    else:
        data['column_type'] = result['type']
        data['column_size'] = result['size']
    if data['column_type'] is None or data['column_type'] == "":
        missing_data = True
        log(f"Column is missing a type in table '{table.name}'","error")
        raise ValueError(f"Column is missing a type in the table '{table.name}'")

    return missing_data

def _rows_to_dictionaries(table:_db_dio_table)->_Iterable[dict]:
    '''
        Iterate through the rows of the table and generate a dictionary
        for each. This requires that the first row is a "header" row.

        The headers are used as the keys.

        ----------

        Arguments
        -------------------------
        `table` {Table}
            A reference to the table instance.


        Return {list}
        ----------------------
        A list of row dictionaries

        Meta
        ----------
        `author`: Colemen Atwood
        `created`: 07-06-2022 08:18:02
        `memberOf`: Row
        `version`: 1.0
        `method_name`: _rows_to_dictionaries
        * @xxx [07-06-2022 08:19:20]: documentation for _rows_to_dictionaries
    '''


    children = table.node.diagram.get_nodes_by_parent(table.node_id)
    headers = []
    if len(children) > 0:
        # @Mstep [] get a list of all headers in the table.
        headers = get_table_headers(table,children)
        # @Mstep [] remove the first row, this is the header row.
        children = children[1:]

    data = []
    for child in children:
        # @Mstep [] get all of the columns in the row.
        columns = table.node.diagram.get_nodes_by_parent(child.attributes['id'])
        values = [x.label for x in columns]
        row = _arr.lists_to_dict(headers,values)
        row['element'] = child
        # print(f"row: {row}")
        data.append(row)
    return data

def get_table_headers(table:_db_dio_table,children)->_Iterable[str]:
    '''
        Get the header row from the table's children

        ----------

        Arguments
        -------------------------
        `table` {Table}
            A reference to the table instance.
        `children` {list}
            A list of children elements.

        Return {list}
        ----------------------
        A list of header strings

        Meta
        ----------
        `author`: Colemen Atwood
        `created`: 07-06-2022 08:19:40
        `memberOf`: Row
        `version`: 1.0
        `method_name`: get_table_headers
        * @xxx [07-06-2022 08:21:22]: documentation for get_table_headers
    '''


    headers = []
    if len(children) > 0:
        columns = table.node.diagram.get_nodes_by_parent(children[0].attributes['id'])
        for col in columns:
            header = _csu.strip(col.label," ")
            header = _csu.to_snake_case(header)
            headers.append(f"column_{header}")

    for req in table.main.required_table_headers:
        if f"column_{req}" not in headers:
            log(f"Table {table.name} is missing the required column: {req}","error")
            table.settings['missing_columns'] = True

    table.data['headers'] = headers
    return headers

def _parse_data(row:Row):
    columns = row.node.diagram.get_nodes_by_parent(row.node_id)
    for col in columns:
        if hasattr(col,'tags'):
            tags = col.tags
            if len(tags) > 0:
                tag = tags[0]
                row.data[tag] = col.label


def _gen_unique_rand_id():
    return f"UQ_{_csu.rand()}"

def _validate_default(row:Row):
    '''
        This helper function is used by the row to change the allow_nulls
        value based on if the default value is "null" or not.

        If the row does not allow nulls but the default value is "null", it will
        change the allow_nulls to True.

        ----------

        Arguments
        -------------------------
        `row` {Row}
            A reference to the Row.


        Meta
        ----------
        `author`: Colemen Atwood
        `created`: 07-06-2022 09:39:15
        `memberOf`: Row
        `version`: 1.0
        `method_name`: _validate_default
        * @xxx [07-06-2022 09:41:00]: documentation for _validate_default
    '''


    default = row.default
    if default is not None:
        if default == "NULL":
            if row.allow_nulls is False:
                row.allow_nulls = True

def _gen_sql(row:Row):

    _validate_default(row)
    quote_char = row.table.main.sql_quote_char

    datas = [
        _csu.rightPad(f"{quote_char}{row.name}{quote_char}",len(row.table.longest_row_name)+5," "),
        _sql.gen_mysql_type(row.data_type,row.size),
        "NULL" if row.allow_nulls is True else "NOT NULL",
        "" if row.default is None else f"DEFAULT {row.default}",
        "" if row.is_auto_increment is False else "AUTO_INCREMENT",
        "" if row.comment is None else f"COMMENT '{row.comment}'"
    ]
    sql = ""
    for idx,k in enumerate(datas):
        
        if len(k) > 0:
            if idx > 0:
                sql = f"{sql} {k}"
            else:
                sql = k

    # sql = ' '.join(datas)

    row.data['sql'] = sql
    return sql


    # replacements = _entity_utils.gen_replacements(row.data)
    # value = _csu.dict_replace_string(_ROW_SQL_TEMPLATE,replacements)
    # value = _csu.strip(value," ")