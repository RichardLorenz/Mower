import time

import pygame as pg
import math

MOWER_DIAMETER = 40
WHEEL_SIZE = (8, 14)
WHEEL_COLOUR = (5, 5, 5)
MOWER_COLOUR = (200, 0, 0)
FIELD_SIZE = (640, 480)
GRASS_UNCUT_COLOUR = (0, 100, 0)
GRASS_CUT_COLOUR = (0, 255, 0)
SPEED = 5
MAX_STEER_ANGLE_CHANGE = 10
MAX_STEER_ANGLE = 80


class Coord:

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def coord(self):
        return [self.x, self.y]

    def __add__(self, p):
        return Coord(self.x + p.x, self.y + p.y)

    def __sub__(self, p):
        return Coord(self.x - p.x, self.y - p.y)

    def __mul__(self, m):
        return Coord(self.x * m, self.y * m)

    def mat_mul(self, mat):
        return Coord(self.x * mat[0][0] + self.y * mat[0][1],
                     self.x * mat[1][0] + self.y * mat[1][1])

    def rot(self, a):
        # Note: a is in radians
        mat = [[math.cos(a), math.sin(a)], [-math.sin(a), math.cos(a)]]
        return self.mat_mul(mat)

    def __repr__(self):
        return "".join(["Point(", str(self.x), ",", str(self.y), ")"])

    def rotate_about_centre(self, centre, angle_in_radians):
        # Set up the rotation matrix
        rotation_matrix = [[math.cos(angle_in_radians), math.sin(angle_in_radians)],
                           [-math.sin(angle_in_radians), math.cos(angle_in_radians)]]

        translated_point = self - centre

        rotated_point = translated_point.mat_mul(rotation_matrix)

        translate_back = rotated_point + centre

        return translate_back


def list_rot(lst, angle_in_radians):
    l2 = []
    for p in lst:
        l2.append(p.rot(angle_in_radians))
    return l2


def list_add(lst, translation):
    l2 = []
    for p in lst:
        l2.append(p + translation)
    return l2


class Mower:
    def __init__(self):

        self.centre = Coord(MOWER_DIAMETER / 2, MOWER_DIAMETER / 2)
        self.angle_in_degrees = 0
        self.wheel_angle_in_degrees = -10
        self.base = pg.Surface([MOWER_DIAMETER, MOWER_DIAMETER], pg.SRCALPHA, 32)
        self.build_base()
        self.image = self.base

    def build_base(self):
        mower_base = pg.Surface([MOWER_DIAMETER, MOWER_DIAMETER], pg.SRCALPHA, 32)
        #        mower_base = mower_base.convert_alpha()
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

    def right_back(self):
        rb = Coord(MOWER_DIAMETER / 2, -MOWER_DIAMETER / 2)
        rb = rb.rot(self.angle_in_degrees)
        rb = rb + self.centre
        return rb

    def left_back(self):
        lb = Coord(-MOWER_DIAMETER / 2, -MOWER_DIAMETER / 2)
        lb = lb.rot(self.angle_in_degrees)
        lb = lb + self.centre
        return lb

    def right_front(self):
        rf = Coord(MOWER_DIAMETER / 2, MOWER_DIAMETER / 2)
        rf = rf.rot(self.angle_in_degrees)
        rf = rf + self.centre
        return rf

    def left_front(self):
        lf = Coord(-MOWER_DIAMETER / 2, MOWER_DIAMETER / 2)
        lf = lf.rot(self.angle_in_degrees)
        lf = lf + self.centre
        return lf

    def build_image(self):
        # Get the base image
        mower_img = self.base

        # Create a rotated front wheel image
        wheel_img = pg.Surface([WHEEL_SIZE[0] + 2, WHEEL_SIZE[1] + 2], pg.SRCALPHA, 32)
        wheel_img = wheel_img.convert_alpha()
        pg.draw.rect(wheel_img,
                     WHEEL_COLOUR,
                     (1, 1) + WHEEL_SIZE)
        wheel_img = pg.transform.rotate(wheel_img, math.radians(self.wheel_angle_in_degrees))

        # Draw right front wheel on the mower
        mower_img.blit(wheel_img, self.right_front().coord())

        # Draw left front wheel on the mower
        mower_img.blit(wheel_img, self.left_front().coord())

        self.image = mower_img

    def drive(self):
        # Change to radians
        steering_angle_in_radians_abs = abs(math.radians(self.wheel_angle_in_degrees))

        # Calculate the rotational centre point based on the steering angle
        pivot_ratio = math.tan(math.pi / 2 - abs(steering_angle_in_radians_abs))

        if self.wheel_angle_in_degrees > 0:

            # Calculate the centre point about which the mower will turn
            centre = self.right_back() + (self.right_back() - self.left_back()) * pivot_ratio
            # this centre is not the correct centre if the angle is negative or if the mower is heading down
            # It's just used to get the correct rotational angle below

            # Calculate the rotation angle based on the far back wheel moving SPEED
            rotational_angle_in_radians = 2 * math.atan(
                (SPEED / 2) / (MOWER_DIAMETER + MOWER_DIAMETER * pivot_ratio))

        elif self.wheel_angle_in_degrees < 0:

            # Calculate the centre point about which the mower will turn
            centre = self.left_back() + (self.left_back() - self.right_back()) * pivot_ratio

            # Calculate the rotation angle based on the far back wheel moving SPEED
            # (positive because turning anti-clockwise)
            rotational_angle_in_radians = -2 * math.atan(
                (SPEED / 2) / (MOWER_DIAMETER + MOWER_DIAMETER * pivot_ratio))

        else:
            centre = Coord(0, 0)
            rotational_angle_in_radians = 0

        self.centre = self.centre.rotate_about_centre(centre, rotational_angle_in_radians)

        new_left_back = self.left_back().rotate_about_centre(centre, rotational_angle_in_radians)
        new_left_front = self.left_front().rotate_about_centre(centre, rotational_angle_in_radians)

        self.angle_in_degrees = math.degrees(math.atan((new_left_front.x - new_left_back.x) / (new_left_front.y - new_left_back.y)))

    def steer(self, delta_angle_in_degrees):
        # if delta_angle_in_degrees > MAX_STEER_ANGLE_CHANGE:
        #     delta_angle_in_degrees = MAX_STEER_ANGLE_CHANGE
        # if delta_angle_in_degrees < -MAX_STEER_ANGLE_CHANGE:
        #     delta_angle_in_degrees = -MAX_STEER_ANGLE_CHANGE

        if (self.wheel_angle_in_degrees + delta_angle_in_degrees) > MAX_STEER_ANGLE:
            self.wheel_angle_in_degrees = MAX_STEER_ANGLE
        elif (self.wheel_angle_in_degrees + delta_angle_in_degrees) < -MAX_STEER_ANGLE:
            self.wheel_angle_in_degrees = -MAX_STEER_ANGLE
        else:
            self.wheel_angle_in_degrees += delta_angle_in_degrees


