# -*- coding: utf-8 -*- 
import bpy
from bpy.props import *
from digidone.props import component_type_save, component_type_get, dgd_add_props, ComponentProps
 

class ComponentTypeOperator(bpy.types.Operator):
    bl_idname = "object.component_type_op"
    bl_label = "Save Component Type"
 
    ct_name = StringProperty(name="Component Type Name")
 
    def execute(self, context):
        try:
            obj = bpy.context.active_object
            ct_props = ComponentProps(obj['dgd_width'], obj['dgd_depth'], obj['dgd_height'])
            component_type_save(self.ct_name, props=ct_props)
        except Exception as e:
            print(e)
        return {'FINISHED'}
 
    def invoke(self, context, event):
        obj = bpy.context.active_object
        self.ct_name = component_type_get(obj['dgd_component_type'])['name']
        return context.window_manager.invoke_props_dialog(self)


def register():
    dgd_add_props()
    bpy.utils.register_class(ComponentTypeOperator)


def unregister():
    bpy.utils.unregister_class(ComponentTypeOperator)


if __name__ == "__main__":
    register()
