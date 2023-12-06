import bpy

def adjust_armature(climber_profile, armature_name):
    armature = bpy.data.objects[armature_name]
    bpy.context.view_layer.objects.active = armature
    bpy.ops.object.mode_set(mode='EDIT')

    armature_scale_factor = climber_profile['height'] / AVERAGE_HEIGHT
    arm_span_scale_factor = climber_profile['armspan'] / AVERAGE_ARM_SPAN

    # Example: Adjusting arm bones
    for bone in armature.data.edit_bones:
        if 'arm' in bone.name.lower():
            bone.length *= arm_span_scale_factor

    bpy.ops.object.mode_set(mode='OBJECT')

# Example climber profile
climber_profile = {
    'height': 180,  # in cm
    'armspan': 185  # in cm
}

adjust_armature(climber_profile, 'Armature')