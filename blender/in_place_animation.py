import bpy

CAMERA_OFFSET_X = 1.31
CAMERA_OFFSET_Y = 0.0
CAMERA_OFFSET_Z = 1.61

CAMERA_ROTATION_X = 45
CAMERA_ROTATION_Y = 0.0
CAMERA_ROTATION_Z = 90

def create_in_place_animation(obj, action_name):
    # Ensure the object has an action
    if obj.animation_data is None or obj.animation_data.action is None:
        print(f"Object {obj.name} has no animation data or action.")
        return

    original_action = obj.animation_data.action
    
    # Find the first and last keyframe of the original animation
    fcurves = original_action.fcurves
    frame_range = [int(fcurve.range()[0]) for fcurve in fcurves] + [int(fcurve.range()[1]) for fcurve in fcurves]
    start_frame, end_frame = min(frame_range), max(frame_range)

    # Get the root bone (assuming it's the first bone in the armature)
    root_bone = obj.data.bones[0]
    
    # Function to get root bone's world position
    def get_root_bone_world_pos():
        if obj.pose.bones:
            return obj.matrix_world @ obj.pose.bones[root_bone.name].matrix.to_translation()
        return obj.matrix_world @ root_bone.matrix_local.to_translation()

    # Get the root bone's position at the start and end frames
    bpy.context.scene.frame_set(start_frame)
    start_pos = get_root_bone_world_pos()
    bpy.context.scene.frame_set(end_frame)
    end_pos = get_root_bone_world_pos()
    delta_pos = end_pos - start_pos

    # Create a new action for the global position animation
    new_action = bpy.data.actions.new(name=action_name)
    obj.animation_data.action = new_action

    # Create F-Curves for X, Y, Z location
    fc_x = new_action.fcurves.new(data_path="location", index=0)
    fc_y = new_action.fcurves.new(data_path="location", index=1)
    fc_z = new_action.fcurves.new(data_path="location", index=2)

    # Add keyframes to create a linear interpolation
    fc_x.keyframe_points.insert(start_frame, 0)
    fc_y.keyframe_points.insert(start_frame, 0)
    fc_z.keyframe_points.insert(start_frame, 0)

    fc_x.keyframe_points.insert(end_frame, -delta_pos.x)
    fc_y.keyframe_points.insert(end_frame, -delta_pos.y)
    fc_z.keyframe_points.insert(end_frame, -delta_pos.z)

    # Set interpolation to linear
    for fc in (fc_x, fc_y, fc_z):
        for kp in fc.keyframe_points:
            kp.interpolation = 'LINEAR'

    # Combine the original action with the new global position action
    track = obj.animation_data.nla_tracks.new()
    track.strips.new(name=original_action.name, start=start_frame, action=original_action)

    # Update the scene
    bpy.context.view_layer.update()

def select_animation(obj, animation_name):
    # Check if the object has animation data
    if obj.animation_data is None:
        obj.animation_data_create()
    
    # Find the action with the given name
    action = bpy.data.actions.get(animation_name)
    
    if action is None:
        print(f"Animation '{animation_name}' not found.")
        return False
    
    # Assign the action to the object
    obj.animation_data.action = action
    print(f"Selected animation '{animation_name}' for object '{obj.name}'.")
    return True

def prepare_animation(obj, original_animation_name):
    inplace_animation_name = f"inplace_{original_animation_name}"
    selected = select_animation(obj, inplace_animation_name)
    if selected:
        return
    
    selected = select_animation(obj, original_animation_name)
    if not selected:
        raise ValueError(f"Object did not have original_animation_name {original_animation_name}")
    create_in_place_animation(obj, inplace_animation_name)

obj = bpy.context.active_object
prepare_animation(obj, "walk_back")
