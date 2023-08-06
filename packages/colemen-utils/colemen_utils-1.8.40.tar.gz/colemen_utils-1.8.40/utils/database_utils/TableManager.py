# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=line-too-long
# pylint: disable=unused-wildcard-import
# pylint: disable=wildcard-import
# pylint: disable=unused-import
# pylint: disable=import-outside-toplevel
'''
    A module of utility methods used for parsing and converting python types.

    ----------

    Meta
    ----------
    `author`: Colemen Atwood
    `created`: 06-03-2022 10:22:15
    `memberOf`: type_utils
'''

import time
from typing import TYPE_CHECKING

import utils.database_utils.TableDataManager as tdm
import utils.dict_utils as obj
import utils.file_utils as cfu
import utils.string_utils as csu
import utils.directory_utils as _dirs
import utils.console_utils as _con
_log = _con.log


class TableManager:
    def __init__(self,parent,table_name=None,schema=None,**kwargs):
        self.main = parent
        if TYPE_CHECKING:
            import utils.database_utils.DatabaseManager as _dbm
            self.main:_dbm.DatabaseManager
        self.table_data = None
        self.settings = {
            "db_path":None,
            "setup_complete":False,
            "table_name":None,
            "create_sql_path":None,
            "insert_test_data_sql_path":None,
            "insert_sql_path":None,
            "insert_tmp_sql_path":None,
            "insert_json_path":None,
            "insert_test_data_json_path":None,
            "db_batch_path_test_data":None,
            "has_test_files":None,
        }
        self.data = {
            'has_test_files':False,
            'columns':[],
            'primary_keys':[],
            'keys':[],
            'constraints':[],
            'indexes':[],
            'content_hash':None,
            'default_insert_data':[],
            'test_insert_data':[],
            'comment':None,
        }


        self.default_data_manager = tdm.TableDataManager(parent,self,insert_type="default")
        self.test_data_manager = tdm.TableDataManager(parent,self,insert_type="test")


        summary = obj.get_kwarg(['summary','summary_path'],None,(str,dict),**kwargs)
        # table_data = obj.get_kwarg(['_table_data'],None,(dict),**kwargs)

        if summary is None:
            self.settings['setup_complete'] = self.standard_load(table_name,schema)
        else:
            if isinstance(summary,(dict)):
                # print("Summary Dictionary Provided.")
                self.setup_from_dict(summary)
            if isinstance(summary,(str)):
                self.load_from_summary_file(summary)


        self.settings['verbose'] = obj.get_kwarg(['verbose'],False,(bool),**kwargs)

    # TODO []: insert a new row into the default data json file.
    # TODO []: Set the value of the default data json file.

    # TODO []: insert a new row into the test_data json file.

    def load_from_summary_file(self,summary_path):
        '''
            Retrieves the settings from a summary file.

            ----------

            Arguments
            -------------------------
            `summar_path` {str}
                The path to the summary file to parse.

            Return {type}
            ----------------------
            return_description

            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 06-02-2022 10:21:34
            `memberOf`: TableManager
            `version`: 1.0
            `method_name`: load_from_summary_file
            * @TODO []: documentation for load_from_summary_file
        '''

        if cfu.exists(summary_path):
            data = cfu.read.as_json(summary_path)
            if data:
                self.setup_from_dict(data)

    def standard_load(self,table,schema=None):
        master = cfu.read.as_json(self.main.master_summary_path)
        if isinstance(table,(list)):
            table = table[0]
        table = csu.mod.to_snake_case(table)
        if schema is None:
            for msche in master['schemas']:
                for tb in msche['tables']:
                    if tb['name'] == table:
                        res = self.setup_from_dict(tb)
                        if res:
                            return True
        print(f"Failed to locate table data for: {table}")

        return False

    def setup_from_dict(self,tb):
        # print(f"    Instantiating: {tb['name']}")
        required_keys = ['name','db_path','schema_name']

        if obj.has_keys(tb,required_keys,message_template="The Table Setup Dictionary is missing the '__KEY__' key.") is False:
            return False

        db_path = obj.get_arg(tb,['db_path'],None,(str))
        schema_name = obj.get_arg(tb,['schema_name'],None,(str))
        table_name = obj.get_arg(tb,['name'],None,(str))
        schema_string = ""
        if schema_name is not None:
            schema_string = f"\\{schema_name}"



        self.table_data = tb
        # f"{db_path}{schema_string}\\{table_name}"
        self.settings['db_path'] = db_path
        # self.settings['comment'] = obj.get_arg(tb,['comment'],None,(int,float))
        self.settings['modified_timestamp'] = obj.get_arg(tb,['modified_timestamp'],time.time(),(int,float))
        self.settings['table_dir_path'] = obj.get_arg(tb,['table_dir_path'],f"{db_path}{schema_string}\\{table_name}",(str))
        self.settings['table_name'] = obj.get_arg(tb,['table_name'],table_name,(str))
        self.settings['name'] = self.settings['table_name']
        self.settings['schema_name'] = schema_name
        self.settings['create_sql_path'] = obj.get_arg(tb,['create_sql_path'],f"{db_path}{schema_string}\\{table_name}\\{table_name}.sql",(str))
        self.settings['insert_test_data_sql_path'] = obj.get_arg(
            tb,['insert_test_data_sql_path'],
            f"{db_path}{schema_string}\\{table_name}\\{table_name}.test_data.sql",
            (str))

        self.settings['table_summary_json_path'] = obj.get_arg(
            tb,['table_summary_json_path'],
            f"{db_path}{schema_string}\\{table_name}\\{table_name}.summary.json",
            (str))

        self.settings['insert_sql_path'] = obj.get_arg(
            tb,['insert_sql_path'],
            f"{db_path}{schema_string}\\{table_name}\\{table_name}.insert.sql",
            (str))

        self.settings['insert_json_path'] = obj.get_arg(
            tb,['insert_json_path'],
            f"{db_path}{schema_string}\\{table_name}\\{table_name}.json",
            (str))

        self.settings['insert_test_data_json_path'] = obj.get_arg(
            tb,['insert_test_data_json_path'],
            f"{db_path}{schema_string}\\{table_name}\\{table_name}.test_data.json",
            (str))
        self.settings['raw_statement'] = obj.get_arg(tb,['raw_statement'],None,(str))
        self.data['comment'] = obj.get_arg(tb,['comment'],None,(str))
        self.data['has_test_files'] = obj.get_arg(tb,['has_test_files'],None,(bool))
        self.data['columns'] = obj.get_arg(tb,['columns'],[],(list))
        self.data['primary_keys'] = obj.get_arg(tb,['primary_keys'],[],(list))
        self.data['unique_keys'] = obj.get_arg(tb,['unique_keys'],[],(list))
        self.data['keys'] = obj.get_arg(tb,['keys'],[],(list))
        self.data['constraints'] = obj.get_arg(tb,['constraints'],[],(list))
        self.data['indexes'] = obj.get_arg(tb,['indexes'],[],(list))
        # self.data['content_hash'] = obj.get_arg(tb,['content_hash'],csu.gen.to_hash(self.settings['raw_statement']),(str))
        self.data['content_hash'] = obj.get_arg(tb,['content_hash'],None,(str))
        self.data['default_insert_data'] = obj.get_arg(tb,['default_insert_data'],[],(str))
        self.data['test_insert_data'] = obj.get_arg(tb,['test_insert_data'],[],(str))



        # The name of the table this instance represents.
        # self.settings["table_name"]=tb['name']

        # The path to the SQL file used to create the table.
        # self.settings["create_sql_path"]=tb['create_sql_path']

        # Contains the test data insert SQL.
        # self.settings["insert_test_data_sql_path"]=f"{tb['table_dir_path']}\\{tb['name']}.test_data.sql"
        # Path to the insert SQL file for the default data
        # self.settings["insert_sql_path"]=f"{tb['table_dir_path']}\\{tb['name']}.insert.sql"
        # Path to the insert JSON file for the default data
        # self.settings["insert_json_path"]=f"{tb['table_dir_path']}\\{tb['name']}.json"

        # self.settings["insert_tmp_sql_path"]=f"{tb['table_dir_path']}\\{tb['name']}.tmp.sql"

        # Path to the insert JSON file for the test data
        # self.settings["insert_test_data_json_path"]=f"{tb['table_dir_path']}\\{tb['name']}.test_data.json"
        # Contains the commands to update the database with the test data
        # self.settings["test_data_batch_path"]=f"{tb['table_dir_path']}\\{tb['name']}.test_data.bat"
        # self.settings["test_data_batch_path"]=f"{tb['table_dir_path']}\\_{tb['name']}.reset.test_data.bat"
        # Contains the commands to update the database with the default data.
        # self.settings["reset_batch_path"]=f"{tb['table_dir_path']}\\_{tb['name']}.reset.bat"

        # This directory contains duplicates of all the batch files for easier access
        # self.settings["db_batch_path_test_data"]=f"{self.main.settings['database_batch_dir']}\\{tb['name']}.test_data.bat"
        # This directory contains duplicates of all the batch files for easier access
        # self.settings["db_batch_path"]=f"{tb['table_dir_path']}\\_{tb['name']}.reset.bat"
        # self.settings["has_test_files"]=False

        # self.confirm_local_resources()
        self.generate_table_local_resources()

        # @Mstep [] confirm the test files exist.
        # self.confirm_test_files()
        # if cfu.exists(self.settings["insert_tmp_sql_path"]):
        #     cfu.delete(self.settings["insert_tmp_sql_path"])
        return True

    def generate_table_local_resources(self):
        '''
            Generate the table's local resources.
            This will create the table folder in the database directory.
            Generate the create SQL file and the data JSON files.

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
            `created`: 06-05-2022 16:56:22
            `memberOf`: TableManager
            `version`: 1.0
            `method_name`: generate_table_local_resources
            * @TODO []: documentation for generate_table_local_resources
        '''

        if self.main.create_dir is True:
            # _log(f"    generate_table_local_resources: {self.name}")
            # @Mstep [] create the table_dir_path.
            self.create_table_dir()
            # @Mstep [IF] if the create file does not exist.
            if self.create_sql_exists is False:
                # @Mstep [] create the file.
                self.gen_create_sql()
            else:
                if _has_create_changed(self) is True:
                    self.gen_create_sql()
                    
            # @Mstep [IF] if the create file exists.
            # if self.create_sql_exists is True:
            #     # @Mstep [] create the file.
            #     self.gen_create_sql()


            self.default_data_manager.import_data()
            self.test_data_manager.import_data()

    def ready(self):
        return self.settings['setup_complete']


    def reset_default_table(self):
        '''
            Reset the table to contain only the default data.

            ----------

            Return {bool}
            ----------------------
            True if the table structure is reset and data is as well, false otherwise.

            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 06-05-2022 16:25:00
            `memberOf`: TableManager
            `version`: 1.0
            `method_name`: reset_default_table
            * @xxx [06-05-2022 16:39:52]: documentation for reset_default_table
        '''

        self.default_data_manager.reset_table()

    def reset_test_table(self):
        '''
            Reset the table to contain only the test data.

            ----------

            Return {bool}
            ----------------------
            True if the table structure is reset and data is as well, false otherwise.

            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 06-05-2022 16:25:00
            `memberOf`: TableManager
            `version`: 1.0
            `method_name`: reset_test_table
            * @xxx [06-05-2022 16:39:52]: documentation for reset_table
        '''
        return self.test_data_manager.reset_table()

    def gen_default_reset(self):
        '''
            Generate the default data insert SQL and reset the table with new data.

            ----------

            Return {bool}
            ----------------------
            True upon success, false otherwise.

            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 06-05-2022 16:54:37
            `memberOf`: TableManager
            `version`: 1.0
            `method_name`: gen_default_reset
            * @xxx [06-05-2022 16:55:26]: documentation for gen_default_reset
        '''


        print(f"Generating insert and reseting table: {self.name}")
        success = self.generate_default_insert()
        if success:
            return self.reset_default_table()

    @property
    def default_data(self)->list:
        '''
            Get this tables default data list.

            ----------


            Return {list}
            ----------------------
            A list of dictionaries.

            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 06-09-2022 14:58:12
            `memberOf`: TableManager
            `version`: 1.0
            `method_name`: default_data
            * @xxx [06-09-2022 14:59:29]: documentation for default_data
        '''


        return self.default_data_manager.insert_data
        # return self.data['default_insert_data']

    def gen_test_reset(self):
        '''
            Generate the test data insert SQL and sync the new data to the database.

            ----------


            Return {bool}
            ----------------------
            True upon success, false otherwise.

            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 06-05-2022 16:23:29
            `memberOf`: TableManager
            `version`: 1.0
            `method_name`: gen_test_reset
            * @xxx [06-05-2022 16:40:19]: documentation for gen_test_reset
        '''


        res = self.generate_test_insert()
        if res:
            return self.reset_test_table()
        return False

    def truncate_table(self):
        '''
            Drop the table and recreate it.
            This isn't actually truncating the table, this is intended to also
            allow new columns to be created and to reset the contents of the table.

            ----------

            Return {bool}
            ----------------------
            True upon success, false otherwise.

            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 06-02-2022 14:28:09
            `memberOf`: TableManager
            `version`: 1.0
            `method_name`: truncate_table
            * @xxx [06-02-2022 14:40:47]: documentation for truncate_table
        '''
        return self.default_data_manager.truncate()


    def drop_table(self):
        '''
            Drop the table from the database.

            ----------

            Return {bool}
            ----------------------
            True upon success, false otherwise.

            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 06-02-2022 14:28:09
            `memberOf`: TableManager
            `version`: 1.0
            `method_name`: truncate_table
            * @xxx [06-02-2022 14:40:47]: documentation for truncate_table
        '''
        drop = csu.sql.drop_table(self.name,self.schema)
        if self.main.connect():
            _log(f"Dropping Table from database: {self.name}","error")
            return self.main.execute_single_statement(drop)
        return True
        # return self.default_data_manager.truncate()



    def generate_test_insert(self):
        '''
            Generate the test data insert SQL.

            ----------


            Return {bool}
            ----------------------
            True upon success, false otherwise.

            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 06-05-2022 16:22:57
            `memberOf`: TableManager
            `version`: 1.0
            `method_name`: generate_test_insert
            * @xxx [06-05-2022 16:23:19]: documentation for generate_test_insert
        '''


        return self.test_data_manager.gen_sql_insert()

    def generate_default_insert(self):
        '''
            Generate the default insert SQL

            ----------

            Return {bool}
            ----------------------
            True upon success, false otherwise.

            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 06-05-2022 16:22:10
            `memberOf`: TableManager
            `version`: 1.0
            `method_name`: generate_default_insert
            * @xxx [06-05-2022 16:22:49]: documentation for generate_default_insert
        '''


        return self.default_data_manager.gen_sql_insert()

    def generate_insert(self):
        '''
            Genearte the insert SQL for the test data and the default data.

            ----------

            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 06-05-2022 16:21:25
            `memberOf`: TableManager
            `version`: 1.0
            `method_name`: generate_insert
            * @xxx [06-05-2022 16:21:55]: documentation for generate_insert
        '''


        self.generate_default_insert()
        self.generate_test_insert()





    def save_default_data(self,gen_sql=True):
        '''
            Save the default insert data to the insert json file.

            ----------

            Arguments
            -------------------------
            [`gen_sql`=True] {bool}
                if True, regenerate the insert SQL file as well.


            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 06-01-2022 15:23:15
            `memberOf`: TableManager
            `version`: 1.0
            `method_name`: save_default_data
            * @xxx [06-01-2022 15:23:45]: documentation for save_default_data
        '''

        return self.default_data_manager.save(gen_sql)

    def save_test_data(self,gen_sql=True):
        '''
            Save the test insert data to the insert json file.

            ----------

            Arguments
            -------------------------
            [`gen_sql`=True] {bool}
                if True, regenerate the insert SQL file as well.

            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 06-01-2022 15:23:15
            `memberOf`: TableManager
            `version`: 1.0
            `method_name`: save_test_data
            * @xxx [06-01-2022 15:23:45]: documentation for save_test_data
        '''

        return self.test_data_manager.save(gen_sql)

    def save_insert_data(self,gen_sql=True):
        '''
            Save the test and default insert data to their json files.save_insert_data

            ----------

            Arguments
            -------------------------
            [`gen_sql`=True] {bool}
                if True, regenerate the insert SQL files as well.


            Return {None}
            ----------------------
            returns nothing.

            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 06-02-2022 12:30:11
            `memberOf`: TableManager
            `version`: 1.0
            `method_name`: save_insert_data
            * @xxx [06-02-2022 12:31:54]: documentation for save_insert_data
        '''

        self.test_data_manager.save(gen_sql)
        self.default_data_manager.save(gen_sql)


    def delete_test_data(self):
        '''
            This will permanently delete the test_data json file and the test data sql file.

            ----------

            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 06-02-2022 12:22:19
            `memberOf`: TableManager
            `version`: 1.0
            `method_name`: delete_test_data
            * @xxx [06-02-2022 12:22:47]: documentation for delete_test_data
        '''
        self.test_data_manager.delete_data()

    def delete_default_data(self):
        '''
            This will permanently delete the default data json file and the default data sql insert file.

            ----------

            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 06-02-2022 12:22:19
            `memberOf`: TableManager
            `version`: 1.0
            `method_name`: delete_default_data
            * @xxx [06-02-2022 12:22:47]: documentation for delete_default_data
        '''
        self.default_data_manager.delete_data()

    def delete_data(self):
        '''
            This will permanently delete:
            - Default data json file
            - Default data SQL insert file
            - Test data json file
            - Test data SQL insert file

            ----------

            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 06-02-2022 12:22:19
            `memberOf`: TableManager
            `version`: 1.0
            `method_name`: delete_data
            * @xxx [06-02-2022 12:22:47]: documentation for delete_data
        '''

        self.delete_test_data()
        self.delete_default_data()

    def delete(self)->bool:
        '''
            This will delete all data in this tables directory.
            It will drop the table from the database as well.

            BE CAREFUL WITH THIS!!!
            This will permanently delete all default and test data as well.

            ----------


            Return {bool}
            ----------------------
            True upon success, false otherwise.

            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 06-07-2022 10:37:05
            `memberOf`: TableManager
            `version`: 1.0
            `method_name`: delete
            * @xxx [06-07-2022 10:38:05]: documentation for delete
        '''
        # print(f"Deleting Table: {self.name}")
        self.drop_table()
        self.settings['is_deleted'] = True
        return _dirs.delete(self.table_dir_path)


    def insert_data(self,data,overwrite=False):
        '''
            Insert a new row or rows into the default data json file.

            ----------

            Arguments
            -------------------------
            `data` {dict|list}
                A dictionary or list of dictionaries to insert.
                Keys must correspond to the column in the table, they are case sensitive.
                This does `NOT` type match the columns, so if you fuck it up, its on you.

            [`overwrite`=False] {bool}
                If True, the existing data is overwritten by the new data.

            Return {bool}
            ----------------------
            True upon success, false otherwise.

            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 06-01-2022 15:14:20
            `memberOf`: TableManager
            `version`: 1.0
            `method_name`: insert_default_data
            * @xxx [06-01-2022 15:16:46]: documentation for insert_default_data
        '''
        return self.default_data_manager.set_insert_data(data,overwrite=overwrite)

    def insert_test_data(self,data,overwrite=False):
        '''
            Insert a new row or rows into the test_data json file.

            ----------

            Arguments
            -------------------------
            `data` {dict|list}
                A dictionary or list of dictionaries to insert.
                Keys must correspond to the column in the table, they are case sensitive.
                This does `NOT` type match the columns, so if you fuck it up, its on you.

            [`overwrite`=False] {bool}
                If True, the existing data is overwritten by the new data.

            Return {type}
            ----------------------
            return_description

            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 06-01-2022 15:14:20
            `memberOf`: TableManager
            `version`: 1.0
            `method_name`: insert_default_data
            * @xxx [06-01-2022 15:16:46]: documentation for insert_default_data
        '''
        return self.test_data_manager.set_insert_data(data,overwrite=overwrite)



    def backup(self):
        '''
            Get all contents from the table and save them to the json insert file. {table_name}.json

            ----------

            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 05-12-2022 10:13:50
            `memberOf`: TableManager
            `version`: 1.0
            `method_name`: backup
            # @xxx [05-12-2022 10:15:00]: documentation for backup
        '''

        if self.ready() is False:
            return False

        data = self.get_current_contents()
        if isinstance(data,(list)):
            if len(data) > 0:
                self.default_data_manager.set_insert_data(data)
            else:
                print(f"{self.settings['table_name']} has no contents.")

    # def update_local_json(self,ec_json):
    #     cfu.writer.to_json(self.settings['insert_json_path'],ec_json)

    def import_default_json_data(self,ignore_errors=False):
        '''
            Reads this table's insert json file and returns the contents.

            ----------

            Return {list|bool}
            ----------------------
            The contents of the insert json file, which should be a list..
            If the file does not exist it will return False.

            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 05-21-2022 13:04:36
            `memberOf`: TableManager
            `version`: 1.0
            `method_name`: import_default_json_data
            # @xxx [05-21-2022 13:05:43]: documentation for import_default_json_data
        '''


        if cfu.exists(self.settings['insert_json_path']):
            return cfu.read.as_json(self.settings['insert_json_path'])
        else:
            if ignore_errors is False:
                print(f"Failed to locate the insert json file for table {self.settings['table_name']}")
                print(f"File path: {self.settings['insert_json_path']}")
            return False
        return False

    def save_json(self,name,data):
        if name in self.settings:
            cfu.writer.to_json(self.settings[name],data)
            return True
        return False

    # def insert_activity_type(self,data):
    #     db = self.main.connect_to_db()
    #     sql = ''
    #     column_string = _gen_column_string(data)
    #     sql += f"INSERT INTO `{self.table_data['schema']}`.`{self.table_data['name']}` ({column_string}) VALUES \n"
    #     sql += f"{_gen_value_string(data)};"
    #     print("sql: ",sql)
    #     result = db.run(sql)
    #     print("result: ",result)
    #     db.close()

    def insert_from_sql(self,sql_path=None):
        '''
            Execute an insert statement on the database from an sql file.

            ----------

            Arguments
            -------------------------
            [`sql_path`=None] {string}
                The path to the sql file to insert, if not provided the table's default insert sql is used.

            Return {type}
            ----------------------
            return_description

            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 05-12-2022 10:11:00
            `memberOf`: TableManager
            `version`: 1.0
            `method_name`: insert_from_sql
            # @xxx [05-12-2022 10:12:37]: documentation for insert_from_sql
        '''

        if sql_path is None:
            sql_path = self.settings['insert_sql_path']

        if cfu.exists(sql_path):
            # sql = cfu.read.read(sql_path)
            db = self.main.connect_to_db()
            result = db.executeSqlFromFile(sql_path)

    def get_current_contents(self):
        db = self.main.connect_to_db()
        db.run(f"SELECT * from `{self.table_data['schema']}`.`{self.table_data['name']}`;")
        result = db.fetchall()
        db.close()
        return result


    def list_local_values(self,key=None):
        data = self.import_default_json_data()
        divider = csu.gen.title_divider(self.settings['table_name'])
        print(f"{divider}\n")
        for x in data:
            if key is not None:
                if key in x:
                    print(f"    {x[key]}")

        print(f"\n{divider}")

    def get_row(self,column,value):
        '''
            Get a row from this table's default data that has a matching value in the column specified.

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
            `created`: 06-05-2022 18:49:16
            `memberOf`: TableManager
            `version`: 1.0
            `method_name`: get_row
            * @TODO []: documentation for get_row
        '''


        data = self.import_default_json_data()
        # divider = csu.gen.title_divider(self.settings['table_name'])
        # print(f"{divider}\n")
        for x in data:
            if column in x:
                if x[column] == value:
                    return x
        return False


    @property
    def indexes(self):
        '''
            Get this TableManager's indexes


            `default`:[]


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-21-2022 10:00:45
            `@memberOf`: TableManager
            `@property`: indexes
        '''
        return obj.get_arg(self.data,['indexes'],[],(list))

    @property
    def fulltext_indexes(self):
        '''
            Get this TableManager's fulltext_indexes


            `default`:None


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-21-2022 10:01:57
            `@memberOf`: TableManager
            `@property`: fulltext_indexes
        '''
        value = []
        for idx in self.indexes:
            if idx['index_type'] == "fulltext":
                value.append(value)
        return value



    @property
    def table_dir_path(self):
        '''
            Get the path to this tables directory.

            ----------

            Return {str}
            ----------------------
            The path to this table's directory.

            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 06-05-2022 18:32:43
            `memberOf`: TableManager
            `version`: 1.0
            `method_name`: table_dir_path
            * @xxx [06-05-2022 18:34:15]: documentation for table_dir_path
        '''


        return self.settings['table_dir_path']

    def create_table_dir(self):
        '''
            Create the table's folder in the database directory.

            ----------

            Return {bool}
            ----------------------
            True upon success, false otherwise.

            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 06-05-2022 17:01:17
            `memberOf`: TableManager
            `version`: 1.0
            `method_name`: create_table_dir
            * @xxx [06-05-2022 17:02:24]: documentation for create_table_dir
        '''

        # @Mstep [] create the table_dir_path.
        if _dirs.exists(self.table_dir_path) is False:
            print(f"self.table_dir_path:{self.table_dir_path}")
            return _dirs.create(self.table_dir_path)
        return True


    @property
    def next_id(self):
        '''
            Get the next row's id for this table.

            ----------

            Return {int}
            ----------------------
            The next auto_incrementing id.

            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 06-05-2022 18:34:26
            `memberOf`: TableManager
            `version`: 1.0
            `method_name`: next_id
            * @xxx [06-05-2022 18:35:35]: documentation for next_id
        '''


        data = self.import_default_json_data()
        if isinstance(data,(list)):
            return len(data) + 1
        else:
            return 1

    @property
    def next_test_id(self):
        data = self.main.insert_data['test'][self.name]
        # data = self.import_default_json_data()
        if isinstance(data,(list)):
            return len(data) + 1
        else:
            return 1

    @property
    def primary(self):
        '''
            The name of the primary column of this table.

            ----------

            Return {str}
            ----------------------
            The primary column's name.

            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 06-05-2022 18:38:45
            `memberOf`: TableManager
            `version`: 1.0
            `method_name`: primary
            * @xxx [06-05-2022 18:39:15]: documentation for primary
        '''


        return get_primary_column(self)

    @property
    def table_name(self)->str:
        '''
            The name of this table.

            ----------

            Return {str}
            ----------------------
            The name of this table.

            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 06-05-2022 18:37:40
            `memberOf`: TableManager
            `version`: 1.0
            `method_name`: table_name
            * @xxx [06-05-2022 18:38:26]: documentation for table_name
        '''


        return self.settings['table_name']



    @property
    def default_insert_json(self):
        '''
            Reads the table's `default data` insert json file and returns the contents.

            ----------

            Return {list}
            ----------------------
            The contents of the insert json file, which should be a list..
            If the file does not exist it will return an empty list.

            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 05-21-2022 13:04:36
            `memberOf`: TableManager
            `version`: 1.0
            `method_name`: import_default_json_data
            # @xxx [05-21-2022 13:05:43]: documentation for import_default_json_data
        '''

        return self.default_data_manager.import_data(True)

    @property
    def table_summary(self)->dict:
        '''
            Get this table's summary.

            ----------


            Return {dict}
            ----------------------
            This table's summary.

            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 06-05-2022 18:35:47
            `memberOf`: TableManager
            `version`: 1.0
            `method_name`: table_summary
            * @xxx [06-05-2022 18:37:25]: documentation for table_summary
        '''

        return {**self.settings, **self.data}

    def save_table_summary(self):
        '''
            Save this table's summary to its json file.

            ----------

            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 06-05-2022 18:39:40
            `memberOf`: TableManager
            `version`: 1.0
            `method_name`: save_table_summary
            * @xxx [06-05-2022 18:40:24]: documentation for save_table_summary
        '''

        cfu.writer.to_json(self.table_summary_json_path,self.table_summary)

    def update_table_data(self,new_data):
        if isinstance(new_data,(dict)):
            self.data = {**self.data,**new_data}


    @property
    def table_summary_json_path(self)->str:
        '''
            Get this table's json summary path.

            ----------

            Return {str}
            ----------------------
            The file path to this table's json summary file.

            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 06-05-2022 18:40:58
            `memberOf`: TableManager
            `version`: 1.0
            `method_name`: table_summary_json_path
            * @xxx [06-05-2022 18:41:35]: documentation for table_summary_json_path
        '''


        return self.settings['table_summary_json_path']

    @property
    def test_insert_json(self):
        '''
            Reads the table's `test data` insert json file and returns the contents.

            ----------

            Return {list}
            ----------------------
            The contents of the insert json file, which should be a list..
            If the file does not exist it will return an empty list.

            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 05-21-2022 13:04:36
            `memberOf`: TableManager
            `version`: 1.0
            `method_name`: import_default_json_data
            # @xxx [05-21-2022 13:05:43]: documentation for import_default_json_data
        '''

        return self.test_data_manager.import_data(True)


    def gen_create_sql(self):
        '''
            Generate the create SQL file and save it to the table's directory.

            ----------

            Return {bool}
            ----------------------
            True upon success, false otherwise.

            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 06-05-2022 16:58:41
            `memberOf`: TableManager
            `version`: 1.0
            `method_name`: gen_create_sql
            * @xxx [06-05-2022 16:59:40]: documentation for gen_create_sql
        '''

        if self.settings['raw_statement'] is not None:
            sql = self.settings['raw_statement']
            sql = f"--====================================================================== CREATE\n\n\n{sql}"
            sql = gen_drop_table(self.name,self.schema,sql)
            sql = prepend_header(None,sql)
            self.data['content_hash'] = csu.gen.to_hash(self.settings['raw_statement'])
            
            cfu.writer.write(self.create_sql_path,sql)
            # self.main.update_table_summary(self.name,self.table_summary)
            return True
        return False

    @property
    def create_sql_path(self)->str:
        '''
            Get the path to the create SQL file.

            ----------

            Return {str}
            ----------------------
            The path to the create SQL file.

            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 06-05-2022 18:42:15
            `memberOf`: TableManager
            `version`: 1.0
            `method_name`: create_sql_path
            * @xxx [06-05-2022 18:43:39]: documentation for create_sql_path
        '''


        return self.settings['create_sql_path']

    @property
    def create_sql_exists(self):
        '''
            Check that the create SQL file exists.

            ----------

            Return {bool}
            ----------------------
            True if the file exists, False otherwise.

            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 06-05-2022 18:47:00
            `memberOf`: TableManager
            `version`: 1.0
            `method_name`: create_sql_exists
            * @xxx [06-05-2022 18:47:42]: documentation for create_sql_exists
        '''


        if cfu.exists(self.create_sql_path) is False:
            return False
        return True

    @property
    def schema(self):
        '''
            Get the name of the schema that the table belongs to.

            ----------

            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 06-02-2022 08:48:02
            `memberOf`: TableDataManager
            `version`: 1.0
            `method_name`: schema
            * @xxx [06-02-2022 08:48:37]: documentation for schema
        '''

        return self.table_data['schema_name']

    @property
    def column_names(self)->list:
        '''
            Get a list of this table's column names.

            ----------

            Return {list}
            ----------------------
            A list of this table's column names.

            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 06-05-2022 18:43:57
            `memberOf`: TableManager
            `version`: 1.0
            `method_name`: column_names
            * @xxx [06-05-2022 18:45:53]: documentation for column_names
        '''


        cols:list = self.table_meta_data
        names = []
        col_data:dict
        for col_data in cols:
            names.append(col_data['name'])
        return names


    @property
    def column_data(self)->list:
        '''
            Get a list of this table's columns and their meta data.

            ----------

            Return {list}
            ----------------------
            A list of this table's column names.

            {
                "name": "amount",\n
                "type": "int",\n
                "allow_nulls": false,\n
                "comment": "Amount (in cents) to be transferred to your bank account or debit card.",\n
                "default": null,\n
                "is_primary_key": false\n
            },


            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 06-05-2022 18:43:57
            `memberOf`: TableManager
            `version`: 1.0
            `method_name`: column_names
            * @xxx [06-05-2022 18:45:53]: documentation for column_names
        '''
        return self.table_meta_data




    @property
    def table_meta_data(self)->list:
        if self.data['columns'] is None:
            sql = cfu.readr(self.create_sql_path)
            self.data['create_file_data']  = csu.parse.sql.parse(sql)
            self.data['columns'] = self.data['create_file_data']['columns']
            # cfu.writer.to_json("col_data.delete.json",col_data)
            return self.data['columns']
        else:
            return self.data['columns']

    @property
    def name(self)->str:
        '''
            Get this table's name.

            ----------


            Return {str}
            ----------------------
            The name of this table.

            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 06-05-2022 18:46:13
            `memberOf`: TableManager
            `version`: 1.0
            `method_name`: name
            * @xxx [06-05-2022 18:46:39]: documentation for name
        '''


        return self.settings['table_name']


