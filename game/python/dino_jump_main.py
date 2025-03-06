#############################################################################
# IMPORTS
#############################################################################

import sys
import random
import numpy as np
import pygame

from sprites import import_sprite


#############################################################################
# GAME MODULE
#############################################################################


class Game:

    def __init__(self):

        # Editable Constants
        self.GRID_SIZE = 4  # scale entire pygame panel size (only for online display)
        self.WIDTH, self.HEIGHT = (
            150,
            48,
        )  # define pixel height and width for actual board
        self.GROUND_RATIO, self.LOW_BIRD_RATIO, self.HIGH_BIRD_RATIO = (
            2,
            18,
            28,
        )  # proportions for the three axes of obstacles

        # Non-Editable Constants
        self.BG_COLOR = (255, 255, 255)  # white colour (background)
        self.BLOCK_COLOR = (0, 0, 0)  # black colour (sprites)
        self.FPS = 60  # frames per second frames update
        self.GROUND_Y = (
            self.HEIGHT - self.GROUND_RATIO
        )  # defines axis height with (0,0) lower left corner
        self.LOW_BIRD_Y = (
            self.HEIGHT - self.LOW_BIRD_RATIO
        )  # defines axis height with (0,0) lower left corner
        self.HIGH_BIRD_Y = (
            self.HEIGHT - self.HIGH_BIRD_RATIO
        )  # defines axis height with (0,0) lower left corner
        self.start_game = False
        self.game_over = False
        self.close_all = False

        # Setup Display
        self.background_game_state_array = np.zeros((self.HEIGHT, self.WIDTH)).astype(
            int
        )
        self.full_game_state_array = np.zeros((self.HEIGHT, self.WIDTH)).astype(int)
        self.screen = pygame.display.set_mode(
            (self.WIDTH * self.GRID_SIZE, self.HEIGHT * self.GRID_SIZE)
        )
        self.clk = pygame.time.Clock()
        pygame.display.set_caption("DinoJump!")

        # Initiate the Dino and ObstacleManager Classes
        self.dino = Dino(self.GROUND_Y, self.FPS)
        self.all_obstacles = ObstacleManager(
            self.WIDTH, (self.GROUND_Y, self.LOW_BIRD_Y, self.HIGH_BIRD_Y)
        )

    def update_board_pixels(self, curr_object):

        # Get all the values from the curr_object and the board
        x, y = int(curr_object.x), int(curr_object.y)
        height, width = curr_object.HEIGHT, curr_object.WIDTH
        min_width, max_width = min(max(x, 0), self.WIDTH), max(
            0, min(x + width, self.WIDTH)
        )

        # Segment the display section to draw to (especially if cropped)
        left_edge = curr_object.ARRAY[:, -(max_width - min_width) :]
        right_edge = curr_object.ARRAY[:, : (max_width - min_width)]
        set_location = self.background_game_state_array[
            y : y + height, min_width:max_width
        ]

        # Extract bitwise OR of incorporating the new drawing
        if min_width == 0 and max_width != 0:
            filled_location = np.bitwise_or(left_edge, set_location)
        else:
            filled_location = np.bitwise_or(right_edge, set_location)

        # Draw the dino and full background on the full_game_state
        if curr_object.OBJECT_TYPE == "dino":
            self.full_game_state_array = np.copy(self.background_game_state_array)
            self.full_game_state_array[y : y + height, min_width:max_width] = (
                filled_location
            )
        else:  # Draw all obstacles on the background
            self.background_game_state_array[y : y + height, min_width:max_width] = (
                filled_location
            )

    def check_collision_and_game_over(self):

        # Get all the values from the dino
        x, y = int(self.dino.x), int(self.dino.y)
        height, width = self.dino.HEIGHT, self.dino.WIDTH

        # Extract the location on the board the dino is at
        set_location = self.background_game_state_array[y : y + height, x : x + width]

        # Check using bitwise AND if the collision has occured
        is_hit = np.sum(np.bitwise_and(self.dino.ARRAY, set_location))

        # If a hit is detected, we end the game
        if is_hit:
            self.game_over = True

    def draw_to_screen(self):
        # Reset the current board
        self.screen.fill(game.BG_COLOR)
        # Use GRID_SIZE to increase the software viewing panel
        draw_array = np.repeat(
            np.repeat(self.full_game_state_array, self.GRID_SIZE, axis=0),
            self.GRID_SIZE,
            axis=1,
        )
        # For each pixel in the game board, draw them in black and white to the screen
        for row in range(draw_array.shape[0]):
            for col in range(draw_array.shape[1]):
                if draw_array[row, col] == 1:
                    pygame.draw.rect(
                        self.screen,
                        self.BLOCK_COLOR,
                        (col, row, 1, 1),
                    )
        # Update the visual board
        pygame.display.flip()
        self.clk.tick(self.FPS)

    def check_start_game(self):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.start_game = True
                self.dino.is_jumping = True
                self.dino.update_jumping_location()

    def check_user_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.dino.is_jumping = True
                if event.key == pygame.K_DOWN:
                    self.dino.is_ducking = True

            if event.type == pygame.KEYUP:
                # if event.key == pygame.K_SPACE:
                #     self.dino.is_jumping = False
                if event.key == pygame.K_DOWN:
                    self.dino.is_ducking = False

    def update_full_game_state(self):
        self.background_game_state_array = np.zeros((game.HEIGHT, game.WIDTH)).astype(
            int
        )
        for obs in self.all_obstacles.curr_obs:
            self.update_board_pixels(obs)
        self.update_board_pixels(self.dino)

    def check_close_panel(self):
        # Checks for another space bar press to close the whole program
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.close_all = True


