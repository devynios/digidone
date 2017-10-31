bl_info = {
    "name": "Digidone",
    "author": "Nesvarbu",
    "version": (0, 0, 1),
    "blender": (2, 80, 0),
    "location": "Toolshelf > Parameters",
    "warning": "",
    "description": "Modify object parameters",
    "wiki_url": "http://wiki.digidone3d.com/index.php/Main_Page",
    "category": "3D View",
}

import bpy


def digidone_objprop_obj_items(self, context):
    actobj = context.active_object
    return [(obj.name, obj.name, '', i) for i, obj in enumerate(actobj.children)]


digidone_objprop_prop_items = [
    ('location.x'      , 'Location X' , '', 0),
    ('location.y'      , 'Location Y' , '', 1),
    ('location.z'      , 'Location Z' , '', 2),
    ('rotation_euler.x', 'Rotation X' , '', 3),
    ('rotation_euler.y', 'Rotation Y' , '', 4),
    ('rotation_euler.z', 'Rotation Z' , '', 5),
    ('dimensions.x'    , 'Dimension X', '', 6),
    ('dimensions.y'    , 'Dimension Y', '', 7),
    ('dimensions.z'    , 'Dimension Z', '', 8),
]


digidone_param_type_items = [
    ('FLOAT'  , 'Float'  , '', 0),
    ('INTEGER', 'Integer', '', 1),
    ('BOOLEAN', 'Boolean', '', 2),
    ('STRING' , 'String' , '', 3),
]


def digidone_param_value_update(self, context):
    objitems = digidone_objprop_obj_items(self, context)
    for a in self.assigned_props:
        idx = a.get('obj', 0)
        obj = bpy.data.objects[objitems[idx][0]]
        idx = a.get('prop', 0)
        (prop, axis) = digidone_objprop_prop_items[idx][0].split('.')
        attr = getattr(obj, prop)
        setattr(attr, axis, self['value_FLOAT'])


def digidone_asm_name_items(self, context):
    return [(str(i), asm.name, '', i) for i, asm in enumerate(context.scene.world.dgd_assemblies)]


def digidone_asm_type_items(self, context):
    objlist = []
    for obj in bpy.data.objects:
        if obj.get('dgd_is_parametric'):
            objlist.append(tuple([getattr(param, 'value_%s' % (param.ptype,)) for param in obj.dgd_assembly.params]))
    #return [('', '', '', 0)] + [(str(i), 'Type %d' % (i,), '', i) for i, obj in enumerate(set(objlist), start=1)]
    return [(str(i), 'Type %d' % (i,), '', i) for i, obj in enumerate(set(objlist))]


class DigidoneObjectProperty(bpy.types.PropertyGroup):
    obj = bpy.props.EnumProperty(name='Object', items=digidone_objprop_obj_items)
    prop = bpy.props.EnumProperty(name='Property', items=digidone_objprop_prop_items)


class DigidoneParameter(bpy.types.PropertyGroup):
    ptype =  bpy.props.EnumProperty(name='Parameter Type', items=digidone_param_type_items)
    name = bpy.props.StringProperty(name='Parameter Name')
    group = bpy.props.StringProperty(name='Parameter Group')
    value_FLOAT = bpy.props.FloatProperty(name='Parameter Value', update=digidone_param_value_update)
    value_INTEGER = bpy.props.IntProperty(name='Parameter Value')
    value_BOOLEAN = bpy.props.BoolProperty(name='Parameter Value')
    value_STRING = bpy.props.StringProperty(name='Parameter Value')
    assigned_props = bpy.props.CollectionProperty(type=DigidoneObjectProperty)


