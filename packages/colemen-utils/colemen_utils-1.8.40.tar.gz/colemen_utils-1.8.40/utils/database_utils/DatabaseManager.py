# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=line-too-long
# pylint: disable=unused-wildcard-import
# pylint: disable=wildcard-import
# pylint: disable=unused-import
'''
    A module of utility methods used for parsing and converting python types.

    ----------

    Meta
    ----------
    `author`: Colemen Atwood
    `created`: 06-03-2022 10:22:15
    `memberOf`: type_utils
'''



import os as _os
import sys
import time
from typing import Union as _Union
from typing import Iterable as _Iterable
import sqlite3
import mysql.connector
import traceback as _traceback
from mysql.connector import Error
from colorama import Fore as _Fore
from colorama import Style as _Style
# import config as _config
import utils.dict_utils as _obj
import utils.file_utils as _cfu
import utils.directory_utils as _dirs
import utils.string_utils as _csu
import utils.list_utils as _lu

# import utils.database_utils.TableManager as _table_manager

import utils.database_utils.TableManager as _table_manager

import utils.database_utils as _cdb
# _TableManager = _cdb.TableManager
import utils.console_utils as _con
_log = _con.log



class DatabaseManager:
    '''
        The DatabaseManager is used to manage a fucking database.

        This particular system is designed to parse a single SQL file (the master sql) into a
        directory structure. From there you can create a {table_name}.json file or (use this class)
        which is treated as the default data for insertion. It can also manage test data separately
        from the default data.

        The master summary file is saved in the root directory, after parsing this class can load
        from that file or parse the master sql again.

        ----------

        Keyword Arguments
        -------------------------
        `verbose` {False}
            If True, the class will be more talkative.

        Meta
        ----------
        `author`: Colemen Atwood
        `created`: 06-05-2022 19:25:23
        `memberOf`: DatabaseManager
        `version`: 1.0
        `class_name`: DatabaseManager
        * @xxx [06-05-2022 19:37:33]: documentation for DatabaseManager
    '''


    def __init__(self,**kwargs):
        self._raw_sql_parse_data = None
        self.init_gen_insert = False


        self.data = {
            "name":_csu.to_snake_case(_obj.get_kwarg(['name'],f"database_{_csu.gen.rand()}",(str),**kwargs)),
            "schemas":[],
            "tables":[],
            "insert_data":{
                "default":{},
                "test":{},
            },
            "table_instances":[],
            "credentials":None,
        }

        self.settings = {
            "setup_complete":False,
            "master_summary_file_name":f"{self.data['name']}.summary.json",
            "master_summary_path":_obj.get_kwarg(['master_summary_path','summary path'],f"{_os.getcwd()}\\{self.data['name']}.summary.json",(str),**kwargs),
            "master_sql_path":_obj.get_kwarg(['master sql path','sql path'],f"{_os.getcwd()}\\master.sql",(str),**kwargs),
            "database_dir_path":_obj.get_kwarg(['database_dir_path'],f"{_os.getcwd()}\\{self.data['name']}",(str),**kwargs),
            "create_dir":_obj.get_kwarg(['create_dir'],True,(bool),**kwargs),
            "skip_orphans":_obj.get_kwarg(['skip orphans'],True,(bool),**kwargs),
            "auto_parse":_obj.get_kwarg(['auto parse'],True,(bool),**kwargs),
            "auto_purge":_obj.get_kwarg(['auto purge'],False,(bool),**kwargs),
            "verbose":_obj.get_kwarg(['verbose'],False,(bool),**kwargs),
            "master_sql_modified":None,
        }


        # _cfu.writer.to_json("dbman_init.delete.json",{**self.data,**self.settings})

        self.con = None
        self.cur = None

        # self.data['tables_cols_cache'] = {}



    # def _parse_kwargs(self,**kwargs):
    #     self.data['name'] = _csu.to_snake_case(_obj.get_kwarg(['name'],"database",(str),**kwargs))
    #     self.settings['master_summary_file_name'] = f"{self.data['name']}.summary.json"
    #     self.settings['database_dir_path'] = _obj.get_kwarg(['database dir path'],f"{_os.getcwd()}\\{self.data['name']}",(str),**kwargs)

    #     self.settings['master_sql_path'] = _obj.get_kwarg(['master sql path','sql path'],f"{_os.getcwd()}\\master.sql",(str),**kwargs)

    #     self.settings['master_summary_path'] = _obj.get_kwarg(['master_summary_path','summary path'],f"{_os.getcwd()}\\{self.data['name']}.summary.json",(str),**kwargs)


    #     self.settings['verbose'] = _obj.get_kwarg(['verbose'],False,(bool),**kwargs)
    #     self.settings['create_dir'] = _obj.get_kwarg(['create_dir'],True,(bool),**kwargs)
    #     self.settings['skip_orphans'] = _obj.get_kwarg(['skip orphans'],True,(bool),**kwargs)
    #     self.settings['auto_parse'] = _obj.get_kwarg(['auto parse'],True,(bool),**kwargs)


    def load_from_summary(self,summary_path=None):
        if summary_path is not None:
            if _cfu.exists(summary_path):
                self.master_summary_path = summary_path
            else:
                _log(f"Failed to locate summary file: {summary_path}","error")
                return False

        indexing = _parse_master_summary_file(self)
        if indexing:
            self.settings['setup_complete'] = True
            self.gen_insert_data()

        if self.settings['auto_parse']:
            # @Mstep [if] compare the saved modified timestamp to the current timestamp.
            if _has_master_changed(self):
                _log("Master SQL has been modified, initiating auto parsing.")
                self.parse_master_sql(
                    self.master_sql_path,
                    create_dir=self.create_dir,
                    dir_path=self.database_dir_path,
                    skip_no_schema=self.skip_orphans
                )
            else:
                _log("Master SQL has not been modified since last parse.")
            # self.gen_creates()

        self.save_master_summary()
        # _cfu.writer.to_json("dbman_summary_load.delete.json",self.settings)


    def load_from_master_sql(self,sql_path=None,create_dir=True,dir_path=None,skip_orphans=True):
        '''
            Load the database from the master sql file.
            This will optionally create the directory structure for the database.

            ----------

            Arguments
            -------------------------
            `sql_path` {str}
                The path to the master sql file to import.

            [`create_dir`=True] {bool}
                If False the directory structure will not be created.

            [`dir_path`=cwd] {str}
                if create_dir is True this is where the directory structure will be created.
                By default that will be the current working directory.

            [`skip_orphans`=True] {bool}
                If False, the orphaned tables will have their table folders created in the root directory.
                "Orphans" are tables that do not belong to a schema, this option is irrelevant if there are
                no schemas.

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
            `created`: 06-01-2022 12:08:43
            `memberOf`: DatabaseManager
            `version`: 1.0
            `method_name`: load_from_master_sql
            * @TODO []: documentation for load_from_master_sql
        '''
        if _confirm_manager_resources(self) is False:
            return False

        sql_path = self.master_sql_path if sql_path is None else sql_path
        self.parse_master_sql(sql_path,create_dir=create_dir,dir_path=dir_path,skip_no_schema=skip_orphans)
        self.settings['setup_complete'] = True
        self.gen_insert_data()

    def connect(self, **kwargs):
        '''
            Sets up the database connection with the initial settings.

            If the DB_PATH is provided, it attempts to connect to an sqlite database.

            If the DB_CREDENTIALS are provided, it attempts to connect to a mysql database.

            ----------

            Keyword Arguments
            -----------------
            `DB_PATH` {string}
                The filepath to the sqlite database

            [`create`=True] {bool}
                If True and SQLite database does not exist yet, create the file.

            `DB_CREDENTIALS` {dict}
                The credentials to connect to the mysql database
                {
                    "user":"string",
                    "password":"string",
                    "host":"string",
                    "database":"string"
                }

            Return {bool}
            ----------
                True upon success, false otherwise.

            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 04-19-2021 08:04:18
            `version`: 1.0
        '''
        # print(f"{self.data['credentials']}")
        dp_path = _obj.get_kwarg(["db_path", "path"], None, str, **kwargs)
        db_creds = _obj.get_kwarg(["db_credentials", "credentials", "creds"], self.data['credentials'], (dict), **kwargs)
        create = _obj.get_kwarg(["create"], True, (bool), **kwargs)
        connect_success = False
        if dp_path is not None:
            if _cfu.exists(dp_path) is True or create is True:
                self.data['db_type'] = "SQLITE"
                self.data['db_path'] = dp_path
                if self.__connect_to_sqlite_db() is True:
                    connect_success = True

        if db_creds is not None:
            # if 'DB_CREDENTIALS' in kwargs:
            self.data['db_type'] = "MYSQL"
            self.data['db_credentials'] = db_creds
            if self.__connect_to_my_sqldb() is True:
                connect_success = True

        return connect_success

    def __connect_to_sqlite_db(self):
        '''
                Creates the connection to an sqlite database.

                ----------

                Meta
                ----------
                `author`: Colemen Atwood
                `created`: 04-19-2021 08:08:13
                `memberOf`: colemen_database
                `version`: 1.0
                `method_name`: __connect_to_sqlite_db
        '''
        if 'db_path' in self.data:
            self.data['db_type'] = "SQLITE"
            self.con = sqlite3.connect(self.data['db_path'])
            self.con.row_factory = sqlite3.Row
            self.cur = self.con.cursor()
            return True

        print("No Database Path Provided.")
        return False

    def __validate_db_credentials(self):
        '''
                Validates that all of the db_credentials are provided.

                ----------

                Return {bool}
                ----------------------
                True upon success, false otherwise.

                Meta
                ----------
                `author`: Colemen Atwood
                `created`: 04-19-2021 08:23:40
                `memberOf`: colemen_database
                `version`: 1.0
                `method_name`: __validate_db_credentials
        '''
        if 'db_credentials' in self.data:
            error_array = []
            creds = self.data['db_credentials']
            if 'user' not in creds:
                error_array.append('user is not provided in db_credentials')
            if 'password' not in creds:
                error_array.append('password is not provided in db_credentials')
            if 'host' not in creds:
                error_array.append('host is not provided in db_credentials')
            if 'database' not in creds:
                error_array.append('database is not provided in db_credentials')
            if len(error_array) == 0:
                # print("Successfully validated db_credentials")
                return True
            return False

        print("Credentials are needed to connect to the Mysql Database.")
        return False

    def __connect_to_my_sqldb(self):
        '''
            Attempts to connect to a mysql database.

            ----------

            Return {bool}
            ----------------------
            True upon success, false otherwise.

            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 04-19-2021 08:23:40
            `memberOf`: colemen_database
            `version`: 1.0
            `method_name`: __connect_to_my_sqldb
        '''
        connect_success = False
        if self.con is not None:
            return True
        if self.__validate_db_credentials() is True:
            self.data['db_type'] = "MYSQL"
            self.con = None
            try:

                self.con = mysql.connector.connect(
                    user=self.data['db_credentials']['user'],
                    password=self.data['db_credentials']['password'],
                    host=self.data['db_credentials']['host'],
                    database=self.data['db_credentials']['database']
                )
                self.cur = self.con.cursor(
                    buffered=True,
                    dictionary=True
                )

                if self.con.is_connected():
                    # print("Successfully connected to mysql database")
                    connect_success = True

            except Error as error:
                print(error)

            # finally:
            #     if self.con is not None and self.con.is_connected():
            #         self.con.close()

        return connect_success

    def list_schemas(self)->list:
        '''
            List all schemas in this database.

            ----------

            Return {list}
            ----------------------
            The list of schemas in this database.

            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 06-05-2022 19:17:41
            `memberOf`: DatabaseManager
            `version`: 1.0
            `method_name`: list_schemas
            * @xxx [06-05-2022 19:19:02]: documentation for list_schemas
        '''

        schemas = []
        if self.settings['setup_complete'] is False:
            return False
        # master = _cfu.read.as_json(f"{_os.getcwd()}\\modules\\equari\\parse_master_sql.json")
        print(f"\n{_csu.gen.title_divider('Equari Database Schemas')}\n\n")
        total_tables = 0
        for schema in self.data['schemas']:
            print(f"    {schema['name']}")
            schemas.append(schema['name'])
            total_tables += len(schema['tables'])

        print(f"Total Schemas: {len(self.data['schemas'])}")
        print(f"Total Tables: {total_tables}")
        print(f"\n\n{_csu.gen.title_divider('Equari Database Schemas')}\n\n")
        return schemas

    def list_tables(self)->list:
        '''
            List all tables associated to this database.

            ----------

            Return {list}
            ----------------------
            A list of table names.

            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 06-05-2022 19:14:27
            `memberOf`: DatabaseManager
            `version`: 1.0
            `method_name`: list_tables
            * @xxx [06-05-2022 19:17:25]: documentation for list_tables
        '''

        tables = []
        if self.settings['setup_complete'] is False:
            return False
        print(f"\n{_csu.gen.title_divider('Equari Database Tables')}\n\n")
        table:_table_manager.TableManager
        for table in self.table_instances:
            tables.append(table.table_name)
            print(_Fore.RED + f"    {_csu.rightPad(table.schema,self.data['longest_schema_name'],' ')}" + _Fore.CYAN + f" - {table.table_name}" + _Style.RESET_ALL)
        print(f"Total Tables: {len(self.data['tables'])}")
        print(f"\n\n{_csu.gen.title_divider('Equari Database Tables')}\n\n")
        return tables

    def gen_insert_data(self):
        '''
            Iterate all tables to collect the default and test insert data files.
            Then it updates the property self.data['insert_data']

            `insert_data` = {
                `default`:{
                    table_name:[
                        {row_data},
                        ...
                    ]
                },
                `test`:{
                    table_name:[
                        {row_data},
                        ...
                    ]
                }
            }


            ----------

            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 06-02-2022 08:24:10
            `memberOf`: DatabaseManager
            `version`: 1.0
            `method_name`: gen_insert_data
            * @xxx [06-02-2022 08:25:28]: documentation for gen_insert_data
        '''


        master_data = {
            "default":{},
            "test":{},
        }

        data = {}
        t:_table_manager.TableManager
        for t in self.data['table_instances']:
            # @Mstep [] get the table's default insert data.
            default_data = t.default_insert_json
            # @Mstep [] assign the data to the master_data dictionary.
            master_data['default'][t.table_name] = default_data


            # @Mstep [] get the table's test insert data.
            test_data = t.test_insert_json
            # @Mstep [] assign the data to the master_data dictionary.
            master_data['test'][t.table_name] = test_data

        self.data['insert_data'] = master_data
        self.init_gen_insert = True

        # TODO []: remove this, only for testing shit.
        _cfu.writer.to_json("dbman.insert.json",data)
        # self.master_data['default'] = data

    def list_columns(self,table_name:str)->list:
        '''
            List all columns in the table.

            ----------

            Arguments
            -------------------------
            `table_name` {str}
                The name of the table to list columns for.

            Return {list}
            ----------------------
            A list of column names.

            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 06-05-2022 19:11:32
            `memberOf`: DatabaseManager
            `version`: 1.0
            `method_name`: list_columns
            * @xxx [06-05-2022 19:13:00]: documentation for list_columns
        '''

        columns = []
        t = _get_table_by_name(self,table_name)
        cols:list = t.column_names
        for col_name in cols:
            columns.append(col_name)
            print(col_name)
        return columns

    def parse_master_sql(self,sql_path=None,**kwargs):
        '''
            Parse the master sql file for this database.

            ----------

            Arguments
            -------------------------
            [`sql_path`=None] {str}
                The path to the master SQL file to parse.

            Keyword Arguments
            -------------------------
            [`create_dir`=True] {bool}
                If False, the database and table directories will not be created
            [`dir_path`=None] {str}
                If provided, this is where the database directory will be created.
                It defaults to .\\database
            [`skip_orphans`=True] {bool}
                If schemas are found the table's without a schema are considered orphans.
                If False, the table's directory is created in the root database folder.

            Return {type}
            ----------------------
            return_description

            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 06-05-2022 19:00:20
            `memberOf`: DatabaseManager
            `version`: 1.0
            `method_name`: parse_master_sql
            * @xxx [06-05-2022 19:11:10]: documentation for parse_master_sql
        '''

        _log("DatabaseManager.parse_master_sql")
        create_dir = _obj.get_kwarg(['create_dir'],self.create_dir,(bool),**kwargs)
        dir_path = _obj.get_kwarg(['dir_path'],self.database_dir_path,(str),**kwargs)
        _is_purge_call = _obj.get_kwarg(['_is_purge_call'],False,(bool),**kwargs)
        if self._raw_sql_parse_data is None:
            if sql_path is not None:
                if _cfu.exists(sql_path):
                    self.master_sql_path = sql_path
                    self.master_summary_path = _os.path.dirname(sql_path) + "\\" + self.settings['master_summary_file_name']

            _log("    Parsing the Master SQL content.")
            if isinstance(sql_path,(str)):
                self._raw_sql_parse_data = _csu.parse.sql.parse(sql_path)

        data = self._raw_sql_parse_data.copy()
        for t in data['tables']:
            t['name'] = t['table_name']

        for t in data['schemas']:
            t['name'] = t['schema_name']
            # del t['schema_name']


        if create_dir:
            _log("    DatabaseManager.parse_master_sql - Creating directories")
            self.settings['database_dir_path'] = _os.path.dirname(sql_path) if dir_path is None else dir_path
            _log(f"       database_dir_path: {self.settings['database_dir_path']}")
            # _cfu.writer.to_json("parse_master_sql.json",data)
            # exit()

            data['schemas'] = _generate_schema_dirs(self,data['schemas'])
            data['tables'] = _generate_table_files(self,data['tables'])

        self.data['schemas'] = data['schemas']
        self.data['tables'] = data['tables']
        data = _organize_summary_tables(data)
        if self.settings['auto_purge'] is True and _is_purge_call is False:
            self.purge_tables()
        self.save_master_summary()

    def save_master_summary(self):
        '''
            compiles the master summary dictionary and saves it.

            ----------


            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 06-01-2022 11:27:24
            `memberOf`: DatabaseManager
            `version`: 1.0
            `method_name`: save_master_summary
            * @xxx [06-01-2022 11:27:47]: documentation for save_master_summary
        '''
        _cfu.writer.to_json(self.master_summary_path,self.master_summary)

    def get_table(self,name:str,schema:_Union[None,str]=None)->_Union[_table_manager.TableManager,None]:
        '''
            Get a table from this database.

            ----------

            Arguments
            -------------------------
            `name` {str|list}
                The name or list of names of tables to retrieve the instances of.

            [`schema`=None] {str}
                The schema to search within, if not provided, it will return the first match.

            Return {TableManager|None}
            ----------------------
            The tableManager instance or None if it cannot be found.

            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 06-01-2022 14:05:18
            `memberOf`: DatabaseManager
            `version`: 1.0
            `method_name`: get_table
            * @xxx [06-07-2022 11:00:38]: documentation for get_table
        '''
        result = self.table(name,schema)
        if result is not None and isinstance(result,(list)) is False:
            return result
        return None

    def table(self,name:_Union[list,str],schema:_Union[None,str]=None)->_Union[_Iterable[_table_manager.TableManager],_table_manager.TableManager,None]:
        '''
            Get a table from this database.

            ----------

            Arguments
            -------------------------
            `name` {str|list}
                The name or list of names of tables to retrieve the instances of.

            [`schema`=None] {str}
                The schema to search within, if not provided, it will return the first match.

            Return {TableManager|None}
            ----------------------
            If multiple table names are provided, it will return a list of instances.
            If one table name is provided, it will return the tableManager instance.
            If no tables are found, returns None.

            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 06-01-2022 14:05:18
            `memberOf`: DatabaseManager
            `version`: 1.0
            `method_name`: table
            * @xxx [06-07-2022 11:00:38]: documentation for table
        '''

        name = _lu.force_list(name)
        if len(name) > 1:
            tables = []
            for table_name in name:
                tb = _get_table_by_name(self,table_name,schema)
                if tb is not None:
                    tables.append(tb)
            if len(tables) == 1:
                return tables[0]
            if len(tables) == 0:
                return None
            return tables
        if len(name) == 1:
            return _get_table_by_name(self,name,schema)

    def truncate(self,tables:_Union[str,list],schemas:_Union[str,list,None]=None)->bool:
        '''
            Truncate tables in the database.

            ----------

            Arguments
            -------------------------
            `tables` {list}
                A list of table names to truncate.

            Return {bool}
            ----------------------
            True if ALL tables are successfully truncated, false otherwise.

            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 06-05-2022 18:55:44
            `memberOf`: DatabaseManager
            `version`: 1.0
            `method_name`: truncate
            * @xxx [06-05-2022 18:59:31]: documentation for truncate
        '''
        failed = []
        truncated = []
        if schemas is not None:
            schemas = _lu.force_list(schemas)
            tb:_table_manager.TableManager
            for tb in _get_tables_by_schema(self,schemas):
                res = tb.truncate_table()
                if res:
                    truncated.append(tb.name)
                else:
                    failed.append(tb.name)


        tables = _lu.force_list(tables)
        for table in tables:
            tb = self.table(table)
            if tb is not None:
                if tb.name not in truncated:
                    res = tb.truncate_table()
                    if res:
                        truncated.append(tb.name)
                    else:
                        failed.append(tb.name)
        if len(failed) > 0:
            for tb in failed:
                _log(f"Failed to truncate table: {tb}","error")
        if len(failed) == 0:
            return True
        return False

    def gen_default_reset(self,tables:_Union[str,list]):
        '''
            Generate the default data insert sql file and reset the table in the databse.

            ----------

            Arguments
            -------------------------
            `tables` {str|list}
                The table name or list of table names to reset.

            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 06-02-2022 14:44:02
            `memberOf`: DatabaseManager
            `version`: 1.0
            `method_name`: gen_default_reset
            * @xxx [06-02-2022 14:45:14]: documentation for gen_default_reset
        '''


        tables = _lu.force_list(tables)
        for table in tables:
            tb = self.table(table)
            if tb is not None:
                tb.gen_default_reset()

    def gen_test_reset(self,tables:_Union[str,list]):
        '''
            Generate the test data insert sql file and reset the table in the databse.

            ----------

            Arguments
            -------------------------
            `tables` {str|list}
                The table name or list of table names to reset.

            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 06-02-2022 14:44:02
            `memberOf`: DatabaseManager
            `version`: 1.0
            `method_name`: gen_test_reset
            * @xxx [06-02-2022 14:45:14]: documentation for gen_test_reset
        '''


        tables = _lu.force_list(tables)
        for table in tables:
            tb = self.table(table)
            if tb is not None:
                tb.gen_test_reset()

    def gen_creates(self):
        '''
            Generate the create sql files for all tables in the databse.

            ----------

            Arguments
            -------------------------
            `tables` {str|list}
                The table name or list of table names to reset.

            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 06-02-2022 14:44:02
            `memberOf`: DatabaseManager
            `version`: 1.0
            `method_name`: gen_test_reset
            * @xxx [06-02-2022 14:45:14]: documentation for gen_test_reset
        '''


        tables = _lu.force_list(self.tables)
        for table in tables:
            tb = self.get_table(table)
            if tb is not None:
                tb.gen_create_sql()

    def purge_test_data(self):
        '''
            Delete test data for all tables.

            This is useful for using a data generator, it will purge all of the old data for a fresh start.

            ----------

            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 06-07-2022 16:42:52
            `memberOf`: DatabaseManager
            `version`: 1.0
            `method_name`: purge_test_data
            * @xxx [06-07-2022 16:43:59]: documentation for purge_test_data
        '''


        tb:_table_manager.TableManager
        for tb in self.data['table_instances']:
            tb.delete_test_data()

    def purge_tables(self):
        '''
            Delete table directories that do not correspond the the master sql.
            Be careful this will delete all default and test data associated to the table.
            This will automatically occur if 'auto_parse' and 'auto_purge' are True when the master sql has been modified.

            ----------

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
            `created`: 06-07-2022 13:20:19
            `memberOf`: DatabaseManager
            `version`: 1.0
            `method_name`: purge_tables
            * @TODO []: documentation for purge_tables
        '''


        _log("    Purging Table Directories.")
        if self._raw_sql_parse_data is None:
            self._raw_sql_parse_data = _csu.parse.sql.parse(self.master_sql_path)
        purge = []

        for tb in self.data['table_instances']:
            match_found = False
            for pt in self._raw_sql_parse_data['tables']:
                if pt['table_name'] == tb.name:
                    match_found = True
            if match_found is False:
                purge.append(tb)

        if len(purge) > 0:
            # tables = self.tables
            tb:_table_manager.TableManager
            for tb in purge:
                _log(f"        Purging Table: {tb.name}")
                tb.delete()
        # @Mstep [] parse the sql data to update the master summary
        self.parse_master_sql(create_dir=False,_is_purge_call=True)





    @property
    def skip_orphans(self)->str:
        return self.settings['skip_orphans']

    @property
    def create_dir(self)->str:
        return self.settings['create_dir']


    @property
    def table_instances(self)->_Iterable[_table_manager.TableManager]:
        return self.data['table_instances']

    @property
    def tables(self)->_Iterable[dict]:
        '''
            Get the list of tables in this database.

            ----------

            Return {str|None}
            ----------------------
            The sql json summary file path if it exists.

            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 05-31-2022 12:39:59
            `memberOf`: DatabaseManager
            `version`: 1.0
            `method_name`: tables
            @xxx [05-31-2022 12:41:14]: documentation for tables
        '''
        return self.data['tables']

    def update_table_summary(self,table_name:str,new_data:dict):
        '''
            Set the master sql json summary path.
            This is where the summary file is saved after an sql file is parsed into a directory.

            ----------

            Arguments
            -------------------------
            `new_path` {str}
                The new location to save the json summary.

            Return {str}
            ----------------------
            The new locations path.

            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 05-31-2022 12:41:26
            `memberOf`: DatabaseManager
            `version`: 1.0
            `method_name`: tables
            @xxx [05-31-2022 12:43:00]: documentation for tables
        '''

        for t in self.data['tables']:
            if t['name'] == table_name:
                t = {**t,**new_data}


    @property
    def schemas(self)->_Iterable[dict]:
        '''
            Get the list of schemas in this database.

            ----------

            Return {list}
            ----------------------
            A list of schema data dictionaries

            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 05-31-2022 12:39:59
            `memberOf`: DatabaseManager
            `version`: 1.0
            `method_name`: schemas
            @xxx [05-31-2022 12:41:14]: documentation for schemas
        '''
        return self.data['schemas']

    @schemas.setter
    def schemas(self,new_path:str):
        '''
            Set the master sql json summary path.
            This is where the summary file is saved after an sql file is parsed into a directory.

            ----------

            Arguments
            -------------------------
            `new_path` {str}
                The new location to save the json summary.

            Return {str}
            ----------------------
            The new locations path.

            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 05-31-2022 12:41:26
            `memberOf`: DatabaseManager
            `version`: 1.0
            `method_name`: schemas
            @xxx [05-31-2022 12:43:00]: documentation for schemas
        '''

        self.data['schemas'] = new_path
        return self.data['schemas']


    @property
    def name(self):
        '''
            Get this databases name

            ----------

            Return {str|None}
            ----------------------
            The name of this database.

            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 05-31-2022 12:39:59
            `memberOf`: DatabaseManager
            `version`: 1.0
            `method_name`: name
            @xxx [05-31-2022 12:41:14]: documentation for name
        '''
        return self.data['name']

    @name.setter
    def name(self,new_name:str):
        '''
            Set the database name.
            This used for titling summary files.

            ----------

            Arguments
            -------------------------
            `new_name` {str}
                The new name of the database.

            Return {str}
            ----------------------
            The new locations path.

            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 05-31-2022 12:41:26
            `memberOf`: DatabaseManager
            `version`: 1.0
            `method_name`: name
            @xxx [05-31-2022 12:43:00]: documentation for name
        '''

        self.data['name'] = new_name
        self.settings['master_summary_file_name'] = f"{new_name}.summary.json"
        return self.data['name']



    @property
    def master_summary(self)->str:
        '''
            Get the master summary data.

            ----------

            Return {dict}
            ----------------------
            The master summary data dictionary.

            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 05-31-2022 12:39:59
            `memberOf`: DatabaseManager
            `version`: 1.0
            `method_name`: master_summary_path
            @xxx [05-31-2022 12:41:14]: documentation for master_summary_path
        '''
        # @Mstep [] update the tables data dictionary by gathering the summary from all tables.
        tables = []
        t:_table_manager.TableManager
        for t in self.data['table_instances']:
            summary =t.table_summary
            tables.append(summary)
        self.data['tables'] = tables

        master_sql_modified_timestamp = None
        if _cfu.exists(self.master_sql_path):
            master_sql_modified_timestamp = _cfu.get_modified_time(self.master_sql_path)


        data = {
            "name":self.name,
            "schemas":self.data['schemas'],
            "tables":self.data['tables'],
            "insert_data":self.data['insert_data'],
            "orphan_tables":_find_orphan_tables(self),
            "database_dir_path":self.settings['database_dir_path'],
            "master_summary_file_name":self.settings['master_summary_file_name'],
            "master_summary_path":self.master_summary_path,
            "master_sql_path":self.master_sql_path,
            "master_sql_modified":master_sql_modified_timestamp,
            "modified_timestamp":time.time(),
        }
        return data

    @property
    def master_summary_path(self)->str:
        '''
            Get the file path for the master sql json summary file.
            This file is generated when an sql file is parsed and the local directory is generated.

            ----------


            Return {str|None}
            ----------------------
            The sql json summary file path if it exists.

            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 05-31-2022 12:39:59
            `memberOf`: DatabaseManager
            `version`: 1.0
            `method_name`: master_summary_path
            @xxx [05-31-2022 12:41:14]: documentation for master_summary_path
        '''
        return self.settings['master_summary_path']

    @master_summary_path.setter
    def master_summary_path(self,new_path:str)->str:
        '''
            Set the master sql json summary path.
            This is where the summary file is saved after an sql file is parsed into a directory.

            ----------

            Arguments
            -------------------------
            `new_path` {str}
                The new location to save the json summary.

            Return {str}
            ----------------------
            The new locations path.

            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 05-31-2022 12:41:26
            `memberOf`: DatabaseManager
            `version`: 1.0
            `method_name`: master_summary_path
            @xxx [05-31-2022 12:43:00]: documentation for master_summary_path
        '''
        # print(f"setting new master summary path: {new_path}")
        self.settings['master_summary_path'] = new_path
        return self.settings['master_summary_path']

    @property
    def master_sql_modified(self)->_Union[int,float,None]:
        '''
            Get the timestamp of the last time the master SQL was modified.

            ----------


            Return {int|float|None}
            ----------------------
            The timestamp of the last modification or None if the summary has not been saved yet.

            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 05-31-2022 12:39:59
            `memberOf`: DatabaseManager
            `version`: 1.0
            `method_name`: master_sql_path
            @xxx [05-31-2022 12:41:14]: documentation for master_sql_path
        '''
        ts = self.settings['master_sql_modified']
        if ts is None:
            ts = _cfu.get_modified_time(self.master_sql_path)
        return ts

    @property
    def master_sql_path(self)->str:
        '''
            Get the file path for the master sql json summary file.
            This file is generated when an sql file is parsed and the local directory is generated.

            ----------


            Return {str|None}
            ----------------------
            The sql json summary file path if it exists.

            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 05-31-2022 12:39:59
            `memberOf`: DatabaseManager
            `version`: 1.0
            `method_name`: master_sql_path
            @xxx [05-31-2022 12:41:14]: documentation for master_sql_path
        '''
        return self.settings['master_sql_path']

    @master_sql_path.setter
    def master_sql_path(self,new_path:str)->str:
        '''
            Set the master sql json summary path.
            This is where the summary file is saved after an sql file is parsed into a directory.

            ----------

            Arguments
            -------------------------
            `new_path` {str}
                The new location to save the json summary.

            Return {str}
            ----------------------
            The new locations path.

            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 05-31-2022 12:41:26
            `memberOf`: DatabaseManager
            `version`: 1.0
            `method_name`: master_sql_path
            @xxx [05-31-2022 12:43:00]: documentation for master_sql_path
        '''

        self.settings['master_sql_path'] = new_path
        return self.settings['master_sql_path']




    @property
    def database_dir_path(self)->str:
        return self.settings['database_dir_path']

    @name.setter
    def credentials(self,new_creds:dict):
        '''
            Set the database name.
            This used for titling summary files.

            ----------

            Arguments
            -------------------------
            `new_name` {str}
                The new name of the database.

            Return {str}
            ----------------------
            The new locations path.

            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 05-31-2022 12:41:26
            `memberOf`: DatabaseManager
            `version`: 1.0
            `method_name`: name
            @xxx [05-31-2022 12:43:00]: documentation for name
        '''

        self.data['credentials'] = new_creds
        return self.data['credentials']


    @property
    def insert_data(self):
        '''
            Get this databases insert_data

            ----------

            Return {str|None}
            ----------------------
            The insert_data of this database.

            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 05-31-2022 12:39:59
            `memberOf`: DatabaseManager
            `version`: 1.0
            `method_insert_data`: insert_data
            @xxx [05-31-2022 12:41:14]: documentation for insert_data
        '''
        if self.init_gen_insert is False:
            self.gen_insert_data()
        return self.data['insert_data']

    def save(self,gen_insert_sql:bool=True):
        '''
            Save the default insert data for all tables in the database and optionally generate the
            default insert SQL files.

            ----------

            Arguments
            -------------------------
            [`gen_insert_sql`=True] {bool}
                if False, the insert sql file will not be generated and saved.

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
            `created`: 06-01-2022 15:25:56
            `memberOf`: DatabaseManager
            `version`: 1.0
            `method_name`: save
            * @xxx [06-01-2022 15:27:53]: documentation for save
        '''

        t:_table_manager.TableManager
        for t in self.data['table_instances']:
            t.save_insert_data(gen_insert_sql)
            self.save_master_summary()

    @property
    def is_connected(self):
        if self.con is not None:
            return True
        return False

    def run(self, sql:str, args=False):
        '''
            Executes a query on the database.

            ----------

            Arguments
            -------------------------
            `sql` {string}
                The sql query to execute.

            `args` {list}
                A list of arguments to apply to the sql query

            Return {bool}
            ----------------------
            True upon success, false otherwise.

            if multiple statements are provided it will return True if ALL statements execute successfully.

            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 04-19-2021 10:07:54
            `memberOf`: colemen_database
            `version`: 1.0
            `method_name`: run
        '''

        statements = sql
        # if the sql is a string, split it into a list of statements
        if isinstance(sql, (str)):
            statements = _to_statement_list(sql)

        if len(statements) > 1:
            # print(f"Multiple statements [{len(statements)}] found in sql.")
            success = True
            for statement in statements:
                # print(f"statement: {statement}")
                res = self.execute_single_statement(statement, args)
                if res is False:
                    success = False
            return success

        if len(statements) == 1:
            return self.execute_single_statement(sql, args)

    def close(self):
        '''
            Close the connection to the mySQL database.

            ----------

            Return {None}
            ----------------------
            None

            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 06-05-2022 19:19:32
            `memberOf`: DatabaseManager
            `version`: 1.0
            `method_name`: close
            * @xxx [06-05-2022 19:20:10]: documentation for close
        '''

        self.con.close()
        self.con = None
        self.cur = None

    def execute_single_statement(self, sql:str, args=False):
        '''
            Executes a single SQL query on the database.

            ----------

            Arguments
            -------------------------
            `sql` {string}
                The SQL to be executed.

            `args` {list}
                A list of arguments for parameter substitution.

            Return {bool}
            ----------------------
            True upon success, false otherwise.

            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 12-09-2021 09:19:40
            `memberOf`: colemen_database
            `version`: 1.0
            `method_name`: execute_single_statement
        '''
        success = False
        if self.cur is None or self.con is None:
            print("Not connected to a database, aborting query.")
            if self.data['credentials'] is not None:
                self.connect()
        try:
            if args is False:
                # print(f"executing sql: ",sql)
                self.cur.execute(sql)
            else:
                args = _csu.sql.sanitize_quotes(args)
                self.cur.execute(sql, args)
                # print(f"result: ",result)

            self.con.commit()
            success = True


        except mysql.connector.errors.IntegrityError:
            _log(f"{_traceback.format_exc()}","error")
            _log(f"SQL: {sql}","error")

        except mysql.connector.errors.DatabaseError:
            # print(f"ERROR: {err}", PRESET="FATAL_ERROR_INVERT")
            _log(f"{_traceback.format_exc()}","error")
            _log(f"SQL: {sql}","error")


        except sqlite3.Warning as error:
            _log(f"Warning: {error}","error")
            _log(_traceback.format_exc(),"error")

        except sqlite3.OperationalError as error:
            _log(f"Fatal Error: {error}","error")
            _log(_traceback.format_exc(),"error")

        except AttributeError:
            _log(f"{_traceback.format_exc()}\n","error")
            _log(f"{print(sys.exc_info()[2])}\n\n","error")
            _log(f"SQL: \033[38;2;(235);(64);(52)m{sql}")
        return success

    def run_from_list(self, query_list,**kwargs):
        '''
            Execute SQL statements from a list.

            ----------

            Arguments
            -------------------------
            `query_list` {list}
                A list of query statements to execute.

            Keyword Arguments
            -------------------------
            [`disable_restraints`=True] {bool}
                If True, temporarily disable foreign_key_checks while executing the queries

            Return {bool}
            ----------------------
            True upon success, false otherwise.

            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 06-05-2022 16:32:58
            `memberOf`: DatabaseManager
            `version`: 1.0
            `method_name`: run_from_list
            * @xxx [06-05-2022 16:36:56]: documentation for run_from_list
        '''

        disable_foreign_key_restraints = _obj.get_kwarg(['disable key restraints','disable restraints'],True,(bool),**kwargs)
        # disable_foreign_key_restraints = True
        # if 'DISABLE_KEY_RESTRAINTS' in kwargs:
        #     if kwargs['DISABLE_KEY_RESTRAINTS'] is False:
        #         disable_foreign_key_restraints = False
        if disable_foreign_key_restraints is True:
            self.run("SET foreign_key_checks = 0;")

        success = True
        for que in query_list:
            success = self.run(que)
            if success is False:
                break

        if disable_foreign_key_restraints is True:
            self.run("SET foreign_key_checks = 1;")
        return success

    def run_multi(self, sql:str, args):
        sql = sql.replace(";", ";STATEMENT_END")
        statements = sql.split('STATEMENT_END')
        for s in statements:
            if len(s) > 0:
                # print(f"query: {s}")
                self.run(s, args)

    def fetchall(self):
        '''
            Executes the fetchall method on the database and converts the result to a dictionary.

            ----------


            Return {dict|list}
            ----------------------
            If there is more than one result, it returns a list of dicts.
            If there is only one result, it returns a single dictionary.

            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 06-02-2022 13:58:55
            `memberOf`: DatabaseManager
            `version`: 1.0
            `method_name`: fetchall
            * @xxx [06-02-2022 13:59:37]: documentation for fetchall
        '''
        return self._to_dict(self.cur.fetchall())

    def fetchone(self):
        """ DOCBLOCK {
                "class_name":"Database",
                "method_name":"fetchone",
                "author":"Colemen Atwood",
                "created": "04-19-2021 08:04:18",
                "version": "1.0",
                "description":"Executes the fetchone method on the database.",
                "returns":{
                    "type":"dict",
                    "description":"The result of the fetchone command"
                }
            }"""
        r = self.cur.fetchone()
        return r

    def execute_sql_from_file(self, filePath:str, **kwargs):
        '''
            Executes queries stored in a file.

            ----------

            Arguments
            -------------------------
            `file_path` {str}
                The filePath to the sql file

            Keyword Arguments
            -------------------------
            `DISABLE_KEY_RESTRAINTS` {bool}
                If True, temporarily disable foreign_key_checks while executing the queries

            Return {bool}
            ----------------------
            True upon success, false otherwise.

            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 06-05-2022 16:29:39
            `memberOf`: DatabaseManager
            `version`: 1.0
            `method_name`: execute_sql_from_file
            * @xxx [06-05-2022 16:41:53]: documentation for execute_sql_from_file
        '''

        with open(filePath, 'r', encoding='utf-8') as file:
            sql = file.read()
            sql = sql.replace(";", ";STATEMENT_END")
            statements = sql.split('STATEMENT_END')

        # self.run("SET foreign_key_checks=0;")
        # "SOURCE /backups/mydump.sql;" -- restore your backup within THIS session
        # statements = getSQLStatementsFromFile(filePath)
        # print(f"statements: {statements}")
        disable_foreign_key_restraints = True
        if 'DISABLE_KEY_RESTRAINTS' in kwargs:
            if kwargs['DISABLE_KEY_RESTRAINTS'] is False:
                disable_foreign_key_restraints = False
        return self.run_from_list(statements, DISABLE_KEY_RESTRAINTS=disable_foreign_key_restraints)
        # self.run("SET foreign_key_checks=1;")

    def _to_dict(self, result):
        # print(f"_to_dict: resultType: {type(result)}")
        if isinstance(result, list):
            new_data = []
            for row in result:
                tmp = {}
                for col in row.keys():
                    tmp[col] = row[col]
                new_data.append(tmp)
            return new_data
        if isinstance(result, sqlite3.Row):
            new_data = {}
            for col in result.keys():
                new_data[col] = result[col]
            return new_data


