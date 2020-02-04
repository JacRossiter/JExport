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
