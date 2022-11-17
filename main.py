import pygame as pg
import math


MOWER_DIAMETER = 40
WHEEL_SIZE = (8, 14)
WHEEL_COLOUR = (0, 100, 100)
MOWER_COLOUR = (200, 0, 0)
FIELD_SIZE = (640, 480)
GRASS_UNCUT_COLOUR = (0, 100, 0)
GRASS_CUT_COLOUR = (0, 255, 0)
SPEED = 5
MAX_STEER_ANGLE_CHANGE = 10
MAX_STEER_ANGLE = 80


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

        self.centre = (MOWER_DIAMETER / 2, MOWER_DIAMETER / 2)
        self.angle_in_degrees = 0
        self.wheel_angle_in_degrees = -10
        self.base = pg.display.set_mode([MOWER_DIAMETER, MOWER_DIAMETER], pg.SRCALPHA, 32)
        self.build_base()
        self.image = self.base

    def build_base(self):
        mower_base = pg.display.set_mode([MOWER_DIAMETER, MOWER_DIAMETER], pg.SRCALPHA, 32)
        mower_base = mower_base.convert_alpha()
        # Draw mower body/blade on the mower
        pg.draw.circle(mower_base, (255, 0, 0), (MOWER_DIAMETER / 2, MOWER_DIAMETER / 2), MOWER_DIAMETER / 2)
        # Draw right back wheel on the mower
        pg.draw.rect(mower_base,
                     WHEEL_COLOUR,
                     (0, 0) + WHEEL_SIZE)
        # Draw left back wheel on the mower
        pg.draw.rect(mower_base,
                     WHEEL_COLOUR,
                     (MOWER_DIAMETER - WHEEL_SIZE[0], 0) + WHEEL_SIZE)
        self.base = mower_base


    def build_image(self):
        # Get the base image
        mower_img = self.base

        # Create a rotated front wheel image
        wheel_img = pg.display.set_mode([WHEEL_SIZE[0] + 2, WHEEL_SIZE[1] + 2], pg.SRCALPHA, 32)
        wheel_img = wheel_img.convert_alpha()
        pg.draw.rect(wheel_img,
                     WHEEL_COLOUR,
                     (1, 1) + WHEEL_SIZE)
        wheel_img = pg.transform.rotate(wheel_img, math.radians(self.wheel_angle_in_degrees))

        # Draw right front wheel on the mower
        mower_img.blit(wheel_img, (WHEEL_SIZE[0] / 2 + 1, WHEEL_SIZE[1] / 2 + 1))

        # Draw left front wheel on the mower
        mower_img.blit(wheel_img, (WHEEL_SIZE[0] / 2 + MOWER_DIAMETER + 1, WHEEL_SIZE[1] / 2 + 1))

        self.image = mower_img


class Field:
    def __init__(self):

        self.screen = pg.display.set_mode(FIELD_SIZE)

    def count_colour(self, colour):
        count = 0
        for i in range(FIELD_SIZE[0]):
            for j in range(FIELD_SIZE[1]):
                if self.screen.get_at((i, j))[0:3] == colour:
                    count += 1
        return count

#    def mow(self):
#        self.screen.blit(mower.base, (300, 300)))


pg.init()
mower = Mower()
field = Field()
clock = pg.time.Clock()

rect = pg.Rect(0, 0, 20, 20)
rect.center = field.screen.get_rect().center
vel = 5

run = True
while run:
    clock.tick(1000)
    for event in pg.event.get():
        if event.type == pg.QUIT:
            run = False
        if event.type == pg.KEYDOWN:
            print(pg.key.name(event.key))

    keys = pg.key.get_pressed()

    if keys[pg.K_LEFT]:
        print("keys_x", keys[pg.K_x])
        pg.draw.rect(field.screen, (0, 0, 255), rect)
        field.screen.blit(mower.base, (200, 200))
    elif keys[pg.K_RIGHT]:
        rect.x += (keys[pg.K_RIGHT] - keys[pg.K_LEFT]) * vel
        rect.y += (keys[pg.K_DOWN] - keys[pg.K_UP]) * vel

        rect.centerx = rect.centerx % field.screen.get_width()
        rect.centery = rect.centery % field.screen.get_height()

        field.screen.fill(0)
        pg.draw.rect(field.screen, (255, 0, 0), rect)
    elif keys[pg.K_UP]:
        field.screen.blit(mower.base, (300, 300))
    elif keys[pg.K_DOWN]:
        mower.build_image()
        field.screen.blit(mower.image, (400, 400))
    else:
        pg.display.flip()

pg.quit()
exit()