def database_from_sql(sql_path:str,**kwargs)->_Union[DatabaseManager,bool]:
    '''
        Instantiate a new Database Manager by parsing an SQL file.
        The database directory structure will be created where the master.sql file is.

        ----------

        Arguments
        -------------------------
        `sql_path` {str}
            The path to the master sql file to parse.

        Keyword Arguments
        -------------------------

        [`name`=None] {str}
            The name to use for this database locally.
            This is used for naming summary files and has no effect on the actual database.
            If not provided, the name of the master sql file will be used.

        [`create_dir`=True] {bool}
            If False, the SQL will not be parsed into a directory structure.
            This will also make it so you cannot insert default data or test data, the directory structure
            is vital to the data management aspect of this module.

        [`skip_orphans`=True] {bool}
            If False, tables that do not belong to a schema will have a folder created in the root directory.
            This only applies if there are schemas and `create_dir` is True.

        [`auto_parse`=True] {bool}
            Irrelevant to this instance, since it will automatically parse the SQL.
            But future instances loaded from the summary file can automatically check if the master.sql has changed
            and parse it to the directory structure.
            If this is False, it will not do this.

        [`verbose`=False] {bool}
            Make it a chatty kathy.


        [`credentials`=None] {dict}
            If you want to synchronize this database to a remote mySQL database, you will need to provide the credentials.
            This can also be provided later using "db.credentials = {beepBoopBleepBlorp}"
            {
                "user":"MrBiscuits",
                "password":"SexyLasagna1234",
                "host":"ServerIPAddress",
                "database":"RemoteDatabaseName"
            }

        Return {DatabaseManager,bool}
        ----------------------
        An instance of the DatabaseManager if successful.
        returns False if the sql file cannot be located

        Meta
        ----------
        `author`: Colemen Atwood
        `created`: 06-07-2022 08:39:19
        `memberOf`: DatabaseManager
        `version`: 1.0
        `method_name`: database_from_sql
        * @xxx [06-07-2022 09:21:15]: documentation for database_from_sql
    '''

    create_dir=_obj.get_kwarg(['create_dir'],True,(bool),**kwargs)
    skip_orphans=_obj.get_kwarg(['skip orphans'],True,(bool),**kwargs)
    auto_parse=_obj.get_kwarg(['auto parse'],True,(bool),**kwargs)
    verbose=_obj.get_kwarg(['verbose'],False,(bool),**kwargs)
    name = _obj.get_kwarg(['name'],None,(str),**kwargs)
    credentials = _obj.get_kwarg(['credentials','creds'],None,(dict),**kwargs)

    # @Mstep [IF] if the sql_path does not exist.
    if _cfu.exists(sql_path) is False:
        # @Mstep [] alert the user of the issue.
        _log(f"Failed to locate the Master SQL file: {sql_path}","error")
        # @Mstep [RETURN] return False.
        return False

    # @Mstep [] parse the directory from the master sql path
    db_path = _os.path.dirname(sql_path)

    # @Mstep [IF] if a name was not provided
    if name is None:
        # @Mstep [] format the master sql file name to be in snake case and use it as the name.
        name = _csu.to_snake_case(_cfu.get_name_no_ext(sql_path))

    # @Mstep [] generate the master_summary_path
    master_summary_path = f"{db_path}\\{name}.summary.json"

    db = DatabaseManager(
        name=name,
        master_summary_path=master_summary_path,
        database_dir_path=db_path,
        sql_path=sql_path,
        create_dir=create_dir,
        skip_orphans=skip_orphans,
        auto_parse=auto_parse,
        verbose=verbose,
    )


    # if name is not None:
    #     # @Mstep [] add it to the database manager.
    #     db.name = name

    # @Mstep [IF] if credentials were provided
    if credentials is not None:
        # @Mstep [] add them to the database manager.
        db.credentials = credentials

    # @Mstep [] initiate the parsing of the master SQL file.
    db.load_from_master_sql()
    # @Mstep [RETURN] return the databaseManager instance.
    return db