#############################################################################
# SINGLE OBSTACLE MODULE
#############################################################################


class Obstacle:

    def __init__(self, obs_type, speed, init_width, AXES):

        # Generation Constants
        self.OBJECT_TYPE = "obstacle"
        self.OBS_TYPE = obs_type  # string, defines c C b B singular obstacle
        self.SPEED = speed  # number of pixels moved to the left per loop
        self.ARRAY = import_sprite(self.OBS_TYPE).astype(
            int
        )  # calls sprites: with type to get pixel array
        self.x = init_width  # initial position of spirt at right edge of board
        self.HEIGHT, self.WIDTH = (
            self.ARRAY.shape
        )  # height and width of the array to call

        # Inherited from Game
        self.GROUND_Y, self.LOW_BIRD_Y, self.HIGH_BIRD_Y = AXES

        # Define the y axis this obstacle sprite travels along
        if self.OBS_TYPE in ("c", "C"):
            self.y = self.GROUND_Y - self.HEIGHT
        elif self.OBS_TYPE == "b":
            self.y = self.LOW_BIRD_Y - self.HEIGHT
        else:
            self.y = self.HIGH_BIRD_Y - self.HEIGHT


#############################################################################
# OBSTACLE MANAGEMENT MODULE
#############################################################################


class ObstacleManager:

    def __init__(self, WIDTH, AXES):

        # Timing Constants
        self.curr_cooldown = (
            0  # counts the number of frames before next obstacle generated
        )
        self.BASE_COOLDOWN = (
            20  # must wait how many frames before new obstacle generates
        )
        self.COOLDOWN_VARIANCE = np.linspace(
            10, 30, 5
        )  # variance of how many frames to add the to baseline

        # Inherited from game
        self.WIDTH = WIDTH
        self.AXES = AXES

        # Possible Choices for Compound Obstacles and Speeds
        self.ALL_SPEEDS = [3]
        self.ALL_OBSTACLE_GROUPS = ["c", "C", "ccc", "CC", "cCc", "cc", "b", "B"]

        # Hold all current obstacle objects to keep track of
        self.curr_obs = []

    def update_location(self):

        # Only care about valid obstacles on the game board
        self.curr_obs = [obs for obs in self.curr_obs if obs.x + obs.WIDTH > 0]

        # Update each obstacle's location by its speed
        for obs in self.curr_obs:
            obs.x -= obs.SPEED

    def choose_random_obstacle_attributes(self):
        # Choose the next obstacle: cactus arrangement, low bird, or high bird
        return np.random.choice(self.ALL_OBSTACLE_GROUPS), np.random.choice(
            self.ALL_SPEEDS
        )

    def generate_obstacle(self):

        # When the cooldown reaches zero, a new obstacle is generated
        if self.curr_cooldown <= 0:
            new_obstacle, new_speed = self.choose_random_obstacle_attributes()
            for i, obs in enumerate(new_obstacle):
                new_obs = Obstacle(obs, new_speed, self.WIDTH, self.AXES)
                new_obs.x += (new_obs.WIDTH + 1) * i
                self.curr_obs.append(new_obs)
            self.curr_cooldown = self.BASE_COOLDOWN + random.choice(
                self.COOLDOWN_VARIANCE
            )

        # Otherwise, we decrement the cooldown timer every loop
        else:
            self.curr_cooldown -= 1


#############################################################################
# DINO MODULE
#############################################################################


