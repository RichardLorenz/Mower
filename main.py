
import sys
from PIL import Image, ImageDraw
import math
import numpy as np
import pygame as pg


MOWER_DIAMETER = 20
FIELD_SIZE = 800
GRASS_UNCUT_COLOUR = (0, 100, 0)
GRASS_CUT_COLOUR = (0, 255, 0)
SPEED = 5
MAX_STEER_ANGLE_CHANGE = 10
MAX_STEER_ANGLE = 80


def rotate_about_centre(point, centre, angle_in_radians):
    # angle_in_radians = (angle_in_degrees / 180) * math.pi

    # Set up the rotation matrix
    rotation_matrix = np.array([[math.cos(angle_in_radians), math.sin(angle_in_radians)],
                                [-math.sin(angle_in_radians), math.cos(angle_in_radians)]])

    translated_point = point - centre

    rotated_point = np.matmul(translated_point, rotation_matrix)

    translate_back = rotated_point + centre

    return translate_back


class Field:
    def __init__(self):
        self.screen = pg.display.set_mode((FIELD_SIZE, FIELD_SIZE))

    def mow(self):
        pg.draw.circle(self.screen, (0, 255, 0), mower.centre(), MOWER_DIAMETER / 2)

    def show_mower(self):
        x = 1

    def show(self):
        pg.display.update()


class Mower:
    def __init__(self):

        self.right_back = np.array([0, 0], dtype=float)
        self.left_back = np.array([MOWER_DIAMETER, 0], dtype=float)
        self.steer_angle_in_degrees = -10

    def left_front(self):
        left_front_x = self.left_back[0] + (self.left_back[1] - self.right_back[1])
        left_front_y = self.left_back[1] + (self.left_back[0] - self.right_back[0])
        return np.array([left_front_x, left_front_y], dtype=float)

    def right_front(self):
        right_front_x = self.right_back[0] + (self.left_back[1] - self.right_back[1])
        right_front_y = self.right_back[1] + (self.left_back[0] - self.right_back[0])
        return np.array([right_front_x, right_front_y], dtype=float)

    def centre(self):
        min_x = min(self.left_back[0], self.right_back[0], self.left_front()[0], self.right_front()[0])
        max_x = max(self.left_back[0], self.right_back[0], self.left_front()[0], self.right_front()[0])
        min_y = min(self.left_back[1], self.right_back[1], self.left_front()[1], self.right_front()[1])
        max_y = max(self.left_back[1], self.right_back[1], self.left_front()[1], self.right_front()[1])
        return np.array([min_x + (max_x - min_x) / 2, min_y + (max_y - min_y) / 2], dtype=float)

    def ellipse_bound(self):
        centre = self.centre()
        return [(centre[0] - MOWER_DIAMETER/2, centre[1] - MOWER_DIAMETER/2),
                (centre[0] + MOWER_DIAMETER/2, centre[1] + MOWER_DIAMETER/2)]

    def drive(self, direction_and_speed):
        # Change to radians
        steering_angle_in_radians_abs = abs(math.radians(self.steer_angle_in_degrees))

        # Calculate the rotational centre point based on the steering angle
        pivot_ratio = math.tan(math.pi / 2 - abs(steering_angle_in_radians_abs))

        if self.steer_angle_in_degrees > 0:

            # Calculate the centre point about which the mower will turn
            centre = self.right_back + pivot_ratio * (self.right_back - self.left_back)

            # Calculate the rotation angle based on the far back wheel moving SPEED
            # (negative because turning clockwise)
            rotational_angle_in_radians = 2 * math.atan((SPEED / 2) / (MOWER_DIAMETER + MOWER_DIAMETER * pivot_ratio))

        elif self.steer_angle_in_degrees < 0:

            # Calculate the centre point about which the mower will turn
            centre = self.left_back + pivot_ratio * (self.left_back - self.right_back)

            # Calculate the rotation angle based on the far back wheel moving SPEED
            # (positive because turning anti-clockwise)
            rotational_angle_in_radians = -2 * math.atan((SPEED / 2) / (MOWER_DIAMETER + MOWER_DIAMETER * pivot_ratio))

        else:
            centre = np.array([0, 0], dtype=float)
            rotational_angle_in_radians = 0

        new_left_back  = rotate_about_centre(self.left_back,  centre, rotational_angle_in_radians)
        new_right_back = rotate_about_centre(self.right_back, centre, rotational_angle_in_radians)

        self.left_back  = new_left_back
        self.right_back = new_right_back

    def steer(self, delta_angle_in_degrees):
        if delta_angle_in_degrees > MAX_STEER_ANGLE_CHANGE:
            delta_angle_in_degrees = MAX_STEER_ANGLE_CHANGE
        if delta_angle_in_degrees < -MAX_STEER_ANGLE_CHANGE:
            delta_angle_in_degrees = -MAX_STEER_ANGLE_CHANGE

        if (self.steer_angle_in_degrees + delta_angle_in_degrees) > MAX_STEER_ANGLE:
            self.steer_angle_in_degrees = MAX_STEER_ANGLE
        elif (self.steer_angle_in_degrees + delta_angle_in_degrees) < -MAX_STEER_ANGLE:
            self.steer_angle_in_degrees = -MAX_STEER_ANGLE
        else:
            self.steer_angle_in_degrees += delta_angle_in_degrees


def drive_and_show(field, speed, delta_angle_in_degrees):
    mower.steer(delta_angle_in_degrees)
    mower.drive(speed)
    pg.draw.circle(field, (0, 255, 0), mower.centre(), MOWER_DIAMETER / 2)
    print(mower.ellipse_bound(), mower.steer_angle_in_degrees)
    pg.display.update()


# field = Field()
mower = Mower()
# Initialise pygame
pg.init()
field = pg.display.set_mode((FIELD_SIZE, FIELD_SIZE))

done = False
while not done:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            done = True
    drive_and_show(field, SPEED, 0)



