import bpy

from bpy.types import Operator

from . jex_export import JExport_Export
	
class JExport_OT_Operator(Operator):
    bl_idname = "object.jex_ot_operator"
    bl_label = "Batch Export"
    bl_description = "Export selected objects as fbx" 
    bl_options = {'REGISTER'}
    
    def execute(self, context):

        bat_export = JExport_Export(context)
        bat_export.do_export()
        
        self.report({'INFO'}, "Exported to " + context.scene.engine_folder)
        return {'FINISHED'}


