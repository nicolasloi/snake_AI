"""
Game Environment for Snake AI
Contains the main SnakeGameAI class
"""

import pygame
import random
import numpy as np
from src.game.constants import *
from src.game.entities import Direction, Point
from src.game.rendering import (
    draw_grid, draw_snake, draw_food, 
    draw_info_box, draw_danger_arrows
)

# Initialize pygame if not already initialized
if not pygame.get_init():
    pygame.init()

class SnakeGameAI:
    """
    Snake game environment for AI
    """
    def __init__(self, w=640, h=480):
        # Adjust dimensions to match the grid
        self.w = GRID_SIZE * (w // GRID_SIZE)
        self.h = GRID_SIZE * (h // GRID_SIZE)
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('Snake AI')
        self.clock = pygame.time.Clock()
        
        # Variables to store prediction scores
        self.prediction_scores = None
        
        # Initialize the game
        self.reset()

    def reset(self):
        """
        Resets the game to its initial state
        """
        self.direction = Direction.RIGHT
        self.head = Point(self.w // 2, self.h // 2)
        self.snake = [self.head,
                      Point(self.head.x - BLOCK_SIZE, self.head.y),
                      Point(self.head.x - (2 * BLOCK_SIZE), self.head.y)]
        self.score = 0
        self.food = None
        self._place_food()
        self.frame_iteration = 0

    def _place_food(self):
        """
        Places food at a random location not occupied by the snake
        """
        x = random.randint(0, (self.w - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        y = random.randint(0, (self.h - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        self.food = Point(x, y)
        if self.food in self.snake:
            self._place_food()

    def play_step(self, action, agent):
        """
        Executes a step in the game with the given action
        
        Args:
            action: action to perform [straight, right_turn, left_turn]
            agent: the agent playing the game
            
        Returns:
            reward: reward for this step
            game_over: True if the game is over
            score: current score
        """
        self.frame_iteration += 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        # Store previous position and distance to food
        prev_head = self.head
        prev_distance = self._calculate_distance_to_food(prev_head)

        # Ensure action is valid (straight, right turn, or left turn)
        valid_actions = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
        action_is_valid = False
        
        for valid_action in valid_actions:
            if np.array_equal(action, valid_action):
                action_is_valid = True
                break
                
        if not action_is_valid:
            # If action is not valid, continue straight by default
            action = [1, 0, 0]

        # Move the snake according to the action
        self._move(action)
        self.snake.insert(0, self.head)

        # Calculate new distance to food
        new_distance = self._calculate_distance_to_food(self.head)

        # Check end game conditions and rewards
        reward, game_over = self._check_game_status(prev_distance, new_distance)

        # Store prediction scores if available
        if hasattr(agent, 'last_prediction_scores'):
            self.prediction_scores = agent.last_prediction_scores

        # Update the user interface
        self._update_ui(agent)
        self.clock.tick(SPEED)

        return reward, game_over, self.score

    def _calculate_distance_to_food(self, position):
        """
        Calculates Euclidean distance between a position and the food
        """
        return ((self.food.x - position.x) ** 2 + (self.food.y - position.y) ** 2) ** 0.5

    def _check_game_status(self, prev_distance, new_distance):
        """
        Checks if the game is over and calculates the reward
        
        Returns:
            reward: reward for this step
            game_over: True if the game is over
        """
        reward = 0
        game_over = False
        
        # Check for collisions or timeout
        if self.is_collision() or self.frame_iteration > 100 * len(self.snake):
            game_over = True
            reward = -10
            return reward, game_over

        # Reward for eating food
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
                
            self.snake.pop()  # Only remove the tail if we didn't eat

        return reward, game_over

    def is_collision(self, pt=None):
        """
        Checks if a position collides with a wall or the snake itself
        """
        if pt is None:
            pt = self.head
            
        # Check for wall collisions
        if pt.x > self.w - BLOCK_SIZE or pt.x < 0 or pt.y > self.h - BLOCK_SIZE or pt.y < 0:
            return True
            
        # Check for collision with snake body
        if pt in self.snake[1:]:
            return True
            
        return False

    def _move(self, action):
        """
        Moves the snake according to the given action
        """
        # Direction in clockwise order
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

        # Update coordinates based on direction
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

    def _update_ui(self, agent):
        """
        Updates the user interface
        """
        # Fill background with black
        self.display.fill(BLACK)

        # Draw the grid
        draw_grid(self.display, self.w, self.h)
        
        # Draw the snake
        draw_snake(self.display, self.snake, self.direction)
        
        # Draw the food
        draw_food(self.display, self.food)
        
        # Draw danger arrows if the agent has a get_state method
        if hasattr(agent, 'get_state'):
            state = agent.get_state(self)
            draw_danger_arrows(self.display, state, self.direction, self.head)
            
        # Draw info box with score, etc.
        game_info = {
            'score': self.score,
            'games': agent.n_games,
            'record': agent.record
        }
        draw_info_box(self.display, game_info)
        
        # Update display
        pygame.display.flip()