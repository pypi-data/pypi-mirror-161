# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=line-too-long
# pylint: disable=unused-wildcard-import
# pylint: disable=wildcard-import
# pylint: disable=unused-import
# pylint: disable=import-outside-toplevel
'''
    A module containing the class for managing a table entity from a diagram

    ----------

    Meta
    ----------
    `author`: Colemen Atwood
    `created`: 07-05-2022 08:52:03
    `memberOf`: database_utils.drawio
    `name`: Table
    * @xxx [07-05-2022 08:52:23]: documentation for Table
'''



# import traceback
import inflect

import utils.list_utils as _arr
import utils.string_utils as _csu
import utils.drawio.diagram_utils as _dia
import utils.database_utils.drawio.entity_utils as _eutils
import utils.database_utils.drawio.Row as _row
import utils.database_utils.drawio.ForeignKey as _fk
from config import _onode_type,_db_dio_parser_type,_db_dio_row_type,_Iterable,_db_dio_foreign_key_type


import utils.dict_utils as _obj
import utils.file_utils as _f

p = inflect.engine()

_CREATE_TABLE_SQL_TEMPLATE = """
__TABLE_DIVIDER__

__CREATE_TABLE_STATEMENT__
(
__CREATE_CONTENT__
)__TABLE_COMMENT__;
"""






def new_table_element(main:_db_dio_parser_type,**kwargs):
    data = {
        "table_name":_obj.get_kwarg(['name'],None,(str),**kwargs),
        "schema_name":_obj.get_kwarg(['schema'],None,(str),**kwargs),
    }
    diagram = main.main_diagram
    diagram.add_table(
        headers=[{
            "name":"KEY",
            "width":40
        },
        {
            "name":"NAME",
            "width":160
        },
        {
            "name":"TYPE",
            "width":80
        },
        {
            "name":"DEFAULT&#10;VALUE",
            "width":80
        },
        {
            "name":"ALLOW NULL",
            "width":80
        },
        {
            "name":"EXTRA",
            "width":120
        },
        {
            "name":"COMMENT",
            "width":240
        },
        {
            "name":"UNIQUE",
            "width":70
        }]
    )



