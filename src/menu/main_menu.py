"""
Main menu implementation for Snake AI
"""

import pygame
import os
import sys
import random
import math
from src.menu.colors import *
from src.menu.button import ModernButton
from src.menu.background import Snake

def show_menu():
    """
    Display the main menu and return the user's choice
    
    Returns:
        bool: True if user wants to use existing model, False for new model
    """
    # Initialize pygame inside the function ONLY if it's not already initialized
    if not pygame.get_init():
        pygame.init()
    
    # Screen configuration
    WIDTH, HEIGHT = 800, 600
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Snake AI - Main Menu')
    
    # Load fonts
    title_font = pygame.font.Font(None, 80)
    button_font = pygame.font.Font(None, 36)
    info_font = pygame.font.Font(None, 24)
    
    # Create clock for limiting FPS
    clock = pygame.time.Clock()
    
    # Create background animation elements
    snake_bg = Snake(WIDTH, HEIGHT)
    
    # Variables
    result = False  # Default value
    run_time = 0
    fade_alpha = 255  # For fade-in effect
    
    # Check if a model exists
    model_path = os.path.join('./model', 'model.pth')
    model_exists = os.path.exists(model_path)
    
    # Action functions that store result in nonlocal variable
    def use_existing():
        nonlocal result
        result = True
        return True
        
    def create_new():
        nonlocal result
        result = False
        return True
    
    def exit_game():
        pygame.quit()
        sys.exit()
    
    # Create buttons
    buttons = [
        ModernButton(WIDTH//2 - 150, HEIGHT//2 - 30, 300, 60, "Use existing model", 
                    DARK_GREEN, NEON_GREEN, WHITE, action=use_existing, enabled=model_exists),
        ModernButton(WIDTH//2 - 150, HEIGHT//2 + 50, 300, 60, "Create new model", 
                    DARK_BLUE, NEON_BLUE, WHITE, action=create_new),
        ModernButton(WIDTH//2 - 150, HEIGHT//2 + 130, 300, 60, "Quit", 
                    DARK_RED, NEON_RED, WHITE, action=exit_game)
    ]
    
    running = True
    while running:
        dt = clock.tick(60) / 1000.0  # Convert to seconds
        run_time += dt
        
        # Process events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            for button in buttons:
                if button.handle_event(event):
                    running = False
                    break
        
        # Update
        snake_bg.update()
        
        # Update button animations
        for button in buttons:
            button.update(dt)
        
        # Draw
        # Background gradient
        for y in range(0, HEIGHT, 2):
            progress = y / HEIGHT
            r = DARK_BG[0] + (LIGHT_BG[0] - DARK_BG[0]) * progress
            g = DARK_BG[1] + (LIGHT_BG[1] - DARK_BG[1]) * progress
            b = DARK_BG[2] + (LIGHT_BG[2] - DARK_BG[2]) * progress
            pygame.draw.line(screen, (r, g, b), (0, y), (WIDTH, y))
        
        # Draw grid pattern
        grid_size = 40
        grid_alpha = 30
        grid_color = (*WHITE[:3], grid_alpha)
        for x in range(0, WIDTH, grid_size):
            pygame.draw.line(screen, grid_color, (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, grid_size):
            pygame.draw.line(screen, grid_color, (0, y), (WIDTH, y))
            
        # Draw animated snake in background
        snake_bg.draw(screen)
        
        # Draw title with glow effect
        title_text = "SNAKE AI"
        title_shadow = title_font.render(title_text, True, BLACK)
        title_surf = title_font.render(title_text, True, WHITE)
        
        # Simplified glow effect
        glow_color = ACCENT
        title_glow = title_font.render(title_text, True, glow_color)
        glow_rect = title_glow.get_rect(center=(WIDTH//2, 120))
        
        # Apply pulsing effect to the glow
        pulse_value = (math.sin(run_time * 2) + 1) * 0.5
        for i in range(3):
            offset = i * 2
            glow_alpha = int(200 * (1 - i/3) * pulse_value)
            glow_surf = title_font.render(title_text, True, (*glow_color, glow_alpha))
            screen.blit(glow_surf, (glow_rect.x - offset, glow_rect.y - offset))
            screen.blit(glow_surf, (glow_rect.x + offset, glow_rect.y - offset))
            
        # Draw title text
        title_rect = title_surf.get_rect(center=(WIDTH//2, 120))
        screen.blit(title_shadow, (title_rect.x + 3, title_rect.y + 3))
        screen.blit(title_surf, title_rect)
        
        # Information message
        if not model_exists:
            info_text = "No existing model found"
            info_surf = info_font.render(info_text, True, NEON_RED)
            info_rect = info_surf.get_rect(center=(WIDTH//2, HEIGHT//2 - 80))
            screen.blit(info_surf, info_rect)
        
        # Display version info
        version_surf = info_font.render("Version 1.0", True, (*WHITE, 128))
        version_rect = version_surf.get_rect(bottomright=(WIDTH-20, HEIGHT-20))
        screen.blit(version_surf, version_rect)
        
        # Display buttons
        for button in buttons:
            button.draw(screen, button_font)
        
        # Fade-in effect
        if fade_alpha > 0:
            fade_surface = pygame.Surface((WIDTH, HEIGHT))
            fade_surface.fill(BLACK)
            fade_surface.set_alpha(fade_alpha)
            screen.blit(fade_surface, (0, 0))
            fade_alpha = max(0, fade_alpha - 5)
        
        pygame.display.flip()
    
    # Fade-out effect
    fade_alpha = 0
    while fade_alpha < 255:
        clock.tick(60)
        fade_alpha = min(255, fade_alpha + 10)
        
        # Draw everything again
        # Background gradient
        for y in range(0, HEIGHT, 2):
            progress = y / HEIGHT
            r = DARK_BG[0] + (LIGHT_BG[0] - DARK_BG[0]) * progress
            g = DARK_BG[1] + (LIGHT_BG[1] - DARK_BG[1]) * progress
            b = DARK_BG[2] + (LIGHT_BG[2] - DARK_BG[2]) * progress
            pygame.draw.line(screen, (r, g, b), (0, y), (WIDTH, y))
            
        # Draw grid pattern
        for x in range(0, WIDTH, grid_size):
            pygame.draw.line(screen, grid_color, (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, grid_size):
            pygame.draw.line(screen, grid_color, (0, y), (WIDTH, y))
            
        # Draw snake
        snake_bg.update()
        snake_bg.draw(screen)
        
        # Title
        screen.blit(title_shadow, (title_rect.x + 3, title_rect.y + 3))
        screen.blit(title_surf, title_rect)
        
        # Buttons
        for button in buttons:
            button.draw(screen, button_font)
        
        # Fade overlay
        fade_surface = pygame.Surface((WIDTH, HEIGHT))
        fade_surface.fill(BLACK)
        fade_surface.set_alpha(fade_alpha)
        screen.blit(fade_surface, (0, 0))
        
        pygame.display.flip()
    
    # Don't close pygame here, the main game still needs it
    return result