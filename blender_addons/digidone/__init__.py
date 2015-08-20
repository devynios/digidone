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


digidone_param_type_items = [
    ('FLOAT'  , 'Float'  , '', 0),
    ('INTEGER', 'Integer', '', 1),
    ('BOOLEAN', 'Boolean', '', 2),
    ('STRING' , 'String' , '', 3),
]


class DigidoneParameter(bpy.types.PropertyGroup):
    ptype =  bpy.props.EnumProperty(name='Parameter Type', items=digidone_param_type_items)
    name = bpy.props.StringProperty(name='Parameter Name')
    group = bpy.props.StringProperty(name='Parameter Group')
    value_FLOAT = bpy.props.FloatProperty(name='Parameter Value')
    value_INTEGER = bpy.props.IntProperty(name='Parameter Value')
    value_BOOLEAN = bpy.props.BoolProperty(name='Parameter Value')
    value_STRING = bpy.props.StringProperty(name='Parameter Value')


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
        bpy.ops.object.parent_set(type='OBJECT')
        return {'FINISHED'}


class OBJECT_OT_digidone_component_addparam(bpy.types.Operator):
    bl_idname = "object.digidone_component_addparam"
    bl_label = "Add Parameter"

    def execute(self, context):
        obj = bpy.context.active_object
        param = obj.dgd_params.add()
        return {'FINISHED'}


class OBJECT_OT_digidone_component_delparam(bpy.types.Operator):
    bl_idname = "object.digidone_component_delparam"
    bl_label = "Remove Parameter"

    index = bpy.props.IntProperty(name='Index', default=-1, options={'HIDDEN'})

    def execute(self, context):
        idx = self.index
        if idx < 0:
            return {'CANCELLED'}
        obj = bpy.context.active_object
        obj.dgd_params.remove(idx)
        return {'FINISHED'}


class OBJECT_OT_digidone_component_editparam(bpy.types.Operator):
    bl_idname = "object.digidone_component_editparam"
    bl_label = "Edit Parameter"

    index = bpy.props.IntProperty(name='Index', default=-1, options={'HIDDEN'})
    name = bpy.props.StringProperty(name='Parameter Name')
    ptype =  bpy.props.EnumProperty(name='Parameter Type', items=digidone_param_type_items)
    group = bpy.props.StringProperty(name='Parameter Group')

    def execute(self, context):
        idx = self.index
        if idx < 0:
            return {'CANCELLED'}
        obj = bpy.context.active_object
        param = obj.dgd_params[idx]
        param.name = self.name
        param.ptype = self.ptype
        param.group = self.group
        for win in context.window_manager.windows:
            for area in win.screen.areas:
                area.tag_redraw()
        return {'FINISHED'}

    def invoke(self, context, event):
        idx = self.index
        obj = bpy.context.active_object
        param = obj.dgd_params[idx]
        self.name = param.name
        self.ptype = param.ptype
        self.group = param.group
        return context.window_manager.invoke_props_dialog(self)


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
        row = layout.row(align=True)
        row.prop(actobj, 'dgd_object_type_sel', text='', icon='TRIA_DOWN', icon_only=True)
        row.prop(actobj, 'dgd_object_type', text='')
        #layout.template_ID(bpy.context.scene.objects, 'dgd_test') # TODO
        for param in actobj.dgd_params:
            pname = param.get('name')
            if not pname:
                continue
            layout.prop(param, 'value_%s' % (param.ptype,), text=pname)


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
        for i, param in enumerate(actobj.dgd_params):
            row = layout.row()
            row.column().prop(param, 'name', text='')
            row = row.column().row(align=True)
            op = row.operator('object.digidone_component_editparam', text='Edit')
            op.index = i
            op = row.operator('object.digidone_component_delparam', text='', icon='ZOOMOUT')
            op.index = i
            op = None


def digidone_obj_type_items(self, context):
    objlist = []
    for obj in context.scene.objects:
        if obj.get('dgd_is_parametric'):
            objlist.append(tuple([getattr(param, 'value_%s' % (param.ptype,)) for param in obj.dgd_params]))
    #return [('', '', '', 0)] + [(str(i), 'Type %d' % (i,), '', i) for i, obj in enumerate(set(objlist), start=1)]
    return [(str(i), 'Type %d' % (i,), '', i) for i, obj in enumerate(set(objlist))]


def digidone_obj_type_update(self, context):
    obj = context.active_object
    obj['dgd_object_type'] = digidone_obj_type_items(self, context)[obj['dgd_object_type_sel']][1]
    #obj['dgd_object_type_sel'] = 0


digidone_modes = [
    ('OBJECT', 'Object', '', 0),
    ('EDIT'  , 'Edit'  , '', 1),
]


def register():
    bpy.utils.register_module(__name__)
    bpy.types.Object.dgd_is_parametric = bpy.props.BoolProperty(name='Is Parametric')
    bpy.types.Object.dgd_params = bpy.props.CollectionProperty(type=DigidoneParameter)
    #bpy.types.Object.dgd_object_family = bpy.props.StringProperty(name='Family')
    bpy.types.Object.dgd_object_type_sel = bpy.props.EnumProperty(name='Type', items=digidone_obj_type_items, update=digidone_obj_type_update)
    bpy.types.Object.dgd_object_type = bpy.props.StringProperty(name='Type')
    bpy.types.Object.dgd_mode = bpy.props.EnumProperty(name='Mode', items=digidone_modes)
    #bpy.types.SceneObjects.dgd_test = bpy.props.PointerProperty(type=DigidoneParameter)


def unregister():
    bpy.utils.unregister_module(__name__)


if __name__ == "__main__":
    register()
