# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=line-too-long
# pylint: disable=unused-wildcard-import
# pylint: disable=wildcard-import
# pylint: disable=unused-import
# pylint: disable=import-outside-toplevel
'''
    A submodule of the database_utils module used for generating databases from drawio diagrams
    You can also create diagrams from the sql.

    ----------

    Meta
    ----------
    `author`: Colemen Atwood
    `created`: 06-03-2022 10:22:15
    `memberOf`: type_utils
'''

import os
from textwrap import indent
import time
import json

import utils.drawio as _drawio
from config import log,_drawing_type,_Iterable,_diagram_type,_connector_type,_db_dio_row_type,_db_dio_foreign_key_type,_db_dio_schema_type
import utils.database_utils.drawio.Table as _table
import utils.database_utils.drawio.Schema as _schema
import utils.database_utils.drawio.entity_utils as _eutils

import utils.string_utils as _csu
import utils.dict_utils as _obj
import utils.file_utils as _f


_VALID_UNIQUE_KEYS_DEFAULT = ["unique","uq","uniq"]
_VALID_FK_OPTIONS = ["no_action","cascade","set_null","set_default","restrict"]
_REQUIRED_TABLE_HEADERS = ["key","name","type","default_value","allow_null","extra","comment","unique"]
_VALID_SQL_TYPES = ["mysql","sqlite"]
_DEFAULT_DIAGRAM_NAME = "Main"


