import bpy

def generate_frequency_list(num_of_bands: int) -> list:
    ret_list = []
    noteStep = 120.0/num_of_bands
    a = 2**(1.0/12.0)
    current_freq = 16.0
    ret_list.append(0.0)
    for i in range(0, num_of_bands):
        current_freq = current_freq * (a ** noteStep)
        ret_list.append(current_freq)
    return ret_list

def create_new_visualizer_armature(bands_n: int) -> bpy.types.Object:
    objs, armatures, col = bpy.data.objects, bpy.data.armatures, bpy.context.scene.collection
    armature: bpy.types.Armature = armatures.new(name = 'Test Armature')
    armature_obj: bpy.types.Object = objs.new(name = 'Test Obj', object_data = armature)
    col.objects.link(armature_obj) #Linking the object to the scene collection. Unlinked by default.
    #bpy.ops.object.mode_set(mode='OBJECT')
    bpy.context.view_layer.objects.active = armature_obj #Setting the active object
    bpy.ops.object.mode_set(mode='EDIT') #Going into edit mode to get edit bones. Can only create new edit bones.
    armature_e_bones: bpy.types.ArmatureEditBones = armature.edit_bones
    base_bone: bpy.types.EditBone = armature_e_bones.new('Base Bone')
    base_bone.tail,base_bone.head = (0,0,1),(0,0,0)
    x_pos = -bands_n/2 + 0.5
    for i in range(bands_n):
        new_bone = armature_e_bones.new(f'Band.{str(i).zfill(3)}')
        new_bone.tail,new_bone.head = (x_pos,0,2),(x_pos,0,1)
        x_pos += 1
    bpy.ops.object.mode_set(mode='OBJECT')
    return armature_obj

def clear_keyframes_bone(bone: bpy.types.Bone, action: bpy.types.Action | None) -> None:
    if action:
        for fcurve in action.fcurves:
            if bone.name in fcurve.data_path:
                action.fcurves.remove(fcurve)

def add_y_kf_for_bone(bone: bpy.types.Bone, action: bpy.types.Action | None) -> bpy.types.FCurve:
    fcurves = action.fcurves
    curve = fcurves.new(data_path = f'pose.bones["{bone.name}"].location', index = 1)
    return curve

class SoundVisualizer(bpy.types.Operator):
    """
    Generates fcurves to sync with a provided 
    """
    bl_idname = "object.soundvisualizer"
    bl_label = "Sound Visualizer"
    def execute(self,context):
        file_path = context.scene.file_path
        context.scene.frame_set(1)
        old_area_type = context.area.type
        freq_bands = generate_frequency_list(num_of_bands = context.scene.num_of_bands)
        armature_obj = create_new_visualizer_armature(bands_n = context.scene.num_of_bands)
        bpy.ops.object.mode_set(mode='POSE')
        armature_obj.keyframe_insert('location', frame = 1)
#        if armature_obj:
#            if armature_obj.type == 'ARMATURE':
        area = context.area
        area.type = 'GRAPH_EDITOR' #Only area this works
        armature: bpy.types.Armature = armature_obj.data
        anim_data: bpy.types.AnimData | None = armature_obj.animation_data
        if anim_data: action = anim_data.action
        else: action = None
        band_bones: list[bpy.types.Bone] = [bone for bone in armature.bones if 'Band' in bone.name] #Get bones with 'Band' in their name
        band_bones.sort(key = lambda bone: bone.name) #Sort by name. Name implies frequency band.
        #Bones assume to start at 1.
        for band_bone in band_bones: 
            armature.bones.active = band_bone
            clear_keyframes_bone(bone = band_bone, action = action) #Removing old keyframes
            add_y_kf_for_bone(bone = band_bone, action = action) #Adding template
        for fcurve in context.editable_fcurves: fcurve.select = False
        editable_fcurves_dict = {fcurve.data_path: fcurve for fcurve in context.editable_fcurves}
        for band_bone in band_bones:
            editable_fcurves_dict[f'pose.bones["{band_bone.name}"].location'].select = True
            index = int(band_bone.name[5:])
#            low_freq, high_freq = freq_bands[index - 1], freq_bands[index]
            low_freq, high_freq = freq_bands[index], freq_bands[index + 1]
            print(f'Baking frequencies ({low_freq}) to ({high_freq}) to bone: {band_bone.name}')
            bpy.ops.graph.sound_to_samples(filepath = file_path, 
                                           low = low_freq, high = high_freq)
            for fcurve in context.editable_fcurves: fcurve.select = False
        area.type = old_area_type
        bpy.ops.object.mode_set(mode='OBJECT')
        return {'FINISHED'}

class TestPanel(bpy.types.Panel):
    bl_label = "Test Panel"
    bl_idname = "Test Panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bpy.types.Scene.file_path = bpy.props.StringProperty(name = "File Path", description="Audio File:", subtype='FILE_PATH')
    bpy.types.Scene.num_of_bands = bpy.props.IntProperty(name = 'Band Amount', default = 10, soft_min = 1)
    def draw(self, context):
        scene = context.scene
        layout = self.layout
        row = layout.row(); row.prop(scene,'file_path')
        row = layout.row(); row.prop(scene,'num_of_bands')
        row = layout.row(); row.operator("object.soundvisualizer")
    
operators = [SoundVisualizer]

panels = [TestPanel]

def register():
    for op in operators:
        bpy.utils.register_class(op)
    for panel in panels:
        bpy.utils.register_class(panel)
        

if __name__ == '__main__':
    register()
    
