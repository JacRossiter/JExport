bl_info = {
    "name" : "JExport",
    "author" : "Jac Rossiter, jayanam",
    "descrtion" : "Batch export as Fbx",
    "blender" : (2, 80, 0),
    "version" : (0, 3, 1, 4),
    "location" : "JExport panel",
    "warning" : "",
    "category" : "Export"
}

import bpy
from bpy.props import *

from . jex_panel import *
from . jex_op import *
from . jex_folder_op import *



bpy.types.Scene.engine_folder = StringProperty(name="engine folder", 
               subtype="DIR_PATH", 
               description="Directory to export the fbx files into")

bpy.types.Scene.bake_folder = StringProperty(name="Bake folder", 
               subtype="DIR_PATH", 
               description="Directory to export the Bake files into")

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
#
bpy.types.Scene.export_target = EnumProperty(name="Target",
                description="Defines whether to export Object or Collection",
                items=(
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


## testing
bpy.types.Scene.export_prefix = BoolProperty(name="Export Prefix",
                default=True,
                description="Includes Prefix in Export")
#
classes = ( JExport_PT_Panel, JExport_OT_Operator, JExport_OT_OpenFolder, JExport_OT_OpenBakeFolder, JExport_PT_Panel_Settings, JExport_PT_Panel_Export_Settings )


def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    
    #bpy.types.Scene.rno_bool_exportall = bpy.props.BoolProperty(name='Export all', default=True)

          
def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)

    #del bpy.types.Scene.rno_bool_exportall
    


if __name__ == "__main__":
    register()