def database_from_summary(summary_path:str,**kwargs)->_Union[DatabaseManager,bool]:
    '''
        Instantiate a new Database Manager by loading it from a summary file.
        ----------

        Arguments
        -------------------------
        `summary_path` {str}
            The path to the master summary file to load from..

        Keyword Arguments
        -------------------------

        [`create_dir`=True] {bool}
            If False, the SQL will not be parsed into a directory structure.
            This will also make it so you cannot insert default data or test data, the directory structure
            is vital to the data management aspect of this module.

        [`skip_orphans`=True] {bool}
            If False, tables that do not belong to a schema will have a folder created in the root directory.
            This only applies if there are schemas and `create_dir` is True.

        [`auto_parse`=True] {bool}
            Automatically check if the master.sql has changed and parse it to the directory structure.
            If this is False, it will not do this.

        [`auto_purge`=True] {bool}
            Automatically delete table directories that do not exist in the master SQL

        [`verbose`=False] {bool}
            Make it a chatty kathy.

        [`credentials`=None] {dict}
            If you want to synchronize this database to a remote mySQL database, you will need to provide the credentials.
            This can also be provided later using "db.credentials = {beepBoopBleepBlorp}"
            {
                "user":"MrBiscuits",
                "password":"SexyLasagna1234",
                "host":"ServerIPAddress",
                "database":"RemoteDatabaseName"
            }

        Return {DatabaseManager,bool}
        ----------------------
        An instance of the DatabaseManager if successful.
        returns False if the summary file cannot be located

        Meta
        ----------
        `author`: Colemen Atwood
        `created`: 06-07-2022 08:39:19
        `memberOf`: DatabaseManager
        `version`: 1.0
        `method_name`: database_from_sql
        * @xxx [06-07-2022 09:21:15]: documentation for database_from_sql
    '''

    auto_purge = _obj.get_kwarg(["auto_purge"], False, (bool), **kwargs)
    create_dir=_obj.get_kwarg(['create_dir'],True,(bool),**kwargs)
    skip_orphans=_obj.get_kwarg(['skip orphans'],True,(bool),**kwargs)
    auto_parse=_obj.get_kwarg(['auto parse'],True,(bool),**kwargs)
    verbose=_obj.get_kwarg(['verbose'],False,(bool),**kwargs)
    # name = _obj.get_kwarg(['name'],None,(str),**kwargs)
    credentials = _obj.get_kwarg(['credentials','creds'],None,(dict),**kwargs)

    # @Mstep [IF] if the sql_path does not exist.
    if _cfu.exists(summary_path) is False:
        # @Mstep [] alert the user of the issue.
        _log(f"Failed to locate the Master SQL file: {summary_path}","error")
        # @Mstep [RETURN] return False.
        return False

    db = DatabaseManager(
        master_summary_path=summary_path,
        auto_purge=auto_purge,
        create_dir=create_dir,
        skip_orphans=skip_orphans,
        auto_parse=auto_parse,
        verbose=verbose
    )


    # @Mstep [IF] if credentials were provided
    if credentials is not None:
        # @Mstep [] add them to the database manager.
        db.credentials = credentials
    # @Mstep [] initiate the parsing of the master SQL file.
    db.load_from_summary()
    
    # @Mstep [RETURN] return the databaseManager instance.
    return db


