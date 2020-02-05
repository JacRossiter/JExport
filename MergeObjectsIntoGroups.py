import bpy

def makeNewCollection(name):
    try:
        if bpy.data.collections[name]:
            targetCollection = bpy.data.collections[name]
    except:
        targetCollection = bpy.data.collections.new(name)
        scn.collection.children.link(targetCollection)
    return targetCollection

def dupliateObject(obj, collectionName):    
    
    objData = obj.data.copy()         
    newObj = bpy.data.objects.new(mergePrefix + obj.name, objData)   
    collectionName.objects.link(newObj) 

    newObj.matrix_world = obj.matrix_world                                        
    newObj.rotation_euler = obj.rotation_euler

    for vertexGroup in obj.vertex_groups:  
        newObj.vertex_groups.new(vertexGroup.name)

    copyModifier(obj,newObj)                        

def copyModifier(source, target):
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

def applyModifiers(ob):
    #would be better to do without bpy.ops

    bpy.context.view_layer.objects.active = ob
    for mod in ob.modifiers:
        bpy.ops.object.modifier_apply(modifier = mod.name)

scn = bpy.context.scene
objectsInGroup = []
groups = []
mergePrefix = "_MergeMe_"
collections = [bpy.context.collection]
collections = bpy.data.collections

for obj in bpy.context.selected_objects:
    obj.select_set(False)

for col in collections:
    if col.name == "Master Collection":
        continue
    if "&" not in col.name:
        continue
    newCollection = makeNewCollection(col.name + "_&&")    
    for obj in col.objects:
        dupliateObject(obj, newCollection)
    for newObj in newCollection.objects:
        applyModifiers(newObj)
        newObj.select_set(True)
    bpy.ops.object.join()
    bpy.context.active_object.name = col.name        