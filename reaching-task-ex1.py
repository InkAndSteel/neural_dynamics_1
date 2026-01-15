import pygame
import sys
import random
import math
import numpy as np
import matplotlib.pyplot as plt
import csv
from datetime import datetime

from sympy import false

# Game parameters
TARGET_ANGLE = None
SCREEN_X, SCREEN_Y = 2800, 1800 # your screen resolution
WIDTH, HEIGHT = SCREEN_X // 1.5  , SCREEN_Y // 1.5 # be aware of monitor scaling on windows (150%)
CIRCLE_SIZE = 25
TARGET_SIZE = CIRCLE_SIZE
TARGET_RADIUS = 300
MASK_RADIUS = 0.66 * TARGET_RADIUS
START_POSITION = (WIDTH // 2, HEIGHT // 2)
START_ANGLE = 0
PERTURBATION_ANGLE= 30
TIME_LIMIT = 1000 # time limit in ms
BASELINE = False

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Initialize Pygame
pygame.init()

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Reaching Game")


# Initialize game metrics
score = 0
attempts = 0
new_target = None
start_time = 0

new_target = None
start_target=math.radians(START_ANGLE)
move_faster = False
clock = pygame.time.Clock()

# Initialize game modes
mask_mode= False
target_mode = 'fix'  # Mode for angular shift of target: random, fix, dynamic
perturbation_mode= False
perturbation_type= 'sudden' # Mode for angular shift of controll: random, gradual or sudden
perturbation_angle = math.radians(PERTURBATION_ANGLE)  # Angle between mouse_pos and circle_pos
perturbed_mouse_angle = 0
gradual_step = 0
gradual_attempts = 1
perturbation_rand=random.uniform(-math.pi/4, +math.pi/4)

error_angles = []  # List to store error angles

# Flag for showing mouse position and deltas
show_mouse_info = False

# Function to generate a new target position
def generate_target_position(fixed_angle=None):
    if fixed_angle is not None:
        angle=fixed_angle;
    elif target_mode == 'random':
        angle = random.uniform(0, 2 * math.pi)

    elif target_mode == 'fix':
        angle=start_target;

    new_target_x = WIDTH // 2 + TARGET_RADIUS * math.sin(angle)
    new_target_y = HEIGHT // 2 + TARGET_RADIUS * -math.cos(angle) # zero-angle at the top
    return [new_target_x, new_target_y]

# Function to check if the current target is reached
def check_target_reached():
    if new_target:
        distance = math.hypot(circle_pos[0] - new_target[0], circle_pos[1] - new_target[1])
        return distance <= CIRCLE_SIZE
    return False

# Function to check if player is at starting position and generate new target
def at_start_position_and_generate_target(mouse_pos):
    distance = math.hypot(mouse_pos[0] - START_POSITION[0], mouse_pos[1] - START_POSITION[1])
    if distance <= CIRCLE_SIZE:
        return True
    return False

# Main game loop
running = True
while running:
    screen.fill(BLACK)

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:  # Press 'esc' to close the experiment
                running = False
            elif event.key == pygame.K_4: # Press '4' to test pertubation_mode
                perturbation_mode = True
            elif event.key == pygame.K_5: # Press '5' to end pertubation_mode
                perturbation_mode = False
            elif event.key == pygame.K_h:  # Press 'h' to toggle mouse info display
                show_mouse_info = not show_mouse_info

    if BASELINE:
        # Design experiment
        if attempts == 0:
            perturbation_mode = False
        elif attempts == 20:
            perturbation_mode = True
            perturbation_type = 'sudden'
        elif attempts == 80:
            perturbation_mode = False
        elif attempts == 100:
            perturbation_mode = True
            perturbation_type = 'sudden'
        elif attempts == 160:
            running = False
    else:
        if attempts == 0:
            TARGET_ANGLE = math.radians(30)
            perturbation_mode = False
        elif attempts == 20: # black
            # Target angle 1
            perturbation_mode = True
            perturbation_type = 'sudden'
        elif attempts == 80:
            perturbation_mode = False
        elif attempts == 100:
            TARGET_ANGLE = math.radians(70)
        elif attempts == 120:  # green
            # Target angle 2
            perturbation_mode = True
            perturbation_type = 'sudden'
        elif attempts == 180:
            perturbation_mode = False
        elif attempts == 200:
            TARGET_ANGLE = math.radians(50)
        elif attempts == 220: # blue
            # Target angle 3
            perturbation_mode = True
            perturbation_type = 'sudden'
        elif attempts == 280:
            perturbation_mode = False
        elif attempts == 300:
            TARGET_ANGLE = math.radians(120)
        elif attempts == 320:  # orange
            # Target angle 4
            perturbation_mode = True
            perturbation_type = 'sudden'
        elif attempts == 380:
            perturbation_mode = False
        elif attempts == 400:
            running = false

    # Hide the mouse cursor
    pygame.mouse.set_visible(False)
    # Get mouse position
    mouse_pos = pygame.mouse.get_pos()

    # Calculate distance from START_POSITION to mouse_pos
    deltax = mouse_pos[0] - START_POSITION[0]
    deltay = mouse_pos[1] - START_POSITION[1]
    distance = math.hypot(deltax, deltay)
    mouse_angle = math.atan2(deltay, deltax)

    # TASK1: CALCULATE perturbed_mouse_pos
    # PRESS 'h' in game for a hint
    def to_cartesian(angle, radius):
        return (START_POSITION[0] + radius * math.cos(angle), START_POSITION[1] + radius * math.sin(angle))

    if perturbation_mode:
        if perturbation_type == 'sudden':
            #sudden clockwise perturbation of perturbation_angle
            perturbed_mouse_angle = (mouse_angle - perturbation_angle)

        elif perturbation_type == 'gradual':
            #gradual counterclockwise perturbation of perturbation_angle in 10 steps, with perturbation_angle/10, each step lasts 3 attempts
            current_step = min(math.ceil(gradual_attempts/3), 10)
            angle_per_step = perturbation_angle / 10
            current_shift = current_step * angle_per_step

            perturbed_mouse_angle = mouse_angle + current_shift

        perturbed_mouse_pos = to_cartesian(perturbed_mouse_angle, distance)
        circle_pos = perturbed_mouse_pos
    else:
        circle_pos = pygame.mouse.get_pos()

    # Check if target is hit or missed
    # hit if circle touches target's center
    if check_target_reached():
        score += 1
        attempts += 1

        # CALCULATE AND SAVE ERRORS between target and circle end position for a hit
        target_angle = math.atan2(new_target[1] - START_POSITION[1], new_target[0] - START_POSITION[0])
        end_angle = math.atan2(circle_pos[1] - START_POSITION[1], circle_pos[0] - START_POSITION[0])
        error_angle = (end_angle - target_angle + math.pi) % (2 * math.pi) - math.pi
        error_angle = math.degrees(error_angle)
        if( move_faster == False):
            error_angles.append(error_angle)
        else:
            error_angles.append(float('nan'))
        new_target = None  # Set target to None to indicate hit
        start_time = 0  # Reset start_time after hitting the target
        if perturbation_type == 'gradual' and perturbation_mode:
            gradual_attempts += 1

    #miss if player leaves the target_radius + 1% tolerance
    elif new_target and math.hypot(circle_pos[0] - START_POSITION[0], circle_pos[1] - START_POSITION[1]) > TARGET_RADIUS*1.01:
        attempts += 1

        target_angle = math.atan2(new_target[1] - START_POSITION[1], new_target[0] - START_POSITION[0])
        end_angle = math.atan2(circle_pos[1] - START_POSITION[1], circle_pos[0] - START_POSITION[0])
        error_angle = (end_angle - target_angle + math.pi) % (2 * math.pi) - math.pi
        error_angle = math.degrees(error_angle)
        if( move_faster == False):
            error_angles.append(error_angle)
        else:
            error_angles.append(float('nan'))

        new_target = None  # Set target to None to indicate miss
        start_time = 0  # Reset start_time after missing the target

        if perturbation_type == 'gradual' and perturbation_mode:
            gradual_attempts += 1

    # Check if player moved to the center and generate new target
    if not new_target and at_start_position_and_generate_target(mouse_pos):
        new_target = generate_target_position(TARGET_ANGLE)
        move_faster = False
        start_time = pygame.time.get_ticks()  # Start the timer for the attempt

    # Check if time limit for the attempt is reached
    current_time = pygame.time.get_ticks()
    if start_time != 0 and (current_time - start_time) > TIME_LIMIT:
        move_faster = True
        start_time = 0  # Reset start_time

    # Show 'MOVE FASTER!'
    if move_faster:
        font = pygame.font.Font(None, 36)
        text = font.render('MOVE FASTER!', True, RED)
        text_rect = text.get_rect(center=(START_POSITION))
        screen.blit(text, text_rect)

# Generate playing field
    # Draw current target
    if new_target:
        pygame.draw.circle(screen, BLUE, new_target, TARGET_SIZE // 2)

    # Draw circle cursor
    if mask_mode:
        if distance < MASK_RADIUS:
            pygame.draw.circle(screen, WHITE, circle_pos, CIRCLE_SIZE // 2)
    else:
        pygame.draw.circle(screen, WHITE, circle_pos, CIRCLE_SIZE // 2)

    # Draw start position
    pygame.draw.circle(screen, WHITE, START_POSITION, 5)

    # Show score
    font = pygame.font.Font(None, 36)
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))

    # Show attempts
    font = pygame.font.Font(None, 36)
    score_text = font.render(f"Attempts: {attempts}", True, WHITE)
    screen.blit(score_text, (10, 30))

    if show_mouse_info:
        mouse_info_text = font.render(f"Mouse: x={mouse_pos[0]}, y={mouse_pos[1]}", True, WHITE)
        delta_info_text = font.render(f"Delta: Δx={deltax}, Δy={deltay}", True, WHITE)
        mouse_angle_text = font.render(f"Mouse_Ang: {np.rint(np.degrees(mouse_angle))}", True, WHITE)
        circle_angle_text = font.render(f"Circle_Ang: {np.rint(np.degrees(math.atan2(circle_pos[1] - START_POSITION[1], circle_pos[0] - START_POSITION[0])))}", True, WHITE)

        if error_angles:
            last_error_text = font.render(f"Last_Error: {np.rint(error_angles[-1])}", True, WHITE)
        screen.blit(mouse_info_text, (10, 60))
        screen.blit(delta_info_text, (10, 90))
        screen.blit(mouse_angle_text, (10, 120))
        screen.blit(circle_angle_text, (10, 150))
        if error_angles:
            screen.blit(last_error_text, (10, 180))

    # Update display
    pygame.display.flip()
    clock.tick(60)

# Quit Pygame
pygame.quit()

## TASK 2, CALCULATE, PLOT AND SAVE (e.g. export as .csv) ERRORS from error_angles
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
csv_name = f"{timestamp}.csv"
with open(csv_name, "w", newline="") as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(["error_angle_deg"])
    for angle in error_angles:
        writer.writerow([angle])

sys.exit()
