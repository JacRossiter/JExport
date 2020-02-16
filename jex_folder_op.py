import bpy
import os
from bpy.types import Operator

class JEXPORT_OT_OpenFolder(Operator):
  
  bl_idname = "object.jex_ot_openfolder"
  bl_label = "Open Export Folder"
  bl_description = "Open the export folder" 
  bl_options = {'REGISTER'}

  def execute(self, context):
    if "../" or "..\\" or "//" in bpy.context.scene.engine_folder:
      filepath = bpy.data.filepath + "\\..\\"
      exportfolder = os.path.dirname(filepath + context.scene.engine_folder)
      print("Opening EngineFolder: ", exportfolder)
      bpy.ops.wm.path_open(filepath=exportfolder)
    else:
      bpy.ops.wm.path_open(filepath=context.scene.engine_folder)
    return {'FINISHED'}

class JEXPORT_OT_OpenBakeFolder(Operator):
  
  bl_idname = "object.jex_ot_openbakefolder"
  bl_label = "Open Bake Folder"
  bl_description = "Open the Bake folder" 
  bl_options = {'REGISTER'}

  def execute(self, context):
    if "../" or "..\\" or "//" in bpy.context.scene.bake_folder:
      filepath = bpy.data.filepath + "\\..\\"
      exportfolder = os.path.dirname(filepath + context.scene.bake_folder)
      print("Opening BakeFolder: ", exportfolder)
      bpy.ops.wm.path_open(filepath=exportfolder)
    else:
      bpy.ops.wm.path_open(filepath=context.scene.bake_folder)
    return {'FINISHED'}


class JEXPORT_OT_OpenTextureFolder(Operator):
  
  bl_idname = "object.jex_ot_opentexturefolder"
  bl_label = "Open Textures Folder"
  bl_description = "Open the Textures folder" 
  bl_options = {'REGISTER'}

  def execute(self, context):
    bpy.ops.wm.path_open(filepath=context.scene.texture_folder)
    return {'FINISHED'}