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
    self.__export_objects = context.selected_objects
    self.__export_target = context.scene.export_target
    self.__export_type = context.scene.export_type
    self.__texture_type = context.scene.texture_type
  
  def do_center(self, obj):
    if self.__center_transform:
      loc = get_object_loc(obj)
      set_object_to_loc(obj, (0,0,0))
      return loc

    return None

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
    
  def collections_recursive(self, c, c_list):
    if not c.exclude:
        c_list.append(c)
    if c.children:
        for _c in c.children:
            self.collections_recursive(_c, c_list)
    else:
        return c_list

  def do_export(self):
    try:
      bpy.ops.object.mode_set(mode='OBJECT')
    except:
      pass

    obj = bpy.context.view_layer.objects.active
    bakefolder = self.__bake_folder + "/"
    enginefolder = self.__engine_folder 

    area = bpy.context.area.type
    bpy.context.area.type = 'VIEW_3D'

    # Export SM_ objects
    if self.__export_target == 'OBJECT':
      print("exporting objects")

      # unhides all collections
      for collection in bpy.context.view_layer.layer_collection.children: # unhides all collections
        collection.hide_viewport = False
      bpy.ops.object.hide_view_clear()

      # Bake Settings
      if self.__export_type == 'BAKE':
        print("Bake Mode")
        if "../" or "..\\" or "//" in bakefolder:
          filepath = bpy.data.filepath + "\\..\\"
          exportfolder = os.path.dirname(filepath + bakefolder + "\\")
        else:
          exportfolder = bakefolder
          try:
            os.makedirs(exportfolder)
          except:
            pass
        exportscale = self.__export_exportScale/100
        
        obj_list = [obj for obj in bpy.context.visible_objects if fnmatch.fnmatch(obj.name, "*_low") or fnmatch.fnmatch(obj.name, "*_high")]
        print(obj_list)

      # Engine Settings
      elif self.__export_type == 'ENGINE':
        print("Engine Mode")
        if "../" or "..\\" or "//" in enginefolder:
          filepath = bpy.data.filepath + "\\..\\"
          exportfolder = os.path.dirname(filepath + enginefolder + "\\")
        else:
          exportfolder = enginefolder
          try:
            os.makedirs(exportfolder)
          except:
            pass
        exportscale = self.__export_exportScale

        obj_list = [obj for obj in bpy.context.visible_objects if fnmatch.fnmatch(obj.name, "SM_*")]
        print(obj_list)
      # SM_ objects to engine
      for obj in obj_list:
        print(obj.name)
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(state = True)

        # Center selected object
        old_pos = self.do_center(obj)

        # Select children if exist
        for child in get_children(obj):
          child.select_set(state=True)
        
        if "../" or "..\\" or "//" in enginefolder:
          filepath = bpy.data.filepath + "\\..\\"
          exportfolder = os.path.dirname(filepath + enginefolder + "\\")
        else:
          exportfolder = enginefolder
          try:
            os.makedirs(exportfolder)
          except:
            pass

        export_name = obj.name
        if self.__export_prefix == False:
          obj.name = obj.name.replace('SM_', '')

          bpy.ops.export_scene.fbx(check_existing=False, filepath=exportfolder + "/" + obj.name + ".fbx", filter_glob="*.fbx",use_selection=True,use_armature_deform_only=True,
          mesh_smooth_type=self.__context.scene.export_smoothing,add_leaf_bones=False,global_scale=exportscale,bake_space_transform=self.__export_applyTransform,
          use_mesh_modifiers=self.__export_applyModifiers,path_mode='ABSOLUTE')

          obj.name = "SM_" + obj.name

        else:
          bpy.ops.export_scene.fbx(check_existing=False, filepath=exportfolder + "/" + export_name + ".fbx", filter_glob="*.fbx",use_selection=True,use_armature_deform_only=True,
          mesh_smooth_type=self.__context.scene.export_smoothing,add_leaf_bones=False,global_scale=exportscale,bake_space_transform=self.__export_applyTransform,
          use_mesh_modifiers=self.__export_applyModifiers,path_mode='ABSOLUTE')

        if old_pos is not None:
          set_object_to_loc(obj, old_pos)

        bpy.context.area.type = area

    # Export SM_ collections
    elif self.__export_target == 'COLLECTION':
      enabled_collections = []
      export_list = []

      c = bpy.context.view_layer.layer_collection
      self.collections_recursive(c, enabled_collections)

      for collection in enabled_collections: # unhides all collections
        collection.hide_viewport = False
      bpy.ops.object.hide_view_clear()

      # Bake Settings
      if self.__export_type == 'BAKE':
        if "../" or "..\\" or "//" in bakefolder:
          filepath = bpy.data.filepath + "\\..\\"
          exportfolder = os.path.dirname(filepath + bakefolder + "\\")
        else:
          exportfolder = bakefolder
          try:
            os.makedirs(exportfolder)
          except:
            pass
        exportscale = self.__export_exportScale/100
        
        for c in enabled_collections:
          if fnmatch.fnmatch(c.name, "*_low") or fnmatch.fnmatch(c.name, "*_high"):
              if c.has_objects():
                  export_list.append(c)

      # Engine Settings
      elif self.__export_type == 'ENGINE':
        if "../" or "..\\" or "//" in enginefolder:
          filepath = bpy.data.filepath + "\\..\\"
          exportfolder = os.path.dirname(filepath + enginefolder)
        else:
          exportfolder = enginefolder
          try:
            os.makedirs(exportfolder)
          except:
            pass
        exportscale = self.__export_exportScale

        print('generating export list')
        for c in enabled_collections:
          if fnmatch.fnmatch(c.name, "SM_*"):
              if c.has_objects():
                  export_list.append(c)

      for c in export_list:
        bpy.ops.object.select_all(action='DESELECT')
        print('deselecting all')
        # Selects Objects in Collection
        
        for obj in c.collection.all_objects:
          obj.select_set(state = True)  
          print('selecting', obj.name)

        print(bpy.context.selected_objects)
        
        export_name = c.name
        if self.__export_prefix == False:
          export_name = c.name.replace('SM_', '')
          print('exporting ',export_name)

        bpy.ops.export_scene.fbx(check_existing=False, filepath=exportfolder + "/" + export_name + ".fbx", filter_glob="*.fbx",use_selection=True,use_armature_deform_only=True,
        mesh_smooth_type=self.__context.scene.export_smoothing,add_leaf_bones=False,global_scale=exportscale,bake_space_transform=self.__export_applyTransform,
        use_mesh_modifiers=self.__export_applyModifiers,path_mode='ABSOLUTE')
        print('export complete')
        
        bpy.context.area.type = area
print('---------------------------------------')

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

