import math
import pygame
import serial
import time

# constants
BUTTONS = {"JCON_UP", "JCON_DOWN", "JCON_LEFT", "JCON_RIGHT", "DUP", "DDOWN", "DLEFT", "DRIGHT", "SR", "SL", "MINUS"}

SERIAL_PORT = "/dev/tty.usbmodem11301" # replace with current serial port
FPS = 60

JOYSTICK_X = 0 # -1 to 1
JOYSTICK_Y = 0 # -1 to 1

KEYS = {
    pygame.K_w: (False, 0),
    pygame.K_a: (False, 0),
    pygame.K_s: (False, 0),
    pygame.K_d: (False, 0),
    pygame.K_h: (False, 0),
    pygame.K_j: (False, 0),
    pygame.K_k: (False, 0),
    pygame.K_l: (False, 0),
    pygame.K_y: (False, 0),
    pygame.K_u: (False, 0),
    pygame.K_1: (False, 0)
}

# initialize serial connection and pygame
# ser = serial.Serial(SERIAL_PORT, 115200) 

pygame.init()
screen = pygame.display.set_mode((640, 480))
pygame.display.set_caption("Keyboard Demo")

clock = pygame.time.Clock()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key in KEYS:
                KEYS[event.key] = (True, time.time())
        elif event.type == pygame.KEYUP:
            if event.key in KEYS:
                KEYS[event.key] = (False, 0)

    # update joystick position based on mouse movement
    mouse_x, mouse_y = pygame.mouse.get_pos()
    JOYSTICK_X = mouse_x
    JOYSTICK_Y = mouse_y

    # normalize the stick within the circle
    center_x, center_y = 320, 240
    JOYSTICK_X -= center_x
    JOYSTICK_Y -= center_y
    radius = math.hypot(JOYSTICK_X, JOYSTICK_Y)
    if radius > 200: 
        # forces radius to 180
        JOYSTICK_X = JOYSTICK_X / radius * 200
        JOYSTICK_Y = JOYSTICK_Y / radius * 200

    screen.fill((0, 0, 0))
    circle = pygame.draw.circle(screen, (0, 255, 0), (320, 240), 200, 4)
    pointer_indicator = pygame.draw.circle(screen, (255, 0, 0), (int((JOYSTICK_X + center_x)), int((JOYSTICK_Y + center_y))), 5)
    pygame.display.flip()

    JOYSTICK_X /= 200
    JOYSTICK_Y /= 200
    report = f"{JOYSTICK_X:.4f},{JOYSTICK_Y:.4f},{int(KEYS[pygame.K_h][0])},{int(KEYS[pygame.K_j][0])},{int(KEYS[pygame.K_k][0])},{int(KEYS[pygame.K_l][0])},{int(KEYS[pygame.K_y][0])},{int(KEYS[pygame.K_u][0])},{int(KEYS[pygame.K_1][0])}\n"
    print(report)
    clock.tick(FPS)

pygame.quit()