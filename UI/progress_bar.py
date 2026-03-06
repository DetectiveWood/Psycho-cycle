# -*- coding: utf-8 -*-
import pygame
from constants import COLORS, FONTS

class ProgressBar:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.value = 0

    def set_value(self, value):
        self.value = max(0, min(100, value))

    def draw(self, screen, color=None, label=""):
        """Draw the progress bar with enhanced styling"""
        if color is None:
            color = COLORS['accent']

        # Background with shadow effect
        shadow_rect = pygame.Rect(self.rect.x + 2, self.rect.y + 2, self.rect.width, self.rect.height)
        pygame.draw.rect(screen, (10, 10, 15), shadow_rect, border_radius=5)

        # Background
        pygame.draw.rect(screen, COLORS['panel_light'], self.rect, border_radius=5)
        pygame.draw.rect(screen, COLORS['accent'], self.rect, 2, border_radius=5)

        # Fill with gradient effect
        fill_width = int((self.value / 100) * (self.rect.width - 4))
        if fill_width > 0:
            fill_rect = pygame.Rect(self.rect.x + 2, self.rect.y + 2, fill_width, self.rect.height - 4)
            pygame.draw.rect(screen, color, fill_rect, border_radius=3)

            # Highlight on top
            highlight_rect = pygame.Rect(fill_rect.x, fill_rect.y, fill_rect.width, 6)
            highlight_color = tuple(min(255, c + 30) for c in color)
            pygame.draw.rect(screen, highlight_color, highlight_rect, border_radius=3)

        # Label and value text
        if label:
            label_surface = FONTS['small'].render(f"{label}: {int(self.value)}", True, COLORS['text'])
        else:
            label_surface = FONTS['small'].render(f"{int(self.value)}", True, COLORS['text'])

        # Add shadow to text
        shadow_surface = FONTS['small'].render(f"{label}: {int(self.value)}" if label else f"{int(self.value)}", True,
                                               (0, 0, 0))
        screen.blit(shadow_surface, (self.rect.centerx - label_surface.get_width() // 2 + 1,
                                     self.rect.centery - label_surface.get_height() // 2 + 1))
        screen.blit(label_surface, (
            self.rect.centerx - label_surface.get_width() // 2, self.rect.centery - label_surface.get_height() // 2))
