"""
colors for thrust activations and assignments of keys for correct thrust don't fully work yet 
and movement with keys is quite challenging to use as a human, especially because the drone rotates on the z ais, 
hopefully the RNN will do better than me! ;)
"""

#orientation with right-click hold
#zoom in and out by scrolling
#use thrusters of quadcopter with q, w, a, s
#pause simulation with p, quit simulation with esc, restart simulation with r (pause and restart have to be added to each agent)

import pygame
from pygame.math import Vector3
from OpenGL.GL import *
from OpenGL.GLU import *
import math
import pygetwindow
import random as r
#import from RNN class, dynamically, to update the 
#drone.left_thrust / drone.right_thrust 
#and give live feedback as 
#drone.x, drone.y, drone.angle, drone.left_thrust, drone.right_thrust

# Initialize Pygame and OpenGL
pygame.init()
WIDTH, HEIGHT = 800, 600
display = (WIDTH, HEIGHT)
pygame.display.set_mode((display), pygame.DOUBLEBUF | pygame.OPENGL | pygame.RESIZABLE)
glEnable(GL_DEPTH_TEST)

pygame.display.set_caption("2D Drone Simulation for RNN")
win = pygetwindow.getWindowsWithTitle("2D Drone Simulation for RNN")[0]
win.maximize()

# Camera properties
camera_distance = 100
camera_yaw = 0
camera_pitch = 45

# Quadcopter properties
THRUST_POWER = 0.02
GRAVITY = Vector3(0, -0.005, 0)
ROTATION_SPEED = 0.06

def set_projection():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, (display[0] / display[1]), 0.1, 2000.0)

def load_texture(image_path):
    image = pygame.image.load(image_path)
    texture_data = pygame.image.tostring(image, "RGBA", 1)
    width, height = image.get_width(), image.get_height()
    texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, texture_data)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    return texture_id

def draw_ground(texture_id, size, height):
    glColor3f(0.5, 0.5, 0.5)
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glBegin(GL_QUADS)
    glTexCoord2f(0, 0); glVertex3f(-size, height, -size)
    glTexCoord2f(1, 0); glVertex3f(size, height, -size)
    glTexCoord2f(1, 1); glVertex3f(size, height, size)
    glTexCoord2f(0, 1); glVertex3f(-size, height, size)
    glEnd()
    glDisable(GL_TEXTURE_2D)

class Quadcopter:
    def __init__(self):
        self.position = Vector3(0, 7, 0)  # Initial position with higher z value
        self.velocity = Vector3(0, 0, 0)
        self.acceleration = Vector3(0, 0, 0)
        self.orientation = Vector3(0, 0, 0)
        self.angular_velocity = Vector3(0, 0, 0)
        self.thrusts = [0, 0, 0, 0]  # FL, FR, BL, BR

    def apply_thrust(self):
        total_thrust = sum(self.thrusts)
        thrust_vector = Vector3(0, total_thrust, 0)
        thrust_vector = self.rotate_vector(thrust_vector)
        self.acceleration = thrust_vector + GRAVITY

        torque_x = (self.thrusts[1] + self.thrusts[3] - self.thrusts[0] - self.thrusts[2]) * ROTATION_SPEED
        torque_y = (-self.thrusts[0] - self.thrusts[1] + self.thrusts[2] + self.thrusts[3]) * ROTATION_SPEED
        torque_z = (self.thrusts[0] + self.thrusts[3] - self.thrusts[1] - self.thrusts[2]) * ROTATION_SPEED
        
        self.angular_velocity += Vector3(torque_x, torque_y, torque_z)

    def rotate_vector(self, vector):
        x, y, z = vector
        pitch, yaw, roll = self.orientation
        # Yaw rotation
        x, z = x * math.cos(yaw) - z * math.sin(yaw), x * math.sin(yaw) + z * math.cos(yaw)
        # Pitch rotation
        y, z = y * math.cos(pitch) - z * math.sin(pitch), y * math.sin(pitch) + z * math.cos(pitch)
        # Roll rotation
        x, y = x * math.cos(roll) - y * math.sin(roll), x * math.sin(roll) + y * math.cos(roll)

        return Vector3(x, y, z)

    def update(self):
        self.apply_thrust()
        self.velocity += self.acceleration
        self.position += self.velocity
        self.orientation += self.angular_velocity

        # Apply air resistance
        self.velocity *= 0.99
        self.angular_velocity *= 0.99

    def draw(self, active_l):
        glPushMatrix()
        glTranslatef(self.position.x, self.position.y, self.position.z)
        glRotatef(math.degrees(self.orientation.x), 1, 0, 0)
        glRotatef(math.degrees(self.orientation.y), 0, 1, 0)
        glRotatef(math.degrees(self.orientation.z), 0, 0, 1)

        # Draw quadcopter body with thicker lines
        glColor3f(191/255, 64/255, 191/255)  # Set quadcopter color
        glLineWidth(3)  # Set line width
        glBegin(GL_LINES)
        glVertex3f(-2, 0, -2)
        glVertex3f(2, 0, 2)
        glVertex3f(-2, 0, 2)
        glVertex3f(2, 0, -2)
        glEnd()

        # Draw rotors
        rotor_positions = [(-2, 0, -2), (2, 0, -2), (-2, 0, 2), (2, 0, 2)]
        for i, pos in enumerate(rotor_positions):
            glPushMatrix()
            glTranslatef(pos[0], pos[1], pos[2])
            glColor3f(active_l[i], 0, 0)
            gluSphere(gluNewQuadric(), 0.1, 10, 10)
            glPopMatrix()

        glPopMatrix()

