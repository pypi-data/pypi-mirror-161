# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=line-too-long
'''
    Methods for managing drawio nodes that are wrapped in an object tag.

    ----------

    Meta
    ----------
    `author`: Colemen Atwood
    `created`: 06-04-2022 15:45:00
    `memberOf`: drawio
    `name`: onode
'''

from lxml import etree as _etree
import utils.string_utils as _csu
import utils.dict_utils as _obj
from config import _diagram_type,_Iterable

from utils.drawio.NodeBase import NodeBase as _NodeBase
import utils.drawio.diagram_utils as _dia
import utils.list_utils as _arr

def new_onode(tree,diagram:_diagram_type,node_id:str=None,**kwargs):
    '''
        Creates a new element for an object node.

        ----------

        Keyword Arguments
        -------------------------
        [`x`=0] {int|str}
            The initial x coordinate of the node
        [`y`=0] {int|str}
            The initial y coordinate of the node
        [`w`=120] {int|str}
            The initial width of the node
        [`h`=60] {int|str}
            The initial height of the node

        Arguments
        -------------------------
        `tree` {object}
            A reference to the lxml tree object.
        `diagram` {object}
            A reference to the Diagram instance this node is added to.
        [`node_id`=None] {string}
            The optional id of the node, if not provided, a random one is generated.

        Return {Onode}
        ----------------------
        An Onode instance.

        Meta
        ----------
        `author`: Colemen Atwood
        `created`: 05-27-2022 11:13:10
        `memberOf`: onode
        `version`: 1.0
        `method_name`: new_onode
    '''

    x = _obj.get_kwarg(['x'],"0",(int,str),**kwargs)
    y = _obj.get_kwarg(['y'],"0",(int,str),**kwargs)
    width = _obj.get_kwarg(['width','w'],"120",(int,str),**kwargs)
    height = _obj.get_kwarg(['height','h'],"60",(int,str),**kwargs)

    onode_element = _etree.SubElement(diagram.dia_root, 'object')
    node_id = _csu.gen.rand() if node_id is None else node_id
    onode_element.attrib['id'] = node_id

    mxcell = _etree.SubElement(onode_element, 'mxCell')
    # mxCell.attrib['style']="shape=hexagon;perimeter=hexagonPerimeter2;whiteSpace=wrap;html=1;fixedSize=1;size=10;fillColor=#76608a;strokeColor=#432D57;fontColor=#ffffff;"
    mxcell.attrib['style']="rounded=0;whiteSpace=wrap;html=1;"
    mxcell.attrib['vertex']="1"
    mxcell.attrib['parent']="1"

    mxgeo = _etree.SubElement(mxcell, 'mxGeometry')
    mxgeo.attrib['x']=str(x)
    mxgeo.attrib['y']=str(y)
    mxgeo.attrib['width']=str(width)
    mxgeo.attrib['height']=str(height)
    mxgeo.attrib['as']="geometry"

    return Onode(tree,onode_element,diagram)

