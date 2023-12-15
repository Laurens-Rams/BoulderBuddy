import bpy
import sys

# Path to the FBX file
fbx_file_path = 'fbx_files/move-four.fbx'

# Path where the GLB file will be saved
glb_file_path = 'output.glb'

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Import the FBX file
bpy.ops.import_scene.fbx(filepath=fbx_file_path)

# Export to GLB
bpy.ops.export_scene.gltf(filepath=glb_file_path, export_format='GLB')