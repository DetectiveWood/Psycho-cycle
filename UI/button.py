# -*- coding: utf-8 -*-
import pygame
from constants import COLORS, FONTS

class Button:
    def __init__(self, x, y, width, height, text, size='medium'):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.size = size
        self.hovered = False
        self.clicked = False

    def update(self, mouse_pos, mouse_clicked):
        """Update button state and return if clicked"""
        self.hovered = self.rect.collidepoint(mouse_pos)
        if self.hovered and mouse_clicked:
            self.clicked = True
            return True
        self.clicked = False
        return False

    def draw(self, screen, disabled=False):
        """Draw the button"""
        if disabled:
            # Disabled button appearance
            color = tuple(c // 3 for c in COLORS['button'])  # Much darker
            border_color = COLORS['text_dim']
            text_color = COLORS['text_dim']
        else:
            # Normal button appearance
            color = COLORS['button_hover'] if self.hovered else COLORS['button']
            border_color = COLORS['accent']
            text_color = COLORS['text']

        pygame.draw.rect(screen, color, self.rect, border_radius=5)
        pygame.draw.rect(screen, border_color, self.rect, 2, border_radius=5)

        # Draw text
        font = FONTS[self.size]
        text_surface = font.render(self.text, True, text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
