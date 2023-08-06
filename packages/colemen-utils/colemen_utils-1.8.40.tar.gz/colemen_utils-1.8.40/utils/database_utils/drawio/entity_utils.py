# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=line-too-long
# pylint: disable=unused-wildcard-import
# pylint: disable=wildcard-import
# pylint: disable=unused-import
# pylint: disable=import-outside-toplevel
'''
    A library of utility methods used in the utils.database_utils.drawio module.

    ----------

    Meta
    ----------
    `author`: Colemen Atwood
    `created`: 07-05-2022 08:50:55
    `memberOf`: entity_utils
'''

# import time
import re
import json
from datetime import datetime



import config as _config
import utils.type_utils as _types
import utils.string_utils as _csu
import utils.list_utils as _arr
import utils.dict_utils as _obj


# import utils.drawio.diagram_utils as _dia
# import utils.database_utils.DrawioParser as _db_parser
# # import utils.database_utils.DrawioTable as _table
# from config import log as _log,_drawio_table,_onode_type,_diagram_type,_mxcell_type
# import utils.dict_utils as _obj
# import utils.file_utils as _f


def trigger_attributes(entity):
    '''
        Iterate throught the entity's data dictionary to find matching
        attributes on the entity object. If it exists, it will call that attribute.
        
        This essentially causes the data dictionary to be populated with all the data 
        that can be determined at the time.

        ----------

        Arguments
        -------------------------
        `entity` {any}
            The entity to update.


        Return {None}
        ----------------------
        returns nothing.

        Meta
        ----------
        `author`: Colemen Atwood
        `created`: 07-05-2022 09:05:52
        `memberOf`: entity_utils
        `version`: 1.0
        `method_name`: trigger_attributes
        * @xxx [07-05-2022 09:09:41]: documentation for trigger_attributes
    '''


    attribs = []
    edata = entity.data.copy()
    # print(f"edata:{edata}")
    # @Mstep [LOOP] iterate the data dictionary.
    for k,_ in edata.items():
        # @Mstep [] if there is an attribute for the key.
        if hasattr(entity,k):
            attribs.append(k)
    for k in attribs:
        # @Mstep [] call the attribute and set the value in the reps dict.
        _ = getattr(entity,k)

def gen_replacements(replacements):
    '''
        Get this Entity's replacements for updating a template.
        This essentially takes the data dictionary and converts the keys to screaming snake.


        `default`:None


        Meta
        ----------
        `@author`: Colemen Atwood
        `@created`: 07-01-2022 12:43:37
        `@memberOf`: EntityBase
        `@property`: replace
    '''

    
    # if hasattr(self,"add_replacements") and self._additional_replacements is None:
    #     _c.con.log(f"       {self.class_name}.{self.name}.gen_replacements : add_replacements attribute found in {self.name}","pink")
    #     newrep = getattr(self,'add_replacements')
    #     # print(f"========================================\n\n")
    #     # print(newrep)
    #     # print(f"========================================\n\n")
    #     for k,v in newrep.items():
    #         print(f"adding key: {k}")
    #         replacements[k] =v
    #     self._additional_replacements = replacements
        # replacements = {**replacements,**newrep}
        # print(replacements)

    # if self._replacements is not None:
    #     return self._replacements
    if "timestamp" not in replacements:
        replacements['timestamp'] = datetime.now().strftime('%m-%d-%Y %H:%M:%S')
    new_reps = {}
    for k,v in replacements.items():
        if k == "replacements":
            continue
        if v is None:
            v = ""
        # v = str(v)
        # @Mstep [] iterate a single level into sub dictionaries.
        if isinstance(v,(dict)):
            for sk,sv in v.items():
                if _types.is_scalar(sv):
                    new_reps[prep_single_key(sk)] = sv

        if isinstance(v,(int,float)):
            v = str(v)
        if isinstance(v,(str)):
            new_reps[prep_single_key(k)] = v
        # k = f"__{_csu.to_screaming_snake(_csu.strip(k,['_']))}__"
        # replacements[k] = v

    return new_reps