class Dino:

    def __init__(self, GROUND_Y, FPS):

        # Type
        self.OBJECT_TYPE = "dino"

        # Jumping Constants
        self.JUMP_HEIGHT = 25  # specify how many pixels upwards the max-height goes
        self.JUMP_DURATION = 300  # specify time in milliseconds dino takes to land
        self.UPDATE_WALK_FRAMES = 3  # how many frames to wait before dino switches legs

        # Inherited from Game
        self.GROUND_Y = GROUND_Y
        self.FPS = FPS

        # Get all pixel arrays for the dino from sprite import (dino:20x19)
        self.JUMP_ARRAY = import_sprite("jump").astype(int)
        self.RRUN_ARRAY = import_sprite("right run").astype(int)
        self.LRUN_ARRAY = import_sprite("left run").astype(int)
        self.RDUCK_ARRAY = import_sprite("right duck").astype(int)
        self.LDUCK_ARRAY = import_sprite("left duck").astype(int)
        self.DONE_ARRAY = import_sprite("done").astype(int)

        # Define Array and Dimensions
        self.ARRAY = self.JUMP_ARRAY  # the first array is still dino frame
        self.HEIGHT, self.WIDTH = (
            self.JUMP_ARRAY.shape
        )  # get height and width to be able to call
        self.OG_DINO_Y = (
            self.GROUND_Y - self.HEIGHT
        )  # define dino's top left pixel height
        self.x = 5  # dino x stays put, how many pixels from left edge
        self.y = self.OG_DINO_Y  # assigned to the y position
        self.is_right_foot_down = (
            True  # used to change between left and right foot arrays displayed
        )
        self.is_jumping = True  # detects if jumping signal is given
        self.is_ducking = False  # detects if ducking signal is given
        self.is_hit = False  # becomes true when obstacle and dino collide
        self.jump_start_time = 0  # used to count time in jumping
        self.curr_walk_frame = (
            self.UPDATE_WALK_FRAMES
        )  # counts how many frames before the legs switch

        # Setup Jumping Dynamics
        self.setup_jump_array()
        self.curr_jumping_index = 0

    def setup_jump_array(self):
        # Generate an array to store jumping parameters and motion
        total_frames = int((self.JUMP_DURATION / 1000) * self.FPS)
        t = np.linspace(0, 1, total_frames)
        jump_arc = self.OG_DINO_Y - (
            -4 * self.JUMP_HEIGHT * (t - 0.5) ** 2 + self.JUMP_HEIGHT
        )
        self.JUMPING_Y_POSITIONS = np.round(jump_arc).astype(int)
        self.END_OF_JUMP_INDEX = len(self.JUMPING_Y_POSITIONS)

    def update_jumping_location(self):
        # Determine y coordinate of dino jump using frames
        if self.is_jumping:
            self.y = self.JUMPING_Y_POSITIONS[self.curr_jumping_index]
            self.curr_jumping_index += 1
            if self.curr_jumping_index == self.END_OF_JUMP_INDEX:
                self.y = self.OG_DINO_Y
                self.is_jumping = False
                self.curr_jumping_index = 0

    def update_dino_footing(self):
        # Determine when the dino foot change happens
        if self.curr_walk_frame <= 0:
            self.is_right_foot_down = not self.is_right_foot_down
            self.curr_walk_frame = self.UPDATE_WALK_FRAMES
        self.curr_walk_frame -= 1

    def update_frame(self):
        # Update dino pixel array
        if self.is_jumping:
            self.ARRAY = self.JUMP_ARRAY
        elif self.is_ducking and self.is_right_foot_down:
            self.ARRAY = self.RDUCK_ARRAY
        elif self.is_ducking:
            self.ARRAY = self.LDUCK_ARRAY
        elif self.is_right_foot_down:
            self.ARRAY = self.RRUN_ARRAY
        else:
            self.ARRAY = self.LRUN_ARRAY

        # If the game is over, show the dead dino frame
        if game.game_over:
            self.ARRAY = self.DONE_ARRAY


#############################################################################
# VOID SETUP
#############################################################################

# Initialises the Dino Game
game = Game()

# Start Pygame
pygame.init()
game.update_full_game_state()
game.draw_to_screen()


#############################################################################
# VOID LOOP
#############################################################################

# Wait until first space bar press until the game starts
while not game.start_game:
    game.check_start_game()

# Simulates the whole loop running
while not game.game_over:
    game.check_user_input()
    game.dino.update_jumping_location()
    game.all_obstacles.generate_obstacle()
    game.dino.update_frame()
    game.dino.update_dino_footing()
    game.all_obstacles.update_location()
    game.update_full_game_state()
    game.check_collision_and_game_over()
    game.draw_to_screen()

print("game over!")
game.dino.update_frame()
game.dino.update_dino_footing()
game.update_full_game_state()
game.draw_to_screen()
while not game.close_all:
    game.check_close_panel()


# CURRENT IMPLEMENTATION: DRAW_AND_CHECK_COLLISION_ALL
# Ideally, draw and check_collision would be two separate functions
# However, currently running the two functions separately results in the game
# ending much earlier than expected
# Current Rationale: Since the function determines the set_location twice for one obs,
# it could affect future calculations
# Need to see how the data within the obstacles are changed after running the function.

#############################################################################
# END USER WORK AREA
#############################################################################
