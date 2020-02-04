import bpy
import os
import fnmatch
from . jex_utils import *

class JEXPORT_Export:
  def __init__(self, context):
    self.__context = context
    self.__engine_folder = context.scene.engine_folder
    self.__bake_folder = context.scene.bake_folder
    self.__export_applyTransform = context.scene.apply_transform
    self.__export_applyModifiers = context.scene.apply_modifiers
    self.__export_prefix = context.scene.export_prefix
    self.__export_exportScale = context.scene.export_scale
    self.__center_transform = context.scene.center_transform
    self.__create_object_lists = context.selected_objects
    self.__export_target = context.scene.export_target
    self.__export_type = context.scene.export_type
    self.__texture_type = context.scene.texture_type
    self.__obj_list = []
    self.__obj_pos_list = []
    print(self.__engine_folder)
    print(self.__bake_folder)

  def exportfbx(self):
    bpy.ops.export_scene.fbx(check_existing=False,
    filepath=exportfolder + c.name + ".fbx",
    filter_glob="*.fbx",
    use_selection=True,
    use_armature_deform_only=True,
    mesh_smooth_type=self.__context.scene.export_smoothing,
    add_leaf_bones=False,
    global_scale=self.exportscale,
    bake_space_transform=self.__export_applyTransform,
    use_mesh_modifiers=self.__export_applyModifiers,
    path_mode='ABSOLUTE')
   
  def do_export(self):
    try:
      bpy.ops.object.mode_set(mode='OBJECT')
    except:
      pass

    area = bpy.context.area.type
    bpy.context.area.type = 'VIEW_3D'

    if self.__export_target == 'OBJECT':
      self.create_object_list()  

    elif self.__export_target == 'COLLECTION':
      self.create_collection_list()

    elif self.__export_target == 'BOTH':
      self.create_object_list()
      self.create_collection_list()

    self.export()
    
    bpy.context.area.type = area

  def create_object_list(self):    
    for obj in bpy.data.objects:
      if obj.users_collection[0].name == "Master Collection": #in base of scene
        self.__obj_list.append(["OBJECT", "", [obj], True]) 

  def create_collection_list(self):
    for col in bpy.data.collections:
      if col.name[-1] == "\\" or col.name[-1] == "/": #export objects collections whos names end with \ or / to individual files
        for obj in col.objects:
          self.__obj_list.append(["OBJECT", col, [obj], True])
      else:
        self.__obj_list.append(["COLLECTION", col, col.objects, False])

  def shouldExportCheck(self, item)
    print("checking")
    return true

  def export(self):    
    itemName =""
    fileName = ""
    folderName = ""

    exportScale = self.__export_exportScale #TODO this is not used
    
    #__obj_list is (type, colletion, object_list[], get_moved_BOOL)
    for obj in self.__obj_list:
      # Desect all objects
      bpy.ops.object.select_all(action='DESELECT')      

      #prepare objects for export,       
      for o in obj[2]:                
        o.select_set(state = True)
        if obj[3] == True:
          self.center_object(o)
        for child in get_children(obj): # TODO add bool
          child.select_set(state=True)
      
      # Setup export file path
      if obj[0] == "OBJECT":  
        itemName = obj[1].name + obj[2][0].name
        
      elif obj[0] == "COLLECTION":
        itemName = obj[1].name
      
      if "/" in itemName:
        itemName = itemName.replace("/", "\\")

      if "\\" in itemName:
        exportFolder = self.__engine_folder + itemName.rsplit('\\', 1)[0] + "\\"
      else:
        exportFolder = self.__engine_folder
      
      # Make folder
      try:
        os.makedirs(exportFolder)
      except:
        pass
      
      # Deal with prefex names
      #if self.__export_prefix == False:
      #  itemName = itemName.replace('SM_', '') #TODO put SM_ on UI

      # Do the actual export
      filePath = self.__engine_folder + itemName + ".fbx"
      print(filePath)
      export = True
      if (export == True):
        bpy.ops.export_scene.fbx(check_existing=False, filepath=filePath, filter_glob="*.fbx",use_selection=True,use_armature_deform_only=True,
                              mesh_smooth_type=self.__context.scene.export_smoothing,add_leaf_bones=False,global_scale=self.__export_exportScale,bake_space_transform=self.__export_applyTransform,
                              use_mesh_modifiers=self.__export_applyModifiers,path_mode='ABSOLUTE')

    # Return objects to old position so
    self.uncenter_objects()

  def center_object(self, obj):
    #add object to list with name and old position
    if self.__center_transform:
      self.__obj_pos_list.append([obj, obj.location.copy()])
      obj.location = (0,0,0)

  def uncenter_objects(self):    
    #loop list and set object to old position
    for o in self.__obj_pos_list:
      o[0].location = o[1]         
  
class JEXPORT_ExportTextures:

  def __init__(self, context):
    self.__context = context
    self.__texture_folder = context.scene.texture_folder
    self.__texture_type = context.scene.texture_type

  def export_textures(self):
    D = bpy.data
    for image in D.images:
      if not image.has_data:
          continue
      overwrite = 'true'
      original_image = bpy.path.abspath(image.filepath)
      print(original_image)
      if original_image.endswith(self.__texture_type):
        overwrite = 'false'

      if fnmatch.fnmatch(image.name, "*.tga"):
        image.name = image.name.replace('.tga', '')
      if fnmatch.fnmatch(image.name, "*.png"):
        image.name = image.name.replace('.png', '')
      if fnmatch.fnmatch(image.name, "*.dds"):
        image.name = image.name.replace('.dds', '')

      if self.__texture_type == '.tga':
        image.file_format = 'TARGA'
      elif self.__texture_type == '.png':
        image.file_format = 'PNG'

      image.filepath_raw = self.__texture_folder + image.name
      image.save()

      #removes old file
      print("Exported: ", self.__texture_type)
      if overwrite == 'true':
        print('deleting ' + original_image)
        os.remove(original_image)

    print('Exported Textures')

  # I should switch to this extension check system:
    #import os
    #base=os.path.basename('my.file.ext')
    #t = os.path.splitext(base)
    #print(t) >>> ('my.file', '.ext')

