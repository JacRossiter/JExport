bl_info = {
    "name" : "JEXPORT",
    "author" : "Jac Rossiter, Frankie Hobbins, jayanam",
    "descrtion" : "Batch export as Fbx",
    "blender" : (2, 80, 0),
    "version" : (0, 3, 1, 8),
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

bpy.types.Scene.engine_folder = StringProperty(name="engine folder", 
               subtype="DIR_PATH", 
               description="Directory to export the fbx files into")

bpy.types.Scene.bake_folder = StringProperty(name="Bake folder", 
               subtype="DIR_PATH", 
               description="Directory to export the Bake files into")

bpy.types.Scene.texture_folder = StringProperty(name="Texture folder", 
               subtype="DIR_PATH", 
               description="Directory to export the Texture files into")

bpy.types.Scene.center_transform = BoolProperty(name="Center transform",
                default=True,
                description="Temporarily move assets to grid zero on export. For collections-if you would like your objects to share a pivot point-parent objects to another object or empty.")

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
                items=(
                    ('BOTH', 'Both', 'Export Both',3),
                    ('OBJECT', 'Object', 'Export Objects',0),
                    ('COLLECTION', 'Collection', 'Export Collections',1)
                    )
                )

bpy.types.Scene.export_type = EnumProperty(name="Type",
                description="Defines whether exporting for Baking or for Engine",
                items=(
                    ('ENGINE', 'Engine', 'Export all assets with SM_ Prefix to Engine Directory',0),
                    ('BAKE', 'Bake', 'Export all assets with either _low or _high suffix assets to Bake Directory',1)
                    )
                )

bpy.types.Scene.export_prefix = BoolProperty(name="Export Prefix",
                default=True,
                description="Includes Prefix in Export name. Disable if not desired")

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
    JEXPORT_PT_Panel_Export_Settings
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
