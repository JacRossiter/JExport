import bpy

# Get a copy of an object's location
def get_object_loc(obj):
  return obj.location.copy()

def get_children(obj): 
  children = [] 
  for ob in bpy.data.objects: 
      if ob.parent == obj: 
          children.append(ob) 
  return children 

def get_cursor_loc(context):
  return context.scene.cursor.location.copy()

def selected_to_cursor():
  bpy.ops.view3d.snap_selected_to_cursor()

def set_cursor_loc(context, loc : tuple):
  context.scene.cursor.location = loc

def do_center(self, obj):
  if self.__center_transform:
    loc = get_object_loc(obj)
    set_object_to_loc(obj, (0,0,0))
    return loc
  return None

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