class Parser:
    def __init__(self,**kwargs):
        self._drawing:_drawing_type = None
        self.settings = {
            "drawing_loaded":False,
            "drawing_path":_obj.get_kwarg(['drawing_path','file_path'],None,(str),**kwargs),
            "sql_save_path":_obj.get_kwarg(['sql_path','sql_save_path'],None,(str),**kwargs),
            "summary_path":_obj.get_kwarg(['summary_path'],None,(str),**kwargs),
            "sql_quote_char":_obj.get_kwarg(['sql_quote_char'],"`",(str),**kwargs),
            "valid_unique_keys":_obj.get_kwarg(['valid_unique_keys'],_VALID_UNIQUE_KEYS_DEFAULT,(list),**kwargs),
            "default_diagram_name":_obj.get_kwarg(['default_diagram_name'],_DEFAULT_DIAGRAM_NAME,(str),**kwargs),
            "valid_fk_options":_obj.get_kwarg(['valid_fk_options'],_VALID_FK_OPTIONS,(list),**kwargs),
            "default_varchar_size":_obj.get_kwarg(['default_varchar_size'],50,(int),**kwargs),
            "database_dir_path":_obj.get_kwarg(['database_dir_path'],None,(str),**kwargs),
            "sql_type":_obj.get_kwarg(['sql_type'],_VALID_SQL_TYPES[0],(str),**kwargs),
            "required_table_headers":_REQUIRED_TABLE_HEADERS,
        }
        self.data = {
            "name":None,
            "tables":[],
            "connectors":{},
            "rows":{},
            "sql":None,
        }
        self._entities = {
            "tables":None,
            "rows":{},
            "foreign_keys":{},
            "schemas":{},
        }

    def master(self):
        drawing = self.drawing
        if drawing is None:
            return False

        # tables = self.tables
        # for table in tables:
        #     print(f"{table.name}")
        #     # print(json.dumps(table.data,indent=4))
        #     print("==============================================")

    @property
    def name(self):
        '''
            Get this Database's name


            `default`:None


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-06-2022 09:01:39
            `@memberOf`: Parser
            `@property`: name
        '''
        value = _obj.get_arg(self.data,['name'],None,(str))
        # @Mstep [IF] if the property is not currenty set
        if value is None:
            value = os.path.basename(self.drawing_path)
            # value = f"Database_{_csu.rand()}"
            self.data['name'] = value
        return value
    @property
    def tables(self)->_Iterable[_table.Table]:
        '''
            Get this DrawioParser's tables


            `default`:None


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-04-2022 09:57:33
            `@memberOf`: DrawioParser
            `@property`: tables
        '''
        value = _obj.get_arg(self._entities,['tables'],None,(list))
        # @Mstep [IF] if the property is not currenty set
        if value is None:
            new_tables = []
            tables = []
            log("Indexing Tables","cyan")
            diagrams = self.drawing.diagrams
            dia:_diagram_type
            for dia in diagrams:
                value = dia.get_nodes_by_tag("table")
                for tb in value:
                    new_tables.append(tb)

            for tb in new_tables:
                tables.append(_table.Table(self,tb))
                value = tables

            self._entities['tables'] = value
        return value

    @property
    def schemas(self)->_Iterable[_db_dio_schema_type]:
        '''
            Get a list this drawing's schema instances.


            `default`:[]


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-06-2022 08:22:35
            `@memberOf`: Parser
            `@property`: schemas
        '''
        value = _obj.get_arg(self._entities,['schemas'],[],(dict))
        # @Mstep [IF] if the property is not currenty set
        if len(value) == 0:
            # The schemas register themselves, so we don't need the return value.
            _schema.generate_schemas(self)
        s_list = []
        for _,schema in value.items():
            s_list.append(schema)
        value = s_list
        return value

    @property
    def schema_names(self):
        '''
            Get a list this drawing's schema names.


            `default`:None


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-06-2022 08:41:13
            `@memberOf`: Parser
            `@property`: schema_names
        '''
        value = _obj.get_arg(self.data,['schema_names'],None,(list))
        # @Mstep [IF] if the property is not currenty set
        if value is None:
            value = []
            schema:_db_dio_schema_type
            for _,schema in self._entities['schemas']:
                value.append(schema.name)
            if len(value) == 0:
                value = None
            self.data['schema_names'] = value
        return value

    @property
    def connectors(self):
        '''
            Get this Parser's connectors


            `default`:None


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-05-2022 12:43:42
            `@memberOf`: Parser
            `@property`: connectors
        '''
        value = _obj.get_arg(self._entities,['connectors'],None,(dict))
        # @Mstep [IF] if the property is not currenty set
        if value is None:
            value = {}
            diagrams = self.drawing.diagrams
            dia:_diagram_type
            for dia in diagrams:
                connectors = dia.get_connectors()
                con:_connector_type
                for con in connectors:
                    value[con.node_id] = con

            self._entities['connectors'] = value
        return value

    @property
    def summary_path(self):
        '''
            Get this Parser's summary_path


            `default`:None


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-05-2022 09:37:33
            `@memberOf`: Parser
            `@property`: summary_path
        '''
        value = _obj.get_arg(self.settings,['summary_path'],None,(str))
        # @Mstep [IF] if the property is not currenty set
        if value is None:
            value = f"{os.getcwd()}\\db_summary.json"
            self.settings['summary_path'] = value
        return value

    @property
    def _summary(self):
        '''
            Get this Parser's summary


            `default`:None


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-05-2022 09:03:43
            `@memberOf`: Parser
            `@property`: summary
        '''
        summary = {
            "drawing_data":_f.get_data(self.drawing_path),
            "schemas":[],
            "tables":[],
        }
        for table in self.tables:
            summary['tables'].append(table.summary)
            
        for schema in self.schemas:
            summary['schemas'].append(schema.summary)
            # tables.append(_eutils.summary(table))
        return summary

    def summary(self):
        '''
            Generate and save a json summary file of the database.

            ----------

            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 07-06-2022 08:55:20
            `memberOf`: Parser
            `version`: 1.0
            `method_name`: summary
            * @xxx [07-06-2022 08:55:50]: documentation for summary
        '''


        if self.drawing_loaded is False:
            return None
        summary = self._summary
        _f.writer.to_json(self.summary_path,summary)


    @property
    def mysql(self):
        '''
            Get this Parser's mysql


            `default`:None


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-06-2022 08:56:06
            `@memberOf`: Parser
            `@property`: mysql
        '''
        value = _obj.get_arg(self.data,['mysql'],None,(str))
        # @Mstep [IF] if the property is not currenty set
        if value is None:
            sql = _gen_master_sql(self)
            value = sql
            self.data['mysql'] = value
        return value

    def save(self):
        self.drawing.save(self.drawing_path)
        _f.write(self.sql_save_path,self.mysql)

    @property
    def sql_quote_char(self):
        '''
            Get this Parser's sql_quote_char


            `default`:None


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-05-2022 10:28:29
            `@memberOf`: Parser
            `@property`: sql_quote_char
        '''
        return self.settings['sql_quote_char']

    @property
    def valid_unique_keys(self):
        '''
            Get this Parser's valid_unique_keys

            These keys are used to identify if a column should have a unique constraint.

            If one of these keys are found in the UNIQUE column of the table node,
            a constraint will be created for it.

            `default`:["unique","uq","uniq"]


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-05-2022 11:23:46
            `@memberOf`: Parser
            `@property`: valid_unique_keys
        '''
        return self.settings['valid_unique_keys']

    @property
    def valid_fk_options(self):
        '''
            Get this Parser's valid_fk_options


            `default`:None


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-05-2022 12:17:18
            `@memberOf`: Parser
            `@property`: valid_fk_options
        '''
        return self.settings['valid_fk_options']

    @property
    def default_varchar_size(self):
        '''
            Get this Parser's default_varchar_size


            `default`:None


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-06-2022 10:33:52
            `@memberOf`: Parser
            `@property`: default_varchar_size
        '''
        return self.settings['default_varchar_size']


    @property
    def required_table_headers(self):
        '''
            Get this Parser's required_table_headers


            `default`:None


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-06-2022 07:32:43
            `@memberOf`: Parser
            `@property`: required_table_headers
        '''
        value = _obj.get_arg(self.settings,['required_table_headers'],_REQUIRED_TABLE_HEADERS,(list))
        # @Mstep [IF] if the property is not currenty set
        if value is None:
            value = True
            self.settings['required_table_headers'] = value
        return value

    @property
    def sql_save_path(self):
        '''
            Get this Parser's sql_save_path


            `default`:None


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-06-2022 09:07:33
            `@memberOf`: Parser
            `@property`: sql_save_path
        '''
        value = self.settings['sql_save_path']
        if value is None:
            value = f"{self.drawing_dir_path}\\{self.drawing_file_name}.sql"
            self.settings['sql_save_path'] = value
            self.settings['master_sql_path'] = value
        return value

    @property
    def drawing_dir_path(self):
        '''
            Get this Parser's drawing_dir_path


            `default`:None


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-06-2022 09:10:36
            `@memberOf`: Parser
            `@property`: drawing_dir_path
        '''
        value = _obj.get_arg(self.data['drawing_data'],['dir_path'],None,(str))
        # @Mstep [IF] if the property is not currenty set
        if value is None:
            # TODO []: when generating from sql, use sql file's directory.
            value = True
            self.data['drawing_data']['dir_path'] = value
        return value

    @property
    def drawing_file_name(self):
        '''
            Get this Parser's drawing_file_name


            `default`:None


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-06-2022 09:12:17
            `@memberOf`: Parser
            `@property`: drawing_file_name
        '''
        value = _obj.get_arg(self.data['drawing_data'],['file_name'],None,(str))
        # @Mstep [IF] if the property is not currenty set
        if value is None:
            value = True
            self.data['drawing_data']['file_name'] = value
        return value



    @property
    def drawing_path(self):
        '''
            Get this DrawioParser's drawing_path


            `default`:None


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-04-2022 09:43:46
            `@memberOf`: DrawioParser
            `@property`: drawing_path
        '''
        return _obj.get_arg(self.settings,['drawing_path'],None,(str))

    @property
    def drawing(self)->_drawing_type:
        '''
            Get this DrawioParser's drawing


            `default`:None


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-04-2022 09:45:21
            `@memberOf`: DrawioParser
            `@property`: drawing
        '''
        value = self._drawing
        # @Mstep [IF] if the property is not currenty set
        if value is None:
            if _f.exists(self.drawing_path) is False:
                log(f"Could not locate database diagram: {self.drawing_path}","error")
                self.settings['drawing_loaded'] = False
                return None
            value = _drawio.drawing.read(self.drawing_path)
            self._drawing = value
            self.settings['drawing_loaded'] = True
            self.data['drawing_data'] = _f.get_data(self.drawing_path)
            
        return value


    def index_master(self):
        # @Mstep [] index all tables.
        tables = self.tables
        
        # # @Mstep [] have each table index its own rows.
        rows = [x.rows for x in tables]
        # # @Mstep [] Now we know the tables and rows, index the connectors
        foreign_keys = [x.foreign_keys for x in tables]
        schemas = self.schemas


    @property
    def sql_type(self):
        '''
            Get this Parser's sql_type


            `default`:None


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-06-2022 11:21:31
            `@memberOf`: Parser
            `@property`: sql_type
        '''
        return self.settings['sql_type']


    def load_drawing(self):
        drawing = self.drawing
        # tables = self.tables
        if drawing is None:
            self.settings['drawing_loaded'] = False
            log("Aborting Parsing of diagram.","error")
            return False

        self.index_master()

    def get_row_by_id(self,row_id:str):
        print(f"        Searching for row by id: {row_id}")
        if row_id in self._entities['rows']:
            return self._entities['rows'][row_id]
        return None

    def register(self, entity_type:str,instance):
        '''
            Register a database entity with this parser.

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
            `created`: 07-05-2022 12:33:03
            `memberOf`: Parser
            `version`: 1.0
            `method_name`: register
            * @TODO []: documentation for register
        '''


        entity_type = _csu.to_snake_case(entity_type)
        if entity_type == "table":
            log(f"Registering New Table: {instance.node_id} - {instance.name}","cyan")
            self._entities['tables'].append(instance)
        if entity_type == "row":

            if instance.node_id not in self._entities['rows']:
                # log(f"Registering New Row: {instance.node_id} - {instance.name}","cyan")
                self._entities['rows'][instance.node_id] = instance

        if entity_type == "foreign_key":
            instance:_db_dio_foreign_key_type
            # log(f"Registering New foreign_key: {instance.parent_row_name}","magenta")
            self._entities['foreign_keys'][instance.node_id] = instance

        if entity_type == "schema":
            instance:_db_dio_schema_type
            log(f"Registering New Schema: {instance.name}","magenta")
            self._entities['schemas'][instance.name] = instance

    @property
    def drawing_loaded(self):
        '''
            Get this Parser's drawing_loaded setting
            this is set to True if the file is found and successfully parsed.


            `default`:False

            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-06-2022 07:16:18
            `@memberOf`: Parser
            `@property`: drawing_loaded
        '''
        value = _obj.get_arg(self.settings,['drawing_loaded'],None,(bool))
        # @Mstep [IF] if the property is not currenty set
        if value is None:
            value = False
            self.settings['drawing_loaded'] = value
        return value

    @property
    def default_diagram_name(self):
        '''
            Get this Parser's default_diagram_name


            `default`:None


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-06-2022 11:47:18
            `@memberOf`: Parser
            `@property`: default_diagram_name
        '''
        return self.settings['default_diagram_name']
    
    @property
    def main_diagram(self)->_diagram_type:
        '''
            Get this Parser's main_diagram


            `default`:None


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-06-2022 11:47:48
            `@memberOf`: Parser
            `@property`: main_diagram
        '''
        diagram = self.drawing.get_diagram(self.default_diagram_name)
        return diagram

    def add_table(self,**kwargs):
        _table.new_table_element(self,**kwargs)



# TODO []: load from diagram entry point.
def from_diagram(**kwargs):
    p = Parser(**kwargs)
    p.load_drawing()
    # p.index_master()
    p.summary()

    return p


# TODO []: create diagram entry point.





def _gen_master_sql(main:Parser):

    drop_tables = '\n\n'.join([x.drop_table_sql for x in main.tables])
    create_schemas = '\n\n'.join([x.sql for x in main.schemas])
    create_tables = '\n\n'.join([x.sql for x in main.tables])


    sql = f"""
-- ******************************** ColemenUtils: MySQL ********************************
-- * Generated by ColemenUtils: {main.name} *

{drop_tables}
{create_schemas}
{create_tables}
    """
    return sql
    