def _has_create_changed(table:TableManager):
    prev_hash = table.data['content_hash']
    current_hash = csu.gen.to_hash(table.settings['raw_statement'])
    if prev_hash != current_hash:
        # print(f"    sql has changed, regenerating create SQL for {table.name}")
        # print(f"    prev: {prev_hash}")
        # print(f"    curr: {current_hash}")
        return True
    return False

def get_column_by_name(table,col):
    for c in table.data['column_data']:
        if c['name'] == col:
            return c
    return None

def get_primary_column(table):
    for c in table.table_meta_data:
        if c['is_primary_key'] is True or c['primary_key'] is True:
            return c['name']
    return None

def allow_null(table,column):
    for c in table.table_meta_data:
        if c['allow_nulls'] is True:
            return True
    return False

def has_required_columns(table,row,print_errors=True):
    '''
        validate a dictionary to confirm each column that does not allow nulls
        has a value.

        ----------

        Arguments
        -------------------------
        `table` {TableManager}
            A reference to the table manager instance.
        `row` {dict}
            The data dictionary to validate.
        [`print_errors`=True] {bool}
            If False it will just return False and not print the warning.

        Return {bool}
        ----------------------
        True upon success, false otherwise.

        Meta
        ----------
        `author`: Colemen Atwood
        `created`: 06-01-2022 15:18:30
        `memberOf`: TableManager
        `version`: 1.0
        `method_name`: has_required_columns
        * @xxx [06-01-2022 15:20:28]: documentation for has_required_columns
    '''


    for k,v in row.items():
        if v is None:
            if allow_null(table,k) is False:
                if print_errors:
                    print(f"{k} is a required column in {table.name}, None was provided.")
                return False
    return True