class Table:
    def __init__(self,main:_db_dio_parser_type,table_node:_onode_type,args=None):
        self.args = {} if args is None else args
        self.main = main
        self._node = table_node
        self._rows:_Iterable[_db_dio_row_type] = None
        self._foreign_keys:_Iterable[_db_dio_foreign_key_type] = None

        self.settings = {}
        self.data = {
            "table_name":None,
            "schema_name":None,
            "comment":None,
            "columns":None,
            "pascal_name":None,
            "pascal_singular_name":None,
            "pascal_plural_name":None,
            "camel_name":None,
            "camel_singular_name":None,
            "camel_plural_name":None,
            "snake_name":None,
            "snake_singular_name":None,
            "snake_plural_name":None,
            "singular_name":None,
            "longest_row_name":None,
            "row_names":None,
            "foreign_keys":None,
            "sql":None,
            "drop_table_sql":None,
        }
        self.data = _obj.set_defaults(self.data,self.args)


    @property
    def summary(self):
        '''
            Get this Table's summary


            `default`:None


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-05-2022 09:10:34
            `@memberOf`: Table
            `@property`: summary
        '''
        _eutils.trigger_attributes(self)
        sum_data = self.data.copy()
        sum_data['raw_statement'] = sum_data['sql']
        sum_data['columns'] = []
        for columns in self.rows:
            sum_data['columns'].append(columns.summary)

        sum_data['foreign_keys'] = []
        for fk in self.foreign_keys:
            sum_data['foreign_keys'].append(fk.summary)

        return sum_data

    @property
    def node_id(self):
        '''
            Get this Table's node_id


            `default`:None


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-04-2022 11:24:29
            `@memberOf`: Table
            `@property`: node_id
        '''
        return self._node.get_id()

    @property
    def node(self):
        '''
            Get this Table's node


            `default`:None


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-04-2022 11:59:50
            `@memberOf`: Table
            `@property`: node
        '''
        return self._node

    @property
    def sql(self):
        '''
            Get this Table's sql


            `default`:None


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-05-2022 10:19:57
            `@memberOf`: Table
            `@property`: sql
        '''
        replacements = self.data.copy()
        replacements['create_table_statement'] = _gen_create_table(self)

        tmp = [
            _gen_column_statements(self),
            _gen_primary_key_statement(self),
            _gen_unique_key_statement(self),
            _gen_foreign_key_statement(self),
        ]
        create_content = ',\n\n'.join(tmp)
        create_content = _csu.strip(create_content,[" ","\n"],"right")
        replacements['create_content'] = f"{create_content}"
        replacements['table_comment'] = ""

        if isinstance(self.comment,(str)) is True and len(self.comment) > 0:
            replacements['table_comment'] = f" COMMENT='{self.comment}'"

        qc = self.main.sql_quote_char
        sname = self.schema_name
        schema_name = f"{qc}{sname}{qc}." if sname is not None or isinstance(sname,(str)) and len(sname) > 0 else ""
        # schema_name = self.schema_name
        # if isinstance(schema_name,(str)) and len(schema_name) > 0:
        #     schema_name = f"{qc}{schema_name}{qc}."

        replacements['table_divider'] = f"-- ************************************** {schema_name}`{self.name}`"
        # replacements['column_declarations'] = _gen_column_statements(self)
        # replacements['primary_key'] = _gen_primary_key_statement(self)
        # replacements['unique_keys'] = _gen_unique_key_statement(self)

        sql = _csu.dict_replace_string(_CREATE_TABLE_SQL_TEMPLATE,_eutils.gen_replacements(replacements))
        self.data['sql'] = sql
        return sql

    @property
    def drop_table_sql(self):
        '''
            Get this Table's drop_table_sql


            `default`:None


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-05-2022 16:30:36
            `@memberOf`: Table
            `@property`: drop_table_sql
        '''
        value = _obj.get_arg(self.data,['drop_table_sql'],None,(str))
        # @Mstep [IF] if the property is not currenty set
        if value is None:
            value = _gen_drop_sql(self)
            self.data['drop_table_sql'] = value
        return value

    @property
    def comment(self):
        '''
            Get this Table's comment


            `default`:None


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-05-2022 11:53:56
            `@memberOf`: Table
            `@property`: comment
        '''
        value = _obj.get_arg(self.data,['comment'],None,(str))
        # @Mstep [IF] if the property is not currenty set
        if value is None:
            value = ""
            if self.node.has_attribute("comment") is True:
                value = self.node.attributes['comment']
            self.data['comment'] = value
        return value

    @property
    def row_names(self):
        '''
            Get a list of all row name's that belong to this table.


            `default`:None


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-05-2022 09:49:47
            `@memberOf`: Table
            `@property`: row_names
        '''
        # for r in self.rows:
        #     print(r.name)
        value = [x.name for x in self.rows]
        self.data['row_names'] = value
        return value

    @property
    def longest_row_name(self):
        '''
            Get this Table's longest_row_name


            `default`:None


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-05-2022 09:48:46
            `@memberOf`: Table
            `@property`: longest_row_name
        '''
        value = None
        row_names = self.row_names
        if isinstance(row_names,(list)):
            length,value = _arr.longest_string(row_names)
            self.data['longest_row_name_length'] = length
            self.data['longest_row_name'] = value
        return value

    @property
    def rows(self):
        '''
            Get this Table's list of row instances


            `default`:[]


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-05-2022 09:11:51
            `@memberOf`: Table
            `@property`: rows
        '''
        value = self._rows
        # # @Mstep [IF] if the property is not currenty set
        if value is None:
            # print(traceback.print_tb())
            print(f"Indexing rows for table: {self.name}")
            value = _row.generate_rows(self)
            self._rows = value
            # value = self._rows
        return value

    @rows.setter
    def rows(self,rows:_Iterable[_db_dio_row_type]):
        '''
            Set this Table's list of row instances


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-05-2022 09:11:51
            `@memberOf`: Table
            `@property`: rows
        '''
        self._rows = rows

    @property
    def foreign_keys(self):
        '''
            Get this Table's foreign_keys


            `default`:None


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-05-2022 13:30:15
            `@memberOf`: Table
            `@property`: foreign_keys
        '''
        value = self._foreign_keys
        # @Mstep [IF] if the property is not currenty set
        if value is None:
            value = _fk.generate_foreign_keys(self)
            self._foreign_keys = value
        return value

    @property
    def primary_key(self):
        '''
            Get this Table's primary_key(s)


            `default`:None


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-05-2022 10:52:11
            `@memberOf`: Table
            `@property`: primary_key
        '''
        value = _obj.get_arg(self.data,['primary_key'],None,(list))
        # @Mstep [IF] if the property is not currenty set
        if value is None:
            pks = []
            for r in self.rows:
                if r.is_primary_key is True:
                    pks.append(r.name)

            value = pks
            self.data['primary_key'] = value
        return value

    @property
    def unique_keys(self):
        '''
            Get this Table's unique_keys


            `default`:None


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-05-2022 10:59:50
            `@memberOf`: Table
            `@property`: unique_keys
        '''
        value = _obj.get_arg(self.data,['unique_keys'],None,(list))
        # @Mstep [IF] if the property is not currenty set
        if value is None:
            pks = []
            for r in self.rows:
                if r.is_unique is True:
                    data = {
                        "name":r.name,
                        "key":r.unique_key,
                    }
                    pks.append(data)
            value = pks
            self.data['unique_keys'] = value
        return value

    @property
    def table_name(self):
        '''
            An alias for the `name` attribute


            `default`:None


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-05-2022 09:26:29
            `@memberOf`: Table
            `@property`: table_name
        '''
        return self.name

    @property
    def name(self)->str:
        '''
            Get this Table's name


            `default`:None


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-04-2022 11:47:52
            `@memberOf`: Table
            `@property`: name
        '''
        value = _obj.get_arg(self.data,['table_name'],None,(str))
        # @Mstep [IF] if the property is not currenty set
        if value is None:
            value = self._node.label
            # if isinstance(value,(str)):
            value = _split_schema_table_name(self,value)

            schema_name = "" if self.schema_name is None else f"{self.schema_name}."
            new_label = f"{schema_name}{value}"
            if new_label != value:
                self._node.set_label(f"{self.data['schema_name']}.{value}")
            self.data['table_name'] = value
            _eutils.gen_name_variations(self,value)
        return value

    @name.setter
    def name(self,name:str)->str:
        '''
            Set this Table's name


            Return {str|bool}
            ----------------------
            The new name for table if successful, False otherwise.

            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-04-2022 11:47:52
            `@memberOf`: Table
            `@property`: name
        '''
        if isinstance(name,(str)) and len(name) > 0:
            self.data['table_name'] = name
            return self.data['table_name']
        return False

    @property
    def schema_name(self):
        '''
            An alias for the `schema` attribute


            `default`:None


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-05-2022 09:25:45
            `@memberOf`: Table
            `@property`: schema_name
        '''
        return self.schema

    @property
    def schema(self):
        '''
            Get this Table's schema


            `default`:None


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-05-2022 08:37:09
            `@memberOf`: Table
            `@property`: schema
        '''

        value = _obj.get_arg(self.data,['schema_name'],None,(str))
        # @Mstep [IF] if the property is not currenty set
        if value is None:
            _split_schema_table_name(self,self.name)
            value = self.data['schema_name']
        return value

    @schema.setter
    def schema(self,name:str)->str:
        '''
            Set this Table's schema


            Return {str|bool}
            ----------------------
            The new schema for table if successful, False otherwise.

            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-04-2022 11:47:52
            `@memberOf`: Table
            `@property`: schema
        '''
        if isinstance(name,(str)) and len(name) > 0:
            self.data['schema_name'] = name
            return self.data['schema_name']
        return False


    @property
    def singular_name(self):
        '''
            Get this tables singular_name\n
            Example:\n
            table name = "user_roles"\n
            singular_name = "user_role"
        '''

        value = self.data['singular_name']
        if value is None:
            value = p.singular_noun(self.name)
            self.data['singular_name'] = value
        return value

    @singular_name.setter
    def singular_name(self,value):
        '''
            Set this tables singular_name
        '''

        self.data['singular_name'] = value
        return self.data['singular_name']

    @property
    def pascal_name(self):
        '''
            Get this tables pascal_name\n
            Example:\n
            table name = "user_roles"\n
            pascal_name = "UserRoles"
        '''

        value = self.data['pascal_name']
        if value is None:
            _eutils.gen_name_variations(self,self.name)
            value = self.data['pascal_name']
        return value

    @pascal_name.setter
    def pascal_name(self,value):
        '''
            Set this tables pascal_name\n
            Example:\n
            table name = "user_roles"\n
            pascal_name = "UserRoles"
        '''

        self.data['pascal_singular_name'] = value
        return self.data['pascal_singular_name']

    @property
    def pascal_singular_name(self):
        '''
            Get this tables pascal_singular_name\n
            Example\n
            table name = "user_roles"\n
            pascal_singular_name = "UserRole"
        '''
        value = self.data['pascal_singular_name']

        if value is None:
            _eutils.gen_name_variations(self,self.name)
            value = self.data['pascal_singular_name']

        return value

    @pascal_singular_name.setter
    def pascal_singular_name(self,value):
        '''
            Set this tables pascal_singular_name\n
            Example:\n
            table name = "user_roles"\n
            pascal_plural_name = "UserRole"
        '''
        self.data['pascal_singular_name'] = value
        return self.data['pascal_singular_name']

    @property
    def pascal_plural_name(self):
        '''
            Get this tables pascal_plural_name\n
            Example\n
            table name = "user_roles"\n
            pascal_plural_name = "UserRoles"
        '''
        value = self.data['pascal_plural_name']

        if value is None:
            _eutils.gen_name_variations(self,self.name)
            value = self.data['pascal_plural_name']

        return value

    @pascal_plural_name.setter
    def pascal_plural_name(self,value):
        '''
            Set this tables pascal_plural_name\n
            Example:\n
            table name = "user_roles"\n
            pascal_plural_name = "UserRoles"
        '''
        self.data['pascal_plural_name'] = value
        return self.data['pascal_plural_name']

    @property
    def camel_name(self):
        '''
            Get this tables camel_name\n
            Example:\n
            table name = "user_roles"\n
            camel_name = "UserRoles"
        '''

        value = self.data['camel_name']
        if value is None:
            _eutils.gen_name_variations(self,self.name)
            value = self.data['camel_name']
        return value

    @camel_name.setter
    def camel_name(self,value):
        '''
            Set this tables camel_name\n
            Example:\n
            table name = "user_roles"\n
            camel_name = "UserRoles"
        '''

        self.data['camel_singular_name'] = value
        return self.data['camel_singular_name']

    @property
    def camel_singular_name(self):
        '''
            Get this tables camel_singular_name\n
            Example\n
            table name = "user_roles"\n
            camel_singular_name = "UserRole"
        '''
        value = self.data['camel_singular_name']

        if value is None:
            _eutils.gen_name_variations(self,self.name)
            value = self.data['camel_singular_name']

        return value

    @camel_singular_name.setter
    def camel_singular_name(self,value):
        '''
            Set this tables camel_singular_name\n
            Example:\n
            table name = "user_roles"\n
            camel_plural_name = "UserRole"
        '''
        self.data['camel_singular_name'] = value
        return self.data['camel_singular_name']

    @property
    def camel_plural_name(self):
        '''
            Get this tables camel_plural_name\n
            Example\n
            table name = "user_roles"\n
            camel_plural_name = "UserRoles"
        '''
        value = self.data['camel_plural_name']

        if value is None:
            _eutils.gen_name_variations(self,self.name)
            value = self.data['camel_plural_name']

        return value

    @camel_plural_name.setter
    def camel_plural_name(self,value):
        '''
            Set this tables camel_plural_name\n
            Example:\n
            table name = "user_roles"\n
            camel_plural_name = "UserRoles"
        '''
        self.data['camel_plural_name'] = value
        return self.data['camel_plural_name']

    @property
    def snake_name(self):
        '''
            Get this tables snake_name\n
            Example:\n
            table name = "user_roles"\n
            snake_name = "user_roles"
        '''

        value = self.data['snake_name']
        if value is None:
            _eutils.gen_name_variations(self,self.name)
            value = self.data['snake_name']
        return value

    @snake_name.setter
    def snake_name(self,value):
        '''
            Set this tables snake_name\n
            Example:\n
            table name = "user_roles"\n
            snake_name = "user_roles"
        '''

        self.data['snake_singular_name'] = value
        return self.data['snake_singular_name']

    @property
    def snake_singular_name(self):
        '''
            Get this tables snake_singular_name\n
            Example\n
            table name = "user_roles"\n
            snake_singular_name = "user_role"
        '''
        value = self.data['snake_singular_name']

        if value is None:
            _eutils.gen_name_variations(self,self.name)
            value = self.data['snake_singular_name']

        return value

    @snake_singular_name.setter
    def snake_singular_name(self,value):
        '''
            Set this tables snake_singular_name\n
            Example:\n
            table name = "user_roles"\n
            snake_plural_name = "user_role"
        '''
        self.data['snake_singular_name'] = value
        return self.data['snake_singular_name']

    @property
    def snake_plural_name(self):
        '''
            Get this tables snake_plural_name\n
            Example\n
            table name = "user_roles"\n
            snake_plural_name = "user_roles"
        '''
        value = self.data['snake_plural_name']

        if value is None:
            _eutils.gen_name_variations(self,self.name)
            value = self.data['snake_plural_name']

        return value

    @snake_plural_name.setter
    def snake_plural_name(self,value):
        '''
            Set this tables snake_plural_name\n
            Example:\n
            table name = "user_roles"\n
            snake_plural_name = "user_roles"
        '''
        self.data['snake_plural_name'] = value
        return self.data['snake_plural_name']


