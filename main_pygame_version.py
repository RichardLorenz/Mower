import pygame as pg
import numpy as np

MOWER_DIAMETER = 40
FIELD_SIZE = (640, 480)
GRASS_UNCUT_COLOUR = (0, 100, 0)
GRASS_CUT_COLOUR = (0, 255, 0)
SPEED = 5
MAX_STEER_ANGLE_CHANGE = 10
MAX_STEER_ANGLE = 80
WHEEL_X = 4
WHEEL_Y = 6
WHEEL = [[-1, -2], [-1, 2], [1, -2], [1, 2]]
MOWER = [[-10, -10], [-10, 10], [10, -10], [10, 10]]


def coord_add(p1, p2):
    return [p1[0] + p2[0], p1[1] + p2[1]]


def coord_mult(p, m):
    return [p[0] * m[0][0] + p[1] * m[0][1],
            p[0] * m[1][0] + p[1] * m[1][1]]


def coord_rot(p, a):
    # Note: a is in radians
    m = [[math.cos(a), math.sin(a)], [-math.sin(a), math.cos(a)]]
    return coord_mult(p, m)


def coord_list_rot(lst, a):
    l2 = []
    for p in lst:
        l2.append(coord_rot(p, a))
    return l2


def coord_list_add(lst, a):
    l2 = []
    for p in lst:
        l2.append(coord_add(p, a))
    return l2


class Mower:
    def __init__(self):

        self.centre = [10, 10]
        self.angle_in_degrees = 0
        self.wheel_angle_in_degrees = -10
        self.base = pg.display.set_mode([MOWER_DIAMETER, MOWER_DIAMETER], pg.SRCALPHA, 32)
        self.image = self.base

    def build_base(self):
        self.base = self.base.convert_alpha()
        # Draw right back wheel on the mower
        pg.draw.rect(self.base, (0, 0, 0), (0, 0, 15, 15))
        # Draw left back wheel on the mower
        pg.draw.rect(self.base, (0, 0, 0), (10, 0, 15, 15))
        # Draw mower body/blade on the mower
        pg.draw.circle(self.base, (255, 0, 0), (MOWER_DIAMETER / 2, MOWER_DIAMETER / 2), 50)

    def build_image(self):
        self.image = self.base
        # Draw right front wheel on the mower
        pg.draw.rect(self.image, (0, 0, 0), (0, 10, 15, 15))
        # Draw left front wheel on the mower
        pg.draw.rect(self.image, (0, 0, 0), (10, 10, 15, 15))


def count_colour(scr, col):
    count = 0
    for i in range(FIELD_SIZE[0]):
        for j in range(FIELD_SIZE[1]):
            if scr.get_at((i, j))[0:3] == (255, 0, 0):
                count += 1
    return count


screen = pg.display.set_mode(FIELD_SIZE)
pg.draw.rect(screen, (0, 100, 0), (0, 0, FIELD_SIZE, FIELD_SIZE))


mower = Mower()
clock = pg.time.Clock()            # get a pygame clock object
player = mower.image
objects = []
for x in range(10):                    # create 10 objects</i>
    o = GameObject(player, x*40, x)
    objects.append(o)
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
    screen.blit(background, o.pos, o.pos)
    for o in objects:
        o.move()
        screen.blit(o.image, o.pos)
    pg.display.update()
    clock.tick(60)