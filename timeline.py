# -*- coding: utf-8 -*-
import pygame
from constants import FONTS

class TimelineActivity:
    def __init__(self, activity, start_time, end_time, x, y, width, height):
        self.activity = activity
        self.start_time = start_time
        self.end_time = end_time
        self.rect = pygame.Rect(x, y, width, height)
        self.dragging = False
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        self.has_conflict = False
        self.marked_for_delete = False

    def update_position(self, x, y):
        self.rect.x = x
        self.rect.y = y

    def draw_current_time_arrow(screen, timeline_rect, arrow_x):
        """
        Рисует красивую стрелку текущего времени по уже готовой координате X.

        Параметры:
        - screen: поверхность для отрисовки
        - timeline_rect: прямоугольник таймлайна (нужен только для Y-координат)
        - arrow_x: точная X-координата стрелки (int или float, будет приведено к int)
        """
        # Приводим X к целому (gfxdraw и draw.line любят int)
        arrow_x = int(arrow_x)

        # Координаты по Y (подгони под свой дизайн)
        tip_y = timeline_rect.top + 70  # верхушка чуть выше панели
        base_y = tip_y - 16  # высота треугольника 16 px
        line_end_y = tip_y - 16  # линия чуть ниже панели

        # Цвета
        fill_color = (240, 80, 80)  # заливка
        border_color = (200, 50, 50)  # обводка
        highlight_color = (255, 160, 160)  # блик

        # Точки треугольника
        points = [
            (arrow_x, tip_y),
            (arrow_x - 8, base_y),
            (arrow_x + 8, base_y),
        ]

        # Заливка треугольника (гладкая)
        pygame.gfxdraw.filled_trigon(screen,
                                     points[0][0], points[0][1],
                                     points[1][0], points[1][1],
                                     points[2][0], points[2][1],
                                     fill_color)

        # Гладкая обводка
        pygame.gfxdraw.aatrigon(screen,
                                points[0][0], points[0][1],
                                points[1][0], points[1][1],
                                points[2][0], points[2][1],
                                border_color)

        # Дополнительная обводка для чёткости
        pygame.gfxdraw.trigon(screen,
                              points[0][0], points[0][1],
                              points[1][0], points[1][1],
                              points[2][0], points[2][1],
                              border_color)

        # Вертикальная линия вниз
        pygame.draw.line(screen, fill_color,
                         (arrow_x, base_y),
                         (arrow_x, line_end_y), 2)

        # Тонкая тень справа
        pygame.draw.line(screen, (0, 0, 0, 40),
                         (arrow_x + 1, base_y),
                         (arrow_x + 1, line_end_y), 1)