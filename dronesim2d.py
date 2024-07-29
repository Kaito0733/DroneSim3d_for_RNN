import pygame
import math
from time import sleep
import random as r
"""
import from RNN class, dynamically, to update the 
drone.left_thrust / drone.right_thrust 
and give live feedback as 
drone.x, drone.y, drone.angle, drone.left_thrust, drone.right_thrust
"""
pygame.init()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

DRONE_WIDTH = 60
DRONE_HEIGHT = 20
THRUST_POWER = 0.35
GRAVITY = 0.35
ROTATION_SPEED = 0.01

screen = pygame.display.set_mode((0, 0), pygame.RESIZABLE)
pygame.display.set_caption("2D Drone Simulation for RNN")
surface = pygame.display.get_surface()

class Drone:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 0
        self.velocity_x = 0
        self.velocity_y = 0
        self.angular_velocity = 0
        self.left_thrust = 0
        self.right_thrust = 0        

    def apply_thrust(self):
        force_x = (self.left_thrust + self.right_thrust) * math.sin(self.angle)
        force_y = -(self.left_thrust + self.right_thrust) * math.cos(self.angle)
        self.velocity_x += force_x
        self.velocity_y += force_y
        self.angular_velocity += (self.right_thrust - self.left_thrust) * ROTATION_SPEED

    def update(self):
        self.apply_thrust()
        self.velocity_y += GRAVITY
        self.x += self.velocity_x
        self.y += self.velocity_y
        self.angle += self.angular_velocity

        #air resistance
        self.velocity_x *= 0.99
        self.velocity_y *= 0.99
        self.angular_velocity *= 0.99
        #box, maybe collision, bounce off

    def draw(self, screen, coo):
        drone_points = [
            (-DRONE_WIDTH//2, -DRONE_HEIGHT//2),
            (DRONE_WIDTH//2, -DRONE_HEIGHT//2),
            (DRONE_WIDTH//2, DRONE_HEIGHT//2),
            (-DRONE_WIDTH//2, DRONE_HEIGHT//2)
        ]
        rotated_points = []
        for point in drone_points:
            x = point[0] * math.cos(self.angle) - point[1] * math.sin(self.angle)
            y = point[0] * math.sin(self.angle) + point[1] * math.cos(self.angle)
            rotated_points.append((x + self.x, y + self.y))
        pygame.draw.polygon(screen, WHITE, rotated_points)

        #thrusters if used
        if self.left_thrust > 0:
            pygame.draw.line(screen, RED, rotated_points[3], (rotated_points[3][0] - 20 * math.sin(self.angle),
                                                              rotated_points[3][1] + 20 * math.cos(self.angle)), 3)
        if self.right_thrust > 0:
            pygame.draw.line(screen, RED, rotated_points[2], (rotated_points[2][0] - 20 * math.sin(self.angle),
                                                              rotated_points[2][1] + 20 * math.cos(self.angle)), 3)
        pygame.draw.circle(screen, (0, 255, 0), coo, 10)

    def checkp(self, coo, collection_distance=10):
        return (math.dist((self.x, self.y), coo)) < collection_distance

#initialization
drone = Drone(surface.get_width() // 2, surface.get_height() // 2)
running = True
clock = pygame.time.Clock()
pause = False

#loop
checkpoint_space = surface.get_height()-100
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    #replace with RNN functions and feedback
    keys = pygame.key.get_pressed()
    drone.left_thrust = THRUST_POWER if keys[pygame.K_LEFT] else 0
    drone.right_thrust = THRUST_POWER if keys[pygame.K_RIGHT] else 0
    if keys[pygame.K_r]:
        drone.__init__(surface.get_width() // 2, surface.get_height() // 2)
    running = False if keys[pygame.K_ESCAPE] else True
    if keys[pygame.K_p]:
        pause = not pause
        sleep(0.25)
 
    if not pause:
        drone.update()
        screen.fill(BLACK)

        try: #purpously here, because will fial the first run
            #check for each agent
            checked = drone.checkp((x_chp, y_chp))
            if checked:
                x_chp = r.randint(0, checkpoint_space)
                y_chp = r.randint(0, checkpoint_space)
        except:
            x_chp = r.randint(0, checkpoint_space)
            y_chp = r.randint(0, checkpoint_space)

        drone.draw(screen, (x_chp, y_chp))
        pygame.display.flip()
        clock.tick(60)

pygame.quit()