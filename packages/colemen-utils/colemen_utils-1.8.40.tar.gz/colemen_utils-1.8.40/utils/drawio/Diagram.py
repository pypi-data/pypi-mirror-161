# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=line-too-long
# pylint: disable=c-extension-no-member
'''
    Methods for managing drawio diagrams.

    ----------

    Meta
    ----------
    `author`: Colemen Atwood
    `created`: 06-04-2022 15:45:00
    `memberOf`: drawio
    `name`: diagram
'''

# from typing import Iterable
from lxml import etree as _etree

# import config as _config
from config import _connector_type,_onode_type,_mxcell_type,_Iterable,_Union



import utils.string_utils as _csu
import utils.drawio.diagram_utils as _dia
import utils.dict_utils as _obj

import utils.drawio.Mxcell as _mxcell_module
import utils.drawio.Onode as _onode_module
import utils.drawio.Connector as connector_module
import utils.drawio.Drawing as _Drawing



_new_mxcell = _mxcell_module.new_mxcell
_Mxcell = _mxcell_module.Mxcell

_Onode = _onode_module.Onode
_new_onode = _onode_module.new_onode

_Connector = connector_module.Connector
_new_connector = connector_module.new_connector


# _onode_type = TypeVar('_onode_type', bound=_Onode)
# _connector_type = TypeVar('_connector_type', bound=_Connector)
# _mxcell_type = TypeVar('_mxcell_type', bound=_Mxcell)
# element_type = TypeVar('element_type', bound=_etree.Element)

_DEFAULT_TABLE_STYLE = {
    "shape":"table",
    "startSize":40,
    "container":1,
    "collapsible":1,
    "childLayout":"tableLayout",
    "fixedRows":1,
    "rowLines":0,
    "fontStyle":1,
    "align":"center",
    "resizeLast":1,
    "swimlaneFillColor":"#333333",
    "fillColor":"#fa6800",
    "strokeColor":"#C73500",
    "fontColor":"#000000",
}
_DEFAULT_HEADER_STYLE = {
    "shape":"partialRectangle",
    "collapsible":0,
    "dropTarget":0,
    "pointerEvents":0,
    "fillColor":"none",
    "top":0,
    "left":0,
    "bottom":1,
    "right":0,
    "points":[[0,0.5],[1,0.5]],
    "portConstraint":"eastwest",
    "fontColor":"#CC6600",
    "spacingLeft":0,
}

_DEFAULT_HEADER_COLUMN_STYLE = {
    "shape":"partialRectangle",
    "connectable":0,
    "fillColor":"none",
    "top":0,
    "left":0,
    "bottom":0,
    "right":0,
    "fontStyle":0,
    "overflow":"hidden",
    "fontColor":"#CC6600",
    "spacingLeft":0,
    "fontSize":8,

}



