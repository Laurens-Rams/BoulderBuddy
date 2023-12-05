import json
import pygame
import sys

def read_json(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def get_joint_position(data, joint_name, frame_number):
    joint_data = data.get(joint_name, [])
    for frame_data in joint_data:
        if frame_data['frame'] == frame_number:
            return frame_data['position']
    return None  # Return None if the joint or frame is not found

def display_animation(data, joints_names):
    pygame.init()
    screen_width, screen_height = 800, 600
    screen = pygame.display.set_mode((screen_width, screen_height))

    running = True
    clock = pygame.time.Clock()

    frame_number = 1
    # Assuming all joints have the same number of frames for simplicity
    max_frames = len(data.get(joints_names[0], []))

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((0, 0, 0))  # Clear screen

        for joint_name in joints_names:
            joint_position = get_joint_position(data, joint_name, frame_number)
            if joint_position:
                x, y = int(joint_position[0]) + screen_width // 2, int(joint_position[1]) + screen_height // 2
                pygame.draw.circle(screen, (255, 0, 0), (x, y), 1)

        pygame.display.flip()

        frame_number += 1
        if frame_number > max_frames:
            frame_number = 1

        clock.tick(60)

    pygame.quit()

def main():
    json_file_path = '/Users/laurensart/Dropbox/Laurens/Move-One-Import/output.json'
    joints_names = [
        "_1:Hips",
        "_1:Spine",
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

    data = read_json(json_file_path)
    display_animation(data, joints_names)

if __name__ == "__main__":
    main()