import bpy

from bpy.types import Operator

from . jex_export import JExport_Export, JExport_ExportTextures
	
class JExport_OT_ExportOperator(Operator):
    bl_idname = "object.jex_ot_operator"
    bl_label = "Batch Export"
    bl_description = "Export selected objects as fbx" 
    bl_options = {'REGISTER'}
    
    def execute(self, context):

        bat_export = JExport_Export(context)
        bat_export.do_export()
        
        self.report({'INFO'}, "Exported to " + context.scene.engine_folder)
        return {'FINISHED'}

class JExport_OT_ExportTexturesOperator(Operator):
    bl_idname = "object.jex_ot_exporttextures"
    bl_label = "Batch Export Textures"
    bl_description = "Export Textures to Engine" 
    bl_options = {'REGISTER'}

    def execute(self, context):
        bat_exporttextures = JExport_ExportTextures(context)
        bat_exporttextures.export_textures()
        return {'FINISHED'}

class JExport_OT_RefreshTextures(Operator):
    bl_idname = "object.refreshtextures"
    bl_label = "Refresh Textures"
    bl_description = "Refresh Textures" 
    bl_options = {'REGISTER'}

    def execute(self, context):
        bpy.ops.autoreload.reload_images()
        return {'FINISHED'}
