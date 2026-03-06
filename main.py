# -*- coding: utf-8 -*-
import pygame
import sys
from Systems import VisualDayPlanningGame

pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

try:
    game = VisualDayPlanningGame()
    game.run()
except Exception as e:
    print(f"Ошибка запуска игры: {e}")
    pygame.quit()
    sys.exit(1)

