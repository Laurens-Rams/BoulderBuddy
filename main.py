import bpy
import json


def import_fbx(fbx_path):
    bpy.ops.import_scene.fbx(filepath=fbx_path)

def set_frame_range():
    # Set specific frame range
    bpy.context.scene.frame_start = 5
    bpy.context.scene.frame_end = 1600

def analyze_armature(armature_name, joints_names):
    data = {}
    armature = bpy.context.scene.objects.get(armature_name)

    if armature:
        bpy.context.view_layer.objects.active = armature
        bpy.ops.object.mode_set(mode='POSE')

        for bone in armature.pose.bones:
            if bone.name in joints_names:
                data[bone.name] = []
                for frame in range(bpy.context.scene.frame_start, bpy.context.scene.frame_end + 1):
                    bpy.context.scene.frame_set(frame)
                    data[bone.name].append({
                        'frame': frame,
                        'position': list(bone.head.xyz),
                    })

    return data


def export_to_json(data, file_path):
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)


def output_bones(armature_name):
    bone_names = []
    armature = bpy.context.scene.objects.get(armature_name)

    if armature:
        bpy.context.view_layer.objects.active = armature
        bpy.ops.object.mode_set(mode='POSE')

        for bone in armature.pose.bones:
            bone_names.append(bone.name)

    return bone_names

def main():
    fbx_file_path = '/Users/laurensart/Dropbox/Laurens/Move-One-Import/move-four.fbx'
    output_file_path = '/Users/laurensart/Dropbox/Laurens/Move-One-Import/output.json'
    output_file_path_bones = '/Users/laurensart/Dropbox/Laurens/Move-One-Import/output-bones.json'
    armature_name = "Armature"
    joints_names = [
        "_1:Hips",
        "_1:Spine",
        "_1:Spine1",
        "_1:Neck",
        "_1:Head",
        "_1:RightShoulder",
        "_1:RightArm",
        "_1:RightForeArm",
        "_1:RightHand",
        "_1:LeftShoulder",
        "_1:LeftArm",
        "_1:LeftForeArm",
        "_1:LeftHand",
        "_1:RightUpLeg",
        "_1:RightLeg",
        "_1:RightFoot",
        "_1:LeftUpLeg",
        "_1:LeftLeg",
        "_1:LeftFoot"
    ]

    import_fbx(fbx_file_path)
    set_frame_range()
    armature_data = analyze_armature(armature_name, joints_names)
    export_to_json(armature_data, output_file_path)

    bone_names = output_bones(armature_name)
    export_to_json(bone_names, output_file_path_bones)


if __name__ == "__main__":
    main()