class Field:
    def __init__(self):

        self.grass = pg.Surface(FIELD_SIZE)
        self.grass.fill(GRASS_UNCUT_COLOUR)

    def count_colour(self, colour):
        count = 0
        for i in range(FIELD_SIZE[0]):
            for j in range(FIELD_SIZE[1]):
                if self.grass.get_at((i, j))[0:3] == colour:
                    count += 1
        return count

    def mow(self, this_mower):
        pg.draw.circle(self.grass, GRASS_CUT_COLOUR, this_mower.centre.coord(), MOWER_DIAMETER / 2)


pg.init()
mower = Mower()
field = Field()
clock = pg.time.Clock()
screen = pg.display.set_mode(FIELD_SIZE)
screen.blit(field.grass, (0, 0))

# rect = pg.Rect(0, 0, 20, 20)
# rect.center = field.grass.get_rect().center
vel = 5

run = True
while run:
    clock.tick(2000)
    for event in pg.event.get():
        if event.type == pg.QUIT:
            run = False
        if event.type == pg.KEYDOWN:
            time.sleep(0.1)
            # print(pg.key.name(event.key))

    keys = pg.key.get_pressed()

    # Now control the mower
    if keys[pg.K_q]:
        screen.blit(field.grass, screen.get_rect().center)
    if keys[pg.K_w]:
        mower.build_image()
        screen.blit(mower.image, (mower.centre.x, mower.centre.y))
    if keys[pg.K_e]:
        field.mow(mower)
    if keys[pg.K_r]:
        screen.blit(field.grass, (0, 0))
    if keys[pg.K_t]:
        pg.draw.circle(field.grass, GRASS_CUT_COLOUR, mower.centre.coord(), MOWER_DIAMETER / 2)
    if keys[pg.K_LEFT]:
        mower.steer(-10)
    if keys[pg.K_RIGHT]:
        mower.steer(10)
    if keys[pg.K_UP]:
        # Mow the field where the mower is now
        # field.mow(mower)
        pg.draw.circle(field.grass, GRASS_CUT_COLOUR, mower.centre.coord(), MOWER_DIAMETER / 2)
        mower.drive()
        print("screen center: ", screen.get_rect().center)
        screen.blit(field.grass, (0, 0))
        screen.blit(mower.image, (mower.centre - Coord(mower.image.get_width() / 2, mower.image.get_height() / 2)).coord())

    # # Show the cut grass
    # screen.blit(field.grass, screen.get_rect().center)
    # # Load the mower image on top
    # mower.build_image()
    # screen.blit(mower.image, (mower.centre.x, mower.centre.y))
    # # print(mower.centre.x, mower.centre.y, mower.centre.coord())

    # Display the window
    pg.display.set_caption("Mower", "Mow")
    pg.display.flip()

pg.quit()
exit()