# def database(**kwargs)->DatabaseManager:
#     '''
#         Instantiate a DatabaseManager class.

#         ----------


#         Keyword Arguments
#         -------------------------
#         [`name`=None] {str}
#             The name of the database.

#         [`credentials`=None] {dict}
#             The database credentials for a mySQL database.

#         [`summary_path`=None] {str}
#             The path to the summary file to load the database manager from.

#         Return {DatabaseManager}
#         ----------------------
#         An instance of the DatabaseManager class.

#         Meta
#         ----------
#         `author`: Colemen Atwood
#         `created`: 06-05-2022 13:52:33
#         `memberOf`: colemen_database
#         `version`: 1.0
#         `method_name`: database
#         * @xxx [06-05-2022 13:58:01]: documentation for database
#     '''
#     db = DatabaseManager(**kwargs)
#     # name = _obj.get_kwarg(['name'],None,(str),**kwargs)
#     # summary_path = _obj.get_kwarg(['summary_path'],None,(str),**kwargs)
#     # credentials = _obj.get_kwarg(['credentials'],None,(dict),**kwargs)
#     # if name is not None:
#     #     db.name = name
#     # if credentials is not None:
#     #     db.credentials = credentials
#     # if summary_path is not None:
#     #     db.load_from_summary(summary_path)
#     return db





