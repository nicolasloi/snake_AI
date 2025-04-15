"""
Button class for Snake AI menu
"""

import pygame
from src.menu.colors import *

class ModernButton:
    def __init__(self, x, y, width, height, text, normal_color, hover_color, text_color, action=None, enabled=True):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.normal_color = normal_color
        self.hover_color = hover_color
        self.current_color = normal_color
        self.target_color = normal_color
        self.text_color = text_color
        self.action = action
        self.enabled = enabled
        self.hover = False
        self.scale = 1.0
        self.target_scale = 1.0
        
    def update(self, dt):
        # Smooth color transition
        r = self.current_color[0] + (self.target_color[0] - self.current_color[0]) * 0.1
        g = self.current_color[1] + (self.target_color[1] - self.current_color[1]) * 0.1
        b = self.current_color[2] + (self.target_color[2] - self.current_color[2]) * 0.1
        self.current_color = (r, g, b)
        
        # Smooth scale transition
        self.scale += (self.target_scale - self.scale) * 0.1
        
    def draw(self, surface, font):
        if not self.enabled:
            color = (80, 80, 100)
            self.target_scale = 1.0
        elif self.hover:
            color = self.hover_color
            self.target_color = self.hover_color
            self.target_scale = 1.05
        else:
            color = self.normal_color
            self.target_color = self.normal_color
            self.target_scale = 1.0
            
        # Calculate scaled dimensions
        scaled_width = self.rect.width * self.scale
        scaled_height = self.rect.height * self.scale
        x = self.rect.centerx - scaled_width // 2
        y = self.rect.centery - scaled_height // 2
        
        # Create rounded rectangle
        rect = pygame.Rect(x, y, scaled_width, scaled_height)
        
        # Draw button with gradient
        self._draw_rounded_rect_with_gradient(surface, rect)
        
        # Draw text with shadow
        text_surf = font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=rect.center)
        
        # Add subtle text shadow
        shadow_surf = font.render(self.text, True, (30, 30, 30))
        shadow_rect = shadow_surf.get_rect(center=(text_rect.centerx + 2, text_rect.centery + 2))
        surface.blit(shadow_surf, shadow_rect)
        surface.blit(text_surf, text_rect)
    
    def _draw_rounded_rect_with_gradient(self, surface, rect):
        # Simplified gradient for better compatibility
        border_radius = 20
        
        # Draw base button with rounded corners
        pygame.draw.rect(surface, self.current_color, rect, border_radius=border_radius)
        
        # Add border for definition
        pygame.draw.rect(surface, (50, 50, 50), rect, width=2, border_radius=border_radius)
        
        # Add highlight at top
        highlight_rect = pygame.Rect(rect.x + 2, rect.y + 2, rect.width - 4, rect.height // 3)
        pygame.draw.rect(surface, (*self.current_color[:3], 100), highlight_rect, border_radius=border_radius)
        
    def handle_event(self, event):
        if not self.enabled:
            return False
            
        mouse_pos = pygame.mouse.get_pos()
        self.hover = self.rect.collidepoint(mouse_pos)
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.hover:
                if self.action:
                    self.action()
                return True
        return False