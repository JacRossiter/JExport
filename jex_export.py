import bpy
import os
import fnmatch
from .jex_utils import *

class Game_Exporter_Export:
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
        self.__item_list = []  # (custom type, colletion, object_list[], get_moved_BOOL)
        self.__obj_pos_list = []
        self.__should_delete_collections = True
        self.__collections_to_delete = []
        self.__exclude_character = "*"
        self.__merge_character = "&"
        self.__keep_duplicated = context.scene.debug_keep_duplicated
        print("----EXPORT INIT----")  # just see when this is called, safe to delete

    def export(self):
        self.start_export()
        self.do_export()
        self.post_export()

    def start_export(self):

        try:
            bpy.ops.object.mode_set(mode='OBJECT')
        except:
            print("must be in object mode to export")
            pass

        area = bpy.context.area.type  # do we need this
        bpy.context.area.type = 'VIEW_3D'

        self.set_empty_paths()

        if self.__export_target == 'OBJECT':
            self.create_object_list()

        elif self.__export_target == 'COLLECTION':
            self.create_collection_list()

        elif self.__export_target == 'BOTH':
            self.create_object_list()
            self.create_collection_list()

        bpy.context.area.type = area  # do we need this

    def do_export(self):
        item_name = ""
        file_name = ""
        folder_name = ""
        export_scale = self.__export_exportScale  # TODO this is not used

        for item in self.__item_list: # (custom type, collection, object_list[], get_moved_BOOL)
            print(item)
            # Deselect all objects
            bpy.ops.object.select_all(action='DESELECT')

            # prepare objects for export
            for o in item[2]:
                o.select_set(state=True)
                if item[3]:
                    self.center_objects(o)
                for child in get_children(item):  # TODO add bool
                    child.select_set(state=True)

            # Setup export file path
            if item[0] == "OBJECT":
                item_name = item[1] + item[2][0].name

            elif item[0] == "COLLECTION":
                item_name = item[1]

            item_name = self.remove_or_replace_characters(item_name)

            if "\\" in item_name:
                export_folder = self.__engine_folder + item_name.rsplit('\\', 1)[0] + "\\"
            else:
                export_folder = self.__engine_folder

            # Make folder
            try:
                os.makedirs(export_folder)
            except:
                pass

            # Do the actual export
            file_path = self.__engine_folder + item_name + ".fbx"
            print(file_path)
            if self.__debug_export:
                bpy.ops.export_scene.fbx(check_existing=False, filepath=file_path, filter_glob="*.fbx",
                                         use_selection=True, use_armature_deform_only=True,
                                         mesh_smooth_type=self.__context.scene.export_smoothing, add_leaf_bones=False,
                                         global_scale=self.__export_exportScale,
                                         bake_space_transform=self.__export_applyTransform,
                                         apply_scale_options='FBX_SCALE_ALL',
                                         use_mesh_modifiers=self.__export_applyModifiers, path_mode='ABSOLUTE')

    def post_export(self):
        self.uncenter_object()
        self.delete_collections()
        bpy.ops.object.select_all(action='DESELECT') #should reselect objects really        

    def set_empty_paths(self):
        if self.__engine_folder == "":
            self.__engine_folder = os.path.dirname(bpy.data.filepath) + "\\"
        if self.__bake_folder == "":
            self.__bake_folder = os.path.dirname(bpy.data.filepath) + "\\"

    def create_object_list(self):
        for obj in bpy.data.objects:
            # print(obj.users_collection[0].name)
            if obj.users_collection[0].name == "Master Collection":  # in base of scene
                if not self.valid_for_export(obj, False):
                    continue
                self.__item_list.append(["OBJECT", "", [obj], True])

    def create_collection_list(self):
        enabled_collections = []
        c = bpy.context.view_layer.layer_collection
        self.collections_recursive_with_limit(c, enabled_collections)

        col_list = []  # list of collections not layer collections
        for i in enabled_collections:
            col_list.append(i.collection)

        for col in col_list:
            if not self.valid_for_export(col, True):
                continue
            if self.treat_as_folder(col):
                for obj in col.objects:
                    self.__item_list.append(["OBJECT", col.name, [obj], True])
                    continue
            if self.__merge_character in col.name:  # actually make a duplicate collection here to merge into 1 mesh
                self.make_duplicates(col)
                continue
            self.__item_list.append(["COLLECTION", col.name, self.get_objects_in_collections(col), False])

    def make_duplicates(self, col):
        duplicated_col = self.duplicate_collection(col)
        obj_list = []
        for obj in duplicated_col.objects:
            obj_list.append(obj)
        self.duplicate_collections_recursive(col, duplicated_col, obj_list)        
        self.__item_list.append(["COLLECTION", duplicated_col.name, obj_list, False])

    def treat_as_folder(self, item):
        # export objects collections whos names end with \ or / to individual files
        if item.name[-1] == "\\" or item.name[-1] == "/":
            return True
        return False

    def valid_for_export(self, item, is_collection):
        if self.__exclude_character in item.name:
            return False
        if item.hide_viewport:
            return False
        if is_collection:
            """for o in bpy.context.view_layer.layer_collection.children:
                if o.collection == item:
                    if o.hide_viewport or o.exclude:
                        return False
            """                        
            return True
        else:
            for o in bpy.context.scene.objects:
                if o == item:
                    if o.hide_viewport:
                        return False
                    return True
        return False

    def remove_or_replace_characters(self, item_name):
        char_to_remove_list = ["&"]
        char_to_replace_list = [["/", "\\"]]
        for i in char_to_remove_list:
            if i in item_name:
                item_name = item_name.replace(i, "")
        for i in char_to_replace_list:
            if i[0] in item_name:
                item_name = item_name.replace(i[0], i[1])
        return item_name

    def center_objects(self, obj):
        if self.__center_transform:
            self.__obj_pos_list.append([obj, obj.location.copy()])
            obj.location = (0, 0, 0)

    def uncenter_object(self):
        for o in self.__obj_pos_list:
            o[0].location = o[1]

    def duplicate_collection(self, col):
        for obj in bpy.context.selected_objects:
            obj.select_set(False)
        if col.name == "Master Collection":
            return
        # if self.__merge_character not in col.name:
        #    return
        new_name = col.name.replace(self.__merge_character, "")
        new_collection = self.make_new_collection(new_name)
        for obj in col.objects:
            self.duplicate_object(obj, new_collection)
        for newObj in new_collection.objects:
            self.apply_modifiers(newObj)
            print(newObj)
            newObj.select_set(True)
        self.merge_objects(new_collection.name)
        self.__collections_to_delete.append(new_collection)
        return new_collection

    def make_new_collection(self, name):
        try:
            if bpy.data.collections[name]:
                target_collection = bpy.data.collections[name]
        except:
            target_collection = bpy.data.collections.new(name)
            bpy.context.scene.collection.children.link(target_collection)
        return target_collection

    def duplicate_object(self, obj, collection_name):
        if obj.type != "MESH":
            return
        if not self.valid_for_export(obj, False):
            return

        merge_prefix = "_M_"
        obj_data = obj.data.copy()
        new_obj = bpy.data.objects.new(merge_prefix + obj.name, obj_data)
        collection_name.objects.link(new_obj)

        new_obj.matrix_world = obj.matrix_world
        new_obj.rotation_euler = obj.rotation_euler

        for vertexGroup in obj.vertex_groups:
            new_obj.vertex_groups.new(vertexGroup.name)

        self.copy_modifier(obj, new_obj)

    def copy_modifier(self, source, target):
        active_object = source
        target_object = target

        for m_src in active_object.modifiers:
            m_dst = target_object.modifiers.get(m_src.name, None)
            if not m_dst:
                m_dst = target_object.modifiers.new(m_src.name, m_src.type)

            # collect names of writable properties
            properties = [p.identifier for p in m_src.bl_rna.properties
                          if not p.is_readonly]

            # copy those properties
            for prop in properties:
                setattr(m_dst, prop, getattr(m_src, prop))

    def apply_modifiers(self, ob):
        bpy.context.view_layer.objects.active = ob
        for mod in ob.modifiers:
            bpy.ops.object.modifier_apply(modifier=mod.name)

    def merge_objects(self, name):
        bpy.ops.object.join()
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        bpy.context.active_object.name = name

    def delete_collections(self):
        if self.__keep_duplicated:
            return
        for col in self.__collections_to_delete:
            for obj in col.objects:
                bpy.data.objects.remove(obj, do_unlink=True)
            bpy.data.collections.remove(col, do_unlink=True)

    def get_objects_in_collections(self, c):
        child_objects = []
        for obj in c.objects:
            child_objects.append(obj)
        print(c)
        print("!!!!!!!!!!!!!!!!!!!!!!!")
        for child_col in c.children:
            for obj in child_col.objects:
                child_objects.append(obj)

        return child_objects
    
    def collections_recursive(self, c, c_list):
        if not c.exclude:
            c_list.append(c)
        if c.children:
            for _c in c.children:
                self.collections_recursive(_c, c_list)
        else:
            return c_list

    def collections_recursive_with_limit(self, c, c_list):
        if not c.exclude and not c.hide_viewport:
            c_list.append(c)
        if c.children and self.__merge_character not in c.name and self.__exclude_character not in c.name:
            for _c in c.children:
                self.collections_recursive_with_limit(_c, c_list)
        else:
            return c_list

    def duplicate_collections_recursive(self, col, dup_col, obj_list):
        for c in col.children:
            if self.valid_for_export(c, True):
                dup_col.children.link(c)
                for obj in c.objects:
                    obj_list.append(obj)
            