def _get_tables_by_schema(main:DatabaseManager,schema:_Union[str,list])->_Union[_Iterable[_table_manager.TableManager],list]:
    '''
        Retrieve all table instances associated the schema.

        ----------

        Arguments
        -------------------------
        `main` {DatabaseManager}
            A reference to the DatabaseManager Instance.
        `schema` {str,list}
            The schema name or list of schema names to retrieve table from.

        Return {list}
        ----------------------
        A list of tableManager instances that are associated to the schemas provided.
        If None are found, the list is empty.

        Meta
        ----------
        `author`: Colemen Atwood
        `created`: 06-06-2022 10:24:01
        `memberOf`: DatabaseManager
        `version`: 1.0
        `method_name`: _get_tables_by_schema
        * @xxx [06-06-2022 10:28:16]: documentation for _get_tables_by_schema
    '''

    schema = _lu.force_list(schema)
    tables = []
    for s_name in schema:
        for s in main.data['schemas']:
            if s['name'] == s_name:
                for t in main.data['table_instances']:
                    if t['schema_name'] == s['name']:
                        tables.append(t)
    return tables

def _get_table_by_name(main:DatabaseManager,table_names:str,schema:str=None)->_table_manager.TableManager:

    table_names = _lu.force_list(table_names)
    for table_name in table_names:

        table_name = _csu.to_snake_case(table_name)
        tables = []
        t:_table_manager.TableManager
        for t in main.data['table_instances']:
            if schema is not None:
                if t['schema_name'] == schema:
                    if t.table_name == table_name:
                        # tables.append(t)
                        return t
            if t.table_name == table_name:
                # tables.append(t)
                return t
    return None

