import bpy
import os
import fnmatch
from . jex_utils import *

class JEXPORT_Export:
  def __init__(self, context):
    self.__context = context
    self.__debug_export = context.scene.debug_export
    self.__selected_only = context.scene.selected_only
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
    print("----EXPORT INIT----") #just see when this is called, safe to delete

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

    self.checkPaths()
      
    if self.__export_target == 'OBJECT':
      self.createObjectList()  

    elif self.__export_target == 'COLLECTION':
      self.createColletionList()

    elif self.__export_target == 'BOTH':
      self.createObjectList()
      self.createColletionList()

    self.export()
    
    bpy.context.area.type = area

  def checkPaths(self):
    if self.__engine_folder == "":
      self.__engine_folder = os.path.dirname(bpy.data.filepath) + "\\"
    if self.__bake_folder == "":
      self.__bake_folder = os.path.dirname(bpy.data.filepath) + "\\"

  def createObjectList(self):
    for obj in bpy.data.objects:
      #if self.__selected_only == True and obj.selec
      if obj.users_collection[0].name == "Master Collection": #in base of scene
        if self.validForExport(obj) == False:          
          continue
        self.__obj_list.append(["OBJECT", "", [obj], True]) 

  def createColletionList(self):
    for col in bpy.data.collections:
      if self.validForExport(col) == False:
        continue
      if self.treatAsFolder(col) == True:
        for obj in col.objects:
          self.__obj_list.append(["OBJECT", col.name, [obj], True])
      else:
        self.__obj_list.append(["COLLECTION", col.name, col.objects, False])
  
  def treatAsFolder(self, item):
    #export objects collections whos names end with \ or / to individual files
    if item.name[-1] == "\\" or item.name[-1] == "/":
      return True
    return False

  def validForExport(self, item):
    if "*" in item.name:
      return False
    if item.hide_viewport:
      return False
    try:
      for o in bpy.context.view_layer.layer_collection.children:
        if o.collection == item:
          if o.hide_viewport == True or o.exclude == True:
            return False
          return True
    except:
      pass    
    try:
      for o in bpy.context.scene.objects:
        if o == item:
          if o.hide_viewport == True:
            print("not valid export222")
            return False
          return True
    except:
      pass    
    return False

  def export(self):    
    itemName =""
    fileName = ""
    folderName = ""
    exportScale = self.__export_exportScale #TODO this is not used
    
    #__obj_list is (type, colletion, object_list[], get_moved_BOOL)
    for obj in self.__obj_list:
      # Desect all objects
      bpy.ops.object.select_all(action='DESELECT')      

      #prepare objects for export
      for o in obj[2]:                
        o.select_set(state = True)
        if obj[3] == True:
          self.centerObject(o)
        for child in get_children(obj): # TODO add bool
          child.select_set(state=True)
      
      # Setup export file path
      if obj[0] == "OBJECT":  
        itemName = obj[1] + obj[2][0].name
        
      elif obj[0] == "COLLECTION":
        itemName = obj[1]
      
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
      if (self.__debug_export == True):
        bpy.ops.export_scene.fbx(check_existing=False, filepath=filePath, filter_glob="*.fbx",use_selection=True,use_armature_deform_only=True,
                              mesh_smooth_type=self.__context.scene.export_smoothing,add_leaf_bones=False,global_scale=self.__export_exportScale,bake_space_transform=self.__export_applyTransform,
                              use_mesh_modifiers=self.__export_applyModifiers,path_mode='ABSOLUTE')
    self.uncenterObjects()

  def centerObject(self, obj):
    #add object to list with name and old position
    if self.__center_transform:
      self.__obj_pos_list.append([obj, obj.location.copy()])
      obj.location = (0,0,0)

  def uncenterObjects(self):    
    #loop list and set object to old position
    for o in self.__obj_pos_list:
      o[0].location = o[1]