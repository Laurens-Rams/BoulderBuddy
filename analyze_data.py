import json
import pygame
import cv2

from OpenGL.GL import *
from OpenGL.GLUT import *
from graphics_utils import draw_axes, draw_grid, setup_camera, handle_camera_controls

from collections import deque
from math import sqrt


# Global scale factor for the joint positions
SCALE_FACTOR = 0.03
HIP_TRAIL_LENGTH = 1500  # Number of frames to remember and display
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
    glutSolidSphere(0.04, 10, 10)
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
        glColor3f(0.5 - color_intensity, color_intensity, 0.0)  # Lerp between green and red
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

def draw_holds(holds, color, size):
    glColor3f(*color)
    for x, y, z in holds:
        glPushMatrix()
        glTranslate(x, y, z)
        glutSolidSphere(size, 10, 10)  # Changed from 0.05 to size
        glPopMatrix()

def distance_between_points(p1, p2):
    return sqrt(sum((a - b) ** 2 for a, b in zip(p1, p2)))

def find_clusters(holds, threshold):
    # Convert the threshold from pixels to your coordinate system
    threshold /= SCALE_FACTOR
    clusters = []
    for hold in holds:
        found = False
        for cluster in clusters:
            if distance_between_points(hold, cluster['center']) < threshold:
                cluster['points'].append(hold)
                # Recalculate cluster center
                xs, ys, zs = zip(*cluster['points'])
                cluster['center'] = (sum(xs) / len(xs), sum(ys) / len(ys), sum(zs) / len(zs))
                found = True
                break
        if not found:
            clusters.append({'center': hold, 'points': [hold]})
    return clusters

def normalize_holds(holds, threshold=100):  # Adjust this threshold as needed
    # Threshold divided by SCALE_FACTOR to convert from pixel distance to your coordinate system
    threshold = threshold * SCALE_FACTOR
    clusters = find_clusters(holds, threshold)
    return [cluster['center'] for cluster in clusters]

def draw_normalized_holds(holds, color):
    for hold in holds:
        draw_holds([hold], color, 0.1)

def main():
    # Initialize Pygame
    pygame.init()

    # Get the desktop height
    desktop_info = pygame.display.Info()
    desktop_height = desktop_info.current_h

    # Choose an aspect ratio (e.g., 9:16 for a typical phone)
    aspect_ratio = (9, 16)

    # Calculate the window width based on the aspect ratio and desktop height
    window_width = desktop_height * aspect_ratio[0] // aspect_ratio[1]

    # Set the display mode
    screen = pygame.display.set_mode((window_width, desktop_height))


    json_file_path = '/Users/laurensart/Dropbox/Laurens/Move-One-Import/output.json'
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

    joint_pairs = [
        ("_1:Hips", "_1:Spine"),
        ("_1:Spine", "_1:Spine1"),
        ("_1:Spine1", "_1:Neck"),
        ("_1:Neck", "_1:Head"),
        ("_1:RightShoulder", "_1:RightArm"),
        ("_1:RightArm", "_1:RightForeArm"),
        ("_1:RightForeArm", "_1:RightHand"),
        ("_1:LeftShoulder", "_1:LeftArm"),
        ("_1:LeftArm", "_1:LeftForeArm"),
        ("_1:LeftForeArm", "_1:LeftHand"),
        ("_1:RightUpLeg", "_1:RightLeg"),
        ("_1:RightLeg", "_1:RightFoot"),
        ("_1:LeftUpLeg", "_1:LeftLeg"),
        ("_1:LeftLeg", "_1:LeftFoot"),
    ]

    frame_counter = 0

    video_path = 'source.mp4'  # Update this with your video file path
    cap = cv2.VideoCapture(video_path)
    video_fps = cap.get(cv2.CAP_PROP_FPS)
    video_frame_duration = int(1000 / video_fps)

    data = read_json(json_file_path)
    setup_camera()

    hip_trail = deque(maxlen=HIP_TRAIL_LENGTH)

    initial_hip_position = get_joint_position(data, "_1:Hips", 1)
    initial_hip_height = initial_hip_position[1] * SCALE_FACTOR if initial_hip_position else 0

    running = True
    frame_number = 1
    max_frames = 1500

    hand_holds, foot_holds = calculate_holds(data, joints_names, max_frames, initial_hip_height)
    normalized_hand_holds = normalize_holds(hand_holds, threshold=0.9)  # Use an appropriate threshold
    normalized_foot_holds = normalize_holds(foot_holds, threshold=0.9)

    cam_angle_x, cam_angle_y = 0, 0
    clock = pygame.time.Clock()

    while running:
        if not cap.isOpened():
            cap = cv2.VideoCapture(video_path)  # Restart the video if it has ended

        ret, frame = cap.read()
        if not ret:
            # Reset the video capture if the video has reached its end
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue  # Skip the rest of the loop iteration

        cv2.imshow("Video", frame)
        cv2.waitKey(video_frame_duration)  # Display each frame for its duration

        running, cam_angle_x, cam_angle_y = handle_camera_controls(cam_angle_x, cam_angle_y)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glPushMatrix()
        glRotatef(cam_angle_x - 100, 1, 0, 0)
        glRotatef(cam_angle_y, 0, 1, 0)

        frame_counter += 1


        # Draw the grid in the background
        draw_grid()

        # Draw the holds for hands and feet
        # draw_holds(hand_holds, (0.1, 0.6, 0.1), 0.05)  # Red for hand holds
         # draw_holds(foot_holds, (0.1, 0.1, 0.6), 0.05)  # Green for foot holds

        # Then, in your drawing code:
        draw_normalized_holds(normalized_hand_holds, (0.8, 0.3, 0.0))
        draw_normalized_holds(normalized_foot_holds, (0.3, 0.0, 0.8))

        # Handle the hip trail and reset it at the beginning of each loop
        if frame_number == 1:
            hip_trail.clear()

        if frame_counter >= 5:
            hip_position = get_joint_position(data, "_1:Hips", frame_number)
            if hip_position:
                x, y, z = (coord * SCALE_FACTOR for coord in hip_position)
                adjusted_y = y - initial_hip_height
                if hip_trail:
                    last_x, last_y, last_z = hip_trail[-1][:3]  # Get the last position
                    speed = calculate_speed((last_x, last_y, last_z), (x, adjusted_y, z))
                else:
                    speed = 0
                hip_trail.append((x, adjusted_y, z, speed))
            frame_counter = 0  # Reset the frame counter

        # Draw the figure along with the limb connections
        display_animation(data, joints_names, frame_number, initial_hip_height)
        draw_limb_connections(data, frame_number, joint_pairs, initial_hip_height)

        if hip_trail:
            draw_trail(hip_trail)

        glPopMatrix()

        pygame.display.flip()
        frame_number = (frame_number % max_frames) + 1
        clock.tick(60)

    cap.release()
    cv2.destroyAllWindows()
    pygame.quit()


if __name__ == "__main__":
    main()