class Onode(_NodeBase):
    def __init__(self,tree,element=None,diagram:_diagram_type=None):
        super().__init__(tree,element,diagram)
        self.settings = {}
        self.tree = tree
        self.element = element
        self.data = {
            "node_type":"onode",
            "lxml":"",
            "xml":"",
            "coords":{
                "x":None,
                "y":None,
                "tlc":[],
                "trc":[],
                "brc":[],
                "blc":[],
            },
            "attributes":{},
            "mxcell":{
                "attributes":{},
                "style":{},
                # "vertex":None,
                # "parent":None,
            },
            "mxgeometry":{
                "x":None,
                "y":None,
                "width":None,
                "height":None,
                "as":None,
            },
            "is_connector":None
        }
        self._from_element()
        # print(self.data)


    def _from_element(self):
        '''
            Parse this node's lxml element attributes and children.

            This method is specific to parsing object nodes.

            ----------

            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 07-04-2022 10:20:43
            `memberOf`: Onode
            `version`: 1.0
            `method_name`: _from_element
            * @TODO []: documentation for _from_element
        '''


        element = self.element
        if element is not None:
            self.data['attributes'] = _dia.attrib_to_dict(element.attrib)
            if 'tags' in self.data['attributes']:
                self.data['attributes']['tags'] = self.data['attributes']['tags'].split(",")

            # @Mstep [] parse the mxcell attributes
            mxcell = element.xpath('mxCell')
            if len(mxcell) > 0:
                self.data['mxcell']['attributes'] = _dia.attrib_to_dict(mxcell[0].attrib)
                # style = _dia.style_to_dict(self.data['mxcell']['attributes']['style'])
                # print(f"style:{style}")

                # @Mstep [] retrieve and parse the mxGeometry attributes.
                mxgeometry = mxcell[0].xpath('mxGeometry')
                self.data['mxgeometry'] = _dia.attrib_to_dict(mxgeometry[0].attrib)

                self.data['mxcell']['attributes']['style'] = _dia.style_to_dict(self.data['mxcell']['attributes']['style'])

                is_connector = self.is_connector
                if is_connector is True:
                    self.data['source'] = self.source
                    self.data['target'] = self.target
            return self.data

    def has_tag(self,value):
        '''
            Check if this object node contains a matching tag in the tags attribute.

            ----------

            Arguments
            -------------------------
            `value` {string|list}
                The tag to search for.

            Return {bool}
            ----------------------
            True upon success, false otherwise.

            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 05-27-2022 10:56:33
            `memberOf`: onode
            `version`: 1.0
            `method_name`: has_tag
            # @xxx [05-27-2022 10:59:21]: documentation for has_tag
        '''

        if isinstance(value,(str)):
            value = [value]
        for v in value:
            if v in self.tags:
                return True
            return False

    def set_tag(self,tag=None):
        '''
            Adds a new tag to the tags attribute of the object node.

            ----------

            Arguments
            -------------------------
            `tag` {string|None}
                The new tag to add.
                if None, all tags will be removed.

            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 05-27-2022 10:59:30
            `memberOf`: onode
            `version`: 1.0
            `method_name`: set_tag
        '''

        if tag is None:
            self.data['attributes']['tags'] = []
            return

        if isinstance(tag,(str)):
            tag = tag.split(",")

        new_tags = _arr.force_list(tag)
        tags = self.tags

        # @Mstep [] filter out empty tags
        for nt in new_tags:
            if len(nt) == 0 or nt == ",":
                continue
            if nt not in tags:
                tags.append(nt)

        # if 'tags' in self.data['attributes']:
        #     if isinstance(self.data['attributes']['tags'],(str)):
        #         self.data['attributes']['tags'] = self.data['attributes']['tags'].split(",")

        # if 'tags' not in self.data['attributes']:
        #     self.data['attributes']['tags'] = []

        # @Mstep [] update the list of tags
        self.data['attributes']['tags'] = tags

        # @Mstep [] update the element with the new tags.
        self.element.attrib['tags'] = ','.join(self.tags)

    def remove_tag(self,tag):
        '''
            Remove a tag from the object node's tags attribute

            ----------

            Arguments
            -------------------------
            `tag` {string}
                The tag to remove.

            Return {bool}
            ----------------------
            return_description

            Meta
            ----------
            `author`: Colemen Atwood
            `created`: 05-27-2022 11:01:49
            `memberOf`: onode
            `version`: 1.0
            `method_name`: remove_tag
        '''

        new_tags = []
        if 'tags' in self.data['attributes']:
            for t in self.data['attributes']['tags']:
                if t != tag:
                    new_tags.append(t)
        self.data['attributes']['tags'] = new_tags
        self.element.attrib['tags'] = ','.join(new_tags)

    @property
    def parent_id(self):
        '''
            Get this Onode's parent_id

            Unlike the other nodes, Object node's parent attribute is stored in
            their child mxcell node.


            `default`:None


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-04-2022 11:37:13
            `@memberOf`: Onode
            `@property`: parent_id
        '''
        return self.data['mxcell']['attributes']['parent']

    @property
    def parent(self):
        '''
            Get this Onode's parent


            `default`:None


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-06-2022 13:53:10
            `@memberOf`: Onode
            `@property`: parent
        '''
        return self.parent_id
    
    @parent.setter
    def parent(self,value):
        '''
            Get this Onode's parent


            `default`:None


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-06-2022 13:52:15
            `@memberOf`: Onode
            `@property`: parent
        '''
        mxCell = self.element.xpath('mxCell')
        mxCell[0].attrib['parent'] = value

    @property
    def tags(self)->_Iterable[str]:
        '''
            Get this Onode's tags


            `default`:None


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-04-2022 10:31:28
            `@memberOf`: Onode
            `@property`: tags
        '''
        value = _obj.get_arg(self.data['attributes'],['tags'],None,(list,str))
        # @Mstep [IF] if the property is not currenty set
        if value is None:
            # @Mstep [] if the tags attribute is a string, convert it to a list.
            if isinstance(value,(str)):
                value = value.split(",")
            value = _arr.remove_duplicates(_arr.force_list(value))

            # @Mstep [] remove empty strings or tags that are only a comma
            new_tags = []
            for tag in value:
                if tag is None:
                    continue
                if len(tag) == 0 or tag == ",":
                    continue
                new_tags.append(tag)


            value = new_tags
            self.data['attributes']['tags'] = value
        return value

    @property
    def source(self):
        '''
            Get this Onode's source


            `default`:None


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-05-2022 14:01:42
            `@memberOf`: Onode
            `@property`: source
        '''
        value = _obj.get_arg(self.mxcell_attributes,['source'],None,(str))
        self.data['source'] = value
        return value

    @property
    def target(self):
        '''
            Get this Onode's target


            `default`:None


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-05-2022 14:03:29
            `@memberOf`: Onode
            `@property`: target
        '''
        value = _obj.get_arg(self.mxcell_attributes,['target'],None,(str))
        self.data['target'] = value
        return value

    @property
    def is_connector(self):
        '''
            Get this Onode's is_connector


            `default`:None


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-05-2022 14:00:09
            `@memberOf`: Onode
            `@property`: is_connector
        '''
        if 'source' in self.mxcell_attributes:
            return True
        return False

    @property
    def mxcell_attributes(self):
        '''
            Get this Onode's mxcell_attributes


            `default`:None


            Meta
            ----------
            `@author`: Colemen Atwood
            `@created`: 07-05-2022 13:57:52
            `@memberOf`: Onode
            `@property`: mxcell_attributes
        '''
        return self.data['mxcell']['attributes']

    def remove_coords(self):
        # self.data['mxcell']['attributes'] = _obj.remove_keys(self.data['mxcell']['attributes'],['x','y'])
        # mxcell = self.element.xpath('mxCell')
        # mxcell = mxcell[0]
        # print(mxcell.attrib)
        mxCell = self.element.xpath('mxCell')
        mxGeo = mxCell[0].xpath('mxGeometry')        
        del mxGeo[0].attrib['x']
        del mxGeo[0].attrib['y']
        del self.data['mxgeometry']['x']
        del self.data['mxgeometry']['y']

