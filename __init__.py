# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name" : "NX_AlignToGlobal",
    "author" : "Franck Demongin",
    "description" : "Align the normal of a face or set of faces to Global orientation",
    "blender" : (2, 80, 0),
    "version" : (1, 0, 0),
    "location" : "View 3D, menu Object > Transform > Align to Global Orientation",
    "warning" : "",
    "category" : "Object"
}

import bpy

class NXATG_OT_alignToGlobal(bpy.types.Operator):    
    """Align face normal to Global orientation"""    
    bl_idname = 'nxatg.align_to_global'
    bl_label = 'Align to Global Orientation'
    bl_options = {'REGISTER', 'UNDO'}
    
    apply_to_children: bpy.props.BoolProperty(name="Apply to Children", default=False)
    apply_recursive: bpy.props.BoolProperty(name="Apply recursive", default=False)

    @classmethod
    def poll(cls, context):
        if (not context.object or 
            len([f for f in context.object.data.polygons if f.select]) == 0):
            return False
                    
        return True
    
    def execute(self, context):

        obj = context.object

        bpy.ops.object.mode_set(mode='EDIT')
    
        area = [a for a in context.screen.areas if a.type == 'VIEW_3D'][-1]
        with context.temp_override(area=area):
            bpy.ops.transform.create_orientation(name="CorrectOrientation", overwrite=True, use=True)
    
        bpy.ops.object.mode_set(mode='OBJECT')
        
        bpy.ops.mesh.primitive_cube_add()
        cube = context.object
        
        bpy.ops.transform.transform(mode="ALIGN", orient_type='CorrectOrientation')
        
        obj.select_set(True)    
        bpy.ops.object.parent_set(type='OBJECT')
        bpy.ops.object.rotation_clear()
        
        context.view_layer.objects.active = obj
        bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
        bpy.ops.object.transform_apply(rotation=True)
        
        if self.apply_to_children:
            if self.apply_recursive:
                objs = obj.children_recursive
            else:
                objs = obj.children

            for ob in objs:
                print(ob.name)
                ob.select_set(True)
                context.view_layer.objects.active = ob
                bpy.ops.object.transform_apply(rotation=True)
                ob.select_set(False)
        
        context.view_layer.objects.active = obj
        
        bpy.data.objects.remove(cube, do_unlink=True)

        with context.temp_override(area=area):
            bpy.ops.transform.delete_orientation()

        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout

        layout.prop(self, 'apply_to_children', text='Apply to Children')

        if self.apply_to_children:
            layout.prop(self, 'apply_recursive', text='Apply recursive')


def draw_menu(self, context):    
    layout = self.layout
    layout.separator()
    layout.operator('nxatg.align_to_global', text="Align to Global Orientation")

classes = (
    NXATG_OT_alignToGlobal,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.VIEW3D_MT_transform_object.append(draw_menu)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    bpy.types.VIEW3D_MT_transform_object.remove(draw_menu)
