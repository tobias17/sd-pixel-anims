import bpy, math
from typing import List

class AnimToRender:
    def __init__(self, anim:str, save:str, frames:List[int], cam_rot=0):
        self.anim = anim
        self.save = save
        self.frames = frames
        self.cam_rot = cam_rot


##############################################
#                   SET ME                   #
OBJ_NAME = "witch_root"
#                                            #
CAMERA_OFFSET_X = 1.31
CAMERA_OFFSET_Y = 0.0
CAMERA_OFFSET_Z = 1.86
CAMERA_ROTATION_X = 45
CAMERA_ROTATION_Y = 0.0
CAMERA_ROTATION_Z = 90
#                                            #
anims_to_render: List[AnimToRender] = [
    AnimToRender(anim="idle",    save="//frames/idle_cam{camera}_anim{index}.png",      frames=[1], cam_rot=90),
    AnimToRender(anim="walk_f",  save="//frames/walk_dir0_cam{camera}_anim{index}.png", frames=[1, 6, 11, 17, 22, 27]),
    AnimToRender(anim="walk_fr", save="//frames/walk_dir1_cam{camera}_anim{index}.png", frames=[1, 6, 11, 17, 22, 27]),
    AnimToRender(anim="walk_r",  save="//frames/walk_dir2_cam{camera}_anim{index}.png", frames=[1, 6, 11, 17, 22, 27]),
    AnimToRender(anim="walk_br", save="//frames/walk_dir3_cam{camera}_anim{index}.png", frames=[1, 6, 11, 17, 22, 27]),
    AnimToRender(anim="walk_b",  save="//frames/walk_dir4_cam{camera}_anim{index}.png", frames=[1, 6, 11, 17, 22, 27]),
    AnimToRender(anim="walk_bl", save="//frames/walk_dir5_cam{camera}_anim{index}.png", frames=[1, 6, 11, 17, 22, 27]),
    AnimToRender(anim="walk_l",  save="//frames/walk_dir6_cam{camera}_anim{index}.png", frames=[1, 6, 11, 17, 22, 27]),
    AnimToRender(anim="walk_fl", save="//frames/walk_dir7_cam{camera}_anim{index}.png", frames=[1, 6, 11, 17, 22, 27]),
]
#
CAMERA_ONLY  = False
CAMERA_INDEX = 0
##############################################



def create_in_place_animation(obj, action_name):
    # Ensure the object has an action
    if obj.animation_data is None or obj.animation_data.action is None:
        print(f"Object {obj.name} has no animation data or action.")
        return
    bpy.context.scene.frame_set(0)
    obj.location = (0,0,0)

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
    bpy.context.view_layer.update()
    return True

def prepare_animation(obj, original_animation_name):
    inplace_animation_name = f"inplace_{original_animation_name}"
#    selected = select_animation(obj, inplace_animation_name)
#    if selected:
#        return
    
    selected = select_animation(obj, original_animation_name)
    if not selected:
        raise ValueError(f"Object did not have original_animation_name {original_animation_name}")
    create_in_place_animation(obj, inplace_animation_name)

def set_camera_position(px, py, pz, rx, ry, rz):
    camera = bpy.data.objects['Camera']
    camera.location = (px, py, pz)
    camera.rotation_euler = (math.radians(rx), math.radians(ry), math.radians(rz))

def render_frame(frame_number, filepath):
    bpy.context.scene.frame_set(frame_number)
    bpy.context.scene.render.filepath = filepath
    bpy.ops.render.render(write_still=True)

def main_loop():
    obj = bpy.data.objects.get(OBJ_NAME)
    if not obj:
        raise ValueError(f"Could not find a object named '{OBJ_NAME}', make sure you set OBJ_NAME in the script to your target object name")

    for anim_to_render in anims_to_render:
        prepare_animation(obj, anim_to_render.anim)
        for camera_i in range(8):
            angle_i = camera_i + (anim_to_render.cam_rot / 45)
            rad = -(angle_i / 4.0) * math.pi
            args = [
                CAMERA_OFFSET_X * math.cos(rad) + CAMERA_OFFSET_Y * math.sin(rad),
                CAMERA_OFFSET_Y * math.cos(rad) + CAMERA_OFFSET_X * math.sin(rad),
                CAMERA_OFFSET_Z,
                CAMERA_ROTATION_X,
                CAMERA_ROTATION_Y,
                CAMERA_ROTATION_Z + -angle_i*45,
            ]
            set_camera_position(*args)
            if CAMERA_ONLY:
                if camera_i == CAMERA_INDEX:
                    return
            else:
                for frame_i, frame_number in enumerate(anim_to_render.frames):
                    render_frame(frame_number, anim_to_render.save.format(camera=camera_i, index=frame_i))

main_loop()
