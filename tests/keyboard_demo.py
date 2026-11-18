import math
import pygame
import serial
import time

# constants
BUTTONS = {"JCON_UP", "JCON_DOWN", "JCON_LEFT", "JCON_RIGHT", "Y", "X", "A", "B", "L", "R", "ZL", "ZR", "MINUS", "PLUS"}

SERIAL_PORT_RIGHT = "/dev/tty.usbmodem11301" # replace with current serial port
SERIAL_PORT_LEFT = "/dev/tty.usbmodem11401" # replace with current serial port
FRICTION_CONSTANT = 0.9 # slow down current velocity and recenter position on release
ACCELERATION_CONSTANT = 0.007 # velocity added per frame
KICK_CONSTANT = 0.2 # kick to simulate a tap
FPS = 60

VELOCITY_X = 0
VELOCITY_Y = 0
JOYSTICK_X = 0 # -1 to 1
JOYSTICK_Y = 0 # -1 to 1

LEFT_JOYSTICK_X = 0 # -1 to 1
LEFT_JOYSTICK_Y = 0 # -1 to 1

MOVE_KEYS = {
    # determines direction of motion
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
    pygame.K_i: (False, 0),
    pygame.K_o: (False, 0),
    pygame.K_1: (False, 0),
    pygame.K_2: (False, 0)
}


# initialize serial connection and pygame
ser_left = serial.Serial(SERIAL_PORT_LEFT, 115200) 
ser_right = serial.Serial(SERIAL_PORT_RIGHT, 115200) 

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


    # left stick update:
    # update joystick position based on mouse movement
    mouse_x, mouse_y = pygame.mouse.get_pos()
    LEFT_JOYSTICK_X = mouse_x
    LEFT_JOYSTICK_Y = mouse_y

    # normalize the stick within the circle
    center_x, center_y = 320, 240
    LEFT_JOYSTICK_X -= center_x
    LEFT_JOYSTICK_Y -= center_y
    radius = math.hypot(LEFT_JOYSTICK_X, LEFT_JOYSTICK_Y)
    if radius > 200: 
        # forces radius to 200
        LEFT_JOYSTICK_X = LEFT_JOYSTICK_X / radius * 200
        LEFT_JOYSTICK_Y = LEFT_JOYSTICK_Y / radius * 200

    screen.fill((0, 0, 0))
    circle = pygame.draw.circle(screen, (0, 255, 0), (320, 240), 200, 4)
    pointer_indicator = pygame.draw.circle(screen, (255, 0, 0), (int((LEFT_JOYSTICK_X + center_x)), int((LEFT_JOYSTICK_Y + center_y))), 5)
    pygame.display.flip()

    LEFT_JOYSTICK_X /= 200
    LEFT_JOYSTICK_Y /= 200

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

    left_report = f"{LEFT_JOYSTICK_X:.4f},{LEFT_JOYSTICK_Y:.4f},{int(KEYS[pygame.K_h][0])},{int(KEYS[pygame.K_j][0])},{int(KEYS[pygame.K_k][0])},{int(KEYS[pygame.K_l][0])},{int(KEYS[pygame.K_y][0])},{int(KEYS[pygame.K_u][0])},{int(KEYS[pygame.K_i][0])},{int(KEYS[pygame.K_o][0])},{int(KEYS[pygame.K_1][0])},{int(KEYS[pygame.K_2][0])}\n"
    right_report = f"{-JOYSTICK_Y:.4f},{JOYSTICK_X:.4f},{int(KEYS[pygame.K_h][0])},{int(KEYS[pygame.K_j][0])},{int(KEYS[pygame.K_k][0])},{int(KEYS[pygame.K_l][0])},{int(KEYS[pygame.K_y][0])},{int(KEYS[pygame.K_u][0])},{int(KEYS[pygame.K_i][0])},{int(KEYS[pygame.K_o][0])},{int(KEYS[pygame.K_1][0])},{int(KEYS[pygame.K_2][0])}\n"
    ser_left.write(left_report.encode())
    ser_right.write(right_report.encode())


pygame.quit()