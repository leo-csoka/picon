import math
import pygame
import serial
import time

# constants
BUTTONS = {"JCON_UP", "JCON_DOWN", "JCON_LEFT", "JCON_RIGHT", "DUP", "DDOWN", "DLEFT", "DRIGHT", "SR", "SL", "MINUS"}

SERIAL_PORT = "/dev/tty.usbmodem1301" # replace with current serial port
FRICTION_CONSTANT = 0.9 # slow down current velocity and recenter position on release
ACCELERATION_CONSTANT = 0.007 # velocity added per frame
KICK_CONSTANT = 0.25 # kick to simulate a tap
FPS = 60

VELOCITY_X = 0
VELOCITY_Y = 0
JOYSTICK_X = 0 # -1 to 1
JOYSTICK_Y = 0 # -1 to 1

MOVE_KEYS = {
    pygame.K_w: (1, 0),
    pygame.K_s: (-1, 0),
    pygame.K_a: (0, 1),
    pygame.K_d: (0, -1)
}

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
ser = serial.Serial(SERIAL_PORT, 115200) 

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
            if event.key in MOVE_KEYS:
                JOYSTICK_X += KICK_CONSTANT * MOVE_KEYS[event.key][0]
                JOYSTICK_Y += KICK_CONSTANT * MOVE_KEYS[event.key][1]
        elif event.type == pygame.KEYUP:
            if event.key in KEYS:
                KEYS[event.key] = (False, 0)

    # fix frame rate
    clock.tick(FPS)

    # key input per axis, -1, 0, 1 -> (w/s for x, a/d for y) (split j-con)
    x_input = MOVE_KEYS[pygame.K_w][0] * KEYS[pygame.K_w][0] + MOVE_KEYS[pygame.K_s][0] * KEYS[pygame.K_s][0]
    y_input = MOVE_KEYS[pygame.K_a][1] * KEYS[pygame.K_a][0] + MOVE_KEYS[pygame.K_d][1] * KEYS[pygame.K_d][0]

    input_length = math.hypot(x_input, y_input)
    if input_length:
        # scale acceleration by input length to normalize diagonals
        VELOCITY_X += ACCELERATION_CONSTANT * x_input / input_length
        VELOCITY_Y += ACCELERATION_CONSTANT * y_input / input_length

    VELOCITY_X *= FRICTION_CONSTANT
    VELOCITY_Y *= FRICTION_CONSTANT

    # change position based on velocity, apply friction if no input to recenter
    JOYSTICK_X = JOYSTICK_X * (1 if x_input else FRICTION_CONSTANT) + VELOCITY_X
    JOYSTICK_Y = JOYSTICK_Y * (1 if y_input else FRICTION_CONSTANT) + VELOCITY_Y

    # normalize the stick within the unit circle
    radius = math.hypot(JOYSTICK_X, JOYSTICK_Y)
    if radius > 1: 
        # forces radius to 1
        JOYSTICK_X /= radius
        JOYSTICK_Y /= radius

        # equivalent to [v_x, v_y] dot [x, y] -> if > 0, pointing outward
        outward = sum(v * p for v, p in zip((VELOCITY_X, VELOCITY_Y), (JOYSTICK_X, JOYSTICK_Y)))
        if outward > 0:
            VELOCITY_X -= outward * JOYSTICK_X
            VELOCITY_Y -= outward * JOYSTICK_Y

    # return controller state report over serial to rpi pico w
    report = f"{JOYSTICK_X:.4f},{JOYSTICK_Y:.4f},{int(KEYS[pygame.K_h][0])},{int(KEYS[pygame.K_j][0])},{int(KEYS[pygame.K_k][0])},{int(KEYS[pygame.K_l][0])},{int(KEYS[pygame.K_y][0])},{int(KEYS[pygame.K_u][0])},{int(KEYS[pygame.K_1][0])}\n"
    print(report, end='')
    ser.write(report.encode())


pygame.quit()