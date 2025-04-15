"""
Background animations for Snake AI menu
"""

import pygame
import random
from src.menu.colors import *

GRID_SIZE = 20
SNAKE_SPEED = 5

class Snake:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid_size = GRID_SIZE
        self.reset()
        
    def reset(self):
        # Start snake at the middle of the screen
        self.direction = "RIGHT"
        x = (self.width // self.grid_size) // 2 * self.grid_size
        y = (self.height // self.grid_size) // 2 * self.grid_size
        self.body = [(x, y), (x-self.grid_size, y), (x-2*self.grid_size, y)]
        self.food = self._place_food()
        self.grow = False
        self.speed_counter = 0
        
    def update(self):
        self.speed_counter += 1
        if self.speed_counter < SNAKE_SPEED:
            return
            
        self.speed_counter = 0
        
        # Move head based on direction
        x, y = self.body[0]
        if self.direction == "RIGHT":
            x += self.grid_size
        elif self.direction == "LEFT":
            x -= self.grid_size
        elif self.direction == "UP":
            y -= self.grid_size
        elif self.direction == "DOWN":
            y += self.grid_size
            
        # Check if out of bounds, wrap around
        if x >= self.width:
            x = 0
        if x < 0:
            x = self.width - self.grid_size
        if y >= self.height:
            y = 0
        if y < 0:
            y = self.height - self.grid_size
            
        # Insert new head
        self.body.insert(0, (x, y))
        
        # Check if food eaten
        if self.body[0] == self.food:
            self.food = self._place_food()
            self.grow = True
        
        # Remove tail if not growing
        if not self.grow:
            self.body.pop()
        else:
            self.grow = False
            
        # Randomly change direction occasionally to make animation more interesting
        if random.random() < 0.03:
            directions = ["RIGHT", "LEFT", "UP", "DOWN"]
            self.direction = random.choice(directions)
    
    def _place_food(self):
        max_x = self.width // self.grid_size - 1
        max_y = self.height // self.grid_size - 1
        
        while True:
            x = random.randint(0, max_x) * self.grid_size
            y = random.randint(0, max_y) * self.grid_size
            if (x, y) not in self.body:
                return (x, y)
    
    def draw(self, surface):
        # Draw food
        food_rect = pygame.Rect(self.food[0], self.food[1], self.grid_size, self.grid_size)
        pygame.draw.rect(surface, FOOD_COLOR, food_rect, border_radius=self.grid_size//2)
        
        # Draw snake
        for i, (x, y) in enumerate(self.body):
            snake_rect = pygame.Rect(x, y, self.grid_size, self.grid_size)
            
            if i == 0:  # Head
                pygame.draw.rect(surface, SNAKE_COLOR, snake_rect, border_radius=self.grid_size//2)
                
                # Eyes
                eye_size = self.grid_size // 5
                eye_offset = self.grid_size // 3
                
                if self.direction == "RIGHT":
                    eye1_pos = (x + self.grid_size - eye_offset, y + eye_offset)
                    eye2_pos = (x + self.grid_size - eye_offset, y + self.grid_size - eye_offset)
                elif self.direction == "LEFT":
                    eye1_pos = (x + eye_offset, y + eye_offset)
                    eye2_pos = (x + eye_offset, y + self.grid_size - eye_offset)
                elif self.direction == "UP":
                    eye1_pos = (x + eye_offset, y + eye_offset)
                    eye2_pos = (x + self.grid_size - eye_offset, y + eye_offset)
                else:  # DOWN
                    eye1_pos = (x + eye_offset, y + self.grid_size - eye_offset)
                    eye2_pos = (x + self.grid_size - eye_offset, y + self.grid_size - eye_offset)
                    
                pygame.draw.circle(surface, BLACK, eye1_pos, eye_size)
                pygame.draw.circle(surface, BLACK, eye2_pos, eye_size)
            else:
                # Body segments get darker further from head
                alpha = max(50, 255 - i * 10)
                if alpha < 0:
                    alpha = 50
                    
                segment_color = (SNAKE_COLOR[0], SNAKE_COLOR[1], SNAKE_COLOR[2], alpha)
                
                # Create a surface with per-pixel alpha
                s = pygame.Surface((self.grid_size, self.grid_size), pygame.SRCALPHA)
                pygame.draw.rect(s, segment_color, s.get_rect(), border_radius=self.grid_size//3)
                surface.blit(s, (x, y))