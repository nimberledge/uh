import pygame
import math
import colorsys
import time
import random

BLACK = (0, 0, 0)

class Circle(object):
    # These were planned to be ellipses but I'd have to create like a pygame rect
    # painful so i just did circles
    MASS_SCALING_FACTOR = 1
    BREATHE_SEQUENCE = [1.0, 1.05, 1.1, 1.15, 1.1, 1.05, 1.0, 0.95, 0.9, 0.85, 0.9, 0.95]
    BREATHE_DELAY = 0.4

    def __init__(self, x, y, radius, color, u_direction, velocity=0.1):
        # u_direction -> initial velocity direction
        self.x, self.y, self.base_radius, self.color = x, y, radius, color
        self.radius = self.base_radius
        self.exact_xy = [self.x, self.y] # Round this to update
        self.mass = self.radius * self.MASS_SCALING_FACTOR
        self.velocity = velocity # magnitude of velocity
        self.u_direction = u_direction # Initial velocity direction
        self.breathe_state = 0
        self.acc = [0, 0]
        self.last_breath = time.time()

    def update(self, objects, breathe_timer, dt=0.02):
        # Acceleration update
        acc = [0, 0]
        for obj in objects:
            obj_acceleration = obj.get_acceleration(self)
            acc[0] += obj_acceleration[0]
            acc[1] += obj_acceleration[1]
        self.acc[0] += acc[0]
        self.acc[1] += acc[1]

        x_vel = self.velocity * self.u_direction[0] + dt * self.acc[0]
        y_vel = self.velocity * self.u_direction[0] + dt * self.acc[1]
        # Velocity update
        exact_x, exact_y = self.exact_xy
        exact_x += x_vel
        exact_y += y_vel
        self.exact_xy = [exact_x, exact_y]
        self.x, self.y = [int(self.exact_xy[i]) for i in range(2)]
        # TODO: update the hue
        # TODO: Add a breathing effect
        # Breathing - change radius periodically
        if breathe_timer - self.last_breath >= self.BREATHE_DELAY:
            self.breathe_state = (self.breathe_state + 1) % len(self.BREATHE_SEQUENCE)
            self.radius = int(self.base_radius * self.BREATHE_SEQUENCE[self.breathe_state])
            self.last_breath = time.time()


    def draw(self, screen):
        if (-self.radius <= self.x < screen.get_width() + self.radius and -self.radius <= self.y < screen.get_height() + self.radius):
            pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)


class PointMass(object):
    EPSILON = 0.000001
    def __init__(self, x, y, mass):
        self.x, self.y, self.mass = x, y, mass

    def get_acceleration(self, ellipse):
        # Assume gravitational constant is 1 fuck it let's be physicists
        r = math.sqrt((self.x - ellipse.x)**2 + (self.y - ellipse.y)**2)
        if r == 0:
            r += self.EPSILON
        acc = self.mass / r**2
        theta = math.acos((self.x - ellipse.x) / r)
        return [acc * math.cos(theta), acc * math.sin(theta)]

    def update_position(self, x, y):
        self.x, self.y = x, y



def screen_test():
    # Some constants
    SPIRAL_ANGLE_DEG = 137.3
    SPIRAL_ANGLE_RAD = SPIRAL_ANGLE_DEG * math.pi / 180
    STATIC_COL = (142, 26, 220)
    MOST_ELLIPSES = 10000
    STATIONARY_PROB = 0.1 # Probability with which they have 0 starting velocity
    pygame.init()
    # pygame.font.init()

    screen_size = (1920, 1080)
    screen = pygame.display.set_mode(screen_size)
    pygame.display.set_caption("L S D")

    screen.fill(BLACK)
    # Hue, saturation, luminance
    h,s,l = 14, 0.4, 0.55
    hue_change_rate = 0.001

    done = False
    generate = True
    ellipses = []
    c = 12                  # Spiral radius constant
    start = time.time()
    gen_rate = 0.00005       # Delay in seconds between drawing ellipses
    n = 0
    mass_r = 600
    mass_theta = math.pi / 2
    test_mass = PointMass(int(mass_r * math.cos(mass_theta) + screen_size[0]/2), int(mass_r * math.cos(mass_theta) + screen_size[1]/2), 100)
    # test_mass_2 = PointMass(screen_size[0] + 20, screen_size[1] + 20, 100)
    mpos_mass = PointMass(int(mass_r * math.cos(mass_theta) + screen_size[0]/2), int(mass_r * math.cos(mass_theta) + screen_size[1]/2), -1000)
    objects = [mpos_mass]
    mass_angle_step = 0.01
    spiral_center = (screen.get_width() / 2, screen.get_height() /2)
    while not done:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                done = True
                continue
            elif event.type == pygame.MOUSEBUTTONDOWN and not generate:
                generate = True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Start pattern again at new random color, within some reason
                h, s, l = (random.uniform(0, 255), random.uniform(0.4, 0.5), 0.55)
                n = 0
                spiral_center = pygame.mouse.get_pos()



        if generate and (time.time()-start) >= gen_rate: # Generate more ellipses
            n += 1
            # theta, r for coordinates
            theta = n * SPIRAL_ANGLE_RAD
            r = c * math.sqrt(n)

            # Convert back, and place relative to spiral center
            # width, height = screen.get_width(), screen.get_height()
            x, y = int(r * math.cos(theta) + spiral_center[0]), int(r * math.sin(theta) + spiral_center[1])

            # Get color in RGB
            color = colorsys.hls_to_rgb(h, l, s)
            color = tuple([k * 255 for k in color])
            # color = STATIC_COL

            # Pick radius of circle, initial velocity
            # radius = int(random.uniform(10, 20))
            # radius = int(random.uniform(1, 5))
            radius = 6
            # print (color)
            v_dir = [math.cos(theta), math.sin(theta)] # Direction of velocity
            vel = 0.0005 * n

            # experiment -
            # vel = random.triangular(0, 0.02)
            # # coin_flip = random.random()
            # if n < MOST_ELLIPSES // 10:
            #     vel = 0.0002

            ellipses.append(Circle(x, y, radius, color, v_dir, velocity=vel))
            h = (h + hue_change_rate) % 360 # The magic
            # Reset clock so that you don't generate too many
            start = time.time()

        mpos = pygame.mouse.get_pos()
        # print (mpos)
        mpos_mass.update_position(mpos[0], mpos[1])
        # Update the mass angle, and move the mass
        mass_theta = mass_theta + mass_angle_step
        if mass_theta >= 2 * math.pi:
            mass_theta = 0
        test_mass.update_position(int(mass_r * math.cos(mass_theta) + screen_size[0]/2), int(mass_r * math.cos(mass_theta) + screen_size[1]/2))
        # print ("Mass coordinates: {} {}".format(test_mass.x, test_mass.y))


        if len(ellipses) >= MOST_ELLIPSES:
            del ellipses[0]

        screen.fill(BLACK)
        for ellipse in ellipses:
            ellipse.update(objects, time.time())
            ellipse.draw(screen)

        pygame.display.flip()
    pygame.quit()

if __name__ == '__main__':
    screen_test()
    print ("Brought to you by LSD")
    # test_test()