# def insert_row(table:Table,data:dict):
#     ono = table.main.main_diagram.add_onode()
    






def _split_schema_table_name(table:Table,value:str):
    name_list = value.split(".")

    # @Mstep [IF] if there is only one indice in the list.
    if len(name_list) == 1:
        # @Mstep [] set the tables name to the value of the list.
        table.name = name_list[0]
        # @Mstep [RETURN] return the table name
        return table.name

    # @Mstep [IF] the name_list has 2 indices.
    if len(name_list) == 2:
        # @Mstep [] set the table name
        table.name = name_list[1]
        # @Mstep [] set the schema name
        table.schema = name_list[0]
        # @Mstep [RETURN] return the table name
        return name_list[1]

    # @Mstep [if] the table node has a schema attribute.
    if table.node.has_attribute('schema'):
        # @Mstep [] get the schema attributes value.
        table.schema = table.node.attributes['schema']
        # @Mstep [] get remove the schema from the label, if it is found.
        name = table.node.label.replace(table.schema,"")
        # @Mstep [] strip leading and trailing spaces and periods.
        name = _csu.strip(name,[" ","."])
        # @Mstep [] set the tables name
        table.name = name
        # @Mstep [RETURN] return the tables name.
        return name

def _gen_create_table(table:Table,safe=True):
    qc = table.main.sql_quote_char
    safe_string = "IF NOT EXISTS "
    schema_name = ""
    if isinstance(table.schema,(str)) and len(table.schema) > 0:
        schema_name = f"{qc}{table.schema}{qc}."
    if safe is False:
        safe_string = ""

    statement = f"CREATE TABLE {safe_string}{schema_name}{qc}{table.name}{qc}"
    return statement

