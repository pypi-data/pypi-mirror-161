# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=line-too-long
# pylint: disable=invalid-name
# pylint: disable=pointless-statement

'''
    Base Class used by connector,onode and mxcell nodes.

    ----------

    Meta
    ----------
    `author`: Colemen Atwood
    `created`: 06-04-2022 15:45:00
    `memberOf`: drawing
    `name`: nodeBase
'''
import json
from typing import Union as _Union
from lxml import etree as _etree
from utils.drawio.diagram_utils import attrib_to_dict
from config import _drawing_type,_diagram_type
import utils.drawio.diagram_utils as _dia
import utils.dict_utils as _obj


class NodeBase:
    def __init__(self,tree,element=None,diagram:_diagram_type=None):
        self.settings = {}
        self.tree = tree
        self.diagram = diagram
        self.element = element
        self._children = None
        self.data = {
            "node_type":None,
            "attributes":{}
        }


    @property
    def summary(self):
        '''
            Get this Node's summary dictionary.


            `default`:None


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-04-2022 10:30:11
            `@memberOf`: NodeBase
            `@property`: summary
        '''
        return self.data

    @property
    def node_type(self):
        '''
            Get this Node's node_type
            
            [onode,connector,mxcell]


            `default`:None


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-04-2022 10:22:45
            `@memberOf`: NodeBase
            `@property`: node_type
        '''
        return _obj.get_arg(self.data,['node_type'],None,(str))

    @property
    def x(self):
        '''
            Get this Node's x coord


            `default`:0


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-04-2022 10:53:42
            `@memberOf`: NodeBase
            `@property`: x
        '''
        coords = self.coords
        return coords['x']

    @x.setter
    def x(self,value):
        '''
            set this Node's x coord


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-04-2022 10:53:42
            `@memberOf`: NodeBase
            `@property`: x
        '''
        self.set_coords(value,None)

    @property
    def y(self):
        '''
            Get this Node's y coord


            `default`:0


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-04-2022 10:53:42
            `@memberOf`: NodeBase
            `@property`: y
        '''
        coords = self.coords
        return coords['y']

    @y.setter
    def y(self,value):
        '''
            set this Node's y coord


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-04-2022 10:53:42
            `@memberOf`: NodeBase
            `@property`: y
        '''
        self.set_coords(None,value)

    @property
    def width(self):
        '''
            Get this Node's width


            `default`:0


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-04-2022 10:53:42
            `@memberOf`: NodeBase
            `@property`: width
        '''
        coords = self.coords
        return coords['w']

    @width.setter
    def width(self,value):
        '''
            set this Node's width


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-04-2022 10:53:42
            `@memberOf`: NodeBase
            `@property`: width
        '''
        self.set_coords(None,None,value)

    @property
    def height(self):
        '''
            Get this Node's height


            `default`:0


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-04-2022 10:53:42
            `@memberOf`: NodeBase
            `@property`: height
        '''
        coords = self.coords
        return coords['h']

    @height.setter
    def height(self,value):
        '''
            set this Node's height


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-04-2022 10:53:42
            `@memberOf`: NodeBase
            `@property`: height
        '''
        self.set_coords(None,None,None,value)


    @property
    def tlc(self):
        '''
            Get the coordinates for this Node's top left corner


            `default`:none


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-04-2022 10:53:42
            `@memberOf`: NodeBase
            `@property`: tlc
        '''
        coords = self.coords
        return coords['tlc']

    @property
    def trc(self):
        '''
            Get the coordinates for this Node's top right corner


            `default`:none


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-04-2022 10:53:42
            `@memberOf`: NodeBase
            `@property`: trc
        '''
        coords = self.coords
        return coords['trc']

    @property
    def brc(self):
        '''
            Get the coordinates for this Node's bottom right corner


            `default`:none


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-04-2022 10:53:42
            `@memberOf`: NodeBase
            `@property`: brc
        '''
        coords = self.coords
        return coords['brc']

    @property
    def blc(self):
        '''
            Get the coordinates for this Node's bottom left corner


            `default`:none


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-04-2022 10:53:42
            `@memberOf`: NodeBase
            `@property`: blc
        '''
        coords = self.coords
        return coords['blc']


    def set_coords(self,x:_Union[int,str]=None,y:_Union[int,str]=None,w:_Union[int,str]=None,h:_Union[int,str]=None):
        '''
            Set the coordinates for this object node.

            Leave any of them null to keep the current value.

            ----------

            Arguments
            -------------------------
            [`x`=None] {int}
                The new x coordinate of the node
            [`y`=None] {int}
                The new y coordinate of the node
            [`w`=None] {int}
                The new width of the node
            [`h`=None] {int}
                The new height of the node


            Return {None}
            ----------------------
            Does not return anything.

            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 05-27-2022 11:10:55
            `memberOf`: onode
            `version`: 1.0
            `method_name`: set_coords
        '''

        if self.element.tag not in ['object','mxCell']:
            return None

        if self.data['coords']['x'] is None:
            self._coords()

        if x is None:
            x = int(self.data['mxgeometry']['x'])
        if y is None:
            y = int(self.data['mxgeometry']['y'])
        if w is None:
            w = int(self.data['mxgeometry']['width'])
        if h is None:
            h = int(self.data['mxgeometry']['height'])

        self.data['coords']['x'] = x
        self.data['coords']['y'] = y
        self.data['coords']['width'] = w
        self.data['coords']['height'] = h

        # if self.element.tag == "object":
        #     self.data['mxcell']['mxgeometry']['x'] = self.data['coords']['x']
        #     self.data['mxcell']['mxgeometry']['y'] = self.data['coords']['y']
        #     self.data['mxcell']['mxgeometry']['width'] = self.data['coords']['width']
        #     self.data['mxcell']['mxgeometry']['height'] = self.data['coords']['height']
        #     mxCell = self.element.xpath('mxCell')
        #     mxGeo = mxCell[0].xpath('mxGeometry')
        #     for k,v in self.data['mxcell']['mxgeometry'].items():
        #         mxGeo[0].attrib[k] = str(v)

        # if self.element.tag == "mxCell":
        
        
        self.data['mxgeometry']['x'] = str(self.data['coords']['x'])
        self.data['mxgeometry']['y'] = str(self.data['coords']['y'])
        self.data['mxgeometry']['width'] = str(self.data['coords']['width'])
        self.data['mxgeometry']['height'] = str(self.data['coords']['height'])
        
        if self.node_type == "onode":
            mxCell = self.element.xpath('mxCell')
            if len(mxCell) > 0:
                mxGeo = mxCell[0].xpath('mxGeometry')
                for k,v in self.data['mxgeometry'].items():
                    mxGeo[0].attrib[k] = str(v)
        if self.node_type == "mxcell":
            mxGeo = self.element.xpath('mxGeometry')
            for k,v in self.data['mxgeometry'].items():
                mxGeo[0].attrib[k] = str(v)


    @property
    def coords(self):
        '''
            Get this NodeBase's coords


            `default`:None


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-04-2022 10:57:10
            `@memberOf`: NodeBase
            `@property`: coords
        '''
        return self._coords()


    def _coords(self):
        '''
            Get this object nodes coordinates.

            {
                "x":int,
                "y":int,
                "w":int,
                "h":int,
                "tlc":{"x":int,"y":int},
                "trc":{"x":int,"y":int},
                "brc":{"x":int,"y":int},
                "blc":{"x":int,"y":int},
            }

            ----------


            Return {dict}
            ----------------------
            The coordinate dictionary for this node.

            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 05-27-2022 11:07:51
            `memberOf`: onode
            `version`: 1.0
            `method_name`: coords
        '''

        if self.element.tag not in ['object','mxCell']:
            return None

        # if self.data['node_type'] == "onode":
        #     x = int(self.data['mxcell']['mxgeometry']['x'])
        #     y = int(self.data['mxcell']['mxgeometry']['y'])
        #     width = int(self.data['mxcell']['mxgeometry']['width'])
        #     height = int(self.data['mxcell']['mxgeometry']['height'])
        print(self.data['mxgeometry'])
        # if self.data['node_type'] == "mxcell":
        x = int(self.data['mxgeometry']['x'])
        y = int(self.data['mxgeometry']['y'])
        width = int(self.data['mxgeometry']['width'])
        height = int(self.data['mxgeometry']['height'])


        self.data['coords']['x'] = x
        self.data['coords']['y'] = y
        self.data['coords']['w'] = width
        self.data['coords']['h'] = height
        self.data['coords']['tlc'] = {"x":x,"y":y}
        self.data['coords']['trc'] = {"x":x + width,"y":y}
        self.data['coords']['brc'] = {"x":x + width,"y":y + height}
        self.data['coords']['blc'] = {"x":x,"y":y + height}

        return self.data['coords']

    def to_element(self,to_string=False):
        xml = self.xml
        if to_string:
            return xml
        return xml

    @property
    def attributes(self):
        '''
            Get this Node's attributes


            `default`:None


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-04-2022 10:12:45
            `@memberOf`: NodeBase
            `@property`: attributes
        '''
        value = _obj.get_arg(self.data,['attributes'],None,(dict))
        # @Mstep [IF] if the property is not currenty set
        if value is None:
            if self.element is not None:
                value = attrib_to_dict(self.element.attrib)
                self.data['attributes'] = value
        return value

    @property
    def xml(self):
        '''
            Get this Node's xml


            `default`:None


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-04-2022 10:10:11
            `@memberOf`: NodeBase
            `@property`: xml
        '''
        value = _obj.get_arg(self.data,['xml'],None,(str))
        # @Mstep [IF] if the property is not currenty set
        if value is None:
            value = self._xml()
            self.data['xml'] = value
        return value

    def _xml(self):
        root_obj = _etree.Element("object")
        for k,v in self.data['attributes'].items():
            if k == "tags":
                root_obj.attrib[k] = ",".join(v)
            else:
                root_obj.attrib[k] = v


        mxcell = _etree.SubElement(root_obj, 'mxCell')
        for k,v in self.data['mxcell']['attributes'].items():
            if k == 'style':
                mxcell.attrib[k] = style_to_string(v)
            else:
                mxcell.attrib[k] = v

        mxgeo = _etree.SubElement(mxcell, 'mxGeometry')
        for k,v in self.data['mxcell']['mxgeometry'].items():
            mxgeo.attrib[k] = v


        # print(_etree.tostring(root_obj))
        self.data['lxml'] = root_obj
        self.data['xml'] = _etree.tostring(root_obj)
        return self.data['xml']

    def set_attribute(self,attribute,value=None):
        '''
            Set an attribute on the node.

            ----------

            Arguments
            -------------------------
            `attribute` {str|dict}
                The name of the attribute to set
                If a dictionary is given, it will add all keys and values as attributes.

            [`value`=None] {str|int}
                The value of the attribute.

            Return {None}
            ----------------------
            Does not return anything.

            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 05-27-2022 11:24:16
            `memberOf`: nodeBase
            `version`: 1.0
            `method_name`: set_attribute
        '''

        if isinstance(attribute,(dict)):
            for k,v in attribute.items():
                self.data['attributes'][k] = v
                self.element.attrib[k] = self.data['attributes'][k]

        if isinstance(attribute,(str)):
            self.data['attributes'][attribute] = value
            self.element.attrib[attribute] = self.data['attributes'][attribute]

    def remove_attribute(self,attribute=None):
        '''
            Remove an attribute from the node.

            ----------

            Arguments
            -------------------------
            `attribute` {str|list|None}
                An attribute or list of attributes to remove from the node.
                if attribute is None, all attributes will be removed.
                Be cautious clearing all attributes, it could break the node in draw.io.

            Return {None}
            ----------------------
            returns nothing.

            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 05-27-2022 11:32:05
            `memberOf`: nodeBase
            `version`: 1.0
            `method_name`: remove_attribute
        '''


        if attribute is None:
            self.data['attributes'] = {}
            self.element.attrib.clear()

        if isinstance(attribute,(list)):
            new_attrib = {}
            for rk in attribute:
                for k,v in self.data['attributes'].items():
                    if rk == k:
                        del self.element.attrib[k]
                    if rk != k:
                        new_attrib[k] = v
            self.data['attributes'] = new_attrib


        if isinstance(attribute,(str)):
            del self.element.attrib[attribute]
            del self.data['attributes'][attribute]

    def has_attribute(self,attribute,value=None):
        '''
            Check if this node contains an attribute.

            ----------

            Arguments
            -------------------------
            `attribute` {str}
                The attribute to search for.

            [`value`=None] {str}
                The optional value to match.

            Return {bool}
            ----------------------
            True upon success, false otherwise.
            If the value is provided, the value must match to be True.

            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 05-27-2022 11:36:48
            `memberOf`: nodeBase
            `version`: 1.0
            `method_name`: has_attribute
        '''


        if attribute in self.data['attributes']:
            if value is not None:
                if self.data['attributes'][attribute] == value:
                    return True
            else:
                return True
        return False

    def set_dict_style(self,styles):
        for k,v in styles.items():
            self.set_style(k,v)

    def set_bgcolor(self,color:str):
        self.set_style("fillColor",color)

    def set_fontcolor(self,color:str):
        self.set_style("fontColor",color)

    def set_fontsize(self,fontSize:int):
        self.set_style("fontSize",str(fontSize))

    def set_bordercolor(self,color:str):
        self.set_style("strokeColor",color)

    def set_shape(self,shape:str):
        self.set_style("hexagon",shape)

    def set_perimeter(self,perimeter:str):
        self.set_style("perimeter",perimeter)

    def set_borderwidth(self,width:int):
        self.set_style("strokeWidth",str(width))

    def set_style(self,key,value=None):
        '''
            Set style attributes on the node.

            if the value is None and the key is a string, the style attribute will be removed from the node.
            This applies to dictionaries as well.

            ----------

            Arguments
            -------------------------
            `key` {str|dict}
                The attribute key or a dictionary of styles to set.
            [`value`=None] {str}
                The value of the style.

            Return {None}
            ----------------------
            returns nothing.

            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 05-27-2022 11:42:35
            `memberOf`: nodeBase
            `version`: 1.0
            `method_name`: set_style
        '''


        if isinstance(key,(dict)):
            for k,v in key.items():
                self.set_style(k,v)
        else:
            if isinstance(key,(str)) and value is None:
                self.remove_style(key)
            else:
                style = self.style_dict
                style[key] = value
                
                self.style_dict = style
                self.update_style()
                # mxCell = self.element.xpath('mxCell')
                # mxCell[0].attrib['style'] = style_to_string(style)

    def remove_style(self,key):
        '''
            Remove a style attribute from the node.

            ----------

            Arguments
            -------------------------
            `key` {str|list}
                A style attribute or list of styles to remove from the node.

            Return {None}
            ----------------------
            returns nothing

            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 05-27-2022 11:45:51
            `memberOf`: nodeBase
            `version`: 1.0
            `method_name`: remove_style
        '''

        if isinstance(key,(list)):
            for k in key:
                if isinstance(k,(str)) and len(k) > 0:
                    self.remove_style(k)
        if isinstance(key,(str)):
            new = {}
            for k,v in self.data['mxcell']['style'].items():
                if k != key:
                    new[k] = v

            self.data['mxcell']['style'] = new
            mxCell = self.element.xpath('mxCell')
            mxCell[0].attrib['style'] = style_to_string(self.data['mxcell']['style'])


    @property
    def style_dict(self):
        '''
            Get this NodeBase's style_dict


            `default`:None


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-06-2022 12:39:18
            `@memberOf`: NodeBase
            `@property`: style_dict
        '''
        style = {}
        if self.node_type == "mxcell":
            if 'style' in self.data['attributes']:
                style = self.data['attributes']['style']
        if self.node_type == "onode":
            style = self.data['mxcell']['attributes']['style']

        return style
    @style_dict.setter
    def style_dict(self,value:dict):
        '''
            set this NodeBase's style_dict


            `default`:None


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-06-2022 12:39:18
            `@memberOf`: NodeBase
            `@property`: style_dict
        '''
        if self.node_type == "mxcell":
            self.data['attributes']['style'] = value
        if self.node_type == "onode":
            self.data['mxcell']['attributes']['style'] = value

    @property
    def style_string(self):
        '''
            Get this NodeBase's style_string


            `default`:None


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-06-2022 12:43:47
            `@memberOf`: NodeBase
            `@property`: style_string
        '''
        value = ""
        if self.node_type == "mxcell":
            if 'style' in self.data['attributes']:
                value = style_to_string(self.style_dict)
                self.element.attrib['style'] = value

        if self.node_type == "onode":
                value = style_to_string(self.style_dict)
                mxCell = self.element.xpath('mxCell')
                mxCell[0].attrib['style'] = value
        return value

    @style_string.setter
    def style_string(self,value):
        '''
            set this NodeBase's style_string


            `default`:None


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-06-2022 12:43:47
            `@memberOf`: NodeBase
            `@property`: style_string
        '''
        if isinstance(value,(str)):
            self.style_dict = _dia.style_to_dict(value)

        value = ""
        if self.node_type == "mxcell":
            if 'style' in self.data['attributes']:
                value = style_to_string(self.style_dict)
                self.element.attrib['style']

        if self.node_type == "onode":
                value = style_to_string(self.style_dict)
                mxCell = self.element.xpath('mxCell')
                mxCell[0].attrib['style']
        return value

    def update_style(self):
        return self.style_string
    # @property
    # def children(self):
    #     '''
    #         Get this NodeBase's children


    #         `default`:None


    #         Meta
    #         ----------
    #         `@author`: Colemen Atwood
    #         `@created`: 07-04-2022 12:23:12
    #         `@memberOf`: NodeBase
    #         `@property`: children
    #     '''
    #     self._children = self.diagram.get_nodes_by_parent(self.node_id)
    #     return self._children

    @property
    def node_id(self):
        '''
            Get this Node's id


            `default`:None


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-04-2022 11:32:01
            `@memberOf`: NodeBase
            `@property`: node_id
        '''
        node_id = self.get_id()
        return node_id
    
    @property
    def parent_id(self):
        '''
            Get this NodeBase's parent_id


            `default`:None


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-04-2022 11:33:02
            `@memberOf`: NodeBase
            `@property`: parent_id
        '''
        # print(json.dumps(self.data['attributes'],indent=4))
        if 'parent' in self.data['attributes']:
            return self.data['attributes']['parent']
        return None


    def get_id(self,test_value=None,default_val=''):
        '''
            Get the id attribute of the node.

            ----------

            Arguments
            -------------------------
            [`test_value`=None] {str}
                If provided, the id value must match this in order to return positively.

            [`default_val`=''] {any}
                The value to return of the id does not exist or does not match the test_value.


            Return {any}
            ----------------------
            If no test_value is provided the id value is returned.
            If a test_value is provided and the id value matches, the id is returned.

            If the id attribute does not exist or does not match the test_value,
            the default_val is returned.

            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 05-27-2022 11:55:25
            `memberOf`: nodeBase
            `version`: 1.0
            `method_name`: id
        '''

        if 'id' in self.data['attributes']:
            if test_value is not None:
                if self.data['attributes']['id'] == test_value:
                    return self.data['attributes']['id']
            else:
                return self.data['attributes']['id']
        return default_val

    def set_id(self, value):
        '''
            Set the id attribute on the node.

            ----------

            Arguments
            -------------------------
            `value` {str}
                Set the id attribute of the node.

            Return {None}
            ----------------------
            returns nothing.

            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 05-27-2022 11:58:55
            `memberOf`: nodeBase
            `version`: 1.0
            `method_name`: id
        '''

        self.data['attributes']['id'] = value
        self.element.attrib['id'] = value



    @property
    def label(self):
        '''
            Get this Node's label


            `default`:None


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-04-2022 11:34:33
            `@memberOf`: NodeBase
            `@property`: label
        '''
        return self.get_label()

    def get_label(self,test_value=None,default_val=''):
        '''
            Get the label attribute of the node.

            ----------

            Arguments
            -------------------------
            [`test_value`=None] {str}
                If provided, the label value must match this in order to return positively.

            [`default_val`=''] {any}
                The value to return of the label does not exist or does not match the test_value.


            Return {any}
            ----------------------
            If no test_value is provided the label value is returned.
            If a test_value is provided and the label value matches, the label is returned.

            If the label attribute does not exist or does not match the test_value,
            the default_val is returned.

            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 05-27-2022 11:55:25
            `memberOf`: nodeBase
            `version`: 1.0
            `method_label`: get_label
        '''
        label = None
        if 'label' in self.data['attributes']:
            label = self.data['attributes']['label']
        if 'value' in self.data['attributes']:
            label = self.data['attributes']['value']

        if test_value is not None:
            if label == test_value:
                return label
        else:
            return label
        return default_val

    def set_label(self, value):
        self.data['attributes']['label'] = value
        self.element.attrib['label'] = value



    @property
    def source(self):
        '''
            Get this NodeBase's source


            `default`:None


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-05-2022 12:07:31
            `@memberOf`: NodeBase
            `@property`: source
        '''
        return self.get_source()

    def get_source(self,test_value=None,default_val=''):
        '''
            Get the source attribute of the node.

            ----------

            Arguments
            -------------------------
            [`test_value`=None] {str}
                If provided, the source value must match this in order to return positively.

            [`default_val`=''] {any}
                The value to return of the source does not exist or does not match the test_value.


            Return {any}
            ----------------------
            If no test_value is provided the source value is returned.
            If a test_value is provided and the source value matches, the source is returned.

            If the source attribute does not exist or does not match the test_value,
            the default_val is returned.

            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 05-27-2022 11:55:25
            `memberOf`: nodeBase
            `version`: 1.0
            `method_name`: source
        '''
        base_attrib = self.data['attributes']
        if self.node_type == "onode":
            base_attrib = self.data['mxcell']['attributes']
        
        if 'source' in base_attrib:
            if test_value is not None:
                if base_attrib['source'] == test_value:
                    return base_attrib['source']
            else:
                return base_attrib['source']
        return default_val

    def set_source(self, value):
        '''
            Set the source attribute on the node.

            ----------

            Arguments
            -------------------------
            `value` {str}
                Set the source attribute of the node.

            Return {None}
            ----------------------
            returns nothing.

            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 05-27-2022 11:58:55
            `memberOf`: nodeBase
            `version`: 1.0
            `method_name`: source
        '''

        self.data['attributes']['source'] = value
        self.element.attrib['source'] = value


    @property
    def target(self):
        '''
            Get this NodeBase's target


            `default`:None


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-05-2022 12:06:42
            `@memberOf`: NodeBase
            `@property`: target
        '''
        return self.get_target()

    def get_target(self,test_value=None,default_val=''):
        '''
            Get the target attribute of the node.

            ----------

            Arguments
            -------------------------
            [`test_value`=None] {str}
                If provided, the target value must match this in order to return positively.

            [`default_val`=''] {any}
                The value to return of the target does not exist or does not match the test_value.


            Return {any}
            ----------------------
            If no test_value is provided the target value is returned.
            If a test_value is provided and the target value matches, the target is returned.

            If the target attribute does not exist or does not match the test_value,
            the default_val is returned.

            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 05-27-2022 11:55:25
            `memberOf`: nodeBase
            `version`: 1.0
            `method_name`: target
        '''
        base_attrib = self.data['attributes']
        if self.node_type == "onode":
            base_attrib = self.data['mxcell']['attributes']


        if 'target' in base_attrib:
            if test_value is not None:
                if base_attrib['target'] == test_value:
                    return base_attrib['target']
            else:
                return base_attrib['target']
        return default_val

    def set_target(self, value):
        '''
            Set the target attribute on the node.

            ----------

            Arguments
            -------------------------
            `value` {str}
                Set the target attribute of the node.

            Return {None}
            ----------------------
            returns nothing.

            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 05-27-2022 11:58:55
            `memberOf`: nodeBase
            `version`: 1.0
            `method_name`: target
        '''

        self.data['attributes']['target'] = value
        self.element.attrib['target'] = value


def style_to_dict(style):
    data = {}
    if isinstance(style,(str)):
        styleList = style.split(";")
        for x in styleList:
            s = x.split("=")
            if len(s) > 1:
                # print(f"s: {s}")
                data[s[0]] = s[1]
    return data

def style_to_string(style):
    tmp = []
    if isinstance(style,(dict)):
        for k,v in style.items():
            tmp.append(f"{k}={v}")
    return ';'.join(tmp)

# def attrib_to_dict(attrib):
#     data = {}
#     for k,v in attrib.items():
#         data[k] = v
#     return data