num_agents = 100
all_agents = []

# Create quadcopter
for i in range(num_agents):
    quadcopter = Quadcopter()
    all_agents.append(quadcopter)

# Load and set up the ground texture
ground_texture_id = load_texture("grid_text2.jpg")

def draw_checkp(size, position):
    glPushMatrix()
    glTranslatef(position[0], position[1], position[2])
    glColor3f(0, 1, 0)  # Green color for checkpoints
    sphere = gluNewQuadric()
    gluSphere(sphere, size, 20, 20)  # Increased resolution to 20 slices and stacks
    gluDeleteQuadric(sphere)  # Clean up the quadric object
    glPopMatrix()

def is_collected(coo, drone_position, collection_distance=5):
    return (drone_position - coo).length() < collection_distance

# Game loop
running = True
paused = False
clock = pygame.time.Clock()
prev_mouse_pos = None
active_l = [0, 0, 0, 0]

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_r:
                all_agents[0] = Quadcopter()  # Restart
            elif event.key == pygame.K_p:
                paused = not paused  # Toggle pause
        elif event.type == pygame.VIDEORESIZE:
            display = (event.w, event.h)
            pygame.display.set_mode(display, pygame.DOUBLEBUF | pygame.OPENGL | pygame.RESIZABLE)
            glViewport(0, 0, display[0], display[1])
            set_projection()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:  # Scroll up
                camera_distance -= 1
                if camera_distance < 1:
                    camera_distance = 1
            elif event.button == 5:  # Scroll down
                camera_distance += 1
                if camera_distance > 100:
                    camera_distance = 100

    if not paused:
        # Handle input or replace with RNN interactions dynamically setting thrustpower for each thrust individually and getting feedback
        keys = pygame.key.get_pressed()
        all_agents[0].thrusts[0] = THRUST_POWER if keys[pygame.K_q] else 0  # Front Left
        all_agents[0].thrusts[1] = THRUST_POWER if keys[pygame.K_w] else 0  # Front Right
        all_agents[0].thrusts[2] = THRUST_POWER if keys[pygame.K_a] else 0  # Back Left
        all_agents[0].thrusts[3] = THRUST_POWER if keys[pygame.K_s] else 0  # Back Right
        #               if all_agents[0].thrusts[0] > 0 else 0
        active_l[3] = 1 if keys[pygame.K_q] else 0  # Front Left
        active_l[0] = 1 if keys[pygame.K_w] else 0  # Front Right
        active_l[2] = 1 if keys[pygame.K_a] else 0  # Back Left
        active_l[1] = 1 if keys[pygame.K_s] else 0  # Back Right
        
        # Update
        all_agents[0].update()
        all_agents[1].update()
    
    # Camera movement
    mouse_buttons = pygame.mouse.get_pressed()
    if mouse_buttons[2]:  # Right mouse button
        mouse_pos = pygame.mouse.get_pos()
        if prev_mouse_pos:
            dx, dy = mouse_pos[0] - prev_mouse_pos[0], mouse_pos[1] - prev_mouse_pos[1]
            camera_yaw += dx * 0.1
            camera_pitch += dy * 0.1
            if camera_pitch < -90:
                camera_pitch = -90
            elif camera_pitch > 90:
                camera_pitch = 90
        prev_mouse_pos = mouse_pos
    else:
        prev_mouse_pos = None

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    # Set camera
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(camera_distance * math.cos(math.radians(camera_yaw)), camera_distance * math.sin(math.radians(camera_pitch)), camera_distance * math.sin(math.radians(camera_yaw)), 0, 0, 0, 0, 1, 0)

    # Draw ground
    #create one for each agent
    draw_ground(ground_texture_id, 300, -35)
    checkpoint_space = 50
    
    try: #purpously here, because will fial the first run
        #check for each agent
        checked = is_collected((x_chp, y_chp, z_chp), all_agents[0].position)
        if checked:
            x_chp = r.randint(-checkpoint_space, checkpoint_space)
            y_chp = r.randint(-checkpoint_space, checkpoint_space)
            z_chp = r.randint(-checkpoint_space, checkpoint_space)
    except:
        x_chp = r.randint(-checkpoint_space, checkpoint_space)
        y_chp = r.randint(-checkpoint_space, checkpoint_space)
        z_chp = r.randint(-checkpoint_space, checkpoint_space)
        
    draw_checkp(0.5, (x_chp, y_chp, z_chp)) #maybe also specify for each agent, for simultaneous training
    
    # Draw quadcopter
    all_agents[0].draw(active_l)
    all_agents[1].draw(active_l)
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()