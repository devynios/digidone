import bpy
from mathutils import Vector

class ComponentProps(object):

    def __init__(self, width=2, depth=2, height=2):
        self.width = width
        self.depth = depth
        self.height = height


_component_types = [
    {'name': 'Small Cube', 'props': ComponentProps()},
    {'name': 'Bigger Cube', 'props': ComponentProps(10, 5, 12)},
]

def component_type_get(num):
    return _component_types[num]

def component_type_find(name):
    for ct in _component_types:
        if ct['name'] == name:
            return ct
    return None

def component_type_save(name, props=ComponentProps()):
    ct = component_type_find(name)
    if ct:
        ct['props'] = props
    else:
        _component_types.append({'name': name, 'props': props})

def update_obj(self, context):
    obj = bpy.context.active_object
    try:
        obj.dimensions = Vector((obj['dgd_width'], obj['dgd_depth'], obj['dgd_height']))
    except Exception as e:
        print(e)

def component_type_update(self, context):
    #new_layer = bpy.context.active_object['dgd_component_type']
    #active_layer = bpy.context.scene.active_layer
    #bpy.context.scene.layers[new_layer] = True
    #bpy.context.scene.layers[active_layer] = False
    obj = bpy.context.active_object
    try:
        obj['dgd_width'] = _component_types[obj['dgd_component_type']]['props'].width
        obj['dgd_depth'] = _component_types[obj['dgd_component_type']]['props'].depth
        obj['dgd_height'] = _component_types[obj['dgd_component_type']]['props'].height
        obj.dimensions = Vector((obj['dgd_width'], obj['dgd_depth'], obj['dgd_height']))
    except Exception as e:
        print(e)

def component_type_items(self, context):
    items = []
    #for i in range(0, 20):
    #    items.append(('cube_type_%s' % i, 'Cube type %s' % i, '', i))
    i = 0
    for ct in _component_types:
        items.append(('component_type_%s' % i, ct['name'], '', i))
        i += 1
    return items


def group_by_items(self, context):
    items = [
        ('component_type', 'Component type', '', 1),
        ('cube_wdh', 'Cube (W x D x H)', '', 2),
        ('cube_wd', 'Cube (W x D)', '', 3),
    ]
    return items


def dgd_add_props():
    bpy.types.Object.dgd_component_type = bpy.props.EnumProperty(
        name='Component type',
        items=component_type_items,
        update=component_type_update,
    )
    bpy.types.Object.dgd_group_by = bpy.props.EnumProperty(name='Group by', items=group_by_items)
    bpy.types.Object.dgd_width = bpy.props.IntProperty(name='Width', default=2, update=update_obj)
    bpy.types.Object.dgd_depth = bpy.props.IntProperty(name='Depth', default=2, update=update_obj)
    bpy.types.Object.dgd_height = bpy.props.IntProperty(name='Height', default=2, update=update_obj)
    #obj = bpy.context.active_object
    #obj['dgd_width'] = 2
    #obj['dgd_depth'] = 2
    #obj['dgd_height'] = 2