def _remove_table_instance(main:DatabaseManager,table_names:str,schema:str=None)->None:
    if len(main.data['table_instances']) == 0:
        return
    
    table_names = _lu.force_list(table_names)
    tb_instances = []
    for table_name in table_names:
        table_name = _csu.to_snake_case(table_name)
        t:_table_manager.TableManager
        for t in main.data['table_instances']:
            if schema is not None:
                if t['schema_name'] == schema:
                    if t.table_name != table_name:
                        tb_instances.append(t)
                        # return t
            if t.table_name != table_name:
                tb_instances.append(t)

    main.data['table_instances'] = tb_instances

def _set_table_instance(main:DatabaseManager,table_data:dict)->_table_manager.TableManager:
    _remove_table_instance(main,table_data['table_name'])
    tb = _table_manager.TableManager(main,table_data['table_name'],table_data['schema_name'],summary=table_data)
    main.data['table_instances'].append(tb)
    return tb

def _generate_schema_dirs(main:DatabaseManager,schemas:_Iterable[dict])->_Iterable[dict]:
    '''
        Generate the directories for all schemas in the database.

        ----------

        Arguments
        -------------------------
        `main` {DatabaseManager}
            A reference to the DatabaseManager Instance.
        `schemas` {list}
            A list of schema data dictionaries.

        Return {list}
        ----------------------
        The list of schema data dictionaries with the "dir_path" property added.

        Meta
        ----------
        `author`: Colemen Atwood
        `created`: 06-07-2022 09:51:57
        `memberOf`: DatabaseManager
        `version`: 1.0
        `method_name`: _generate_schema_dirs
        * @xxx [06-07-2022 09:53:47]: documentation for _generate_schema_dirs
    '''


    db_path = main.settings['database_dir_path']
    for s in schemas:
        s['dir_path'] = f"{db_path}\\{s['name']}"
        if _dirs.exists(s['dir_path']) is False:
            _dirs.create(s['dir_path'])
    return schemas

