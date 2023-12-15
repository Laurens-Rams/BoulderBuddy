import json
import pygame
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

def draw_axes():
    glBegin(GL_LINES)
    # X axis in red
    glColor3f(1.0, 0.0, 0.0)
    glVertex3f(0.0, 0.0, 0.0)
    glVertex3f(10.0, 0.0, 0.0)
    # Y axis in green
    glColor3f(0.0, 1.0, 0.0)
    glVertex3f(0.0, 0.0, 0.0)
    glVertex3f(0.0, 10.0, 0.0)
    # Z axis in blue
    glColor3f(0.0, 0.0, 1.0)
    glVertex3f(0.0, 0.0, 0.0)
    glVertex3f(0.0, 0.0, 10.0)
    glEnd()

def draw_grid():
    glBegin(GL_LINES)
    glColor3f(0.1, 0.1, 0.1)  # Grey color for the grid lines
    for i in range(-10, 11, 1):
        glVertex3f(i, -10, 0)
        glVertex3f(i, 10, 0)
        glVertex3f(-10, i, 0)
        glVertex3f(10, i, 0)
    glEnd()

def setup_camera():
    display = pygame.display.get_surface().get_size()
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    glEnable(GL_DEPTH_TEST)
    gluPerspective(50, (display[0] / display[1]), 0.5, 50.0)
    glTranslatef(0.0, -3, -10)

def handle_camera_controls(cam_angle_x, cam_angle_y):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False, cam_angle_x, cam_angle_y
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                cam_angle_y += 5
            elif event.key == pygame.K_RIGHT:
                cam_angle_y -= 5
            elif event.key == pygame.K_UP:
                cam_angle_x += 5
            elif event.key == pygame.K_DOWN:
                cam_angle_x -= 5
    return True, cam_angle_x, cam_angle_y
