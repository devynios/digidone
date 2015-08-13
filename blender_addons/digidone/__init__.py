bl_info = {
    "name": "Digidone",
    "author": "Nesvarbu",
    "version": (0, 0, 1),
    "blender": (2, 75, 0),
    "location": "Toolshelf > Parameters",
    "warning": "",
    "description": "Modify object parameters",
    "wiki_url": "http://wiki.digidone3d.com/index.php/Main_Page",
    "category": "3D View",
}

import bpy


digidone_type_items = [
    ("FLOAT"  , "Float"  , '', 0),
    ("INTEGER", "Integer", '', 1),
    ("BOOLEAN", "Boolean", '', 2),
    ("STRING" , "String" , '', 3),
]


digidone_modes = [
    ("OBJET", "Object", '', 0),
    ("EDIT" , "Edit"  , '', 1),
]


class DigidoneParameter(bpy.types.PropertyGroup):
    ptype =  bpy.props.EnumProperty(name='Parameter Type', items=digidone_type_items)
    name = bpy.props.StringProperty(name="Parameter Name")
    group = bpy.props.StringProperty(name="Parameter Group")
    value = bpy.props.FloatProperty(name="Value Parameter")


class OBJECT_OT_digidone_component_create(bpy.types.Operator):
    bl_idname = "object.digidone_component_create"
    bl_label = "Create Parametric Object"

    def execute(self, context):
        selobjs = list(bpy.context.selected_objects)
        actobj = bpy.context.active_object
        bpy.ops.object.empty_add(
            type='PLAIN_AXES',
            view_align=False,
            location=tuple(actobj.location),
            rotation=(0, 0, 0),
            #layers=current_layers,
        )
        actobj = bpy.context.active_object
        actobj['dgd_is_parametric'] = True
        for obj in selobjs:
            obj.select = True
        actobj.select = False
        actobj.select = True
        bpy.ops.object.parent_set(type="OBJECT")
        return {'FINISHED'}


class OBJECT_OT_digidone_component_addparam(bpy.types.Operator):
    bl_idname = "object.digidone_component_addparam"
    bl_label = "Add Parameter"

    def execute(self, context):
        obj = bpy.context.active_object
        param = obj.dgd_params.add()
        # TODO
        return {'FINISHED'}


class OBJECT_PT_digidone_parameters(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "Digidone"
    bl_label = "Parameters"
    #bl_options = {'DEFAULT_CLOSED'}

    #@classmethod
    #def poll(cls, context):
    #    return True

    def draw(self, context):
        layout = self.layout
        actobj = bpy.context.active_object
        if not actobj.get('dgd_is_parametric'):
            return
        layout.prop(actobj, 'dgd_object_type')
        for param in actobj.dgd_params:
            row = layout.row()
            row.label(text=param['name'])
            row.column().prop(param, 'value', text='Value')


class OBJECT_PT_digidone_edit_parameters(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "Digidone"
    bl_label = "Edit Parameters"
    #bl_options = {'DEFAULT_CLOSED'}

    #@classmethod
    #def poll(cls, context):
    #    return True

    def draw(self, context):
        layout = self.layout
        actobj = bpy.context.active_object
        layout.prop(actobj, 'dgd_mode', expand=True)
        layout.operator('object.digidone_component_create')
        if not actobj.get('dgd_is_parametric'):
            return
        layout.prop(actobj, 'name')
        layout.operator('object.digidone_component_addparam')
        for param in actobj.dgd_params:
            row = layout.row()
            row.column().prop(param, 'ptype', text='Type')
            row.column().prop(param, 'name', text='Name')
            row.column().prop(param, 'group', text='Group')


def digidone_type_items(self, context):
    objlist = []
    for obj in context.scene.objects:
        if obj.get('dgd_is_parametric'):
            objlist.append(tuple([param.value for param in obj.dgd_params]))
    return [(str(i), 'Type %d' % (i,), '', i) for i, obj in enumerate(set(objlist))]


def register():
    bpy.utils.register_module(__name__)
    bpy.types.Object.dgd_params = bpy.props.CollectionProperty(type=DigidoneParameter)
    bpy.types.Object.dgd_object_type = bpy.props.EnumProperty(name='Type', items=digidone_type_items)
    bpy.types.Object.dgd_mode = bpy.props.EnumProperty(name='Mode', items=digidone_modes)


def unregister():
    bpy.utils.unregister_module(__name__)


if __name__ == "__main__":
    register()
