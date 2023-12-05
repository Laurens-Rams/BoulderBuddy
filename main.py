import bpy
import json

def import_fbx(fbx_path):
    bpy.ops.import_scene.fbx(filepath=fbx_path)

def analyze_armature(armature_name):
    data = {}
    armature = bpy.context.scene.objects.get(armature_name)

    if armature:
        bpy.context.view_layer.objects.active = armature
        bpy.ops.object.mode_set(mode='POSE')

        for bone in armature.pose.bones:
            bone_name = bone.name
            data[bone_name] = []
            for frame in range(bpy.context.scene.frame_start, bpy.context.scene.frame_end + 1):
                bpy.context.scene.frame_set(frame)
                data[bone_name].append({
                    'frame': frame,
                    'position': list(bone.head.xyz),
                    'rotation': list(bone.rotation_quaternion)
                })

    return data

def output_bones(armature_name):
    bone_names = []
    armature = bpy.context.scene.objects.get(armature_name)

    if armature:
        bpy.context.view_layer.objects.active = armature
        bpy.ops.object.mode_set(mode='POSE')

        for bone in armature.pose.bones:
            bone_names.append(bone.name)

    return bone_names

def export_to_json(data, file_path):
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)


def main():
    fbx_file_path = '/Users/laurensart/Dropbox/Laurens/Move-One-Import/move-two.fbx'
    output_file_path = '/Users/laurensart/Dropbox/Laurens/Move-One-Import/output.json'
    output_file_path_bones = '/Users/laurensart/Dropbox/Laurens/Move-One-Import/output-bones.json'
    armature_name = "Armature"

    import_fbx(fbx_file_path)
    armature_data = analyze_armature(armature_name)
    export_to_json(armature_data, output_file_path)

    bone_names = output_bones(armature_name)
    export_to_json(bone_names, output_file_path_bones)


if __name__ == "__main__":
    main()