class Diagram:
    '''
        Manages a drawio diagram.
        The diagrams contains the nodes and appear as tabs in the drawing.

        ----------

        Arguments
        -------------------------
        `tree` {etree}
            The drawing xml tree.
        `element` {element}
            The etree element that will be added to the drawing.
            The new_diagram method generates this automatically.

        Meta
        ----------
        `author`: Colemen Atwood
        `created`: 06-04-2022 16:47:17
        `memberOf`: diagram
        `version`: 1.0
        `method_name`: Diagram
        * @xxx [06-04-2022 16:49:56]: documentation for Diagram
    '''


    def __init__(self,tree:_etree,element=None):
        self.settings = {}
        self.tree = tree
        self.element = element
        self.dia_root = None
        self.data = {
            "attributes":{},
            "connectors":[],
            "mxcells":[],
            "onodes":[],
            "children":[],
        }

        self._from_element()
        # self.set_defaults()

    def _from_element(self):
        element = self.element
        if element is not None:
            root_list:_Iterable = _dia.get_diagram_root_node(element)
            if len(root_list) > 0:
                dia_root = root_list[0]
                self.dia_root = dia_root
            self.data['attributes'] = _dia.attrib_to_dict(element.attrib)
            # self.data['connectors'] = _dia.get_connectors(element)
            children = _dia.get_children(self.dia_root)
            # print(f"children: {children}")
            for c in children:
                if c.tag == "mxCell":
                    if 'source' in c.attrib:
                        con = _Connector(self.tree,c,self)
                        self.data['connectors'].append(con)
                        # self.data['connectors']
                        # print(f"connector Found: {c}")
                    else:
                        self.data['mxcells'].append(_Mxcell(self.tree,c,self))
                        # print(f"mxcell found: {c}")

                if c.tag == "object":
                    O = _Onode(self.tree,c,self)

                    if 'source' in O.mxcell_attributes:
                        self.data['connectors'].append(O)

                    self.data['onodes'].append(O)
                    # print(f"object found: {c}")
                # self.data['children']['id'] = c.attrib['id']

            return self.data

    def show_grid(self,value:bool):
        if value is True:
            self.element.attrib['grid'] = "1"
        if value is False:
            self.element.attrib['grid'] = "0"

    def grid_size(self,value:int):
        if value < 1:
            value = 10
        self.element.attrib['gridSize'] = str(value)

    def list_node_labels(self):
        '''
            Print the labels of every node in this diagram.

            ----------


            Return {None}
            ----------------------
            returns nothing.

            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 05-27-2022 12:45:59
            `memberOf`: diagram
            `version`: 1.0
            `method_name`: list_node_labels
        '''
        x:_Onode
        for x in self.data['onodes']:
            label = x.get_label(None)
            if label is not None:
                print(label)

        x:_Mxcell
        for x in self.data['mxcells']:
            label = x.get_label(None)
            if label is not None:
                print(label)

        x:_Connector
        for x in self.data['connectors']:
            label = x.get_label(None)
            if label is not None:
                print(label)

    def add_mxcell(self,**kwargs)->_mxcell_type:
    # def add_mxcell(self,node_id=None,parent=None,x=None,y=None,width=None,height=None,geo_as=None)->_mxcell_type:
        cell = _new_mxcell(self.tree,self,**kwargs)
        self.data['mxcells'].append(cell)
        return cell

    def add_onode(self,node_id=None)->_onode_type:
        cell = _new_onode(self.tree,self,node_id)
        self.data['onodes'].append(cell)
        return cell

    def add_connector(self,source,target)->_connector_type:
        cell = _new_connector(self.tree,self,source,target)
        self.data['connectors'].append(cell)
        return cell
    
    def add_table(self,**kwargs):
        return _gen_table(self,**kwargs)

    def get_nodes_by_tag(self,tag)->_Iterable[_Onode]:
        '''
            Get all nodes that contain the tag provided.

            ----------

            Arguments
            -------------------------
            `tag` {str|list}
                The tag or list of tags to search for.


            Return {list}
            ----------------------
            A list of onodes that contain the tag.
            Only object nodes support the tags attribute, so this will not include mxcells or connectors.

            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 05-27-2022 13:36:21
            `memberOf`: diagram
            `version`: 1.0
            `method_name`: get_nodes_by_tag
        '''

        nodes = []
        c:_Onode
        for c in self.data['onodes']:
            if c.has_tag(tag):
                nodes.append(c)
        return nodes


    def get_nodes_by_parent(self,parent_id:str)->_Iterable[_Union[_Onode,_mxcell_type,_connector_type]]:
        '''
            Get all nodes that are children of the parent_id provided.

            ----------

            Arguments
            -------------------------
            `tag` {str|list}
                The tag or list of tags to search for.


            Return {list}
            ----------------------
            A list of onodes that contain the tag.
            Only object nodes support the tags attribute, so this will not include mxcells or connectors.

            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 05-27-2022 13:36:21
            `memberOf`: diagram
            `version`: 1.0
            `method_name`: get_nodes_by_tag
        '''

        nodes = []
        c:_Onode
        for c in self.data['onodes']:
            # print(f"search parent_id:{c.parent_id}")
            # print(f"parent_id: {parent_id}")
            if c.parent_id == parent_id:
                # print(f"CHILD FOUND: {c.parent_id} > {c.node_id}")
                nodes.append(c)

        c:_mxcell_type
        for c in self.data['mxcells']:
            if c.parent_id == parent_id:
                # print(f"CHILD FOUND: {c.parent_id} > {c.node_id}")
                nodes.append(c)
        return nodes

    def get_connectors(self,target_id=None,source_id=None):
        '''
            Get connectors from this diagram.

            ----------

            Arguments
            -------------------------
            [`target_id`=None] {str}
                If provided, only connectors with a target attribute matching this
                value will be returned
            [`source_id`=None] {str}
                If provided, only connectors with a source attribute matching this
                value will be returned

            Return {list}
            ----------------------
            A list of connectors matching the criteria provided.
            If no connectors match, the list is empty.
            
            If no target or source is provided, it will return all connectors.

            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 07-05-2022 12:45:05
            `memberOf`: diagram
            `version`: 1.0
            `method_name`: get_connectors
            * @xxx [07-05-2022 12:47:04]: documentation for get_connectors
        '''


        if target_id is None and source_id is None:
            return []
        
        cons = []
        for con in self.connectors:
            if target_id is not None:
                if con.get_target(target_id,False):
                    cons.append(con)
            if source_id is not None:
                if con.get_source(source_id,False):
                    cons.append(con)
        return cons

    def set_name(self,name:str):
        '''
            Set this diagrams name.

            ----------

            Arguments
            -------------------------
            `name` {str}
                The new name to assign.

            Return {None}
            ----------------------
            returns nothing

            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 05-27-2022 13:38:58
            `memberOf`: diagram
            `version`: 1.0
            `method_name`: set_name
        '''

        self.data['attributes']['name'] = name
        self.element.attrib['name'] = name

    def get_name(self,test_value=None,default_val=False):
        '''
            Get the name attribute of the diagram.

            ----------

            Arguments
            -------------------------
            [`test_value`=None] {str}
                If provided, the name value must match this in order to return positively.

            [`default_val`=''] {any}
                The value to return of the name does not exist or does not match the test_value.


            Return {any}
            ----------------------
            If no test_value is provided the name value is returned.
            If a test_value is provided and the name value matches, the name is returned.

            If the name attribute does not exist or does not match the test_value,
            the default_val is returned.

            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 05-27-2022 11:55:25
            `memberOf`: nodeBase
            `version`: 1.0
            `method_name`: get_name
        '''

        if 'name' in self.data['attributes']:
            if test_value is not None:
                if self.data['attributes']['name'] == test_value:
                    return self.data['attributes']['name']
            else:
                return self.data['attributes']['name']
        return default_val


    def has_name(self,name=None):
        if 'name' in self.data['attributes']:
            if name is not None:
                if self.data['attributes']['name'] == name:
                    return True
            return True
        return False


    @property
    def connectors(self)->_Iterable[_Connector]:
        '''
            Get this Diagram's connectors


            `default`:[]


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-05-2022 12:04:14
            `@memberOf`: Diagram
            `@property`: connectors
        '''
        return self.data['connectors']



