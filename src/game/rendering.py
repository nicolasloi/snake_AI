"""
Graphic rendering module for Snake AI
"""

import pygame
import math
from src.game.constants import *
from src.game.entities import Direction, Point

# Initialize font only once
if pygame.get_init():
    font = pygame.font.SysFont('arial', 25)
else:
    font = None

def draw_grid(display, width, height):
    """
    Draws the game grid
    """
    for x in range(0, width, GRID_SIZE):
        pygame.draw.line(display, GRID_COLOR, (x, 0), (x, height))
    for y in range(0, height, GRID_SIZE):
        pygame.draw.line(display, GRID_COLOR, (0, y), (width, y))

def draw_snake(display, snake, direction):
    """
    Draws the snake
    """
    for i, pt in enumerate(snake):
        if i == 0:  # Head
            draw_snake_head(display, pt, direction)
        else:  # Body
            draw_snake_body(display, pt)

def draw_snake_head(display, position, direction):
    """
    Draws the snake's head
    """
    pygame.draw.rect(display, BLUE1, pygame.Rect(position.x, position.y, BLOCK_SIZE, BLOCK_SIZE))
    
    # Add eyes based on direction
    eye_size = 4
    eye_offset = 4

    if direction == Direction.RIGHT:
        pygame.draw.rect(display, WHITE, pygame.Rect(position.x + BLOCK_SIZE - eye_offset, position.y + eye_offset, eye_size, eye_size))
        pygame.draw.rect(display, WHITE, pygame.Rect(position.x + BLOCK_SIZE - eye_offset, position.y + BLOCK_SIZE - eye_offset - eye_size, eye_size, eye_size))
    elif direction == Direction.LEFT:
        pygame.draw.rect(display, WHITE, pygame.Rect(position.x + eye_offset - eye_size, position.y + eye_offset, eye_size, eye_size))
        pygame.draw.rect(display, WHITE, pygame.Rect(position.x + eye_offset - eye_size, position.y + BLOCK_SIZE - eye_offset - eye_size, eye_size, eye_size))
    elif direction == Direction.UP:
        pygame.draw.rect(display, WHITE, pygame.Rect(position.x + eye_offset, position.y + eye_offset - eye_size, eye_size, eye_size))
        pygame.draw.rect(display, WHITE, pygame.Rect(position.x + BLOCK_SIZE - eye_offset - eye_size, position.y + eye_offset - eye_size, eye_size, eye_size))
    elif direction == Direction.DOWN:
        pygame.draw.rect(display, WHITE, pygame.Rect(position.x + eye_offset, position.y + BLOCK_SIZE - eye_offset, eye_size, eye_size))
        pygame.draw.rect(display, WHITE, pygame.Rect(position.x + BLOCK_SIZE - eye_offset - eye_size, position.y + BLOCK_SIZE - eye_offset, eye_size, eye_size))

def draw_snake_body(display, position):
    """
    Draws a segment of the snake's body
    """
    pygame.draw.rect(display, BLUE2, pygame.Rect(position.x, position.y, BLOCK_SIZE, BLOCK_SIZE))
    # Snake body pattern
    pygame.draw.rect(display, BLUE1, pygame.Rect(position.x + 4, position.y + 4, BLOCK_SIZE - 8, BLOCK_SIZE - 8))

def draw_food(display, food):
    """
    Draws the food with an effect
    """
    pygame.draw.rect(display, RED, pygame.Rect(food.x, food.y, BLOCK_SIZE, BLOCK_SIZE))
    pygame.draw.circle(display, WHITE, (food.x + 5, food.y + 5), 2)  # Reflection on the apple

def draw_info_box(display, game_info):
    """
    Draws the information box with score, etc.
    
    Args:
        game_info: dictionary containing information to display
    """
    global font
    
    if font is None and pygame.get_init():
        font = pygame.font.SysFont('arial', 25)
    
    # Create info box
    info_box = pygame.Surface((200, 100))
    info_box.fill((30, 30, 30))
    info_box.set_alpha(200)  # Semi-transparent
    display.blit(info_box, [10, 10])

    # Display game information
    score_text = font.render(f"Score: {game_info['score']}", True, WHITE)
    display.blit(score_text, [20, 15])

    game_text = font.render(f"Game: {game_info['games']}", True, WHITE)
    display.blit(game_text, [20, 45])

    record_text = font.render(f"Record: {game_info['record']}", True, WHITE)
    display.blit(record_text, [20, 75])

