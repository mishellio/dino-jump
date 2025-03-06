# This script is adpated from dino_jump_main.py, but is much simpler as all it does is parse lines
# of strings from stdin, convert them into frames, and show frames using pygame.
import sys
import numpy as np
import pygame


class Game:

    def __init__(self):

        # Editable Constants
        self.GRID_SIZE = 4  # scale entire pygame panel size (only for online display)
        self.WIDTH, self.HEIGHT = (
            150,
            48,
        )  # define pixel height and width for actual board

        # Non-Editable Constants
        self.BG_COLOR = (255, 255, 255)  # white colour (background)
        self.BLOCK_COLOR = (0, 0, 0)  # black colour (sprites)
        self.FPS = 60  # frames per second frames update
        self.game_over = False

        # Setup Display
        self.full_game_state_array = np.zeros((self.HEIGHT, self.WIDTH)).astype(int)
        self.screen = pygame.display.set_mode(
            (self.WIDTH * self.GRID_SIZE, self.HEIGHT * self.GRID_SIZE)
        )
        self.clk = pygame.time.Clock()
        pygame.display.set_caption("DinoJump!")

    def parse_frame_string(self):
        self.full_game_state_array = np.zeros((self.HEIGHT, self.WIDTH), dtype=int)
        try:
            s = input()
        except EOFError as e:
            print("error: ", e)
            sys.exit(1)
        print(s)

        if "Score" in s:
            self.game_over = True
            return

        tokens = s.split(",")
        col = 0

        # We skip the last token as we expect a comma in the end
        for t in tokens[:-1]:
            if col >= self.WIDTH:
                print("unexpected token")
                sys.exit(1)

            if t[0] == "#":
                cols = int(t[1:], 16)
                for _ in range(cols):
                    self.full_game_state_array[:, col] = 0
                    col += 1
            else:
                binary_str = format(int(t, 16), "048b")
                binary_array = np.array([int(bit) for bit in binary_str])
                self.full_game_state_array[:, col] = binary_array.reshape(
                    -1, 1
                ).flatten()[::-1]
                col += 1

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
        pygame.display.flip()
        self.clk.tick(self.FPS)


game = Game()

pygame.init()

while not game.game_over:
    game.parse_frame_string()
    game.draw_to_screen()

print("game over!")
