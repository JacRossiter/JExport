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
    self.__item_list = [] #(custom type, colletion, object_list[], get_moved_BOOL)
    self.__obj_pos_list = []
    self.__should_dete_collections = True
    self.__collections_to_delete = []
    self.__exclude_character = "*"
    self.__merge_character = "&"
    self.__keep_duplicated = context.scene.debug_keep_duplicated
    print("----EXPORT INIT----") #just see when this is called, safe to delete

  def export(self):
    self.startExport()
    self.doExport()
    self.postExport()

  def startExport(self):
    
    try:
      bpy.ops.object.mode_set(mode='OBJECT')
    except:
      print("must be in object mode to export")
      pass

    area = bpy.context.area.type # do we need this
    bpy.context.area.type = 'VIEW_3D'

    self.checkPaths()
      
    if self.__export_target == 'OBJECT':
      self.createObjectList()  

    elif self.__export_target == 'COLLECTION':
      self.createColletionList()

    elif self.__export_target == 'BOTH':
      self.createObjectList()
      self.createColletionList()

    bpy.context.area.type = area # do we need this

  def doExport(self):    
    itemName =""
    fileName = ""
    folderName = ""
    exportScale = self.__export_exportScale #TODO this is not used
    
    for item in self.__item_list:
      # Deselct all objects
      bpy.ops.object.select_all(action='DESELECT')      

      #prepare objects for export
      for o in item[2]:                
        o.select_set(state = True)
        if item[3] == True:
          self.centerObject(o)
        for child in get_children(item): # TODO add bool
          child.select_set(state=True)
      
      # Setup export file path
      if item[0] == "OBJECT":  
        itemName = item[1] + item[2][0].name
        
      elif item[0] == "COLLECTION":
        itemName = item[1]
      
      itemName = self.removeOrReplaceCharacters(itemName)
      
      if "\\" in itemName:
        exportFolder = self.__engine_folder + itemName.rsplit('\\', 1)[0] + "\\"
      else:
        exportFolder = self.__engine_folder
      
      # Make folder
      try:
        os.makedirs(exportFolder)
      except:
        pass
      
      # Do the actual export
      filePath = self.__engine_folder + itemName + ".fbx"
      print(filePath)
      if (self.__debug_export == True):
        bpy.ops.export_scene.fbx(check_existing=False, filepath=filePath, filter_glob="*.fbx",use_selection=True,use_armature_deform_only=True,
                              mesh_smooth_type=self.__context.scene.export_smoothing,add_leaf_bones=False,global_scale=self.__export_exportScale,bake_space_transform=self.__export_applyTransform,
                              apply_scale_options = 'FBX_SCALE_ALL',use_mesh_modifiers=self.__export_applyModifiers,path_mode='ABSOLUTE')  

  def postExport(self):
    self.uncenterObjects()
    self.deleteCollections()

  def checkPaths(self):
    if self.__engine_folder == "":
      self.__engine_folder = os.path.dirname(bpy.data.filepath) + "\\"
    if self.__bake_folder == "":
      self.__bake_folder = os.path.dirname(bpy.data.filepath) + "\\"

  def createObjectList(self):
    for obj in bpy.data.objects:
      if obj.users_collection[0].name == "Master Collection": #in base of scene
        if self.validForExport(obj) == False:          
          continue
        self.__item_list.append(["OBJECT", "", [obj], True]) 

  def createColletionList(self):
    for col in bpy.data.collections:
      if self.validForExport(col) == False:
        continue
      if self.treatAsFolder(col) == True:
        for obj in col.objects:
          self.__item_list.append(["OBJECT", col.name, [obj], True])
          continue
      if self.__merge_character in col.name: #actually make a duplicate collection here to merge into 1 mesh
        duplicatedCol = self.duplicateCollection(col)
        self.__item_list.append(["COLLECTION", duplicatedCol.name, duplicatedCol.objects, False])
        self.__collections_to_delete.append(duplicatedCol)
        continue
      self.getObectsInCollections(col)
      self.__item_list.append(["COLLECTION", col.name, col.objects, False])
  
  def treatAsFolder(self, item):
    #export objects collections whos names end with \ or / to individual files
    if item.name[-1] == "\\" or item.name[-1] == "/":
      return True
    return False

  def validForExport(self, item):
    if self.__exclude_character in item.name:
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
            return False
          return True
    except:
      pass
    return False

  def removeOrReplaceCharacters(self, itemName):
    charToRemoveList = ["&"]
    charToReplaceList = [["/","\\"]]
    
    for i in charToRemoveList:
      if i in itemName:
        itemName = itemName.replace(i,"")

    for i in charToReplaceList:
      if i[0] in itemName:
        itemName = itemName.replace(i[0],i[1])        
    
    return itemName

  def centerObject(self, obj):
    if self.__center_transform:
      self.__obj_pos_list.append([obj, obj.location.copy()])
      obj.location = (0,0,0)

  def uncenterObjects(self):    
    for o in self.__obj_pos_list:
      o[0].location = o[1]

  def duplicateCollection(self, col):
      for obj in bpy.context.selected_objects:
          obj.select_set(False)
      if col.name == "Master Collection":
          return
      #if self.__merge_character not in col.name:
      #    return
      newName = col.name.replace(self.__merge_character, "")
      newCollection = self.makeNewCollection(newName)
      for obj in col.objects:
          self.dupliateObject(obj, newCollection)
      for newObj in newCollection.objects:
          self.applyModifiers(newObj)
          newObj.select_set(True)
      self.mergeObjects(newCollection.name)
      return newCollection

  def makeNewCollection(self, name):
      try:
          if bpy.data.collections[name]:
              targetCollection = bpy.data.collections[name]
      except:
          targetCollection = bpy.data.collections.new(name)
          bpy.context.scene.collection.children.link(targetCollection)
      return targetCollection

  def dupliateObject(self, obj, collectionName):
      if obj.type != "MESH":
        return
      if self.validForExport(obj) == False:
        return
        
      mergePrefix = "_M_"
      objData = obj.data.copy()         
      newObj = bpy.data.objects.new(mergePrefix + obj.name, objData)   
      collectionName.objects.link(newObj) 

      newObj.matrix_world = obj.matrix_world                                        
      newObj.rotation_euler = obj.rotation_euler

      for vertexGroup in obj.vertex_groups:  
          newObj.vertex_groups.new(vertexGroup.name)

      self.copyModifier(obj,newObj)

  def copyModifier(self, source, target):
      active_object = source
      target_object = target

      for mSrc in active_object.modifiers:
          mDst = target_object.modifiers.get(mSrc.name, None)
          if not mDst:
              mDst = target_object.modifiers.new(mSrc.name, mSrc.type)

          # collect names of writable properties
          properties = [p.identifier for p in mSrc.bl_rna.properties
                        if not p.is_readonly]

          # copy those properties
          for prop in properties:
              setattr(mDst, prop, getattr(mSrc, prop))

  def applyModifiers(self, ob):    
      bpy.context.view_layer.objects.active = ob
      for mod in ob.modifiers:
          bpy.ops.object.modifier_apply(modifier = mod.name)

  def mergeObjects(self, name):
    bpy.ops.object.join()
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bpy.context.active_object.name = name

  def deleteCollections(self):
    if self.__keep_duplicated == True:
      return
    for col in self.__collections_to_delete:
      for obj in col.objects:
        bpy.data.objects.remove(obj, do_unlink=True)
      bpy.data.collections.remove(col, do_unlink=True)

  def getObectsInCollections(self, c):
    c_list = []
    objectList = self.collectionsRecursive(c, c_list)
    for o in objectList:
      print(o)

  def collectionsRecursive(self, c, c_list):    
    #if not c.exclude:
    c_list.append(c)
    if c.children:
        for _c in c.children:
            self.collectionsRecursive(_c, c_list)
    else:
        return c_list


  