def _generate_table_files(main:DatabaseManager,tables:_Iterable[dict])->_Iterable[dict]:
    '''
        Create table directories and their SQL create files.

        ----------

        Arguments
        -------------------------
        `main` {DatabaseManager}
            A reference to the DatabaseManager Instance.

        `tables` {list}
            A list of table data dictionaries.

        Return {list}
        ----------------------
        A list of table data dictionaries.

        Meta
        ----------
        `author`: Colemen Atwood
        `created`: 06-07-2022 09:54:33
        `memberOf`: DatabaseManager
        `version`: 1.0
        `method_name`: _generate_table_files
        * @xxx [06-07-2022 09:59:51]: documentation for _generate_table_files
    '''


    # skip_no_schema = _obj.get_kwarg(['skip_no_schema'],True,(bool),**kwargs)
    skip_no_schema = main.skip_orphans
    db_path = main.database_dir_path

    # print(f"_generate_table_files.db_path: {db_path}")
    new_tables = []
    for t in tables:
        table_name = t['name']
        schema_name = t['schema_name']
        # print(f"t['columns']: {t['columns']}")
        t['modified_timestamp'] = time.time()

        if skip_no_schema is True:
            if schema_name is None:
                continue
        # schema_string = ""
        # if schema_name is not None:
        #     schema_string = f"\\{schema_name}"


        t['db_path'] = db_path
        t['has_test_files'] = False

        # tb = _table_manager.TableManager(main,table_name,schema_name,summary=t)
        tb = _set_table_instance(main,t)
        
        new_tables.append(tb.table_summary)
    return new_tables

def _set_settings(main:DatabaseManager,key,value):
    if value is not None:
        main.settings[key] = value

def _has_master_changed(main:DatabaseManager)->bool:
    '''
        Check if the master sql file has changed since it was last parsed.

        ----------

        Arguments
        -------------------------
        `main` {DatabaseManager}
            A reference to the DatabaseManager Instance.

        Return {bool}
        ----------------------
        True if the file has changed or it has not been parsed, False otherwise.

        Meta
        ----------
        `author`: Colemen Atwood
        `created`: 06-07-2022 10:01:45
        `memberOf`: DatabaseManager
        `version`: 1.0
        `method_name`: _has_master_changed
        * @xxx [06-07-2022 10:02:51]: documentation for _has_master_changed
    '''


    # summary = main.master_summary
    last_modified = main.master_sql_modified
    current_mod = _cfu.get_modified_time(main.master_sql_path)
    if last_modified is None:
        return True
    if current_mod != last_modified:
        return True
    # print(f"last_modified: {last_modified}")
    # print(f"current_mod: {current_mod}")
    return False

def _organize_summary_tables(data:dict)->dict:
    '''
        Reorganize the parsed master sql data.
        This will place the tables within their respective schema's under the "tables" key.

        ----------

        Arguments
        -------------------------
        `data` {dict}
            The master data dictionary to organize.

        Return {dict}
        ----------------------
        The master data dictionary with the table sorted.

        Meta
        ----------
        `author`: Colemen Atwood
        `created`: 06-05-2022 19:38:44
        `memberOf`: DatabaseManager
        `version`: 1.0
        `method_name`: _organize_summary_tables
        * @xxx [06-05-2022 19:40:27]: documentation for _organize_summary_tables
    '''


    sorted_tables = []
    for s in data['schemas']:
        s['tables'] = []
        for t in data['tables']:
            if t['schema_name'] == s['name']:
                s['tables'].append(t)
                sorted_tables.append(t['name'])

    data['orphan_tables'] = []
    # print(f"sorted_tables: {sorted_tables}")
    for t in data['tables']:
        if t['name'] not in sorted_tables:
            data['orphan_tables'].append(t)

    del data['tables']
    del data['statements']
    return data

def _find_orphan_tables(main:DatabaseManager):
    '''
        Locates all tables that are not associated to a known schema.

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
        `created`: 06-01-2022 11:49:06
        `memberOf`: DatabaseManager
        `version`: 1.0
        `method_name`: _find_orphan_tables
        * @TODO []: documentation for _find_orphan_tables
    '''


    sorted_tables = []
    for s in main.schemas:
        for t in main.tables:
            if t['name'] == s['name']:
                sorted_tables.append(t['name'])

    orphan_tables = []
    # print(f"sorted_tables: {sorted_tables}")
    for t in main.tables:
        if t['name'] not in sorted_tables:
            orphan_tables.append(t)

    # @Mstep [IF] if all tables are orphaned, then None of them are actually orphaned.
    if len(orphan_tables) == len(sorted_tables):
        # @Mstep [RETURN] return an empty list.
        return []
    # @Mstep [RETURN] return the orphan list.
    return orphan_tables

def _to_statement_list(sql):
    sql = sql.replace(";", ";STATEMENT_END")
    statements = sql.split('STATEMENT_END')
    output = [x.strip() for x in statements if len(x.strip()) > 0]
    return output