def _gen_column_statements(table:Table):
    '''
        Iterate all columns in the table to gather their declarations.
        Then concatenate them into a single string.

        ----------


        Return {str}
        ----------------------
        The sql string.

        Meta
        ----------
        `author`: Colemen Atwood
        `created`: 07-05-2022 10:50:38
        `memberOf`: Table
        `version`: 1.0
        `method_name`: _gen_column_statements
        * @xxx [07-05-2022 10:51:28]: documentation for _gen_column_statements
    '''


    rows = []
    for row in table.rows:
        _eutils.trigger_attributes(row)
        sql = row.sql
        if isinstance(sql,(str)) and len(sql) > 0:
            rows.append(sql)
    master = ',\n'.join(rows)
    return master

def _gen_primary_key_statement(table:Table):
    qc = table.main.sql_quote_char
    pks = table.primary_key
    pk_strings = []
    sql = ""

    if len(pks) > 0:
        for pk in pks:
            if len(pk) > 0:
                pk_strings.append(f"{qc}{pk}{qc}")

        pk_string = ','.join(pk_strings)
        sql = f"PRIMARY KEY ({pk_string})"
    return sql

def _gen_unique_key_statement(table:Table):
    qc = table.main.sql_quote_char
    uks = table.unique_keys
    if len(uks) == 0:
        return ""

    uks_org = {}
    for uk in uks:
        # print(f"uk: {uk}")
        key = uk['key']
        if key not in uks_org:
            uks_org[key] = []

        uks_org[key].append(uk['name'])

    sql = ""
    constraints = []

    for key,rows in uks_org.items():
        row_strings = [f"{qc}{x}{qc}" for x in rows]
        row_names = ','.join(row_strings)
        sql = f"UNIQUE KEY {qc}{key}{qc} ({row_names})"
        constraints.append(sql)


    sql = ',\n'.join(constraints)
    return sql

