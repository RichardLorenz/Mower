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


class Coord:

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, p):
        return [self.x + p.x, self.y + p.y]

    def mult(self, p, m):
        return [p[0] * m[0][0] + p[1] * m[0][1],
                p[0] * m[1][0] + p[1] * m[1][1]]

    def rot(self, p, a):
        # Note: a is in radians
        m = [[math.cos(a), math.sin(a)], [-math.sin(a), math.cos(a)]]
        return coord_mult(p, m)

    def list_rot(self, lst, a):
        l2 = []
        for p in lst:
            l2.append(coord_rot(p, a))
        return l2

    def list_add(self, lst, a):
        l2 = []
        for p in lst:
            l2.append(coord_add(p, a))
        return l2


def rotate_about_centre(point, centre, angle_in_radians):
    # angle_in_radians = (angle_in_degrees / 180) * math.pi

    # Set up the rotation matrix
    rotation_matrix = np.array([[math.cos(angle_in_radians), math.sin(angle_in_radians)],
                                [-math.sin(angle_in_radians), math.cos(angle_in_radians)]])

    translated_point = point - centre

    rotated_point = np.matmul(translated_point, rotation_matrix)

    translate_back = rotated_point + centre

    return translate_back


class Mower:
    def __init__(self):

        self.centre = [MOWER_DIAMETER / 2, MOWER_DIAMETER / 2]
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
        rb = [MOWER_DIAMETER/2, MOWER_DIAMETER/2]
        rb = coord_rot(rb, self.angle_in_degrees)
        rb = coord_add(rb, self.centre)
        return rb

    def left_back(self):
        lb = [-MOWER_DIAMETER/2, -MOWER_DIAMETER/2]
        lb = coord_rot(lb, self.angle_in_degrees)
        lb = coord_add(lb, self.centre)
        return lb

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
        mower_img.blit(wheel_img, (WHEEL_SIZE[0] / 2 + 1, WHEEL_SIZE[1] / 2 + 1))

        # Draw left front wheel on the mower
        mower_img.blit(wheel_img, (WHEEL_SIZE[0] / 2 + MOWER_DIAMETER + 1, WHEEL_SIZE[1] / 2 + 1))

        self.image = mower_img

    def drive(self, direction_and_speed):
        # Change to radians
        steering_angle_in_radians_abs = abs(math.radians(self.steer_angle_in_degrees))

        # Calculate the rotational centre point based on the steering angle
        pivot_ratio = math.tan(math.pi / 2 - abs(steering_angle_in_radians_abs))

        if self.steer_angle_in_degrees > 0:

            # Calculate the centre point about which the mower will turn
            centre = self.right_back() + pivot_ratio * coord_add(self.right_back(), -1 * self.left_back())
            # this centre is not the correct centre if the angle is negative or if the mower is heading down
            # It's just used to get the correct rotational angle below

            # Calculate the rotation angle based on the far back wheel moving SPEED
            # (negative because turning clockwise)
            rotational_angle_in_radians = 2 * math.atan(
                (SPEED / 2) / (MOWER_DIAMETER + MOWER_DIAMETER * pivot_ratio))

        elif self.steer_angle_in_degrees < 0:

            # Calculate the centre point about which the mower will turn
            centre = self.left_back + pivot_ratio * (self.left_back - self.right_back)

            # Calculate the rotation angle based on the far back wheel moving SPEED
            # (positive because turning anti-clockwise)
            rotational_angle_in_radians = -2 * math.atan(
                (SPEED / 2) / (MOWER_DIAMETER + MOWER_DIAMETER * pivot_ratio))

        else:
            centre = np.array([0, 0], dtype=float)
            rotational_angle_in_radians = 0

        new_left_back = rotate_about_centre(self.left_back, centre, rotational_angle_in_radians)
        new_right_back = rotate_about_centre(self.right_back, centre, rotational_angle_in_radians)

        self.left_back = new_left_back
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
        pg.draw.circle(self.grass, GRASS_CUT_COLOUR, this_mower.centre, MOWER_DIAMETER / 2)


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
    clock.tick(1000)
    for event in pg.event.get():
        if event.type == pg.QUIT:
            run = False
        if event.type == pg.KEYDOWN:
            screen.blit(field.grass, (0, 0))
            print(pg.key.name(event.key))

    keys = pg.key.get_pressed()

    if keys[pg.K_q]:
        screen.blit(mower.base, (0, 0))
    if keys[pg.K_w]:
        screen.blit(mower.image, (0, 0))
    if keys[pg.K_e]:
        field.mow(mower)
    if keys[pg.K_r]:
        print("r")
        screen.blit(field.grass, (0, 0))
    # if keys[pg.K_t]:
    #     # nothing
    if keys[pg.K_LEFT]:
        print("keys_x", keys[pg.K_x])
        pg.draw.rect(field.grass, (0, 0, 255), rect)
        field.grass.blit(mower.base, (200, 200))
    elif keys[pg.K_RIGHT]:
        rect.x += (keys[pg.K_RIGHT] - keys[pg.K_LEFT]) * vel
        rect.y += (keys[pg.K_DOWN] - keys[pg.K_UP]) * vel

        rect.centerx = rect.centerx % field.grass.get_width()
        rect.centery = rect.centery % field.grass.get_height()

        field.grass.fill(0)
        pg.draw.rect(field.grass, (255, 0, 0), rect)
    elif keys[pg.K_UP]:
        field.grass.blit(mower.base, (300, 300))
    elif keys[pg.K_DOWN]:
        mower.build_image()
        field.grass.blit(mower.image, (400, 400))
    else:
        pg.display.flip()

pg.quit()
exit()