class DigidoneAssembly(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty(name='Assembly Name')
    params = bpy.props.CollectionProperty(type=DigidoneParameter)


class OBJECT_OT_digidone_assembly_create(bpy.types.Operator):
    bl_idname = "object.digidone_assembly_create"
    bl_label = "Create Assembly"

    def execute(self, context):
        selobjs = list(context.selected_objects)
        actobj = context.active_object
        bpy.ops.object.empty_add(
            type='PLAIN_AXES',
            view_align=False,
            location=tuple(actobj.location),
            rotation=(0, 0, 0),
            #layers=current_layers,
        )
        actobj = context.active_object
        actobj['dgd_is_parametric'] = True
        for obj in selobjs:
            obj.select_set('SELECT')
        actobj.select_set('DESELECT')
        actobj.select_set('SELECT')
        bpy.ops.object.parent_set(type='OBJECT')
        world = context.scene.world
        asm = world.dgd_assemblies.add()
        asm.name = 'Asm.%d' % (world.dgd_nextasmnum,)
        world.dgd_nextasmnum += 1
        actobj.name = asm.name
        actobj['dgd_assembly_name'] = asm.name
        actobj['dgd_assembly'] = asm
        mc = context.scene.master_collection
        if 'dgd_assemblies' not in mc.collections:
            mc.collections.new('dgd_assemblies')
        mc.collections['dgd_assemblies'].objects.link(actobj)
        return {'FINISHED'}


class OBJECT_OT_digidone_assembly_add(bpy.types.Operator):
    bl_idname = "object.digidone_assembly_add"
    bl_label = "Add Assembly"

    asm =  bpy.props.EnumProperty(name='Assembly', items=digidone_asm_name_items)
    asmtype =  bpy.props.EnumProperty(name='Type', items=digidone_asm_type_items)

    def execute(self, context):
        if not self.asm:
            return {'CANCELLED'}
        item = digidone_asm_name_items(self, context)[int(self.asm)]
        obj = bpy.data.objects[item[1]]
        obj.select_set('SELECT')
        bpy.ops.object.select_grouped()
        obj.select_set('SELECT')
        bpy.ops.object.duplicate_move_linked()
        obj = context.active_object
        obj.location = context.scene.cursor_location
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


class OBJECT_OT_digidone_assembly_addparam(bpy.types.Operator):
    bl_idname = "object.digidone_assembly_addparam"
    bl_label = "Add Parameter"

    def execute(self, context):
        obj = bpy.context.active_object
        param = obj.dgd_assembly.params.add()
        return {'FINISHED'}


class OBJECT_OT_digidone_assembly_delparam(bpy.types.Operator):
    bl_idname = "object.digidone_assembly_delparam"
    bl_label = "Remove Parameter"

    index = bpy.props.IntProperty(name='Index', default=-1, options={'HIDDEN'})

    def execute(self, context):
        idx = self.index
        if idx < 0:
            return {'CANCELLED'}
        obj = bpy.context.active_object
        obj.dgd_assembly.params.remove(idx)
        return {'FINISHED'}


class OBJECT_OT_digidone_assembly_editparam(bpy.types.Operator):
    bl_idname = "object.digidone_assembly_editparam"
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
        param = obj.dgd_assembly.params[idx]
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
        param = obj.dgd_assembly.params[idx]
        self.name = param.name
        self.ptype = param.ptype
        self.group = param.group
        return context.window_manager.invoke_props_dialog(self)


class OBJECT_OT_digidone_assembly_assignparam(bpy.types.Operator):
    bl_idname = "object.digidone_assembly_assignparam"
    bl_label = "Assign Parameter"

    index = bpy.props.IntProperty(name='Index', default=-1, options={'HIDDEN'})

    def execute(self, context):
        idx = self.index
        if idx < 0:
            return {'CANCELLED'}
        obj = bpy.context.active_object
        param = obj.dgd_assembly.params[idx]
        param.assigned_props.add()
        return {'FINISHED'}


class OBJECT_OT_digidone_assembly_unassignparam(bpy.types.Operator):
    bl_idname = "object.digidone_assembly_unassignparam"
    bl_label = "Remove Parameter Assignment"

    index = bpy.props.IntProperty(name='Index', default=-1, options={'HIDDEN'})
    propindex = bpy.props.IntProperty(name='Property Index', default=-1, options={'HIDDEN'})

    def execute(self, context):
        idx = self.index
        pidx = self.propindex
        if (idx < 0) or (pidx < 0):
            return {'CANCELLED'}
        obj = bpy.context.active_object
        param = obj.dgd_assembly.params[idx]
        param.assigned_props.remove(pidx)
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
        layout.operator('object.digidone_assembly_add')
        actobj = bpy.context.active_object
        if (actobj is None) or (not actobj.get('dgd_is_parametric')):
            return
        row = layout.row(align=True)
        row.prop(actobj, 'dgd_assembly_name_sel', text='', icon='TRIA_DOWN', icon_only=True)
        row.prop(actobj, 'dgd_assembly_name', text='')
        row = layout.row(align=True)
        row.prop(actobj, 'dgd_assembly_type_sel', text='', icon='TRIA_DOWN', icon_only=True)
        row.prop(actobj, 'dgd_assembly_type', text='')
        #layout.template_ID(bpy.context.scene.objects, 'dgd_test') # TODO
        for param in actobj.dgd_assembly.params:
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
        if actobj is None:
            return
        layout.prop(actobj, 'dgd_mode', expand=True)
        layout.operator('object.digidone_assembly_create')
        if not actobj.get('dgd_is_parametric'):
            return
        row = layout.row(align=True)
        row.prop(actobj, 'dgd_assembly_name_sel', text='', icon='TRIA_DOWN', icon_only=True)
        row.prop(actobj, 'dgd_assembly_name', text='')
        row = layout.row(align=True)
        row.prop(actobj, 'dgd_assembly_type_sel', text='', icon='TRIA_DOWN', icon_only=True)
        row.prop(actobj, 'dgd_assembly_type', text='')
        row = layout.row(align=True)
        row.operator('object.digidone_assembly_addparam')
        row.operator('object.digidone_assembly_addparam', text='', icon='ZOOMIN')
        for i, param in enumerate(actobj.dgd_assembly.params):
            row = layout.row()
            row.column().prop(param, 'name', text='')
            row = row.column().row(align=True)
            op = row.operator('object.digidone_assembly_editparam', text='Edit')
            op.index = i
            op = row.operator('object.digidone_assembly_delparam', text='', icon='ZOOMOUT')
            op.index = i
            row = layout.row(align=True)
            op = row.operator('object.digidone_assembly_assignparam', text='', icon='ZOOMIN')
            op.index = i
            for j, prop in enumerate(param.assigned_props):
                row = layout.row(align=True)
                row.prop(prop, 'obj', text='')
                row.prop(prop, 'prop', text='')
                op = row.operator('object.digidone_assembly_unassignparam', text='', icon='ZOOMOUT')
                op.index = i
                op.propindex = j


def digidone_asm_name_select(self, context):
    obj = context.active_object
    item = digidone_asm_name_items(self, context)[obj['dgd_assembly_name_sel']]
    if obj['dgd_assembly_name'] == item[1]:
        return
    bpy.ops.object.select_grouped()
    obj.select_set('SELECT')
    loc = tuple(obj.location)
    bpy.ops.object.delete() # use_global=False/True
    obj = bpy.data.objects[item[1]]
    obj.select_set('SELECT')
    bpy.ops.object.select_grouped()
    obj.select_set('SELECT')
    bpy.ops.object.duplicate_move_linked()
    obj = context.active_object
    obj.location = loc


def digidone_asm_name_update(self, context):
    obj = bpy.context.active_object
    obj.name = obj.dgd_assembly_name
    try:
        context.scene.world.dgd_assemblies[obj.dgd_assembly.name].name = obj.dgd_assembly_name
    except:
        pass


def digidone_asm_update(self, context):
    pass # TODO


def digidone_asm_type_select(self, context):
    obj = context.active_object
    obj['dgd_assembly_type'] = digidone_asm_type_items(self, context)[obj['dgd_assembly_type_sel']][1]


digidone_modes = [
    ('OBJECT', 'Object', '', 0),
    ('EDIT'  , 'Edit'  , '', 1),
]


def register():
    bpy.utils.register_module(__name__)
    bpy.types.World.dgd_assemblies = bpy.props.CollectionProperty(type=DigidoneAssembly)
    bpy.types.World.dgd_nextasmnum = bpy.props.IntProperty(name='Next Assembly Number')
    bpy.types.Object.dgd_is_parametric = bpy.props.BoolProperty(name='Is Parametric')
    bpy.types.Object.dgd_assembly = bpy.props.PointerProperty(type=DigidoneAssembly, update=digidone_asm_update)
    bpy.types.Object.dgd_assembly_name = bpy.props.StringProperty(name='Assembly Name', update=digidone_asm_name_update)
    bpy.types.Object.dgd_assembly_name_sel = bpy.props.EnumProperty(name='Assembly Name', items=digidone_asm_name_items, update=digidone_asm_name_select)
    bpy.types.Object.dgd_assembly_type_sel = bpy.props.EnumProperty(name='Type', items=digidone_asm_type_items, update=digidone_asm_type_select)
    bpy.types.Object.dgd_assembly_type = bpy.props.StringProperty(name='Type')
    bpy.types.Object.dgd_mode = bpy.props.EnumProperty(name='Mode', items=digidone_modes)


def unregister():
    bpy.utils.unregister_module(__name__)


if __name__ == "__main__":
    register()