def draw_danger_arrows(display, state, direction, head_position):
    """
    Draws arrows indicating dangers around the snake's head
    """
    # Colors for danger arrows
    ARROW_COLORS = [
        (255, 0, 0),      # Red for immediate danger (1st block)
        (255, 165, 0),    # Orange for medium danger (2nd block)
        (255, 255, 0),    # Yellow for distant danger (3rd block)
        (200, 200, 0),    # Light yellow for 4th block
        (150, 150, 0)     # Very light yellow for 5th block
    ]
    
    # Arrow parameters
    arrow_length = [BLOCK_SIZE * 1.2, BLOCK_SIZE * 1.8, BLOCK_SIZE * 2.4, BLOCK_SIZE * 3.0, BLOCK_SIZE * 3.6]
    arrow_width = 3
    arrow_head_size = 7
    
    # Calculate center of snake's head
    center_x = head_position.x + BLOCK_SIZE // 2
    center_y = head_position.y + BLOCK_SIZE // 2
    
    # Define arrow directions based on current snake direction
    if direction == Direction.RIGHT:
        directions = [
            # Straight (right)
            [(center_x + arrow_length[i], center_y) for i in range(5)],
            # Right turn (down)
            [(center_x, center_y + arrow_length[i]) for i in range(5)],
            # Left turn (up)
            [(center_x, center_y - arrow_length[i]) for i in range(5)]
        ]
    elif direction == Direction.LEFT:
        directions = [
            # Straight (left)
            [(center_x - arrow_length[i], center_y) for i in range(5)],
            # Right turn (up)
            [(center_x, center_y - arrow_length[i]) for i in range(5)],
            # Left turn (down)
            [(center_x, center_y + arrow_length[i]) for i in range(5)]
        ]
    elif direction == Direction.UP:
        directions = [
            # Straight (up)
            [(center_x, center_y - arrow_length[i]) for i in range(5)],
            # Right turn (right)
            [(center_x + arrow_length[i], center_y) for i in range(5)],
            # Left turn (left)
            [(center_x - arrow_length[i], center_y) for i in range(5)]
        ]
    elif direction == Direction.DOWN:
        directions = [
            # Straight (down)
            [(center_x, center_y + arrow_length[i]) for i in range(5)],
            # Right turn (left)
            [(center_x - arrow_length[i], center_y) for i in range(5)],
            # Left turn (right)
            [(center_x + arrow_length[i], center_y) for i in range(5)]
        ]
    
    # Draw danger arrows for straight, right, left
    for dir_idx in range(3):  # 0=straight, 1=right, 2=left
        for dist_idx in range(5):  # 0=close, 1=medium, 2=far, 3=very far, 4=extremely far
            # Calculate index in state array
            state_idx = dir_idx * 5 + dist_idx
            
            # Check if the index exists in state before using it
            if state_idx < len(state) and state[state_idx]:
                # Draw arrow for this danger
                start_pos = (center_x, center_y)
                end_pos = directions[dir_idx][dist_idx]
                draw_arrow(display, start_pos, end_pos, ARROW_COLORS[dist_idx], arrow_width)

def draw_arrow(display, start_pos, end_pos, color, width):
    """
    Draws an arrow from start point to end point
    """
    # Draw main line
    pygame.draw.line(display, color, start_pos, end_pos, width)
    
    # Draw arrowhead
    arrow_head_size = 7
    angle = math.atan2(end_pos[1] - start_pos[1], end_pos[0] - start_pos[0])
    end_x, end_y = end_pos
    pygame.draw.polygon(display, color, [
        (end_x, end_y),
        (end_x - arrow_head_size * math.cos(angle - math.pi/6), 
         end_y - arrow_head_size * math.sin(angle - math.pi/6)),
        (end_x - arrow_head_size * math.cos(angle + math.pi/6), 
         end_y - arrow_head_size * math.sin(angle + math.pi/6))
    ])