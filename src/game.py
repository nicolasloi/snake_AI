import pygame
import random
import numpy as np
from enum import Enum
from collections import namedtuple

# Initialize pygame only if it's not already initialized
if not pygame.get_init():
    pygame.init()
    
font = pygame.font.SysFont('arial', 25)


class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4


Point = namedtuple('Point', 'x, y')

# Improved colors
WHITE = (255, 255, 255)
RED = (220, 20, 60)      # Brighter red for the apple
GREEN1 = (50, 205, 50)   # Light green for the head
GREEN2 = (34, 139, 34)   # Dark green for the body
BLACK = (0, 0, 0)        # Background
GRID_COLOR = (40, 40, 40) # Grid color

# Game parameters
BLOCK_SIZE = 20
SPEED = 40  # Reduced from 60 to 40 for slower movement
GRID_SIZE = 20  # Grid size


class SnakeGameAI:
    def __init__(self, w=640, h=480):
        # Adjust dimensions to match the grid
        self.w = GRID_SIZE * (w // GRID_SIZE)
        self.h = GRID_SIZE * (h // GRID_SIZE)
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('Snake Classic')
        self.clock = pygame.time.Clock()

        # Load images for apple and head (optional)
        self.apple_img = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE))
        self.apple_img.fill(RED)

        self.head_img = {
            Direction.UP: pygame.Surface((BLOCK_SIZE, BLOCK_SIZE)),
            Direction.DOWN: pygame.Surface((BLOCK_SIZE, BLOCK_SIZE)),
            Direction.LEFT: pygame.Surface((BLOCK_SIZE, BLOCK_SIZE)),
            Direction.RIGHT: pygame.Surface((BLOCK_SIZE, BLOCK_SIZE))
        }

        for dir_img in self.head_img.values():
            dir_img.fill(GREEN1)
            
        # Add variable to store prediction scores
        self.prediction_scores = None

        self.reset()

    def reset(self):
        self.direction = Direction.RIGHT
        self.head = Point(self.w / 2, self.h / 2)
        self.snake = [self.head,
                      Point(self.head.x - BLOCK_SIZE, self.head.y),
                      Point(self.head.x - (2 * BLOCK_SIZE), self.head.y)]
        self.score = 0
        self.food = None
        self._place_food()
        self.frame_iteration = 0

    def _place_food(self):
        x = random.randint(0, (self.w - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        y = random.randint(0, (self.h - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        self.food = Point(x, y)
        if self.food in self.snake:
            self._place_food()

    def play_step(self, action, agent):
        self.frame_iteration += 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        self._move(action)
        self.snake.insert(0, self.head)

        reward = 0
        game_over = False
        if self.is_collision() or self.frame_iteration > 100 * len(self.snake):
            game_over = True
            reward = -10
            return reward, game_over, self.score

        if self.head == self.food:
            self.score += 1
            reward = 10
            self._place_food()
        else:
            self.snake.pop()

        # Store the prediction scores from agent if available
        if hasattr(agent, 'last_prediction_scores'):
            self.prediction_scores = agent.last_prediction_scores

        self._update_ui(agent)
        self.clock.tick(SPEED)

        return reward, game_over, self.score

    def _update_ui(self, agent):
        self.display.fill(BLACK)

        # Draw the grid
        for x in range(0, self.w, GRID_SIZE):
            pygame.draw.line(self.display, GRID_COLOR, (x, 0), (x, self.h))
        for y in range(0, self.h, GRID_SIZE):
            pygame.draw.line(self.display, GRID_COLOR, (0, y), (self.w, y))

        # Draw the snake
        for i, pt in enumerate(self.snake):
            if i == 0:  # Head
                # Draw the head with eyes according to the direction
                pygame.draw.rect(self.display, GREEN1, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE))

                # Add eyes according to the direction
                eye_size = 4
                eye_offset = 4

                if self.direction == Direction.RIGHT:
                    pygame.draw.rect(self.display, BLACK, pygame.Rect(pt.x + BLOCK_SIZE - eye_offset, pt.y + eye_offset, eye_size, eye_size))
                    pygame.draw.rect(self.display, BLACK, pygame.Rect(pt.x + BLOCK_SIZE - eye_offset, pt.y + BLOCK_SIZE - eye_offset - eye_size, eye_size, eye_size))
                elif self.direction == Direction.LEFT:
                    pygame.draw.rect(self.display, BLACK, pygame.Rect(pt.x + eye_offset - eye_size, pt.y + eye_offset, eye_size, eye_size))
                    pygame.draw.rect(self.display, BLACK, pygame.Rect(pt.x + eye_offset - eye_size, pt.y + BLOCK_SIZE - eye_offset - eye_size, eye_size, eye_size))
                elif self.direction == Direction.UP:
                    pygame.draw.rect(self.display, BLACK, pygame.Rect(pt.x + eye_offset, pt.y + eye_offset - eye_size, eye_size, eye_size))
                    pygame.draw.rect(self.display, BLACK, pygame.Rect(pt.x + BLOCK_SIZE - eye_offset - eye_size, pt.y + eye_offset - eye_size, eye_size, eye_size))
                elif self.direction == Direction.DOWN:
                    pygame.draw.rect(self.display, BLACK, pygame.Rect(pt.x + eye_offset, pt.y + BLOCK_SIZE - eye_offset, eye_size, eye_size))
                    pygame.draw.rect(self.display, BLACK, pygame.Rect(pt.x + BLOCK_SIZE - eye_offset - eye_size, pt.y + BLOCK_SIZE - eye_offset, eye_size, eye_size))
            else:  # Body
                pygame.draw.rect(self.display, GREEN2, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE))
                # Snake body pattern drawing
                pygame.draw.rect(self.display, GREEN1, pygame.Rect(pt.x + 4, pt.y + 4, BLOCK_SIZE - 8, BLOCK_SIZE - 8))

        # Draw the apple with an effect
        pygame.draw.rect(self.display, RED, pygame.Rect(self.food.x, self.food.y, BLOCK_SIZE, BLOCK_SIZE))
        pygame.draw.circle(self.display, WHITE, (self.food.x + 5, self.food.y + 5), 2)  # Reflection on the apple

        # Display game information in a box
        info_box = pygame.Surface((200, 90))
        info_box.fill((30, 30, 30))
        info_box.set_alpha(200)  # Semi-transparent
        self.display.blit(info_box, [10, 10])

        score_text = font.render(f"Score: {self.score}", True, WHITE)
        self.display.blit(score_text, [20, 15])

        game_text = font.render(f"Game: {agent.n_games}", True, WHITE)
        self.display.blit(game_text, [20, 45])

        record_text = font.render(f"Record: {agent.record}", True, WHITE)
        self.display.blit(record_text, [20, 75])
        
        # Display AI's "thought process" - visualization of prediction scores
        if hasattr(agent, 'last_prediction_scores') and agent.last_prediction_scores is not None:
            # Create a panel for AI thinking visualization
            panel_width = 200
            panel_height = 150
            # Position in the bottom left corner of the screen
            panel_x = 10
            panel_y = self.h - panel_height - 10
            
            # Create the panel box
            ai_panel = pygame.Surface((panel_width, panel_height))
            ai_panel.fill((30, 30, 30))
            ai_panel.set_alpha(220)
            self.display.blit(ai_panel, [panel_x, panel_y])
            
            # Panel title
            title_text = font.render("AI Thinking", True, WHITE)
            self.display.blit(title_text, [panel_x + 10, panel_y + 10])
            
            # Direction labels
            clock_wise = ["Straight", "Right", "Left"]
            
            # Draw bars representing prediction scores
            bar_height = 20
            max_bar_width = panel_width - 80
            
            for i, (direction, score) in enumerate(zip(clock_wise, agent.last_prediction_scores)):
                # Direction text
                dir_text = font.render(f"{direction}:", True, WHITE)
                self.display.blit(dir_text, [panel_x + 10, panel_y + 40 + i * 30])
                
                # Bar background
                bar_bg_rect = pygame.Rect(panel_x + 80, panel_y + 45 + i * 30, max_bar_width, bar_height - 5)
                pygame.draw.rect(self.display, (60, 60, 60), bar_bg_rect)
                
                # Bar representing probability
                bar_width = int(max_bar_width * score)
                
                # Different colors for different actions
                if i == 0:  # Straight - green
                    bar_color = (50, 205, 50)
                elif i == 1:  # Right - blue
                    bar_color = (30, 144, 255)
                else:  # Left - purple
                    bar_color = (147, 112, 219)
                
                bar_rect = pygame.Rect(panel_x + 80, panel_y + 45 + i * 30, bar_width, bar_height - 5)
                pygame.draw.rect(self.display, bar_color, bar_rect)
                
                # Percentage text
                pct_text = font.render(f"{int(score * 100)}%", True, WHITE)
                self.display.blit(pct_text, [panel_x + 85 + bar_width, panel_y + 40 + i * 30])
            
            # Display if the current move was random or predicted
            if agent.epsilon > 0 and random.randint(0, 200) < agent.epsilon:
                random_text = font.render("(Random Exploration)", True, (255, 165, 0))  # Orange
                self.display.blit(random_text, [panel_x + 10, panel_y + 125])
            else:
                predict_text = font.render("(Model Prediction)", True, (135, 206, 250))  # Light blue
                self.display.blit(predict_text, [panel_x + 10, panel_y + 125])

        pygame.display.flip()

    def is_collision(self, pt=None):
        if pt is None:
            pt = self.head
        if pt.x > self.w - BLOCK_SIZE or pt.x < 0 or pt.y > self.h - BLOCK_SIZE or pt.y < 0:
            return True
        if pt in self.snake[1:]:
            return True
        return False

    def _move(self, action):
        clock_wise = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
        idx = clock_wise.index(self.direction)

        if np.array_equal(action, [1, 0, 0]):  # straight
            new_dir = clock_wise[idx]
        elif np.array_equal(action, [0, 1, 0]):  # right turn
            next_idx = (idx + 1) % 4
            new_dir = clock_wise[next_idx]
        else:  # [0,0,1] left turn
            next_idx = (idx - 1) % 4
            new_dir = clock_wise[next_idx]

        self.direction = new_dir

        x = self.head.x
        y = self.head.y
        if self.direction == Direction.RIGHT:
            x += BLOCK_SIZE
        elif self.direction == Direction.LEFT:
            x -= BLOCK_SIZE
        elif self.direction == Direction.DOWN:
            y += BLOCK_SIZE
        elif self.direction == Direction.UP:
            y -= BLOCK_SIZE

        self.head = Point(x, y)