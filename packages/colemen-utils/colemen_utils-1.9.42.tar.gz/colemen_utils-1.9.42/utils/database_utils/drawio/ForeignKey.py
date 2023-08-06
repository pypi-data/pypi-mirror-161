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


from config import log,_db_dio_table,_mxcell_type,_Iterable,_db_dio_parser_type,_db_dio_row_type,_connector_type,_diagram_type,_db_dio_foreign_key_type
import utils.string_utils as _csu
import utils.type_utils as _types
import utils.list_utils as _arr
import utils.database_utils.drawio.entity_utils as _entity_utils
import utils.dict_utils as _obj
import utils.file_utils as _f


# _ROW_SQL_TEMPLATE = """`__COLUMN_NAME__`__INDENT____DATA_TYPE__ __NULL__ __DEFAULT_REP__ __AUTO_INC__ __COMMENT_SQL__"""

class ForeignKey:
    '''
        This class represents a foreign key connection between two tables.

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
        `memberOf`: DrawioRow
        `version`: 1.0
        `method_name`: DrawioRow
        * @TODO []: documentation for DrawioRow
    '''


    def __init__(
        self,
            main:_db_dio_parser_type,
            connector:_connector_type,
            parent_row:_db_dio_row_type,
            child_row:_db_dio_row_type,
            args=None
        ):
        self.args = {} if args is None else args

        self.main = main
        self._node = connector

        self._parent_row:_db_dio_row_type = parent_row
        self._parent_table:_db_dio_table = parent_row.table

        self._child_row:_db_dio_row_type = child_row
        self._child_table:_db_dio_table = child_row.table

        self.settings = {}
        self.data = {
            "parent_row_name":None,
            "parent_table_name":None,

            "child_row_name":None,
            "child_table_name":None,

            "data_type":None,
            "size":None,
            "allow_nulls":None,

            "label":None,
            "on_delete":None,
            "on_update":None,


            "sql":None,
        }
        self.data = _obj.set_defaults(self.args,self.data)
        self.main.register('foreign_key',self)


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
    def parent_table(self):
        '''
            Get this ForeignKey's parent_table


            `default`:None


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-05-2022 12:18:46
            `@memberOf`: ForeignKey
            `@property`: parent_table
        '''
        return self._parent_table

    @property
    def parent_row(self):
        '''
            Get this ForeignKey's parent_row


            `default`:None


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-05-2022 13:21:17
            `@memberOf`: ForeignKey
            `@property`: parent_row
        '''
        return self._parent_row

    @property
    def parent_row_name(self):
        '''
            Get this ForeignKey's parent_row_name


            `default`:None


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-05-2022 13:46:14
            `@memberOf`: ForeignKey
            `@property`: parent_row_name
        '''
        value = _obj.get_arg(self.data,['parent_row_name'],None,(str))
        # @Mstep [IF] if the property is not currenty set
        if value is None:
            value = self.parent_row.name
            self.data['parent_row_name'] = value
        return value

    @property
    def parent_table_name(self):
        '''
            Get this ForeignKey's parent_table_name


            `default`:None


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-05-2022 13:46:36
            `@memberOf`: ForeignKey
            `@property`: parent_table_name
        '''
        value = _obj.get_arg(self.data,['parent_table_name'],None,(str))
        # @Mstep [IF] if the property is not currenty set
        if value is None:
            value = self.parent_table.name
            self.data['parent_table_name'] = value
        return value


    @property
    def child_table(self):
        '''
            Get this ForeignKey's child_table


            `default`:None


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-05-2022 13:20:42
            `@memberOf`: ForeignKey
            `@property`: child_table
        '''
        return self._child_table

    @property
    def child_row(self):
        '''
            Get this ForeignKey's child_row


            `default`:None


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-05-2022 13:21:03
            `@memberOf`: ForeignKey
            `@property`: child_row
        '''
        return self._child_row

    @property
    def child_row_name(self):
        '''
            Get this ForeignKey's child_row_name


            `default`:None


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-05-2022 13:47:04
            `@memberOf`: ForeignKey
            `@property`: child_row_name
        '''
        value = _obj.get_arg(self.data,['child_row_name'],None,(str))
        # @Mstep [IF] if the property is not currenty set
        if value is None:
            value = self.child_row.name
            self.data['child_row_name'] = value
        return value

    @property
    def child_table_name(self):
        '''
            Get this ForeignKey's child_table_name


            `default`:None


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-05-2022 13:47:25
            `@memberOf`: ForeignKey
            `@property`: child_table_name
        '''
        value = _obj.get_arg(self.data,['child_table_name'],None,(str))
        # @Mstep [IF] if the property is not currenty set
        if value is None:
            value = self.child_row.table_name
            self.data['child_table_name'] = value
        return value

    @property
    def label(self):
        '''
            Get this ForeignKey's label


            `default`:None


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-05-2022 14:37:44
            `@memberOf`: ForeignKey
            `@property`: label
        '''
        value = _obj.get_arg(self.data,['label'],None,(str))
        # @Mstep [IF] if the property is not currenty set
        if value is None:
            value = self.node.label
            self.data['label'] = value
        return value

    @property
    def on_delete(self):
        '''
            Get this ForeignKey's on_delete


            `default`:None

            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-05-2022 14:37:26
            `@memberOf`: ForeignKey
            `@property`: on_delete
        '''
        value = _obj.get_arg(self.data,['on_delete'],None,(str))
        # @Mstep [IF] if the property is not currenty set
        if value is None:
            if self.node.has_attribute("on_delete"):
                value = _csu.to_snake_case(self.node.attributes['on_delete'])
            if value not in self.main.valid_fk_options:
                value = None
            self.data['on_delete'] = value
        return value

    @property
    def on_update(self):
        '''
            Get this ForeignKey's on_update


            `default`:None


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-05-2022 15:02:35
            `@memberOf`: ForeignKey
            `@property`: on_update
        '''
        value = _obj.get_arg(self.data,['on_update'],None,(str))
        # @Mstep [IF] if the property is not currenty set
        if value is None:
            if self.node.has_attribute("on_update"):
                value = _csu.to_snake_case(self.node.attributes['on_update'])
            if value not in self.main.valid_fk_options:
                value = None
            self.data['on_update'] = value
        return value

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
    def data_type(self):
        '''
            Get this DrawioRow's data_type


            `default`:None


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-04-2022 14:36:37
            `@memberOf`: DrawioRow
            `@property`: data_type
        '''
        value = _obj.get_arg(self.data,['data_type'],None,(str))
        # @Mstep [IF] if the property is not currenty set
        if value is None:
            # TODO []: add validation to confirm column type is valid
            # TODO []: add custom types [unix_timestamp]
            value = self.parent_row.data_type
            self.data['data_type'] = value
        return value

    @property
    def sql(self):
        '''
            Get this DrawioRow's sql


            `default`:None


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-04-2022 14:33:31
            `@memberOf`: DrawioRow
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
            
            value = _gen_sql(self)
            print(f"    value:{value}")
            self.data['sql'] = value
        return value

    @property
    def size(self):
        '''
            Get this DrawioRow's size


            `default`:None


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-04-2022 14:30:35
            `@memberOf`: DrawioRow
            `@property`: size
        '''
        value = _obj.get_arg(self.data,['size'],None,(int))
        # @Mstep [IF] if the property is not currenty set
        if value is None:
            # TODO []: parse table size
            value = self.parent_row.size
            self.data['size'] = value
        return value

    @property
    def allow_nulls(self):
        '''
            Get this DrawioRow's allow_nulls


            `default`:None


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-04-2022 14:02:54
            `@memberOf`: DrawioRow
            `@property`: allow_nulls
        '''
        value = _obj.get_arg(self.data,['allow_nulls'],None,(bool))
        # @Mstep [IF] if the property is not currenty set
        if value is None:
            value = self.parent_row.allow_nulls
            self.data['allow_nulls'] = value
        return value








def generate_foreign_keys(table:_db_dio_table)->_Iterable[_db_dio_foreign_key_type]:
    output = []
    diagrams = table.main.drawing.diagrams
    dia:_diagram_type
    for dia in diagrams:
        target_row:_db_dio_row_type
        for target_row in table.rows:
            target_id = target_row.node_id

            # @Mstep [] get all connectors that point TOWARDS this row.
            connectors = dia.get_connectors(target_id)
            if len(connectors) == 0:
                continue
            # print(f"searching for connectors with target: {target_row.node_id} to row {target_row.name}")
            # print(f"    connectors: {connectors}")
            # print(f"    {len(connectors)} Connectors found.")

            con:_connector_type
            for con in connectors:

                source_row = table.main.get_row_by_id(con.source)
                if source_row is None:
                    log(f"Failed to locate source row with id: {con.source}","error")
                    continue
                source_row:_db_dio_row_type
                data = {
                    "parent_row_name":source_row.name,
                    "parent_table_name":source_row.table_name,

                    "child_row_name":target_row.name,
                    "child_table_name":target_row.table_name,
                }
                output.append(ForeignKey(table.main,con,source_row,target_row,data))
                print("")
    return output

def _gen_sql(fk:ForeignKey):
    # KEY `FK_Breeds_ParentBreedID` (`parent_breed_id`),
    # CONSTRAINT `FK_Breed_ParentBreed` FOREIGN KEY `FK_Breeds_ParentBreedID` (`parent_breed_id`) REFERENCES `idealech_Equari_Management_Database`.`breeds` (`breed_id`) ON DELETE CASCADE ON UPDATE CASCADE,

    # KEY `fkIdx_910` (`profile_image_id`),
    # CONSTRAINT `FK_users_files_profileImageID_KyOEqngrNiZd` FOREIGN KEY `fkIdx_910` (`profile_image_id`)
    # REFERENCES `idealech_Equari_Content_Database`.`files` (`file_id`) ON DELETE SET NULL ON UPDATE CASCADE

    qc = fk.parent_table.main.sql_quote_char
    
    key = f"FK_{_csu.rand()}"
    child_row_name = fk.child_row_name

    parent_table = fk.parent_table_name
    parent_row_name = fk.parent_row_name

    constraint_name = f"FK_{_csu.rand()}"
    schema = ""
    if isinstance(fk.parent_table.schema,(str)) and len(fk.parent_table.schema) > 0:
        schema = f"{qc}{fk.parent_table.schema}{qc}."
    # print(f"generating foreign key constraint sql")

    on_delete = ""
    if isinstance(fk.on_delete,(str)) and len(fk.on_delete) > 0:
        on_delete = F" ON DELETE {_csu.to_pascal_case(fk.on_delete)}"

    on_update = ""
    if isinstance(fk.on_update,(str)) and len(fk.on_update) > 0:
        on_update = F" ON UPDATE {_csu.to_pascal_case(fk.on_update)}"


    the_stuff = f"""KEY {qc}{key}{qc} ({qc}{child_row_name}{qc}),\nCONSTRAINT {qc}{constraint_name}{qc} FOREIGN KEY {qc}{key}{qc} ({qc}{child_row_name}{qc}) REFERENCES {schema}{qc}{parent_table}{qc} ({qc}{parent_row_name}{qc}){on_delete}{on_update}"""

    return the_stuff

def _align_parent_child_types(fk:ForeignKey):
    parent_type = fk.parent_row.data_type
    child_type = fk.child_row.data_type
    if parent_type != child_type:
        fk.child_row.data_type = parent_type