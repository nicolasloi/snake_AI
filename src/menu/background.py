"""
Background animation module for Snake AI menu
"""

import pygame
import random
from src.menu.colors import *

class Snake:
    """
    Animated snake for menu background
    """
    def __init__(self, width, height):
        self.width = width
        self.height = height
        
        # Snake parameters
        self.block_size = 15
        self.snake_length = 15
        self.positions = []
        
        # Initialize snake in a random position
        self.head_x = random.randint(0, width - self.block_size)
        self.head_y = random.randint(0, height - self.block_size)
        self.direction = random.choice([(1, 0), (0, 1), (-1, 0), (0, -1)])
        
        # Initialize snake positions
        for i in range(self.snake_length):
            pos_x = self.head_x - self.direction[0] * i * self.block_size
            pos_y = self.head_y - self.direction[1] * i * self.block_size
            self.positions.append((pos_x, pos_y))
        
        # Initialize food position
        self.food_pos = self._get_new_food_position()
        
        # Animation parameters
        self.move_timer = 0
        self.move_delay = 0.1  # seconds per movement

    def _get_new_food_position(self):
        """
        Generates a new random position for food
        """
        x = random.randint(0, (self.width - self.block_size) // self.block_size) * self.block_size
        y = random.randint(0, (self.height - self.block_size) // self.block_size) * self.block_size
        
        # Make sure food doesn't spawn on snake
        while (x, y) in self.positions:
            x = random.randint(0, (self.width - self.block_size) // self.block_size) * self.block_size
            y = random.randint(0, (self.height - self.block_size) // self.block_size) * self.block_size
            
        return (x, y)

    def update(self):
        """
        Updates snake position and checks for food collection
        """
        # Update position
        self.move_timer += 1
        
        if self.move_timer >= 4:  # Slowed down movement for smoother animation
            self.move_timer = 0
            
            # Change direction randomly sometimes
            if random.random() < 0.1:
                # Choose a direction that's not directly opposite to current
                possible_dirs = [(1, 0), (0, 1), (-1, 0), (0, -1)]
                opposite = (-self.direction[0], -self.direction[1])
                possible_dirs.remove(opposite)
                self.direction = random.choice(possible_dirs)
            
            # Calculate new head position
            head_x = self.positions[0][0] + self.direction[0] * self.block_size
            head_y = self.positions[0][1] + self.direction[1] * self.block_size
            
            # Wrap around edges
            if head_x < 0:
                head_x = self.width - self.block_size
            elif head_x >= self.width:
                head_x = 0
                
            if head_y < 0:
                head_y = self.height - self.block_size
            elif head_y >= self.height:
                head_y = 0
                
            # Add new head position
            self.positions.insert(0, (head_x, head_y))
            
            # Check if food eaten
            if self.positions[0] == self.food_pos:
                # Grow snake
                self.snake_length += 1
                # New food position
                self.food_pos = self._get_new_food_position()
            else:
                # If no food eaten, remove tail
                if len(self.positions) > self.snake_length:
                    self.positions.pop()

    def draw(self, surface):
        """
        Draws the snake and food on the given surface
        
        Args:
            surface: pygame surface to draw on
        """
        # Draw food with glow
        pygame.draw.rect(surface, FOOD_COLOR, (
            self.food_pos[0], 
            self.food_pos[1], 
            self.block_size, 
            self.block_size
        ))
        
        # Add small reflection on food
        pygame.draw.circle(
            surface, 
            WHITE, 
            (self.food_pos[0] + 4, self.food_pos[1] + 4), 
            2
        )
        
        # Draw snake with gradient coloring
        for i, pos in enumerate(self.positions):
            # Calculate gradient color based on position in snake
            progress = i / max(1, self.snake_length - 1)
            alpha = 255 - int(200 * progress)
            
            pygame.draw.rect(surface, (*SNAKE_COLOR, alpha), (
                pos[0], 
                pos[1], 
                self.block_size, 
                self.block_size
            ))
            
            # Draw smaller rectangle inside for texture
            inner_offset = 2
            inner_size = self.block_size - 2 * inner_offset
            pygame.draw.rect(surface, (*SNAKE_COLOR, alpha - 40), (
                pos[0] + inner_offset, 
                pos[1] + inner_offset, 
                inner_size, 
                inner_size
            ))