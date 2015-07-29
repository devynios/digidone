import bpy
from bpy.types import NodeTree, Node, NodeSocket
import digidone.props


class ComponentNodeTree(NodeTree):
    '''A custom node tree type that will show up in the node editor header'''
    bl_idname = 'ComponentTreeType'
    bl_label = 'Component Node Tree'
    bl_icon = 'NODETREE'


class ComponentTypeSocket(NodeSocket):
    '''Custom node socket type'''
    bl_idname = 'ComponentTypeSocket'
    bl_label = 'Component Type Socket'

    component_type = bpy.props.EnumProperty(
        name='Component type',
        items=digidone.props.component_type_items,
        update=digidone.props.component_type_update,
    )

    def draw(self, context, layout, node, text):
        if self.is_linked:
            layout.label(text)
        else:
            layout.prop(self, "component_type", text=text)

    def draw_color(self, context, node):
        return (1.0, 0.4, 0.216, 0.5)


class ComponentBaseNode:

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'ComponentTreeType'


class ComponentNode(Node, ComponentBaseNode):
    '''A custom node'''
    bl_idname = 'ComponentNodeType'
    bl_label = 'Component Node'
    bl_icon = 'SOUND'

    group_by = bpy.props.EnumProperty(name='Group by', items=digidone.props.group_by_items)
    #width = bpy.props.IntProperty(name='Width', default=200)
    #depth = bpy.props.IntProperty(name='Depth', default=300)
    #height = bpy.props.IntProperty(name='Height', default=200)


    def init(self, context):
        self.inputs.new('ComponentTypeSocket', "Hello")
        self.inputs.new('NodeSocketInt', "Width")
        self.inputs.new('NodeSocketInt', "Depth")
        self.inputs.new('NodeSocketInt', "Height")

        self.outputs.new('NodeSocketColor', "color")
        self.outputs.new('NodeSocketFloat', "float")
        self.outputs.new('ComponentTypeSocket', "Component Type")

    # Copy function to initialize a copied node from an existing one.
    def copy(self, node):
        print("Copying from node ", node)

    # Free function to clean up on removal.
    def free(self):
        print("Removing node ", self, ", Goodbye!")

    # Additional buttons displayed on the node.
    #def draw_buttons(self, context, layout):
    #    layout.label("Node settings")
    #    layout.prop(self, "myFloatProperty")

    # Detail buttons in the sidebar.
    # If this function is not defined, the draw_buttons function is used instead
    #def draw_buttons_ext(self, context, layout):
    #    layout.prop(self, "myFloatProperty")
    #    # myStringProperty button will only be visible in the sidebar
    #    layout.prop(self, "myStringProperty")


import nodeitems_utils
from nodeitems_utils import NodeCategory, NodeItem

class ComponentNodeCategory(NodeCategory):
    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'ComponentTreeType'

# all categories in a list
node_categories = [
    # identifier, label, items list
    ComponentNodeCategory("COMPONENTNODES", "Component Nodes", items=[
        # our basic node
        NodeItem("ComponentNodeType"),
        ]),
    #ComponentNodeCategory("OTHERNODES", "Other Nodes", items=[
    #    # the node item can have additional settings,
    #    # which are applied to new nodes
    #    # NB: settings values are stored as string expressions,
    #    # for this reason they should be converted to strings using repr()
    #    NodeItem("CustomNodeType", label="Node A", settings={
    #        "myStringProperty" : repr("Lorem ipsum dolor sit amet"),
    #        "myFloatProperty" : repr(1.0),
    #        }),
    #    NodeItem("CustomNodeType", label="Node B", settings={
    #        "myStringProperty" : repr("consectetur adipisicing elit"),
    #        "myFloatProperty" : repr(2.0),
    #        }),
    #    ]),
    ]


def register():
    bpy.utils.register_class(ComponentNodeTree)
    bpy.utils.register_class(ComponentTypeSocket)
    bpy.utils.register_class(ComponentNode)

    nodeitems_utils.register_node_categories("COMPONENT_NODES", node_categories)


def unregister():
    nodeitems_utils.unregister_node_categories("COMPONENT_NODES")

    bpy.utils.unregister_class(ComponentNodeTree)
    bpy.utils.unregister_class(ComponentTypeSocket)
    bpy.utils.unregister_class(ComponentNode)


if __name__ == "__main__":
    register()
