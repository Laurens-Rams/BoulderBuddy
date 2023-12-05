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

def export_to_json(data, file_path):
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)

def main():
    fbx_file_path = '/Users/laurensart/Dropbox/Laurens/Move-One-Import/move-one.fbx'
    output_file_path = '/Users/laurensart/Dropbox/Laurens/Move-One-Import/output.json'
    armature_name = "Armature"

    import_fbx(fbx_file_path)
    armature_data = analyze_armature(armature_name)
    export_to_json(armature_data, output_file_path)


if __name__ == "__main__":
    main()