import bpy
import csv

def import_fbx(fbx_path):
    bpy.ops.import_scene.fbx(filepath=fbx_path)

def set_frame_range():
    bpy.context.scene.frame_start = 50
    bpy.context.scene.frame_end = 1600

def analyze_armature(armature_name, joints_names):
    data = []
    armature = bpy.context.scene.objects.get(armature_name)

    if armature:
        bpy.context.view_layer.objects.active = armature
        bpy.ops.object.mode_set(mode='POSE')

        for frame in range(bpy.context.scene.frame_start, bpy.context.scene.frame_end + 1):
            bpy.context.scene.frame_set(frame)  # Set the current frame
            frame_data = {'frame': frame}
            for bone in armature.pose.bones:
                if bone.name in joints_names:
                    frame_data[f'{bone.name}_x'] = bone.head.x
                    frame_data[f'{bone.name}_y'] = bone.head.y
                    frame_data[f'{bone.name}_z'] = bone.head.z
            data.append(frame_data)

    return data

def export_to_csv(data, file_path):
    with open(file_path, mode='w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)

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
    fbx_file_path = 'fbx_files/move-four.fbx'
    output_file_path_csv = '/Users/laurensart/Dropbox/Laurens/Move-One-Import/Move_4.csv'
    armature_name = "Armature"
    joints_names = [
        "_1:Root",
        "_1:Hips",
        "_1:Spine",
        "_1:Spine1",
        "_1:Neck",
        "_1:Head",
        "_1:RightShoulder",
        "_1:RightArm",
        "_1:RightForeArm",
        "_1:RightHand",
        "_1:RightUpLeg",
        "_1:RightLeg",
        "_1:RightFoot",
        "_1:RightToeBase",
        "_1:LeftShoulder",
        "_1:LeftArm",
        "_1:LeftForeArm",
        "_1:LeftHand",
        "_1:LeftUpLeg",
        "_1:LeftLeg",
        "_1:LeftFoot",
        "_1:LeftToeBase",
        "_1:RightHandThumb1",
        "_1:RightHandThumb2",
        "_1:RightHandIndex1",
        "_1:RightHandMiddle1",
        "_1:RightHandRing1",
        "_1:RightHandPinky1",
        "_1:LeftHandThumb1",
        "_1:LeftHandThumb2",
        "_1:LeftHandIndex1",
        "_1:LeftHandMiddle1",
        "_1:LeftHandRing1",
        "_1:LeftHandPinky1",
        "_1:heel.02.R",
        "_1:heel.02.L",
        "_1:Head_end",
        "_1:palm.01.R",
        "_1:palm.01.L",
        "_1:palm.02.R",  # Optional
        "_1:palm.02.L"  # Optional
    ]

    import_fbx(fbx_file_path)
    set_frame_range()
    armature_data = analyze_armature(armature_name, joints_names)
    export_to_csv(armature_data, output_file_path_csv)

if __name__ == "__main__":
    main()