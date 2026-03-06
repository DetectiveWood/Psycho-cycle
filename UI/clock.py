import pygame
import math
from constants import  COLORS

# Статические переменные модуля
_animation_active = False
_old_time = 8.0
_target_time = 8.0

# Запоминаем позицию часовой стрелки на время анимации
_fixed_hour_angle = None

def draw_analog_clock(screen, center_x, center_y, radius, current_time_hours):
    # Фон циферблата
    pygame.draw.circle(screen, COLORS.get('panel_light', (35, 35, 55)), (center_x, center_y), radius)
    pygame.draw.circle(screen, COLORS.get('accent', (100, 150, 255)), (center_x, center_y), radius, 3)

    # Метки часов (оставляем как было)
    for i in range(12):
        angle = math.radians(-90 + i * 30)
        x_outer = center_x + math.cos(angle) * (radius - 2)
        y_outer = center_y + math.sin(angle) * (radius - 2)
        inner_offset = 16 if i % 3 == 0 else 11
        x_inner = center_x + math.cos(angle) * (radius - inner_offset)
        y_inner = center_y + math.sin(angle) * (radius - inner_offset)
        thickness = 5 if i % 3 == 0 else 3
        pygame.draw.line(screen, COLORS.get('accent'), (x_inner, y_inner), (x_outer, y_outer), thickness)

    # Вычисляем положение стрелок напрямую из current_time_hours
    hours = current_time_hours % 12
    minutes = (current_time_hours % 1) * 60

    # Часовая стрелка
    hour_angle = math.radians(-90 + (hours + minutes / 60) * 30)
    hour_length = radius * 0.55
    hour_x = center_x + math.cos(hour_angle) * hour_length
    hour_y = center_y + math.sin(hour_angle) * hour_length
    pygame.draw.line(screen, COLORS.get('text', (220, 220, 235)), (center_x, center_y), (hour_x, hour_y), 5)

    # Минутная стрелка
    minute_angle = math.radians(-90 + minutes * 6)
    minute_length = radius * 0.80
    minute_x = center_x + math.cos(minute_angle) * minute_length
    minute_y = center_y + math.sin(minute_angle) * minute_length
    pygame.draw.line(screen, COLORS.get('text_dim', (150, 150, 170)), (center_x, center_y), (minute_x, minute_y), 3)

    # Центральная точка
    pygame.draw.circle(screen, COLORS.get('accent'), (center_x, center_y), 6)