import pygame
import random
import numpy as np
import math
import time
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
SPEED = 10  # Vitesse constante du jeu - valeur fixe
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
        # Nombre d'inférences effectuées pour la décision actuelle
        self.inference_count = 0

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

        # Store previous head position to calculate distance change
        prev_head = self.head
        prev_distance = ((self.food.x - prev_head.x) ** 2 + (self.food.y - prev_head.y) ** 2) ** 0.5

        # S'assurer que l'action est valide (continuer tout droit, tourner à gauche ou à droite)
        valid_actions = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
        action_is_valid = False
        
        for valid_action in valid_actions:
            if np.array_equal(action, valid_action):
                action_is_valid = True
                break
                
        if not action_is_valid:
            # Si l'action n'est pas valide, on continue tout droit par défaut
            action = [1, 0, 0]

        self._move(action)
        self.snake.insert(0, self.head)

        # Calculate new distance to food
        new_distance = ((self.food.x - self.head.x) ** 2 + (self.food.y - self.head.y) ** 2) ** 0.5

        reward = 0
        game_over = False
        
        # Game over conditions
        if self.is_collision() or self.frame_iteration > 100 * len(self.snake):
            game_over = True
            reward = -10
            return reward, game_over, self.score

        # Food reward
        if self.head == self.food:
            self.score += 1
            reward = 10
            self._place_food()
        else:
            # Small reward or penalty based on if we're getting closer to food
            if new_distance < prev_distance:
                reward = 0.1  # Small reward for moving toward food
            else:
                reward = -0.1  # Small penalty for moving away from food
                
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
                    
                # Draw obstacle detection arrows if we have access to the agent's state
                if hasattr(agent, 'get_state'):
                    # Get the current state which contains danger information
                    state = agent.get_state(self)
                    
                    # Colors for the danger arrows
                    ARROW_COLORS = [
                        (255, 0, 0),      # Red for immediate danger (1st block)
                        (255, 165, 0),     # Orange for medium danger (2nd block)
                        (255, 255, 0)      # Yellow for distant danger (3rd block)
                    ]
                    
                    # Arrow parameters
                    arrow_length = [BLOCK_SIZE * 1.2, BLOCK_SIZE * 1.8, BLOCK_SIZE * 2.4]
                    arrow_width = 3
                    arrow_head_size = 7
                    
                    # Calculate center of the snake's head
                    center_x = pt.x + BLOCK_SIZE // 2
                    center_y = pt.y + BLOCK_SIZE // 2
                    
                    # Function to draw an arrow
                    def draw_arrow(start_pos, end_pos, color, width):
                        pygame.draw.line(self.display, color, start_pos, end_pos, width)
                        # Draw arrowhead
                        angle = math.atan2(end_pos[1] - start_pos[1], end_pos[0] - start_pos[0])
                        end_x, end_y = end_pos
                        pygame.draw.polygon(self.display, color, [
                            (end_x, end_y),
                            (end_x - arrow_head_size * math.cos(angle - math.pi/6), end_y - arrow_head_size * math.sin(angle - math.pi/6)),
                            (end_x - arrow_head_size * math.cos(angle + math.pi/6), end_y - arrow_head_size * math.sin(angle + math.pi/6))
                        ])
                    
                    # Extract danger states
                    # State structure: state[0:3] = straight dangers, state[3:6] = right dangers, state[6:9] = left dangers
                    
                    # Define arrow directions based on current snake direction
                    if self.direction == Direction.RIGHT:
                        directions = [
                            # Straight (right)
                            [(center_x + arrow_length[i], center_y) for i in range(3)],
                            # Right turn (down)
                            [(center_x, center_y + arrow_length[i]) for i in range(3)],
                            # Left turn (up)
                            [(center_x, center_y - arrow_length[i]) for i in range(3)]
                        ]
                    elif self.direction == Direction.LEFT:
                        directions = [
                            # Straight (left)
                            [(center_x - arrow_length[i], center_y) for i in range(3)],
                            # Right turn (up)
                            [(center_x, center_y - arrow_length[i]) for i in range(3)],
                            # Left turn (down)
                            [(center_x, center_y + arrow_length[i]) for i in range(3)]
                        ]
                    elif self.direction == Direction.UP:
                        directions = [
                            # Straight (up)
                            [(center_x, center_y - arrow_length[i]) for i in range(3)],
                            # Right turn (right)
                            [(center_x + arrow_length[i], center_y) for i in range(3)],
                            # Left turn (left)
                            [(center_x - arrow_length[i], center_y) for i in range(3)]
                        ]
                    elif self.direction == Direction.DOWN:
                        directions = [
                            # Straight (down)
                            [(center_x, center_y + arrow_length[i]) for i in range(3)],
                            # Right turn (left)
                            [(center_x - arrow_length[i], center_y) for i in range(3)],
                            # Left turn (right)
                            [(center_x + arrow_length[i], center_y) for i in range(3)]
                        ]
                    
                    # Draw danger arrows for straight, right, left
                    for dir_idx in range(3):  # 0=straight, 1=right, 2=left
                        for dist_idx in range(3):  # 0=close, 1=medium, 2=far
                            # Calculate the index in the state array
                            state_idx = dir_idx * 3 + dist_idx
                            
                            # If there's danger at this position
                            if state[state_idx]:
                                # Draw arrow for this danger
                                start_pos = (center_x, center_y)
                                end_pos = directions[dir_idx][dist_idx]
                                draw_arrow(start_pos, end_pos, ARROW_COLORS[dist_idx], arrow_width)
                    
            else:  # Body
                pygame.draw.rect(self.display, GREEN2, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE))
                # Snake body pattern drawing
                pygame.draw.rect(self.display, GREEN1, pygame.Rect(pt.x + 4, pt.y + 4, BLOCK_SIZE - 8, BLOCK_SIZE - 8))

        # Draw the apple with an effect
        pygame.draw.rect(self.display, RED, pygame.Rect(self.food.x, self.food.y, BLOCK_SIZE, BLOCK_SIZE))
        pygame.draw.circle(self.display, WHITE, (self.food.x + 5, self.food.y + 5), 2)  # Reflection on the apple

        # Display game information in a box - Interface simplifiée
        info_box = pygame.Surface((200, 100))
        info_box.fill((30, 30, 30))
        info_box.set_alpha(200)  # Semi-transparent
        self.display.blit(info_box, [10, 10])

        score_text = font.render(f"Score: {self.score}", True, WHITE)
        self.display.blit(score_text, [20, 15])

        game_text = font.render(f"Game: {agent.n_games}", True, WHITE)
        self.display.blit(game_text, [20, 45])

        record_text = font.render(f"Record: {agent.record}", True, WHITE)
        self.display.blit(record_text, [20, 75])

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