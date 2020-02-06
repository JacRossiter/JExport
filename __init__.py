bl_info = {
    "name" : "JEXPORT",
    "author" : "Jac Rossiter, jayanam",
    "descrtion" : "Batch export as Fbx",
    "blender" : (2, 80, 0),
    "version" : (0, 3, 1, 6),
    "location" : "JEXPORT panel",
    "warning" : "",
    "category" : "Export"
}

import importlib

if "bpy" in locals():    
    importlib.reload(jex_export)
    importlib.reload(jex_folder_op)
    importlib.reload(jex_op)
    importlib.reload(jex_panel)
    importlib.reload(jex_utils)
    
import bpy
from bpy.props import *
from . jex_export import *
from . jex_folder_op import *
from . jex_op import *
from . jex_panel import *
from . jex_utils import *

bpy.types.Scene.debug_export = BoolProperty(name="dont export",
                default=True,
                description="easy way to stop actual export happening")

bpy.types.Scene.debug_keep_duplicated = BoolProperty(name="keep duplicated",
                default=False,
                description="keep duplicated and merged collection so you can see whats going on")

bpy.types.Scene.engine_folder = StringProperty(name="engine folder", 
               subtype="DIR_PATH", 
               description="Directory to export the fbx files into")

bpy.types.Scene.bake_folder = StringProperty(name="Bake folder", 
               subtype="DIR_PATH", 
               description="Directory to export the Bake files into")

bpy.types.Scene.selected_only = BoolProperty(name="Only Export Selected Objects",
                default=False,
                description="Export selection and ignore un selected objects")

bpy.types.Scene.export_hidden = BoolProperty(name="Export Hidden Objects",
                default=False,
                description="Export objects even if they are hidden")

bpy.types.Scene.exclude_star = BoolProperty(name="Don't Export Objects Containing *",
                default=True,
                description="Objects or Collections with * appearing anywhere in the name wont get exported")

bpy.types.Scene.merge_ampersand = BoolProperty(name="Merge All Chidren Of Collections Containing \&",
                default=True,
                description="Collections with & anywhere in name will have all containing objects merged into 1 on export")

bpy.types.Scene.unreal_only = BoolProperty(name="Only Export Objects With Unreal Prefixes",
                default=False,
                description="Object must have SM_ or SK_ prefix to get exported")

bpy.types.Scene.remove_unreal = BoolProperty(name="Remove Unreal Prefix on Export",
                default=False,
                description="Objects with SM_ or SK_ in the name will have it removed on export")                

bpy.types.Scene.folders_from_names = BoolProperty(name="Use / in names to change folders",
                default=True,
                description="create folder structures by using / in folder names")

bpy.types.Scene.texture_folder = StringProperty(name="Texture folder", 
               subtype="DIR_PATH", 
               description="Directory to export the Texture files into")

bpy.types.Scene.center_transform = BoolProperty(name="Center transform",
                default=True,
                description="Set the pivot point of the object to the center")

bpy.types.Scene.apply_transform = BoolProperty(name="Apply transform",
                default=True,
                description="Applies experimental scale and transforms")

bpy.types.Scene.apply_modifiers = BoolProperty(name="Apply modifiers",
                default=True,
                description="Applies modifiers")

bpy.types.Scene.export_scale = FloatProperty(name="Export scale",
                default=1.0,
                min=0.01,
                max=10.0,
                description="Sets the exported model scale")

bpy.types.Scene.export_smoothing = EnumProperty(name="Smoothing",
                description="Defines the export smoothing information",
                items=(
                    ('EDGE', 'Edge', 'Write edge smoothing',0),
                    ('FACE', 'Face', 'Write face smoothing',1),
                    ('OFF', 'Normals Only', 'Write normals only',2)
                    ),
                default='OFF'
                )
                
bpy.types.Scene.export_target = EnumProperty(name="Target",
                description="Defines whether to export Object or Collection",
                default='BOTH',
                items=(
                    ('BOTH', 'Both', 'Export Both',2),
                    ('OBJECT', 'Object', 'Export Objects',0),
                    ('COLLECTION', 'Collection', 'Export Collections',1)
                    )
                )

bpy.types.Scene.export_type = EnumProperty(name="Type",
                description="Defines whether to for Baking or for Engine",
                items=(
                    ('ENGINE', 'Engine', 'EXPORT to Engine',0),
                    ('BAKE', 'Bake', 'Export to Bake',1)
                    )
                )

bpy.types.Scene.export_prefix = BoolProperty(name="Export Prefix",
                default=True,
                description="Includes Prefix in Export")

bpy.types.Scene.texture_type = EnumProperty(name="Type",
                description="Defines What Texture type to use",
                items=(
                    ('.tga', 'TGA', 'Export TGA',0),
                    ('.png', 'PNG', 'Export PNG',1)
                    )
                )

classes = (
    JEXPORT_PT_panel,
    JEXPORT_OT_ExportOperator,
    JEXPORT_OT_ExportTexturesOperator,
    JEXPORT_OT_RefreshTextures, 
    JEXPORT_OT_OpenFolder, 
    JEXPORT_OT_OpenBakeFolder,
    JEXPORT_OT_OpenTextureFolder,
    JEXPORT_PT_Panel_Settings,
    JEXPORT_PT_Panel_Export_Settings,
    JEXPORT_PT_Panel_Export_Textures,
    JEXPORT_PT_Panel_Texture_Settings
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
          
def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
    
if __name__ == "__main__":
    register()
