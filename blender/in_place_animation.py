import bpy
import mathutils

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
    print(f"Frame range: [{start_frame}, {end_frame}]")

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

    # Calculate the position delta
    delta_pos = end_pos - start_pos
    print(f"delta_pos: {delta_pos}")

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
    obj.animation_data.action = original_action
    track = obj.animation_data.nla_tracks.new()
    track.strips.new(name=original_action.name, start=start_frame, action=original_action)
    
    track = obj.animation_data.nla_tracks.new()
    track.strips.new(name=new_action.name, start=start_frame, action=new_action)

    # Update the scene
    bpy.context.view_layer.update()

# Example usage
obj = bpy.context.active_object
create_in_place_animation(obj, "InPlaceAnimation")