def has_column(table,col):
    for c in table.data['column_data']:
        if c['name'] == col:
            return True
    return False

def validate_row_types(table,data):
    new_data = {}
    for c in table.data['column_data']:
        val = None
        if c['name'] in data:
            val = data[c]
        if val is None:
            if c['allow_nulls'] is True:
                new_data[c['name']] = data[c]

        # csu.parse.sql.sql_type_to_python(c['type'])
        sql_type = csu.parse.sql.sql_type_to_python(c['type'])
        if sql_type is not None:
            if str(type(val).__name__) in sql_type:
                new_data[c['name']] = data[c]
            else:
                if "bool" in sql_type:
                    bool_val = csu.convert.to_bool(val)
                    new_data[c['name']] = bool_val
                    continue

def prepend_header(header,sql):
    '''
        Append a header to the sql provided.

        ----------

        Arguments
        -------------------------
        `header` {str|bool}
            Rembember! This must be commented as it will be in the sql file!
            The header to apply to the sql or the path to the header file.

            if False, no header will be applied.

        `sql` {str}
            The sql content to prepend the header to.

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
        `created`: 06-01-2022 10:02:44
        `memberOf`: DatabaseManager
        `version`: 1.0
        `method_name`: prepend_header
        @xxx [06-01-2022 10:05:18]: documentation for prepend_header
    '''
    if header is False:
        return sql

    default_header = '''

-- * ======================= DO NOT MODIFY ======================== *
-- * This file was automatically generated from the master.sql file *
-- * Update the database model and export it to master.sql          *
-- * ======================= DO NOT MODIFY ======================== *'''
    if isinstance(header,(str)):
        if cfu.exists(header) is False:
            default_header = header
        else:
            h =cfu.readr(header)
            if h is not False:
                default_header = h

    # @Mstep [] prepend the header text.
    return f"{default_header}\n{sql}"

def gen_drop_table(table_name,schema_name=None,sql=None):
    '''
        Generate a drop table statement

        ----------

        Arguments
        -------------------------
        `table_name` {str}
            The name of the table to create a drop statement for.
        [`schema_name`=None] {str}
            The name of the schema the table belongs to.
        [`sql`=None] {str}
            The sql to prepend the drop statement to.

        Return {str}
        ----------------------
        The drop statement if no sql is provided, otherwise The sql with the drop statement prepended.

        Meta
        ----------
        `author`: Colemen Atwood
        `created`: 06-01-2022 10:12:12
        `memberOf`: DatabaseManager
        `version`: 1.0
        `method_name`: gen_drop_table
        * @xxx [06-01-2022 10:44:44]: documentation for gen_drop_table
    '''

    drop = csu.sql.drop_table(table_name,schema_name)
    if sql is not None:
        return f"\n\n{drop}\n\n{sql}"
    return drop


