import bpy, os

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
        new_bone = armature_e_bones.new(f'Band{str(i).zfill(3)}')
        new_bone.tail,new_bone.head = (x_pos,0,2),(x_pos,0,1)
        x_pos += 1
    bpy.ops.object.mode_set(mode='OBJECT')
    return armature_obj

def clear_keyframes_bone(bone: bpy.types.Bone, action: bpy.types.Action | None) -> None:
    if action:
        for fcurve in action.fcurves:
            if bone.name in fcurve.data_path:
                action.fcurves.remove(fcurve)

def add_y_kf_for_bone(bone: bpy.types.Bone, action: bpy.types.Action) -> bpy.types.FCurve:
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
        scene = context.scene
        file_path, old_area_type, use_active = scene.file_path, context.area.type, scene.use_active
        file_name = os.path.basename(file_path)
        area = context.area
        context.scene.frame_set(1)
        if use_active: 
            armature_obj: bpy.types.Object | None = context.active_object
            assert armature_obj, 'There is no active object!'
            assert armature_obj.type == 'ARMATURE', 'Active object is not an armature!'
            print(f'\nBaking song to active object: {armature_obj.name}')
        else: 
            armature_obj: bpy.types.Object = create_new_visualizer_armature(bands_n = context.scene.num_of_bands)
            print(f'\nBaking song to new object: {armature_obj.name}')
        armature: bpy.types.Armature = armature_obj.data
        band_bones: list[bpy.types.Bone] = [bone for bone in armature.bones if 'Band' in bone.name] #Get bones with 'Band' in their name
        freq_bands = generate_frequency_list(num_of_bands = len(band_bones))
        #Setting action.
        action_name = f'{str(len(band_bones)).zfill(3)}-{file_name}'
        action = bpy.data.actions.get(action_name)
        if not action: action = bpy.data.actions.new(os.path.basename(action_name))
        if not armature_obj.animation_data: armature_obj.animation_data_create()
        armature_obj.animation_data.action = action
        #Verify that the fcurves are editable by selecting the bones.
        bpy.context.view_layer.objects.active = armature_obj #Setting the active object
        bpy.ops.object.mode_set(mode='POSE')
        for bone in band_bones: bone.select = True
        #
        armature_obj.keyframe_insert('location', frame = 1)
        area.type = 'GRAPH_EDITOR' #Only area this works
        #Bones assume to start at 0.
        for band_bone in band_bones: 
            armature.bones.active = band_bone
            clear_keyframes_bone(bone = band_bone, action = action) #Removing old keyframes
            add_y_kf_for_bone(bone = band_bone, action = action) #Adding template
        editable_fcurves_dict = {fcurve.data_path: fcurve for fcurve in context.editable_fcurves}
        for fcurve in context.editable_fcurves: fcurve.select = False
        for band_bone in band_bones:
            editable_fcurves_dict[f'pose.bones["{band_bone.name}"].location'].select = True
            index = int(band_bone.name[4:])
#            low_freq, high_freq = freq_bands[index - 1], freq_bands[index]
            low_freq, high_freq = freq_bands[index], freq_bands[index + 1]
            print(f'\tBaking frequencies ({low_freq}) to ({high_freq}) to bone: {band_bone.name}')
            bpy.ops.graph.sound_to_samples(filepath = file_path, 
                                           low = low_freq, high = high_freq)
            for fcurve in context.editable_fcurves: fcurve.select = False
        area.type = old_area_type
        bpy.ops.object.mode_set(mode='OBJECT')
        if scene.add_audio:
            if not scene.sequence_editor:
                scene.sequence_editor_create() 
            sequences = scene.sequence_editor.sequences
            for sequence in sequences: #Get rid of old ones.
                if sequence.name != file_name: sequence.volume = 0
                else: sequence.volume = 1
            sequence_names = [sequence.name for sequence in sequences]
            if file_name not in sequence_names:
                print(f'Adding song ({file_name}) to sequencer')
                soundstrip = sequences.new_sound(file_name, file_path, 0, 0)
        print('Done!')
        return {'FINISHED'}

def get_actions(scene,context) -> list[tuple[str,str,str]]:
    obj = context.active_object
    if obj and obj.type == 'ARMATURE':
        song_actions = []
        for action in bpy.data.actions:
            try: int(action.name[:3])
            except: pass
            else: song_actions.append(action)
        armature = obj.data
        band_bones: list[bpy.types.Bone] = [bone for bone in armature.bones if 'Band' in bone.name] #Get bones with 'Band' in their name
        bones_n = len(band_bones)
        if band_bones and song_actions:
            return [(action.name,action.name,action.name) for action in song_actions if int(action.name[:3]) == bones_n]
        else: return[('N/A','N/A','N/A')]
    else: return[('N/A','N/A','N/A')]

class ActionSelector(bpy.types.Operator):
    """
    Sets selected action to be active and unmutes the song if present.
    """
    bl_idname = "object.selectaction"
    bl_label = "Action and Sound Selector"
    def execute(self,context):
        scene,obj = context.scene,context.active_object
        action_name = scene.available_action_enum
        action = bpy.data.actions.get(action_name)
        context.scene.frame_set(1)
        song_name = action_name[4:]
        if obj.type == 'ARMATURE':
            obj.animation_data.action = action
            for sequence in scene.sequence_editor.sequences:
                if sequence.name != song_name: sequence.volume = 0
                else: sequence.volume = 1
        return {'FINISHED'}
    
class TestPanel(bpy.types.Panel):
    bl_label = "Rigualizer"
    bl_idname = "Rigualizer"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bpy.types.Scene.file_path = bpy.props.StringProperty(name = "File Path", description="Audio File:", subtype='FILE_PATH')
    bpy.types.Scene.num_of_bands = bpy.props.IntProperty(name = 'Band Amount', default = 10, soft_min = 1)
    bpy.types.Scene.use_active = bpy.props.BoolProperty(name = 'Use Active', description = 'Adds a new action to the active object')
    bpy.types.Scene.add_audio = bpy.props.BoolProperty(name = 'Add Audio', description = f'Mutes all songs in the sequencer and adds it to the sequence.\nAllows you to hear the song when running the animation')
    bpy.types.Scene.available_action_enum = bpy.props.EnumProperty(items = get_actions, name = 'Selected Action', description = 'Gets all actions with the corresponding amount of bones.')
    def draw(self, context):
        scene = context.scene
        layout = self.layout
        row = layout.row(); row.prop(scene,'file_path')
        row = layout.row(); row.prop(scene,'use_active'); row.prop(scene,'add_audio')
        if not scene.use_active:
            row = layout.row(); row.prop(scene,'num_of_bands')
        row = layout.row(); row.operator("object.soundvisualizer")
        row = layout.row(); row.prop(scene,'available_action_enum')
        row = layout.row(); row.operator("object.selectaction")
        
    
operators = [SoundVisualizer,ActionSelector]

panels = [TestPanel]

def register():
    for op in operators:
        bpy.utils.register_class(op)
    for panel in panels:
        bpy.utils.register_class(panel)
        
if __name__ == '__main__':
    register()
    