def get_data_attrib(entity,key:str,default_value=None,types=None):
    key = _arr.force_list(key)
    final_value = default_value
    data_key = key[0]
    # value_found = False
    for k in key:
        value = _obj.get_arg(entity.data,k,"__NO_DATA_ATTRIBUTE_FOUND__",(types))
        if value != "__NO_DATA_ATTRIBUTE_FOUND__":
            # value_found = True
            final_value = value
            data_key = k
            break

    entity.data[data_key] = final_value
    return final_value

def prep_single_key(key:str)->str:
    return f"__{_csu.to_screaming_snake(_csu.strip(key,['_']))}__"

def _is_hashable(value):
    try:
        json.dumps(value)
    except TypeError:
        return False
    return True

def strip_class_references(data):
    if _is_hashable(data):
        return data
    new_data = None
    
    if isinstance(data,(list)):
        new_data = []
        for v in data:
            if hasattr(v,"__dict__"):
                # if hasattr(v,"data"):
                    # new_data.append(strip_class_references(getattr(v,"data")))
                continue
            if isinstance(v,(list,dict)):
                new_data.append(strip_class_references(v))
                continue
            
            new_data.append(v)
    
    elif isinstance(data,(dict)):
        for k,v in data.items():
            new_data = {}
            if hasattr(v,"__dict__"):
                continue
            if isinstance(v,(list,dict)):
                new_data[k] = strip_class_references(v)
                continue
            new_data[k] = v
    # else:
    #     return data
    return new_data

def summary(entity,populate_data=True):
    '''
        Get this Entity's summary


        `default`:None


        Meta
        ----------
        `@author`: Colemen Atwood
        `@created`: 07-01-2022 10:59:44
        `@memberOf`: EntityBase
        `@property`: summary
    '''
    if populate_data:
        trigger_attributes(entity)

    # data = entity.data
    sum_data = {
        "data":{},
        "settings":{},
    }
    raw_data = entity.data.copy()
    raw_settings = entity.settings.copy()

    for k,v in raw_data.items():
        if hasattr(v,"__dict__"):
            # _c.con.log(f"class found: {k} - {v}","yellow")
            continue

        if isinstance(v,(list,dict)):
            sum_data['data'][k] = strip_class_references(v)
            continue

        sum_data['data'][k] = v
        
    for k,v in raw_settings.items():
        if hasattr(v,"__dict__"):
            # _c.con.log(f"class found: {k} - {v}","yellow")
            continue

        if isinstance(v,(list,dict)):
            sum_data['settings'][k] = strip_class_references(v)
            continue

        sum_data['settings'][k] = v

    return sum_data


def gen_name_variations(entity,value:str):
    
    if isinstance(value,(str)) is False:
        return None
    p = _config.inflect_engine()
    data = {}
    data['singular_name'] = _csu.singular_noun(value)

    data['pascal_name'] = _trail_id_caps(_csu.to_pascal_case(value))
    data['pascal_singular_name'] = _trail_id_caps(p.singular_noun(data['pascal_name']))
    data['pascal_plural_name'] = _trail_id_caps(p.plural(data['pascal_singular_name']))

    data['camel_name'] = _trail_id_caps(_csu.to_camel_case(value))
    data['camel_singular_name'] = _trail_id_caps(p.singular_noun(data['camel_name']))
    data['camel_plural_name'] = _trail_id_caps(p.plural(data['camel_singular_name']))


    data['snake_name'] = _csu.to_snake_case(value)
    data['snake_singular_name'] = p.singular_noun(data['snake_name'])
    data['snake_plural_name'] = p.plural(data['snake_singular_name'])


    data = {**entity.data,**data}
    entity.data = data



def _trail_id_caps(value):
    return re.sub(r"(id)(s)?$",r"ID\2",value)