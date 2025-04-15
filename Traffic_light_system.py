import pygame
import math
import random

pygame.init()

WIDTH, HEIGHT = 1500, 800
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Traffic Light System")

car_image = pygame.image.load("car.png")
car_image = pygame.transform.scale(car_image, (30, 30))
pygame.mouse.set_visible(False)


BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (34, 139, 34)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GRAY = (50, 50, 50)


RED_LIGHT = 0
YELLOW_LIGHT = 1
GREEN_LIGHT = 2


GREEN_TIME = 180
YELLOW_TIME = 60

CIRCLE_CENTER = (750, 400)
OUTER_RADIUS = 270
INNER_RADIUS = 170
CAR_SPEED = 3
EXIT_SPEED = 5


class TrafficLight:
    def __init__(self, x, y, is_horizontal, facing_right_or_down, exit_dir, name):
        self.x = x
        self.y = y
        self.is_horizontal = is_horizontal
        self.facing_right_or_down = facing_right_or_down
        self.exit_dir = exit_dir
        self.name = name
        self.state = RED_LIGHT
        self.queue = []

    def draw_light(self):
        light_size = (25, 80) if not self.is_horizontal else (80, 25)
        light_rect = pygame.Rect(self.x, self.y, *light_size)
        pygame.draw.rect(win, BLACK, light_rect)
        if self.state == RED_LIGHT:
            pygame.draw.circle(win, RED, (self.x + 12, self.y + 12), 7)
        elif self.state == YELLOW_LIGHT:
            pygame.draw.circle(win, YELLOW, (self.x + 12, self.y + 40), 7)
        elif self.state == GREEN_LIGHT:
            pygame.draw.circle(win, GREEN, (self.x + 12, self.y + 65), 7)

    def add_car_to_queue(self, x, y):
        if len(self.queue) < 10:
            offset = random.choice([-10, 10])
            if self.is_horizontal:
                self.queue.append([x, self.y + offset, 0, CAR_SPEED])
            else:
                self.queue.append([self.x + offset, y, 0, CAR_SPEED])

    def draw_queue(self):
        for car in self.queue:
            win.blit(car_image, (car[0], car[1]))

    def move_cars(self):
        new_queue = []
        for car in self.queue:
            if self.state == GREEN_LIGHT:
                if car[2] == 0:
                    if self.is_horizontal:
                        car[0] += car[3] if self.facing_right_or_down else -car[3]
                        if (self.facing_right_or_down and car[0] >= 500) or (not self.facing_right_or_down and car[0] <= 1000):
                            car[2] = 1
                    else:
                        car[1] += car[3] if self.facing_right_or_down else -car[3]
                        if (self.facing_right_or_down and car[1] >= 180) or (not self.facing_right_or_down and car[1] <= 540):
                            car[2] = 1
                elif car[2] == 1:
                    angle = math.atan2(car[1] - CIRCLE_CENTER[1], car[0] - CIRCLE_CENTER[0])
                    angle += 0.04
                    car[0] = CIRCLE_CENTER[0] + OUTER_RADIUS * math.cos(angle)
                    car[1] = CIRCLE_CENTER[1] + OUTER_RADIUS * math.sin(angle)
                    if self.check_exit(car):
                        car[2] = 2
                elif car[2] == 2:
                    if self.exit_dir == "right":
                        car[0] += EXIT_SPEED
                    elif self.exit_dir == "left":
                        car[0] -= EXIT_SPEED
                    elif self.exit_dir == "up":
                        car[1] -= EXIT_SPEED
                    elif self.exit_dir == "down":
                        car[1] += EXIT_SPEED
                    if car[0] < 0 or car[0] > WIDTH or car[1] < 0 or car[1] > HEIGHT:
                        continue
            new_queue.append(car)
        self.queue = new_queue

    def check_exit(self, car):
        if self.exit_dir == "right" and car[0] > 800 and 360 < car[1] < 440:
            return True
        elif self.exit_dir == "left" and car[0] < 690 and 360 < car[1] < 440:
            return True
        elif self.exit_dir == "up" and car[1] < 360 and 720 < car[0] < 780:
            return True
        elif self.exit_dir == "down" and car[1] > 440 and 720 < car[0] < 780:
            return True
        return False


lights = [
    TrafficLight(740, 270, False, True, "down", "north"),
    TrafficLight(740, 450, False, False, "up", "south"),
    TrafficLight(620, 380, True, True, "right", "west"),
    TrafficLight(810, 380, True, False, "left", "east"),
]


def draw_environment():
    win.fill(WHITE)
    pygame.draw.rect(win, GRAY, (0, 290, WIDTH, 220))
    pygame.draw.line(win, WHITE, (0, 390), (WIDTH, 390), 5)
    pygame.draw.line(win, WHITE, (0, 410), (WIDTH, 410), 5)
    pygame.draw.rect(win, GRAY, (640, 0, 220, HEIGHT))
    pygame.draw.line(win, WHITE, (740, 0), (740, HEIGHT), 5)
    pygame.draw.line(win, WHITE, (760, 0), (760, HEIGHT), 5)
    pygame.draw.circle(win, GRAY, CIRCLE_CENTER, OUTER_RADIUS)
    pygame.draw.circle(win, GREEN, CIRCLE_CENTER, INNER_RADIUS)


phase_order = ["north", "west", "south", "east"]
phase_index = 0
phase_timer = GREEN_TIME
yellow_phase = False

def update_traffic_lights():
    global phase_index, phase_timer, yellow_phase
    if phase_timer <= 0:
        if yellow_phase:
            phase_index = (phase_index + 1) % 4
            yellow_phase = False
            phase_timer = GREEN_TIME
        else:
            yellow_phase = True
            phase_timer = YELLOW_TIME

        for light in lights:
            if light.name == phase_order[phase_index]:
                light.state = YELLOW_LIGHT if yellow_phase else GREEN_LIGHT
            else:
                light.state = RED_LIGHT
    else:
        phase_timer -= 1


def get_road_for_mouse(x, y):
    if 290 <= y <= 510:
        return lights[2] if x < 750 else lights[3]
    elif 640 <= x <= 860:
        return lights[0] if y < 400 else lights[1]
    return None

clock = pygame.time.Clock()
running = True

while running:
    draw_environment()

    mouse_x, mouse_y = pygame.mouse.get_pos()
    win.blit(car_image, (mouse_x - 20, mouse_y - 20))

    for light in lights:
        light.draw_light()
        light.draw_queue()
        light.move_cars()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            selected = get_road_for_mouse(mouse_x, mouse_y)
            if selected:
                selected.add_car_to_queue(mouse_x, mouse_y)

    update_traffic_lights()
    pygame.display.update()
    clock.tick(60)

pygame.quit()
