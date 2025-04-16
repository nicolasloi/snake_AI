"""
State management module for Snake AI Agent
"""

import numpy as np
from src.game.entities import Point, Direction

def get_state(game):
    """
    Extracts the current state of the game for the agent
    
    Args:
        game: instance of SnakeGameAI
        
    Returns:
        A numpy array representing the game state
    """
    head = game.snake[0]
    block_size = game.w // 32  # Assumed value of BLOCK_SIZE
    
    # Define points at 1, 2, and 3 blocks distance in each direction
    # Left direction
    point_l1 = Point(head.x - block_size, head.y)
    point_l2 = Point(head.x - (2 * block_size), head.y)
    point_l3 = Point(head.x - (3 * block_size), head.y)
    
    # Right direction
    point_r1 = Point(head.x + block_size, head.y)
    point_r2 = Point(head.x + (2 * block_size), head.y)
    point_r3 = Point(head.x + (3 * block_size), head.y)
    
    # Up direction
    point_u1 = Point(head.x, head.y - block_size)
    point_u2 = Point(head.x, head.y - (2 * block_size))
    point_u3 = Point(head.x, head.y - (3 * block_size))
    
    # Down direction
    point_d1 = Point(head.x, head.y + block_size)
    point_d2 = Point(head.x, head.y + (2 * block_size))
    point_d3 = Point(head.x, head.y + (3 * block_size))

    # Current direction
    dir_l = game.direction == Direction.LEFT
    dir_r = game.direction == Direction.RIGHT
    dir_u = game.direction == Direction.UP
    dir_d = game.direction == Direction.DOWN

    # Extended state with perception at 3 blocks
    state = [
        # Danger straight ahead - 1st block
        (dir_r and game.is_collision(point_r1)) or 
        (dir_l and game.is_collision(point_l1)) or
        (dir_u and game.is_collision(point_u1)) or
        (dir_d and game.is_collision(point_d1)),
        
        # Danger straight ahead - 2nd block
        (dir_r and game.is_collision(point_r2)) or 
        (dir_l and game.is_collision(point_l2)) or
        (dir_u and game.is_collision(point_u2)) or
        (dir_d and game.is_collision(point_d2)),
        
        # Danger straight ahead - 3rd block
        (dir_r and game.is_collision(point_r3)) or 
        (dir_l and game.is_collision(point_l3)) or
        (dir_u and game.is_collision(point_u3)) or
        (dir_d and game.is_collision(point_d3)),

        # Danger to the right - 1st block
        (dir_u and game.is_collision(point_r1)) or 
        (dir_d and game.is_collision(point_l1)) or
        (dir_l and game.is_collision(point_u1)) or
        (dir_r and game.is_collision(point_d1)),
        
        # Danger to the right - 2nd block
        (dir_u and game.is_collision(point_r2)) or 
        (dir_d and game.is_collision(point_l2)) or
        (dir_l and game.is_collision(point_u2)) or
        (dir_r and game.is_collision(point_d2)),
        
        # Danger to the right - 3rd block
        (dir_u and game.is_collision(point_r3)) or 
        (dir_d and game.is_collision(point_l3)) or
        (dir_l and game.is_collision(point_u3)) or
        (dir_r and game.is_collision(point_d3)),

        # Danger to the left - 1st block
        (dir_d and game.is_collision(point_r1)) or 
        (dir_u and game.is_collision(point_l1)) or
        (dir_r and game.is_collision(point_u1)) or
        (dir_l and game.is_collision(point_d1)),
        
        # Danger to the left - 2nd block
        (dir_d and game.is_collision(point_r2)) or 
        (dir_u and game.is_collision(point_l2)) or
        (dir_r and game.is_collision(point_u2)) or
        (dir_l and game.is_collision(point_d2)),
        
        # Danger to the left - 3rd block
        (dir_d and game.is_collision(point_r3)) or 
        (dir_u and game.is_collision(point_l3)) or
        (dir_r and game.is_collision(point_u3)) or
        (dir_l and game.is_collision(point_d3)),

        # Current direction
        dir_l,
        dir_r,
        dir_u,
        dir_d,

        # Food position relative to head
        game.food.x < game.head.x,  # food left
        game.food.x > game.head.x,  # food right
        game.food.y < game.head.y,  # food up
        game.food.y > game.head.y   # food down
    ]
    
    return np.array(state, dtype=int)