import pygame
import numpy as np

MOWER_DIAMETER = 20
FIELD_SIZE = (640, 480)
GRASS_UNCUT_COLOUR = (0, 100, 0)
GRASS_CUT_COLOUR = (0, 255, 0)
SPEED = 5
MAX_STEER_ANGLE_CHANGE = 10
MAX_STEER_ANGLE = 80
WHEEL_X = 4
WHEEL_Y = 6



class Mower:
    def __init__(self):

        self.mower_rb = np.array([10, 10], dtype=float)
        self.mower_angle_in_degrees = 0
        self.wheel_angle_in_degrees = -10

    def wheel_rb(self):
        return(np)

screen = pygame.display.set_mode(FIELD_SIZE)
clock = pygame.time.Clock()            #get a pygame clock object
player = pygame.image.load('player.bmp').convert()
background = pygame.image.load('background.bmp').convert()
screen.blit(background, (0, 0))
objects = []
for x in range(10):                    #create 10 objects</i>
    o = GameObject(player, x*40, x)
    objects.append(o)
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
    for o in objects:
        screen.blit(background, o.pos, o.pos)
    for o in objects:
        o.move()
        screen.blit(o.image, o.pos)
    pygame.display.update()
    clock.tick(60)