def _gen_foreign_key_statement(table:Table):
    # qc = table.main.sql_quote_char
    fks = table.foreign_keys
    if len(fks) == 0:
        return ""

    sql = ""
    constraints = []

    for fk in fks:
        constraints.append(fk.sql)


    sql = ',\n'.join(constraints)
    return sql

def _gen_drop_sql(table:Table,safe=True):
    qc = table.main.sql_quote_char
    safe_string = "IF NOT EXISTS "
    if safe is False:
        safe_string = ""

    schema_name = ""
    if isinstance(table.schema,(str)) and len(table.schema) > 0:
        schema_name = f"{qc}{table.schema}{qc}."

    sql = f"""DROP TABLE {safe_string}{schema_name}{qc}{table.name}{qc}"""
    return sql






# def _get_columns(table:Table):
#     # print(f"locate table columns")
#     children = table.node.diagram.get_nodes_by_parent(table.node_id)
#     # print(len(children))
#     if len(children) >0:
#         children = children[1:]
#     columns = []
#     for child in children:
#         _row.DrawioRow(table.main,table,)
#     #     print(child.node_id)
#     #     rows = table.node.diagram.get_nodes_by_parent(child.get_id())
#     #     for row in rows:
#     #         columns.append(row)
#     #         # print(row.label)
#     return children