def _confirm_manager_resources(main:DatabaseManager):

    # @Mstep [IF] if the database directory does not exist.
    if _dirs.exists(main.database_dir_path) is False:
        # @Mstep [] create the database directory.
        _dirs.create(main.database_dir_path)

    # @Mstep [IF] if the master sql and master summary cannot be found.
    if _cfu.exists(main.master_sql_path) is False and _cfu.exists(main.master_summary_path):
        # @Mstep [] alert the user of the issue.
        _log("Could not find the Master Sql File or the Master Summary File.","error")
        _log(f"    Master SQL Path         : {main.master_sql_path}")
        _log(f"    Master Summary Path     : {main.master_summary_path}")
        _log(f"    Database Directory Path : {main.database_dir_path}")
        return False

    # @Mstep [IF] if the master sql file exists.
    if _cfu.exists(main.master_sql_path) is True:
        # @Mstep [IF] if the master_summary path does not exist.
        if _cfu.exists(main.master_summary_path) is False:
            # @Mstep [] get the directory path from the master_sql
            database_dir_path = _os.path.dirname(main.master_sql_path)
            # @Mstep [] change the database_dir_path to be in the same directory as the master_sql
            main.settings['database_dir_path'] = database_dir_path
            # @Mstep [] change the master_summary_path to be in the same directory as the master_sql
            # os.path.dirname(self.master_sql_path)
            main.settings['master_summary_path'] = f"{database_dir_path}\\{main.data['name']}.summary.json"

def _confirm_table_db_paths(master:dict)->bool:
    '''
        Used to confirm that all tables in the master summary file are located within the
        database directory.

        ----------

        Arguments
        -------------------------
        `master` {dict}
            The raw master summary file to validate.

        Return {bool}
        ----------------------
        True upon success, false otherwise.

        Meta
        ----------
        `author`: Colemen Atwood
        `created`: 06-07-2022 12:51:47
        `memberOf`: DatabaseManager
        `version`: 1.0
        `method_name`: _confirm_table_db_paths
        * @xxx [06-07-2022 12:52:41]: documentation for _confirm_table_db_paths
    '''


    database_dir_path = master['database_dir_path']
    db_paths = []
    tables_dicts = []
    # @Mstep [LOOP] iterate the schemas.
    for schema in master['schemas']:
        # @Mstep [LOOP] iterate the table data dictionaries
        for tb in schema['tables']:
            # @Mstep [IF] if the db_path is not equal to the database_dir_path
            if tb['db_path'] != database_dir_path:
                # @Mstep [] append the table to the db_paths list.
                db_paths.append(tb['db_path'])
                tables_dicts.append(tb)

    # @Mstep [IF] if the db_paths has more than one database root directory.
    if len(db_paths) > 1:
        # @Mstep [] alert the user of the issue
        _log(f"{len(db_paths)} Tables are located outside of the database directory: ","error")
        for dp in tables_dicts:
            _log(f"    {dp['db_path']} - {dp['table_name']}","error")

        _log(f"You can correct these paths in the {master['master_summary_file_name']} or parse from the master sql to reset the summary and recreate the database directory.","error")
        # @Mstep [RETURN] return False
        return False
    # @Mstep [RETURN] return True
    return True

def _parse_master_summary_file(main:DatabaseManager):

    if _cfu.exists(main.settings['master_summary_path']) is False:
        _log(f"Could not find {main.settings['master_summary_path']}","error")
        return False

    master:_Union[dict,bool] = _cfu.read.as_json(main.settings['master_summary_path'])
    if isinstance(master,(dict)) is False:
        _log(f"Invalid master summary file: {main.settings['master_summary_path']}","error")
        return False

    else:
        _set_settings(main,"master_summary_file_name",_obj.get_arg(master,['master_summary_file_name'],None,(str)))
        _set_settings(main,"master_summary_path",_obj.get_arg(master,['master_summary_path'],None,(str)))
        _set_settings(main,"master_sql_path",_obj.get_arg(master,['master_sql_path'],None,(str)))
        _set_settings(main,"master_sql_modified",_obj.get_arg(master,['master_sql_modified'],None,(int,float)))
        _set_settings(main,"database_dir_path",_obj.get_arg(master,['database_dir_path'],None,(str)))
        if _confirm_table_db_paths(master) is False:
            _log("\nAborting import from summary file.","error")
            return False



    longest_schema_name = 0
    schemas = []
    # tables = []
    # @Mstep [LOOP] iterate the schema dictionaries
    for schema in master['schemas']:
        if len(schema['name']) > longest_schema_name:
            longest_schema_name = len(schema['name'])

        schemas.append(schema)
        # @Mstep [LOOP] iterate the table data dictionaries
        for tb in schema['tables']:
            # @Mstep [] add the default data to the to the dictionary.
            tb['default_insert_data'] = _obj.get_arg(
                main.data['insert_data']['default'],
                [tb['name']],
                [],
                (list))

            # @Mstep [] add the test data to the dictionary.
            tb['test_insert_data'] = _obj.get_arg(
                main.data['insert_data']['test'],
                [tb['name']],
                [],
                (list))

            # @Mstep [] instantiate a tablemanager and append it to the tables list.
            _set_table_instance(main,tb)
            # tables.append(_table_manager.TableManager(main,tb['name'],None,summary_path=tb))

    main.data['schemas'] = schemas
    main.data['longest_schema_name'] = longest_schema_name
    # main.data['table_instances'] = tables
    main.save_master_summary()
    # main.data['tables'] = tables
    return True


# def _remove_table_data_dict(main:DatabaseManager,table_name:str)->bool:
#     '''
#         Remove a table data dictionary from the database Managers tables list.
#         This will remove any tables that match the table_name provided.
#         Then update DatabaseManager.data['table'] with the updated list.

#         ----------

#         Arguments
#         -------------------------
#         `main` {DatabaseManager}
#             A reference to the DatabaseManager
#         `table_name` {str}
#             The name of the table to remove.

#         Return {bool}
#         ----------------------
#         True upon success, false otherwise.

#         Meta
#         ----------
#         `author`: Colemen Atwood
#         `created`: 06-07-2022 11:09:38
#         `memberOf`: DatabaseManager
#         `version`: 1.0
#         `method_name`: _remove_table_data_dict
#         * @xxx [06-07-2022 11:11:03]: documentation for _remove_table_data_dict
#     '''


#     new_tables = []
#     match_found = False
#     for table in main.tables:
#         if table['table_name'] != table_name:
#             new_tables.append(table)
#         else:
#             match_found = True
#     main.settings['tables'] = new_tables
#     return match_found


# def _delete_table_instance(main:DatabaseManager,table_names:_Union[list,str],schema:_Union[str,None]=None)->bool:
#     '''
#         Remove a table manager instance.

#         ----------

#         Arguments
#         -------------------------
#         `main` {DatabaseManager}
#             A reference to the DatabaseManager

#         `table_name` {list|str}
#             The name of the table to remove.

#         [`schema`=None] {str}
#             If provided, the matching table must also belong to this schema.

#         Return {bool}
#         ----------------------
#         True upon success, false otherwise.

#         Meta
#         ----------
#         `author`: Colemen Atwood
#         `created`: 06-07-2022 11:27:05
#         `memberOf`: DatabaseManager
#         `version`: 1.0
#         `method_name`: _delete_table_instance
#         * @xxx [06-07-2022 11:29:13]: documentation for _delete_table_instance
#     '''


#     table_names = _lu.force_list(table_names)
#     new_tables = []
#     match_found = False
#     for table_name in table_names:

#         table_name = _csu.to_snake_case(table_name)
#         t:_table_manager.TableManager
#         for t in main.data['table_instances']:
#             if schema is not None:
#                 if t['schema_name'] == schema:
#                     if t.table_name != table_name:
#                         new_tables.append(t)
#                         continue
#                     else:
#                         _remove_table_data_dict(main,table_name)
#                         # print(f"Deleting table instance: {table_name}")
#                         match_found = True
#             if t.table_name != table_name:
#                 # print(_Fore.GREEN + f"Keeping {t.name}" + _Style.RESET_ALL)
#                 new_tables.append(t)
#             else:
#                 _remove_table_data_dict(main,table_name)
#                 # print(_Fore.RED + f"Deleting {t.name}" + _Style.RESET_ALL)
#                 # print(f"Deleting table instance: {table_name}")
#                 match_found = True
#     main.data['table_instances'] = new_tables
#     return match_found
