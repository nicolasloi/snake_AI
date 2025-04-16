"""
Interactive button module for Snake AI menu
"""

import pygame
import math

class ModernButton:
    """
    Modern animated button with hover and click effects
    """
    def __init__(self, x, y, width, height, text, color, hover_color, text_color, action=None, enabled=True):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.text = text
        self.action = action
        self.enabled = enabled
        
        # Animation variables
        self.hover = False
        self.click = False
        self.animation_progress = 0.0
        self.wave_offset = 0.0
        self.alpha = 255 if enabled else 100

    def handle_event(self, event):
        """
        Handles mouse events for the button
        
        Args:
            event: pygame event
            
        Returns:
            True if action was triggered, False otherwise
        """
        if not self.enabled:
            return False
            
        if event.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)
                
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.hover:
                self.click = True
                return False
                
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and self.click and self.hover and self.action:
                self.click = False
                return self.action()
                
            self.click = False
                
        return False
        
    def update(self, dt):
        """
        Updates button animations
        
        Args:
            dt: time delta in seconds
        """
        # Update hover animation
        target = 1.0 if self.hover else 0.0
        self.animation_progress += (target - self.animation_progress) * min(1.0, dt * 10)
        
        # Update wave animation
        self.wave_offset += dt * 2.0

    def draw(self, surface, font):
        """
        Draws the button
        
        Args:
            surface: pygame surface to draw on
            font: pygame font for text rendering
        """
        width = self.rect.width
        height = self.rect.height
        
        # Calculate current color based on hover state
        r = self.color[0] + (self.hover_color[0] - self.color[0]) * self.animation_progress
        g = self.color[1] + (self.hover_color[1] - self.color[1]) * self.animation_progress
        b = self.color[2] + (self.hover_color[2] - self.color[2]) * self.animation_progress
        
        # Button shadow
        shadow_rect = pygame.Rect(self.rect.x + 3, self.rect.y + 3, width, height)
        pygame.draw.rect(surface, (20, 20, 20, 100), shadow_rect, border_radius=10)
        
        # Main button rect with border radius
        button_color = (r, g, b, self.alpha)
        pygame.draw.rect(surface, button_color, self.rect, border_radius=10)
        
        # Add glow effect when hovered
        if self.hover and self.enabled:
            for i in range(3):
                glow_rect = pygame.Rect(
                    self.rect.x - i*2, 
                    self.rect.y - i*2, 
                    width + i*4, 
                    height + i*4
                )
                glow_alpha = int(100 * (3-i)/3 * self.animation_progress)
                pygame.draw.rect(
                    surface, 
                    (*self.hover_color, glow_alpha), 
                    glow_rect, 
                    border_radius=10, 
                    width=2
                )
        
        # Add animated elements for non-disabled buttons
        if self.enabled:
            # Animated border (wave effect)
            wave_positions = []
            num_points = 20
            for i in range(num_points):
                angle = (i / num_points) * math.pi * 2 + self.wave_offset
                
                # Calculate position on the rounded rectangle
                # This is a simplification, doesn't perfectly follow border
                cx = self.rect.centerx
                cy = self.rect.centery
                rx = width / 2
                ry = height / 2
                
                x = cx + rx * math.cos(angle)
                y = cy + ry * math.sin(angle)
                
                wave_positions.append((x, y))
            
            # Draw pulsing dots along the border
            for pos in wave_positions:
                size = 2 + math.sin(self.wave_offset * 2) * 1
                alpha = 150 + math.sin(self.wave_offset + wave_positions.index(pos) * 0.5) * 100
                dot_color = (*self.hover_color, int(alpha))
                pygame.draw.circle(surface, dot_color, pos, size)
        
        # Render text
        if self.enabled:
            text_color = self.text_color
        else:
            text_color = (128, 128, 128)  # Gray for disabled buttons
            
        text_surf = font.render(self.text, True, text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        
        # Add slight offset when clicked
        if self.click and self.enabled:
            text_rect.x += 2
            text_rect.y += 2
            
        surface.blit(text_surf, text_rect)