def _gen_table(diagram:Diagram,**kwargs):
    name = _obj.get_kwarg(['name'],"new_table",(str),**kwargs)
    x_co = _obj.get_kwarg(['x'],0,(int),**kwargs)
    y_co = _obj.get_kwarg(['y'],0,(int),**kwargs)
    headers = _obj.get_kwarg(['headers'],[{"name":"header"}],(list),**kwargs)
    
    
    
    tb_node = diagram.add_onode()
    tb_node.set_style(_DEFAULT_TABLE_STYLE)
    # print(f"name: {name}")
    tb_node.set_label(name)
    tb_node.set_coords(x_co,y_co,880,120)
    
    # y="40" width="870" height="30" as="geometry"
    header_con = diagram.add_mxcell(
        parent=tb_node.get_id(),
        node_id=f"header_row_{_csu.rand()}",
        x=0,
        y=40,
        width=880,
        height=30,
    )
    header_con.set_style(_DEFAULT_HEADER_STYLE)
    # print(header_con.data)
    # header_con.set_coords(0,40,40,40)

    for hdata in headers:
        hdr_id = f"tbl_header_{_csu.rand()}_ignore"
        hdr = diagram.add_onode(hdr_id)
        hdr.parent = header_con.get_id()
        hdr.set_label(hdata['name'])
        hdr.set_style(_DEFAULT_HEADER_COLUMN_STYLE)
        hdr.set_coords(x_co,y_co,hdata["width"],30)


def new_diagram(drawing:_Drawing,name:str)->Diagram:
    '''
        Create a new diagram in the drawing.

        ----------

        Arguments
        -------------------------
        `drawing` {Drawing}
            A reference to the drawing that this diagram will belong to.
        `name` {str}
            The name of the diagram, this is shown on the tabs in draw.io

        Return {Diagram}
        ----------------------
        An instance of the Diagram class

        Meta
        ----------
        `author`: Colemen Atwood
        `created`: 05-27-2022 12:42:40
        `memberOf`: diagram
        `version`: 1.0
        `method_name`: new_diagram
    '''

    diagram = _etree.SubElement(drawing, 'diagram')
    # diagram = _etree.Element("diagram")

    diagram.attrib['id'] = _csu.gen.rand(20)
    diagram.attrib['name'] = name

    mxgm_data = {
        "dx":"1074",
        "dy":"954",
        "grid":"1",
        "gridSize":"10",
        "guides":"1",
        "tooltips":"1",
        "connect":"1",
        "arrows":"1",
        "fold":"1",
        "page":"1",
        "pageScale":"1",
        "pageWidth":"1700",
        "pageHeight":"1100",
        "math":"0",
        "shadow":"0",
    }

    mxGraphModel = _etree.SubElement(diagram, 'mxGraphModel')
    for k,v in mxgm_data.items():
        mxGraphModel.attrib[k] = v

    # @Mstep [] create the root node for the diagram
    root = _etree.SubElement(mxGraphModel, 'root')


    d = Diagram(drawing,diagram)

    # @Mstep [] add the two default nodes to the diagram.
    d.add_mxcell(node_id="0")
    d.add_mxcell(node_id="1",parent="0")

    # @Mstep [RETURN] return the diagram instance.
    return d



