import bpy
from bpy.types import Panel

class JEXPORT_PT_panel(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_label = "Export FBX"
    bl_category = "JEXPORT"
    
    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.scale_y = 1.5
        col.operator('object.jex_ot_operator', text='Export')
        
        col = layout.column()
        col.prop(context.scene, "selected_only", text="selected only")
        col.prop(context.scene, "export_hidden", text="export hidden")

class JEXPORT_PT_Panel_Settings(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_label = "What to export?"
    bl_parent_id = "JEXPORT_PT_panel"
    bl_category = "JEXPORT"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):        
        layout = self.layout
        scene = context.scene
        c = layout.column()

        row = c.row()
        split = row.split(factor=0.3)
        c = split.column()
        c.operator('object.jex_ot_openfolder', text='Engine')
        split = split.split()
        c = split.column()
        c.prop(context.scene, "engine_folder", text="")
        c = layout.column()
        row = c.row()
        split = row.split(factor=0.3)
        c = split.column()
        c.operator('object.jex_ot_openbakefolder', text='Bake')
        split = split.split()
        c = split.column()
        c.prop(context.scene, "bake_folder", text="")

        row = layout.row()
        row.prop(context.scene, "export_target", text="")
        row.prop(context.scene, "export_type", text="")

        col = layout.column()
        col.prop(context.scene, "exclude_star", text="exclude *")
        col.prop(context.scene, "merge_ampersand", text="merge &")
        col.prop(context.scene, "unreal_only", text="unreal prefix only")
        col.prop(context.scene, "remove_unreal", text="remove unreal prefix")    
        col.prop(context.scene, "debug_export", text="export")    
        col.prop(context.scene, "debug_keep_duplicated", text="keep duplicated")    
        


class JEXPORT_PT_Panel_Export_Settings(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_label = "Export Settings"
    bl_parent_id = "JEXPORT_PT_panel"
    bl_category = "JEXPORT"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        
        layout = self.layout
        scene = context.scene

        #col = layout.row()
        col = layout.column(align=True)
        
        if context.scene.export_target == 'OBJECT':
            col.prop(context.scene, "center_transform", text="Move to Zero")
        
        col.prop(context.scene, "apply_transform", text="Apply Transform")
        col.prop(context.scene, "apply_modifiers", text="Apply Modifiers")
        col.prop(context.scene, "export_prefix", text="Export Prefix")
        col.separator(factor=1.0)

        row = layout.row()
        row.prop(context.scene, "export_scale", text="Export Scale")
        row = layout.row()
        row.prop(context.scene, "export_smoothing", text="")

class JEXPORT_PT_Panel_Export_Textures(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_label = "Export Textures"
    #bl_parent_id = "JEXPORT_PT_Panel"
    bl_category = "JEXPORT"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        
        layout = self.layout
        col = layout.column()
        row = col.row()
        split = row.split(factor=0.3)
        col = split.column()
        col.operator('object.jex_ot_opentexturefolder', text='Folder')
        split = split.split()
        col = split.column()
        col.prop(context.scene, "texture_folder", text="")
        row = layout.row(align=True)
        row.scale_y = 1.5
        row.operator('object.jex_ot_exporttextures', text='Export')

class JEXPORT_PT_Panel_Texture_Settings(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_label = "Texture Settings"
    bl_parent_id = "JEXPORT_PT_Panel_Export_Textures"
    bl_category = "JEXPORT"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        
        layout = self.layout
        scene = context.scene
        col = layout.column()
        row = col.row()
        split = row.split(factor=0.3)
        col = split.column()
        col.label(text="Format")
        split = split.split()
        col = split.column()
        col.prop(context.scene, "texture_type", text="")
        col = layout.column()
        row = col.row()
        col.operator('object.refreshtextures', text='Refresh Textures', icon = "FILE_REFRESH")