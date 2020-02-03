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

  def export(self):    
    itemName =""
    fileName = ""
    folderName = ""

    exportScale = self.__export_exportScale #TODO this is not used
    
    if self.__export_type == 'BAKE':
      exportFolder = self.__bake_folder
      exportScale = self.__export_exportScale/100 #why 100

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

  def create_collection_list(self):
    for col in bpy.data.collections:
      if col.name[-1] == "\\" or col.name[-1] == "/": #export objects collections whos names end with \ or / to individual files
        for obj in col.objects:
          self.__obj_list.append(["OBJECT", col, [obj], True])
      else:
        self.__obj_list.append(["COLLECTION", col, col.objects, False])

  def create_object_list(self):    
    for obj in bpy.data.objects:
      if obj.users_collection[0].name == "Master Collection": #in base of scene
        self.__obj_list.append(["OBJECT", "", [obj], True]) 

  def create_collection_list_old(self):
    enabled_collections = []
    export_list = []

    #make a list of all enabled collections #TODO add to ui
    c = bpy.context.view_layer.layer_collection
    self.collections_recursive(c, enabled_collections)

    # unhides all collections
    for collection in enabled_collections: 
      collection.hide_viewport = False
    bpy.ops.object.hide_view_clear()

    # Engine Settings list creator
    if self.__export_type == 'ENGINE':
      for c in enabled_collections:
        if fnmatch.fnmatch(c.name, "SM_*"):
            if c.has_objects():
                export_list.append(c)

    # Bake Settings list creator
    #elif self.__export_type == 'BAKE':     
    #  for c in enabled_collections:
    #    if fnmatch.fnmatch(c.name, "*_low") or fnmatch.fnmatch(c.name, "*_high"):
    #        if c.has_objects():
    #            export_list.append(c)
    
    # Selects Objects in Collection
    for c in export_list:
      # Deselect all objcets
      bpy.ops.object.select_all(action='DESELECT')
      print('deselecting all')
      
      # Select the ones we want in a collection
      for obj in c.collection.all_objects:
        obj.select_set(state = True)  
        print('selecting', obj.name)
      
      # Set export name to be collection name
      export_name = c.name
      if self.__export_prefix == False:
        export_name = c.name.replace('SM_', '')
        print('exporting ',export_name)

      bpy.ops.export_scene.fbx(check_existing=False, filepath=exportfolder + export_name + ".fbx", filter_glob="*.fbx",use_selection=True,use_armature_deform_only=True,
      mesh_smooth_type=self.__context.scene.export_smoothing,add_leaf_bones=False,global_scale=exportscale,bake_space_transform=self.__export_applyTransform,
      use_mesh_modifiers=self.__export_applyModifiers,path_mode='ABSOLUTE')
      print('export complete')    

  def center_object(self, obj):
    #add object to list with name and old position
    if self.__center_transform:
      self.__obj_pos_list.append([obj, obj.location.copy()])
      obj.location = (0,0,0)

  def uncenter_objects(self):    
    #loop list and set object to old position
    for o in self.__obj_pos_list:
      o[0].location = o[1]    
      
  def collections_recursive(self, c, c_list):    
    if not c.exclude:
        c_list.append(c)
    if c.children:
        for _c in c.children:
            self.collections_recursive(_c, c_list)
    else:
        return c_list
  
  def do_center(self, obj):
    if self.__center_transform:
      loc = get_object_loc(obj)
      set_object_to_loc(obj, (0,0,0))
      return loc
    return None

  def create_object_list_old(self):
    print("exporting objects")

    # unhides all collections
    for collection in bpy.context.view_layer.layer_collection.children: # unhides all collections
      collection.hide_viewport = False
    bpy.ops.object.hide_view_clear()

    # Bake Settings  list creator
    if self.__export_type == 'BAKE':    
      self.__obj_list = [obj for obj in bpy.context.visible_objects if fnmatch.fnmatch(obj.name, "*_low") or fnmatch.fnmatch(obj.name, "*_high")]
      print(self.__obj_list)

    # Engine Settings list creator
    elif self.__export_type == 'ENGINE':
      self.__obj_list = [obj for obj in bpy.context.visible_objects if fnmatch.fnmatch(obj.name, "SM_*")]
      print(self.__obj_list)

  def export_old(self):
    for obj in self.__obj_list:
      # Get correct objects selected
      bpy.ops.object.select_all(action='DESELECT')      
      for o in obj[1]:
        o.select_set(state = True)

      # Center selected object
      old_pos = self.do_center(obj)

      # Select children if exist
      for child in get_children(obj):
        child.select_set(state=True)
      
      # Setup Export Folder     
      exportfolder =  self.__engine_folder + obj.users_collection[0].name + "/"
      exportscale = self.__export_exportScale
      if self.__export_type == 'BAKE':
        exportfolder = self.__bake_folder + "/"
        exportscale = self.__export_exportScale/100 #why 100
      
      try:
        os.makedirs(exportfolder)
      except:
        pass

      # Deal with prefex names
      export_name = obj.name
      if self.__export_prefix == False:
        export_name = obj.name.replace('SM_', '')

      # Do the actual export
      bpy.ops.export_scene.fbx(check_existing=False, filepath=exportfolder + export_name + ".fbx", filter_glob="*.fbx",use_selection=True,use_armature_deform_only=True,
      mesh_smooth_type=self.__context.scene.export_smoothing,add_leaf_bones=False,global_scale=self.__export_exportScale,bake_space_transform=self.__export_applyTransform,
      use_mesh_modifiers=self.__export_applyModifiers,path_mode='ABSOLUTE')

      # Return object to old position 
      if old_pos is not None:
        set_object_to_loc(obj, old_pos)      

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

