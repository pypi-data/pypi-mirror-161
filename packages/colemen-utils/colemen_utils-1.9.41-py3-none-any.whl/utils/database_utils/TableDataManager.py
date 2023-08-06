
# pylint: disable=missing-class-docstring
# pylint: disable=anomalous-backslash-in-string
# pylint: disable=line-too-long
# pylint: disable=import-outside-toplevel
'''
    Used by a TableManager instance to manage the default and test data associated to the table.

    ----------

    Meta
    ----------
    `author`: Colemen Atwood
    `created`: 06-05-2022 16:46:53
    `memberOf`:  boobs
    `name`: TableDataManager
    * @xxx [06-05-2022 16:48:41]: documentation for TableDataManager
'''




# import os
# import json
from typing import TYPE_CHECKING

import utils.file_utils as _cfu
import utils.string_utils as _csu
import utils.dict_utils as _obj
import utils.list_utils as _lu

import config as _config
import utils.console_utils as _con
_log = _con.log
# import colemen_file_utils as cfu
# import colemen_string_utils as csu
# import utils.object_utils as obj


class TableDataManager:
    def __init__(self,database,table,**kwargs):
        self.db = database
        self.table = table
        self.settings = {}
        self.data = {}

        self.insert_type = _obj.get_kwarg(['insert_type'],"default",(str),**kwargs)
        self.set_defaults()

    def set_defaults(self):
        self.settings = self.table.settings

    def import_data(self,ignore_errors=False):
        '''
            Reads the table's insert json file and returns the contents.

            ----------

            Arguments
            -------------------------

            [`ignore_errors`=False] {bool}
                If True, the errors will not printed to the console.

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
        path = self.data_path
        result = []

        if isinstance(path,(str)):
            if _cfu.exists(path):
                result = _cfu.read.as_json(path)
        else:
            if ignore_errors is False:
                print(f"Failed to locate the insert json file for table {self.name}")
                print(f"File path: {path}")

        return result

    def save(self,gen_sql=True):
        '''
            Save the insert data to the insert json file.

            ----------

            Arguments
            -------------------------
            [`gen_sql`=True] {bool}
                If True, it will generate the insert SQL and save it as well.


            Return {bool}
            ----------------------
            True upon success, false otherwise.

            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 06-01-2022 15:23:15
            `memberOf`: TableManager
            `version`: 1.0
            `method_name`: save
            * @xxx [06-01-2022 15:23:45]: documentation for save
        '''

        idata = self.insert_data
        path = self.data_path

        if isinstance(idata,(list)) is False:
            return False

        # @Mstep [IF] if the data is empty.
        if len(idata) == 0:
            # @Mstep [IF] if the json file already exists
            if _cfu.exists(path):
                # @Mstep [] delete the json file
                self.delete_json_data()
                # @Mstep [] delete the sql file.
                self.delete_sql_insert()
            return True

        if path is not None:
            _cfu.writer.to_json(path,idata)
            if gen_sql:
                self.gen_sql_insert()
            return True
        return False

    # xxx [06-02-2022 09:29:14]: generate the data insert SQL file

    def truncate(self):
        '''
            Truncate data in the table.
            Not an actual truncate statement, it just resets the table structure.

            ----------

            Return {bool}
            ----------------------
            True upon success, false otherwise.

            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 06-05-2022 16:40:54
            `memberOf`: TableDataManager
            `version`: 1.0
            `method_name`: truncate
            * @TODO []: documentation for truncate
        '''


        print(f"truncating table: {self.name}")
        self.db.connect()
        # @Mstep [] execute the create table sql which will essentially truncate it and add new columns.
        return self.db.execute_sql_from_file(self.create_sql_path)

    # def drop_table(self):
    #     if TYPE_CHECKING:
    #         from utils.database_utils.DatabaseManager import DatabaseManager as db
    #         self.db:db

    #     drop = _csu.sql.drop_table(self.table.name,self.table.schema)
    #     self.db.connect()
    #     return self.db.execute_single_statement(drop)

    def reset_table(self):
        '''
            Reset the data in the table using the test or default data.

            ----------

            Return {bool}
            ----------------------
            True if the table structure is reset and data is, false otherwise.

            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 06-05-2022 16:25:00
            `memberOf`: TableDataManager
            `version`: 1.0
            `method_name`: reset_table
            * @xxx [06-05-2022 16:39:52]: documentation for reset_table
        '''

        sql = self.insert_sql
        if TYPE_CHECKING:
            from utils.database_utils.DatabaseManager import DatabaseManager as db
            self.db:db
        success = True
        if isinstance(sql,(str)):
            self.db.connect()
            # @Mstep [] execute the create table sql which will essentially truncate it and add new columns.
            if _cfu.exists(self.create_sql_path):
                success = self.db.execute_sql_from_file(self.create_sql_path)
            if _cfu.exists(self.insert_path):
                # @Mstep [] execute the insert sql
                success = self.db.execute_sql_from_file(self.insert_path)
            # print(f"boobs")
        return success

    def gen_sql_insert(self):
        '''
            Generate the insert sql for the data.

            ----------

            Return {bool}
            ----------------------
            True upon success, false otherwise.

            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 06-02-2022 09:27:32
            `memberOf`: TableDataManager
            `version`: 1.0
            `method_name`: gen_sql_insert
            * @xxx [06-02-2022 09:28:12]: documentation for gen_sql_insert
        '''


        data = self.insert_data
        path = self.insert_path

        if isinstance(data,(list)) is False:
            print("Invalid insert data, it must be a list of dictionaries.")
            return False

        if len(data) == 0:
            # @Mstep [] delete the sql file.
            self.delete_sql_insert()
            return True

        sql = _csu.sql.insert_sql(data,self.name,self.schema)
        if sql:
            _cfu.write(path,sql)
            return True

    def delete_data(self):
        '''
            Delete the insert data.

            ----------

            Return {bool}
            ----------------------
            True upon success, false otherwise.

            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 06-05-2022 16:44:40
            `memberOf`: TableDataManager
            `version`: 1.0
            `method_name`: delete_data
            * @xxx [06-05-2022 16:46:22]: documentation for delete_data
        '''

        self.set_insert_data(None)
        success = False
        res = self.delete_sql_insert()
        if res is True:
            success = self.delete_json_data()
        return success

    def delete_sql_insert(self):
        '''
            Delete the sql insert file.

            ----------

            Return {bool}
            ----------------------
            True upon success, false otherwise.

            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 06-02-2022 09:38:43
            `memberOf`: TableDataManager
            `version`: 1.0
            `method_name`: delete_sql_insert
            * @xxx [06-02-2022 09:39:07]: documentation for delete_sql_insert
        '''


        path = self.insert_path
        if _cfu.exists(path):
            # print(f"deleting insert file: {path}")
            return _cfu.delete(path)
        return True

    def delete_json_data(self):
        '''
            Delete the json data file.

            ----------

            Return {bool}
            ----------------------
            True upon success, false otherwise.

            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 06-02-2022 09:38:43
            `memberOf`: TableDataManager
            `version`: 1.0
            `method_name`: delete_json_data
            * @xxx [06-02-2022 09:39:07]: documentation for delete_json_data
        '''
        path = self.data_path
        if _cfu.exists(path):
            return _cfu.delete(self.data_path)
        return True

    def setting(self,key,default=None):
        return _obj.get_arg(self.settings,key,default)

    @property
    def insert_data(self):
        '''
            Retrieves the insert data for this table depending on the insert_type

            ----------

            Return {type}
            ----------------------
            return_description

            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 06-02-2022 08:41:06
            `memberOf`: TableDataManager
            `version`: 1.0
            `method_name`: insert_data
            * @TODO []: documentation for insert_data
        '''
        if self.name not in self.db.insert_data[self.insert_type]:
            self.db.insert_data[self.insert_type][self.name] = []
        return self.db.insert_data[self.insert_type][self.name]

    def set_insert_data(self,data,save_all=False,**kwargs):
        '''
            Set the insert data for the table.

            ----------

            Arguments
            -------------------------
            `data` {list|dict|None}
                The insert data.

                `!!! CAUTION !!!`\n
                If data is None, the insert data is reset to an empty list.

                If a list of dictionaries is provided, the dictionaries are appended as rows to the insert data.

                If a dictionary is provided, the data is appended as a new row to the insert data.

            Return {bool}
            ----------------------
            True upon success, false otherwise.

            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 06-02-2022 09:44:54
            `memberOf`: TableDataManager
            `version`: 1.0
            `method_name`: insert_data
            * @xxx [06-02-2022 09:45:42]: documentation for insert_data
        '''
        overwrite = _obj.get_kwarg(['overwrite'],False,bool,**kwargs)

        if overwrite is True:
            self.db.insert_data[self.insert_type][self.name] = []
            # self.save(True)
        # @Mstep [IF] if data is None
        if data is None:
            # @Mstep [] set the insert data to an empty list.
            self.db.insert_data[self.insert_type][self.name] = []
            self.save(True)
            # @Mstep [RETURN] return True
            return True

        data = _lu.force_list(data)
        primary_col_name = self.primary
        # print(f"self.table_meta_data:{self.table_meta_data}")
        # print(f"pri: {pri}")


        rows = []
        # @Mstep [LOOP] iterate the rows in the data provided.
        for row in data:
            # print(f"row: {row}")
            # @Mstep [LOOP] iterate the columns of the table.
            for col_name in self.table.column_names:
                # @Mstep [IF] if the column is the primary key.
                if col_name == primary_col_name:
                    # @Mstep [IF] if the row's value is None.
                    if row[col_name] is None:
                        # @Mstep [] set the value to the next available id.
                        row[col_name] = self.next_id
                        # @Mstep [] continue to the next column
                        continue
                # @Mstep [IF] if the column name is a key in the row dictionary.
                if col_name in row:
                    # TODO []: create a type validation for the row value.
                    continue
                # @Mstep [ELSE] if the column name is not a key in the row dictionary.
                else:
                    # @Mstep [] set the column name as a key on the row dict and its value is None
                    row[col_name] = None

            # @Mstep [IF] if all required columns have a value other than None in the row dictionary
            if has_required_columns(self.table,row,True):
                # @Mstep [] append the row to the rows list.
                rows.append(row)
            # else:
            #     print(f"missing columns: {row}")

        # @Mstep [] if the rows list contains at least one row.
        if len(rows) > 0:
            cur_idata = self.insert_data
            # @Mstep [] append the rows to the tables insert data list.
            cur_idata = cur_idata + rows
            # @Mstep [] update the master insert data dict with the new data.
            if self.insert_type == "default":
                self.table.data['default_insert_data'] = cur_idata
            if self.insert_type == "test":
                self.table.data['test_insert_data'] = cur_idata
            # self.db.insert_data[self.insert_type][self.name] = cur_idata
            self.db.insert_data[self.insert_type][self.name] = cur_idata
            if save_all:
                self.db.save()
            # @Mstep [] save the insert json file and generate the insert SQL.
            return self.save(True)

    @property
    def data_path(self):
        if self.insert_type == "default":
            return _obj.get_arg(self.settings,'insert_json_path',None)
        if self.insert_type == "test":
            return _obj.get_arg(self.settings,'insert_test_data_json_path',None)

    @property
    def insert_path(self):
        if self.insert_type == "default":
            return _obj.get_arg(self.settings,'insert_sql_path',None)
        if self.insert_type == "test":
            return _obj.get_arg(self.settings,'insert_test_data_sql_path',None)

    @property
    def next_id(self):
        '''
            Get the next auto_increment id for this table.

            ----------

            Return {int}
            ----------------------
            The next available integer id for the table.

            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 06-02-2022 09:49:49
            `memberOf`: TableDataManager
            `version`: 1.0
            `method_name`: next_id
            * @xxx [06-02-2022 09:50:50]: documentation for next_id
        '''


        data = self.insert_data
        return len(data) + 1

    @property
    def primary(self):
        return get_primary_column(self)

    @property
    def table_name(self):
        return self.table.table_name

    @property
    def name(self):
        return self.table.name



    @property
    def insert_json(self):
        '''
            Import the insert json file and return the contents.

            ----------

            Return {list}
            ----------------------
            The insert contents which must be a list.
            If it does not exist or the contents are invalid the list is empty.

            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 06-02-2022 09:47:54
            `memberOf`: TableDataManager
            `version`: 1.0
            `method_name`: insert_json
            * @xxx [06-02-2022 09:49:00]: documentation for insert_json
        '''

        data = []
        if _cfu.exists(self.data_path):
            res = _cfu.read.as_json(self.data_path)
            if isinstance(res,(list)):
                data = res
        return data

    @property
    def create_sql_path(self):
        return self.settings['create_sql_path']

    @property
    def insert_sql(self):
        if _cfu.exists(self.create_sql_path):
            return _cfu.readr(self.create_sql_path)
        return None

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

        return self.table.schema

    @property
    def column_names(self):
        cols:list = self.table_meta_data
        names = []
        col_data:dict
        for col_data in cols:
            names.append(col_data['name'])
        return names

    @property
    def table_meta_data(self)->list:
        if isinstance(self.table.data['columns'],(list)):
            if len(self.table.data['columns']) == 0:
                self.table.data['columns'] = None

        if self.table.data['columns'] is None:
            # @Mstep [IF] if the create sql file does not exist, we cannot parse it.
            if self.table.create_sql_exists is False:
                # @Mstep [return] return an empty list.
                return []
            # @Mstep [] read the create file sql
            sql = _cfu.readr(self.create_sql_path)
            # @Mstep [] parse the sql for table data.
            create_file_data:dict = _csu.parse.sql.parse(sql)
            # @Mstep [] if we successfully parse the create file.
            if isinstance(create_file_data,(dict)):
                # @Mstep [] update the table's data with the newly parsed data.
                self.table.data = {**self.table.data,**create_file_data}
                # @Mstep [RETURN] return the columns key of the tables data dict.
                return self.table.data['columns']
            return []
            # self.table.data['columns'] = self.data['create_file_data']['columns']
            # _cfu.write.to_json("col_data.delete.json",col_data)
        else:
            return self.table.data['columns']

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

    alerts = []
    for k,v in row.items():
        if v is None:
            if allow_null(table,k) is False:
                if print_errors:
                    msg = f"{k} is a required column in {table.name}, None was provided."
                    alerts.append(msg)
                    _config.log(msg,"error")
                    # print(f"{k} is a required column in {table.name}, None was provided.")
    if len(alerts) > 0:
        logged = []
        for alert in alerts:
            if alert not in logged:
                count = _lu.count(alerts,alert)
                if count > 1:
                    _log(f"{count} - {alert}","error")
                    logged.append(alert)
        return False
    return True
def insert_single_row(table,data):
    '''
        Insert a new row or rows into the default data json file.

        ----------

        Arguments
        -------------------------
        `data` {dict|list}
            A dictionary or list of dictionaries to insert.
            Keys must correspond to the column in the table, they are case sensitive.
            This does `NOT` type match the columns, so if you fuck it up, its on you.

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


    # self.main.insert_data()
    data = _lu.force_list(data)
    primary_col_name = table.primary
    # print(f"self.table_meta_data:{self.table_meta_data}")
    # print(f"pri: {pri}")


    rows = []
    for row in data:
        # print(f"d: {d}")
        for col_name in table.column_names:
            if col_name in row:
                if col_name == primary_col_name:
                    if row[col_name] is None:
                        row[col_name] = len(table.main.insert_data[table.name]) + 1
                        continue
                row[col_name] = row[col_name]
            else:
                if col_name == primary_col_name:
                    row[col_name] = len(table.main.insert_data[table.name]) + 1
                    continue
                row[col_name] = None

        if has_required_columns(table,row,True):
            rows.append(row)


# TODO []: set defaults per column on a dictionary.
# def set_default_values(table,data):

#     for c in table.data['column_data']:
#         if c['is_primary_key'] is True:
#             return c['name']
#     return None

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

        sql_type = _csu.sql.sql_type_to_python(c['type'])
        if sql_type is not None:
            if str(type(val).__name__) in sql_type:
                new_data[c['name']] = data[c]
            else:
                if "bool" in sql_type:
                    bool_val = _csu.convert.to_bool(val)
                    new_data[c['name']] = bool_val
                    continue

# def save_default_insert_json(table,data):
#     _cfu.write.to_json(table.settings['insert_json_path'],data)





