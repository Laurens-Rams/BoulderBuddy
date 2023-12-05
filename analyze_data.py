import json
import pygame


from OpenGL.GL import *
from OpenGL.GLUT import *
from graphics_utils import draw_axes, draw_grid, setup_camera, handle_camera_controls

from collections import deque
from math import sqrt


# Global scale factor for the joint positions
SCALE_FACTOR = 0.02
HIP_TRAIL_LENGTH = 121  # Number of frames to remember and display
TRAIL_SPHERE_SIZE = 0.02
SPEED_THRESHOLD = 0.008
def read_json(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def draw_joint(x, y, z):
    glPushMatrix()
    glTranslate(x, y, z)
    glColor3f(0.7, 0.7, 0.7)
    glutSolidSphere(0.08, 10, 10)
    glPopMatrix()

def draw_joint_trail(x, y, z):
    glPushMatrix()
    glTranslate(x, y, z)
    glutSolidSphere(0.02, 10, 10)
    glPopMatrix()

def display_animation(data, joints_names, frame_number, initial_hip_height):
    draw_grid()
    for joint_name in joints_names:
        joint_position = get_joint_position(data, joint_name, frame_number)
        if joint_position:
            x, y, z = (coord * SCALE_FACTOR for coord in joint_position)
            adjusted_y = y - initial_hip_height
            draw_joint(x, adjusted_y, z)

def get_joint_position(data, joint_name, frame_number):
    joint_data = data.get(joint_name, [])
    for frame_data in joint_data:
        if frame_data['frame'] == frame_number:
            return frame_data['position']
    return None

def calculate_speed(position1, position2):
    return sqrt(sum((p1 - p2) ** 2 for p1, p2 in zip(position1, position2)))

def draw_trail(trail):
    for x, y, z, speed in trail:
        color_intensity = max(0.0, min(speed / 0.1, 1.0))  # Normalize speed value
        glColor3f(1.0 - color_intensity, color_intensity, 0.0)  # Lerp between green and red
        draw_joint_trail(x, y, z)

def draw_limb_connections(data, frame_number, joint_pairs, initial_hip_height):
    glBegin(GL_LINES)
    glColor3f(0.5, 0.5, 0.5)
    for joint1, joint2 in joint_pairs:
        pos1 = get_joint_position(data, joint1, frame_number)
        pos2 = get_joint_position(data, joint2, frame_number)
        if pos1 and pos2:
            x1, y1, z1 = (coord * SCALE_FACTOR for coord in pos1)
            x2, y2, z2 = (coord * SCALE_FACTOR for coord in pos2)
            glVertex3f(x1, y1 - initial_hip_height, z1)
            glVertex3f(x2, y2 - initial_hip_height, z2)
    glEnd()

def calculate_holds(data, joint_names, max_frames, initial_hip_height):
    hand_holds, foot_holds = [], []
    previous_positions = {}

    for frame_number in range(1, max_frames + 1):
        for joint_name in joint_names:
            current_position = get_joint_position(data, joint_name, frame_number)
            if current_position:
                scaled_position = tuple(coord * SCALE_FACTOR for coord in current_position)
                adjusted_y = scaled_position[1] - initial_hip_height  # Apply hip height adjustment
                adjusted_position = (scaled_position[0], adjusted_y, scaled_position[2])

                if joint_name in previous_positions:
                    speed = calculate_speed(previous_positions[joint_name], adjusted_position)
                    if speed < SPEED_THRESHOLD:
                        if 'Hand' in joint_name:
                            hand_holds.append(adjusted_position)
                        elif 'Foot' in joint_name:
                            foot_holds.append(adjusted_position)
                previous_positions[joint_name] = adjusted_position

    return hand_holds, foot_holds

def draw_holds(holds, color):
    glColor3f(*color)
    for x, y, z in holds:
        glPushMatrix()
        glTranslate(x, y, z)
        glutSolidSphere(0.05, 10, 2)
        glPopMatrix()

def main():
    json_file_path = '/Users/laurensart/Dropbox/Laurens/Move-One-Import/output.json'
    joints_names = [
    "mixamorig:Hips",
    "mixamorig:Spine",
    "mixamorig:Spine1",
    "mixamorig:Spine2",
    "mixamorig:Neck",
    "mixamorig:Head",
    "mixamorig:LeftShoulder",
    "mixamorig:LeftArm",
    "mixamorig:LeftForeArm",
    "mixamorig:LeftHand",
    "mixamorig:RightShoulder",
    "mixamorig:RightArm",
    "mixamorig:RightForeArm",
    "mixamorig:RightHand",
    "mixamorig:LeftUpLeg",
    "mixamorig:LeftLeg",
    "mixamorig:LeftFoot",
    "mixamorig:RightUpLeg",
    "mixamorig:RightLeg",
    "mixamorig:RightFoot"
    ]

    joint_pairs = [
        ("mixamorig:Hips", "mixamorig:Spine"),
        ("mixamorig:Spine", "mixamorig:Spine1"),
        ("mixamorig:Spine1", "mixamorig:Spine2"),
        ("mixamorig:Spine2", "mixamorig:Neck"),
        ("mixamorig:Neck", "mixamorig:Head"),
        ("mixamorig:LeftShoulder", "mixamorig:LeftArm"),
        ("mixamorig:LeftArm", "mixamorig:LeftForeArm"),
        ("mixamorig:LeftForeArm", "mixamorig:LeftHand"),
        ("mixamorig:RightShoulder", "mixamorig:RightArm"),
        ("mixamorig:RightArm", "mixamorig:RightForeArm"),
        ("mixamorig:RightForeArm", "mixamorig:RightHand"),
        ("mixamorig:LeftUpLeg", "mixamorig:LeftLeg"),
        ("mixamorig:LeftLeg", "mixamorig:LeftFoot"),
        ("mixamorig:RightUpLeg", "mixamorig:RightLeg"),
        ("mixamorig:RightLeg", "mixamorig:RightFoot"),
    ]

    data = read_json(json_file_path)
    setup_camera()

    hip_trail = deque(maxlen=HIP_TRAIL_LENGTH)
    initial_hip_position = get_joint_position(data, "mixamorig:Hips", 1)
    initial_hip_height = initial_hip_position[1] * SCALE_FACTOR if initial_hip_position else 0

    running = True
    frame_number = 1
    max_frames = 121

    hand_holds, foot_holds = calculate_holds(data, joints_names, max_frames, initial_hip_height)

    cam_angle_x, cam_angle_y = 0, 0
    clock = pygame.time.Clock()

    while running:
        running, cam_angle_x, cam_angle_y = handle_camera_controls(cam_angle_x, cam_angle_y)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glPushMatrix()
        glRotatef(cam_angle_x, 1, 0, 0)
        glRotatef(cam_angle_y - 180, 0, 1, 0)

        # Draw the grid in the background
        draw_grid()

        # Draw the holds for hands and feet
        draw_holds(hand_holds, (0.1, 0.6, 0.1))  # Red for hand holds
        draw_holds(foot_holds, (0.1, 0.1, 0.6))  # Green for foot holds

        # Handle the hip trail and reset it at the beginning of each loop
        if frame_number == 1:
            hip_trail.clear()

        hip_position = get_joint_position(data, "mixamorig:Hips", frame_number)
        if hip_position:
            x, y, z = (coord * SCALE_FACTOR for coord in hip_position)
            adjusted_y = y - initial_hip_height
            if hip_trail:
                speed = calculate_speed(hip_trail[-1][:3], (x, adjusted_y, z))
            else:
                speed = 0
            hip_trail.append((x, adjusted_y, z, speed))
        #draw_trail(hip_trail)

        # Draw the figure along with the limb connections
        display_animation(data, joints_names, frame_number, initial_hip_height)
        draw_limb_connections(data, frame_number, joint_pairs, initial_hip_height)

        glPopMatrix()
        pygame.display.flip()
        frame_number = (frame_number % max_frames) + 1
        clock.tick(30)

    pygame.quit()


if __name__ == "__main__":
    main()
