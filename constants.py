# -*- coding: utf-8 -*-
import pygame
pygame.init()

WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
FPS = 60

COLORS = {
    'bg': (15, 15, 25),  # Dark blue background
    'panel': (25, 25, 40),  # Panel background
    'panel_light': (35, 35, 55),  # Lighter panel
    'text': (220, 220, 235),  # Main text
    'text_dim': (150, 150, 170),  # Dimmed text
    'accent': (100, 150, 255),  # Blue accent
    'button': (60, 100, 180),  # Button color
    'button_hover': (80, 120, 200),  # Button hover
    'success': (80, 200, 120),  # Green for positive
    'warning': (255, 180, 80),  # Orange for warning
    'danger': (255, 100, 100),  # Red for danger
    'mandatory': (255, 120, 120),  # Red for mandatory
    'optional': (120, 180, 255),  # Blue for optional
    'timeline_bg': (40, 40, 60),  # Timeline background
    'timeline_hour': (60, 60, 80),  # Hour markers
    'activity_placed': (70, 140, 210),  # Placed activity
    'activity_conflict': (200, 80, 80),  # Conflicting activity
}
FONTS = {}

sizes = {
    'title': 32,
    'large': 28,
    'medium': 24,
    'small': 20,
    'tiny': 16
}

for name, size in sizes.items():
        FONTS[name] = pygame.font.Font(None, size)
        ##FONTS[name] = pygame.font.SysFont("segoeuisymbol", size)
