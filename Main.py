# -*- coding: utf-8 -*-
import pygame
import sys
import random
import time
from typing import Dict, List, Tuple, Optional
import math

# Initialize Pygame
pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

# Constants
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
FPS = 60

# Colors
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
# Initialiпрze fonts
FONTS = {}


def init_fonts():
    """Initialize font objects"""
    try:
        FONTS['title'] = pygame.font.Font(None, 32)
        FONTS['large'] = pygame.font.Font(None, 28)
        FONTS['medium'] = pygame.font.Font(None, 24)
        FONTS['small'] = pygame.font.Font(None, 20)
        FONTS['tiny'] = pygame.font.Font(None, 16)
    except:
        # Fallback if no fonts available
        FONTS['title'] = pygame.font.Font(None, 32)
        FONTS['large'] = pygame.font.Font(None, 28)
        FONTS['medium'] = pygame.font.Font(None, 24)
        FONTS['small'] = pygame.font.Font(None, 20)
        FONTS['tiny'] = pygame.font.Font(None, 16)


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

    def update_position(self, x, y):
        self.rect.x = x
        self.rect.y = y


class DreamSystem:
    """Система снов с различными категориями"""

    def __init__(self):
        self.dreams = {
            # Предупреждающие сны (warning) - негативные сны о локациях/действиях
            'warning_restaurant': {
                'type': 'warning',
                'target': 'location',
                'location': 'restaurant',
                'descriptions': [
                    'Вам снится ресторан, наполненный странным шёпотом. Все посетители смотрят на вас, а еда имеет странный привкус...',
                    'Во сне вы заходите в ресторан, но все столы пустые. Официант подаёт вам блюдо, но внутри что-то шевелится...',
                    'Сон показывает ресторан в огне. Вы пытаетесь выбраться, но двери заперты. Дым становится всё гуще...'
                ],
                'penalty': {'stress': 15, 'paranoia': 10, 'energy': -10},
                'base_chance': 0.15,
                'stat_modifiers': {'stress': 0.3, 'paranoia': 0.4}
            },
            'warning_walk': {
                'type': 'warning',
                'target': 'activity',
                'activity': 'прогул',  # Будет матчиться с "Утренняя прогулка" и "Вечерняя прогулка"
                'descriptions': [
                    'Во время прогулки вокруг становится мрачно. Тени двигаются сами по себе, а ветер шепчет тревожные слова...',
                    'Вы гуляете, но небо становится всё темнее. Ветер усиливается, и вы слышите чьи-то шаги за спиной...',
                    'Во сне прогулка превращается в лабиринт. Вы заблудились, а из тумана появляются странные силуэты...'
                ],
                'penalty': {'stress': 12, 'paranoia': 15, 'energy': -8},
                'base_chance': 0.15,
                'stat_modifiers': {'stress': 0.2, 'paranoia': 0.5}
            },
            'warning_cinema': {
                'type': 'warning',
                'target': 'location',
                'location': 'cinema',
                'descriptions': [
                    'Кинотеатр во сне пуст, кроме вас. На экране показывают ваши худшие воспоминания, и вы не можете отвести взгляд...',
                    'Вы смотрите фильм, но внезапно экран становится чёрным. Все двери заперты, и свет гаснет...',
                    'Сон показывает кинотеатр, где все зрители - это вы в разные моменты жизни. Они все смотрят на вас с осуждением...'
                ],
                'penalty': {'stress': 18, 'paranoia': 12, 'energy': -5},
                'base_chance': 0.12,
                'stat_modifiers': {'stress': 0.4, 'paranoia': 0.3}
            },
            'warning_gym': {
                'type': 'warning',
                'target': 'location',
                'location': 'gym',
                'descriptions': [
                    'В спортзале все тренажёры двигаются сами. Вы пытаетесь бежать, но беговая дорожка ускоряется, не давая остановиться...',
                    'Во сне вы в спортзале, но не можете двигаться. Ваше тело не слушается, а зеркала показывают искажённое отражение...',
                    'Сон показывает пустой спортзал ночью. Слышны странные звуки из раздевалок, и свет мигает...'
                ],
                'penalty': {'stress': 10, 'energy': -15},
                'base_chance': 0.10,
                'stat_modifiers': {'stress': 0.3, 'energy': -0.2}
            },

            # Предупреждающие сны о действиях
            'warning_reading': {
                'type': 'warning',
                'target': 'activity',
                'activity': 'Чтение',
                'descriptions': [
                    'Вам снится, что вы читаете книгу, но буквы складываются в пугающие предсказания о вашем будущем...',
                    'Во сне каждая прочитанная страница высасывает из вас силы. Книга притягивает вас, не давая оторваться...',
                    'Сон показывает библиотеку, где все книги говорят одновременно, создавая невыносимый шум в вашей голове...'
                ],
                'penalty': {'stress': 20, 'paranoia': 8, 'energy': -12},
                'base_chance': 0.08,
                'stat_modifiers': {'paranoia': 0.5, 'stress': 0.2}
            },
            'warning_work': {
                'type': 'warning',
                'target': 'activity',
                'activity': 'Работа',
                'descriptions': [
                    'Во сне вы работаете, но задачи множатся. Чем больше вы делаете, тем больше их появляется. Вы в ловушке...',
                    'Сон показывает ваше рабочее место, затопленное бумагами. Вы тонете в них, не в силах выбраться...',
                    'Вам снится, что вы работаете уже несколько дней подряд без сна. Реальность начинает размываться...'
                ],
                'penalty': {'stress': 25, 'energy': -20},
                'base_chance': 0.12,
                'stat_modifiers': {'stress': 0.6, 'energy': -0.3}
            },

            # Мотивирующие сны (motivating) - позитивные сны о локациях/действиях
            'motivating_home': {
                'type': 'motivating',
                'target': 'location',
                'location': 'home',
                'descriptions': [
                    'Вам снится ваш дом, наполненный тёплым светом и уютом. Вы чувствуете себя в безопасности и покое...',
                    'Во сне вы дома, и всё вокруг идеально. Вы ощущаете глубокое спокойствие и желание провести там больше времени...',
                    'Сон показывает ваш дом как убежище от всех проблем. Каждый уголок излучает тепло и комфорт...'
                ],
                'bonus': {'stress': -10, 'energy': 15},
                'penalty_if_not_done': {'stress': 15, 'paranoia': 5},
                'base_chance': 0.20,
                'stat_modifiers': {'stress': -0.3, 'paranoia': -0.2}
            },
            'motivating_park': {
                'type': 'motivating',
                'target': 'location',
                'location': 'park',
                'descriptions': [
                    'Во сне вы гуляете по прекрасному парку. Солнце светит, птицы поют, и вы чувствуете необыкновенную лёгкость...',
                    'Сон показывает парк в золотых лучах заката. Вы идёте по аллее, и каждый шаг наполняет вас энергией...',
                    'Вам снится парк весной, когда всё цветёт. Аромат цветов успокаивает, и вы хотите вернуться туда наяву...'
                ],
                'bonus': {'stress': -15, 'energy': 10, 'paranoia': -5},
                'penalty_if_not_done': {'stress': 12, 'energy': -10},
                'base_chance': 0.18,
                'stat_modifiers': {'stress': -0.4, 'energy': 0.2}
            },
            'motivating_reading': {
                'type': 'motivating',
                'target': 'activity',
                'activity': 'Чтение',
                'descriptions': [
                    'Вам снится удивительная книга, которая открывает новые миры. Вы просыпаетесь с желанием читать...',
                    'Во сне вы в уютной библиотеке, окружены интересными книгами. Чтение приносит вам глубокое удовлетворение...',
                    'Сон показывает, как знания из книг помогают вам решить все проблемы. Вы понимаете силу чтения...'
                ],
                'bonus': {'stress': -12, 'energy': 8, 'paranoia': -8},
                'penalty_if_not_done': {'stress': 18, 'paranoia': 10},
                'base_chance': 0.15,
                'stat_modifiers': {'paranoia': -0.4, 'stress': -0.3}
            },
            'motivating_exercise': {
                'type': 'motivating',
                'target': 'activity',
                'activity': 'Спорт',
                'descriptions': [
                    'Во сне вы бежите, и это легко и приятно. Ваше тело полно энергии, вы чувствуете себя сильным...',
                    'Сон показывает вас после тренировки - довольным и полным сил. Вы хотите испытать это в реальности...',
                    'Вам снится, что физическая активность решает все ваши проблемы. Вы просыпаетесь с желанием двигаться...'
                ],
                'bonus': {'energy': 20, 'stress': -8},
                'penalty_if_not_done': {'energy': -15, 'stress': 10},
                'base_chance': 0.12,
                'stat_modifiers': {'energy': 0.3, 'stress': -0.2}
            },
            'motivating_meditation': {
                'type': 'motivating',
                'target': 'activity',
                'activity': 'Медитация',
                'descriptions': [
                    'Во сне вы медитируете, и достигаете полного внутреннего покоя. Это чувство остаётся после пробуждения...',
                    'Сон показывает вас в состоянии глубокой медитации. Все тревоги уходят, остаётся только спокойствие...',
                    'Вам снится, что медитация даёт вам контроль над мыслями и эмоциями. Вы хотите это повторить...'
                ],
                'bonus': {'stress': -20, 'paranoia': -15, 'energy': 10},
                'penalty_if_not_done': {'stress': 20, 'paranoia': 12},
                'base_chance': 0.14,
                'stat_modifiers': {'stress': -0.5, 'paranoia': -0.6}
            }
        }

        self.current_dream = None
        self.pending_motivation_check = False

    def generate_dream(self, stress, paranoia, energy):
        """Генерирует сон на основе статов и случайности"""
        available_dreams = []

        for dream_id, dream_data in self.dreams.items():
            chance = dream_data['base_chance']

            # Модификация шанса от статов
            stat_mods = dream_data['stat_modifiers']
            if 'stress' in stat_mods:
                chance += (stress / 100) * stat_mods['stress']
            if 'paranoia' in stat_mods:
                chance += (paranoia / 100) * stat_mods['paranoia']
            if 'energy' in stat_mods:
                chance += (energy / 100) * stat_mods['energy']

            # Нормализуем шанс (минимум 5%, максимум 40%)
            chance = max(0.05, min(0.40, chance))

            if random.random() < chance:
                available_dreams.append((dream_id, dream_data, chance))

        if not available_dreams:
            return None

        # Выбираем один случайный сон из доступных
        dream_id, dream_data, chance = random.choice(available_dreams)

        # Выбираем случайное описание из списка
        description = random.choice(dream_data['descriptions'])

        dream_info = {
            'id': dream_id,
            'type': dream_data['type'],
            'target': dream_data['target'],
            'description': description,
            'chance_rolled': chance
        }

        # Добавляем специфичные данные в зависимости от типа
        if dream_data['target'] == 'location':
            dream_info['location'] = dream_data['location']
        elif dream_data['target'] == 'activity':
            dream_info['activity'] = dream_data['activity']

        if dream_data['type'] == 'warning':
            dream_info['penalty'] = dream_data['penalty']
        elif dream_data['type'] == 'motivating':
            dream_info['bonus'] = dream_data['bonus']
            dream_info['penalty_if_not_done'] = dream_data['penalty_if_not_done']

        return dream_info


class GameState:
    def __init__(self):
        self.day = 1
        self.phase = 'planning'  # 'planning', 'execution', 'results'
        self.day_of_week = 0  # 0=Понедельник, 1=Вторник, ..., 6=Воскресенье
        self.weekdays = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']

        # Mental state
        self.energy = 100
        self.stress = 0
        self.paranoia = 0
        self.inner_voice_relationship = 0

        # Dream system
        self.dream_system = DreamSystem()
        self.current_dream = None
        self.show_dream_popup = False

        # Event series tracking
        self.event_series_progress = {
            'cats': 0,  # Прогресс серии о котиках
            'stalker': 0  # Прогресс серии о незнакомке
        }
        self.event_series_completed = set()  # Завершенные серии

        # Time management - переход на получасовые интервалы
        self.current_time = 8.0  # 8 AM start
        self.max_hours = 14  # 14 hours available per day
        self.timeline_start_hour = 6  # 6 AM
        self.timeline_end_hour = 23  # 11 PM
        self.time_precision = 0.5  # 30-minute intervals
        self.free_time_penalty = 0  # Track accumulated free time for stress penalty

        # 🖥️ КОНСОЛЬНОЕ ЛОГИРОВАНИЕ АКТИВИРОВАНО
        print("=" * 60)
        print("📊 КОНСОЛЬНОЕ ЛОГИРОВАНИЕ СТРЕССА АКТИВНО")
        print("ℹ️  Все изменения стресса будут отображаться в консоли")
        print("🔍 Источники: Активности, Свободное время, Статус-эффекты")
        print("=" * 60)

        # Activities
        self.available_activities = [
            {
                'name': 'Завтрак',
                'duration': 1,
                'location': 'home',
                'mandatory': True,
                'energy_recovery': 5,
                'stress_recovery': -5,
                'time_constraint': (7, 10),
                'icon': '🍳',
                'time_display': '7:00-10:00',
                'day_availability': None  # Доступно каждый день
            },
            {
                'name': 'Работа',
                'duration': 6,
                'location': 'office',
                'mandatory': True,
                'energy_recovery': -20,
                'stress_recovery': 20,
                'time_constraint': (8, 17),
                'icon': '💼',
                'time_display': '8:00-17:00',
                'day_availability': [0, 1, 2, 3, 4]  # Только в будние дни (Пн-Пт)
            },
            {
                'name': 'Ужин',
                'duration': 1,
                'location': 'home',
                'mandatory': True,
                'energy_recovery': 5,
                'stress_recovery': -5,
                'time_constraint': (17, 21),
                'icon': '🍽️',
                'time_display': '17:00-21:00',
                'day_availability': None  # Доступно каждый день
            },
            {
                'name': 'Подготовка ко сну',
                'duration': 1,
                'location': 'home',
                'mandatory': True,
                'energy_recovery': 5,
                'stress_recovery': -5,
                'time_constraint': (20, 23),
                'icon': '💤',
                'time_display': '20:00-23:00',
                'day_availability': None  # Доступно каждый день
            },
            {
                'name': 'Утренняя пробежка',
                'duration': 1,
                'location': 'outdoor',
                'mandatory': False,
                'energy_recovery': -5,
                'stress_recovery': -10,
                'time_constraint': (6, 11),
                'icon': '🏃',
                'time_display': '6:00-11:00',
                'day_availability': None  # Доступно каждый день
            },
            {
                'name': 'Покупки',
                'duration': 2,
                'location': 'store',
                'mandatory': False,
                'energy_recovery': -10,
                'stress_recovery': -10,
                'time_constraint': (8, 20),
                'icon': '🛒',
                'time_display': '8:00-20:00',
                'day_availability': [0, 1, 2, 3, 4, 5]  # Закрыто в воскресенье
            },
            {
                'name': 'Обед с друзьями',
                'duration': 1,
                'location': 'restaurant',
                'mandatory': False,
                'energy_recovery': 15,
                'stress_recovery': -10,
                'time_constraint': (11, 15),
                'icon': '👥',
                'time_display': '11:00-15:00',
                'day_availability': None  # Доступно каждый день
            },
            {
                'name': 'Спортзал',
                'duration': 1,
                'location': 'gym',
                'mandatory': False,
                'energy_recovery': -15,
                'stress_recovery': -15,
                'time_constraint': (6, 22),
                'icon': '💪',
                'time_display': '6:00-22:00',
                'day_availability': [0, 1, 2, 3, 4, 5]  # Закрыт в воскресенье
            },
            {
                'name': 'Кино',
                'duration': 2,
                'location': 'cinema',
                'mandatory': False,
                'energy_recovery': 20,
                'stress_recovery': -10,
                'time_constraint': (18, 22),
                'icon': '🎬',
                'time_display': '18:00-22:00',
                'day_availability': None  # Доступно каждый день
            },
            {
                'name': 'Вечерняя прогулка',
                'duration': 1,
                'location': 'outdoor',
                'mandatory': False,
                'energy_recovery': -5,
                'stress_recovery': -10,
                'time_constraint': (17, 21),
                'icon': '🚶',
                'time_display': '17:00-21:00',
                'day_availability': None  # Доступно каждый день
            },
            {
                'name': 'Уборка дома',
                'duration': 1,
                'location': 'home',
                'mandatory': False,
                'energy_recovery': -10,
                'stress_recovery': -5,
                'time_constraint': (9, 18),
                'icon': '🧹',
                'time_display': '9:00-18:00',
                'becomes_mandatory_after': 3,
                'activity_type': 'hygiene',
                'day_availability': None  # Доступно каждый день
            },
            {
                'name': 'Покупки продуктов',
                'duration': 1.5,
                'location': 'store',
                'mandatory': False,
                'energy_recovery': -10,
                'stress_recovery': 5,
                'time_constraint': (8, 20),
                'icon': '🛒',
                'time_display': '8:00-20:00',
                'becomes_mandatory_after': 4,
                'activity_type': 'supplies',
                'day_availability': None  # Доступно каждый день
            },
            {
                'name': 'Стирка белья',
                'duration': 0.5,
                'location': 'home',
                'mandatory': False,
                'energy_recovery': -5,
                'stress_recovery': -5,
                'time_constraint': (8, 22),
                'icon': '👕',
                'time_display': '8:00-22:00',
                'becomes_mandatory_after': 3,
                'activity_type': 'hygiene',
                'day_availability': None  # Доступно каждый день
            },
            {
                'name': 'Визит к врачу',
                'duration': 2,
                'location': 'clinic',
                'mandatory': False,
                'energy_recovery': -10,
                'stress_recovery': 10,
                'time_constraint': (9, 16),
                'icon': '👩‍⚕️',
                'time_display': '9:00-16:00',
                'becomes_mandatory_after': 7,
                'activity_type': 'health',
                'day_availability': [0, 1, 2, 3, 4]  # Только в будние дни
            },
            {
                'name': 'Чтение книг',
                'duration': 1.5,
                'location': 'home',
                'mandatory': False,
                'energy_recovery': 15,
                'stress_recovery': -10,
                'time_constraint': (10, 22),
                'icon': '📚',
                'time_display': '10:00-22:00',
                'day_availability': None  # Доступно каждый день
            },
            {
                'name': 'Прослушивание музыки',
                'duration': 1,
                'location': 'home',
                'mandatory': False,
                'energy_recovery': 10,
                'stress_recovery': -10,
                'time_constraint': (8, 23),
                'icon': '🎵',
                'time_display': '8:00-23:00',
                'day_availability': None  # Доступно каждый день
            }
        ]

        # Activity tracking system for mandatory enforcement
        self.last_activity_completion = {}  # Track when activities were last completed
        self.initialize_activity_tracking()

        # Activity adaptation system - tracks effectiveness degradation/recovery
        self.activity_adaptation = {}  # Track adaptation level for each activity
        self.initialize_activity_adaptation()

        # Timeline activities (placed on timeline)
        self.timeline_activities = []
        self.active_events = []
        self.daily_events = []  # События с назначенным временем

        # UI state
        self.selected_activity = -1
        self.scroll_offset = 0
        self.show_help = False
        self.show_cards_panel = False
        self.show_voice_panel = False
        self.show_event_popup = False
        self.show_voice_message_popup = False  # New: voice message popup
        self.current_event = None
        self.current_voice_message = None  # New: current voice message
        self.dragging_activity = None
        self.timeline_rect = pygame.Rect(20, 400, 1140, 180)  # Timeline area - значительно увеличена длина

        # Messages system
        self.messages = []
        self.message_timer = 0

        # Execution state
        self.current_activity_index = 0
        self.activity_results = []

        # Generate events for the day
        self.generate_random_events()

        # Cards and voice system
        self.card_points = 0 if self.day < 3 else 3  # Start with points only after voice system unlocks
        self.voice_history = []
        self.last_voice_interaction = None
        self.voice_tasks = []  # Current tasks from inner voice
        self.completed_voice_tasks = []
        self.voice_trust_level = 0  # Trust affects available tasks

        # Card effects
        self.luck_active = False
        self.protection_active = False
        self.focus_active = False
        self.time_card_active = False

        # Initialize full card deck
        self.all_cards = self.initialize_full_card_deck()
        self.player_deck = []  # Cards owned by player
        self.used_cards = []  # Cards used this day

        # Status effects system - ensure it's initialized and working
        self.status_effects = {}  # Dict of active status effects
        self.initialize_status_effects()  # Always initialize the system

        # Voice task system (only generate if voice system is unlocked)
        if self.day >= 3:
            self.generate_voice_tasks()

        # Voice interaction limitations
        self.daily_voice_interactions = 0  # Track voice interactions per day
        self.max_daily_voice_interactions = 3  # Maximum 3 interactions per day

        # Schedule save/load system
        self.saved_schedule = []  # Store saved timeline activities

        # Show voice message for the first day immediately when game starts
        if self.day == 1:
            voice_message = self.generate_voice_new_day_message(self.day)
            if voice_message:  # Only show if message exists
                self.current_voice_message = voice_message
                self.show_voice_message_popup = True

    def initialize_full_card_deck(self):
        """Initialize the complete deck of 36 cards"""
        return [
            # Базовые карты выживания (9 карт)
            {
                'id': 'energy_boost',
                'name': 'Энергетический напиток',
                'icon': '⚡',
                'description': 'Быстро восстанавливает энергию',
                'cost': 10,
                'rarity': 'common',
                'effect_type': 'immediate',
                'effect': {'energy': 25},
                'unlock_day': 1
            },
            {
                'id': 'stress_relief',
                'name': 'Дыхательные упражнения',
                'icon': '🧘',
                'description': 'Снижает текущий стресс',
                'cost': 10,
                'rarity': 'common',
                'effect_type': 'immediate',
                'effect': {'stress': -20},
                'unlock_day': 1
            },
            {
                'id': 'paranoia_calm',
                'name': 'Успокаивающие мысли',
                'icon': '💭',
                'description': 'Уменьшает паранойю',
                'cost': 10,
                'rarity': 'common',
                'effect_type': 'immediate',
                'effect': {'paranoia': -15},
                'unlock_day': 2
            },
            {
                'id': 'emergency_rest',
                'name': 'Экстренный отдых',
                'icon': '🛏️',
                'description': 'Полностью восстанавливает энергию',
                'cost': 28,
                'rarity': 'uncommon',
                'effect_type': 'immediate',
                'effect': {'energy': 100},
                'unlock_day': 3
            },
            {
                'id': 'meditation',
                'name': 'Глубокая медитация',
                'icon': '🕯️',
                'description': 'Значительно снижает стресс и паранойю',
                'cost': 21,
                'rarity': 'uncommon',
                'effect_type': 'immediate',
                'effect': {'stress': -30, 'paranoia': -20},
                'unlock_day': 4
            },
            {
                'id': 'coffee_break',
                'name': 'Кофе-пауза',
                'icon': '☕',
                'description': 'Небольшое восстановление энергии и снижение стресса',
                'cost': 12,
                'rarity': 'common',
                'effect_type': 'immediate',
                'effect': {'energy': 15, 'stress': -10},
                'unlock_day': 1
            },
            {
                'id': 'power_nap',
                'name': 'Короткий сон',
                'icon': '😴',
                'description': 'Восстанавливает энергию, требует 1 час свободного времени',
                'cost': 12,
                'rarity': 'common',
                'effect_type': 'time_dependent',
                'effect': {'energy': 35, 'time_cost': 1},
                'unlock_day': 2
            },
            {
                'id': 'healthy_snack',
                'name': 'Здоровый перекус',
                'icon': '🥗',
                'description': 'Постепенно восстанавливает энергию',
                'cost': 14,
                'rarity': 'common',
                'effect_type': 'immediate',
                'effect': {'energy': 20},
                'unlock_day': 1
            },
            {
                'id': 'panic_control',
                'name': 'Контроль паники',
                'icon': '🆘',
                'description': 'Экстренное снижение стресса',
                'cost': 20,
                'rarity': 'uncommon',
                'effect_type': 'immediate',
                'effect': {'stress': -40},
                'unlock_day': 3
            },

            # Защитные карты (9 карт)
            {
                'id': 'stress_shield',
                'name': 'Щит от стресса',
                'icon': '🛡️',
                'description': 'Блокирует стресс от следующего события',
                'cost': 13,
                'rarity': 'uncommon',
                'effect_type': 'next_event',
                'effect': {'block_stress': True},
                'unlock_day': 5
            },
            {
                'id': 'luck_charm',
                'name': 'Талисман удачи',
                'icon': '🍀',
                'description': 'Улучшает исходы событий на день',
                'cost': 13,
                'rarity': 'rare',
                'effect_type': 'day_buff',
                'effect': {'luck_bonus': 2},
                'unlock_day': 7
            },
            {
                'id': 'energy_shield',
                'name': 'Защита энергии',
                'icon': '⚡🛡️',
                'description': 'Снижает потерю энергии от активностей',
                'cost': 10,
                'rarity': 'uncommon',
                'effect_type': 'day_buff',
                'effect': {'energy_protection': 0.5},
                'unlock_day': 6
            },
            {
                'id': 'paranoia_ward',
                'name': 'Оберег от паранойи',
                'icon': '👁️‍🗨️',
                'description': 'Предотвращает рост паранойи',
                'cost': 20,
                'rarity': 'uncommon',
                'effect_type': 'day_buff',
                'effect': {'paranoia_immunity': True},
                'unlock_day': 4
            },
            {
                'id': 'confidence_boost',
                'name': 'Прилив уверенности',
                'icon': '💪',
                'description': 'Улучшает все действия на день',
                'cost': 15,
                'rarity': 'rare',
                'effect_type': 'day_buff',
                'effect': {'action_bonus': 1.5},
                'unlock_day': 8
            },
            {
                'id': 'social_armor',
                'name': 'Социальная броня',
                'icon': '👥🛡️',
                'description': 'Защищает от социальных событий',
                'cost': 8,
                'rarity': 'uncommon',
                'effect_type': 'category_protection',
                'effect': {'protect_social': True},
                'unlock_day': 6
            },
            {
                'id': 'tech_immunity',
                'name': 'Техно-иммунитет',
                'icon': '💻🛡️',
                'description': 'Защищает от технических проблем',
                'cost': 8,
                'rarity': 'uncommon',
                'effect_type': 'category_protection',
                'effect': {'protect_technical': True},
                'unlock_day': 5
            },
            {
                'id': 'weather_prep',
                'name': 'Погодная подготовка',
                'icon': '🌦️🛡️',
                'description': 'Защищает от погодных событий',
                'cost': 8,
                'rarity': 'common',
                'effect_type': 'category_protection',
                'effect': {'protect_weather': True},
                'unlock_day': 3
            },
            {
                'id': 'emergency_kit',
                'name': 'Аварийный набор',
                'icon': '🎒',
                'description': 'Защищает от любого одного события',
                'cost': 7,
                'rarity': 'rare',
                'effect_type': 'one_time_protection',
                'effect': {'universal_protection': True},
                'unlock_day': 9
            },

            # Карты усиления (9 карт)
            {
                'id': 'focus_enhancer',
                'name': 'Усилитель фокуса',
                'icon': '🎯',
                'description': 'Удваивает эффект следующей активности',
                'cost': 10,
                'rarity': 'uncommon',
                'effect_type': 'next_activity',
                'effect': {'activity_multiplier': 2},
                'unlock_day': 5
            },
            {
                'id': 'productivity_surge',
                'name': 'Всплеск продуктивности',
                'icon': '📈',
                'description': 'Улучшает все активности на день',
                'cost': 17,
                'rarity': 'rare',
                'effect_type': 'day_buff',
                'effect': {'productivity_bonus': 1.3},
                'unlock_day': 7
            },
            {
                'id': 'social_boost',
                'name': 'Социальный буст',
                'icon': '🗣️',
                'description': 'Улучшает социальные активности',
                'cost': 10,
                'rarity': 'uncommon',
                'effect_type': 'activity_type_bonus',
                'effect': {'social_bonus': 1.5},
                'unlock_day': 4
            },
            {
                'id': 'physical_boost',
                'name': 'Физический буст',
                'icon': '🏃',
                'description': 'Улучшает физические активности',
                'cost': 10,
                'rarity': 'uncommon',
                'effect_type': 'activity_type_bonus',
                'effect': {'physical_bonus': 1.5},
                'unlock_day': 4
            },
            {
                'id': 'mental_clarity',
                'name': 'Ясность ума',
                'icon': '🧠',
                'description': 'Улучшает умственные активности',
                'cost': 10,
                'rarity': 'uncommon',
                'effect_type': 'activity_type_bonus',
                'effect': {'mental_bonus': 1.5},
                'unlock_day': 5
            },
            {
                'id': 'time_efficiency',
                'name': 'Эффективность времени',
                'icon': '⏰',
                'description': 'Сокращает время активностей',
                'cost': 10,
                'rarity': 'rare',
                'effect_type': 'day_buff',
                'effect': {'time_efficiency': 0.8},
                'unlock_day': 8
            },
            {
                'id': 'energy_efficiency',
                'name': 'Энергоэффективность',
                'icon': '⚡💡',
                'description': 'Снижает энергозатраты активностей',
                'cost': 15,
                'rarity': 'uncommon',
                'effect_type': 'day_buff',
                'effect': {'energy_efficiency': 0.7},
                'unlock_day': 6
            },
            {
                'id': 'motivation_surge',
                'name': 'Прилив мотивации',
                'icon': '🔥',
                'description': 'Значительно улучшает одну активность',
                'cost': 10,
                'rarity': 'uncommon',
                'effect_type': 'target_activity',
                'effect': {'motivation_multiplier': 3},
                'unlock_day': 5
            },
            {
                'id': 'perfect_timing',
                'name': 'Идеальный тайминг',
                'icon': '⏱️',
                'description': 'Позволяет переместить любую активность',
                'cost': 0,
                'rarity': 'uncommon',
                'effect_type': 'time_manipulation',
                'effect': {'move_activity': True},
                'unlock_day': 6
            },

            # Специальные карты (9 карт)
            {
                'id': 'time_rewind',
                'name': 'Возврат времени',
                'icon': '⏪',
                'description': 'Отменяет последнее событие',
                'cost': 0,
                'rarity': 'legendary',
                'effect_type': 'event_manipulation',
                'effect': {'undo_last_event': True},
                'unlock_day': 12
            },
            {
                'id': 'future_sight',
                'name': 'Предвидение',
                'icon': '🔮',
                'description': 'Показывает следующие события',
                'cost': 0,
                'rarity': 'rare',
                'effect_type': 'information',
                'effect': {'reveal_events': 3},
                'unlock_day': 10
            },
            {
                'id': 'voice_harmony',
                'name': 'Гармония с голосом',
                'icon': '🎵',
                'description': 'Улучшает отношения с внутренним голосом',
                'cost': 13,
                'rarity': 'rare',
                'effect_type': 'voice_relationship',
                'effect': {'voice_bonus': 20},
                'unlock_day': 8
            },
            {
                'id': 'voice_silence',
                'name': 'Тишина в голове',
                'icon': '🔇',
                'description': 'Временно отключает внутренний голос',
                'cost': 10,
                'rarity': 'uncommon',
                'effect_type': 'voice_control',
                'effect': {'silence_voice': True},
                'unlock_day': 6
            },
            {
                'id': 'memory_boost',
                'name': 'Усиление памяти',
                'icon': '🧩',
                'description': 'Позволяет переиспользовать карту',
                'cost': 15,
                'rarity': 'rare',
                'effect_type': 'card_manipulation',
                'effect': {'recycle_card': True},
                'unlock_day': 11
            },
            {
                'id': 'deck_shuffle',
                'name': 'Перетасовка колоды',
                'icon': '🔀',
                'description': 'Получить 3 случайные карты',
                'cost': 30,
                'rarity': 'rare',
                'effect_type': 'card_generation',
                'effect': {'random_cards': 3},
                'unlock_day': 9
            },
            {
                'id': 'lucky_break',
                'name': 'Счастливый случай',
                'icon': '✨',
                'description': 'Случайный положительный эффект',
                'cost': 0,
                'rarity': 'uncommon',
                'effect_type': 'random_positive',
                'effect': {'random_bonus': True},
                'unlock_day': 7
            },
            {
                'id': 'chaos_control',
                'name': 'Контроль хаоса',
                'icon': '🌀',
                'description': 'Превращает следующее негативное событие в позитивное',
                'cost': 15,
                'rarity': 'rare',
                'effect_type': 'event_manipulation',
                'effect': {'reverse_event': True},
                'unlock_day': 7
            },
            {
                'id': 'cleanse_effects',
                'name': 'Очищение разума',
                'icon': '✨',
                'description': 'Удаляет все негативные статусы от событий',
                'cost': 20,
                'rarity': 'rare',
                'effect_type': 'cleanse_negative',
                'effect': {'cleanse_negative_effects': True},
                'unlock_day': 12
            },
            {
                'id': 'perfect_day',
                'name': 'Идеальный день',
                'icon': '👑',
                'description': 'Устраняет все негативные эффекты дня',
                'cost': 25,
                'rarity': 'legendary',
                'effect_type': 'day_perfection',
                'effect': {'perfect_day': True},
                'unlock_day': 15
            }
        ]

    def generate_voice_tasks(self):
        """Generate tasks from inner voice based on relationship level"""
        self.voice_tasks = []

        # Define task pools by difficulty/complexity level
        easy_tasks = [
            {
                'id': 'plan_exercise',
                'name': 'Движение - жизнь',
                'description': 'Добавь в план пробежку или спортзал',
                'reward': {'card_points': 3, 'voice_relationship': 4},
                'difficulty': 2,
                'check': lambda game: any(
                    'пробежка' in ta.activity['name'].lower() or 'спорт' in ta.activity['name'].lower() for ta in
                    game.timeline_activities)
            },
            {
                'id': 'social_activity',
                'name': 'Не закрывайся от мира',
                'description': 'Добавь встречу с друзьями или обед',
                'reward': {'card_points': 3, 'voice_relationship': 4},
                'difficulty': 2,
                'check': lambda game: any(
                    'друг' in ta.activity['name'].lower() or 'обед' in ta.activity['name'].lower() for ta in
                    game.timeline_activities)
            },
            {
                'id': 'maintain_energy',
                'name': 'Не истощай своё тело',
                'description': 'Закончи день с энергией более 30%',
                'reward': {'card_points': 3, 'voice_relationship': 5},
                'difficulty': 2,
                'check': lambda game: game.energy > 30
            },
            {
                'id': 'home_activities',
                'name': 'Проведи больше времени дома',
                'description': 'Запланируй минимум 3 домашние активности',
                'reward': {'card_points': 3, 'voice_relationship': 4},
                'difficulty': 2,
                'check': lambda game: len(
                    [ta for ta in game.timeline_activities if ta.activity.get('location') == 'home']) >= 3
            },
        ]

        medium_tasks = [
            {
                'id': 'avoid_stress',
                'name': 'Не истощай свой разум',
                'description': 'Закончи день со стрессом менее 50%',
                'reward': {'card_points': 4, 'voice_relationship': 7},
                'difficulty': 3,
                'check': lambda game: game.stress < 50
            },
            {
                'id': 'avoid_cinema',
                'name': 'Не смотри кино',
                'description': 'Не планируй поход в кино сегодня',
                'reward': {'card_points': 4, 'voice_relationship': 6},
                'difficulty': 3,
                'forbidden_activity': 'Кино',
                'check': lambda game, task=None: not any(
                    ta.activity['name'] == task.get('forbidden_activity', 'Кино')
                    for ta in game.timeline_activities
                ) if task else False
            },
            {
                'id': 'avoid_gym',
                'name': 'Не напрягайся в зале',
                'description': 'Не планируй тренировку в спортзале сегодня',
                'reward': {'card_points': 4, 'voice_relationship': 6},
                'difficulty': 3,
                'forbidden_activity': 'Спортзал',
                'check': lambda game, task=None: not any(
                    ta.activity['name'] == task.get('forbidden_activity', 'Спортзал')
                    for ta in game.timeline_activities
                ) if task else False
            },
            {
                'id': 'avoid_shopping',
                'name': 'Не ходи в магазин',
                'description': 'Не планируй походы по магазинам сегодня',
                'reward': {'card_points': 4, 'voice_relationship': 6},
                'difficulty': 3,
                'forbidden_activity': 'Покупки',
                'check': lambda game, task=None: not any(
                    ta.activity['name'] == task.get('forbidden_activity', 'Покупки')
                    for ta in game.timeline_activities
                ) if task else False
            },
            {
                'id': 'avoid_social_lunch',
                'name': 'Избегай ИХ',
                'description': 'Не планируй обеды с друзьями сегодня',
                'reward': {'card_points': 4, 'voice_relationship': 6},
                'difficulty': 3,
                'forbidden_activity': 'Обед с друзьями',
                'check': lambda game, task=None: not any(
                    ta.activity['name'] == task.get('forbidden_activity', 'Обед с друзьями')
                    for ta in game.timeline_activities
                ) if task else False
            },
            {
                'id': 'avoid_evening_walk',
                'name': 'Избегай вечерних прогулок',
                'description': 'Не планируй вечерние прогулки сегодня',
                'reward': {'card_points': 4, 'voice_relationship': 6},
                'difficulty': 3,
                'forbidden_activity': 'Вечерняя прогулка',
                'check': lambda game, task=None: not any(
                    ta.activity['name'] == task.get('forbidden_activity', 'Вечерняя прогулка')
                    for ta in game.timeline_activities
                ) if task else False
            },
            {
                'id': 'avoid_running',
                'name': 'Избегай пробежек',
                'description': 'Не планируй утренние пробежки сегодня',
                'reward': {'card_points': 4, 'voice_relationship': 6},
                'difficulty': 3,
                'forbidden_activity': 'Утренняя пробежка',
                'check': lambda game, task=None: not any(
                    ta.activity['name'] == task.get('required_activity', 'Утренняя пробежка')
                    for ta in game.timeline_activities
                ) if task else False
            },
            {
                'id': 'outdoor_time',
                'name': 'Проведи время на улице',
                'description': 'Запланируй минимум 2 уличные активности',
                'reward': {'card_points': 4, 'voice_relationship': 7},
                'difficulty': 3,
                'check': lambda game: len(
                    [ta for ta in game.timeline_activities if ta.activity.get('location') == 'outdoor']) >= 2
            },
        ]

        hard_tasks = [
            {
                'id': 'overcome_paranoia',
                'name': 'Не позволяй ИМ овладеть тобой',
                'description': 'Закончи день с паранойей менее 30%',
                'reward': {'card_points': 6, 'voice_relationship': 12},
                'difficulty': 4,
                'check': lambda game: game.paranoia < 30
            },
            {
                'id': 'energy_management',
                'name': 'Управляй энергией',
                'description': 'Закончи день с энергией 40-70%',
                'reward': {'card_points': 6, 'voice_relationship': 11},
                'difficulty': 4,
                'check': lambda game: 40 <= game.energy <= 70
            },
            {
                'id': 'stress_control',
                'name': 'Контролируй стресс',
                'description': 'Не превышай 60% стресса весь день',
                'reward': {'card_points': 6, 'voice_relationship': 13},
                'difficulty': 4,
                'check': lambda game: game.stress <= 60
            },
            {
                'id': 'perfect_planning',
                'name': 'Идеальное планирование',
                'description': 'Запланируй день без конфликтов времени',
                'reward': {'card_points': 3, 'voice_relationship': 14},
                'difficulty': 4,
                'check': lambda game: not any(ta.has_conflict for ta in game.timeline_activities)
            },
            {
                'id': 'specific_time_breakfast',
                'name': 'Точность - завтрак',
                'description': 'Запланируй завтрак на указанное время',
                'reward': {'card_points': 7, 'voice_relationship': 8},
                'difficulty': 3,
                'required_time': None,  # Will be set randomly
                'required_activity': 'Завтрак',
                'time_slots_required': None,  # Will be set based on activity
                'check': lambda game, task=None: any(
                    ta.activity['name'] == task.get('required_activity', 'Завтрак') and
                    ta.start_time == task.get('required_time', 8.0)
                    for ta in game.timeline_activities
                ) if task else False
            },
            {
                'id': 'specific_time_work',
                'name': 'Точность - работа',
                'description': 'Начни работу в указанное время',
                'reward': {'card_points': 7, 'voice_relationship': 10},
                'difficulty': 3,
                'required_time': None,  # Will be set randomly
                'required_activity': 'Работа',
                'time_slots_required': None,  # Will be set based on activity
                'check': lambda game, task=None: any(
                    ta.activity['name'] == task.get('required_activity', 'Работа') and
                    ta.start_time == task.get('required_time', 9.0)
                    for ta in game.timeline_activities
                ) if task else False
            },
            {
                'id': 'specific_time_dinner',
                'name': 'Точность - ужин',
                'description': 'Запланируй ужин на указанное время',
                'reward': {'card_points': 7, 'voice_relationship': 8},
                'difficulty': 3,
                'required_time': None,  # Will be set randomly
                'required_activity': 'Ужин',
                'time_slots_required': None,  # Will be set based on activity
                'check': lambda game, task=None: any(
                    ta.activity['name'] == task.get('required_activity', 'Ужин') and
                    ta.start_time == task.get('required_time', 18.0)
                    for ta in game.timeline_activities
                ) if task else False
            },
            {
                'id': 'specific_time_exercise',
                'name': 'Точность - пробежка',
                'description': 'Запланируй пробежку на указанное время',
                'reward': {'card_points': 7, 'voice_relationship': 7},
                'difficulty': 3,
                'required_time': None,  # Will be set randomly
                'required_activity': 'Утренняя пробежка',
                'time_slots_required': None,  # Will be set based on activity
                'check': lambda game, task=None: any(
                    ta.activity['name'] == task.get('required_activity', 'Утренняя пробежка') and
                    ta.start_time == task.get('required_time', 7.0)
                    for ta in game.timeline_activities
                ) if task else False
            },
        ]

        very_hard_tasks = [
            {
                'id': 'stress_master',
                'name': 'Будь спокоен',
                'description': 'Не превышай 40% стресса весь день',
                'reward': {'card_points': 9, 'voice_relationship': 18},
                'difficulty': 5,
                'check': lambda game: game.stress < 40
            },
            {
                'id': 'balanced_master',
                'name': 'Мастер баланса',
                'description': 'Все показатели в зелёной зоне',
                'reward': {'card_points': 7, 'voice_relationship': 22},
                'difficulty': 5,
                'check': lambda game: game.energy >= 70 and game.stress <= 30 and game.paranoia <= 30
            },
            {
                'id': 'exactly_7_activities',
                'name': 'Семь точно',
                'description': 'Запланируй точно 7 активностей',
                'reward': {'card_points': 8, 'voice_relationship': 12},
                'difficulty': 4,
                'check': lambda game: len(game.timeline_activities) == 7
            },
            {
                'id': 'exactly_9_activities',
                'name': 'Девять активностей',
                'description': 'Запланируй ровно 9 активностей',
                'reward': {'card_points': 8, 'voice_relationship': 16},
                'difficulty': 5,
                'check': lambda game: len(game.timeline_activities) == 9
            },
            {
                'id': 'twelve_different_activities',
                'name': 'Двенадцать разных дел',
                'description': 'Запланируй 12 разных активностей',
                'reward': {'card_points': 10, 'voice_relationship': 20},
                'difficulty': 5,
                'check': lambda game: len(set(ta.activity['name'] for ta in game.timeline_activities)) >= 12
            },
            {
                'id': 'perfectionist',
                'name': 'Перфекционист',
                'description': 'Идеальный день: энергия >80%, стресс <20%, нет конфликтов',
                'reward': {'card_points': 10, 'voice_relationship': 25},
                'difficulty': 5,
                'check': lambda game: (game.energy > 80 and game.stress < 20 and
                                       not any(ta.has_conflict for ta in game.timeline_activities))
            },
            {
                'id': 'zen_master',
                'name': 'Мастер дзен',
                'description': 'Закончи день с паранойей <10% и стрессом <25%',
                'reward': {'card_points': 10, 'voice_relationship': 20},
                'difficulty': 5,
                'check': lambda game: game.paranoia < 10 and game.stress < 25
            },
        ]

        # Select appropriate task pool based on relationship level
        relationship = self.inner_voice_relationship
        available_tasks = []

        if relationship < -50:
            # Очень плохие отношения - никаких заданий! Нужно сначала наладить отношения через диалог
            available_tasks = []
        elif relationship < -20:
            # Плохие отношения - только простые задания
            available_tasks = easy_tasks
        elif relationship < 0:
            # Нейтральные/слегка негативные - простые и средние
            available_tasks = easy_tasks + medium_tasks[:2]  # Только первые 2 средних
        elif relationship < 20:
            # Слегка позитивные - средние задания
            available_tasks = easy_tasks[-2:] + medium_tasks  # Последние 2 простых + все средние
        elif relationship < 50:
            # Хорошие отношения - средние и сложные
            available_tasks = medium_tasks + hard_tasks
        else:
            # Отличные отношения - сложные и очень сложные задания
            available_tasks = hard_tasks + very_hard_tasks

        # Select 2-3 tasks for the day, ensuring all are different and non-conflicting
        num_tasks = min(3, len(available_tasks))

        if num_tasks == 0:
            # If no tasks available (relationship < -50), don't generate any tasks
            # Player must improve relationship through dialogue first
            return

        selected_tasks = []
        reserved_time_slots = []  # Track reserved time slots to prevent conflicts

        # Create a copy of available tasks to avoid modifying the original
        available_copy = available_tasks.copy()

        # Helper function to check if two time ranges overlap
        def times_overlap(start1, end1, start2, end2):
            return not (end1 <= start2 or start1 >= end2)

        # Select tasks ensuring no duplicates and no time conflicts
        for _ in range(num_tasks):
            if not available_copy:
                break

            # Try to find a task that doesn't conflict with already selected tasks
            attempts = 0
            max_attempts = 10  # Prevent infinite loops

            while attempts < max_attempts and available_copy:
                chosen_task = random.choice(available_copy)
                task_copy = chosen_task.copy()
                task_copy['day_assigned'] = self.day

                # Check if this is a specific time task
                if task_copy['id'].startswith('specific_time_'):
                    activity_name = task_copy.get('required_activity', '')
                    # Find the activity to get its time constraints and duration
                    activity = None
                    for act in self.available_activities:
                        if act['name'] == activity_name:
                            activity = act
                            break

                    if activity and 'time_constraint' in activity:
                        constraint_start, constraint_end = activity['time_constraint']
                        activity_duration = activity['duration']

                        # Generate possible times within constraints (30-minute intervals)
                        possible_times = []
                        current_time = constraint_start
                        while current_time <= constraint_end - activity_duration:
                            possible_times.append(current_time)
                            current_time += 0.5

                        # Filter out times that conflict with already reserved slots
                        available_times = []
                        for possible_time in possible_times:
                            possible_end = possible_time + activity_duration

                            # Check if this time conflicts with any reserved slot
                            conflicts = False
                            for reserved_start, reserved_end in reserved_time_slots:
                                if times_overlap(possible_time, possible_end, reserved_start, reserved_end):
                                    conflicts = True
                                    break

                            if not conflicts:
                                available_times.append(possible_time)

                        if available_times:
                            # Choose a random available time
                            task_copy['required_time'] = random.choice(available_times)
                            task_copy['time_slots_required'] = [
                                (task_copy['required_time'], task_copy['required_time'] + activity_duration)]

                            # Update task description with specific time
                            time_str = f"{int(task_copy['required_time'])}:{int((task_copy['required_time'] % 1) * 60):02d}"
                            task_copy['description'] = task_copy['description'].replace('указанное время',
                                                                                        f'{time_str}')
                            task_copy['name'] = f"{task_copy['name']} в {time_str}"

                            # Reserve the time slots for this task
                            reserved_time_slots.extend(task_copy['time_slots_required'])

                            # Task is valid, add it
                            selected_tasks.append(task_copy)
                            available_copy = [task for task in available_copy if task['id'] != chosen_task['id']]
                            break
                        else:
                            # No available times for this task, remove it from options
                            available_copy = [task for task in available_copy if task['id'] != chosen_task['id']]
                    else:
                        # Activity not found or no time constraints, skip this task
                        available_copy = [task for task in available_copy if task['id'] != chosen_task['id']]
                else:
                    # Not a specific time task, no conflict possible
                    selected_tasks.append(task_copy)
                    available_copy = [task for task in available_copy if task['id'] != chosen_task['id']]
                    break

                attempts += 1

        # Ensure we clear existing tasks before adding new ones
        if not hasattr(self, 'voice_tasks'):
            self.voice_tasks = []

        # Add all successfully selected tasks
        for task in selected_tasks:
            self.voice_tasks.append(task)

    def generate_random_events(self):
        """Generate random events for the day"""
        self.active_events = []
        num_events = random.randint(0, 3)  # От 0 до 3 событий
        self.daily_events = []  # События с назначенным временем

        # Если событий нет, просто выходим
        if num_events == 0:
            return

        event_types = [
            # Негативные события - требуют выбора
            {
                'name': 'Сильный дождь', 'icon': '🌧️', 'type': 'choice', 'category': 'weather',
                'effects': {
                    'ignore': {'stress': 10, 'paranoia': 3, 'energy': 0},
                    'energy_solution': {'stress': 5, 'paranoia': 2, 'energy': -16},
                    'time_solution': {'stress': 3, 'paranoia': 2, 'energy': 5}
                }
            },
            {
                'name': 'Пробки', 'icon': '🚗', 'type': 'choice', 'category': 'transport',
                'effects': {
                    'ignore': {'stress': 8, 'paranoia': 2, 'energy': 0},
                    'energy_solution': {'stress': 4, 'paranoia': 1, 'energy': -20},
                    'time_solution': {'stress': 2, 'paranoia': 1, 'energy': -3}
                }
            },
            {
                'name': 'Отключение света', 'icon': '⚡', 'type': 'choice', 'category': 'infrastructure',
                'effects': {
                    'ignore': {'stress': 15, 'paranoia': 5, 'energy': 0},
                    'energy_solution': {'stress': 8, 'paranoia': 3, 'energy': -18},
                    'time_solution': {'stress': 6, 'paranoia': 3, 'energy': -8}
                }
            },
            {
                'name': 'Магазин закрыт', 'icon': '🏪', 'type': 'choice', 'category': 'service',
                'effects': {
                    'ignore': {'stress': 12, 'paranoia': 3, 'energy': 0},
                    'energy_solution': {'stress': 6, 'paranoia': 2, 'energy': -18},
                    'time_solution': {'stress': 4, 'paranoia': 2, 'energy': -6}
                }
            },
            {
                'name': 'Подозрительный человек', 'icon': '👁️', 'type': 'choice', 'category': 'social',
                'effects': {
                    'ignore': {'stress': 8, 'paranoia': 15, 'energy': 0},
                    'energy_solution': {'stress': 3, 'paranoia': 4, 'energy': -13},
                    'time_solution': {'stress': 3, 'paranoia': 5, 'energy': -5}
                }
            },
            {
                'name': 'Тревожные новости', 'icon': '📰', 'type': 'choice', 'category': 'information',
                'effects': {
                    'ignore': {'stress': 6, 'paranoia': 10, 'energy': 0},
                    'energy_solution': {'stress': 4, 'paranoia': 5, 'energy': -15},
                    'time_solution': {'stress': 2, 'paranoia': 3, 'energy': -3}
                }
            },
            {
                'name': 'Поломка техники', 'icon': '💻', 'type': 'choice', 'category': 'technical',
                'effects': {
                    'ignore': {'stress': 12, 'paranoia': 4, 'energy': 0},
                    'energy_solution': {'stress': 3, 'paranoia': 2, 'energy': -17},
                    'time_solution': {'stress': 4, 'paranoia': 2, 'energy': -6}
                }
            },

            # Позитивные события - только уведомления
            {
                'name': 'Отличная погода', 'icon': '☀️', 'type': 'notification', 'category': 'weather',
                'effects': {
                    'acknowledge': {'stress': -12, 'paranoia': -3, 'energy': 10}
                }
            },
            {
                'name': 'Неожиданная скидка', 'icon': '💰', 'type': 'notification', 'category': 'economic',
                'effects': {
                    'acknowledge': {'stress': -10, 'paranoia': -4, 'energy': -5}
                }
            },
            {
                'name': 'Хорошие новости', 'icon': '📺', 'type': 'notification', 'category': 'information',
                'effects': {
                    'acknowledge': {'stress': -10, 'paranoia': -5, 'energy': 8}
                }
            },
            {
                'name': 'Встреча со старым другом', 'icon': '👋', 'type': 'notification', 'category': 'social',
                'effects': {
                    'acknowledge': {'stress': -15, 'paranoia': -8, 'energy': -5}
                }
            },

            # Новые позитивные события с статусами
            {
                'name': 'Вдохновляющая книга', 'icon': '📚', 'type': 'notification', 'category': 'inspiration',
                'effects': {
                    'acknowledge': {'stress': -8, 'paranoia': -5, 'energy': -3, 'status': 'inspired'}
                }
            },
            {
                'name': 'Мотивирующий фильм', 'icon': '🎥', 'type': 'notification', 'category': 'inspiration',
                'effects': {
                    'acknowledge': {'stress': -10, 'paranoia': -3, 'energy': 5, 'status': 'inspired'}
                }
            },
            {
                'name': 'Успешная медитация', 'icon': '🧘', 'type': 'notification', 'category': 'wellness',
                'effects': {
                    'acknowledge': {'stress': -12, 'paranoia': -8, 'energy': -5, 'status': 'focused'}
                }
            },
            {
                'name': 'Похвала от коллеги', 'icon': '👏', 'type': 'notification', 'category': 'social',
                'effects': {
                    'acknowledge': {'stress': -10, 'paranoia': -5, 'energy': 8, 'status': 'confident'}
                }
            },
            {
                'name': 'Отличный сон', 'icon': '😴', 'type': 'notification', 'category': 'wellness',
                'effects': {
                    'acknowledge': {'stress': -15, 'paranoia': -5, 'energy': 20, 'status': 'energized'}
                }
            },
            {
                'name': 'Неожиданное признание', 'icon': '🏆', 'type': 'notification', 'category': 'achievement',
                'effects': {
                    'acknowledge': {'stress': -8, 'paranoia': -3, 'energy': 10, 'status': 'confident'}
                }
            },

            # Нейтральные события - простой выбор
            {
                'name': 'Звонок друга', 'icon': '📞', 'type': 'simple_choice', 'category': 'social',
                'effects': {
                    'accept': {'stress': -10, 'paranoia': -3, 'energy': -8},
                    'decline': {'stress': 0, 'paranoia': 0, 'energy': 0}
                }
            },
            {
                'name': 'Реклама мероприятия', 'icon': '🎪', 'type': 'simple_choice', 'category': 'entertainment',
                'effects': {
                    'accept': {'stress': -5, 'paranoia': -4, 'energy': -5},
                    'decline': {'stress': 0, 'paranoia': 0, 'energy': 0}
                }
            },

            # Новые паранойяльные события
            {
                'name': 'Странная тень', 'icon': '👥', 'type': 'choice', 'category': 'paranoia',
                'effects': {
                    'ignore': {'stress': 5, 'paranoia': 20, 'energy': 0},
                    'energy_solution': {'stress': 1, 'paranoia': 6, 'energy': -12},
                    'time_solution': {'stress': 2, 'paranoia': 5, 'energy': -5}
                }
            },
            {
                'name': 'Незнакомка следит', 'icon': '👁️‍🗨️', 'type': 'choice', 'category': 'paranoia',
                'effects': {
                    'ignore': {'stress': 12, 'paranoia': 25, 'energy': 0},
                    'energy_solution': {'stress': 5, 'paranoia': 4, 'energy': -22},
                    'time_solution': {'stress': 5, 'paranoia': 5, 'energy': -4}
                }
            },
            {
                'name': 'Предмет переставлен', 'icon': '📦', 'type': 'choice', 'category': 'paranoia',
                'effects': {
                    'ignore': {'stress': 8, 'paranoia': 18, 'energy': 0},
                    'energy_solution': {'stress': 2, 'paranoia': 3, 'energy': -15},
                    'time_solution': {'stress': 4, 'paranoia': 6, 'energy': -3}
                }
            },

            # Серия событий про котиков на улице
            {
                'name': 'Странный кот на улице', 'icon': '🐱', 'type': 'notification', 'category': 'cats',
                'series': 'cats', 'series_order': 1,
                'effects': {
                    'acknowledge': {'stress': 5, 'paranoia': -5, 'energy': 0}
                }
            },
            {
                'name': 'И снова черный кот', 'icon': '😻', 'type': 'simple_choice', 'category': 'cats',
                'series': 'cats', 'series_order': 2,
                'effects': {
                    'accept': {'stress': -10, 'paranoia': -5, 'energy': -5},
                    'decline': {'stress': 1, 'paranoia': 1, 'energy': 0}
                },
                'choices': {
                    'accept': 'Присесть и позвать котика',
                    'decline': 'Пройти мимо'
                }
            },
            {
                'name': 'Черный кот просит о помощи?', 'icon': '😸', 'type': 'simple_choice', 'category': 'cats',
                'series': 'cats', 'series_order': 3,
                'effects': {
                    'accept': {'stress': 10, 'paranoia': 15, 'energy': -25},
                    'decline': {'stress': 0, 'paranoia': 0, 'energy': 0}
                },
                'choices': {
                    'accept': 'Идти до конца',
                    'decline': 'Поспешить обратно'
                }
            },
            {
                'name': 'Голодный черный кот', 'icon': '😻❤️', 'type': 'simple_choice', 'category': 'cats',
                'series': 'cats', 'series_order': 4,
                'effects': {
                    'accept': {'stress': -10, 'paranoia': -5, 'energy': -25},
                    'decline': {'stress': 0, 'paranoia': 0, 'energy': 0}
                },
                'choices': {
                    'accept': 'Покормить котика',
                    'decline': 'Пройти мимо'
                }
            },

            # Серия событий про незнакомку
            {
                'name': 'Таинственная незнакомка', 'icon': '👩', 'type': 'notification', 'category': 'stalker',
                'series': 'stalker', 'series_order': 1,
                'description': 'Вас уже некоторое время не покидает чувство преследования... На протяжении 20 минут от вас не отстает ни на шаг один человек. '
                               'Странная незнакомая женщина в солцнезащитных очках и длинном черном плаще как будто преследует вас. '
                               'Через какое-то время вы терете её из виду, но странное чувство никуда не уходит...',
                'effects': {
                    'acknowledge': {'stress': 5, 'paranoia': 20, 'energy': 0}
                }
            },
            {
                'name': 'Странная записка', 'icon': '👀', 'type': 'notification', 'category': 'stalker',
                'series': 'stalker', 'series_order': 2,
                'description': 'Вы заходите в помещение и снимаете верхнюю одежду как вдруг замечаете выпашую записку. Она гласит: '
                               '"Совсем скоро нам нужно будет встретиться. Я сама тебя найду. Не бойся - я не причиню вреда, так что постарайся не убегать в этот раз." '
                               'Записка точно выпала именно из вашего кармана, но как она туда попала...',
                'effects': {
                    'acknowledge': {'stress': 10, 'paranoia': 15, 'energy': 0}
                }
            },
            {
                'name': 'Незнакомка прямо перед вами', 'icon': '👩', 'type': 'simple_choice', 'category': 'stalker',
                'series': 'stalker', 'series_order': 3,
                'description': 'Проходя очередное, ничем не примечательное здание, и заворачивая за угол, вы замечаете её - незнакому в очках и черном плаще. '
                               'В этот раз она оказалась прямо перед вами. Выйдя из оцепенения вы понимаете, что женщина никуда не уходит и ничего не говорит. '
                               'Вы все ещё можете вернуться за угол и убежать, но хотите ли вы этого?..',
                'effects': {
                    'accept': {'stress': 15, 'paranoia': 5, 'energy': 5},
                    'decline': {'stress': 5, 'paranoia': 15, 'energy': -10}
                },
                'choices': {
                    'accept': 'Заговорить',
                    'decline': 'Убежать'
                }
            },
            {
                'name': 'Ещё одна встреча', 'icon': '📝', 'type': 'notification', 'category': 'stalker',
                'series': 'stalker', 'series_order': 4,
                'description': 'В почтовом ящике вас ждет конверт без обратного адреса. Внутри - записка, написанная каллиграфическим почерком: "Я наблюдаю за тобой уже неделю. Ты очень интересная личность. Скоро мы встретимся лицом к лицу. Не бойся - я не причиню вреда. Просто хочу познакомиться." Подпись отсутствует.',
                'effects': {
                    'acknowledge': {'stress': 15, 'paranoia': 25, 'energy': -5}
                }
            }
        ]

        # Создаём события с назначенным временем от 7:00 до 20:00
        selected_events = []
        used_times = set()  # Чтобы избежать одинакового времени

        for i in range(num_events):
            # Проверяем возможность серийных событий
            series_event = self.get_next_series_event(event_types)

            if series_event:
                # Проверяем на дубликат серийного события
                if series_event['name'] not in [se['name'] for se in selected_events]:
                    event = series_event.copy()
                else:
                    # Серийное событие уже выбрано, отключаем
                    series_event = None

            if not series_event:
                # Избегаем дублирования типов событий в один день и исключаем серийные
                available_events = [
                    e for e in event_types
                    if e['name'] not in [se['name'] for se in selected_events]
                       and not e.get('series')  # Исключаем серийные события
                       # Дополнительно исключаем события завершенных серий
                       and not (e.get('series') == 'cats' and hasattr(self,
                                                                      'permanent_statuses') and 'cat_blessing' in getattr(
                        self, 'permanent_statuses', {}))
                       and not (e.get('series') in self.event_series_completed)
                ]
                if not available_events:
                    # Если нет обычных событий, возьмем любое
                    available_events = [e for e in event_types if not e.get('series')]
                    if not available_events:
                        available_events = event_types  # На крайний случай

                event = random.choice(available_events).copy()

            # Пропускаем итерацию, если не смогли выбрать событие
            if 'event' not in locals():
                continue

            # Назначаем случайное время только в ровные часы от 7:00 до 19:00
            # Доступные времена: 7:00, 8:00, 9:00, ... 19:00
            available_times = []
            for hour in range(7, 20):  # От 7 до 19 включительно
                if hour not in used_times:
                    available_times.append(hour)

            if available_times:
                event_time = random.choice(available_times)
                used_times.add(event_time)
            else:
                # Если все времена заняты, выбираем любой ровный час
                event_time = random.randint(7, 19)

            event['time'] = event_time
            event['triggered'] = False
            event['event_index'] = i
            selected_events.append(event)
            self.daily_events.append(event)

        # Сортируем события по времени
        self.daily_events.sort(key=lambda x: x['time'])

    def get_hour_x_position(self, hour):
        """Get X position for a given hour on the timeline"""
        hours_range = self.timeline_end_hour - self.timeline_start_hour
        hour_width = (self.timeline_rect.width - 40) / hours_range
        return self.timeline_rect.x + 20 + (hour - self.timeline_start_hour) * hour_width

    def get_hour_from_x_position(self, x):
        """Get hour from X position on timeline - snaps to half-hour grid based on mouse position"""
        hours_range = self.timeline_end_hour - self.timeline_start_hour
        hour_width = (self.timeline_rect.width - 40) / hours_range
        relative_x = x - (self.timeline_rect.x + 20)
        hour = self.timeline_start_hour + (relative_x / hour_width)

        # Snap to nearest half-hour based on which half of the hour cell the mouse is in
        base_hour = int(hour)
        fraction = hour - base_hour

        if fraction < 0.25:
            snapped_hour = base_hour
        elif fraction < 0.75:
            snapped_hour = base_hour + 0.5
        else:
            snapped_hour = base_hour + 1

        return max(self.timeline_start_hour, min(self.timeline_end_hour - 0.5, snapped_hour))

    def can_place_activity_at_time(self, activity, start_time):
        """Check if activity can be placed at given time"""
        end_time = start_time + activity['duration']

        # Check time constraints
        if 'time_constraint' in activity and activity['time_constraint']:
            constraint_start, constraint_end = activity['time_constraint']
            if start_time < constraint_start or end_time > constraint_end:
                return False

        # Check for duplicate mandatory activities
        if activity['mandatory']:
            for timeline_activity in self.timeline_activities:
                if timeline_activity.activity['name'] == activity['name']:
                    return False

        # Check conflicts with existing activities
        for timeline_activity in self.timeline_activities:
            existing_start = timeline_activity.start_time
            existing_end = timeline_activity.end_time

            # Check overlap
            if not (end_time <= existing_start or start_time >= existing_end):
                return False

        return True

    def place_activity_on_timeline(self, activity, start_time):
        """Place activity on timeline"""
        if not self.can_place_activity_at_time(activity, start_time):
            # Check specific reason for failure
            end_time = start_time + activity['duration']

            # Check for duplicate mandatory activity
            if activity['mandatory']:
                for timeline_activity in self.timeline_activities:
                    if timeline_activity.activity['name'] == activity['name']:
                        self.add_message(f"'{activity['name']}' уже запланирована на день!", 'danger')
                        return False

            # Check time constraints
            if 'time_constraint' in activity and activity['time_constraint']:
                constraint_start, constraint_end = activity['time_constraint']
                if start_time < constraint_start or end_time > constraint_end:
                    time_range = f"{int(constraint_start)}:00-{int(constraint_end)}:00"
                    self.add_message(f"'{activity['name']}' доступна только в {time_range}!", 'danger')
                    return False

            # Must be time conflict
            self.add_message("Конфликт времени с другой активностью!", 'danger')
            return False

        end_time = start_time + activity['duration']

        # Calculate position and size with precise alignment
        x = self.get_hour_x_position(start_time)
        width = self.get_hour_x_position(end_time) - x
        y = self.timeline_rect.y + 60
        height = 40

        # Create timeline activity with increased height for better text visibility
        height = 50  # Увеличена с 40 до 50 для лучшего отображения текста
        timeline_activity = TimelineActivity(activity, start_time, end_time, x, y, width, height)
        self.timeline_activities.append(timeline_activity)

        # Use proper time formatting for the message
        start_str = self.format_time_display(start_time)
        end_str = self.format_time_display(end_time)
        self.add_message(f"Добавлено: {activity['name']} ({start_str}-{end_str})", 'success')
        return True

    def remove_timeline_activity(self, timeline_activity):
        """Remove activity from timeline"""
        if timeline_activity in self.timeline_activities:
            self.timeline_activities.remove(timeline_activity)
            self.add_message(f"Удалено: {timeline_activity.activity['name']}", 'warning')

    def get_timeline_activity_at_position(self, x, y):
        """Get timeline activity at mouse position"""
        for timeline_activity in self.timeline_activities:
            if timeline_activity.rect.collidepoint(x, y):
                return timeline_activity
        return None

    def update_timeline_conflicts(self):
        """Update conflict status for all timeline activities"""
        for activity in self.timeline_activities:
            activity.has_conflict = False

        for i, activity1 in enumerate(self.timeline_activities):
            for j, activity2 in enumerate(self.timeline_activities[i + 1:], i + 1):
                # Check overlap
                if not (activity1.end_time <= activity2.start_time or
                        activity1.start_time >= activity2.end_time):
                    activity1.has_conflict = True
                    activity2.has_conflict = True

    def add_message(self, text, msg_type='info'):
        """Add a message to display"""
        self.messages.append({
            'text': text,
            'type': msg_type,
            'time': time.time()
        })

    def update_messages(self):
        """Update message system"""
        current_time = time.time()
        self.messages = [msg for msg in self.messages if current_time - msg['time'] < 3.0]

    def get_mental_state_color(self, value, is_energy=False):
        """Get color based on mental state value"""
        if is_energy:
            if value >= 70:
                return COLORS['success']
            elif value >= 40:
                return COLORS['warning']
            else:
                return COLORS['danger']
        else:  # Stress/Paranoia
            if value <= 30:
                return COLORS['success']
            elif value <= 60:
                return COLORS['warning']
            else:
                return COLORS['danger']

    def get_planned_schedule(self):
        """Get sorted list of timeline activities"""
        return sorted(self.timeline_activities, key=lambda x: x.start_time)

    def is_activity_available_today(self, activity):
        """Check if activity is available on current day of week"""
        day_availability = activity.get('day_availability')
        if day_availability is None:
            return True  # Available every day
        return self.day_of_week in day_availability

    def get_available_activities_today(self):
        """Get list of activities available today"""
        return [activity for activity in self.available_activities
                if self.is_activity_available_today(activity)]

    def get_unavailable_reason(self, activity):
        """Get reason why activity is unavailable"""
        if not self.is_activity_available_today(activity):
            current_day_name = self.weekdays[self.day_of_week]
            if activity.get('day_availability'):
                available_days = [self.weekdays[day] for day in activity['day_availability']]
                if len(available_days) <= 2:
                    return f"Недоступно в {current_day_name} (доступно: {', '.join(available_days)})"
                else:
                    return f"Недоступно в {current_day_name}"
            return f"Недоступно в {current_day_name}"
        return None

    def initialize_status_effects(self):
        """Initialize the status effects system"""
        self.status_effects = {}

    def add_status_effect(self, status_id, name, icon, description, duration_hours, condition_check=None, effects=None):
        """Add a status effect"""
        self.status_effects[status_id] = {
            'name': name,
            'icon': icon,
            'description': description,
            'duration_hours': duration_hours,
            'remaining_time': duration_hours,
            'condition_check': condition_check,
            'effects': effects or {},
            'start_time': getattr(self, 'current_time', 8.0)
        }

    def remove_status_effect(self, status_id):
        """Remove a status effect"""
        if status_id in self.status_effects:
            status_name = self.status_effects[status_id]['name']
            del self.status_effects[status_id]
            self.add_message(f"Статус '{status_name}' закончился", 'info')

    def get_next_series_event(self, event_types):
        """Get the next event in an active series"""
        # ВАЖНО: Не генерируем события из завершенных серий

        # Собираем все возможные серийные события
        available_series_events = []

        # Проверяем продолжение серии котиков
        if (self.event_series_progress['cats'] > 0 and
                'cats' not in self.event_series_completed and
                (not hasattr(self, 'permanent_statuses') or 'cat_blessing' not in getattr(self, 'permanent_statuses',
                                                                                          {}))):
            next_order = self.event_series_progress['cats'] + 1
            for event in event_types:
                if (event.get('series') == 'cats' and
                        event.get('series_order') == next_order):
                    available_series_events.append(event)
                    break  # Одно событие на серию

        # Проверяем продолжение серии про незнакомку
        if self.event_series_progress['stalker'] > 0 and 'stalker' not in self.event_series_completed:
            next_order = self.event_series_progress['stalker'] + 1
            for event in event_types:
                if (event.get('series') == 'stalker' and
                        event.get('series_order') == next_order):
                    available_series_events.append(event)
                    break  # Одно событие на серию

        # Если есть продолжение серий, возвращаем одно случайно
        if available_series_events:
            return random.choice(available_series_events)

        # Проверяем возможность начала новой серии (3% шанс)
        if random.random() < 0.03:
            new_series_events = []
            for event in event_types:
                series = event.get('series')
                if (series and event.get('series_order') == 1 and
                        self.event_series_progress.get(series, 0) == 0 and
                        series not in self.event_series_completed):
                    # Дополнительная проверка для серии котиков
                    if (series == 'cats' and
                            hasattr(self, 'permanent_statuses') and
                            'cat_blessing' in self.permanent_statuses):
                        continue
                    new_series_events.append(event)

            # Возвращаем случайно выбранное новое событие серии
            if new_series_events:
                return random.choice(new_series_events)

        return None

    def update_status_effects(self):
        """Update all active status effects"""
        current_time = getattr(self, 'current_time', 8.0)

        # Check for new status effects based on current state
        self.check_new_status_effects()

        # Update existing status effects
        effects_to_remove = []

        for status_id, status in self.status_effects.items():
            # Calculate time passed since start
            time_passed = current_time - status['start_time']
            remaining = status['duration_hours'] - time_passed

            # Apply hourly effects for paranoia statuses
            effects = status.get('effects', {})
            if 'hourly_stress' in effects or 'hourly_paranoia' in effects:
                # Check if a full hour has passed since last application
                if not hasattr(status, 'last_hourly_application'):
                    status['last_hourly_application'] = status['start_time']

                hours_since_last = current_time - status['last_hourly_application']
                if hours_since_last >= 1.0:  # At least 1 hour passed
                    if 'hourly_stress' in effects:
                        stress_increase = effects['hourly_stress']
                        old_stress = self.stress
                        self.stress = min(100, self.stress + stress_increase)

                        # 🚨 ОТЛАДКА: Логируем в глобальный счётчик
                        if not hasattr(self, 'stress_change_log'):
                            self.stress_change_log = []

                        import time
                        timestamp = time.time()
                        self.stress_change_log.append({
                            'time': current_time,
                            'source': f'status_{status["name"]}_hourly',
                            'change': stress_increase,
                            'before': old_stress,
                            'after': self.stress,
                            'timestamp': timestamp
                        })

                        # 🖥️ КОНСОЛЬНЫЙ ВЫВОД: Почасовой стресс от статусов
                        print(
                            f"📊 СТРЕСС ОТ СТАТУСА '{status['name']}': {old_stress}→{self.stress} (+{stress_increase})")

                        # 🚨 ОТЛАДКА: Детально логируем почасовые эффекты
                        self.add_message(
                            f"📱 {status['name']}: почасовой стресс {old_stress}→{self.stress} (+{stress_increase})",
                            'warning'
                        )

                    if 'hourly_paranoia' in effects:
                        paranoia_increase = effects['hourly_paranoia']
                        old_paranoia = self.paranoia
                        self.paranoia = min(100, self.paranoia + paranoia_increase)
                        # 🚨 ОТЛАДКА: Детально логируем почасовые эффекты
                        self.add_message(
                            f"📱 {status['name']}: почасовая паранойя {old_paranoia}→{self.paranoia} (+{paranoia_increase})",
                            'warning'
                        )

                    # Update last application time
                    status['last_hourly_application'] = current_time

                    # Show message about hourly effect
                    if 'hourly_stress' not in effects and 'hourly_paranoia' not in effects:
                        self.add_message(f"📱 {status['name']}: почасовой эффект активирован", 'warning')

            if remaining <= 0:
                # Status expired by time
                effects_to_remove.append(status_id)
            elif status['condition_check']:
                # Check if condition still applies
                if not status['condition_check'](self):
                    effects_to_remove.append(status_id)
                # Note: Removed automatic timer reset to prevent unwanted status extension

        # Remove expired effects
        for status_id in effects_to_remove:
            self.remove_status_effect(status_id)

    def check_new_status_effects(self):
        """Check and apply new status effects based on current state"""

        # Clear expired status effects based on conditions
        effects_to_remove = []
        for status_id, status in self.status_effects.items():
            if status['condition_check'] and not status['condition_check'](self):
                effects_to_remove.append(status_id)

        for status_id in effects_to_remove:
            self.remove_status_effect(status_id)

        # Истощение (низкая энергия)
        if self.energy < 30 and 'exhaustion' not in self.status_effects:
            self.add_status_effect(
                'exhaustion', 'Истощение', '😴',
                'Весь получаемый стресс увеличен на 50%',
                3.0,
                lambda game: game.energy < 30,
                {'stress_multiplier': 1.5}
            )
            self.add_message("Получен статус: Истощение", 'warning')

        # Перенапряжение (высокий стресс)
        elif self.stress > 70 and 'overstress' not in self.status_effects:
            self.add_status_effect(
                'overstress', 'Перенапряжение', '😰',
                'Энергия восстанавливается на 50% медленнее',
                2.5,
                lambda game: game.stress > 70,
                {'energy_recovery_multiplier': 0.5}
            )
            self.add_message("Получен статус: Перенапряжение", 'warning')

        # Паранойя (высокая паранойя)
        elif self.paranoia > 60 and 'paranoid_episode' not in self.status_effects:
            self.add_status_effect(
                'paranoid_episode', 'Приступ паранойи', '👁️',
                'Все негативные события наносят +25% стресса и паранойи',
                4.0,
                lambda game: game.paranoia > 60,
                {'negative_event_multiplier': 1.25}
            )
            self.add_message("Получен статус: Приступ паранойи", 'danger')

        # Прилив сил (высокая энергия и низкий стресс)
        elif (self.energy > 80 and self.stress < 20 and
              'energized' not in self.status_effects):
            self.add_status_effect(
                'energized', 'Прилив сил', '⚡',
                'Все активности требуют на 20% меньше энергии',
                2.0,
                lambda game: game.energy > 75 and game.stress < 30,
                {'energy_cost_multiplier': 0.8}
            )
            self.add_message("Получен статус: Прилив сил", 'success')

        # Спокойствие (низкий стресс и паранойя)
        elif (self.stress < 30 and self.paranoia < 30 and
              'calm' not in self.status_effects):
            self.add_status_effect(
                'calm', 'Спокойствие', '😌',
                'Стресс от событий снижен на 30%',
                3.0,
                lambda game: game.stress < 30 and game.paranoia < 30,
                {'stress_reduction': 0.3}
            )
            self.add_message("Получен статус: Спокойствие", 'success')

        # Фокус (средние показатели всех параметров)
        elif (40 <= self.energy <= 70 and 30 <= self.stress <= 50 and
              0 <= self.paranoia <= 40 and 'focused' not in self.status_effects):
            self.add_status_effect(
                'focused', 'Сосредоточенность', '🎯',
                'Активности дают на 15% больше положительных эффектов',
                1.5,
                lambda game: (35 <= game.energy <= 75 and 25 <= game.stress <= 55 and
                              0 <= game.paranoia <= 45),
                {'positive_effects_multiplier': 1.15}
            )
            self.add_message("Получен статус: Сосредоточенность", 'success')

        # Критическое состояние (очень плохие показатели)
        elif (self.energy < 25 and self.stress > 75 and
              'critical' not in self.status_effects):
            self.add_status_effect(
                'critical', 'Критическое состояние', '💀',
                'Все негативные эффекты усилены в 2 раза',
                1.0,
                lambda game: game.energy < 25 and game.stress > 75,
                {'all_negative_multiplier': 2.0}
            )
            self.add_message("Получен статус: Критическое состояние", 'danger')

        # Дополнительные комбинированные статусы
        # Выгорание (высокий стресс + низкая энергия)
        elif (self.energy < 40 and self.stress > 60 and
              'burnout' not in self.status_effects):
            self.add_status_effect(
                'burnout', 'Выгорание', '🔥',
                'Все активности требуют больше энергии и вызывают стресс',
                2.0,
                lambda game: game.energy < 45 and game.stress > 55,
                {'energy_cost_multiplier': 1.3, 'stress_from_activities': 5}
            )
            self.add_message("Получен статус: Выгорание", 'danger')

        # Тревожность (средний стресс + паранойя)
        elif (self.stress > 50 and self.paranoia > 40 and
              'anxiety' not in self.status_effects):
            self.add_status_effect(
                'anxiety', 'Тревожность', '😨',
                'Социальные активности вызывают дополнительный стресс',
                3.5,
                lambda game: game.stress > 45 and game.paranoia > 35,
                {'social_stress_multiplier': 1.4}
            )
            self.add_message("Получен статус: Тревожность", 'warning')

    def apply_status_effects_to_value(self, effect_type, base_value, is_negative=False):
        """Apply status effects to a value"""
        modified_value = base_value

        for status_id, status in self.status_effects.items():
            effects = status.get('effects', {})

            if effect_type == 'stress' and is_negative:
                if 'stress_multiplier' in effects:
                    modified_value *= effects['stress_multiplier']
                if 'stress_reduction' in effects and base_value > 0:
                    modified_value *= (1 - effects['stress_reduction'])
                if 'negative_event_multiplier' in effects:
                    modified_value *= effects['negative_event_multiplier']
                if 'all_negative_multiplier' in effects:
                    modified_value *= effects['all_negative_multiplier']

            elif effect_type == 'energy_recovery' and base_value > 0:
                if 'energy_recovery_multiplier' in effects:
                    modified_value *= effects['energy_recovery_multiplier']
                if 'positive_effects_multiplier' in effects:
                    modified_value *= effects['positive_effects_multiplier']

            elif effect_type == 'energy_cost' and base_value > 0:
                if 'energy_cost_multiplier' in effects:
                    modified_value *= effects['energy_cost_multiplier']

            elif effect_type == 'paranoia' and is_negative:
                # New: paranoia vulnerability multiplier
                if 'paranoia_vulnerability' in effects:
                    modified_value *= effects['paranoia_vulnerability']
                if 'negative_event_multiplier' in effects:
                    modified_value *= effects['negative_event_multiplier']
                if 'all_negative_multiplier' in effects:
                    modified_value *= effects['all_negative_multiplier']

        return modified_value

    def get_status_effects_summary(self):
        """Get summary of active status effects for display"""
        summary = []
        current_time = getattr(self, 'current_time', 8.0)

        for status in self.status_effects.values():
            remaining_time = max(0, status['duration_hours'] - (current_time - status['start_time']))

            summary.append({
                'name': status['name'],
                'icon': status['icon'],
                'description': status['description'],
                'remaining_time': remaining_time,
                'effects': status.get('effects', {}),
                'severity': self.get_status_severity(status)
            })

        # Sort by severity (most severe first) then by remaining time
        summary.sort(key=lambda x: (-x['severity'], x['remaining_time']))
        return summary

    def get_status_severity(self, status):
        """Get numerical severity of a status effect for sorting"""
        status_name = status['name'].lower()
        if 'критическое' in status_name:
            return 5
        elif any(word in status_name for word in ['выгорание', 'паранойя']):
            return 4
        elif any(word in status_name for word in ['истощение', 'перенапряжение', 'тревожность']):
            return 3
        elif any(word in status_name for word in ['прилив', 'спокойствие']):
            return 1
        else:
            return 2

    def format_time_display(self, time_value):
        """Format time value for display (e.g., 8.5 -> 8:30)"""
        hours = int(time_value)
        minutes = int((time_value % 1) * 60)
        return f"{hours}:{minutes:02d}"

    def initialize_activity_tracking(self):
        """Initialize activity tracking system"""
        # Ensure the tracking dict exists
        if not hasattr(self, 'last_activity_completion'):
            self.last_activity_completion = {}

        # Initialize last completion tracking for trackable activities
        for activity in self.available_activities:
            if activity.get('becomes_mandatory_after'):
                activity_name = activity['name']
                if activity_name not in self.last_activity_completion:
                    # Set initial completion to current day so activities don't immediately become mandatory
                    # This gives players a grace period from the start
                    self.last_activity_completion[activity_name] = self.day

    def initialize_activity_adaptation(self):
        """Initialize activity adaptation tracking system"""
        if not hasattr(self, 'activity_adaptation'):
            self.activity_adaptation = {}

        # Основные активности, к которым нельзя привыкнуть
        basic_activities = ['Завтрак', 'Ужин', 'Подготовка ко сну']

        # Initialize adaptation tracking for activities with stress recovery
        for activity in self.available_activities:
            activity_name = activity['name']
            # Исключаем основные активности из системы адаптации
            if (activity.get('stress_recovery', 0) < 0 and  # Negative stress recovery = stress reduction
                    activity_name not in basic_activities):  # Но не основные активности
                if activity_name not in self.activity_adaptation:
                    self.activity_adaptation[activity_name] = {
                        'effectiveness': 1.0,  # 1.0 = full effectiveness, 0.5 = minimum effectiveness
                        'last_used': 0,  # Day when last used
                        'consecutive_uses': 0,  # Count of consecutive uses
                        'original_stress_recovery': activity['stress_recovery']  # Store original value
                    }

    def get_adapted_stress_recovery(self, activity):
        """Get stress recovery value adapted for usage frequency"""
        activity_name = activity['name']
        original_recovery = activity.get('stress_recovery', 0)

        # Only apply adaptation to positive activities (stress reduction)
        if original_recovery >= 0:
            return original_recovery

        # Адаптация работает только с 8-го дня
        if self.day < 8:
            return original_recovery

        # Основные активности не подвержены адаптации
        basic_activities = ['Завтрак', 'Ужин', 'Подготовка ко сну']
        if activity_name in basic_activities:
            return original_recovery

        # Ensure adaptation tracking exists for this activity
        if activity_name not in self.activity_adaptation:
            self.activity_adaptation[activity_name] = {
                'effectiveness': 1.0,
                'last_used': 0,
                'consecutive_uses': 0,
                'original_stress_recovery': original_recovery
            }

        adaptation_data = self.activity_adaptation[activity_name]
        effectiveness = adaptation_data['effectiveness']

        # Apply effectiveness multiplier to stress recovery
        # Since stress_recovery is negative (e.g., -10), we multiply by effectiveness
        # At 1.0 effectiveness: -10 * 1.0 = -10 (full effect)
        # At 0.5 effectiveness: -10 * 0.5 = -5 (half effect)
        adapted_recovery = int(original_recovery * effectiveness)

        return adapted_recovery

    def update_activity_adaptation(self, used_activity_names):
        """Update adaptation levels based on which activities were used today"""
        # Адаптация работает только с 8-го дня
        if self.day < 8:
            return

        # Основные активности не подвержены адаптации
        basic_activities = ['Завтрак', 'Ужин', 'Подготовка ко сну']

        # Определяем минимальную эффективность в зависимости от дня
        if self.day < 15:
            min_effectiveness = 0.5  # 50% с 8 по 14 день
        else:
            min_effectiveness = 0.2  # 20% с 15 дня

        for activity in self.available_activities:
            activity_name = activity['name']

            # Only track positive stress recovery activities, excluding basic ones
            if (activity.get('stress_recovery', 0) >= 0 or
                    activity_name in basic_activities):
                continue

            # Ensure adaptation data exists
            if activity_name not in self.activity_adaptation:
                self.activity_adaptation[activity_name] = {
                    'effectiveness': 1.0,
                    'last_used': 0,
                    'consecutive_uses': 0,
                    'original_stress_recovery': activity['stress_recovery']
                }

            adaptation_data = self.activity_adaptation[activity_name]

            if activity_name in used_activity_names:
                # Activity was used today - decrease effectiveness
                adaptation_data['last_used'] = self.day
                adaptation_data['consecutive_uses'] += 1

                # Decrease effectiveness based on consecutive uses
                # Each use reduces effectiveness by 15%, minimum depends on day
                reduction = min(0.15 * adaptation_data['consecutive_uses'], 1.0 - min_effectiveness)
                adaptation_data['effectiveness'] = max(min_effectiveness, 1.0 - reduction)

            else:
                # Activity was not used today - recover effectiveness
                if adaptation_data['last_used'] < self.day:
                    # Reset consecutive uses counter
                    adaptation_data['consecutive_uses'] = 0

                    # Increase effectiveness by 20% each day not used, up to 100%
                    adaptation_data['effectiveness'] = min(1.0, adaptation_data['effectiveness'] + 0.2)

    def get_adaptation_status_text(self, activity):
        """Get text describing adaptation status for an activity"""
        activity_name = activity['name']

        # Only show for positive stress recovery activities
        if activity.get('stress_recovery', 0) >= 0:
            return ""

        # Адаптация работает только с 8-го дня
        if self.day < 8:
            return ""

        # Основные активности не показывают статус адаптации
        basic_activities = ['Завтрак', 'Ужин', 'Подготовка ко сну']
        if activity_name in basic_activities:
            return ""

        if activity_name not in self.activity_adaptation:
            return ""

        adaptation_data = self.activity_adaptation[activity_name]
        effectiveness = adaptation_data['effectiveness']

        if effectiveness >= 0.95:
            return ""  # No status at full effectiveness
        else:
            # Show effectiveness percentage
            percentage = int(effectiveness * 100)
            return f" ({percentage}%)"

    def update_mandatory_activities(self):
        """Update mandatory status based on time since last completion"""
        mandatory_made = []

        for activity in self.available_activities:
            becomes_mandatory_after = activity.get('becomes_mandatory_after')
            if becomes_mandatory_after:
                activity_name = activity['name']
                last_completion = self.last_activity_completion.get(activity_name, 0)

                days_since_completion = self.day - last_completion

                # Check if should become mandatory
                if days_since_completion >= becomes_mandatory_after:
                    if not activity['mandatory']:
                        activity['mandatory'] = True
                        mandatory_made.append(activity_name)

        # Notify about newly mandatory activities
        if mandatory_made:
            for activity_name in mandatory_made:
                if len(mandatory_made) == 1:
                    self.add_message(f"⚠️ {activity_name} теперь обязательна! Давно не выполнялась.", 'warning')
                else:
                    # Just add one message for multiple activities
                    if activity_name == mandatory_made[0]:  # Only for first activity
                        activities_text = ", ".join(mandatory_made)
                        self.add_message(f"⚠️ Обязательны: {activities_text} (давно не выполнялись)", 'warning')

    def record_activity_completion(self, activity_name):
        """Record that an activity was completed today"""
        # Reset mandatory status when completed and update last completion time
        for activity in self.available_activities:
            if activity['name'] == activity_name and activity.get('becomes_mandatory_after'):
                # Record completion time FIRST (this resets the countdown)
                self.last_activity_completion[activity_name] = self.day

                # If activity was mandatory, reset it to optional
                if activity.get('mandatory', False):
                    activity['mandatory'] = False  # Reset to optional
                    self.add_message(f"✅ {activity_name} больше не обязательна (счётчик сброшен)", 'success')
                else:
                    # Even if not mandatory, show that countdown was reset
                    self.add_message(f"✅ {activity_name} выполнена (счётчик дней до обязательности сброшен)", 'info')
                break

    def generate_voice_end_day_message(self):
        """Generate end-of-day message from inner voice based on performance"""
        # Analyze player's performance
        stress = self.stress
        energy = self.energy
        paranoia = self.paranoia
        relationship = self.inner_voice_relationship
        completed_activities = len(self.activity_results)
        planned_activities = len(self.timeline_activities)

        # Calculate performance score
        performance_score = 0

        # Energy management
        if energy > 70:
            performance_score += 2
        elif energy > 40:
            performance_score += 1
        elif energy < 20:
            performance_score -= 2

        # Stress management
        if stress < 30:
            performance_score += 2
        elif stress < 60:
            performance_score += 1
        elif stress > 80:
            performance_score -= 2

        # Paranoia control
        if paranoia < 20:
            performance_score += 1
        elif paranoia > 60:
            performance_score -= 2

        # Activity completion
        completion_rate = completed_activities / max(1, planned_activities)
        if completion_rate >= 0.9:
            performance_score += 2
        elif completion_rate >= 0.7:
            performance_score += 1
        elif completion_rate < 0.5:
            performance_score -= 1

        # Generate message based on performance and relationship
        if performance_score >= 5:
            if relationship >= 20:
                message = "Превосходно! Ты действительно слушаешь мои советы и умело управляешь своим днём. Я горжусь тобой, продолжай в том же духе!"
                tone = "impressed"
            else:
                message = "Хм, неплохо справился... Может быть, я недооценивал тебя. Хотя не думай, что это что-то меняет между нами."
                tone = "grudging_respect"
        elif performance_score >= 2:
            if relationship >= 0:
                message = "Неплохой день, хотя есть над чем поработать. Обрати внимание на управление стрессом и энергией."
                tone = "encouraging"
            else:
                message = "Ну что ж, хотя бы не полный провал. Хотя я предупреждал тебя о некоторых вещах, которые ты проигнорировал."
                tone = "neutral_critical"
        elif performance_score >= 0:
            if relationship >= 10:
                message = "Этот день мог быть лучше, но ничего страшного. Главное - учиться на ошибках и двигаться дальше."
                tone = "supportive"
            else:
                message = "Средненько. Ты мог бы справиться лучше, если бы больше прислушивался к разуму."
                tone = "disappointed"
        else:
            if relationship < -20:
                message = "Катастрофа! Я же говорил тебе, что так делать нельзя! Но ты, как всегда, меня не слушаешь. Теперь расхлёбывай последствия."
                tone = "angry"
            elif paranoia > 70:
                message = "Что с тобой происходит? Ты совсем потерял контроль... Они всё видят, всё знают. Нужно быть осторожнее!"
                tone = "paranoid"
            else:
                message = "Этот день прошёл не очень хорошо. Нужно серьёзно пересмотреть свой подход к планированию."
                tone = "concerned"

        return {
            'message': message,
            'tone': tone,
            'performance_score': performance_score,
            'day': self.day
        }

    def generate_voice_new_day_message(self, day):
        """Generate start-of-day message from inner voice based on day number"""

        if day == 1:
            message = (
                "Просыпайся. Эй, ты меня вообще слышишь? Не говори что ты опять все забыл... Ох... Хорошо. Это не первый и, видимо, не последний раз. "
                "Ты даже не помнишь свой прошлый план? Какая жалость, видимо придется составить его заново. Давай быстрее - у нас мало времени. ")
            tone = "neutral"
            return {
                'message': message,
                'tone': tone,
                'day': day
            }
        elif day == 2:
            message = (
                "Я должен прояснить кое-что. Все эти параметры: энергия, стресс, паранойя... Они не совсем отражают действительность. Во-первых, по факту "
                "они лишь в твоей глове. Во-вторых, ты можешь себя хорошо чувствовать и при высокой и при низкой энергии, однако если опустишь её уж совсем "
                "низко, то появится неприятный статус - истощение. Вот как раз на статусы нужно обращать больше вниманияи. Понятное дело, что их гораздо больше "
                "и обо всех я тебе не расскажу. Просто помни, что держать параметры нужно в золотой середине. ")
            tone = "neutral"
            return {
                'message': message,
                'tone': tone,
                'day': day
            }
        elif day == 3:
            message = (
                "Вижу ты уже немного освоился, да? На первый взгляд может показаться, что все даже слишком просто, но... Не стоит делать поспешных выводов. "
                "Не обещаю, что буду приходить сюда каждый день, но постараюсь давать дельные советы. А и ещё... Иногда я буду давать тебе задания. "
                "Не удивляйся им. На самом деле ты сам хотел их выполнить в прошлом, просто видимо забыл. ")
            tone = "neutral"
            return {
                'message': message,
                'tone': tone,
                'day': day
            }
        elif day == 4:
            message = (
                "Слушай... Тебе сейчас может показаться странным - зачем я даю тебе какие-то задания? На самом деле я уже объяснял, что это "
                "твои собственные задания - ты про них просто забыл. Но в любом случае - если тебе вдруг станет тяжело на душе или ещё "
                "чего случиться... Можешь поговорить со мной. Я постараюсь тебя успокоить. Но ты должен понимать - у всего есть своя цена... ")
            tone = "neutral"
            return {
                'message': message,
                'tone': tone,
                'day': day
            }
        elif day == 5:
            message = (
                "За несколько последних дней ты уже получил неколько... поощрений от меня, да? Но ты пока не знаешь куда их потратить. "
                "В общем у меня есть для тебя сюрприз. Я же на самом деле не просто голос в твоей голове. Вернее... "
                "Ладно, не так важно, суть в том, что я могу несколько управлять твоим сознанием. Не бойся, хозяин тела до сих пор ты. "
                "Просто я могу немного корректировать твоё восприятие вещей. Сейчас откроется доступ к некоторым моим возможностям. "
                "Для простоты буду называть их карточками. Попробуй мысленно зайти туда и осмотреться, но знай - тебе доступно ещё не все. ")
            tone = "neutral"
            return {
                'message': message,
                'tone': tone,
                'day': day
            }
        elif day == 6:
            message = (
                "А, кстати. Ещё раз напомню, ведь ты скорее всего забыл - выкладывайся каждый день на максимум. На тридцатый день, а это через 26 дней, "
                "мы с тобой кое о чем поговорим. Чем сильнее ты подготовишься к этому дню - тем лучше. Опять же - не буду раскрывать все свои карты, "
                "но скажу так - ты забыл слегка больше, чем думаешь.")
            tone = "neutral"
            return {
                'message': message,
                'tone': tone,
                'day': day
            }
        elif day == 8:
            message = (
                "Не устал делать одно и тоже? Повторение одинаковых действий неизбежно ведет к накоплению скуки и потере интереса. Чтобы этого не "
                "произошло старайся не делать одни и теже активности слишком много дней подряд. В ином случае их эффективность будет снижена. "
                "Потерянный интерес возвращается со временем. Вообще... Его можно вернуть и другим образом, но тебе о нем знать рано. "
                "Кстати, теперь ты будешь видеть проценты эффективности у активностей, которые тебе надоели.")
            tone = "neutral"
            return {
                'message': message,
                'tone': tone,
                'day': day
            }
        elif day == 10:
            message = (
                "Помнишь, что я тебе говорил о 30 дне? Он все ближе и ближе. Осталось всего 20 дней. Надеюсь ты уже освоил все, что я тебе показал? ")
            tone = "neutral"
            return {
                'message': message,
                'tone': tone,
                'day': day
            }
        elif day == 20:
            message = (
                "Помнишь, что я тебе говорил о 30 дне? Он все ближе и ближе. Осталось всего 10 дней. Мне уже нечего от тебя скрывать. "
                "Ну почти. Тебе уже стали доступны все мои 'ментальные карточки', воспользуйся ими в нужный момент. ")
            tone = "neutral"
            return {
                'message': message,
                'tone': tone,
                'day': day
            }
        elif day == 29:
            message = (
                "...Совсем Близко...")
            tone = "neutral"
            return {
                'message': message,
                'tone': tone,
                'day': day
            }
        elif day == 30:
            message = (
                "Сегодня вечером нам нужно встретиться на крыше одного заброшенного здания. Зачем? Оно должно пробудить в тебе "
                "остатки воспоминаний. Не буду пока вдаваться в подробности, но... В общем ты сам все увидишь. Не помнишь адреса? "
                "Иди по интуиции. Уверен, она не подведет тебя. ")
            tone = "neutral"
            return {
                'message': message,
                'tone': tone,
                'day': day
            }
        else:
            # Для остальных дней не показываем сообщение
            return None


class MusicManager:
    def __init__(self):
        self.current_playlist = None
        self.current_track_index = 0
        self.track_start_time = 0
        self.min_track_duration = 20000  # 20 seconds minimum
        self.fade_duration = 2000  # 2 seconds fade
        self.is_fading = False
        self.fade_start_time = 0
        self.next_playlist = None
        self.volume = 0.3  # Background music volume

        # Music playlists - automatically load from directories
        self.playlists = self.load_music_playlists()

        # Ending music tracks
        self.ending_tracks = self.load_ending_music()

        # Try to load sounds, fallback to silence if files don't exist
        self.sounds_loaded = self.load_sounds()

        # Whisper system for paranoia effects
        self.whisper_sounds = self.load_whisper_sounds()
        self.last_whisper_time = 0
        self.whisper_finished_time = 0  # Track when last whisper finished
        self.whisper_cooldown = 20000  # 20 seconds minimum between whispers
        self.whisper_volume = 0.12  # Base whisper volume (slightly higher)

        # Fade-in system for music startup
        self.is_fading_in = False
        self.fade_in_start_time = 0
        self.fade_in_duration = 3000  # 3 seconds fade-in

    def load_music_playlists(self):
        """Automatically load music files from directories"""
        import os
        import glob

        playlists = {
            'normal': [],
            'tense': [],
            'paranoid': []
        }

        # Supported audio formats
        audio_extensions = ['*.ogg', '*.wav', '*.mp3', '*.flac', '*.aac']

        for playlist_name in playlists.keys():
            playlist_dir = f'music/{playlist_name}'

            # Check if directory exists
            if os.path.exists(playlist_dir) and os.path.isdir(playlist_dir):
                # Scan for all supported audio files
                for extension in audio_extensions:
                    pattern = os.path.join(playlist_dir, extension)
                    files = glob.glob(pattern)
                    playlists[playlist_name].extend(files)

                # Sort files for consistent ordering
                playlists[playlist_name].sort()

                pass  # Playlist loaded successfully
            else:
                pass  # Directory not found

        # Fallback to empty lists if no files found
        if not any(playlists.values()):
            playlists = {
                'normal': ['silent'],
                'tense': ['silent'],
                'paranoid': ['silent']
            }

        return playlists

    def load_ending_music(self):
        """Load ending music tracks from music/end directory"""
        import os
        import glob

        ending_tracks = {
            'good': None,  # music/end/1.*
            'neutral': None,  # music/end/2.*
            'bad': None,  # music/end/3.*
            'perfect': None,  # music/end/4.*
            'breakthrough': None,  # music/end/5.*
            'control': None  # music/end/6.*
        }

        # Supported audio formats
        audio_extensions = ['*.ogg', '*.wav', '*.mp3', '*.flac', '*.aac']

        end_dir = 'music/end'

        if os.path.exists(end_dir) and os.path.isdir(end_dir):
            # Look for specific numbered tracks
            track_mappings = {
                'good': '1',
                'neutral': '2',
                'bad': '3',
                'perfect': '4',
                'breakthrough': '5',
                'control': '6'
            }

            for ending_type, track_number in track_mappings.items():
                for extension in audio_extensions:
                    pattern = os.path.join(end_dir, f"{track_number}.*")
                    files = glob.glob(pattern)
                    if files:
                        # Take the first matching file
                        ending_tracks[ending_type] = files[0]
                        break

        return ending_tracks

    def load_ending_music_duplicate(self):
        """DEPRECATED: Duplicate function - should be removed"""
        import os
        import glob

        ending_tracks = {
            'good': None,  # music/end/1.*
            'neutral': None,  # music/end/2.*
            'bad': None,  # music/end/3.*
            'perfect': None,  # music/end/4.*
            'breakthrough': None,  # music/end/5.*
            'control': None  # music/end/6.*
        }

        # Supported audio formats
        audio_extensions = ['*.ogg', '*.wav', '*.mp3', '*.flac', '*.aac']

        end_dir = 'music/end'

        if os.path.exists(end_dir) and os.path.isdir(end_dir):
            # Look for specific numbered tracks
            track_mappings = {
                'good': '1',
                'neutral': '2',
                'bad': '3',
                'perfect': '4',
                'breakthrough': '5',
                'control': '6'
            }

            for ending_type, track_number in track_mappings.items():
                for extension in audio_extensions:
                    pattern = os.path.join(ens_dir, f"{track_number}.*")
                    files = glob.glob(pattern)
                    if files:
                        # Take the first matching file
                        ending_tracks[ending_type] = files[0]
                        break

        return ending_tracks

    def load_whisper_sounds(self):
        """Load whisper sound effects for paranoia system"""
        import os
        import glob

        whisper_sounds = []

        # Supported audio formats
        audio_extensions = ['*.ogg', '*.wav', '*.mp3', '*.flac', '*.aac']

        whisper_dir = 'whisper'

        # Check if whisper directory exists
        if os.path.exists(whisper_dir) and os.path.isdir(whisper_dir):
            # Scan for all supported audio files
            for extension in audio_extensions:
                pattern = os.path.join(whisper_dir, extension)
                files = glob.glob(pattern)
                whisper_sounds.extend(files)

            # Sort files for consistent ordering
            whisper_sounds.sort()

            pass  # Whisper sounds loaded successfully
        else:
            pass  # Directory not found

        # If no whisper sounds found, create empty list
        if not whisper_sounds:
            pass  # No whisper sounds found
            whisper_sounds = []

        return whisper_sounds

    def load_sounds(self):
        """Try to load sound files, return True if successful"""
        try:
            # Test loading one file from each playlist
            for playlist_name, tracks in self.playlists.items():
                if tracks and tracks[0] != 'silent':
                    # Try to load first track to test (skip 'silent' placeholder)
                    test_sound = pygame.mixer.Sound(tracks[0])
                    del test_sound  # Clean up test
            return True
        except (pygame.error, FileNotFoundError):
            # If sounds can't be loaded, create silent placeholders
            self.create_silent_placeholders()
            return False

    def create_silent_placeholders(self):
        """Create silent audio for when music files aren't available"""

        # Replace all tracks with silence
        for playlist_name in self.playlists:
            self.playlists[playlist_name] = ['silent']

    def get_target_playlist(self, stress, paranoia):
        """Determine which playlist should be playing based on mental state"""
        if paranoia >= 40:
            if stress >= 50:
                return 'paranoid'
            else:
                return 'tense'
        elif stress >= 40:
            return 'tense'
        else:
            return 'normal'

    def update(self, stress, paranoia):
        """Update music system based on current mental state"""
        if not self.sounds_loaded:
            return  # Skip if no sounds available

        # Don't update music during ending
        if self.current_playlist and self.current_playlist.startswith('ending_'):
            return  # Keep ending music playing without interruption

        current_time = pygame.time.get_ticks()
        target_playlist = self.get_target_playlist(stress, paranoia)

        # Check if we need to change playlist
        if target_playlist != self.current_playlist and not self.is_fading:
            # Only change if current track has played for minimum duration
            track_duration = current_time - self.track_start_time
            if track_duration >= self.min_track_duration or self.current_playlist is None:
                self.start_fade_to_playlist(target_playlist)

        # Handle fade-in from startup
        if self.is_fading_in:
            fade_in_progress = (current_time - self.fade_in_start_time) / self.fade_in_duration
            if fade_in_progress >= 1.0:
                # Fade-in complete
                self.is_fading_in = False
                pygame.mixer.music.set_volume(self.volume)
            else:
                # Apply fade-in effect (gradual volume increase)
                fade_in_volume = self.volume * fade_in_progress
                pygame.mixer.music.set_volume(fade_in_volume)

        # Handle regular fading (between playlists)
        elif self.is_fading:
            fade_progress = (current_time - self.fade_start_time) / self.fade_duration
            if fade_progress >= 1.0:
                # Fade complete, switch to new playlist
                self.complete_fade()
            else:
                # Apply fade effect
                fade_volume = self.volume * (1.0 - fade_progress)
                pygame.mixer.music.set_volume(fade_volume)

        # Check if current track finished and start next (don't interfere with fade-in)
        if not pygame.mixer.music.get_busy() and self.current_playlist and not self.is_fading and not self.is_fading_in:
            self.play_next_track()

        # Handle whisper system for paranoia
        self.update_whisper_system(paranoia, current_time)

    def start_fade_to_playlist(self, new_playlist):
        """Start fading current music to switch to new playlist"""
        self.is_fading = True
        self.fade_start_time = pygame.time.get_ticks()
        self.next_playlist = new_playlist

    def complete_fade(self):
        """Complete the fade transition and start new playlist"""
        self.is_fading = False
        self.current_playlist = self.next_playlist
        self.next_playlist = None

        # Start with random track instead of first track
        import random
        playlist = self.playlists[self.current_playlist]
        if playlist:
            self.current_track_index = random.randint(0, len(playlist) - 1)
        else:
            self.current_track_index = 0

        self.play_current_track()

    def play_current_track(self):
        """Play the current track in the current playlist"""
        if not self.sounds_loaded or not self.current_playlist:
            return

        playlist = self.playlists[self.current_playlist]
        if not playlist:
            return

        track_path = playlist[self.current_track_index]

        try:
            if track_path == 'silent':
                # For silent placeholder, just set a timer
                self.track_start_time = pygame.time.get_ticks()
                return

            pygame.mixer.music.load(track_path)
            # Set volume based on current fade state
            if self.is_fading_in:
                # During fade-in, volume will be controlled by update method
                pygame.mixer.music.set_volume(0)
            else:
                pygame.mixer.music.set_volume(self.volume)
            pygame.mixer.music.play()
            self.track_start_time = pygame.time.get_ticks()

            # Track is now playing
            pass

        except (pygame.error, FileNotFoundError) as e:
            # Skip to next track if current one fails
            self.play_next_track()

    def play_next_track(self):
        """Move to next track in current playlist"""
        if not self.current_playlist:
            return

        playlist = self.playlists[self.current_playlist]
        self.current_track_index = (self.current_track_index + 1) % len(playlist)
        self.play_current_track()

    def start_playlist(self, playlist_name):
        """Start playing a specific playlist immediately"""
        if playlist_name in self.playlists:
            self.current_playlist = playlist_name
            self.is_fading = False

            # Start with random track instead of first track
            import random
            playlist = self.playlists[playlist_name]
            if playlist:
                self.current_track_index = random.randint(0, len(playlist) - 1)
            else:
                self.current_track_index = 0

            self.play_current_track()

    def start_fade_in(self):
        """Start fade-in effect for music at game startup"""
        self.is_fading_in = True
        self.fade_in_start_time = pygame.time.get_ticks()
        # Set initial volume to 0 for fade-in
        pygame.mixer.music.set_volume(0)

    def stop(self):
        """Stop all music"""
        pygame.mixer.music.stop()
        self.current_playlist = None
        self.is_fading = False

    def update_whisper_system(self, paranoia, current_time):
        """Handle whisper sound effects based on paranoia level"""
        if paranoia <= 30 or not self.whisper_sounds:
            return  # No whispers below 30% paranoia or if no sounds available

        # Calculate whisper frequency based on paranoia level
        # Higher paranoia = more frequent whispers
        # At 30% paranoia: 60 seconds, at 100% paranoia: 20 seconds
        max_interval = 60000  # 60 seconds at 30% paranoia
        min_interval = 20000  # 20 seconds at 100% paranoia
        paranoia_factor = (paranoia - 30) / 70  # 0.0 to 1.0 for paranoia 30-100
        whisper_interval = max_interval - (paranoia_factor * (max_interval - min_interval))

        # Check if enough time has passed since last whisper FINISHED
        # Use whisper_finished_time instead of last_whisper_time
        time_since_last_finished = current_time - self.whisper_finished_time
        if time_since_last_finished >= whisper_interval:
            # Random chance to play whisper (higher paranoia = higher chance)
            whisper_chance = 0.3 + (paranoia_factor * 0.4)  # 30% to 70% chance

            if random.random() < whisper_chance:
                self.play_whisper(paranoia)
                self.last_whisper_time = current_time

    def play_whisper(self, paranoia):
        """Play a random whisper sound with volume based on paranoia level"""
        if not self.whisper_sounds:
            return

        try:
            # Select random whisper sound
            whisper_file = random.choice(self.whisper_sounds)

            # Calculate volume based on paranoia (30-100 -> 0.08-0.25 volume)
            paranoia_factor = (paranoia - 30) / 70  # 0.0 to 1.0
            volume = 0.08 + (paranoia_factor * 0.17)  # 0.08 to 0.25 volume (slightly louder)

            # Load and play whisper on a separate channel
            whisper_sound = pygame.mixer.Sound(whisper_file)
            whisper_sound.set_volume(volume)

            # Play on any available channel
            channel = whisper_sound.play()

            # Set when this whisper will finish (estimate based on sound length)
            if channel:
                # Get sound length in milliseconds
                sound_length_ms = int(whisper_sound.get_length() * 1000)
                self.whisper_finished_time = pygame.time.get_ticks() + sound_length_ms
            else:
                # Fallback if channel info unavailable - assume 2 second whisper
                self.whisper_finished_time = pygame.time.get_ticks() + 2000

            # Whisper sound is playing
            pass

        except (pygame.error, FileNotFoundError) as e:
            # Error playing whisper sound
            pass

    def play_ending_music(self, ending_type):
        """Play ending music based on ending type"""
        if not self.sounds_loaded:
            return

        track_path = self.ending_tracks.get(ending_type)
        if not track_path:
            return  # No ending music found for this type

        try:
            # Stop current music and start ending track
            pygame.mixer.music.stop()
            pygame.mixer.music.load(track_path)
            pygame.mixer.music.set_volume(self.volume * 1.2)  # Slightly louder for dramatic effect
            pygame.mixer.music.play(-1)  # Loop ending music indefinitely

            # Update current playlist to indicate ending music is playing
            self.current_playlist = f'ending_{ending_type}'
            self.is_fading = False
            self.is_fading_in = False

        except (pygame.error, FileNotFoundError):
            pass  # Silently fail if ending music can't be played

    def play_ending_music(self, ending_type):
        """Play ending music based on ending type"""
        if not self.sounds_loaded:
            return

        track_path = self.ending_tracks.get(ending_type)
        if not track_path:
            return  # No ending music found for this type

        try:
            # Stop current music and start ending track
            pygame.mixer.music.stop()
            pygame.mixer.music.load(track_path)
            pygame.mixer.music.set_volume(self.volume * 1.2)  # Slightly louder for dramatic effect
            pygame.mixer.music.play(-1)  # Loop ending music

            # Update current playlist to indicate ending music is playing
            self.current_playlist = f'ending_{ending_type}'
            self.is_fading = False
            self.is_fading_in = False

        except (pygame.error, FileNotFoundError):
            pass  # Silently fail if ending music can't be played

    def set_volume(self, volume):
        """Set music volume (0.0 to 1.0)"""
        self.volume = max(0.0, min(1.0, volume))
        # Don't change volume immediately if we're in any fade state
        if not self.is_fading and not self.is_fading_in:
            pygame.mixer.music.set_volume(self.volume)


class VisualDayPlanningGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Phyco Phycles")
        self.clock = pygame.time.Clock()
        self.running = True

        init_fonts()

        self.game_state = GameState()

        # Initialize music system
        self.music_manager = MusicManager()
        self.music_enabled = True

        # Start with normal playlist with fade-in effect
        self.music_manager.start_playlist('normal')
        self.music_manager.start_fade_in()

        # UI components
        self.create_ui_components()

    def can_click_button(self, button_id):
        """Check if enough time has passed since last click on this specific button"""
        current_time = pygame.time.get_ticks()
        last_click = self.button_last_click.get(button_id, 0)
        return current_time - last_click > self.click_cooldown

    def register_button_click(self, button_id):
        """Register a successful click on a specific button"""
        self.button_last_click[button_id] = pygame.time.get_ticks()

    def create_ui_components(self):
        """Create UI buttons and components"""
        # Main action buttons - унифицированный размер и расположение
        button_width = 115
        button_height = 35

        self.buttons = {
            # Первый ряд (y = 630)
            'save_schedule': Button(650, 630, button_width, button_height, "Сохранить"),
            'clear_timeline': Button(780, 630, button_width, button_height, "Очистить"),

            # Второй ряд (y = 675)
            'load_schedule': Button(650, 675, button_width, button_height, "Загрузить"),
            'start_day': Button(780, 675, button_width, button_height, "Начать день"),
            'next_phase': Button(910, 675, button_width, button_height, "Далее"),

            # Третий ряд (y = 720) - только кнопка "Новый день"
            'new_day': Button(910, 720, button_width, button_height, "Новый день"),

            # Верхние кнопки панелей (текст будет обновляться динамически) - под словом "Фаза:"
            'voice_panel': Button(1000, 80, 75, 30, "???", 'small'),  # Изначально заблокировано
            'help': Button(1000, 120, 75, 30, "Помощь", 'small'),  # Под кнопкой голос
            'music_toggle': Button(1080, 80, 75, 30, "Музыка", 'small'),
            'cards_panel': Button(1080, 120, 75, 30, "???", 'small')  # Под кнопкой музыка
        }

        # Progress bars
        self.progress_bars = {
            'energy': ProgressBar(20, 80, 220, 30),
            'stress': ProgressBar(20, 120, 220, 30),
            'paranoia': ProgressBar(250, 80, 220, 30)
        }

        # Per-button click protection system
        self.button_last_click = {}  # Track last click time for each button
        self.click_cooldown = 500  # 500ms (0.5 second) cooldown per button

    def handle_events(self):
        """Handle pygame events"""
        # Skip event handling during restart transition
        if hasattr(self, 'restart_transition_phase'):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
            return

        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = False
        mouse_released = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    mouse_clicked = True
                    self.handle_mouse_down(mouse_pos)
                elif event.button == 3:  # Right click
                    self.handle_right_click(mouse_pos)

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Left click release
                    mouse_released = True
                    self.handle_mouse_up(mouse_pos)

            elif event.type == pygame.MOUSEMOTION:
                self.handle_mouse_motion(mouse_pos)

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_h:
                    self.game_state.show_help = not self.game_state.show_help
                elif event.key == pygame.K_SPACE:
                    if self.game_state.phase == 'planning':
                        self.start_day()
                    elif self.game_state.phase == 'execution':
                        self.continue_execution()
                    elif self.game_state.phase == 'results':
                        self.new_day()
                    elif self.game_state.phase == 'game_ending':
                        # Restart game from ending screen
                        self.restart_game_completely()
                elif event.key == pygame.K_c:
                    if self.game_state.phase == 'planning':
                        self.clear_timeline()

            elif event.type == pygame.MOUSEWHEEL:
                # Handle scrolling in different panels
                mouse_pos = pygame.mouse.get_pos()

                # Check if mouse is over cards panel
                if (self.game_state.show_cards_panel and
                        pygame.Rect(30, 180, 450, 500).collidepoint(mouse_pos)):
                    # Different scroll handling based on current tab
                    current_tab = getattr(self, 'current_card_tab', 0)
                    if current_tab == 0:  # Available cards
                        if not hasattr(self, 'card_scroll'):
                            self.card_scroll = 0
                        self.card_scroll += event.y * 30
                    elif current_tab == 1:  # All cards catalog
                        if not hasattr(self, 'catalog_scroll'):
                            self.catalog_scroll = 0
                        self.catalog_scroll += event.y * 30
                    elif current_tab == 2:  # Player deck
                        if not hasattr(self, 'deck_scroll'):
                            self.deck_scroll = 0
                        self.deck_scroll += event.y * 30
                else:
                    # Handle scrolling in activity list
                    self.game_state.scroll_offset = max(0, self.game_state.scroll_offset - event.y * 20)

        # Handle button clicks with per-button protection
        if mouse_clicked:
            # Start day button
            if (self.buttons['start_day'].update(mouse_pos, True) and
                    self.game_state.phase == 'planning' and
                    self.can_click_button('start_day')):
                self.register_button_click('start_day')
                self.start_day()

            # Next phase button
            elif (self.buttons['next_phase'].update(mouse_pos, True) and
                  self.can_click_button('next_phase')):
                self.register_button_click('next_phase')
                if self.game_state.phase == 'execution':
                    self.continue_execution()
                elif self.game_state.phase == 'results':
                    self.new_day()

            # Help button
            elif (self.buttons['help'].update(mouse_pos, True) and
                  self.can_click_button('help')):
                self.register_button_click('help')
                self.game_state.show_help = not self.game_state.show_help

            # New day button
            elif (self.buttons['new_day'].update(mouse_pos, True) and
                  self.game_state.phase == 'results' and
                  self.can_click_button('new_day')):
                self.register_button_click('new_day')
                self.new_day()

            # Clear timeline button
            elif (self.buttons['clear_timeline'].update(mouse_pos, True) and
                  self.game_state.phase == 'planning' and
                  self.can_click_button('clear_timeline')):
                self.register_button_click('clear_timeline')
                self.clear_timeline()

            # Cards panel button (only if unlocked)
            elif (self.buttons['cards_panel'].update(mouse_pos, True) and
                  self.can_click_button('cards_panel') and
                  self.game_state.day >= 5):
                self.register_button_click('cards_panel')
                self.game_state.show_cards_panel = not self.game_state.show_cards_panel

            # Voice panel button (only if unlocked)
            elif (self.buttons['voice_panel'].update(mouse_pos, True) and
                  self.can_click_button('voice_panel') and
                  self.game_state.day >= 3):
                self.register_button_click('voice_panel')
                self.game_state.show_voice_panel = not self.game_state.show_voice_panel

            # Music toggle button
            elif (self.buttons['music_toggle'].update(mouse_pos, True) and
                  self.can_click_button('music_toggle')):
                self.register_button_click('music_toggle')
                self.toggle_music()

            # Save schedule button
            elif (self.buttons['save_schedule'].update(mouse_pos, True) and
                  self.game_state.phase == 'planning' and
                  self.can_click_button('save_schedule')):
                self.register_button_click('save_schedule')
                self.save_current_schedule()

            # Load schedule button
            elif (self.buttons['load_schedule'].update(mouse_pos, True) and
                  self.game_state.phase == 'planning' and
                  self.can_click_button('load_schedule')):
                self.register_button_click('load_schedule')
                self.load_saved_schedule()

        # Always update button hover states
        for button in self.buttons.values():
            if not mouse_clicked:
                button.update(mouse_pos, False)

        # Handle activity selection from available list (now optional - for visual feedback only)
        if self.game_state.phase == 'planning' and not self.game_state.dragging_activity and mouse_clicked:
            activity_area = pygame.Rect(510, 220, 460, 140)  # Updated bounds
            if activity_area.collidepoint(mouse_pos):
                # Calculate which activity was clicked with improved precision
                relative_y = mouse_pos[1] - 230 + self.game_state.scroll_offset
                activity_index = relative_y // 50

                # Sort activities the same way as in draw_activities_panel
                sorted_activities = sorted(self.game_state.available_activities,
                                           key=lambda act: (not act['mandatory'], act['name']))

                # Make sure the index is valid and the activity is visible and available
                if 0 <= activity_index < len(sorted_activities):
                    actual_y = 230 + activity_index * 50 - self.game_state.scroll_offset
                    if 220 <= actual_y <= 360:  # Activity is visible in clipped panel
                        selected_activity = sorted_activities[activity_index]
                        if self.game_state.is_activity_available_today(selected_activity):
                            # Find the original index of the selected activity
                            original_index = self.game_state.available_activities.index(selected_activity)
                            self.game_state.selected_activity = original_index
                        else:
                            self.game_state.add_message(
                                f"{selected_activity['name']}: {self.game_state.get_unavailable_reason(selected_activity)}",
                                'warning')

    def handle_mouse_down(self, mouse_pos):
        """Handle mouse button down"""
        if self.game_state.phase != 'planning':
            return

        # Check if clicking on timeline activity
        timeline_activity = self.game_state.get_timeline_activity_at_position(mouse_pos[0], mouse_pos[1])
        if timeline_activity:
            self.game_state.dragging_activity = timeline_activity
            timeline_activity.dragging = True
            timeline_activity.drag_offset_x = mouse_pos[0] - timeline_activity.rect.x
            timeline_activity.drag_offset_y = mouse_pos[1] - timeline_activity.rect.y
            return

        # Check if clicking on available activity to drag to timeline (no selection required)
        activity_area = pygame.Rect(510, 220, 460, 140)  # Updated bounds
        if activity_area.collidepoint(mouse_pos):
            # Calculate which activity was clicked for dragging
            relative_y = mouse_pos[1] - 230 + self.game_state.scroll_offset
            clicked_activity_index = relative_y // 50

            # Sort activities the same way as in draw_activities_panel
            sorted_activities = sorted(self.game_state.available_activities,
                                       key=lambda act: (not act['mandatory'], act['name']))

            # Any activity can be dragged, regardless of selection
            if 0 <= clicked_activity_index < len(sorted_activities):
                actual_y = 230 + clicked_activity_index * 50 - self.game_state.scroll_offset
                if 220 <= actual_y <= 360:  # Activity is visible in clipped area
                    activity = sorted_activities[clicked_activity_index]

                    # Check if activity is available today
                    if not self.game_state.is_activity_available_today(activity):
                        self.game_state.add_message(
                            f"{activity['name']}: {self.game_state.get_unavailable_reason(activity)}", 'warning')
                        return

                    # Calculate activity width based on duration and timeline scale
                    hours_range = self.game_state.timeline_end_hour - self.game_state.timeline_start_hour
                    hour_width = (self.game_state.timeline_rect.width - 40) / hours_range
                    duration_width = hour_width * activity['duration']

                    # Create temporary timeline activity for dragging
                    temp_activity = TimelineActivity(activity, 0, activity['duration'], mouse_pos[0], mouse_pos[1],
                                                     duration_width, 50)  # Увеличена высота
                    temp_activity.dragging = True
                    temp_activity.drag_offset_x = duration_width // 2  # Center the drag
                    temp_activity.drag_offset_y = 20
                    self.game_state.dragging_activity = temp_activity

    def handle_mouse_up(self, mouse_pos):
        """Handle mouse button up"""
        if not self.game_state.dragging_activity:
            return

        dragging_activity = self.game_state.dragging_activity

        # Check if dropping on timeline
        if self.game_state.timeline_rect.collidepoint(mouse_pos):
            # Calculate precise drop time based on mouse position
            drop_time = self.game_state.get_hour_from_x_position(mouse_pos[0])

            if dragging_activity in self.game_state.timeline_activities:
                # Moving existing activity
                old_start = dragging_activity.start_time
                old_end = dragging_activity.end_time

                # Temporarily remove from timeline for conflict checking
                self.game_state.timeline_activities.remove(dragging_activity)

                # Check if activity can be placed normally or with special card ability
                can_place_normally = self.game_state.can_place_activity_at_time(dragging_activity.activity, drop_time)
                can_place_with_card = (hasattr(self.game_state, 'activity_move_uses') and
                                       self.game_state.activity_move_uses > 0)

                if can_place_normally or can_place_with_card:
                    # Update position to exact drop location
                    dragging_activity.start_time = drop_time
                    dragging_activity.end_time = drop_time + dragging_activity.activity['duration']

                    # Update visual position with precise grid alignment
                    x = self.game_state.get_hour_x_position(dragging_activity.start_time)
                    width = self.game_state.get_hour_x_position(dragging_activity.end_time) - x
                    dragging_activity.rect.x = x
                    dragging_activity.rect.y = self.game_state.timeline_rect.y + 60
                    dragging_activity.rect.width = width
                    dragging_activity.rect.height = 50

                    # ВАЖНО: Добавляем обратно в список ДО вызова format_time_display
                    self.game_state.timeline_activities.append(dragging_activity)

                    # Use card ability if needed
                    if not can_place_normally and can_place_with_card:
                        self.game_state.activity_move_uses -= 1
                        message_suffix = " (использована карта времени)"
                    else:
                        message_suffix = ""

                    # More informative message showing exact time placement
                    start_str = self.format_time_display(drop_time)
                    end_str = self.format_time_display(dragging_activity.end_time)
                    self.game_state.add_message(
                        f"Перемещено: {dragging_activity.activity['name']} ({start_str}-{end_str}){message_suffix}",
                        'success')
                else:
                    # Restore original position
                    dragging_activity.start_time = old_start
                    dragging_activity.end_time = old_end
                    x = self.game_state.get_hour_x_position(old_start)
                    width = self.game_state.get_hour_x_position(old_end) - x
                    dragging_activity.rect.x = x
                    dragging_activity.rect.width = width
                    dragging_activity.rect.height = 50  # Восстанавливаем высоту тоже
                    self.game_state.timeline_activities.append(dragging_activity)
                    self.game_state.add_message("Нельзя переместить сюда!", 'danger')
            else:
                # Adding new activity from available list to exact drop location
                self.game_state.place_activity_on_timeline(dragging_activity.activity, drop_time)

        # Reset dragging state
        if dragging_activity:
            dragging_activity.dragging = False
        self.game_state.dragging_activity = None
        self.game_state.update_timeline_conflicts()

    def handle_mouse_motion(self, mouse_pos):
        """Handle mouse motion"""
        if self.game_state.dragging_activity:
            activity = self.game_state.dragging_activity
            activity.rect.x = mouse_pos[0] - activity.drag_offset_x
            activity.rect.y = mouse_pos[1] - activity.drag_offset_y

    def handle_right_click(self, mouse_pos):
        """Handle right mouse click"""
        if self.game_state.phase != 'planning':
            return

        # Check if right-clicking on timeline activity to remove it
        timeline_activity = self.game_state.get_timeline_activity_at_position(mouse_pos[0], mouse_pos[1])
        if timeline_activity:
            self.game_state.remove_timeline_activity(timeline_activity)
            self.game_state.update_timeline_conflicts()

    def format_time_display(self, time_value):
        """Format time value for display (e.g., 8.5 -> 8:30)"""
        hours = int(time_value)
        minutes = int((time_value % 1) * 60)
        return f"{hours}:{minutes:02d}"

    def clear_timeline(self):
        """Clear all activities from timeline"""
        self.game_state.timeline_activities.clear()
        self.game_state.add_message("Временная шкала очищена", 'warning')

    def start_day(self):
        """Start the execution phase"""
        if not self.game_state.timeline_activities:
            self.game_state.add_message("Пожалуйста, запланируйте хотя бы одну активность!", 'warning')
            return

        # Check if all mandatory activities are scheduled (only those available today)
        available_mandatory = [act for act in self.game_state.available_activities
                               if act['mandatory'] and self.game_state.is_activity_available_today(act)]
        scheduled_names = [ta.activity['name'] for ta in self.game_state.timeline_activities]
        missing_mandatory = [act for act in available_mandatory if act['name'] not in scheduled_names]

        if missing_mandatory:
            missing_names = [act['name'] for act in missing_mandatory]
            self.game_state.add_message(f"Отсутствуют обязательные: {', '.join(missing_names)}", 'danger')
            return

        # Check for conflicts
        self.game_state.update_timeline_conflicts()
        has_conflicts = any(ta.has_conflict for ta in self.game_state.timeline_activities)

        if has_conflicts:
            self.game_state.add_message("Устраните конфликты времени перед началом дня!", 'danger')
            return

        self.game_state.phase = 'execution'
        self.game_state.current_time = 8.0
        self.game_state.current_activity_index = 0
        self.game_state.add_message("Выполнение дня началось!", 'success')

    def resume_activity_if_interrupted(self):
        """Возобновляем активность если она была прервана событием"""
        if (hasattr(self.game_state, 'interrupted_activity') and
                self.game_state.interrupted_activity and
                hasattr(self.game_state, 'activity_end_time')):
            old_time = self.game_state.current_time
            # Переносим время на конец активности, чтобы избежать стресса за "безделье"
            self.game_state.current_time = self.game_state.activity_end_time
            self.game_state.interrupted_activity = False
            delattr(self.game_state, 'activity_end_time')
            self.game_state.add_message(
                f"✅ Активность возобновлена: время {old_time:.1f} -> {self.game_state.current_time:.1f}",
                'success')

    def continue_execution(self):
        """Continue with day execution"""
        scheduled_activities = self.game_state.get_planned_schedule()

        if self.game_state.current_activity_index >= len(scheduled_activities):
            self.end_day()
            return

        # Process current activity
        current_timeline_activity = scheduled_activities[self.game_state.current_activity_index]
        current_activity = current_timeline_activity.activity

        # 🔍 ЛОГИРОВАНИЕ: Показываем статус флагов события
        if hasattr(self.game_state, 'event_time_skip_active') and self.game_state.event_time_skip_active:
            print(
                f"🛡️ Обнаружен активный флаг события перед активностью '{current_timeline_activity.activity['name']}'")
            # НЕ очищаем флаг, пусть сама защита его обработает

        # Отладочное сообщение
        self.game_state.add_message(
            f"🕰 Активность '{current_timeline_activity.activity['name']}': {current_timeline_activity.start_time}-{current_timeline_activity.end_time}, тек.вр.: {self.game_state.current_time:.1f}",
            'info')

        # Проверяем свободное время ДО активности (не во время активности!)
        self.check_free_time_penalty(current_timeline_activity.start_time, False)

        # Проверяем, нужно ли возобновить активность после события
        if (hasattr(self.game_state, 'event_interrupted_activity') and
                self.game_state.event_interrupted_activity and
                hasattr(self.game_state, 'activity_resume_time')):
            # Возобновляем активность с момента окончания
            self.game_state.current_time = self.game_state.activity_resume_time
            self.game_state.event_interrupted_activity = False
            delattr(self.game_state, 'activity_resume_time')

        # Если событие активно, прерываем выполнение
        if hasattr(self.game_state, 'show_event_popup') and self.game_state.show_event_popup:
            # Событие прервало выполнение, остаемся на текущем времени
            return

        # Apply activity effects
        self.process_activity(current_activity)

        # 🛡️ УНИВЕРСАЛЬНАЯ ЗАЩИТА: Любое событие во время активности
        # Если происходит событие, устанавливаем защиту от стресса
        if (hasattr(self.game_state, 'show_event_popup') and
                self.game_state.show_event_popup and
                hasattr(self.game_state, 'current_event')):
            # Устанавливаем защиту от свободного времени
            event_start = self.game_state.current_time
            activity_end = current_timeline_activity.end_time

            print(f"🛡️ ОБНАРУЖЕНО СОБЫТИЕ ВО ВРЕМЯ АКТИВНОСТИ!")
            print(f"   Событие: '{self.game_state.current_event.get('name', '???')}'")
            print(f"   Время события: {event_start:.1f}")
            print(f"   Конец активности: {activity_end:.1f}")

            # Устанавливаем флаги защиты
            self.game_state.event_time_skip_start = event_start
            self.game_state.event_time_skip_end = activity_end
            self.game_state.event_time_skip_active = True

            print(f"🛡️ УСТАНОВЛЕНА ЗАЩИТА: [{event_start:.1f}, {activity_end:.1f}]")

        # Move to next activity
        self.game_state.current_time = current_timeline_activity.end_time
        self.game_state.current_activity_index += 1

        # Check for events (постоянная проверка времени)
        self.check_for_events()

        # Дополнительная проверка событий во время активности
        self.check_activity_random_events()

        # Check for game over conditions
        if self.check_game_over_conditions():
            return

        # Check if day is complete
        if (self.game_state.current_activity_index >= len(scheduled_activities) or
                self.game_state.current_time >= 22):
            # Check final free time before end of day
            self.check_free_time_penalty(22)
            self.end_day()

    def check_free_time_penalty(self, next_activity_time, is_during_activity=False):
        """Apply stress penalty for free time with simplified logic"""

        print(f"🔍 ПРОВЕРКА СТРЕССА [вызов #{getattr(self, '_stress_check_count', 0)}]:")
        if not hasattr(self, '_stress_check_count'):
            self._stress_check_count = 0
        self._stress_check_count += 1

        print(f"   Текущее время: {self.game_state.current_time:.1f}")
        print(f"   Следующая активность: {next_activity_time:.1f}")
        print(f"   Во время активности: {is_during_activity}")
        print(
            f"   Защита активна: {hasattr(self.game_state, 'event_time_skip_active') and self.game_state.event_time_skip_active}")
        if hasattr(self.game_state, 'event_time_skip_active') and self.game_state.event_time_skip_active:
            print(
                f"   Период защиты: [{getattr(self.game_state, 'event_time_skip_start', '?'):.1f}, {getattr(self.game_state, 'event_time_skip_end', '?'):.1f}]")
        print(f"   Активное событие: {getattr(self.game_state, 'show_event_popup', False)}")
        if hasattr(self.game_state, 'current_event') and self.game_state.current_event:
            print(f"   Имя события: '{self.game_state.current_event.get('name', '?')}'")
        print(f"   Стресс до проверки: {self.game_state.stress}")
        print("---")

        # Проверяем есть ли свободное время
        if self.game_state.current_time >= next_activity_time:
            print("✅ Нет свободного времени - ок")
            return

        # ПРАВИЛО 1: Если произошло случайное событие И оно внутри активности - НЕТ СТРЕССА
        event_active = (hasattr(self.game_state, 'event_time_skip_active') and
                        self.game_state.event_time_skip_active)

        if event_active and is_during_activity:
            print("🛡️ Событие внутри активности - стресс НЕ начисляется")
            self.game_state.add_message("🛡️ Событие внутри активности - без стресса", 'success')
            return

        # ПРАВИЛО 2: Если есть активное событие (не во время активности) - НЕТ СТРЕССА
        if event_active:
            print("🛡️ Активное событие защищает от стресса")
            self.game_state.add_message("🛡️ Защита от события", 'success')
            return

        # ПРАВИЛО 3: Если НЕТ события, но переход между активностями - СЧИТАЕМ СТРЕСС
        print(f"📊 Считаем стресс за свободное время: {self.game_state.current_time:.1f} → {next_activity_time:.1f}")

        # Рассчитываем свободное время
        free_time_hours = next_activity_time - self.game_state.current_time
        free_time_minutes = free_time_hours * 60

        # Каждые 10 минут = 4 очка стресса
        stress_penalty = int(free_time_minutes // 10) * 4

        if stress_penalty > 0:
            # Применяем множитель паранойи
            paranoia_multiplier = 1 + (self.game_state.paranoia * 0.01)
            final_stress_penalty = int(stress_penalty * paranoia_multiplier)

            old_stress = self.game_state.stress
            self.game_state.stress = min(100, self.game_state.stress + final_stress_penalty)

            print(f"💀 СТРЕСС НАЧИСЛЕН: {old_stress} → {self.game_state.stress} (+{final_stress_penalty})")
            self.game_state.add_message(f"💀 Стресс за безделье: +{final_stress_penalty} ({free_time_hours:.1f}ч)",
                                        'warning')

        else:
            print("✅ Нет свободного времени для начисления стресса")

        # 🔧 СБРАСЫВАЕМ ЗАЩИТУ ПОСЛЕ ПРОВЕРКИ СТРЕССА
        if hasattr(self.game_state, 'event_time_skip_active') and self.game_state.event_time_skip_active:
            print(f"💫 Очищаем флаг защиты ПОСЛЕ проверки стресса")
            self.game_state.event_time_skip_active = False
            # Удаляем и остальные флаги для очистки
            if hasattr(self.game_state, 'event_time_skip_start'):
                delattr(self.game_state, 'event_time_skip_start')
            if hasattr(self.game_state, 'event_time_skip_end'):
                delattr(self.game_state, 'event_time_skip_end')

        # 🔧 СБРАСЫВАЕМ ЗАЩИТУ ПОСЛЕ ПРОВЕРКИ СТРЕССА
        if hasattr(self.game_state, 'event_time_skip_active') and self.game_state.event_time_skip_active:
            print(f"💫 Очищаем флаг защиты ПОСЛЕ проверки стресса")
            self.game_state.event_time_skip_active = False
            # Удаляем и остальные флаги для очистки
            if hasattr(self.game_state, 'event_time_skip_start'):
                delattr(self.game_state, 'event_time_skip_start')
            if hasattr(self.game_state, 'event_time_skip_end'):
                delattr(self.game_state, 'event_time_skip_end')

    def check_game_over_conditions(self):
        """Check if game should end due to failure conditions"""
        if self.game_state.energy <= 0:
            self.game_over("Энергия исчерпана! Вы не можете продолжать день.")
            return True

        if self.game_state.stress >= 100:
            self.game_over("Стресс достиг критического уровня! Нервный срыв.")
            return True

        return False

    def game_over(self, reason):
        """Handle game over scenario"""
        self.game_state.phase = 'game_over'
        self.game_state.add_message(f"ИГРА ОКОНЧЕНА: {reason}", 'danger')
        self.game_state.game_over_reason = reason

    def process_activity(self, activity):
        """Process an activity and its effects with paranoia modifiers and card effects"""
        # 🚨 ОТЛАДКА: Начало обработки активности
        self.game_state.add_message(
            f"🎢 Обработка активности: '{activity['name']}' (баз.стресс: {activity.get('stress_change', 0)})",
            'info'
        )

        # Check for next activity multiplier from cards
        activity_multiplier = 1.0
        if hasattr(self.game_state, 'next_activity_multiplier'):
            activity_multiplier = self.game_state.next_activity_multiplier
            self.game_state.next_activity_multiplier = 1.0  # Reset after use

        # 🌙 Бонус от осознанного сна
        if hasattr(self.game_state, 'dream_activity_boost') and self.game_state.dream_activity_boost:
            activity_multiplier = max(activity_multiplier, 1.5)
            self.game_state.dream_activity_boost = False
            self.game_state.add_message("✨ Бонус от сна: +50% эффективности!", 'success')

        # Check for motivation boost (target specific activity)
        if (hasattr(self.game_state, 'motivation_boost_active') and
                self.game_state.motivation_boost_active):
            # For simplicity, apply to any activity
            if hasattr(self.game_state, 'motivation_multiplier'):
                activity_multiplier = max(activity_multiplier, self.game_state.motivation_multiplier)
                self.game_state.motivation_boost_active = False

        # Check for activity type bonuses from cards
        activity_location = activity.get('location', '')
        activity_name = activity.get('name', '').lower()

        # Improved activity type detection
        location_to_type = {
            'restaurant': 'social',
            'cinema': 'social',
            'gym': 'physical',
            'outdoor': 'physical',
            'office': 'mental'
        }

        # Additional detection by activity name
        if 'работа' in activity_name or 'учеба' in activity_name:
            activity_type = 'mental'
        elif 'друзьями' in activity_name or 'обед' in activity_name:
            activity_type = 'social'
        elif 'пробежка' in activity_name or 'спортзал' in activity_name or 'прогулка' in activity_name:
            activity_type = 'physical'
        else:
            activity_type = location_to_type.get(activity_location, 'other')

        type_multiplier = 1.0

        if activity_type == 'social' and hasattr(self.game_state, 'social_activities_bonus'):
            type_multiplier = self.game_state.social_activities_bonus
        elif activity_type == 'physical' and hasattr(self.game_state, 'physical_activities_bonus'):
            type_multiplier = self.game_state.physical_activities_bonus
        elif activity_type == 'mental' and hasattr(self.game_state, 'mental_activities_bonus'):
            type_multiplier = self.game_state.mental_activities_bonus

        # Calculate base energy cost
        base_energy_cost = activity['duration'] * 3

        # Apply efficiency bonuses from cards
        if hasattr(self.game_state, 'energy_efficiency'):
            base_energy_cost *= self.game_state.energy_efficiency

        # Calculate raw effects with adaptation
        raw_energy_recovery = activity['energy_recovery']
        raw_stress_change = self.game_state.get_adapted_stress_recovery(activity)  # Use adapted value

        # Apply card multipliers to benefits
        if raw_energy_recovery > 0:
            raw_energy_recovery *= activity_multiplier * type_multiplier
        if raw_stress_change < 0:  # Stress reduction (negative values)
            raw_stress_change *= activity_multiplier * type_multiplier

        # Apply paranoia penalties
        paranoia_factor = self.game_state.paranoia * 0.01

        # Paranoia reduces energy recovery from all sources
        if raw_energy_recovery > 0:
            effective_energy_recovery = raw_energy_recovery * (1 - paranoia_factor * 0.5)
        else:
            effective_energy_recovery = raw_energy_recovery

        # Apply status effects to energy recovery (only if methods exist)
        if hasattr(self.game_state, 'apply_status_effects_to_value'):
            if raw_energy_recovery > 0:
                effective_energy_recovery = self.game_state.apply_status_effects_to_value(
                    'energy_recovery', effective_energy_recovery, False)

            # Apply status effects to energy cost
            base_energy_cost = self.game_state.apply_status_effects_to_value(
                'energy_cost', base_energy_cost, False)

        # Paranoia increases stress from all sources
        if raw_stress_change > 0:  # Positive stress change (bad)
            effective_stress_change = raw_stress_change * (1 + paranoia_factor)
        else:  # Negative stress change (stress relief)
            effective_stress_change = raw_stress_change * (1 - paranoia_factor * 0.3)

        # Apply status effects to stress changes (only if methods exist)
        if hasattr(self.game_state, 'apply_status_effects_to_value'):
            if raw_stress_change > 0:
                effective_stress_change = self.game_state.apply_status_effects_to_value(
                    'stress', effective_stress_change, True)
            else:
                effective_stress_change = self.game_state.apply_status_effects_to_value(
                    'stress', effective_stress_change, False)

            # Apply additional status-specific effects
            for status in self.game_state.status_effects.values():
                effects = status.get('effects', {})

                # Social stress multiplier for social activities
                if (activity['location'] in ['restaurant', 'cinema'] and
                        'social_stress_multiplier' in effects):
                    effective_stress_change *= effects['social_stress_multiplier']

                # Additional stress from activities (burnout effect)
                if 'stress_from_activities' in effects:
                    effective_stress_change += effects['stress_from_activities']

        # Final energy change
        energy_change = effective_energy_recovery - base_energy_cost

        # Location modifiers
        if activity['location'] == 'home':
            home_stress_reduction = 1
            home_paranoia_reduction = 1

            # Check for permanent cat blessing status
            if (hasattr(self.game_state, 'permanent_statuses') and
                    'cat_blessing' in self.game_state.permanent_statuses):
                cat_effects = self.game_state.permanent_statuses['cat_blessing']['effects']
                # Apply cat blessing bonuses (50% additional reduction)
                if 'home_stress_reduction' in cat_effects:
                    home_stress_reduction *= (1 + cat_effects['home_stress_reduction'] / 100)
                if 'home_paranoia_reduction' in cat_effects:
                    home_paranoia_reduction *= (1 + cat_effects['home_paranoia_reduction'] / 100)

                # Additional hourly blessing effects: -5 stress, -2 paranoia per hour at home
                duration_hours = activity['duration']
                cat_stress_reduction = 5 * duration_hours
                cat_paranoia_reduction = 2 * duration_hours

                effective_stress_change -= cat_stress_reduction
                self.game_state.paranoia = max(0, self.game_state.paranoia - cat_paranoia_reduction)

                self.game_state.add_message(
                    f"🐱✨ Кошачье благословение: -{cat_stress_reduction} стресса, -{cat_paranoia_reduction} паранойи",
                    'success')

            # Check for home invasion fear status
            for status in self.game_state.status_effects.values():
                effects = status.get('effects', {})
                if 'home_paranoia_reduction' in effects:
                    home_paranoia_reduction *= effects['home_paranoia_reduction']

            effective_stress_change -= home_stress_reduction
            self.game_state.paranoia = max(0, self.game_state.paranoia - home_paranoia_reduction)
        else:
            effective_stress_change += 2
            if self.game_state.paranoia > 40:
                self.game_state.paranoia = min(100, self.game_state.paranoia + 1)

        # 🌙 Проверка предупреждений от снов
        if hasattr(self.game_state, 'dream_warnings'):
            warnings = self.game_state.dream_warnings
            penalty_applies = False

            # Проверяем локацию
            if 'location' in warnings and warnings['location'] == activity_location:
                penalty_applies = True

            # Проверяем активность
            if 'activity' in warnings and warnings['activity'] in activity_name:
                penalty_applies = True

            if penalty_applies:
                penalty = warnings['penalty']
                self.game_state.add_message("⚠️ Сон предупреждал об этом! Дебафы применены.", 'danger')
                if 'stress' in penalty:
                    effective_stress_change += penalty['stress']
                if 'paranoia' in penalty:
                    self.game_state.paranoia = max(0, min(100, self.game_state.paranoia + penalty['paranoia']))
                if 'energy' in penalty:
                    energy_change += penalty['energy']
                print(f"⚠️ Применены дебафы от сна: {penalty}")
                # Очищаем предупреждение после применения
                delattr(self.game_state, 'dream_warnings')

        # 🌙 Проверка мотиваций от снов
        dream_bonus_applied = False
        if hasattr(self.game_state, 'dream_motivations'):
            motivations = self.game_state.dream_motivations
            bonus_applies = False

            # Проверяем локацию
            if 'location' in motivations and motivations['location'] == activity_location:
                bonus_applies = True

            # Проверяем активность
            if 'activity' in motivations and motivations['activity'] in activity_name:
                bonus_applies = True

            if bonus_applies:
                bonus = motivations['bonus']
                self.game_state.add_message("✨ Сон мотивировал вас! Бонусы применены.", 'success')
                if 'stress' in bonus:
                    effective_stress_change += bonus['stress']
                if 'energy' in bonus:
                    energy_change += bonus['energy']
                if 'paranoia' in bonus:
                    self.game_state.paranoia = max(0, min(100, self.game_state.paranoia + bonus['paranoia']))
                print(f"✨ Применены бонусы от сна: {bonus}")
                dream_bonus_applied = True
                # Очищаем мотивацию после применения
                delattr(self.game_state, 'dream_motivations')
                # Очищаем флаг проверки, так как мотивация выполнена
                if hasattr(self.game_state.dream_system, 'pending_motivation_check'):
                    self.game_state.dream_system.pending_motivation_check = False
                    print("✅ Мотивация от сна выполнена! Штрафы не будут применены.")

        # Apply changes
        old_stress = self.game_state.stress
        old_energy = self.game_state.energy

        self.game_state.energy = max(0, min(100, self.game_state.energy + energy_change))
        self.game_state.stress = max(0, min(100, self.game_state.stress + effective_stress_change))

        # 🖥️ КОНСОЛЬНЫЙ ВЫВОД: Информация о изменении стресса от активности
        if effective_stress_change != 0:
            print(
                f"📊 СТРЕСС ОТ АКТИВНОСТИ '{activity['name']}': {old_stress}→{self.game_state.stress} ({effective_stress_change:+.0f})")

        # 🚨 ОТЛАДКА: Глобальный счётчик изменений стресса для полного контроля
        if not hasattr(self.game_state, 'stress_change_log'):
            self.game_state.stress_change_log = []

        if abs(effective_stress_change) > 0.1:
            import time
            timestamp = time.time()
            self.game_state.stress_change_log.append({
                'time': self.game_state.current_time,
                'source': f'activity_{activity["name"]}',
                'change': effective_stress_change,
                'before': old_stress,
                'after': self.game_state.stress,
                'timestamp': timestamp
            })

            # 🖥️ КОНСОЛЬНЫЙ ВЫВОД: Показываем последние 3 изменения при больших изменениях
            if abs(effective_stress_change) >= 15:
                recent_changes = self.game_state.stress_change_log[-3:]
                changes_text = ' | '.join([f'{c["source"]}: {c["change"]:+.1f}' for c in recent_changes])
                print(f'🔥 БОЛЬШОЕ ИЗМЕНЕНИЕ СТРЕССА ({effective_stress_change:+.1f})!')
                print(f'📊 ПОСЛЕДНИЕ ИСТОЧНИКИ: {changes_text}')
                self.game_state.add_message(f'📊 Последние изменения стресса: {changes_text}', 'info')

        # 🚨 ОТЛАДКА: Детальное логирование изменений от активности (после записи в лог)
        if abs(effective_stress_change) > 0.1:  # Логируем только значительные изменения
            self.game_state.add_message(
                f"⚡ Активность '{activity['name']}': стресс {old_stress}→{self.game_state.stress} ({effective_stress_change:+.1f})",
                'warning' if effective_stress_change > 0 else 'success'
            )

            # Показываем детали расчета при больших изменениях
            if abs(effective_stress_change) >= 10:
                self.game_state.add_message(
                    f"📊 Расчет: базовый={raw_stress_change}, паранойя x{1 + paranoia_factor:.2f}, итог={effective_stress_change:.1f}",
                    'info'
                )

        # Check for game over conditions after applying activity effects
        if self.check_game_over_conditions():
            return

        # Record result
        result = {
            'activity': activity['name'],
            'energy_change': energy_change,
            'stress_change': effective_stress_change,
            'completed': True
        }
        self.game_state.activity_results.append(result)

        # Record activity completion for mandatory tracking
        self.game_state.record_activity_completion(activity['name'])

        # Add message with effects if enhanced
        message_suffix = ""
        if activity_multiplier > 1.0 or type_multiplier > 1.0:
            total_multiplier = activity_multiplier * type_multiplier
            message_suffix = f" (усилено картами x{total_multiplier:.1f})"
        elif paranoia_factor > 0.2:  # 20% or more paranoia
            message_suffix = " (паранойя влияет на эффект)"

        self.game_state.add_message(f"Завершено: {activity['name']}{message_suffix}", 'success')

    def check_for_events(self):
        """Check for and trigger events by exact time (постоянная проверка времени)"""
        # Check for repeat events first
        self.check_repeat_events()

        if not hasattr(self.game_state, 'daily_events') or not self.game_state.daily_events:
            return

        current_time = self.game_state.current_time

        # Проверяем все события на текущее время
        for event in self.game_state.daily_events:
            if event.get('triggered', False):
                continue

            event_time = event.get('time', 0)

            # Событие происходит когда текущее время >= времени события
            # Для ровных часов: проверяем, что текущий час соответствует часу события
            current_hour = int(current_time) if current_time == int(current_time) else int(current_time) + (
                1 if current_time > int(current_time) else 0)
            event_hour = int(event_time)

            if current_hour >= event_hour:
                event['triggered'] = True

                # Форматируем время для отображения (ровные часы)
                time_str = f"{int(event_time):02d}:00"

                # Событие активируется

                # Корректируем время на точное время события (ровный час)
                self.game_state.current_time = event_time

                # Проверяем, активен ли эффект обращения событий
                if (hasattr(self.game_state, 'event_reversal_active') and
                        self.game_state.event_reversal_active and
                        self.is_negative_event(event)):
                    # Обращаем негативное событие в позитивное
                    self.game_state.event_reversal_active = False
                    positive_event = self.reverse_event_to_positive(event)
                    # Popup уже показывается в reverse_event_to_positive
                    break

                # 🛡️ ПРЕДВАРИТЕЛЬНАЯ ЗАЩИТА: Устанавливаем защиту сразу при обнаружении события
                current_time_before_event = self.game_state.current_time

                # Показываем popup события
                self.game_state.current_event = event
                self.game_state.show_event_popup = True

                # 🛡️ УСТАНАВЛИВАЕМ ЗАЩИТУ ОТ ЛЮБЫХ СОБЫТИЙ
                # Предполагаем максимально возможное смещение времени (5 часов)
                max_time_shift = 5.0
                protection_end = min(22.0, current_time_before_event + max_time_shift)

                self.game_state.event_time_skip_start = current_time_before_event
                self.game_state.event_time_skip_end = protection_end
                self.game_state.event_time_skip_active = True

                print(
                    f"🛡️ ПРЕДВАРИТЕЛЬНАЯ ЗАЩИТА ОТ СОБЫТИЯ '{event['name']}': [{current_time_before_event:.1f}, {protection_end:.1f}]")

                # Добавляем в лог
                self.game_state.add_message(f"🎲 Событие в {time_str}: {event['name']}", 'info')
                break  # Показываем только одно событие за раз

    def check_activity_random_events(self):
        """Проверяем возможность случайного события во время выполнения активности (5% шанс)"""
        if not hasattr(self.game_state, 'daily_events') or not self.game_state.daily_events:
            return

        # 5% шанс события прямо во время активности
        if random.random() < 0.05:
            # Выбираем случайное неактивированное событие
            available_events = [event for event in self.game_state.daily_events
                                if not event.get('triggered', False)]

            if available_events:
                event = random.choice(available_events)
                event['triggered'] = True

                # ВАЖНО: Сохраняем информацию о прерванной активности
                if (hasattr(self.game_state, 'current_activity_index') and
                        self.game_state.current_activity_index < len(self.game_state.timeline)):
                    scheduled_activities = self.get_scheduled_activities()
                    if self.game_state.current_activity_index < len(scheduled_activities):
                        current_activity = scheduled_activities[self.game_state.current_activity_index]
                        # Сохраняем информацию для возобновления активности
                        self.game_state.interrupted_activity = True
                        self.game_state.activity_end_time = current_activity.end_time

                # Проверяем, активен ли эффект обращения событий
                if (hasattr(self.game_state, 'event_reversal_active') and
                        self.game_state.event_reversal_active and
                        self.is_negative_event(event)):
                    # Обращаем негативное событие в позитивное
                    self.game_state.event_reversal_active = False
                    positive_event = self.reverse_event_to_positive(event)
                    # Popup уже показывается в reverse_event_to_positive
                    return

                # 🛡️ ПРЕДВАРИТЕЛЬНАЯ ЗАЩИТА ДЛЯ СОБЫТИЙ ВО ВРЕМЯ АКТИВНОСТИ
                current_time_before_event = self.game_state.current_time

                # Показываем popup события
                self.game_state.current_event = event
                self.game_state.show_event_popup = True

                # 🛡️ УСТАНАВЛИВАЕМ ИЛИ ОБНОВЛЯЕМ ЗАЩИТУ ОТ СОБЫТИЙ ВО ВРЕМЯ АКТИВНОСТИ
                max_time_shift = 5.0
                protection_end = min(22.0, current_time_before_event + max_time_shift)

                if hasattr(self.game_state, 'activity_end_time') and self.game_state.activity_end_time:
                    # Если есть информация о конце активности, используем её
                    protection_end = max(protection_end, self.game_state.activity_end_time)

                if not hasattr(self.game_state, 'event_time_skip_active') or not self.game_state.event_time_skip_active:
                    # Первое событие - устанавливаем новую защиту
                    self.game_state.event_time_skip_start = current_time_before_event
                    self.game_state.event_time_skip_end = protection_end
                    self.game_state.event_time_skip_active = True
                    print(
                        f"🛡️ НОВАЯ ЗАЩИТА ВО ВРЕМЯ АКТИВНОСТИ: '{event['name']}' [{current_time_before_event:.1f}, {protection_end:.1f}]")
                else:
                    # Расширяем существующую защиту
                    self.game_state.event_time_skip_start = min(self.game_state.event_time_skip_start,
                                                                current_time_before_event)
                    self.game_state.event_time_skip_end = max(self.game_state.event_time_skip_end, protection_end)
                    print(
                        f"🛡️ РАСШИРЕНА ЗАЩИТА ВО ВРЕМЯ АКТИВНОСТИ: '{event['name']}' [{self.game_state.event_time_skip_start:.1f}, {self.game_state.event_time_skip_end:.1f}]")

                # Добавляем в лог
                self.game_state.add_message(f"🎲 Неожиданное событие во время активности: {event['name']}", 'info')

    def check_for_events_OLD(self):
        """Check for and trigger events after activity completion"""
        # Проверяем, есть ли события для активации после завершения активности
        if hasattr(self.game_state, 'daily_events') and self.game_state.daily_events:
            # 40% шанс активации события после каждой активности (снижено с 50%)
            if random.random() < 0.4:
                # Выбираем случайное неактивированное событие
                available_events = [event for event in self.game_state.daily_events
                                    if not event.get('triggered', False)]

                if available_events:
                    event = random.choice(available_events)
                    event['triggered'] = True

                    # Показываем popup события
                    self.game_state.current_event = event
                    self.game_state.show_event_popup = True

                    # Добавляем в лог для отслеживания
                    self.game_state.add_message(f"🎲 Случайное событие: {event['name']}", 'info')

    def get_event_choice_tooltip(self, event, choice_type):
        """Get tooltip information for event choices"""
        tooltip_info = {
            'effects': [],
            'description': ''
        }

        # Get effects from event definition
        effects = event.get('effects', {}).get(choice_type, {})

        if not effects:
            tooltip_info['effects'] = ["Без изменений"]
            tooltip_info['description'] = "Никакого эффекта"
            return tooltip_info

        # Apply paranoia multiplier to effects
        paranoia_factor = self.game_state.paranoia * 0.01

        # Calculate actual effects with paranoia influence
        actual_effects = []

        if effects.get('stress', 0) != 0:
            stress_effect = effects['stress']
            if stress_effect > 0:  # Negative effect - increased by paranoia
                actual_stress = int(stress_effect * (1 + paranoia_factor))
            else:  # Positive effect - slightly reduced by paranoia
                actual_stress = int(stress_effect * (1 - paranoia_factor * 0.3))
            actual_effects.append(f"Стресс: {actual_stress:+d}")

        if effects.get('paranoia', 0) != 0:
            paranoia_effect = effects['paranoia']
            if paranoia_effect > 0:  # Negative effect - base value
                actual_paranoia = paranoia_effect
            else:  # Positive effect - base value
                actual_paranoia = paranoia_effect
            actual_effects.append(f"Паранойя: {actual_paranoia:+d}")

        if effects.get('energy', 0) != 0:
            energy_effect = effects['energy']
            if energy_effect > 0:  # Positive effect - base value
                actual_energy = energy_effect
            else:  # Negative effect (energy cost) - increased by paranoia
                actual_energy = int(energy_effect * (1 + paranoia_factor))
            actual_effects.append(f"Энергия: {actual_energy:+d}")

        # Add time cost for time solutions
        if choice_type == 'time_solution':
            # Calculate time cost based on original severity concept
            original_severity = max(1, (abs(effects.get('stress', 5)) + abs(effects.get('paranoia', 2))) // 5)
            time_cost = original_severity * 0.5
            actual_effects.append(f"Время: +{time_cost:.1f}ч")

        tooltip_info['effects'] = actual_effects

        # Set descriptions based on choice type
        if choice_type == 'acknowledge':
            tooltip_info['description'] = "Получите пользу от хорошего события"
        elif choice_type == 'accept':
            tooltip_info['description'] = "Принять предложение"
        elif choice_type == 'decline':
            tooltip_info['description'] = "Отклонить предложение"
        elif choice_type == 'ignore':
            tooltip_info['description'] = "Игнорирование проблемы усугубляет её"
        elif choice_type == 'energy_solution':
            tooltip_info['description'] = "Активное решение проблемы, но затратное"
        elif choice_type == 'time_solution':
            tooltip_info['description'] = "Осторожное решение, но требует времени"

        return tooltip_info

    def get_event_button_labels(self, event_name):
        """Get context-specific button labels for events"""
        button_configs = {
            'Сильный дождь': {
                'ignore': 'Идти под дождём',
                'energy': 'Вызвать такси',
                'time': 'Переждать дома'
            },
            'Пробки': {
                'ignore': 'Ехать как есть',
                'energy': 'Бежать пешком',
                'time': 'Объехать окружной'
            },
            'Отключение света': {
                'ignore': 'Сидеть в темноте',
                'energy': 'Попытаться починить самому',
                'time': 'Ждать включения'
            },
            'Поломка техники': {
                'ignore': 'Обойтись без него',
                'energy': 'Срочно чинить',
                'time': 'Искать замену'
            },
            'Магазин закрыт': {
                'ignore': 'Остаться без покупки',
                'energy': 'Искать другой магазин',
                'time': 'Прийти позже'
            },
            'Подозрительный человек': {
                'ignore': 'Игнорировать его',
                'energy': 'Поговорить с ним',
                'time': 'Уйти обходным путём'
            },
            'Тревожные новости': {
                'ignore': 'Не обращать внимания',
                'energy': 'Разобраться в ситуации',
                'time': 'Отключить новости'
            },
            'Странная тень': {
                'ignore': 'Продолжать идти',
                'energy': 'Активно искать источник',
                'time': 'Осторожно осмотреться'
            },
            'Незнакомка следит': {
                'ignore': 'Делать вид, что не замечаете',
                'energy': 'Подойти и спросить прямо',
                'time': 'Уйти окольными путями'
            },
            'Предмет переставлен': {
                'ignore': 'Просто переставить обратно',
                'energy': 'Тщательно проверить дом',
                'time': 'Осторожно всё обследовать'
            }
        }

        return button_configs.get(event_name, {
            'ignore': 'Игнорировать',
            'energy': 'Действовать активно',
            'time': 'Действовать осторожно'
        })

    def process_event(self, event, choice="ignore"):
        """Process an environmental event with player choice"""
        # Check for universal protection
        if (hasattr(self.game_state, 'universal_protection_active') and
                self.game_state.universal_protection_active):
            self.game_state.universal_protection_active = False
            self.game_state.add_message(f"Универсальная защита поглотила событие: {event['name']}", 'success')
            return

        # Check for category-specific protection
        event_category = event.get('category', '')
        category_protections = {
            'social': 'social_protection_active',
            'technical': 'technical_protection_active',
            'weather': 'weather_protection_active'
        }

        if event_category in category_protections:
            protection_attr = category_protections[event_category]
            if hasattr(self.game_state, protection_attr) and getattr(self.game_state, protection_attr):
                setattr(self.game_state, protection_attr, False)
                self.game_state.add_message(f"Защита от {event_category} событий поглотила: {event['name']}", 'success')
                return

        # Get effects from event definition
        effects = event.get('effects', {}).get(choice, {})

        if not effects:
            self.game_state.add_message(f"{event['name']}: Никакого эффекта", 'info')
            return

        # Store original effects for potential undo
        original_effects = effects.copy()

        # Apply paranoia multiplier to effects
        paranoia_factor = self.game_state.paranoia * 0.01

        # Track changes for message and undo functionality
        changes = []
        applied_effects = {}

        # Apply stress changes
        if effects.get('stress', 0) != 0:
            stress_effect = effects['stress']

            # Check for stress protection
            if (stress_effect > 0 and hasattr(self.game_state, 'stress_protection_active') and
                    self.game_state.stress_protection_active):
                self.game_state.stress_protection_active = False
                self.game_state.add_message("Защита от стресса поглотила негативный эффект!", 'success')
                stress_effect = 0

            if stress_effect != 0:
                if stress_effect > 0:  # Negative effect - increased by paranoia
                    actual_stress = int(stress_effect * (1 + paranoia_factor))
                else:  # Positive effect - slightly reduced by paranoia
                    actual_stress = int(stress_effect * (1 - paranoia_factor * 0.3))

                # Apply status effects if available
                if hasattr(self.game_state, 'apply_status_effects_to_value'):
                    if actual_stress > 0:
                        actual_stress = int(
                            self.game_state.apply_status_effects_to_value('stress', actual_stress, True))
                    else:
                        actual_stress = int(
                            self.game_state.apply_status_effects_to_value('stress', actual_stress, False))

                self.game_state.stress = max(0, min(100, self.game_state.stress + actual_stress))
                changes.append(f"{actual_stress:+d} стресса")
                applied_effects['stress'] = actual_stress

        # Apply paranoia changes
        if effects.get('paranoia', 0) != 0:
            paranoia_effect = effects['paranoia']

            # Apply status effects if available
            if hasattr(self.game_state, 'apply_status_effects_to_value'):
                if paranoia_effect > 0:
                    paranoia_effect = int(
                        self.game_state.apply_status_effects_to_value('paranoia', paranoia_effect, True))
                else:
                    paranoia_effect = int(
                        self.game_state.apply_status_effects_to_value('paranoia', paranoia_effect, False))

            self.game_state.paranoia = max(0, min(100, self.game_state.paranoia + paranoia_effect))
            changes.append(f"{paranoia_effect:+d} паранойи")
            applied_effects['paranoia'] = paranoia_effect

        # Apply energy changes
        if effects.get('energy', 0) != 0:
            energy_effect = effects['energy']
            if energy_effect < 0:  # Energy cost - increased by paranoia
                actual_energy = int(energy_effect * (1 + paranoia_factor))

                # Apply status effects if available
                if hasattr(self.game_state, 'apply_status_effects_to_value'):
                    actual_energy = int(
                        self.game_state.apply_status_effects_to_value('energy_cost', abs(actual_energy), False))
                    actual_energy = -actual_energy  # Make it negative again
            else:  # Energy gain - base value
                actual_energy = energy_effect

                # Apply status effects if available
                if hasattr(self.game_state, 'apply_status_effects_to_value'):
                    actual_energy = int(
                        self.game_state.apply_status_effects_to_value('energy_recovery', actual_energy, False))

            self.game_state.energy = max(0, min(100, self.game_state.energy + actual_energy))
            changes.append(f"{actual_energy:+d} энергии")
            applied_effects['energy'] = actual_energy

        # Apply time cost for time solutions
        if choice == 'time_solution':
            # Calculate time cost based on effect severity
            stress_severity = abs(effects.get('stress', 0))
            paranoia_severity = abs(effects.get('paranoia', 0))
            time_cost = max(0.5, (stress_severity + paranoia_severity) // 10 * 0.5)

            # 🛡️ ОБНОВЛЕННАЯ ЗАЩИТА: Пропуск времени от time_solution
            time_before = self.game_state.current_time
            time_after = self.game_state.current_time + time_cost

            # Обновляем или устанавливаем флаги защиты
            if not hasattr(self.game_state, 'event_time_skip_active') or not self.game_state.event_time_skip_active:
                # Первое событие - устанавливаем новую защиту
                self.game_state.event_time_skip_start = time_before
                self.game_state.event_time_skip_end = time_after
                self.game_state.event_time_skip_active = True
                print(f"🛡️ НОВАЯ ЗАЩИТА: time_solution [{time_before:.1f}, {time_after:.1f}]")
            else:
                # Расширяем существующую защиту
                self.game_state.event_time_skip_start = min(self.game_state.event_time_skip_start, time_before)
                self.game_state.event_time_skip_end = max(self.game_state.event_time_skip_end, time_after)
                print(
                    f"🛡️ РАСШИРЕНА ЗАЩИТА: time_solution [{self.game_state.event_time_skip_start:.1f}, {self.game_state.event_time_skip_end:.1f}]")

            self.game_state.current_time += time_cost
            changes.append(f"+{time_cost:.1f}ч времени")
            applied_effects['time_cost'] = time_cost

        # Store effects for potential undo
        self.game_state.last_event_effects = applied_effects

        # Apply status effects from event if specified
        if effects.get('status'):
            status_id = effects['status']
            self.apply_positive_status(status_id)
            changes.append(f"Получен статус: {status_id}")

        # Apply paranoia-related status effects for specific events when ignored
        if choice == 'ignore':
            self.apply_paranoia_status_from_event(event)

        # Generate appropriate message based on choice type
        message_type = 'info'
        action_text = ""

        if choice == 'acknowledge':
            action_text = "Отлично!"
            message_type = 'success'
        elif choice == 'accept':
            action_text = "Принято:"
            message_type = 'success'
        elif choice == 'decline':
            action_text = "Отклонено:"
            message_type = 'info'
        elif choice == 'ignore':
            action_text = "Проигнорировано:"
            message_type = 'warning'
        elif choice == 'energy_solution':
            action_text = "Решено энергично:"
            message_type = 'warning'
        elif choice == 'time_solution':
            action_text = "Решено осторожно:"
            message_type = 'info'

        # Build message
        if changes:
            changes_text = " (" + ", ".join(changes) + ")"
        else:
            changes_text = ""

        self.game_state.add_message(f"{action_text} {event['name']}{changes_text}", message_type)

        # Handle series event progression
        self.handle_series_progression(event, choice)

        # Check for game over after processing any event
        if self.check_game_over_conditions():
            return

        # 🖥️ КОНСОЛЬНЫЙ ВЫВОД: Показываем статус защиты
        if choice == 'time_solution' and hasattr(self.game_state, 'event_time_skip_active'):
            print(
                f"🛡️ ЗАЩИТА ОТ СТРЕССА АКТИВНА: {self.game_state.event_time_skip_start:.1f} -> {self.game_state.event_time_skip_end:.1f}")
        else:
            print(f"📊 Обычное событие: {choice} (защита не нужна)")

    def handle_series_progression(self, event, choice):
        """Handle progression in event series based on player choice"""
        series = event.get('series')
        if not series:
            return

        # Determine if this is a positive choice (acceptance)
        positive_choices = ['accept', 'acknowledge', 'energy_solution', 'time_solution']
        is_positive_choice = choice in positive_choices

        # If only one choice available, always progress (for notification type events)
        event_type = event.get('type', 'choice')
        is_single_choice = event_type == 'notification'

        if is_positive_choice or is_single_choice:
            # Advance the series
            current_progress = self.game_state.event_series_progress.get(series, 0)
            current_order = event.get('series_order', 1)

            # Only advance if this is the current expected event
            if current_order == current_progress + 1:
                self.game_state.event_series_progress[series] = current_order

                # Check if this is the last event in the cats series (order 4)
                if series == 'cats' and current_order == 4:
                    # Give permanent cat blessing status
                    self.give_cat_blessing()
                    # Mark series as completed to prevent repetition
                    self.game_state.event_series_completed.add('cats')
                    self.game_state.add_message(
                        "🐱✨ Вы получили кошачье благословение! Коты навсегда стали вашими друзьями.", 'success')

                # Check if this is the last event in the stalker series (order 4) with positive choice
                elif series == 'stalker' and current_order == 4 and is_positive_choice:
                    # Give permanent doubt status only for positive choices (acknowledge for notification events)
                    self.give_doubt_status()
                    # Mark series as completed to prevent repetition
                    self.game_state.event_series_completed.add('stalker')
                    self.game_state.add_message(
                        "💭 Встреча с незнакомкой заставила вас усомниться в своих отношениях с голосом...", 'warning')

                # Mark series as completed if this was the final event
                max_orders = {
                    'cats': 4,
                    'stalker': 4
                }
                if current_order >= max_orders.get(series, 4):
                    self.game_state.event_series_completed.add(series)
        else:
            # Negative choice - schedule event for repeat
            self.schedule_event_repeat(event)

    def schedule_event_repeat(self, event):
        """Schedule an event to repeat later if player declined it"""
        if not hasattr(self.game_state, 'pending_repeat_events'):
            self.game_state.pending_repeat_events = []

        # Create a copy for repeat with random delay
        repeat_event = event.copy()
        repeat_event['triggered'] = False
        repeat_event['repeat_delay'] = random.uniform(2, 5)  # 2-5 hours delay
        repeat_event['scheduled_time'] = self.game_state.current_time + repeat_event['repeat_delay']

        self.game_state.pending_repeat_events.append(repeat_event)

    def check_repeat_events(self):
        """Check if any repeat events should trigger"""
        if not hasattr(self.game_state, 'pending_repeat_events'):
            return

        current_time = getattr(self.game_state, 'current_time', 8.0)
        events_to_trigger = []

        for event in self.game_state.pending_repeat_events:
            if current_time >= event['scheduled_time']:
                events_to_trigger.append(event)

        # Remove triggered events from pending and show them
        for event in events_to_trigger:
            self.game_state.pending_repeat_events.remove(event)

            # Show the repeat event immediately
            self.game_state.current_event = event
            self.game_state.show_event_popup = True
            self.game_state.add_message(f"🔄 Повторное событие: {event['name']}", 'info')
            break  # Show only one at a time

    def give_cat_blessing(self):
        """Give permanent cat blessing status"""
        if not hasattr(self.game_state, 'permanent_statuses'):
            self.game_state.permanent_statuses = {}

        self.game_state.permanent_statuses['cat_blessing'] = {
            'name': 'Кошачье благословение',
            'description': 'Коты дарят вам умиротворение и защиту от тревог',
            'icon': '🐱✨',
            'effects': {
                'home_stress_reduction': 50,  # 50% доп. снижение стресса дома
                'home_paranoia_reduction': 50  # 50% доп. снижение паранойи дома
            },
            'permanent': True
        }

    def give_doubt_status(self):
        """Give permanent doubt status after positive stranger encounter"""
        if not hasattr(self.game_state, 'permanent_statuses'):
            self.game_state.permanent_statuses = {}

        self.game_state.permanent_statuses['doubt'] = {
            'name': 'Сомнения',
            'description': 'Встреча с незнакомкой заставила вас усомниться в своих отношениях с голосом',
            'icon': '💭',
            'effects': {
                'voice_relationship_reduction': 50,  # -50% к получаемым отношениям с голосом
                'voice_paranoia_reduction': 50  # -50% к паранойе от невыполненных заданий голоса
            },
            'permanent': True
        }

    def apply_doubt_effects_to_voice_relationship(self, relationship_change):
        """Apply doubt status effects to voice relationship changes"""
        if (hasattr(self.game_state, 'permanent_statuses') and
                self.game_state.permanent_statuses and
                'doubt' in self.game_state.permanent_statuses):
            # Reduce relationship changes by 50% (works for both positive and negative values)
            original_change = relationship_change
            # For positive values: reduce gains, for negative values: reduce penalties (make them less harsh)
            relationship_change = int(relationship_change * 0.5)
            print(f"💭 Сомнения снижают влияние голоса: {original_change} → {relationship_change}")
        return relationship_change

    def apply_doubt_effects_to_voice_paranoia(self, paranoia_change):
        """Apply doubt status effects to paranoia from unfulfilled voice tasks"""
        if (hasattr(self.game_state, 'permanent_statuses') and
                self.game_state.permanent_statuses and
                'doubt' in self.game_state.permanent_statuses):
            # Reduce paranoia from voice tasks by 50%
            original_change = paranoia_change
            paranoia_change = int(paranoia_change * 0.5)
            print(f"💭 Сомнения снижают паранойю от голоса: {original_change} → {paranoia_change}")
        return paranoia_change

    def is_negative_event(self, event):
        """Проверяем, является ли событие негативным"""
        # Негативные события - те, которые наносят вред
        negative_event_names = [
            'Сильный дождь', 'Пробки', 'Отключение света', 'Поломка техники',
            'Магазин закрыт', 'Подозрительный человек', 'Тревожные новости',
            'Странная тень', 'Незнакомка следит', 'Предмет переставлен'
        ]

        event_name = event.get('name', '')
        return event_name in negative_event_names

    def reverse_event_to_positive(self, event):
        """Convert a negative event into a random positive one and show popup"""
        # Список позитивных событий для замены (включая новые со статусами)
        positive_events = [
            # Обычные позитивные события
            {
                'name': 'Отличная погода',
                'icon': '☀️',
                'category': 'weather',
                'type': 'notification',
                'effects': {
                    'acknowledge': {'stress': -12, 'paranoia': -3, 'energy': 10}
                }
            },
            {
                'name': 'Неожиданная скидка',
                'icon': '💰',
                'category': 'economic',
                'type': 'notification',
                'effects': {
                    'acknowledge': {'stress': -10, 'paranoia': -4, 'energy': -5}
                }
            },
            {
                'name': 'Хорошие новости',
                'icon': '📺',
                'category': 'information',
                'type': 'notification',
                'effects': {
                    'acknowledge': {'stress': -10, 'paranoia': -5, 'energy': 8}
                }
            },
            {
                'name': 'Встреча со старым другом',
                'icon': '👋',
                'category': 'social',
                'type': 'notification',
                'effects': {
                    'acknowledge': {'stress': -15, 'paranoia': -8, 'energy': -5}
                }
            },
            # Новые события с позитивными статусами
            {
                'name': 'Вдохновляющая книга',
                'icon': '📚',
                'category': 'inspiration',
                'type': 'notification',
                'effects': {
                    'acknowledge': {'stress': -8, 'paranoia': -5, 'energy': -3, 'status': 'inspired'}
                }
            },
            {
                'name': 'Мотивирующий фильм',
                'icon': '🎥',
                'category': 'inspiration',
                'type': 'notification',
                'effects': {
                    'acknowledge': {'stress': -10, 'paranoia': -3, 'energy': 5, 'status': 'inspired'}
                }
            },
            {
                'name': 'Успешная медитация',
                'icon': '🧘',
                'category': 'wellness',
                'type': 'notification',
                'effects': {
                    'acknowledge': {'stress': -12, 'paranoia': -8, 'energy': -5, 'status': 'focused'}
                }
            },
            {
                'name': 'Похвала от коллеги',
                'icon': '👏',
                'category': 'social',
                'type': 'notification',
                'effects': {
                    'acknowledge': {'stress': -10, 'paranoia': -5, 'energy': 8, 'status': 'confident'}
                }
            },
            {
                'name': 'Отличный сон',
                'icon': '😴',
                'category': 'wellness',
                'type': 'notification',
                'effects': {
                    'acknowledge': {'stress': -15, 'paranoia': -5, 'energy': 20, 'status': 'energized'}
                }
            }
        ]

        # Выбираем случайное позитивное событие
        positive_event = random.choice(positive_events)

        # Сохраняем старое название для сообщения
        old_name = event['name']

        # Заменяем событие на позитивное и показываем popup
        self.game_state.current_event = positive_event
        self.game_state.show_event_popup = True

        # Добавляем сообщение о замене
        self.game_state.add_message(f"🌀 Контроль хаоса! '{old_name}' заменено на '{positive_event['name']}'", 'success')

        return positive_event

    def apply_paranoia_status_from_event(self, event):
        """Apply paranoia-related status effects when certain events are ignored"""
        event_name = event['name']

        # Define events that can trigger paranoia statuses when ignored
        paranoia_events = {
            'Подозрительный человек': {
                'status_id': 'stalked_feeling',
                'name': 'Ощущение слежки',
                'icon': '👁️',
                'description': 'Кажется, что за вами следят. Увеличен урон паранойи от событий на 25%',
                'duration': 6.0,
                'effects': {'paranoia_vulnerability': 1.25}
            },
            'Тревожные новости': {
                'status_id': 'information_anxiety',
                'name': 'Информационная тревога',
                'icon': '📺',
                'description': 'Постоянные тревожные мысли о новостях. +3 стресса и +2 паранойи каждый час',
                'duration': 6.0,
                'effects': {'hourly_stress': 3, 'hourly_paranoia': 2}
            },
            'Незнакомка следит': {
                'status_id': 'surveillance_paranoia',
                'name': 'Паранойя слежки',
                'icon': '🕵️',
                'description': 'Постоянное чувство наблюдения. Социальные активности вызывают +50% стресса',
                'duration': 6.0,
                'effects': {'social_stress_multiplier': 1.5}
            },
            'Странная тень': {
                'status_id': 'shadow_paranoia',
                'name': 'Теневая паранойя',
                'icon': '👥',
                'description': 'Мерещатся тени в периферическом зрении. Все негативные события на 30% сильнее',
                'duration': 6.0,
                'effects': {'negative_event_multiplier': 1.3}
            },
            'Предмет переставлен': {
                'status_id': 'home_invasion_fear',
                'name': 'Страх вторжения',
                'icon': '🏠',
                'description': 'Боязнь, что кто-то проникает в дом. Домашние активности дают меньше спокойствия',
                'duration': 6.0,
                'effects': {'home_paranoia_reduction': 0.5}
            },
            'Поломка техники': {
                'status_id': 'tech_sabotage_fear',
                'name': 'Страх саботажа',
                'icon': '💻',
                'description': 'Подозрение что технику намеренно портят. +25% урона от технических событий',
                'duration': 6.0,
                'effects': {'tech_event_multiplier': 1.25}
            }
        }

        # Check if this event can trigger a paranoia status
        if event_name in paranoia_events:
            status_config = paranoia_events[event_name]

            # Always apply status if not already active
            if status_config['status_id'] not in self.game_state.status_effects:
                # Apply the paranoia status
                self.game_state.add_status_effect(
                    status_config['status_id'],
                    status_config['name'],
                    status_config['icon'],
                    status_config['description'],
                    status_config['duration'],
                    condition_check=None,  # These are time-based, not condition-based
                    effects=status_config['effects']
                )

                self.game_state.add_message(
                    f"🧠 Получен статус: {status_config['name']}", 'danger'
                )

    def get_voice_state(self):
        """Get current inner voice state based on mental condition"""
        # Check if voice is silenced
        if (hasattr(self.game_state, 'voice_silenced_until') and
                self.game_state.voice_silenced_until > self.game_state.day):
            return {
                'message': '...',
                'color': COLORS['text_dim']
            }

        stress = self.game_state.stress
        paranoia = self.game_state.paranoia
        energy = self.game_state.energy
        relationship = self.game_state.inner_voice_relationship

        if relationship >= 30 and stress < 40:
            return {
                'message': 'Ты хорошо справляешься! Может стоит добавить что-то приятное в планы?',
                'color': COLORS['success']
            }
        elif relationship < -20 or paranoia > 60:
            return {
                'message': 'Опять всё делаешь неправильно... Лучше бы просто остался дома.',
                'color': COLORS['danger']
            }
        elif stress > 70:
            return {
                'message': 'Столько стресса! Нужно что-то менять в планах, иначе будет только хуже.',
                'color': COLORS['warning']
            }
        elif energy < 30:
            return {
                'message': 'Энергии совсем нет... Может пересмотреть активности на что-то более спокойное?',
                'color': COLORS['warning']
            }
        else:
            return {
                'message': 'День как день. Ничего особенного. Главное - не испортить то, что уже запланировано.',
                'color': COLORS['text']
            }

    def listen_to_voice(self):
        """Listen to inner voice advice - WITH INDIVIDUAL BUTTON PROTECTION"""
        if not self.can_click_button('listen_voice'):
            return

        # Check if voice system is unlocked
        if self.game_state.day < 3:
            self.game_state.add_message("Система внутреннего голоса ещё не активна", 'warning')
            return

        # Check daily interaction limit
        if self.game_state.daily_voice_interactions >= self.game_state.max_daily_voice_interactions:
            self.game_state.add_message(
                f"Вы уже достаточно общались с голосом сегодня ({self.game_state.max_daily_voice_interactions}/3)",
                'warning')
            return

        self.register_button_click('listen_voice')
        self.game_state.daily_voice_interactions += 1

        # Improve relationship slightly (with doubt effect if applicable)
        relationship_change = self.apply_doubt_effects_to_voice_relationship(5)
        self.game_state.inner_voice_relationship = min(100,
                                                       self.game_state.inner_voice_relationship + relationship_change)

        # Random outcome (50/50 chance)
        if random.random() < 0.5:
            # Good outcome: stress relief but slight paranoia
            self.game_state.stress = max(0, self.game_state.stress - 10)
            self.game_state.paranoia = min(100, self.game_state.paranoia + 5)
            effect = "голос успокоил вас, но какое-то странное чувство осталось..."
            message_type = 'warning'
        else:
            # Bad outcome: disturbing truth
            self.game_state.paranoia = min(100, self.game_state.paranoia + 10)
            self.game_state.stress = min(100, self.game_state.stress + 5)
            effect = "голос открыл вам страшную правду, вы были не готовы"
            message_type = 'danger'

        self.game_state.voice_history.append(f"Выслушали голос - {effect}")
        self.game_state.add_message(f"Внутренний голос: {effect}", message_type)

        # Check for game over after voice interaction
        if self.check_game_over_conditions():
            return

    def argue_with_voice(self):
        """Argue with inner voice - WITH INDIVIDUAL BUTTON PROTECTION"""
        if not self.can_click_button('argue_voice'):
            return

        # Check if voice system is unlocked
        if self.game_state.day < 3:
            self.game_state.add_message("Система внутреннего голоса ещё не активна", 'warning')
            return

        # Check daily interaction limit
        if self.game_state.daily_voice_interactions >= self.game_state.max_daily_voice_interactions:
            self.game_state.add_message(
                f"Вы уже достаточно общались с голосом сегодня ({self.game_state.max_daily_voice_interactions}/3)",
                'warning')
            return

        self.register_button_click('argue_voice')
        self.game_state.daily_voice_interactions += 1

        # Significantly worsen relationship
        self.game_state.inner_voice_relationship = max(-100, self.game_state.inner_voice_relationship - 8)

        # Random outcome (50/50 chance)
        if random.random() < 0.5:
            # Good outcome: satisfying victory but exhausting
            self.game_state.stress = max(0, self.game_state.stress - 10)
            self.game_state.paranoia = max(0, self.game_state.paranoia - 8)
            self.game_state.energy = max(0, self.game_state.energy - 12)
            effect = "вы чувствуете удовлетворение от победы, но споры истощили вас"
            message_type = 'warning'
        else:
            # Bad outcome: obsessive thoughts
            self.game_state.stress = min(100, self.game_state.stress + 12)
            self.game_state.paranoia = min(100, self.game_state.paranoia + 10)
            effect = "теперь назойливые мысли не покидают вас и вы прокручиваете этот спор из раза в раз"
            message_type = 'danger'

        self.game_state.voice_history.append(f"Поспорили с голосом - {effect}")
        self.game_state.add_message(f"Спор с внутренним голосом: {effect}", message_type)

        # Check for game over after voice interaction
        if self.check_game_over_conditions():
            return

    def use_card(self, card):
        """Use a specific card"""
        if not card['available'] or self.game_state.card_points < card['cost']:
            self.game_state.add_message("Недостаточно очков для использования карты", 'warning')
            return

        self.game_state.card_points -= card['cost']

        if card['name'] == 'Карта энергии':
            self.game_state.energy = min(100, self.game_state.energy + 30)
            self.game_state.add_message("Карта энергии: +30 энергии", 'success')

        elif card['name'] == 'Карта спокойствия':
            self.game_state.stress = max(0, self.game_state.stress - 25)
            self.game_state.add_message("Карта спокойствия: -25 стресса", 'success')

        elif card['name'] == 'Карта удачи':
            # Set temporary luck effect
            self.game_state.luck_active = True
            self.game_state.add_message("Карта удачи активна: события будут мягче", 'success')

        elif card['name'] == 'Карта защиты':
            self.game_state.protection_active = True
            self.game_state.add_message("Карта защиты активна: следующее событие не причинит стресса", 'success')

        elif card['name'] == 'Карта фокуса':
            self.game_state.focus_active = True
            self.game_state.add_message("Карта фокуса активна: активности будут эффективнее", 'success')

        elif card['name'] == 'Карта времени':
            # Allow one-time activity rearrangement
            self.game_state.time_card_active = True
            self.game_state.add_message("Карта времени активна: можно переместить одну активность", 'success')

    def end_day(self):
        """End the current day and show results"""
        self.game_state.phase = 'results'

        # Store task statistics for voice message
        task_statistics = {
            'completed_tasks': [],
            'failed_tasks': [],
            'total_card_points_earned': 0,
            'total_relationship_gained': 0,
            'total_relationship_lost': 0,
            'total_paranoia_penalty': 0  # 🚨 ИСПРАВЛЕНИЕ: паранойя вместо стресса
        }

        # Automatically check all voice tasks for completion at end of day (only if voice system unlocked)
        if self.game_state.day >= 3 and hasattr(self.game_state, 'voice_tasks'):
            if not hasattr(self.game_state, 'completed_voice_tasks'):
                self.game_state.completed_voice_tasks = []

            for task in self.game_state.voice_tasks:
                if task['id'] not in self.game_state.completed_voice_tasks:
                    # For tasks that require task context, pass the task itself to the check function
                    task_completed = False
                    try:
                        if task['id'].startswith('specific_time_') or task['id'].startswith('avoid_'):
                            task_completed = task['check'](self.game_state, task)
                        else:
                            task_completed = task['check'](self.game_state)
                    except TypeError:
                        # Fallback for tasks that don't expect task parameter
                        task_completed = task['check'](self.game_state)

                    if task_completed:
                        # Task completed automatically!
                        self.game_state.completed_voice_tasks.append(task['id'])
                        task_statistics['completed_tasks'].append(task)

                        # Give rewards
                        reward = task['reward']
                        card_points_reward = reward.get('card_points', 0)
                        relationship_reward = reward.get('voice_relationship', 0)

                        # Apply doubt effects to relationship reward
                        effective_relationship_reward = self.apply_doubt_effects_to_voice_relationship(
                            relationship_reward)

                        self.game_state.card_points += card_points_reward
                        self.game_state.inner_voice_relationship += effective_relationship_reward

                        # Track for statistics
                        task_statistics['total_card_points_earned'] += card_points_reward
                        task_statistics['total_relationship_gained'] += effective_relationship_reward

                        self.game_state.add_message(
                            f"🎯 Задание выполнено: {task['name']} (+{card_points_reward} очков карт, +{effective_relationship_reward} отношений)",
                            'success')
                        self.game_state.voice_history.append(f"Выполнили задание: {task['name']}")
                    else:
                        # Task failed - apply penalties
                        task_statistics['failed_tasks'].append(task)

            # Apply penalties for failed tasks
            for failed_task in task_statistics['failed_tasks']:
                reward = failed_task['reward']

                # 🚨 ИСПРАВЛЕНИЕ: Penalty is proportional to the reward - ПАРАНОЙЯ вместо стресса
                relationship_penalty = -abs(reward.get('voice_relationship', 5))
                # Меньшее наказание паранойей вместо стресса (1-3 паранойи вместо 3-6 стресса)
                paranoia_penalty = max(1, abs(reward.get('card_points', 1)) * 1)  # 1-3 paranoia per failed task

                # Apply doubt effects to voice-related paranoia and relationship penalties
                effective_paranoia_penalty = self.apply_doubt_effects_to_voice_paranoia(paranoia_penalty)
                effective_relationship_penalty = self.apply_doubt_effects_to_voice_relationship(relationship_penalty)

                self.game_state.inner_voice_relationship = max(-100,
                                                               self.game_state.inner_voice_relationship + effective_relationship_penalty)
                self.game_state.paranoia = min(100, self.game_state.paranoia + effective_paranoia_penalty)

                # Track for statistics
                task_statistics['total_relationship_lost'] += abs(effective_relationship_penalty)
                # Переименовываем статистику
                if 'total_paranoia_penalty' not in task_statistics:
                    task_statistics['total_paranoia_penalty'] = 0
                task_statistics['total_paranoia_penalty'] += effective_paranoia_penalty

                self.game_state.add_message(
                    f"❌ Задание провалено: {failed_task['name']} ({effective_relationship_penalty} отношений, +{effective_paranoia_penalty} паранойи)",
                    'danger')
                self.game_state.voice_history.append(f"Провалили задание: {failed_task['name']}")

        # Calculate day completion bonus (only if voice system is unlocked - день 3+)
        if self.game_state.day >= 3:
            completion_bonus = 0

            # Mental state bonuses
            if self.game_state.stress < 30:
                completion_bonus += 1
                self.game_state.add_message("Бонус за низкий стресс: +1 очко", 'success')

            if self.game_state.energy > 50:
                if self.game_state.energy > 70:
                    completion_bonus += 1
                    self.game_state.add_message("Бонус за отличную энергию: +1 очко", 'success')

            self.game_state.card_points += completion_bonus

        # 🌙 Проверка выполнения мотивирующих снов
        if (hasattr(self.game_state.dream_system, 'pending_motivation_check') and
                self.game_state.dream_system.pending_motivation_check):

            # Проверяем, была ли выполнена мотивация
            if hasattr(self.game_state, 'dream_motivations'):
                # Мотивация не была выполнена - применяем штраф
                motivations = self.game_state.dream_motivations
                penalty = motivations['penalty_if_not_done']

                if 'stress' in penalty:
                    self.game_state.stress = max(0, min(100, self.game_state.stress + penalty['stress']))
                if 'paranoia' in penalty:
                    self.game_state.paranoia = max(0, min(100, self.game_state.paranoia + penalty['paranoia']))
                if 'energy' in penalty:
                    self.game_state.energy = max(0, min(100, self.game_state.energy + penalty['energy']))

                self.game_state.add_message("⚠️ Вы не послушались вдохновляющего сна! Штрафы применены.", 'danger')
                print(f"⚠️ Не выполнена мотивация от сна: {penalty}")

                # Очищаем мотивацию
                delattr(self.game_state, 'dream_motivations')

            # Сбрасываем флаг
            self.game_state.dream_system.pending_motivation_check = False

        # Очищаем предупреждения от снов (если остались)
        if hasattr(self.game_state, 'dream_warnings'):
            delattr(self.game_state, 'dream_warnings')

        # Generate status effects summary for the day
        status_summary = self.generate_status_effects_summary()

        # Show voice message popup (for any day with voice system)
        if self.game_state.day >= 1:
            voice_message = self.game_state.generate_voice_end_day_message()
            if voice_message and self.game_state.day >= 3:  # Add task statistics only if voice system is active
                voice_message['task_statistics'] = task_statistics
            # Add status effects summary to voice message
            voice_message['status_summary'] = status_summary
            self.game_state.current_voice_message = voice_message
            self.game_state.show_voice_message_popup = True

        self.game_state.add_message("День завершен!", 'success')

        # Apply overnight recovery with paranoia penalty
        base_recovery = 40

        # Paranoia reduces energy recovery (0-50% reduction based on paranoia level)
        paranoia_penalty = (self.game_state.paranoia / 100) * 0.5  # 0% to 50% reduction
        effective_recovery = int(base_recovery * (1 - paranoia_penalty))

        self.game_state.energy = min(100, self.game_state.energy + effective_recovery)

        # High stress still affects recovery
        if self.game_state.stress > 70:
            self.game_state.energy = max(0, self.game_state.energy - 10)

        # Reset daily card usage (no longer needed since cards are removed)
        if hasattr(self.game_state, 'used_cards'):
            self.game_state.used_cards = []

        # Reset daily card effects
        card_effects_to_reset = [
            'luck_active', 'protection_active', 'focus_active', 'time_card_active',
            'energy_shield', 'next_activity_multiplier', 'motivation_boost_active',
            'motivation_multiplier', 'activity_move_uses', 'event_reversal_active',
            'universal_protection_active', 'stress_protection_active',
            'social_protection_active', 'technical_protection_active', 'weather_protection_active',
            'social_activities_bonus', 'physical_activities_bonus', 'mental_activities_bonus',
            'energy_efficiency', 'productivity_bonus', 'action_bonus'
        ]

        for effect in card_effects_to_reset:
            if hasattr(self.game_state, effect):
                delattr(self.game_state, effect)

        # Update activity adaptation based on today's usage
        used_activity_names = [result['activity'] for result in self.game_state.activity_results]
        self.game_state.update_activity_adaptation(used_activity_names)

    def generate_status_effects_summary(self):
        """Generate a summary of status effects that were active during the day"""
        if not hasattr(self.game_state, 'status_effects') or not self.game_state.status_effects:
            return {'active_count': 0, 'effects_list': [], 'impact_summary': 'Никаких статусов не было активно'}

        active_effects = list(self.game_state.status_effects.values())

        # Categorize effects
        positive_effects = []
        negative_effects = []

        for effect in active_effects:
            if any(word in effect['name'].lower() for word in ['прилив', 'спокойствие', 'фокус']):
                positive_effects.append(effect['name'])
            else:
                negative_effects.append(effect['name'])

        # Generate impact summary
        if len(negative_effects) > len(positive_effects):
            impact = "Преобладали негативные эффекты"
        elif len(positive_effects) > len(negative_effects):
            impact = "Преобладали положительные эффекты"
        else:
            impact = "Был баланс эффектов"

        return {
            'active_count': len(active_effects),
            'positive_effects': positive_effects,
            'negative_effects': negative_effects,
            'impact_summary': impact
        }

    def restart_game_completely(self):
        """Completely restart the game to initial state with transition effects"""
        # Start transition sequence
        self.restart_transition_phase = 'black_screen'
        self.restart_transition_start_time = pygame.time.get_ticks()
        self.restart_transition_duration = 6000  # 6 seconds for each phase

    def handle_restart_transition(self):
        """Handle the restart transition sequence"""
        if not hasattr(self, 'restart_transition_phase'):
            return False

        current_time = pygame.time.get_ticks()
        elapsed = current_time - self.restart_transition_start_time

        if self.restart_transition_phase == 'black_screen':
            if elapsed >= self.restart_transition_duration:
                # Move to white screen phase
                self.restart_transition_phase = 'white_screen'
                self.restart_transition_start_time = current_time
            return True

        elif self.restart_transition_phase == 'white_screen':
            if elapsed >= self.restart_transition_duration:
                # Transition complete, actually restart the game
                self.complete_restart()
                return False
            return True

        return False

    def complete_restart(self):
        """Complete the actual restart after transition effects"""
        # Reset game state to completely new instance
        self.game_state = GameState()

        # Reset UI state
        if hasattr(self, 'current_card_tab'):
            delattr(self, 'current_card_tab')
        if hasattr(self, 'card_scroll'):
            delattr(self, 'card_scroll')
        if hasattr(self, 'pending_tooltip'):
            delattr(self, 'pending_tooltip')
        if hasattr(self, 'pending_event_tooltip'):
            delattr(self, 'pending_event_tooltip')

        # Reset button click protection system
        self.button_last_click = {}

        # Reset music to normal playlist
        if hasattr(self, 'music_manager') and self.music_enabled:
            # Stop any ending music first
            self.music_manager.stop()
            self.music_manager.start_playlist('normal')
            self.music_manager.start_fade_in()

        # Clear transition state
        if hasattr(self, 'restart_transition_phase'):
            delattr(self, 'restart_transition_phase')
        if hasattr(self, 'restart_transition_start_time'):
            delattr(self, 'restart_transition_start_time')
        if hasattr(self, 'restart_transition_duration'):
            delattr(self, 'restart_transition_duration')

        self.game_state.add_message("Новая история начинается...", 'success')

    def transition_status_effects_to_new_day(self):
        """Properly handle status effects when transitioning to a new day"""
        if not hasattr(self.game_state, 'status_effects') or not self.game_state.status_effects:
            return

        # 🚨 ОТЛАДКА: Показываем какие статусы обрабатываем
        status_names = [status['name'] for status in self.game_state.status_effects.values()]
        if status_names:
            self.game_state.add_message(
                f"📊 Обработка статусов при переходе на новый день: {', '.join(status_names)}",
                'info'
            )

        # Текущее время в конце предыдущего дня (примерно 22-24 часа)
        end_of_day_time = 22.0
        new_day_start_time = 8.0

        effects_to_remove = []

        for status_id, status in list(self.game_state.status_effects.items()):
            # Рассчитываем сколько времени прошло до конца дня
            time_passed = end_of_day_time - status['start_time']
            remaining_time = status['duration_hours'] - time_passed

            if remaining_time <= 0:
                # Статус должен был закончиться в предыдущий день - удаляем
                effects_to_remove.append(status_id)
                self.game_state.add_message(
                    f"⏰ Статус '{status['name']}' завершился в конце дня", 'info'
                )
            else:
                # Статус продолжается - корректируем start_time для нового дня
                # Устанавливаем start_time так, чтобы remaining_time было корректным
                status['start_time'] = new_day_start_time - (status['duration_hours'] - remaining_time)
                self.game_state.add_message(
                    f"📅 Статус '{status['name']}' продолжается (осталось {remaining_time:.1f}ч)", 'success'
                )

        # Удаляем истекшие статусы
        for status_id in effects_to_remove:
            self.game_state.remove_status_effect(status_id)

    def new_day(self):
        """Start a new day or restart after game over"""
        if self.game_state.phase == 'game_over':
            # Reset to initial state
            self.restart_game_completely()
            self.game_state.add_message("Игра перезапущена. Попробуйте ещё раз!", 'success')
        else:
            # Check for game ending after 30 days
            if self.game_state.day >= 30:
                self.trigger_game_ending()
                return

            # Normal new day progression
            self.game_state.day += 1
            self.game_state.day_of_week = (self.game_state.day_of_week + 1) % 7  # Переход к следующему дню недели

            # 🌙 Сон уже был показан после голосового диалога конца предыдущего дня
            # Не генерируем сон здесь, чтобы избежать дублирования

            # 🖥️ КОНСОЛЬНЫЙ ВЫВОД: Новый день
            weekday_name = self.game_state.weekdays[self.game_state.day_of_week]
            print(f"\n🌅 ==== ДЕНЬ {self.game_state.day} ({weekday_name}) ====")
            print(
                f"🔋 Начальные параметры: Стресс={self.game_state.stress}, Паранойя={self.game_state.paranoia}, Энергия={self.game_state.energy}")
            self.game_state.phase = 'planning'
            self.game_state.current_time = 8.0
            self.game_state.current_activity_index = 0
            self.game_state.timeline_activities = []
            self.game_state.activity_results = []
            self.game_state.selected_activity = -1
            self.game_state.free_time_penalty = 0

            # Generate new events
            self.game_state.generate_random_events()

            # Update mandatory activities based on time since last completion
            self.game_state.update_mandatory_activities()

            # Initialize adaptation system if it doesn't exist (for save compatibility)
            if not hasattr(self.game_state, 'activity_adaptation'):
                self.game_state.initialize_activity_adaptation()

            # Reset daily card usage
            self.game_state.used_cards = []

            # Reset daily voice interactions
            self.game_state.daily_voice_interactions = 0

            # Clear prediction data from previous day
            if hasattr(self.game_state, 'prediction_data'):
                delattr(self.game_state, 'prediction_data')

            # 🖥️ КОНСОЛЬНОЕ ЛОГИРОВАНИЕ: Статус флагов события на новый день
            if hasattr(self.game_state, 'event_time_skip_active') and self.game_state.event_time_skip_active:
                print(f"🔍 Новый день: обнаружен активный флаг события, оставляем для защиты")
            # Очистка флагов только после 30 дней (в конце игры)
            if self.game_state.day >= 30:
                if hasattr(self.game_state, 'event_time_skip_active'):
                    self.game_state.event_time_skip_active = False
                    print("🔄 Очистка флагов события в конце игры")

            # 🚨 ИСПРАВЛЕНИЕ: Правильный переход статусов на новый день
            self.transition_status_effects_to_new_day()

            # Show voice message for new day (only if message exists)
            voice_message = self.game_state.generate_voice_new_day_message(self.game_state.day)
            if voice_message:
                self.game_state.current_voice_message = voice_message
                self.game_state.show_voice_message_popup = True

            # Replace completed voice tasks with new ones (only if voice system unlocked)
            if self.game_state.day >= 3:
                if hasattr(self.game_state, 'voice_tasks') and hasattr(self.game_state, 'completed_voice_tasks'):
                    # Remove completed tasks and generate new ones to replace them
                    old_task_count = len(self.game_state.voice_tasks)
                    completed_count = len(self.game_state.completed_voice_tasks)

                    # Filter out completed tasks
                    self.game_state.voice_tasks = [task for task in self.game_state.voice_tasks
                                                   if task['id'] not in self.game_state.completed_voice_tasks]

                    # Clear completed tasks list
                    self.game_state.completed_voice_tasks = []

                    # Generate new tasks to maintain the same total number
                    remaining_tasks = len(self.game_state.voice_tasks)
                    needed_tasks = min(3, old_task_count) - remaining_tasks

                    if needed_tasks > 0:
                        # Generate replacement tasks
                        temp_tasks = []
                        self.game_state.voice_tasks = temp_tasks  # Temporarily clear for generation
                        self.game_state.generate_voice_tasks()

                        # Take only the number of new tasks we need
                        new_tasks = self.game_state.voice_tasks[:needed_tasks]

                        # Restore original remaining tasks and add new ones
                        remaining_original_tasks = [task for task in self.game_state.voice_tasks
                                                    if task['id'] not in [t['id'] for t in new_tasks]]
                        self.game_state.voice_tasks = remaining_original_tasks + new_tasks

                        if completed_count > 0:
                            self.game_state.add_message(f"📋 {completed_count} выполненных заданий заменены новыми",
                                                        'success')
                elif self.game_state.day == 3:
                    # First time unlocking voice system - generate initial tasks
                    self.game_state.generate_voice_tasks()
                    if hasattr(self.game_state, 'voice_tasks') and self.game_state.voice_tasks:
                        self.game_state.add_message("🎯 Система заданий от внутреннего голоса активирована!", 'success')
            else:
                # For days when voice system is unlocked but no existing tasks - generate new ones
                if not hasattr(self.game_state, 'voice_tasks') or not self.game_state.voice_tasks:
                    self.game_state.generate_voice_tasks()
                    if hasattr(self.game_state, 'voice_tasks') and self.game_state.voice_tasks:
                        self.game_state.add_message("📋 Новые задания от внутреннего голоса!", 'success')

            current_day_name = self.game_state.weekdays[self.game_state.day_of_week]
            self.game_state.add_message(f"День {self.game_state.day} - {current_day_name} начался!", 'success')

    def trigger_game_ending(self):
        """Trigger game ending after 30 days based on final mental state"""
        final_stress = self.game_state.stress
        final_paranoia = self.game_state.paranoia

        # Determine ending based on stress and paranoia levels
        ending_data = self.determine_ending(final_stress, final_paranoia)

        # Set game to ending phase
        self.game_state.phase = 'game_ending'
        self.game_state.current_ending = ending_data

        # Play appropriate ending music
        if self.music_enabled:
            self.music_manager.play_ending_music(ending_data['type'])

        # Show ending message

    # ========================================
    # 🌙 СИСТЕМА СНОВИДЕНИЙ
    # ========================================

    def get_dream_database(self):
        """База данных сновидений"""
        return {
            # 💚 СПОКОЙНЫЕ СНЫ (низкий стресс, низкая паранойя)
            'calm': [
                {
                    'id': 'calm_garden',
                    'name': 'Сад спокойствия',
                    'descriptions': [
                        'Вы гуляете по тихому саду. Цветы излучают мягкий свет. Всё наполнено спокойствием.',
                        'Солнечный сад окружает вас теплом. Птицы поют, ветер шепчет. Мир идеален.',
                        'Вы сидите на скамейке в саду. Время замедлилось. Ничто не тревожит вас.'
                    ],
                    'effects': {'stress': -5, 'energy': 5},
                    'hint': 'Спокойствие - ценный ресурс. Цените такие моменты.'
                },
                {
                    'id': 'calm_flight',
                    'name': 'Полёт',
                    'descriptions': [
                        'Вы легко парите над городом. Ветер приятен и свеж. Всё кажется простым.',
                        'Крылья несут вас сквозь облака. Свобода наполняет каждую клетку тела.',
                        'Вы парите в вышине. Земля далеко внизу. Вы чувствуете лёгкость бытия.'
                    ],
                    'effects': {'stress': -8, 'paranoia': -3},
                    'hint': 'Иногда нужно отпустить и позволить себе парить.'
                },
                {
                    'id': 'calm_home',
                    'name': 'Дом',
                    'descriptions': [
                        'Вы в уютном доме. Тепло, тихо, безопасно. Всё на своих местах.',
                        'Камин горит, чай готов. Вы в кресле с любимой книгой. Всё идеально.',
                        'Дом встречает вас теплом. Знакомые стены, любимые вещи. Покой и уют.'
                    ],
                    'effects': {'stress': -6, 'energy': 8},
                    'hint': 'Создайте себе убежище - место, где вы в безопасности.'
                }
            ],

            # 🟡 СВЕТЛЫЕ СНЫ (средний стресс/паранойя)
            'light': [
                {
                    'id': 'light_city',
                    'name': 'Город заката',
                    'descriptions': [
                        'Вы идёте по городу на закате. Люди вокруг заняты своими делами. Обычный день.',
                        'Закатное солнце золотит улицы. Город живёт своей жизнью. Вы часть этого.',
                        'Вечерний город шумит и светится. Вы идёте не спеша. Всё как обычно.'
                    ],
                    'effects': {'stress': -2},
                    'hint': 'Иногда обычное - это тоже хорошо.'
                },
                {
                    'id': 'light_work',
                    'name': 'Рабочая рутина',
                    'descriptions': [
                        'Вы выполняете знакомые задачи. Всё получается легко и быстро. Вы контролируете ситуацию.',
                        'Работа идёт как по маслу. Каждое движение отточено. Вы мастер своего дела.',
                        'Задачи решаются одна за другой. Вы в потоке. Всё под контролем.'
                    ],
                    'effects': {'energy': 5},
                    'hint': 'Практика делает вас лучше в любом деле.'
                },
                {
                    'id': 'light_conversation',
                    'name': 'Разговор',
                    'descriptions': [
                        'Вы разговариваете с кем-то знакомым. Слова текут легко. Вы чувствуете связь.',
                        'Приятный разговор за чашкой кофе. Смех, понимание. Это важно.',
                        'Вы делитесь мыслями с другом. Диалог лёгкий и искренний. Вас слышат.'
                    ],
                    'effects': {'stress': -3, 'paranoia': -2},
                    'hint': 'Общение - лучшее лекарство от одиночества.'
                }
            ],

            # 🟠 ТЁМНЫЕ СНЫ (высокий стресс)
            'dark': [
                {
                    'id': 'dark_chase',
                    'name': 'Погоня',
                    'descriptions': [
                        'Кто-то или что-то преследует вас. Вы бежите, но не можете оторваться...',
                        'Шаги за спиной всё ближе. Вы бежите изо всех сил. Но не можете убежать...',
                        'Погоня не прекращается. Силы на исходе. Преследователь настигает...'
                    ],
                    'effects': {'stress': 5},
                    'hint': 'Иногда лучше остановиться и разобраться в причинах страха.'
                },
                {
                    'id': 'dark_exam',
                    'name': 'Неподготовленность',
                    'descriptions': [
                        'Вы на важном испытании, но совершенно не готовы. Время истекает...',
                        'Экзамен начался. Вы не знаете ответов. Все смотрят на вас. Паника...',
                        'Тест перед вами. Вопросы непонятны. Время тикает. Вы провалитесь...'
                    ],
                    'effects': {'stress': 8, 'energy': -5},
                    'hint': 'Подготовка и планирование снижают тревогу.'
                },
                {
                    'id': 'dark_fall',
                    'name': 'Падение',
                    'descriptions': [
                        'Вы падаете в бездну. Падение кажется бесконечным. Нет контроля...',
                        'Земля уходит из-под ног. Вы летите вниз. Не за что ухватиться...',
                        'Свободное падение в темноту. Ветер свистит. Конца не видно...'
                    ],
                    'effects': {'stress': 6, 'paranoia': 3},
                    'hint': 'Потеря контроля начинается с маленьких вещей.'
                }
            ],

            # 🔴 КОШМАРЫ (высокая паранойя)
            'nightmare': [
                {
                    'id': 'nightmare_watchers',
                    'name': 'Наблюдатели',
                    'descriptions': [
                        'Вы чувствуете взгляды. Они повсюду. Следят. Оценивают. Судят.',
                        'Тени наблюдают за вами. Вы чувствуете их присутствие. Всегда. Везде.',
                        'Невидимые глаза следят за каждым вашим движением. Нет покоя.'
                    ],
                    'effects': {'paranoia': 5, 'stress': 3},
                    'hint': 'Не все смотрят на вас. Большинство занято собой.'
                },
                {
                    'id': 'nightmare_conspiracy',
                    'name': 'Заговор',
                    'descriptions': [
                        'Вы видите связи между всем. Всё сплелось против вас. Они знают...',
                        'Знаки повсюду. Совпадений слишком много. Это не случайно. Заговор...',
                        'Все они часть плана. Против вас. Вы видите паутину интриг. Ловушка...'
                    ],
                    'effects': {'paranoia': 8, 'stress': 5},
                    'hint': 'Совпадения - это часто просто совпадения.'
                },
                {
                    'id': 'nightmare_double',
                    'name': 'Двойник',
                    'descriptions': [
                        'Вы встречаете себя. Но это... другой вы. Кто из вас настоящий?',
                        'Зеркало отражает не вас. Двойник смотрит со злобой. Он заменит вас...',
                        'Вы видите себя со стороны. Но вы же здесь. Кто из вас реален?'
                    ],
                    'effects': {'paranoia': 10, 'energy': -8},
                    'hint': 'Идентичность - это не одно что-то постоянное. Мы меняемся.'
                }
            ],

            # 🔮 ОСОЗНАННЫЕ СНЫ (редкие, дают бонусы)
            'lucid': [
                {
                    'id': 'lucid_control',
                    'name': 'Контроль над сном',
                    'descriptions': [
                        'Вы понимаете, что спите. Мир подчиняется вашей воле. Вы можете всё!',
                        'Осознание приходит мгновенно. Это сон. Вы контролируете реальность.',
                        'Вы проснулись во сне. Безграничная власть над миром сновидений.'
                    ],
                    'effects': {'stress': -15, 'paranoia': -10, 'energy': 15},
                    'hint': 'Осознанность - первый шаг к изменениям.'
                },
                {
                    'id': 'lucid_practice',
                    'name': 'Тренировка',
                    'descriptions': [
                        'Вы практикуетесь в решении сложных задач. Всё получается легко!',
                        'Во сне вы тренируете навыки. Результат превосходный. Эффект будет в реальности.',
                        'Вы отрабатываете действия снова и снова. Совершенство близко.'
                    ],
                    'effects': {'energy': 20},
                    'hint': 'Следующая активность будет легче!',
                    'bonus': 'next_activity_boost'
                },
                {
                    'id': 'lucid_prophecy',
                    'name': 'Прозрение',
                    'descriptions': [
                        'Вы видите отрывки будущего. События, которые ещё не произошли...',
                        'Видения наполняют сознание. Будущее открывается фрагментами.',
                        'Сон показывает возможные пути. Вы видите то, что ещё не свершилось.'
                    ],
                    'effects': {'paranoia': -5},
                    'hint': 'Сегодня произойдёт что-то неожиданное.',
                    'bonus': 'event_hint'
                }
            ],

            # ⚠️ ПРЕДУПРЕЖДАЮЩИЕ СНЫ (устрашают от действий)
            'warning': [
                {
                    'id': 'warning_restaurant',
                    'name': 'Тёмный ресторан',
                    'descriptions': [
                        'Вы в ресторане. Еда пахнет странно. Официант смотрит угрожающе. Что-то не так...',
                        'Ресторан полон людей, но все они смотрят на вас. Еда превращается в пепел во рту.',
                        'В зале ресторана душно и темно. Стены сжимаются. Вы задыхаетесь от запахов.'
                    ],
                    'effects': {'stress': 3, 'paranoia': 2},
                    'hint': 'Возможно, стоит избегать общественных мест сегодня...',
                    'avoid_location': 'restaurant',
                    'penalty': {'stress': 8, 'paranoia': 5}
                },
                {
                    'id': 'warning_gym',
                    'name': 'Удушающий зал',
                    'descriptions': [
                        'Спортзал давит на вас. Тренажёры выглядят как орудия пыток. Воздух тяжёл...',
                        'В зале слишком много людей. Они все смотрят. Вы чувствуете слабость...',
                        'Вы пытаетесь тренироваться, но тело не слушается. Насмешки вокруг...'
                    ],
                    'effects': {'stress': 4, 'energy': -3},
                    'hint': 'Физические нагрузки могут быть опасны сегодня...',
                    'avoid_location': 'gym',
                    'penalty': {'stress': 10, 'energy': -10}
                },
                {
                    'id': 'warning_outdoor',
                    'name': 'Враждебная природа',
                    'descriptions': [
                        'Парк выглядит зловеще. Деревья скрипят угрожающе. Тени движутся...',
                        'На улице холодно и пусто. Ветер несёт угрозу. Вы не в безопасности...',
                        'Природа враждебна. Птицы кричат тревожно. Небо темнеет. Беда близко...'
                    ],
                    'effects': {'paranoia': 4, 'stress': 2},
                    'hint': 'Сегодня лучше остаться в помещении...',
                    'avoid_location': 'outdoor',
                    'penalty': {'paranoia': 8, 'stress': 6}
                }
            ],

            # ✨ МОТИВИРУЮЩИЕ СНЫ (побуждают к действиям)
            'motivating': [
                {
                    'id': 'motivating_restaurant',
                    'name': 'Праздник вкуса',
                    'descriptions': [
                        'Вы в прекрасном ресторане. Ароматы восхитительны. Люди улыбаются. Счастье...',
                        'Ресторан полон света и радости. Еда божественна. Вы хотите вернуться...',
                        'Идеальный вечер в ресторане. Атмосфера, еда, люди - всё идеально.'
                    ],
                    'effects': {'stress': -3, 'energy': 3},
                    'hint': 'Посещение ресторана принесёт особую радость сегодня!',
                    'encourage_location': 'restaurant',
                    'bonus_effects': {'stress': -8, 'energy': 8},
                    'penalty': {'stress': 6, 'energy': -5}
                },
                {
                    'id': 'motivating_gym',
                    'name': 'Сила и энергия',
                    'descriptions': [
                        'Вы тренируетесь. Тело наполнено силой. Каждое движение даёт энергию. Мощь!',
                        'Спортзал - ваша стихия. Вы чувствуете себя непобедимым. Сила растёт.',
                        'Тренировка идеальна. Результаты превосходят ожидания. Вы на пике!'
                    ],
                    'effects': {'energy': 5, 'stress': -2},
                    'hint': 'Физическая активность сегодня принесёт невероятный эффект!',
                    'encourage_location': 'gym',
                    'bonus_effects': {'energy': 15, 'stress': -10},
                    'penalty': {'energy': -8, 'stress': 8}
                },
                {
                    'id': 'motivating_reading',
                    'name': 'Мудрость страниц',
                    'descriptions': [
                        'Вы читаете книгу. Каждая страница открывает истину. Знание - сила.',
                        'Слова книги резонируют с душой. Вы понимаете больше, чем написано.',
                        'Чтение приносит озарения. Мысли становятся яснее. Мудрость приходит.'
                    ],
                    'effects': {'stress': -4, 'paranoia': -2},
                    'hint': 'Чтение сегодня откроет важные истины!',
                    'encourage_activity': 'чтени',
                    'bonus_effects': {'stress': -12, 'paranoia': -8},
                    'penalty': {'paranoia': 7, 'stress': 5}
                },
                {
                    'id': 'motivating_work',
                    'name': 'Продуктивность',
                    'descriptions': [
                        'Работа спорится невероятно. Идеи льются потоком. Вы гений!',
                        'Рабочие задачи решаются мгновенно. Вы в потоке. Продуктивность зашкаливает.',
                        'Каждое действие на работе приносит результат. Вы на волне успеха.'
                    ],
                    'effects': {'energy': 4, 'stress': -3},
                    'hint': 'Рабочая активность сегодня принесёт особый успех!',
                    'encourage_activity': 'работ',
                    'bonus_effects': {'energy': 12, 'stress': -8},
                    'penalty': {'stress': 9, 'energy': -6}
                }
            ]
        }

    def determine_dream_type(self):
        """Определяет тип сна на основе состояния игрока и рандома"""
        stress = self.game_state.stress
        paranoia = self.game_state.paranoia
        rand = random.random()

        # 5% шанс осознанного сна
        if rand < 0.05:
            return 'lucid'

        # 10% шанс предупреждающего сна
        if rand < 0.15:
            return 'warning'

        # 10% шанс мотивирующего сна
        if rand < 0.25:
            return 'motivating'

        # Вычисляем вероятности на основе статов
        nightmare_chance = paranoia / 100
        dark_chance = stress / 100
        calm_chance = (100 - stress) / 100 * (100 - paranoia) / 100

        # Добавляем случайность (20% шанс на любой тип сна)
        base_random_chance = 0.2

        nightmare_weight = nightmare_chance + base_random_chance
        dark_weight = dark_chance + base_random_chance
        calm_weight = calm_chance + base_random_chance
        light_weight = 1.0 + base_random_chance

        total_weight = nightmare_weight + dark_weight + calm_weight + light_weight

        # Нормализуем вероятности
        nightmare_weight /= total_weight
        dark_weight /= total_weight
        calm_weight /= total_weight
        light_weight /= total_weight

        # Выбираем тип сна на основе вероятностей
        choice = random.random()

        if choice < nightmare_weight:
            return 'nightmare'
        elif choice < nightmare_weight + dark_weight:
            return 'dark'
        elif choice < nightmare_weight + dark_weight + calm_weight:
            return 'calm'
        else:
            return 'light'

    def get_random_dream(self, dream_type):
        """Выбирает случайный сон из категории и случайное описание"""
        dreams_db = self.get_dream_database()
        dreams = dreams_db.get(dream_type, dreams_db['light'])
        dream = random.choice(dreams).copy()

        # Выбираем случайное описание из списка
        if 'descriptions' in dream:
            dream['description'] = random.choice(dream['descriptions'])

        return dream

    def start_dream_phase(self):
        """Начать фазу сновидения"""
        print(f"🌙 ФАЗА СНА: День {self.game_state.day}")

        # Определяем тип сна
        dream_type = self.determine_dream_type()
        current_dream = self.get_random_dream(dream_type)

        print(f"🌙 Тип сна: {dream_type}")
        print(f"🌙 Сновидение: {current_dream['name']}")

        # Сохраняем текущий сон
        self.game_state.current_dream = current_dream
        self.game_state.phase = 'dreaming'

    def apply_dream_effects(self, dream):
        """Применяет эффекты сновидения"""
        effects = dream.get('effects', {})

        # Применяем стандартные эффекты
        if 'stress' in effects:
            self.game_state.stress = max(0, min(100, self.game_state.stress + effects['stress']))
        if 'paranoia' in effects:
            self.game_state.paranoia = max(0, min(100, self.game_state.paranoia + effects['paranoia']))
        if 'energy' in effects:
            self.game_state.energy = max(0, min(100, self.game_state.energy + effects['energy']))

        # Применяем специальные бонусы
        bonus = dream.get('bonus')
        if bonus == 'next_activity_boost':
            self.game_state.dream_activity_boost = True
            self.game_state.add_message("✨ Следующая активность будет эффективнее!", 'success')
        elif bonus == 'event_hint':
            self.game_state.dream_event_hint = True
            self.game_state.add_message("🔮 Вы предчувствуете грядущие события...", 'info')

        # Сохраняем информацию о предупреждающих/мотивирующих снах
        if 'avoid_location' in dream:
            if not hasattr(self.game_state, 'dream_warnings'):
                self.game_state.dream_warnings = {}
            self.game_state.dream_warnings['location'] = dream['avoid_location']
            self.game_state.dream_warnings['penalty'] = dream['penalty']
            print(f"⚠️ Предупреждение: избегайте {dream['avoid_location']}")

        if 'encourage_location' in dream:
            if not hasattr(self.game_state, 'dream_motivations'):
                self.game_state.dream_motivations = {}
            self.game_state.dream_motivations['location'] = dream['encourage_location']
            self.game_state.dream_motivations['bonus'] = dream['bonus_effects']
            self.game_state.dream_motivations['penalty'] = dream['penalty']
            print(f"✨ Мотивация: посетите {dream['encourage_location']}")

        if 'encourage_activity' in dream:
            if not hasattr(self.game_state, 'dream_motivations'):
                self.game_state.dream_motivations = {}
            self.game_state.dream_motivations['activity'] = dream['encourage_activity']
            self.game_state.dream_motivations['bonus'] = dream['bonus_effects']
            self.game_state.dream_motivations['penalty'] = dream['penalty']
            print(f"✨ Мотивация: выполните {dream['encourage_activity']}")

        print(f"🌙 Эффекты сна применены: {effects}")

    def complete_dream_phase(self):
        """Завершает фазу сновидения и переходит к новому дню"""
        # Применяем эффекты сна
        if hasattr(self.game_state, 'current_dream'):
            self.apply_dream_effects(self.game_state.current_dream)
            delattr(self.game_state, 'current_dream')

        # Переходим к новому дню - выполняем всю логику инициализации дня
        weekday_name = self.game_state.weekdays[self.game_state.day_of_week]
        print(f"\n🌅 ==== ДЕНЬ {self.game_state.day} ({weekday_name}) ====")
        print(
            f"🔋 Начальные параметры: Стресс={self.game_state.stress}, Паранойя={self.game_state.paranoia}, Энергия={self.game_state.energy}")

        # Переходим к фазе планирования
        self.game_state.phase = 'planning'
        self.game_state.current_time = 8.0
        self.game_state.current_activity_index = 0
        self.game_state.timeline_activities = []
        self.game_state.activity_results = []
        self.game_state.selected_activity = -1
        self.game_state.free_time_penalty = 0

        # Generate new events
        self.game_state.generate_random_events()

        # Update mandatory activities based on time since last completion
        self.game_state.update_mandatory_activities()

        # Initialize adaptation system if it doesn't exist (for save compatibility)
        if not hasattr(self.game_state, 'activity_adaptation'):
            self.game_state.initialize_activity_adaptation()

        # Reset daily card usage
        self.game_state.used_cards = []

        # Reset daily voice interactions
        self.game_state.daily_voice_interactions = 0

        # Сообщение о начале нового дня
        self.game_state.add_message(f"День {self.game_state.day} ({weekday_name}) начался!", 'success')

    def determine_ending(self, stress, paranoia):
        """Determine which ending to show based on final mental state and voice relationship"""
        voice_relationship = self.game_state.inner_voice_relationship

        # Calculate voice task statistics
        total_tasks_assigned = 0
        total_tasks_completed = 0

        # Count all tasks that were ever assigned during the game
        if hasattr(self.game_state, 'voice_history'):
            for entry in self.game_state.voice_history:
                if 'Выполнили задание:' in entry:
                    total_tasks_completed += 1
                elif 'Провалили задание:' in entry:
                    pass  # Already counted in assignment

        # Estimate total assigned tasks based on days (rough calculation)
        # Voice system starts on day 3, so roughly (30-3) * 2.5 average tasks per day
        if self.game_state.day >= 3:
            estimated_total_tasks = max(1, (self.game_state.day - 2) * 2)  # Conservative estimate
            total_tasks_assigned = estimated_total_tasks

        # Calculate task completion rate
        task_completion_rate = 0
        if total_tasks_assigned > 0:
            task_completion_rate = total_tasks_completed / total_tasks_assigned

        # Complex ending determination considering stress, paranoia, voice relationship, and tasks
        mental_health_score = 100 - ((stress + paranoia) / 2)  # 0-100 scale
        relationship_bonus = max(-20, min(20, voice_relationship / 5))  # -20 to +20 bonus
        task_bonus = task_completion_rate * 15  # 0 to 15 bonus for task completion

        final_score = mental_health_score + relationship_bonus + task_bonus

        if total_tasks_completed == 0:
            total_tasks_completed == 1

        # Special overrides for extreme cases
        if voice_relationship <= -50:
            ending_type = 'bad'  # Very bad relationship forces bad ending
        elif stress >= 80 or paranoia >= 80:
            ending_type = 'bad'  # Extreme mental distress forces bad ending
        elif stress <= 30 and paranoia <= 30:
            ending_type = 'good'  # Excellent relationship + good mental health = good ending
        elif stress <= 60 and paranoia <= 60:
            ending_type = 'neutral'
        else:
            ending_type = 'bad'

        description_1 = (
            "30 дней... Как долго они тянулись. Ты же хотел узнать ответы? Сейчас все и получишь. Надеюсь ты готов... "
            "Я думаю ты понимаешь как стресс может разъедать человека изнутри? У любого параметра есть пределы, твоё "
            "психологическое состояние не исключение. Однажды оно подошло к такой грани, что ты решился на кардинальные изменения... "
            "Тебе необходим был проводник в это неспокойное время. Так появился Я. Однако этого оказалось недостаточно. "
            "Ты часто не слушал меня, хотя я и был лишен различных недостатков вроде морали, сострадания, нерешимости и т.д. "
            "Тогда ты решился на немыслимое... Попросил меня стереть тебе память и контролировать каждый твой шаг. ")
        if voice_relationship >= 35:
            description_2 = (
                "После всего этого ты начал меня слушаться. Да, до сих пор не всегда, но ты пытался исправно выполнять мои, а точнее, "
                "свои же задания. Я награждал тебя за это и пытался этим питать твою мотивацию. Я надеюсь теперь ты понимаешь "
                "почему я не мог помогать тебе безгранично, а выставлял цену за каждое своё действие? ")
        if voice_relationship < 35:
            description_2 = ("Даже после всего этого ты не начал меня слушаться. Ты почти не выполнял мои, а точнее, "
                             "свои же задания. Я наказывал тебя и пытался этим изменить твоё отношение. Я надеюсь теперь ты понимаешь "
                             "почему я иногда 'ставил палки тебе в колеса', а не пытался безгранично помогать? ")
        if total_tasks_assigned / total_tasks_completed <= 1.3:
            description_3 = ("Что по итогу? Ты и правда выполнил достаточно много заданий. Помогло ли это?")
        if total_tasks_assigned / total_tasks_completed > 1.3:
            description_3 = (
                "Что по итогу? Ты выполнил достаточно мало заданий. Но так ли сильно это повлияло на общую ситуацию?")
        if ending_type == 'good':
            return {
                'type': 'good',
                'title': 'Почти идеал',
                'description': [
                    description_1, description_2, description_3,
                    "Стресс и правда стал меньше, а паранойя отступила. Но можно ли это назвать победой? Ты всегда призывал стремиться только "
                    "к идеалу. Разве это можно назвать идеалом? Нет... Придеться все начинать сначала... "
                ],
                'stats': {
                    'final_stress': stress,
                    'final_paranoia': paranoia,
                    'voice_relationship': voice_relationship,
                    'final_score': final_score,
                    'total_tasks_assigned': total_tasks_assigned,
                    'total_tasks_completed': total_tasks_completed,
                    'task_completion_rate': task_completion_rate
                }
            }
        elif ending_type == 'neutral':  # Moderate levels
            return {
                'type': 'neutral',
                'title': 'Минимальные изменения',
                'description': [
                    description_1, description_2, description_3,
                    "Ничего по итогу не изменилось. Стресс все такой же, паранойя до сих пор не отступает. "
                    "С другой стороны - не стало и хуже, но разве можно останавливаться на этом? Ты всегда призывал "
                    "стремиться только к идеалу. Разве это можно назвать идеалом? Нет... Придеться все начинать сначала... "
                ],
                'stats': {
                    'final_stress': stress,
                    'final_paranoia': paranoia,
                    'voice_relationship': voice_relationship,
                    'final_score': final_score,
                    'total_tasks_assigned': total_tasks_assigned,
                    'total_tasks_completed': total_tasks_completed,
                    'task_completion_rate': task_completion_rate
                }
            }
        else:  # Bad ending
            return {
                'type': 'bad',
                'title': 'Потеря контроля',
                'description': [
                    description_1, description_2, description_3,
                    "Ты... Как можно было настолько облажаться? Теперь все ещё хуже, чем было. "
                    "Ты абсолютно некомпетентен. Ты никого не слушаешь. Даже себя. Поэтому то ты "
                    "ничего не можешь достигнуть. Можно конечно все начать сначала, но... имеет ли это смысл? "
                    "Возможно лучше тебе... просто передать мне контроль? "
                ],
                'stats': {
                    'final_stress': stress,
                    'final_paranoia': paranoia,
                    'voice_relationship': voice_relationship,
                    'final_score': final_score,
                    'total_tasks_assigned': total_tasks_assigned,
                    'total_tasks_completed': total_tasks_completed,
                    'task_completion_rate': task_completion_rate
                }
            }

    def draw_header(self):
        """Draw the game header"""
        # Background
        header_rect = pygame.Rect(0, 0, WINDOW_WIDTH, 160)
        pygame.draw.rect(self.screen, COLORS['panel'], header_rect)
        pygame.draw.line(self.screen, COLORS['accent'], (0, 160), (WINDOW_WIDTH, 160), 2)

        # Title
        current_day_name = self.game_state.weekdays[self.game_state.day_of_week]
        title = f"День {self.game_state.day} - {current_day_name}"
        title_surface = FONTS['title'].render(title, True, COLORS['text'])
        self.screen.blit(title_surface, (20, 10))

        # Phase indicator with Russian phase names
        phase_names = {
            'planning': 'планирование',
            'execution': 'исполнение',
            'results': 'результаты',
            'game_over': 'конец игры',
            'game_ending': 'концовка'
        }
        phase_russian = phase_names.get(self.game_state.phase, self.game_state.phase)
        phase_text = f"Фаза: {phase_russian}"
        phase_surface = FONTS['medium'].render(phase_text, True, COLORS['accent'])
        self.screen.blit(phase_surface, (WINDOW_WIDTH - 200, 15))

        # Time
        if self.game_state.phase == 'execution':
            time_text = f"Время: {int(self.game_state.current_time)}:00"
            time_surface = FONTS['medium'].render(time_text, True, COLORS['text'])
            self.screen.blit(time_surface, (WINDOW_WIDTH - 200, 45))

        # Mental state bars
        self.progress_bars['energy'].set_value(self.game_state.energy)
        self.progress_bars['stress'].set_value(self.game_state.stress)
        self.progress_bars['paranoia'].set_value(self.game_state.paranoia)

        # Draw bars with integrated labels
        self.progress_bars['energy'].draw(self.screen,
                                          self.game_state.get_mental_state_color(self.game_state.energy, True),
                                          "Энергия")
        self.progress_bars['stress'].draw(self.screen,
                                          self.game_state.get_mental_state_color(self.game_state.stress, False),
                                          "Стресс")
        self.progress_bars['paranoia'].draw(self.screen,
                                            self.game_state.get_mental_state_color(self.game_state.paranoia, False),
                                            "Паранойя")

    def draw_activities_panel(self):
        """Draw the available activities panel"""
        panel_rect = pygame.Rect(500, 170, 480, 200)
        pygame.draw.rect(self.screen, COLORS['panel'], panel_rect)
        pygame.draw.rect(self.screen, COLORS['accent'], panel_rect, 2)

        # Title
        title = "Доступные активности"
        title_surface = FONTS['medium'].render(title, True, COLORS['text'])
        self.screen.blit(title_surface, (510, 180))

        # Instruction
        instruction = "Перетащите на временную шкалу"
        instruction_surface = FONTS['small'].render(instruction, True, COLORS['text_dim'])
        self.screen.blit(instruction_surface, (510, 200))

        # Create clipping area for activities
        clip_rect = pygame.Rect(510, 220, 460, 140)  # Narrowed visible area
        original_clip = self.screen.get_clip()
        self.screen.set_clip(clip_rect)

        # Activity list with proper bounds checking
        y_offset = 230
        activity_height = 45
        max_visible_activities = 3  # Show only 3 activities at once

        # Calculate maximum scroll offset
        total_activities_height = len(self.game_state.available_activities) * 50
        visible_area_height = 140
        max_scroll = max(0, total_activities_height - visible_area_height)
        self.game_state.scroll_offset = min(self.game_state.scroll_offset, max_scroll)

        # Sort activities to show mandatory ones first
        sorted_activities = sorted(self.game_state.available_activities,
                                   key=lambda act: (not act['mandatory'], act['name']))

        for i, activity in enumerate(sorted_activities):
            # Calculate position with scroll offset
            display_y = y_offset + i * 50 - self.game_state.scroll_offset

            # Skip if completely outside visible area
            if display_y < 210 or display_y > 370:
                continue

            # Check if activity is available today
            is_available = self.game_state.is_activity_available_today(activity)
            unavailable_reason = self.game_state.get_unavailable_reason(activity) if not is_available else None

            # Activity background - ensure it stays within bounds
            activity_rect = pygame.Rect(510, display_y, 460, activity_height)

            # Selection highlight (only if available)
            if i == self.game_state.selected_activity and is_available:
                pygame.draw.rect(self.screen, COLORS['button_hover'], activity_rect, border_radius=4)
                pygame.draw.rect(self.screen, COLORS['accent'], activity_rect, 3, border_radius=4)
            else:
                # Different background for unavailable activities
                bg_color = COLORS['panel_light'] if is_available else COLORS['panel']
                pygame.draw.rect(self.screen, bg_color, activity_rect, border_radius=4)

            # Mandatory/Optional indicator with availability
            if is_available:
                border_color = COLORS['mandatory'] if activity['mandatory'] else COLORS['optional']
            else:
                border_color = COLORS['text_dim']  # Gray for unavailable
            pygame.draw.rect(self.screen, border_color, activity_rect, 2, border_radius=4)

            # Icon (grayed out if unavailable)
            icon_color = COLORS['text'] if is_available else COLORS['text_dim']
            icon_surface = FONTS['large'].render(activity['icon'], True, icon_color)
            self.screen.blit(icon_surface, (520, display_y + 8))

            # Name (grayed out if unavailable) with adaptation status
            name_color = COLORS['text'] if is_available else COLORS['text_dim']
            activity_name = activity['name']
            if not is_available:
                activity_name += " (недоступно)"
            else:
                # Add adaptation status for positive stress activities
                adaptation_status = self.game_state.get_adaptation_status_text(activity)
                activity_name += adaptation_status

            name_surface = FONTS['medium'].render(activity_name, True, name_color)
            self.screen.blit(name_surface, (555, display_y + 3))

            # Duration and time constraint or unavailable reason
            if is_available:
                duration_text = f"{activity['duration']}ч • {activity['time_display']}"
                duration_surface = FONTS['small'].render(duration_text, True, COLORS['text_dim'])

                # Проверяем, помещается ли текст в доступную область
                available_width_duration = 460 - 45  # ширина панели минус отступы и иконка
                if duration_surface.get_width() > available_width_duration:
                    # Сокращаем формат времени
                    duration_text = f"{activity['duration']}ч"
                    duration_surface = FONTS['small'].render(duration_text, True, COLORS['text_dim'])

                self.screen.blit(duration_surface, (555, display_y + 25))
            else:
                reason_surface = FONTS['small'].render(unavailable_reason, True, COLORS['warning'])
                self.screen.blit(reason_surface, (555, display_y + 25))

            # Effects с проверкой размещения и учётом адаптации
            effects = []
            if activity['energy_recovery'] != 0:
                effects.append(f"Энергия: {activity['energy_recovery']:+d}")
            if activity['stress_recovery'] != 0:
                # Show adapted stress recovery value
                if is_available:
                    adapted_stress = self.game_state.get_adapted_stress_recovery(activity)
                    effects.append(f"Стресс: {adapted_stress:+d}")
                else:
                    effects.append(f"Стресс: {activity['stress_recovery']:+d}")

            if effects:
                effects_text = " | ".join(effects)
                effects_surface = FONTS['small'].render(effects_text, True, COLORS['warning'])

                # Позиционируем эффекты справа, но с проверкой
                effects_x = max(800, 510 + 460 - effects_surface.get_width() - 10)
                effects_x = min(effects_x, 910)  # Не выходим за границы панели

                self.screen.blit(effects_surface, (effects_x, display_y + 15))

        # Reset clipping
        self.screen.set_clip(original_clip)

        # Draw scroll indicators
        if len(self.game_state.available_activities) > max_visible_activities:
            # Scroll up indicator
            if self.game_state.scroll_offset > 0:
                up_arrow = "▲"
                up_surface = FONTS['small'].render(up_arrow, True, COLORS['accent'])
                self.screen.blit(up_surface, (960, 225))

            # Scroll down indicator
            if self.game_state.scroll_offset < max_scroll:
                down_arrow = "▼"
                down_surface = FONTS['small'].render(down_arrow, True, COLORS['accent'])
                self.screen.blit(down_surface, (960, 345))

    def draw_timeline(self):
        """Draw the timeline and placed activities with visual grid cells"""
        # Timeline background
        pygame.draw.rect(self.screen, COLORS['timeline_bg'], self.game_state.timeline_rect)
        pygame.draw.rect(self.screen, COLORS['accent'], self.game_state.timeline_rect, 2)

        # Title
        title_surface = FONTS['medium'].render("Временная шкала дня", True, COLORS['text'])
        self.screen.blit(title_surface, (30, self.game_state.timeline_rect.y + 10))

        # Instructions
        instruction1 = "Перетаскивайте активности сюда • ПКМ - удалить"
        instruction1_surface = FONTS['small'].render(instruction1, True, COLORS['text_dim'])
        self.screen.blit(instruction1_surface, (30, self.game_state.timeline_rect.y + 30))

        # Calculate grid parameters
        hours_y = self.game_state.timeline_rect.y + 50
        activity_area_top = self.game_state.timeline_rect.y + 60
        activity_area_height = 50

        # Draw time cell backgrounds to show drop zones
        current_time = self.game_state.timeline_start_hour
        while current_time < self.game_state.timeline_end_hour:
            x_start = self.game_state.get_hour_x_position(current_time)
            x_end = self.game_state.get_hour_x_position(current_time + 0.5)

            # Create subtle grid cells
            cell_rect = pygame.Rect(x_start, activity_area_top, x_end - x_start, activity_area_height)

            # Alternate cell colors for better visibility
            is_even_hour = int(current_time) % 2 == 0
            is_full_hour = current_time == int(current_time)

            if is_even_hour and is_full_hour:
                cell_color = (45, 45, 70)  # Slightly lighter
            elif is_even_hour:
                cell_color = (40, 40, 65)  # Medium
            elif is_full_hour:
                cell_color = (35, 35, 60)  # Medium-dark
            else:
                cell_color = (30, 30, 55)  # Darkest

            pygame.draw.rect(self.screen, cell_color, cell_rect)
            pygame.draw.rect(self.screen, COLORS['timeline_hour'], cell_rect, 1)

            current_time += 0.5

        # Draw hour markers and half-hour markers
        current_time = self.game_state.timeline_start_hour
        while current_time <= self.game_state.timeline_end_hour:
            x = self.game_state.get_hour_x_position(current_time)

            # Determine if this is a full hour or half hour
            is_full_hour = current_time == int(current_time)
            is_major_hour = is_full_hour and int(current_time) % 2 == 0

            # Line style based on time type
            if is_major_hour:
                line_color = COLORS['accent']
                line_width = 2
            elif is_full_hour:
                line_color = COLORS['timeline_hour']
                line_width = 1
            else:
                line_color = COLORS['timeline_hour']
                line_width = 1

            pygame.draw.line(self.screen, line_color,
                             (x, hours_y), (x, self.game_state.timeline_rect.bottom - 20), line_width)

            # Label logic
            if is_full_hour:
                hour_label = f"{int(current_time)}:00"
                label_color = COLORS['text'] if is_major_hour else COLORS['text_dim']
                hour_surface = FONTS['tiny'].render(hour_label, True, label_color)
                label_rect = hour_surface.get_rect()
                label_rect.centerx = x
                label_rect.y = self.game_state.timeline_rect.bottom - 15
                self.screen.blit(hour_surface, label_rect)
            else:
                # Half-hour mark - no labels, just visual indicators
                pass

            current_time += 0.5

        # Highlight drop zone when dragging
        if self.game_state.dragging_activity:
            mouse_pos = pygame.mouse.get_pos()
            if self.game_state.timeline_rect.collidepoint(mouse_pos):
                drop_time = self.game_state.get_hour_from_x_position(mouse_pos[0])
                duration = self.game_state.dragging_activity.activity['duration']

                # Highlight the cells where the activity would be placed
                highlight_start = self.game_state.get_hour_x_position(drop_time)
                highlight_end = self.game_state.get_hour_x_position(drop_time + duration)
                highlight_rect = pygame.Rect(highlight_start, activity_area_top,
                                             highlight_end - highlight_start, activity_area_height)

                # Check if placement is valid
                can_place = self.game_state.can_place_activity_at_time(
                    self.game_state.dragging_activity.activity, drop_time)

                highlight_color = (80, 120, 80, 100) if can_place else (120, 80, 80, 100)
                highlight_surface = pygame.Surface((highlight_rect.width, highlight_rect.height))
                highlight_surface.set_alpha(100)
                highlight_surface.fill(highlight_color[:3])
                self.screen.blit(highlight_surface, highlight_rect)

                # Draw border
                border_color = COLORS['success'] if can_place else COLORS['danger']
                pygame.draw.rect(self.screen, border_color, highlight_rect, 3)

        # Draw placed activities
        for timeline_activity in self.game_state.timeline_activities:
            self.draw_timeline_activity(timeline_activity)

        # Draw dragging activity
        if self.game_state.dragging_activity and self.game_state.dragging_activity not in self.game_state.timeline_activities:
            self.draw_timeline_activity(self.game_state.dragging_activity)

    def draw_prediction_panel(self):
        """Draw prediction panel showing upcoming events"""
        if not hasattr(self.game_state, 'prediction_data'):
            return

        prediction_data = self.game_state.prediction_data
        current_time = time.time()
        elapsed_time = current_time - prediction_data['start_time']

        # Remove prediction data if duration has passed
        if elapsed_time >= prediction_data['duration']:
            delattr(self.game_state, 'prediction_data')
            return

        # Calculate remaining time and fade effect
        remaining_time = prediction_data['duration'] - elapsed_time
        fade_start = prediction_data['duration'] - 3.0  # Start fading 3 seconds before end

        if remaining_time < 3.0:
            # Fade out effect in last 3 seconds
            alpha = int(255 * (remaining_time / 3.0))
        else:
            alpha = 255

        # Panel positioning - place it prominently
        panel_rect = pygame.Rect(500, 120, 480, 100)

        # Create surfaces with alpha
        panel_surface = pygame.Surface((panel_rect.width, panel_rect.height))
        panel_surface.set_alpha(alpha)
        panel_surface.fill(COLORS['panel_light'])

        border_surface = pygame.Surface((panel_rect.width, panel_rect.height))
        border_surface.set_alpha(alpha)
        border_surface.fill(COLORS['warning'])

        # Draw background
        self.screen.blit(panel_surface, panel_rect)
        pygame.draw.rect(self.screen, COLORS['warning'], panel_rect, 3, border_radius=8)

        # Title with crystal ball icon
        title_text = "🔮 Предвидение активно"
        title_surface = FONTS['medium'].render(title_text, True, COLORS['warning'])
        title_surface.set_alpha(alpha)
        self.screen.blit(title_surface, (panel_rect.x + 10, panel_rect.y + 10))

        # Remaining time indicator
        time_text = f"Осталось: {remaining_time:.1f}с"
        time_surface = FONTS['small'].render(time_text, True, COLORS['text_dim'])
        time_surface.set_alpha(alpha)
        time_rect = time_surface.get_rect()
        time_rect.topright = (panel_rect.right - 10, panel_rect.y + 12)
        self.screen.blit(time_surface, time_rect)

        # Display predicted events
        events_y = panel_rect.y + 35
        for i, event in enumerate(prediction_data['events']):
            if events_y + 15 > panel_rect.bottom - 10:
                break

            # Получаем время события (ровные часы)
            event_time = event['time']
            if isinstance(event_time, (int, float)):
                time_str = f"{int(event_time):02d}:00"
            else:
                time_str = str(event_time)
            event_text = f"• {event['icon']} {event['name']} в {time_str}"
            event_surface = FONTS['small'].render(event_text, True, COLORS['text'])
            event_surface.set_alpha(alpha)
            self.screen.blit(event_surface, (panel_rect.x + 20, events_y))
            events_y += 18

    def draw_prediction_panel(self):
        """Draw prediction panel showing upcoming events"""
        if not hasattr(self.game_state, 'prediction_data'):
            return

        prediction_data = self.game_state.prediction_data

        # Check if prediction should be cleared (new day started)
        if prediction_data.get('day_activated') != self.game_state.day:
            delattr(self.game_state, 'prediction_data')
            return

        # Panel positioning - bottom edge aligned with stress progress bar
        stress_bar_bottom = 120 + 30  # stress bar y (120) + height (30)
        panel_height = 140  # Restored original height
        panel_y = stress_bar_bottom - panel_height
        panel_rect = pygame.Rect(500, panel_y, 480, panel_height)

        # Draw background
        pygame.draw.rect(self.screen, COLORS['panel_light'], panel_rect, border_radius=8)
        pygame.draw.rect(self.screen, COLORS['warning'], panel_rect, 3, border_radius=8)

        # Title with crystal ball icon
        title_text = "🔮 Предвидение: Предстоящие события"
        title_surface = FONTS['medium'].render(title_text, True, COLORS['warning'])
        self.screen.blit(title_surface, (panel_rect.x + 10, panel_rect.y + 10))

        # Убираем статус индикатор "Активно до конца дня"

        # Display predicted events with better spacing
        events_y = panel_rect.y + 40
        for i, event in enumerate(prediction_data.get('events', [])):
            if events_y + 20 > panel_rect.bottom - 10:
                break

            # Check if event was already processed by checking pending_activity_events
            event_processed = False
            event_name_to_check = event.get('name', '')

            # Проверяем в новой системе событий между активностями
            if hasattr(self.game_state, 'pending_activity_events'):
                for pending_event in self.game_state.pending_activity_events:
                    if pending_event.get('name') == event_name_to_check:
                        event_processed = pending_event.get('triggered', False)
                        break

            event_color = COLORS['text_dim'] if event_processed else COLORS['text']

            # Add status indicator
            status_indicator = "✓" if event_processed else "⏳"
            event_icon = event.get('icon', '?')
            event_name = event.get('name', 'Неизвестное событие')
            event_time = event.get('time', 12)
            if isinstance(event_time, (int, float)):
                event_time_display = f"{int(event_time):02d}:00"
            else:
                event_time_display = str(event_time)
            event_text = f"{status_indicator} {event_icon} {event_name} в {event_time_display}"

            event_surface = FONTS['small'].render(event_text, True, event_color)
            self.screen.blit(event_surface, (panel_rect.x + 20, events_y))
            events_y += 22

        # Убираем пояснительную надпись "Серые события уже произошли"

    def draw_status_effects_bar(self):
        """Draw the status effects bar between timeline and messages"""
        bar_y = self.game_state.timeline_rect.bottom + 10
        bar_height = 60
        bar_rect = pygame.Rect(20, bar_y, WINDOW_WIDTH - 600, bar_height)

        # Background
        pygame.draw.rect(self.screen, COLORS['panel'], bar_rect, border_radius=8)
        pygame.draw.rect(self.screen, COLORS['accent'], bar_rect, 2, border_radius=8)

        # Title (smaller to fit in reduced height)
        title_surface = FONTS['medium'].render("Статусы:", True, COLORS['text'])
        self.screen.blit(title_surface, (30, bar_y + 23))

        # Get active status effects - always try to get them
        active_statuses = []
        if hasattr(self.game_state, 'get_status_effects_summary'):
            try:
                active_statuses = self.game_state.get_status_effects_summary()
            except Exception:
                active_statuses = []  # Just use empty list if error

        # Define common variables for status drawing
        start_x = 150  # Starting position for status circles
        circle_size = 40  # Smaller circles for compact bar
        circle_spacing = 55  # Closer together

        # 🌙 Проверяем наличие снов для правильной проверки "нет статусов"
        has_dream_warnings = hasattr(self.game_state, 'dream_warnings')
        has_dream_motivations = hasattr(self.game_state, 'dream_motivations')
        has_any_effects = active_statuses or has_dream_warnings or has_dream_motivations

        if not has_any_effects:
            # No active effects
            no_effects_surface = FONTS['medium'].render("Нет активных статусов", True, COLORS['text'])
            self.screen.blit(no_effects_surface, (120, bar_y + 23))
        else:
            # Draw status effects as circles
            mouse_pos = pygame.mouse.get_pos()

            for i, status in enumerate(active_statuses):
                if i >= 20:  # More statuses can fit in wider bar
                    break

                circle_x = start_x + i * circle_spacing
                circle_y = bar_y + 30  # Adjusted for smaller bar height (centered)
                circle_center = (circle_x, circle_y)

                # Проверяем что круг помещается в панель
                if circle_x + circle_size // 2 > bar_rect.right - 10:
                    break

                # Determine status color based on type - безопасная проверка
                status_name = status.get('name', '').lower()
                status_id = status.get('status_id', '')

                # Негативные статусы
                if any(keyword in status_name for keyword in
                       ['истощение', 'критическое', 'паранойя', 'слежка', 'тревога', 'страх']):
                    status_color = COLORS['danger']
                elif any(keyword in status_name for keyword in ['перенапряжение']):
                    status_color = COLORS['warning']
                # Позитивные статусы
                elif status_id in ['inspired', 'focused', 'confident', 'energized'] or any(
                        keyword in status_name for keyword in
                        ['воодушв', 'концентрац', 'уверенн', 'энергичн', 'прилив', 'спокойствие', 'фокус']):
                    status_color = COLORS['success']
                else:
                    status_color = COLORS['accent']

                # Draw circle background
                pygame.draw.circle(self.screen, status_color, circle_center, circle_size // 2)
                pygame.draw.circle(self.screen, COLORS['text'], circle_center, circle_size // 2, 2)

                # Draw icon - smaller font for compact circles
                status_icon = status.get('icon', '❓')
                try:
                    icon_surface = FONTS['small'].render(status_icon, True,
                                                         COLORS['text'])  # Smaller font for compact circles
                    icon_rect = icon_surface.get_rect(center=circle_center)
                    self.screen.blit(icon_surface, icon_rect)
                except:
                    # Fallback icon если проблемы с отрисовкой
                    fallback_surface = FONTS['small'].render('●', True, COLORS['text'])
                    fallback_rect = fallback_surface.get_rect(center=circle_center)
                    self.screen.blit(fallback_surface, fallback_rect)

                # Draw remaining time as tiny text below circle - more compact
                remaining_hours = status.get('remaining_time', 0)
                if remaining_hours > 0:
                    try:
                        if remaining_hours >= 1:
                            time_text = f"{remaining_hours:.0f}ч"
                        else:
                            time_text = f"{remaining_hours:.1f}ч"
                        time_surface = FONTS['tiny'].render(time_text, True, COLORS['text'])
                        time_rect = time_surface.get_rect(center=(circle_x, circle_y + 12))  # Closer to circle
                        self.screen.blit(time_surface, time_rect)
                    except:
                        pass  # Игнорируем ошибки отрисовки времени

                # Tooltip on hover - безопасная проверка
                try:
                    circle_rect = pygame.Rect(circle_x - circle_size // 2, circle_y - circle_size // 2,
                                              circle_size, circle_size)
                    if circle_rect.collidepoint(mouse_pos):
                        self.draw_status_tooltip(status, mouse_pos)
                except:
                    pass  # Игнорируем ошибки тултипов

        # 🌙 Draw active dream warnings/motivations BEFORE permanent statuses
        dream_x_offset = 0
        mouse_pos = pygame.mouse.get_pos()

        if hasattr(self.game_state, 'dream_warnings'):
            dream_start_x = start_x + len(active_statuses) * circle_spacing + 20
            circle_center = (dream_start_x, bar_y + 30)

            # Red circle for warning dreams
            warning_color = COLORS['danger']
            pygame.draw.circle(self.screen, (150, 50, 50), circle_center, circle_size // 2 + 3)  # Glow
            pygame.draw.circle(self.screen, warning_color, circle_center, circle_size // 2)
            pygame.draw.circle(self.screen, (255, 100, 100), circle_center, circle_size // 2, 2)

            # Icon
            icon_surface = FONTS['small'].render('⚠️', True, COLORS['text'])
            icon_rect = icon_surface.get_rect(center=circle_center)
            self.screen.blit(icon_surface, icon_rect)

            # Label
            label_surface = FONTS['tiny'].render('СОН', True, warning_color)
            label_rect = label_surface.get_rect(center=(dream_start_x, bar_y + 30 + 12))
            self.screen.blit(label_surface, label_rect)

            # Tooltip
            circle_rect = pygame.Rect(dream_start_x - circle_size // 2, bar_y + 30 - circle_size // 2,
                                      circle_size, circle_size)
            if circle_rect.collidepoint(mouse_pos):
                warnings = self.game_state.dream_warnings
                if warnings['type'] == 'location':
                    tooltip_text = f"⚠️ Предупреждение сна: Избегайте {warnings['location']}"
                else:
                    tooltip_text = f"⚠️ Предупреждение сна: Избегайте {warnings['activity']}"
                self.draw_simple_tooltip(tooltip_text, mouse_pos)

            dream_x_offset = circle_spacing

        if hasattr(self.game_state, 'dream_motivations'):
            dream_start_x = start_x + len(active_statuses) * circle_spacing + 20 + dream_x_offset
            circle_center = (dream_start_x, bar_y + 30)

            # Green circle for motivating dreams
            motivation_color = COLORS['success']
            pygame.draw.circle(self.screen, (50, 150, 100), circle_center, circle_size // 2 + 3)  # Glow
            pygame.draw.circle(self.screen, motivation_color, circle_center, circle_size // 2)
            pygame.draw.circle(self.screen, (100, 255, 150), circle_center, circle_size // 2, 2)

            # Icon
            icon_surface = FONTS['small'].render('✨', True, COLORS['text'])
            icon_rect = icon_surface.get_rect(center=circle_center)
            self.screen.blit(icon_surface, icon_rect)

            # Label
            label_surface = FONTS['tiny'].render('СОН', True, motivation_color)
            label_rect = label_surface.get_rect(center=(dream_start_x, bar_y + 30 + 12))
            self.screen.blit(label_surface, label_rect)

            # Tooltip
            circle_rect = pygame.Rect(dream_start_x - circle_size // 2, bar_y + 30 - circle_size // 2,
                                      circle_size, circle_size)
            if circle_rect.collidepoint(mouse_pos):
                motivations = self.game_state.dream_motivations
                if motivations['type'] == 'location':
                    tooltip_text = f"✨ Мотивация сна: Посетите {motivations['location']}"
                else:
                    tooltip_text = f"✨ Мотивация сна: Выполните {motivations['activity']}"
                self.draw_simple_tooltip(tooltip_text, mouse_pos)

            dream_x_offset += circle_spacing

        # Draw permanent statuses (like cat blessing) at the end
        if hasattr(self.game_state, 'permanent_statuses') and self.game_state.permanent_statuses:
            # Calculate where to place permanent statuses
            permanent_start_x = start_x + len(active_statuses) * circle_spacing + 20 + dream_x_offset

            for perm_id, perm_status in self.game_state.permanent_statuses.items():
                if permanent_start_x + circle_size // 2 > bar_rect.right - 10:
                    break  # Не помещается

                circle_center = (permanent_start_x, bar_y + 30)

                # Special golden color for permanent statuses
                perm_color = (255, 215, 0)  # Gold color

                # Draw circle with golden glow effect
                pygame.draw.circle(self.screen, (255, 235, 100), circle_center, circle_size // 2 + 3)
                pygame.draw.circle(self.screen, perm_color, circle_center, circle_size // 2)
                pygame.draw.circle(self.screen, (255, 255, 255), circle_center, circle_size // 2, 2)

                # Draw icon
                perm_icon = perm_status.get('icon', '✨')
                try:
                    icon_surface = FONTS['small'].render(perm_icon, True, (0, 0, 0))
                    icon_rect = icon_surface.get_rect(center=circle_center)
                    self.screen.blit(icon_surface, icon_rect)
                except:
                    fallback_surface = FONTS['small'].render('✨', True, (0, 0, 0))
                    fallback_rect = fallback_surface.get_rect(center=circle_center)
                    self.screen.blit(fallback_surface, fallback_rect)

                # Draw "PERM" text below
                perm_text_surface = FONTS['tiny'].render('PERM', True, perm_color)
                perm_text_rect = perm_text_surface.get_rect(center=(permanent_start_x, bar_y + 30 + 12))
                self.screen.blit(perm_text_surface, perm_text_rect)

                # Tooltip for permanent status
                try:
                    perm_circle_rect = pygame.Rect(permanent_start_x - circle_size // 2, bar_y + 30 - circle_size // 2,
                                                   circle_size, circle_size)
                    if perm_circle_rect.collidepoint(mouse_pos):
                        self.draw_permanent_status_tooltip(perm_status, mouse_pos)
                except:
                    pass

                permanent_start_x += circle_spacing

    def draw_simple_tooltip(self, text, mouse_pos):
        """Простой тултип для снов и других элементов"""
        padding = 10
        line_height = 18

        # Рендерим текст
        text_surface = FONTS['small'].render(text, True, COLORS['text'])
        tooltip_width = text_surface.get_width() + padding * 2
        tooltip_height = line_height + padding * 2

        # Позиционирование
        tooltip_x = mouse_pos[0] + 15
        tooltip_y = mouse_pos[1] - tooltip_height - 15

        # Проверка границ экрана
        if tooltip_x + tooltip_width > WINDOW_WIDTH - 10:
            tooltip_x = mouse_pos[0] - tooltip_width - 15
        if tooltip_y < 10:
            tooltip_y = mouse_pos[1] + 15
        if tooltip_y + tooltip_height > WINDOW_HEIGHT - 10:
            tooltip_y = WINDOW_HEIGHT - tooltip_height - 10

        # Тень
        shadow_rect = pygame.Rect(tooltip_x + 3, tooltip_y + 3, tooltip_width, tooltip_height)
        shadow_surface = pygame.Surface((tooltip_width, tooltip_height))
        shadow_surface.set_alpha(80)
        shadow_surface.fill((0, 0, 0))
        self.screen.blit(shadow_surface, shadow_rect.topleft)

        # Основной тултип
        tooltip_rect = pygame.Rect(tooltip_x, tooltip_y, tooltip_width, tooltip_height)
        pygame.draw.rect(self.screen, COLORS['panel'], tooltip_rect, border_radius=8)
        pygame.draw.rect(self.screen, COLORS['accent'], tooltip_rect, 2, border_radius=8)

        # Текст
        self.screen.blit(text_surface, (tooltip_x + padding, tooltip_y + padding))

    def draw_permanent_status_tooltip(self, status, mouse_pos):
        """Draw tooltip for permanent status effect"""
        # Tooltip content
        lines = [
            f"{status['icon']} {status['name']}",
            status['description'],
            "🔒 Постоянный статус"
        ]

        # Add effect descriptions
        effects = status.get('effects', {})

        # Special handling for cat blessing
        if status.get('name') == 'Кошачье благословение':
            lines.append("📉 Дополнительно снижает стресс дома на 50%")
            lines.append("🧘 Дополнительно снижает паранойю дома на 50%")
            lines.append("✨ Дает -5 стресса и -2 паранойи за каждый час дома")
        else:
            # Standard effect descriptions for other statuses
            if 'home_stress_reduction' in effects:
                lines.append(f"📉 Снижение стресса дома: +{effects['home_stress_reduction']}%")
            if 'home_paranoia_reduction' in effects:
                lines.append(f"🧘 Снижение паранойи дома: +{effects['home_paranoia_reduction']}%")

        # Calculate tooltip size
        max_width = 0
        line_height = 18
        padding = 10

        line_surfaces = []
        for i, line in enumerate(lines):
            if i == 0:
                color = (255, 215, 0)  # Gold for title
            elif i == 2:
                color = (255, 215, 0)  # Gold for "permanent"
            else:
                color = COLORS['text']
            surface = FONTS['small'].render(line, True, color)
            line_surfaces.append(surface)
            max_width = max(max_width, surface.get_width())

        tooltip_width = max_width + padding * 2
        tooltip_height = len(lines) * line_height + padding * 2

        # Smart positioning
        tooltip_x = mouse_pos[0] + 15
        tooltip_y = mouse_pos[1] - tooltip_height - 15

        # Check screen bounds
        if tooltip_x + tooltip_width > WINDOW_WIDTH - 10:
            tooltip_x = mouse_pos[0] - tooltip_width - 15
        if tooltip_y < 10:
            tooltip_y = mouse_pos[1] + 15
        if tooltip_y + tooltip_height > WINDOW_HEIGHT - 10:
            tooltip_y = WINDOW_HEIGHT - tooltip_height - 10

        # Draw shadow
        shadow_rect = pygame.Rect(tooltip_x + 3, tooltip_y + 3, tooltip_width, tooltip_height)
        shadow_surface = pygame.Surface((tooltip_width, tooltip_height))
        shadow_surface.set_alpha(80)
        shadow_surface.fill((0, 0, 0))
        self.screen.blit(shadow_surface, shadow_rect.topleft)

        # Main tooltip with golden border
        tooltip_rect = pygame.Rect(tooltip_x, tooltip_y, tooltip_width, tooltip_height)
        pygame.draw.rect(self.screen, COLORS['panel'], tooltip_rect, border_radius=8)
        pygame.draw.rect(self.screen, (255, 215, 0), tooltip_rect, 2, border_radius=8)

        # Draw text lines
        y_offset = tooltip_y + padding
        for surface in line_surfaces:
            self.screen.blit(surface, (tooltip_x + padding, y_offset))
            y_offset += line_height

    def draw_status_tooltip(self, status, mouse_pos):
        """Draw tooltip for status effect"""
        # Tooltip content
        lines = [
            f"{status['icon']} {status['name']}",
            status['description'],
            f"Осталось: {status['remaining_time']:.1f} часов"
        ]

        # Calculate tooltip size
        max_width = 0
        line_height = 18
        padding = 10

        line_surfaces = []
        for i, line in enumerate(lines):
            color = COLORS['accent'] if i == 0 else COLORS['text']
            if i == 2:  # Time line
                color = COLORS['text_dim']
            surface = FONTS['small'].render(line, True, color)
            line_surfaces.append(surface)
            max_width = max(max_width, surface.get_width())

        tooltip_width = max_width + padding * 2
        tooltip_height = len(lines) * line_height + padding * 2

        # Smart positioning
        tooltip_x = mouse_pos[0] + 15
        tooltip_y = mouse_pos[1] - tooltip_height - 15

        # Check screen bounds
        if tooltip_x + tooltip_width > WINDOW_WIDTH - 10:
            tooltip_x = mouse_pos[0] - tooltip_width - 15
        if tooltip_y < 10:
            tooltip_y = mouse_pos[1] + 15
        if tooltip_y + tooltip_height > WINDOW_HEIGHT - 10:
            tooltip_y = WINDOW_HEIGHT - tooltip_height - 10

        # Draw shadow
        shadow_rect = pygame.Rect(tooltip_x + 3, tooltip_y + 3, tooltip_width, tooltip_height)
        shadow_surface = pygame.Surface((tooltip_width, tooltip_height))
        shadow_surface.set_alpha(80)
        shadow_surface.fill((0, 0, 0))
        self.screen.blit(shadow_surface, shadow_rect.topleft)

        # Draw main tooltip
        tooltip_rect = pygame.Rect(tooltip_x, tooltip_y, tooltip_width, tooltip_height)
        pygame.draw.rect(self.screen, COLORS['panel'], tooltip_rect, border_radius=8)
        pygame.draw.rect(self.screen, COLORS['accent'], tooltip_rect, 2, border_radius=8)

        # Draw text lines
        y_offset = tooltip_y + padding
        for surface in line_surfaces:
            self.screen.blit(surface, (tooltip_x + padding, y_offset))
            y_offset += line_height

    def get_smart_activity_name(self, activity_name, available_width, font):
        """Smart text truncation for activity names"""
        # Словарь сокращений для частых слов
        abbreviations = {
            'Завтрак': 'Завтрак',
            'Работа/Учеба': 'Работа',
            'Утренняя пробежка': 'Пробежка',
            'Обед с друзьями': 'Обед',
            'Вечерняя прогулка': 'Прогулка',
            'Подготовка ко сну': 'Сон',
            'Покупки': 'Магазин'
        }

        # Сначала попробуем готовые сокращения
        if activity_name in abbreviations:
            short_name = abbreviations[activity_name]
            if font.render(short_name, True, COLORS['text']).get_width() <= available_width:
                return short_name

        # Если не подходит, используем умное сокращение
        test_surface = font.render(activity_name, True, COLORS['text'])
        if test_surface.get_width() <= available_width:
            return activity_name

        # Попробуем убрать артикли и предлоги
        words = activity_name.split()
        if len(words) > 1:
            # Убираем служебные слова
            filtered_words = [word for word in words if word.lower() not in ['с', 'в', 'на', 'ко', 'и']]
            if len(filtered_words) >= 1:
                candidate = ' '.join(filtered_words[:2])  # Берем первые 2 значимых слова
                if font.render(candidate, True, COLORS['text']).get_width() <= available_width:
                    return candidate

                # Если не помещается, берем первое слово
                if font.render(filtered_words[0], True, COLORS['text']).get_width() <= available_width:
                    return filtered_words[0]

        # В крайнем случае обрезаем по символам
        for i in range(len(activity_name), 3, -1):
            candidate = activity_name[:i - 3] + "..."
            if font.render(candidate, True, COLORS['text']).get_width() <= available_width:
                return candidate

        return "..."

    def draw_timeline_activity(self, timeline_activity):
        """Draw a single activity on the timeline with improved text handling"""
        activity = timeline_activity.activity
        rect = timeline_activity.rect

        # Choose color based on conflicts
        if timeline_activity.has_conflict:
            color = COLORS['activity_conflict']
        elif timeline_activity.dragging:
            color = COLORS['button_hover']
        else:
            color = COLORS['activity_placed']

        # Draw activity rectangle with gradient effect for better visibility
        pygame.draw.rect(self.screen, color, rect, border_radius=5)

        # Add subtle inner highlight
        highlight_color = tuple(min(255, c + 20) for c in color)
        highlight_rect = pygame.Rect(rect.x + 1, rect.y + 1, rect.width - 2, 6)
        pygame.draw.rect(self.screen, highlight_color, highlight_rect, border_radius=3)

        pygame.draw.rect(self.screen, COLORS['accent'], rect, 2, border_radius=5)

        # Calculate available space more precisely
        icon_width = 20
        time_width = 65  # Примерная ширина времени
        padding = 10
        available_text_width = rect.width - icon_width - time_width - padding

        # Draw icon
        icon_surface = FONTS['small'].render(activity['icon'], True, COLORS['text'])
        icon_x = rect.x + 3
        icon_y = rect.y + (rect.height - icon_surface.get_height()) // 2
        self.screen.blit(icon_surface, (icon_x, icon_y))

        # Smart name truncation
        name_text = self.get_smart_activity_name(activity['name'], available_text_width, FONTS['small'])
        name_surface = FONTS['small'].render(name_text, True, COLORS['text'])

        name_x = icon_x + icon_width + 2
        name_y = rect.y + 4

        # Add text shadow for better readability
        shadow_surface = FONTS['small'].render(name_text, True, (0, 0, 0))
        self.screen.blit(shadow_surface, (name_x + 1, name_y + 1))
        self.screen.blit(name_surface, (name_x, name_y))

        # Draw time in compact format supporting half-hours
        start_time = timeline_activity.start_time
        end_time = timeline_activity.end_time

        def format_time(time):
            hours = int(time)
            minutes = int((time % 1) * 60)
            if minutes == 0:
                return f"{hours}:00"
            else:
                return f"{hours}:{minutes:02d}"

        # Компактный формат времени с поддержкой получаса
        time_text = f"{format_time(start_time)}-{format_time(end_time)}"

        time_surface = FONTS['tiny'].render(time_text, True, COLORS['text_dim'])
        time_x = rect.right - time_surface.get_width() - 3
        time_y = rect.y + rect.height - 13

        # Time background for better readability
        time_bg_rect = pygame.Rect(time_x - 2, time_y - 1, time_surface.get_width() + 4, 12)
        time_bg_surface = pygame.Surface((time_bg_rect.width, time_bg_rect.height))
        time_bg_surface.set_alpha(128)
        time_bg_surface.fill((0, 0, 0))
        self.screen.blit(time_bg_surface, time_bg_rect)

        self.screen.blit(time_surface, (time_x, time_y))

        # Store tooltip info for later rendering (will be drawn on top of everything)
        # But only if no event popup is active
        if not self.game_state.show_event_popup:
            mouse_pos = pygame.mouse.get_pos()
            if rect.collidepoint(mouse_pos):
                # Store tooltip data for rendering at the end
                if not hasattr(self, 'pending_tooltip'):
                    self.pending_tooltip = None
                self.pending_tooltip = (activity, mouse_pos)

    def draw_activity_tooltips(self):
        """Draw activity tooltips on top of everything else"""
        # Don't show activity tooltips during event popup
        if self.game_state.show_event_popup:
            return

        # Clear tooltip data at the start of each frame
        if not hasattr(self, 'pending_tooltip'):
            return

        if self.pending_tooltip is None:
            return

        activity, mouse_pos = self.pending_tooltip

        # Draw tooltip with enhanced styling and improved positioning
        lines = [
            f"{activity['icon']} {activity['name']}",
            f"Длительность: {activity['duration']} час(а)",
            f"Локация: {self.get_location_name(activity['location'])}",
            f"Энергия: {activity['energy_recovery']:+d}",
            f"Стресс: {self.game_state.get_adapted_stress_recovery(activity):+d}"
        ]

        # Add adaptation info for positive stress activities
        if activity.get('stress_recovery', 0) < 0:
            adaptation_status = self.game_state.get_adaptation_status_text(activity)
            if adaptation_status:
                effectiveness = self.game_state.activity_adaptation.get(activity['name'], {}).get('effectiveness', 1.0)
                lines.append(f"📉 Эффективность: {int(effectiveness * 100)}%")

        if activity['mandatory']:
            lines.append("⚠️ Обязательная активность")

        # Calculate tooltip size with improved styling
        max_width = 0
        line_height = 20  # Увеличен для лучшей читаемости
        padding = 12  # Увеличен отступ

        line_surfaces = []
        for line in lines:
            surface = FONTS['small'].render(line, True, COLORS['text'])
            line_surfaces.append(surface)
            max_width = max(max_width, surface.get_width())

        tooltip_width = max_width + padding * 2
        tooltip_height = len(lines) * line_height + padding * 2

        # Smart positioning to avoid screen edges
        tooltip_x = mouse_pos[0] + 15  # Увеличен отступ от курсора
        tooltip_y = mouse_pos[1] - tooltip_height - 15

        # Проверка границ экрана с улучшенной логикой
        if tooltip_x + tooltip_width > WINDOW_WIDTH - 10:
            tooltip_x = mouse_pos[0] - tooltip_width - 15
        if tooltip_y < 10:
            tooltip_y = mouse_pos[1] + 15

        # Дополнительная проверка, чтобы тултип не выходил за нижний край
        if tooltip_y + tooltip_height > WINDOW_HEIGHT - 10:
            tooltip_y = WINDOW_HEIGHT - tooltip_height - 10

        # Enhanced shadow effect
        shadow_rect = pygame.Rect(tooltip_x + 3, tooltip_y + 3, tooltip_width, tooltip_height)
        shadow_surface = pygame.Surface((tooltip_width, tooltip_height))
        shadow_surface.set_alpha(80)
        shadow_surface.fill((0, 0, 0))
        self.screen.blit(shadow_surface, shadow_rect.topleft)

        # Main tooltip background with gradient effect
        tooltip_rect = pygame.Rect(tooltip_x, tooltip_y, tooltip_width, tooltip_height)

        # Background
        pygame.draw.rect(self.screen, COLORS['panel'], tooltip_rect, border_radius=8)

        # Subtle inner highlight
        highlight_rect = pygame.Rect(tooltip_x + 1, tooltip_y + 1, tooltip_width - 2, 8)
        highlight_color = tuple(min(255, c + 15) for c in COLORS['panel'])
        pygame.draw.rect(self.screen, highlight_color, highlight_rect, border_radius=6)

        # Border
        pygame.draw.rect(self.screen, COLORS['accent'], tooltip_rect, 2, border_radius=8)

        # Draw text lines with improved spacing
        y_offset = tooltip_y + padding
        for i, surface in enumerate(line_surfaces):
            # Highlight the first line (activity name)
            if i == 0:
                text_color = COLORS['accent']
                # Redraw first line with accent color
                line_text = lines[0]
                surface = FONTS['small'].render(line_text, True, text_color)

            self.screen.blit(surface, (tooltip_x + padding, y_offset))
            y_offset += line_height

        # Clear tooltip data after drawing
        self.pending_tooltip = None

    def draw_game_ending_screen(self):
        """Draw the game ending screen"""
        if self.game_state.phase != 'game_ending' or not hasattr(self.game_state, 'current_ending'):
            return

        # Full screen overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.fill(COLORS['bg'])
        self.screen.blit(overlay, (0, 0))

    def draw_dream_screen(self):
        """🌙 Отрисовка экрана сновидения"""
        if not hasattr(self.game_state, 'current_dream'):
            return

        dream = self.game_state.current_dream

        # Тёмный фон с градиентом
        for i in range(WINDOW_HEIGHT // 3):
            alpha = 200 - (i)
            gradient_surface = pygame.Surface((WINDOW_WIDTH, 3))
            gradient_surface.set_alpha(max(20, alpha))
            gradient_surface.fill((5, 5, 15))
            self.screen.blit(gradient_surface, (0, i * 3))

        # Определяем цвет в зависимости от типа сна
        dream_id = dream.get('id', '')
        if 'calm' in dream_id:
            accent_color = (100, 200, 150)  # Зелёный
        elif 'lucid' in dream_id:
            accent_color = (150, 100, 255)  # Фиолетовый
        elif 'dark' in dream_id:
            accent_color = (255, 150, 80)  # Оранжевый
        elif 'nightmare' in dream_id:
            accent_color = (255, 80, 80)  # Красный
        else:
            accent_color = (150, 150, 200)  # Синий

        # Главная панель
        content_rect = pygame.Rect(150, 100, WINDOW_WIDTH - 300, WINDOW_HEIGHT - 200)
        panel_surface = pygame.Surface((content_rect.width, content_rect.height))
        panel_surface.set_alpha(220)
        panel_surface.fill((15, 15, 30))
        self.screen.blit(panel_surface, content_rect)

        # Рамка с эффектом свечения
        pygame.draw.rect(self.screen, accent_color, content_rect, 3, border_radius=10)

        # Заголовок
        y_pos = content_rect.y + 40
        title_text = FONTS['title'].render("🌙 СНОВИДЕНИЕ 🌙", True, accent_color)
        title_rect = title_text.get_rect(center=(WINDOW_WIDTH // 2, y_pos))
        self.screen.blit(title_text, title_rect)

        # Название сна
        y_pos += 60
        name_text = FONTS['large'].render(dream['name'], True, COLORS['text'])
        name_rect = name_text.get_rect(center=(WINDOW_WIDTH // 2, y_pos))
        self.screen.blit(name_text, name_rect)

        # Описание сна (многострочное)
        y_pos += 60
        description = dream['description']
        max_width = content_rect.width - 100

        # Разбиваем текст на строки
        words = description.split(' ')
        lines = []
        current_line = []

        for word in words:
            test_line = ' '.join(current_line + [word])
            test_surface = FONTS['medium'].render(test_line, True, COLORS['text'])
            if test_surface.get_width() <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        if current_line:
            lines.append(' '.join(current_line))

        # Отрисовываем строки
        for line in lines:
            line_surface = FONTS['medium'].render(line, True, COLORS['text_dim'])
            line_rect = line_surface.get_rect(center=(WINDOW_WIDTH // 2, y_pos))
            self.screen.blit(line_surface, line_rect)
            y_pos += 35

        # Эффекты сна
        y_pos += 30
        effects_title = FONTS['medium'].render("Эффекты:", True, accent_color)
        effects_rect = effects_title.get_rect(center=(WINDOW_WIDTH // 2, y_pos))
        self.screen.blit(effects_title, effects_rect)

        y_pos += 40
        effects = dream.get('effects', {})
        for effect_name, effect_value in effects.items():
            if effect_value != 0:
                sign = '+' if effect_value > 0 else ''
                effect_map = {
                    'stress': '💥 Стресс',
                    'paranoia': '👁️ Паранойя',
                    'energy': '⚡ Энергия'
                }
                effect_text_str = f"{effect_map.get(effect_name, effect_name)}: {sign}{effect_value}"
                effect_color = COLORS['success'] if effect_value < 0 else COLORS['warning']
                effect_text = FONTS['small'].render(effect_text_str, True, effect_color)
                effect_rect = effect_text.get_rect(center=(WINDOW_WIDTH // 2, y_pos))
                self.screen.blit(effect_text, effect_rect)
                y_pos += 30

        # Подсказка
        if 'hint' in dream:
            y_pos += 20
            hint_text = FONTS['small'].render(f"💡 {dream['hint']}", True, COLORS['text_dim'])
            hint_rect = hint_text.get_rect(center=(WINDOW_WIDTH // 2, y_pos))
            self.screen.blit(hint_text, hint_rect)

        # Кнопка продолжения
        button_y = content_rect.bottom - 60
        continue_btn = Button(WINDOW_WIDTH // 2 - 100, button_y, 200, 40, "Проснуться", 'medium')

        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = pygame.mouse.get_pressed()[0]

        if (continue_btn.update(mouse_pos, mouse_clicked) and
                self.can_click_button('dream_wake')):
            self.register_button_click('dream_wake')
            # Завершаем фазу сна
            self.complete_dream_phase()

        continue_btn.draw(self.screen)

    def draw_game_ending_screen(self):
        """Draw the game ending screen"""
        ending = self.game_state.current_ending
        ending_type = ending['type']

        # Background color based on ending type
        if ending_type == 'good':
            bg_color = (20, 40, 20)  # Dark green
            accent_color = COLORS['success']
        elif ending_type == 'neutral':
            bg_color = (30, 30, 40)  # Dark blue-gray
            accent_color = COLORS['accent']
        else:  # bad
            bg_color = (40, 20, 20)  # Dark red
            accent_color = COLORS['danger']

        # Background gradient effect
        for i in range(WINDOW_HEIGHT // 4):
            alpha = 255 - (i * 2)
            gradient_surface = pygame.Surface((WINDOW_WIDTH, 4))
            gradient_surface.set_alpha(max(0, alpha))
            gradient_surface.fill(bg_color)
            self.screen.blit(gradient_surface, (0, i * 4))

        # Main content area
        content_rect = pygame.Rect(100, 80, WINDOW_WIDTH - 200, WINDOW_HEIGHT - 160)

        # Semi-transparent background panel
        panel_surface = pygame.Surface((content_rect.width, content_rect.height))
        panel_surface.set_alpha(200)
        panel_surface.fill(COLORS['panel'])
        self.screen.blit(panel_surface, content_rect)

        # Panel border
        pygame.draw.rect(self.screen, accent_color, content_rect, 3, border_radius=15)

        # Title
        title_surface = FONTS['title'].render(ending['title'], True, accent_color)
        title_rect = title_surface.get_rect(centerx=WINDOW_WIDTH // 2, y=content_rect.y + 20)
        self.screen.blit(title_surface, title_rect)

        # Final stats
        stats = ending['stats']
        stats_y = title_rect.bottom + 30

        # Main mental health stats
        main_stats_text = f"Финальные показатели: Стресс {int(stats['final_stress'])}% • Паранойя {int(stats['final_paranoia'])}% • Отношения с голосом {stats['voice_relationship']:+d}"
        main_stats_surface = FONTS['small'].render(main_stats_text, True, COLORS['text'])
        main_stats_rect = main_stats_surface.get_rect(centerx=WINDOW_WIDTH // 2, y=stats_y)
        self.screen.blit(main_stats_surface, main_stats_rect)

        # Task completion stats (if voice system was active)
        if stats['total_tasks_assigned'] > 0:
            task_stats_y = main_stats_rect.bottom + 10
            completion_percentage = int(stats['task_completion_rate'] * 100)

            task_stats_text = f"Задания от голоса: {stats['total_tasks_completed']}/{stats['total_tasks_assigned']} выполнено ({completion_percentage}%)"

            # Color based on completion rate
            if completion_percentage >= 80:
                task_color = COLORS['success']
            elif completion_percentage >= 50:
                task_color = COLORS['warning']
            else:
                task_color = COLORS['danger']

            task_stats_surface = FONTS['small'].render(task_stats_text, True, task_color)
            task_stats_rect = task_stats_surface.get_rect(centerx=WINDOW_WIDTH // 2, y=task_stats_y)
            self.screen.blit(task_stats_surface, task_stats_rect)

        else:
            stats_rect = main_stats_rect

        # Story text
        story_start_y = task_stats_rect.bottom + 40
        line_height = 22
        current_y = story_start_y

        for line in ending['description']:
            if current_y > content_rect.bottom - 100:  # Leave space for button
                break

            if line == '':  # Empty line for spacing
                current_y += line_height // 2
                continue

            # Different styling for special lines
            if line.startswith('🎭'):  # Voice lines
                line_color = accent_color
                font = FONTS['medium']
            elif line.startswith(('🌟', '⚖️', '🌑')):  # Title lines
                line_color = accent_color
                font = FONTS['large']
            else:
                line_color = COLORS['text']
                font = FONTS['small']

            # Word wrapping for long lines
            if font.size(line)[0] > content_rect.width - 40:
                words = line.split()
                current_line = []
                for word in words:
                    test_line = ' '.join(current_line + [word])
                    if font.size(test_line)[0] <= content_rect.width - 40:
                        current_line.append(word)
                    else:
                        if current_line:
                            line_surface = font.render(' '.join(current_line), True, line_color)
                            line_rect = line_surface.get_rect(centerx=WINDOW_WIDTH // 2, y=current_y)
                            self.screen.blit(line_surface, line_rect)
                            current_y += line_height
                            current_line = [word]
                        else:
                            # Word too long, just draw it
                            line_surface = font.render(word, True, line_color)
                            line_rect = line_surface.get_rect(centerx=WINDOW_WIDTH // 2, y=current_y)
                            self.screen.blit(line_surface, line_rect)
                            current_y += line_height

                if current_line:
                    line_surface = font.render(' '.join(current_line), True, line_color)
                    line_rect = line_surface.get_rect(centerx=WINDOW_WIDTH // 2, y=current_y)
                    self.screen.blit(line_surface, line_rect)
                    current_y += line_height
            else:
                line_surface = font.render(line, True, line_color)
                line_rect = line_surface.get_rect(centerx=WINDOW_WIDTH // 2, y=current_y)
                self.screen.blit(line_surface, line_rect)
                current_y += line_height

        # Restart button
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = pygame.mouse.get_pressed()[0]

        restart_btn = Button(WINDOW_WIDTH // 2 - 100, content_rect.bottom - 60, 200, 40,
                             "Начать заново", 'medium')

        if (restart_btn.update(mouse_pos, mouse_clicked) and
                self.can_click_button('ending_restart')):
            self.register_button_click('ending_restart')
            # Restart the game completely
            self.restart_game_completely()
        else:
            restart_btn.update(mouse_pos, False)

        restart_btn.draw(self.screen)

    def draw_restart_transition(self):
        """Draw restart transition effects"""
        if not hasattr(self, 'restart_transition_phase'):
            return False

        current_time = pygame.time.get_ticks()
        elapsed = current_time - self.restart_transition_start_time
        progress = min(1.0, elapsed / self.restart_transition_duration)

        if self.restart_transition_phase == 'black_screen':
            # Fill screen with black
            self.screen.fill((0, 0, 0))

            # Fade in text "Цикл продолжается вновь..."
            text_alpha = int(255 * min(1.0, progress * 2))  # Fade in faster
            text = "Цикл продолжается вновь..."

            # Create text surface
            text_surface = FONTS['title'].render(text, True, (255, 255, 255))
            text_surface.set_alpha(text_alpha)

            # Center the text
            text_rect = text_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            self.screen.blit(text_surface, text_rect)

        elif self.restart_transition_phase == 'white_screen':
            # Fill screen with white
            self.screen.fill((255, 255, 255))

            # Optional: Add fade out effect for white screen
            # Make the white gradually fade to normal background
            if progress > 0.7:  # Start fading in the last 30% of white screen duration
                fade_progress = (progress - 0.7) / 0.3
                overlay_alpha = int(255 * (1 - fade_progress))

                # Draw background
                self.screen.fill(COLORS['bg'])

                # Overlay white with decreasing alpha
                white_overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
                white_overlay.set_alpha(overlay_alpha)
                white_overlay.fill((255, 255, 255))
                self.screen.blit(white_overlay, (0, 0))

        return True

    def draw_event_choice_tooltips(self):
        """Draw tooltips for event choice buttons"""
        if not hasattr(self, 'pending_event_tooltip') or self.pending_event_tooltip is None:
            return

        if not self.game_state.show_event_popup or not self.game_state.current_event:
            return

        choice_type, mouse_pos = self.pending_event_tooltip
        event = self.game_state.current_event

        # Get tooltip info for this choice
        tooltip_info = self.get_event_choice_tooltip(event, choice_type)

        if not tooltip_info['effects']:
            return

        # Create tooltip content
        lines = [f"📊 Последствия выбора:"]
        lines.extend([f"  {effect}" for effect in tooltip_info['effects']])
        lines.append("")
        lines.append(f"💡 {tooltip_info['description']}")

        # Calculate tooltip size
        max_width = 0
        line_height = 18
        padding = 10

        line_surfaces = []
        for i, line in enumerate(lines):
            color = COLORS['accent'] if i == 0 else COLORS['text']
            if line.strip().startswith('💡'):
                color = COLORS['text_dim']
            surface = FONTS['small'].render(line, True, color)
            line_surfaces.append(surface)
            max_width = max(max_width, surface.get_width())

        tooltip_width = max_width + padding * 2
        tooltip_height = len(lines) * line_height + padding * 2

        # Smart positioning
        tooltip_x = mouse_pos[0] + 15
        tooltip_y = mouse_pos[1] - tooltip_height - 15

        # Check screen bounds
        if tooltip_x + tooltip_width > WINDOW_WIDTH - 10:
            tooltip_x = mouse_pos[0] - tooltip_width - 15
        if tooltip_y < 10:
            tooltip_y = mouse_pos[1] + 15
        if tooltip_y + tooltip_height > WINDOW_HEIGHT - 10:
            tooltip_y = WINDOW_HEIGHT - tooltip_height - 10

        # Draw shadow
        shadow_rect = pygame.Rect(tooltip_x + 3, tooltip_y + 3, tooltip_width, tooltip_height)
        shadow_surface = pygame.Surface((tooltip_width, tooltip_height))
        shadow_surface.set_alpha(80)
        shadow_surface.fill((0, 0, 0))
        self.screen.blit(shadow_surface, shadow_rect.topleft)

        # Draw main tooltip
        tooltip_rect = pygame.Rect(tooltip_x, tooltip_y, tooltip_width, tooltip_height)
        pygame.draw.rect(self.screen, COLORS['panel'], tooltip_rect, border_radius=8)
        pygame.draw.rect(self.screen, COLORS['accent'], tooltip_rect, 2, border_radius=8)

        # Draw text lines
        y_offset = tooltip_y + padding
        for surface in line_surfaces:
            self.screen.blit(surface, (tooltip_x + padding, y_offset))
            y_offset += line_height

        # Clear tooltip data after drawing
        self.pending_event_tooltip = None

    def draw_activity_tooltip(self, activity, mouse_pos):
        """Legacy method - now redirects to the new system"""
        # This method is kept for compatibility but functionality moved to draw_activity_tooltips
        pass

    def get_location_name(self, location):
        """Get human-readable location name"""
        location_names = {
            'home': 'Дом',
            'office': 'Офис/Учеба',
            'outdoor': 'На улице',
            'store': 'Магазин',
            'restaurant': 'Ресторан',
            'gym': 'Спортзал',
            'cinema': 'Кинотеатр'
        }
        return location_names.get(location, location.title())

    def draw_phase_instructions(self):
        """Draw instructions based on current phase"""
        panel_rect = pygame.Rect(20, 170, 460, 200)
        pygame.draw.rect(self.screen, COLORS['panel'], panel_rect)
        pygame.draw.rect(self.screen, COLORS['accent'], panel_rect, 2)

        # Title
        title_surface = FONTS['medium'].render("Инструкции", True, COLORS['text'])
        self.screen.blit(title_surface, (30, 180))

        y_offset = 210

        if self.game_state.phase == 'game_over':
            # Game over screen
            instructions = [
                "ИГРА ОКОНЧЕНА!",
                "",
                f"Причина: {getattr(self.game_state, 'game_over_reason', 'Неизвестно')}",
                "",
                f"День: {self.game_state.day}",
                f"Энергия: {self.game_state.energy}",
                f"Стресс: {self.game_state.stress}",
                f"Паранойя: {self.game_state.paranoia}",
                "",
                "Нажмите 'Новый день'",
                "чтобы начать заново"
            ]
        elif self.game_state.phase == 'game_ending':
            # Game ending screen
            instructions = [
                "30 ДНЕЙ ПРОШЛО",
                "",
                "История завершена!",
                "",
                "Прочитайте концовку",
                "и узнайте, чем",
                "закончилось ваше",
                "путешествие.",
                "",
                "Нажмите кнопку",
                "'Начать заново'",
                "чтобы попробовать",
                "получить другую",
                "концовку"
            ]
        elif self.game_state.phase == 'planning':
            instructions = [
                "1. Выберите активность",
                "2. Перетащите на временную шкалу",
                "3. Включите все обязательные",
                "4. Начните день",
                "",
                "Управление:",
                "ПКМ - удалить с шкалы",
                "Сохранить/Загрузить - распорядок",
                "C - очистить шкалу",
                "H - помощь",
                "Space - начать день"
            ]
        elif self.game_state.phase == 'execution':
            scheduled_activities = self.game_state.get_planned_schedule()
            current_day_name = self.game_state.weekdays[self.game_state.day_of_week]
            instructions = [
                f"День {self.game_state.day} - {current_day_name}",
                "выполняется...",
                "",
                f"Активность: {self.game_state.current_activity_index + 1}/{len(scheduled_activities)}",
                "",
                "Нажмите 'Далее'",
                "для продолжения",
                "",
                "Space - продолжить"
            ]
        else:  # results
            current_day_name = self.game_state.weekdays[self.game_state.day_of_week]
            instructions = [
                f"День {self.game_state.day} - {current_day_name}",
                "завершен!",
                "",
                "Просмотрите результаты",
                "и начните новый день",
                "",
                "Нажмите 'Новый день'",
                "",
                "Space - новый день"
            ]

        for instruction in instructions:
            if y_offset > 350:
                break
            instruction_surface = FONTS['small'].render(instruction, True, COLORS['text'])
            self.screen.blit(instruction_surface, (40, y_offset))
            y_offset += 18

    def draw_buttons(self):
        """Draw all buttons"""
        for button_name, button in self.buttons.items():
            # Show/hide buttons based on phase
            if button_name == 'start_day' and self.game_state.phase != 'planning':
                continue
            if button_name == 'next_phase' and self.game_state.phase in ['planning', 'game_over', 'game_ending']:
                continue
            if button_name == 'new_day' and self.game_state.phase not in ['results', 'game_over']:
                continue
            if button_name == 'clear_timeline' and self.game_state.phase != 'planning':
                continue
            if button_name in ['save_schedule', 'load_schedule'] and self.game_state.phase != 'planning':
                continue

            # Hide most buttons during ending screen
            if self.game_state.phase == 'game_ending' and button_name not in ['help', 'music_toggle']:
                continue

            # Update button text dynamically for system unlock buttons
            if button_name == 'cards_panel':
                button.text = "Карты" if self.game_state.day >= 5 else "???"
            elif button_name == 'voice_panel':
                button.text = "Голос" if self.game_state.day >= 3 else "???"

            # Check if button should be disabled
            disabled = False
            if button_name == 'cards_panel' and self.game_state.day < 5:
                disabled = True
            elif button_name == 'voice_panel' and self.game_state.day < 3:
                disabled = True

            button.draw(self.screen, disabled)

    def draw_messages(self):
        """Draw message system"""
        # Position messages below status effects bar and buttons - moved even lower
        status_bar_bottom = self.game_state.timeline_rect.bottom + 53  # Adjusted for new smaller status bar height
        y_offset = max(WINDOW_HEIGHT - 80, status_bar_bottom + 20)  # More space below status bar

        for i, message in enumerate(reversed(self.game_state.messages[-3:])):  # Show last 3 messages
            # Message background
            text_surface = FONTS['small'].render(message['text'], True, COLORS['text'])
            bg_rect = pygame.Rect(20, y_offset, text_surface.get_width() + 20, 25)

            # Color based on message type
            bg_color = COLORS['panel']
            if message['type'] == 'success':
                bg_color = COLORS['success']
            elif message['type'] == 'warning':
                bg_color = COLORS['warning']
            elif message['type'] == 'danger':
                bg_color = COLORS['danger']

            # Fade based on age
            age = time.time() - message['time']
            alpha = max(50, 255 - int(age * 85))  # Fade over 3 seconds

            # Draw background with alpha
            fade_surface = pygame.Surface((bg_rect.width, bg_rect.height))
            fade_surface.set_alpha(alpha)
            fade_surface.fill(bg_color)
            self.screen.blit(fade_surface, bg_rect)

            # Draw text
            text_surface.set_alpha(alpha)
            self.screen.blit(text_surface, (30, y_offset + 3))

            y_offset -= 30

    def draw_help_panel(self):
        """Draw help panel if active"""
        if not self.game_state.show_help:
            return

        # Semi-transparent overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        # Help panel
        help_rect = pygame.Rect(200, 100, 800, 600)
        pygame.draw.rect(self.screen, COLORS['panel'], help_rect)
        pygame.draw.rect(self.screen, COLORS['accent'], help_rect, 3)

        # Title
        title_surface = FONTS['title'].render("Phyco Phycles - Помощь", True, COLORS['text'])
        self.screen.blit(title_surface, (220, 120))

        # Help content
        help_content = [
            "",
            "ЦЕЛЬ:",
            "Планируйте и выполняйте ежедневные активности, управляя ментальным здоровьем.",
            "",
            "МЕНТАЛЬНОЕ СОСТОЯНИЕ:",
            "• Энергия: Уменьшается с активностями, увеличивается с отдыхом",
            "• Стресс: Увеличивается со сложными активностями и событиями",
            "• Паранойя: Увеличивается с подозрительными событиями",
            "",
            "ПЛАНИРОВАНИЕ:",
            "• Красная граница = Обязательная активность",
            "• Синяя граница = Необязательная активность",
            "• Перетащите активности на временную шкалу",
            "• ПКМ на активности в шкале = удалить",
            "",
            "ФАЗЫ:",
            "1. Планирование: Размещайте активности на временной шкале",
            "2. Выполнение: Активности выполняются автоматически",
            "3. Результаты: Просмотр дня и начало нового",
            "",
            "УПРАВЛЕНИЕ:",
            "• Мышь: Перетаскивание и взаимодействие",
            "• H: Вкл/выкл эту помощь",
            "• Space: Переход к следующей фазе",
            "• C: Очистить временную шкалу",
            "• ПКМ: Удалить активность с шкалы",
            "",
            "Нажмите H или кликните в другом месте, чтобы закрыть"
        ]

        y_offset = 160
        for line in help_content:
            if y_offset > 650:
                break
            text_surface = FONTS['small'].render(line, True, COLORS['text'])
            self.screen.blit(text_surface, (220, y_offset))
            y_offset += 20

    def is_currently_executing_activity(self):
        """Проверяем, выполняется ли сейчас какая-то активность"""
        if self.game_state.phase != 'execution':
            return False

        scheduled_activities = self.game_state.get_planned_schedule()
        current_time = self.game_state.current_time

        # Проверяем, находится ли текущее время внутри какой-либо активности
        for activity in scheduled_activities:
            if activity.start_time <= current_time < activity.end_time:
                return True

        return False

    def can_use_time_solution(self, event):
        """Check if time-based solution is available"""
        if self.game_state.phase != 'execution':
            return True  # During planning, all options available

        # ВАЖНО: Если событие происходит во время выполнения активности, блокируем временное решение
        if self.is_currently_executing_activity():
            return False

        effects = event.get('effects', {}).get('time_solution', {})

        if not effects:
            return False

        # Check if we have enough time buffer before next activity
        scheduled_activities = self.game_state.get_planned_schedule()
        current_activity_index = self.game_state.current_activity_index

        if current_activity_index >= len(scheduled_activities):
            return True  # No more activities, can spend time

        # Calculate time cost based on effect severity
        stress_severity = abs(effects.get('stress', 0))
        paranoia_severity = abs(effects.get('paranoia', 0))
        time_cost = max(0.5, (stress_severity + paranoia_severity) // 10 * 0.5)

        # Check if this would conflict with next activity
        next_activity = scheduled_activities[current_activity_index]
        time_until_next = next_activity.start_time - self.game_state.current_time

        return time_until_next >= time_cost

    def can_use_energy_solution(self, event):
        """Check if energy-based solution is viable"""
        effects = event.get('effects', {}).get('energy_solution', {})

        if not effects:
            return False

        energy_cost = abs(effects.get('energy', 0))

        if energy_cost == 0:
            return True

        # Apply paranoia penalty to energy calculation
        paranoia_factor = self.game_state.paranoia * 0.01
        effective_energy_cost = int(energy_cost * (1 + paranoia_factor))

        return self.game_state.energy >= effective_energy_cost

    def draw_event_popup(self):
        """Draw event popup window"""
        if not self.game_state.show_event_popup or not self.game_state.current_event:
            return

        # Semi-transparent overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        # Popup window - возвращено в левую часть экрана
        popup_rect = pygame.Rect(250, 200, 700, 400)
        pygame.draw.rect(self.screen, COLORS['panel'], popup_rect, border_radius=10)
        pygame.draw.rect(self.screen, COLORS['accent'], popup_rect, 3, border_radius=10)

        # Initialize event choice tooltip system
        if not hasattr(self, 'pending_event_tooltip'):
            self.pending_event_tooltip = None

        event = self.game_state.current_event
        event_type = event.get('type', 'choice')

        # Event icon
        icon_surface = FONTS['title'].render(event['icon'], True, COLORS['text'])
        self.screen.blit(icon_surface, (270, 230))

        # Event name
        name_surface = FONTS['large'].render(event['name'], True, COLORS['text'])
        self.screen.blit(name_surface, (320, 230))

        # Enhanced descriptions based on event and type
        descriptions = {
            'Сильный дождь': 'На улице начался проливной дождь. Вы промокнете до нитки, если выйдете. Нужно как-то добираться до важных дел или переждать непогоду.',
            'Пробки': 'Город встал в огромных пробках из-за аварии. Все дороги забиты машинами. Вы опоздаете на запланированные мероприятия, если не предпримете что-то.',
            'Отключение света': 'В вашем районе отключили электричество из-за технических работ. Без света и интернета многие планы под угрозой.',
            'Поломка техники': 'Важное устройство внезапно сломалось именно тогда, когда оно больше всего нужно. Это серьёзно нарушает ваши планы.',
            'Магазин закрыт': 'Вы пришли в нужный магазин, а там висит табличка "Закрыто на ремонт". А ведь вы рассчитывали на эту покупку.',
            'Подозрительный человек': 'Вы заметили, что какой-то незнакомец пристально следит за вами уже несколько минут. Его взгляд вызывает беспокойство. Чего он хочет?',
            'Тревожные новости': 'По всем новостным каналам передают тревожную информацию о событиях в мире. Это серьёзно влияет на ваше настроение и концентрацию.',
            'Отличная погода': 'Неожиданно выглянуло солнце, и на улице установилась прекрасная погода! Настроение заметно поднимается, хочется больше времени проводить на свежем воздухе.',
            'Неожиданная скидка': 'В вашем любимом магазине неожиданно объявили большую распродажу! Можно купить то, о чём давно мечтали, по очень выгодной цене.',
            'Хорошие новости': 'По телевизору и в интернете передают приятные новости - что-то действительно хорошее происходит в мире. Это поднимает настроение.',
            'Встреча со старым другом': 'На улице вы неожиданно встретили старого друга, с которым давно не виделись! Какая приятная неожиданность.',
            'Звонок друга': 'Вам звонит хороший друг и предлагает провести время вместе - сходить в кафе, кино или просто погулять.',
            'Реклама мероприятия': 'Вы увидели яркую рекламу интересного мероприятия - концерта, выставки или фестиваля. Это может быть отличным способом провести время.',
            'Странная тень': 'Боковым зрением вы заметили странную тень, которая как будто двигалась сама по себе. Когда повернули голову - ничего нет. Может быть, это просто игра света? Или кто-то действительно следит за вами?',
            'Незнакомка следит': 'Вы несколько раз замечали одну и ту же женщину в разных местах города. Она всегда делает вид, что занята своими делами, но её взгляд постоянно направлен на вас. Совпадение или целенаправленное наблюдение?',
            'Предмет переставлен': 'Вернувшись домой, вы обнаружили, что один из ваших предметов находится не на своём обычном месте. Вы точно помните, где его оставили. Кто-то был в вашей комнате или это ваша память подводит?',
            'Вдохновляющая книга': 'Вы прочитали небольшую книгу. Она так вас вдохновила, что теперь, по ощущениям, вы можете решить любую проблему в своей жизни!',
            'Мотивирующий фильм': 'Недавно вы посмотрели фильм. Он так вас вдохновил, что теперь, по ощущениям, вы можете решить любую проблему в своей жизни!',
            'Успешная медитация': 'Вы провели немного времени медетирую. Теперь вы чувствуете себя лучше. Тревоги и стресс отходят на второй план, рассудок становится более ясным',
            'Похвала от коллеги': 'На работе вас похвалил коллега. Это очень вас вдохновило. Теперь вы чувствуете, что способны на большее',
            'Отличный сон': 'Вы сегодня так хорошо спали, что, по ощущениям, теперь заряжены в два раза сильнее чем обычно',
            'Неожиданное признание': 'Неожидано, но вашу работу признал начальник. Вы не только получили его расположение, но и почувствовали себя лучше',
            # События серии "Котики"
            'Странный кот на улице': 'На углу улицы вы замечаете пушистого черного котика. Он сидит под фонарем и смотрит на вас большими зелеными глазами. '
                                     'Котик тихонько мяукает, словно пытается что-то сказать. Его шерстка выглядит ухоженной, но ошейника нет. '
                                     'Вы смотрите ему прямо в глаза. Его взгляд кажется вам слишком... пронизывающим. Как будто котик смотрит вам прямо в душу',
            'И снова черный кот': 'Тот же черный котик появляется снова! На этот раз он медленно подходит ближе, негромко мурлыча. '
                                  'Его хвост поднят трубой - явный знак дружелюбия. Котик останавливается в паре метров от вас и ожидающе смотрит, словно ждет приглашения.',

            'Черный кот просит о помощи?': 'За углом одного из неприметный домов вы замечаете своего "нового" друга - черного кота. '
                                           'Он тоже вас заметил, но в этот раз не спешит на встречу. У вас ощущение, что котик пытается вас куда-то провести. '
                                           'Немного проследовав за ним вы оказываетесь в неизвестном районе города. У вас возникает странное чувство. Нужно ли вам идти дальше?..',
            'Голодный черный кот': 'Вы опять встречаете черного котика. В этот раз - прямо у вашего дома. Как только он замечает вас - сразу же подбегает и радостно мурчит. '
                                   'Он ласково трется об ваши ноги и смотрит вам в глаза проникновенным взглядом. В этот раз он изо всех сил пытается показать, что очень голоден. ',
            # События серии "Незнакомка"
            'Таинственная незнакомка': 'Вас уже некоторое время не покидает чувство преследования... На протяжении 20 минут от вас не отстает ни на шаг один человек. '
                                       'Странная незнакомая женщина в солцнезащитных очках и длинном черном плаще как будто преследует вас. '
                                       'Через какое-то время вы терете её из виду, но странное чувство никуда не уходит...',
            'Странная записка': 'Вы заходите в помещение и снимаете верхнюю одежду как вдруг замечаете выпашую записку. Она гласит: '
                                '"Совсем скоро нам нужно будет встретиться. Я сама тебя найду. Не бойся - я не причиню вреда, так что постарайся не убегать в этот раз." '
                                'Записка точно выпала именно из вашего кармана, но как она туда попала...',
            'Незнакомка прямо перед вами': 'Проходя очередное, ничем не примечательное здание, и заворачивая за угол, вы замечаете её - незнакому в очках и черном плаще. '
                                           'В этот раз она оказалась прямо перед вами. Выйдя из оцепенения вы понимаете, что женщина никуда не уходит и ничего не говорит. '
                                           'Вы все ещё можете вернуться за угол и убежать, но хотите ли вы этого?..',
            'Ещё одна встреча': 'Вечером, возвращаясь домой, вы обнаруживаете в почтовом ящике необычное письмо. '
                                'На конверте только ваше имя, написанное красивым почерком. Никакого обратного адреса или марки. '
                                'Внутри - короткая записка: "Я знаю ваши привычки. Я знаю ваш распорядок. Не пытайтесь меня найти. Мы увидимся, когда придет время". Подписано просто: "Наблюдатель".'

        }

        desc_text = descriptions.get(event['name'], 'Произошло событие.')

        # Multi-line description с умным переносом
        desc_words = desc_text.split()
        desc_lines = []
        current_desc_line = []
        max_desc_width = 650  # ширина для описания события

        for word in desc_words:
            test_desc_line = ' '.join(current_desc_line + [word])
            test_desc_surface = FONTS['medium'].render(test_desc_line, True, COLORS['text_dim'])

            if test_desc_surface.get_width() <= max_desc_width:
                current_desc_line.append(word)
            else:
                if current_desc_line:
                    desc_lines.append(' '.join(current_desc_line))
                    current_desc_line = [word]
                else:
                    desc_lines.append(word)
                    current_desc_line = []

        if current_desc_line:
            desc_lines.append(' '.join(current_desc_line))

        y_pos = 270
        for line in desc_lines:
            if y_pos > 400:  # Ограничиваем количество строк
                break
            desc_surface = FONTS['medium'].render(line, True, COLORS['text_dim'])
            self.screen.blit(desc_surface, (270, y_pos))
            y_pos += 25

        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = pygame.mouse.get_pressed()[0]

        # Different button layouts based on event type
        if event_type == 'notification':
            # Only acknowledgment button for positive events
            ok_btn = Button(450, 450, 120, 40, "Хорошо", 'medium')

            if (ok_btn.update(mouse_pos, mouse_clicked) and
                    self.can_click_button('event_acknowledge')):
                self.register_button_click('event_acknowledge')
                self.process_event(event, "acknowledge")
                self.game_state.show_event_popup = False
                self.game_state.current_event = None

                # 🔧 НЕ СБРАСЫВАЕМ ЗАЩИТУ СРАЗУ!
                # Защита должна действовать до следующей проверки стресса
                if hasattr(self.game_state, 'event_time_skip_active') and self.game_state.event_time_skip_active:
                    print(f"🛡️ Защита остаётся активной до следующей проверки стресса")
                    # НЕ сбрасываем флаг здесь!
                    # self.game_state.event_time_skip_active = False

                # Возобновляем активность если она была прервана
                self.resume_activity_if_interrupted()
            else:
                ok_btn.update(mouse_pos, False)

            # Store tooltip for acknowledge button
            if ok_btn.rect.collidepoint(mouse_pos):
                self.pending_event_tooltip = ('acknowledge', mouse_pos)

            ok_btn.draw(self.screen)

        elif event_type == 'simple_choice':
            # Simple accept/decline for neutral events
            accept_btn = Button(350, 450, 120, 40, "Принять", 'medium')
            decline_btn = Button(500, 450, 120, 40, "Отклонить", 'medium')

            if (accept_btn.update(mouse_pos, mouse_clicked) and
                    self.can_click_button('event_accept')):
                self.register_button_click('event_accept')
                self.process_event(event, "accept")
                self.game_state.show_event_popup = False
                self.game_state.current_event = None

                # 🛡️ Защита остаётся активной до проверки стресса
                if hasattr(self.game_state, 'event_time_skip_active') and self.game_state.event_time_skip_active:
                    print(f"🛡️ Защита остаётся активной (accept)")
                    # НЕ сбрасываем здесь!

                # Возобновляем активность если она была прервана
                self.resume_activity_if_interrupted()
            else:
                accept_btn.update(mouse_pos, False)

            # Store tooltip for accept button
            if accept_btn.rect.collidepoint(mouse_pos):
                self.pending_event_tooltip = ('accept', mouse_pos)

            if (decline_btn.update(mouse_pos, mouse_clicked) and
                    self.can_click_button('event_decline')):
                self.register_button_click('event_decline')
                self.process_event(event, "decline")
                self.game_state.show_event_popup = False
                self.game_state.current_event = None

                # 🛡️ Защита остаётся активной до проверки стресса
                if hasattr(self.game_state, 'event_time_skip_active') and self.game_state.event_time_skip_active:
                    print(f"🛡️ Защита остаётся активной (decline)")
                    # НЕ сбрасываем здесь!

                # Возобновляем активность если она была прервана
                self.resume_activity_if_interrupted()
            else:
                decline_btn.update(mouse_pos, False)

            # Store tooltip for decline button
            if decline_btn.rect.collidepoint(mouse_pos):
                self.pending_event_tooltip = ('decline', mouse_pos)

            accept_btn.draw(self.screen)
            decline_btn.draw(self.screen)

        else:  # 'choice' - complex choice events
            # Get context-specific button labels
            button_labels = self.get_event_button_labels(event['name'])

            # Check which solutions are available
            can_use_energy = self.can_use_energy_solution(event)
            can_use_time = self.can_use_time_solution(event)

            # Three different approaches to handle the event - увеличиваем ширину кнопок еще больше
            ignore_btn = Button(260, 450, 200, 40, button_labels['ignore'], 'small')

            # Energy button - may be disabled
            energy_text = button_labels['energy']
            if not can_use_energy:
                energy_text = f"{energy_text} (нет энергии)"
            energy_btn = Button(470, 450, 200, 40, energy_text, 'tiny')

            # Time button - may be disabled
            time_text = button_labels['time']
            if not can_use_time:
                # Проверяем причину блокировки
                if self.is_currently_executing_activity():
                    time_text = f"{time_text} (во время активности)"
                else:
                    time_text = f"{time_text} (нет времени)"
            time_btn = Button(680, 450, 200, 40, time_text, 'tiny')

            # Always allow ignore
            if (ignore_btn.update(mouse_pos, mouse_clicked) and
                    self.can_click_button('event_ignore')):
                self.register_button_click('event_ignore')
                self.process_event(event, "ignore")
                self.game_state.show_event_popup = False
                self.game_state.current_event = None

                # 🛡️ Защита остаётся активной до проверки стресса
                if hasattr(self.game_state, 'event_time_skip_active') and self.game_state.event_time_skip_active:
                    print(f"🛡️ Защита остаётся активной (ignore)")
                    # НЕ сбрасываем здесь!

                # Возобновляем активность если она была прервана
                self.resume_activity_if_interrupted()
            else:
                ignore_btn.update(mouse_pos, False)

            # Store tooltip for ignore button
            if ignore_btn.rect.collidepoint(mouse_pos):
                self.pending_event_tooltip = ('ignore', mouse_pos)

            # Energy solution - only if viable
            if can_use_energy:
                if (energy_btn.update(mouse_pos, mouse_clicked) and
                        self.can_click_button('event_energy')):
                    self.register_button_click('event_energy')
                    self.process_event(event, "energy_solution")
                    self.game_state.show_event_popup = False
                    self.game_state.current_event = None

                    # 🔧 Очищаем флаг защиты от стресса ПОСЛЕ завершения события
                    if hasattr(self.game_state, 'event_time_skip_active') and self.game_state.event_time_skip_active:
                        print(f"💫 Очищаем флаг защиты после energy_solution")
                        self.game_state.event_time_skip_active = False

                    # Возобновляем активность если она была прервана
                    self.resume_activity_if_interrupted()
                else:
                    energy_btn.update(mouse_pos, False)

                # Store tooltip for energy button
                if energy_btn.rect.collidepoint(mouse_pos):
                    self.pending_event_tooltip = ('energy_solution', mouse_pos)
            else:
                energy_btn.update(mouse_pos, False)

            # Time solution - only if viable
            if can_use_time:
                if (time_btn.update(mouse_pos, mouse_clicked) and
                        self.can_click_button('event_time')):
                    self.register_button_click('event_time')
                    self.process_event(event, "time_solution")
                    self.game_state.show_event_popup = False
                    self.game_state.current_event = None

                    # 🔧 Очищаем флаг защиты от стресса ПОСЛЕ завершения события
                    if hasattr(self.game_state, 'event_time_skip_active') and self.game_state.event_time_skip_active:
                        print(f"💫 Очищаем флаг защиты после time_solution")
                        self.game_state.event_time_skip_active = False

                    # Возобновляем активность если она была прервана
                    self.resume_activity_if_interrupted()
                else:
                    time_btn.update(mouse_pos, False)

                # Store tooltip for time button
                if time_btn.rect.collidepoint(mouse_pos):
                    self.pending_event_tooltip = ('time_solution', mouse_pos)
            else:
                time_btn.update(mouse_pos, False)

            # Draw buttons with different styles based on availability
            ignore_btn.draw(self.screen)

            # Energy button - grayed out if disabled
            if can_use_energy:
                energy_btn.draw(self.screen)
            else:
                # Draw disabled button
                disabled_color = tuple(c // 3 for c in COLORS['button'])
                pygame.draw.rect(self.screen, disabled_color, energy_btn.rect, border_radius=5)
                pygame.draw.rect(self.screen, COLORS['text_dim'], energy_btn.rect, 2, border_radius=5)
                text_surface = FONTS['small'].render(button_labels['energy'], True, COLORS['text_dim'])
                text_rect = text_surface.get_rect(center=energy_btn.rect.center)
                self.screen.blit(text_surface, text_rect)

            # Time button - grayed out if disabled
            if can_use_time:
                time_btn.draw(self.screen)
            else:
                # Draw disabled button with proper text
                disabled_color = tuple(c // 3 for c in COLORS['button'])
                pygame.draw.rect(self.screen, disabled_color, time_btn.rect, border_radius=5)
                pygame.draw.rect(self.screen, COLORS['text_dim'], time_btn.rect, 2, border_radius=5)

                # Отображаем правильный текст для заблокированной кнопки
                disabled_text = button_labels['time']
                if self.is_currently_executing_activity():
                    disabled_text = "Нельзя во время активности"
                else:
                    disabled_text = "Нет времени"

                text_surface = FONTS['tiny'].render(disabled_text, True, COLORS['text_dim'])
                text_rect = text_surface.get_rect(center=time_btn.rect.center)
                self.screen.blit(text_surface, text_rect)

        # Draw event choice tooltips at the end
        self.draw_event_choice_tooltips()

    def draw_cards_panel(self):
        """Draw cards management panel with full deck"""
        if not self.game_state.show_cards_panel or self.game_state.day < 5:
            return

        panel_rect = pygame.Rect(30, 180, 450, 500)
        pygame.draw.rect(self.screen, COLORS['panel'], panel_rect)
        pygame.draw.rect(self.screen, COLORS['accent'], panel_rect, 2)

        # Title and stats
        title_surface = FONTS['medium'].render("Колода карт", True, COLORS['text'])
        self.screen.blit(title_surface, (45, 195))

        points_text = f"Очки карт: {self.game_state.card_points}"
        points_surface = FONTS['small'].render(points_text, True, COLORS['warning'])
        self.screen.blit(points_surface, (350, 198))

        # Tab selection
        tab_y = 220
        tab_width = 100
        tabs = ['Доступные', 'Все карты', 'Колода']

        if not hasattr(self, 'current_card_tab'):
            self.current_card_tab = 0

        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = pygame.mouse.get_pressed()[0]

        # Draw tabs
        for i, tab_name in enumerate(tabs):
            tab_rect = pygame.Rect(45 + i * tab_width, tab_y, tab_width - 5, 25)
            tab_color = COLORS['button_hover'] if i == self.current_card_tab else COLORS['panel_light']
            pygame.draw.rect(self.screen, tab_color, tab_rect, border_radius=5)
            pygame.draw.rect(self.screen, COLORS['accent'], tab_rect, 1, border_radius=5)

            tab_surface = FONTS['small'].render(tab_name, True, COLORS['text'])
            tab_text_rect = tab_surface.get_rect(center=tab_rect.center)
            self.screen.blit(tab_surface, tab_text_rect)

            if (tab_rect.collidepoint(mouse_pos) and mouse_clicked and
                    self.can_click_button(f'card_tab_{i}')):
                self.register_button_click(f'card_tab_{i}')
                self.current_card_tab = i

        # Content area
        content_rect = pygame.Rect(45, 250, 390, 400)

        if self.current_card_tab == 0:  # Available cards
            self.draw_available_cards(content_rect, mouse_pos, mouse_clicked)
        elif self.current_card_tab == 1:  # All cards
            self.draw_all_cards_catalog(content_rect, mouse_pos, mouse_clicked)
        else:  # Player deck
            self.draw_player_deck(content_rect, mouse_pos, mouse_clicked)

    def draw_available_cards(self, rect, mouse_pos, mouse_clicked):
        """Draw cards available for purchase"""
        available_cards = [card for card in self.game_state.all_cards
                           if self.game_state.day >= card['unlock_day']]

        # Scroll handling
        if not hasattr(self, 'card_scroll'):
            self.card_scroll = 0

        # Calculate maximum scroll offset
        card_height = 50
        card_spacing = 2
        total_cards_height = len(available_cards) * (card_height + card_spacing)
        visible_area_height = rect.height
        max_scroll = max(0, total_cards_height - visible_area_height)
        self.card_scroll = max(-max_scroll, min(0, self.card_scroll))

        y_pos = rect.y + self.card_scroll

        for card in available_cards:
            if y_pos > rect.bottom:
                break
            if y_pos + card_height < rect.y:
                y_pos += card_height + card_spacing
                continue

            card_rect = pygame.Rect(rect.x, y_pos, rect.width - 20, card_height)

            # Affordability check
            can_afford = self.game_state.card_points >= card['cost']

            # Colors based on rarity and affordability
            rarity_colors = {
                'common': COLORS['text_dim'],
                'uncommon': COLORS['accent'],
                'rare': COLORS['warning'],
                'legendary': COLORS['danger']
            }

            bg_color = COLORS['panel_light'] if can_afford else COLORS['panel']
            border_color = rarity_colors.get(card['rarity'], COLORS['text_dim'])
            text_color = COLORS['text'] if can_afford else COLORS['text_dim']

            pygame.draw.rect(self.screen, bg_color, card_rect, border_radius=5)
            pygame.draw.rect(self.screen, border_color, card_rect, 2, border_radius=5)

            # Card content с проверкой размещения
            icon_surface = FONTS['medium'].render(card['icon'], True, text_color)
            self.screen.blit(icon_surface, (card_rect.x + 5, card_rect.y + 5))

            # Название карты с проверкой длины
            card_name = card['name']
            available_name_width = card_rect.width - 80  # место для иконки и цены
            name_surface = FONTS['small'].render(card_name, True, text_color)

            if name_surface.get_width() > available_name_width:
                # Сокращаем название
                while len(card_name) > 8 and name_surface.get_width() > available_name_width:
                    card_name = card_name[:-4] + "..."
                    name_surface = FONTS['small'].render(card_name, True, text_color)

            self.screen.blit(name_surface, (card_rect.x + 35, card_rect.y + 5))

            # Цена карты
            cost_surface = FONTS['small'].render(f"{card['cost']}💎", True, COLORS['warning'])
            cost_x = card_rect.right - cost_surface.get_width() - 5
            self.screen.blit(cost_surface, (cost_x, card_rect.y + 5))

            # Описание карты с переносом
            desc_text = card['description']
            available_desc_width = card_rect.width - 40  # отступы
            desc_surface = FONTS['tiny'].render(desc_text, True, text_color)

            if desc_surface.get_width() > available_desc_width:
                # Обрезаем описание
                while len(desc_text) > 10 and desc_surface.get_width() > available_desc_width:
                    desc_text = desc_text[:-4] + "..."
                    desc_surface = FONTS['tiny'].render(desc_text, True, text_color)

            self.screen.blit(desc_surface, (card_rect.x + 35, card_rect.y + 25))

            # Click to buy with protection against rapid clicks - усиленная защита
            card_button_id = f"buy_card_{card['id']}"
            if (can_afford and card_rect.collidepoint(mouse_pos) and mouse_clicked):
                current_time = pygame.time.get_ticks()
                last_click = self.button_last_click.get(card_button_id, 0)
                # Проверяем общую задержку для всех карточек
                last_any_card_click = self.button_last_click.get('any_card_action', 0)
                if (current_time - last_click > 800 and current_time - last_any_card_click > 400):
                    self.button_last_click[card_button_id] = current_time
                    self.button_last_click['any_card_action'] = current_time
                    self.buy_card(card)

            y_pos += card_height + card_spacing

        # Draw scroll indicators if needed
        if len(available_cards) > 0:
            total_cards_height = len(available_cards) * (card_height + card_spacing)
            if total_cards_height > visible_area_height:
                # Can scroll up indicator
                if self.card_scroll < 0:
                    up_arrow = "▲"
                    up_surface = FONTS['small'].render(up_arrow, True, COLORS['accent'])
                    self.screen.blit(up_surface, (rect.right - 20, rect.y + 5))

                # Can scroll down indicator
                if abs(self.card_scroll) < max_scroll:
                    down_arrow = "▼"
                    down_surface = FONTS['small'].render(down_arrow, True, COLORS['accent'])
                    self.screen.blit(down_surface, (rect.right - 20, rect.bottom - 20))

    def draw_all_cards_catalog(self, rect, mouse_pos, mouse_clicked):
        """Draw catalog of all cards in game"""
        # Scroll handling for catalog
        if not hasattr(self, 'catalog_scroll'):
            self.catalog_scroll = 0

        categories = {
            'Выживание': [card for card in self.game_state.all_cards if
                          'energy' in str(card.get('effect', {})) or 'stress' in str(card.get('effect', {}))],
            'Защита': [card for card in self.game_state.all_cards if
                       'protection' in card.get('effect_type', '') or 'shield' in card['id']],
            'Усиление': [card for card in self.game_state.all_cards if
                         'boost' in card['id'] or 'enhancer' in card['id']],
            'Специальные': [card for card in self.game_state.all_cards if card['rarity'] in ['rare', 'legendary']]
        }

        # Calculate total content height
        total_height = 0
        for category, cards in categories.items():
            total_height += 25  # Category header
            total_height += min(len(cards), 5) * 18  # Show up to 5 cards per category
            total_height += 10  # Category spacing

        # Calculate scroll limits
        visible_area_height = rect.height
        max_scroll = max(0, total_height - visible_area_height)
        self.catalog_scroll = max(-max_scroll, min(0, self.catalog_scroll))

        y_pos = rect.y + self.catalog_scroll

        for category, cards in categories.items():
            if y_pos > rect.bottom:
                break
            if y_pos + 25 < rect.y:
                y_pos += 25 + min(len(cards), 5) * 18 + 10
                continue

            # Category header
            if y_pos >= rect.y and y_pos <= rect.bottom - 25:
                cat_surface = FONTS['medium'].render(category, True, COLORS['accent'])
                self.screen.blit(cat_surface, (rect.x, y_pos))
            y_pos += 25

            # Cards in category (up to 5)
            for i, card in enumerate(cards[:5]):
                if y_pos > rect.bottom:
                    break
                if y_pos + 18 < rect.y:
                    y_pos += 18
                    continue

                unlocked = self.game_state.day >= card['unlock_day']
                text_color = COLORS['text'] if unlocked else COLORS['text_dim']

                card_line = f"{card['icon']} {card['name']}"
                if not unlocked:
                    card_line += f" (День {card['unlock_day']})"

                if y_pos >= rect.y and y_pos <= rect.bottom - 18:
                    card_surface = FONTS['small'].render(card_line, True, text_color)
                    self.screen.blit(card_surface, (rect.x + 10, y_pos))
                y_pos += 18

            y_pos += 10

        # Draw scroll indicators
        if total_height > visible_area_height:
            if self.catalog_scroll < 0:
                up_arrow = "▲"
                up_surface = FONTS['small'].render(up_arrow, True, COLORS['accent'])
                self.screen.blit(up_surface, (rect.right - 20, rect.y + 5))

            if abs(self.catalog_scroll) < max_scroll:
                down_arrow = "▼"
                down_surface = FONTS['small'].render(down_arrow, True, COLORS['accent'])
                self.screen.blit(down_surface, (rect.right - 20, rect.bottom - 20))

    def draw_player_deck(self, rect, mouse_pos, mouse_clicked):
        """Draw player's current deck"""
        deck_cards = getattr(self.game_state, 'player_deck', [])

        if not deck_cards:
            no_cards_surface = FONTS['medium'].render("Колода пуста", True, COLORS['text_dim'])
            no_cards_rect = no_cards_surface.get_rect(center=(rect.centerx, rect.centery))
            self.screen.blit(no_cards_surface, no_cards_rect)
            return

        # Scroll handling for player deck
        if not hasattr(self, 'deck_scroll'):
            self.deck_scroll = 0

        card_height = 45
        card_spacing = 2
        total_deck_height = len(deck_cards) * (card_height + card_spacing)
        visible_area_height = rect.height
        max_scroll = max(0, total_deck_height - visible_area_height)
        self.deck_scroll = max(-max_scroll, min(0, self.deck_scroll))

        y_pos = rect.y + self.deck_scroll

        for i, card in enumerate(deck_cards):
            if y_pos > rect.bottom:
                break
            if y_pos + card_height < rect.y:
                y_pos += card_height + card_spacing
                continue

            card_rect = pygame.Rect(rect.x, y_pos, rect.width - 20, card_height)

            # Check if this specific card instance was used today (use index to distinguish)
            card_instance_id = f"{card['id']}_{i}"
            used_today = card_instance_id in getattr(self.game_state, 'used_cards', [])

            # Check if card is available (for time-dependent cards)
            card_available = not used_today
            if card.get('effect_type') == 'time_dependent' and not used_today:
                required_time = card.get('effect', {}).get('time_cost', 1)
                if self.game_state.phase == 'execution':
                    card_available = self.has_free_time(required_time)
                else:
                    card_available = False  # Time-dependent cards only usable during execution

            if used_today:
                bg_color = COLORS['panel']
                text_color = COLORS['text_dim']
            elif not card_available:
                bg_color = COLORS['panel']
                text_color = COLORS['text_dim']
            else:
                bg_color = COLORS['panel_light']
                text_color = COLORS['text']

            pygame.draw.rect(self.screen, bg_color, card_rect, border_radius=5)
            pygame.draw.rect(self.screen, COLORS['accent'], card_rect, 1, border_radius=5)

            # Card info
            icon_surface = FONTS['medium'].render(card['icon'], True, text_color)
            self.screen.blit(icon_surface, (card_rect.x + 5, card_rect.y + 5))

            name_surface = FONTS['small'].render(card['name'], True, text_color)
            self.screen.blit(name_surface, (card_rect.x + 35, card_rect.y + 5))

            if used_today:
                used_surface = FONTS['tiny'].render("Использовано", True, COLORS['text_dim'])
                self.screen.blit(used_surface, (card_rect.right - 80, card_rect.y + 5))
            elif not card_available and card.get('effect_type') == 'time_dependent':
                if self.game_state.phase != 'execution':
                    status_surface = FONTS['tiny'].render("Только в игре", True, COLORS['warning'])
                else:
                    status_surface = FONTS['tiny'].render("Нет времени", True, COLORS['warning'])
                self.screen.blit(status_surface, (card_rect.right - 80, card_rect.y + 5))

            desc_surface = FONTS['tiny'].render(card['description'], True, text_color)
            self.screen.blit(desc_surface, (card_rect.x + 35, card_rect.y + 25))

            # Click to use (if available) with protection against rapid clicks - усиленная защита
            deck_card_button_id = f"use_deck_card_{card_instance_id}"
            if (card_available and card_rect.collidepoint(mouse_pos) and mouse_clicked):
                current_time = pygame.time.get_ticks()
                last_click = self.button_last_click.get(deck_card_button_id, 0)
                # Проверяем общую задержку для всех карточек
                last_any_card_click = self.button_last_click.get('any_card_action', 0)
                if (current_time - last_click > 800 and current_time - last_any_card_click > 400):
                    self.button_last_click[deck_card_button_id] = current_time
                    self.button_last_click['any_card_action'] = current_time
                    self.use_deck_card(card, i)

            y_pos += card_height + card_spacing

        # Draw scroll indicators
        if len(deck_cards) > 0 and total_deck_height > visible_area_height:
            if self.deck_scroll < 0:
                up_arrow = "▲"
                up_surface = FONTS['small'].render(up_arrow, True, COLORS['accent'])
                self.screen.blit(up_surface, (rect.right - 20, rect.y + 5))

            if abs(self.deck_scroll) < max_scroll:
                down_arrow = "▼"
                down_surface = FONTS['small'].render(down_arrow, True, COLORS['accent'])
                self.screen.blit(down_surface, (rect.right - 20, rect.bottom - 20))

    def buy_card(self, card):
        """Buy a card and add to player deck"""
        if self.game_state.card_points >= card['cost']:
            self.game_state.card_points -= card['cost']
            if not hasattr(self.game_state, 'player_deck'):
                self.game_state.player_deck = []
            self.game_state.player_deck.append(card.copy())
            self.game_state.add_message(f"Куплена карта: {card['name']}", 'success')
        else:
            self.game_state.add_message("Недостаточно очков карт!", 'warning')

    def use_deck_card(self, card, card_index):
        """Use a specific card instance from player deck"""
        if not hasattr(self.game_state, 'used_cards'):
            self.game_state.used_cards = []

        # Use unique identifier for each card instance
        card_instance_id = f"{card['id']}_{card_index}"

        if card_instance_id in self.game_state.used_cards:
            self.game_state.add_message("Карта уже использована сегодня!", 'warning')
            return

        # Apply card effect
        success = self.apply_card_effect(card)

        if success:
            # Store the last used card for potential restoration
            self.game_state.last_used_card = card.copy()

            # Remove the card from player's deck
            if hasattr(self.game_state, 'player_deck') and card_index < len(self.game_state.player_deck):
                removed_card = self.game_state.player_deck.pop(card_index)
                self.game_state.add_message(f"Использована и удалена: {removed_card['name']}", 'success')
            else:
                self.game_state.add_message(f"Использована: {card['name']}", 'success')
        else:
            self.game_state.add_message(f"Не удалось использовать: {card['name']}", 'warning')

    def apply_card_effect(self, card):
        """Apply the effect of a used card"""
        effect = card.get('effect', {})
        effect_type = card.get('effect_type', 'immediate')

        if effect_type == 'immediate':
            if 'energy' in effect:
                self.game_state.energy = min(100, self.game_state.energy + effect['energy'])
            if 'stress' in effect:
                self.game_state.stress = max(0, self.game_state.stress + effect['stress'])
            if 'paranoia' in effect:
                self.game_state.paranoia = max(0, self.game_state.paranoia + effect['paranoia'])

            # Check for game over after applying card effects
            if self.check_game_over_conditions():
                return True

        elif effect_type == 'day_buff':
            # Apply day-long buffs
            if 'luck_bonus' in effect:
                self.game_state.luck_active = True
            if 'energy_protection' in effect:
                self.game_state.energy_shield = effect['energy_protection']

        elif effect_type == 'voice_relationship':
            if 'voice_bonus' in effect:
                self.game_state.inner_voice_relationship = min(100,
                                                               self.game_state.inner_voice_relationship + effect[
                                                                   'voice_bonus'])

        elif effect_type == 'event_manipulation':
            # Cards that manipulate events
            if 'undo_last_event' in effect:
                return self.undo_last_event()
            elif 'reverse_event' in effect:
                return self.activate_event_reversal()

        elif effect_type == 'time_manipulation':
            # Cards that allow activity manipulation
            if 'move_activity' in effect:
                return self.activate_activity_move_mode()

        elif effect_type == 'card_manipulation':
            # Cards that affect other cards
            if 'recycle_card' in effect:
                return self.activate_card_recycling()

        elif effect_type == 'card_generation':
            # Cards that generate new cards
            if 'random_cards' in effect:
                return self.generate_random_cards(effect['random_cards'])

        elif effect_type == 'random_positive':
            # Cards with random positive effects
            if 'random_bonus' in effect:
                return self.apply_random_positive_effect()

        elif effect_type == 'cleanse_negative':
            # Cards that cleanse negative status effects
            if 'cleanse_negative_effects' in effect:
                return self.cleanse_negative_effects()

        elif effect_type == 'day_perfection':
            # Special cards that perfect the day
            if 'perfect_day' in effect:
                return self.activate_perfect_day()

        elif effect_type == 'next_event' or effect_type == 'one_time_protection':
            # Protective cards for events
            return self.activate_event_protection(effect)

        elif effect_type == 'next_activity':
            # Cards that affect next activity
            return self.activate_next_activity_buff(effect)

        elif effect_type == 'category_protection':
            # Cards that protect from specific event categories
            return self.activate_category_protection(effect)

        elif effect_type == 'activity_type_bonus':
            # Cards that boost specific activity types
            return self.activate_activity_type_bonus(effect)

        elif effect_type == 'time_dependent':
            # Cards that require free time to use
            return self.apply_time_dependent_effect(effect)

        elif effect_type == 'information':
            # Cards that provide information
            if 'reveal_events' in effect:
                return self.reveal_upcoming_events(effect['reveal_events'])

        elif effect_type == 'voice_control':
            # Cards that control the inner voice
            if 'silence_voice' in effect:
                return self.silence_inner_voice()

        return True

    def undo_last_event(self):
        """Undo the effects of the last processed event"""
        if not hasattr(self.game_state, 'last_event_effects') or not self.game_state.last_event_effects:
            self.game_state.add_message("Нет события для отмены", 'warning')
            return False

        # Reverse the last event effects
        last_effects = self.game_state.last_event_effects

        if 'stress' in last_effects:
            self.game_state.stress = max(0, min(100, self.game_state.stress - last_effects['stress']))
        if 'paranoia' in last_effects:
            self.game_state.paranoia = max(0, min(100, self.game_state.paranoia - last_effects['paranoia']))
        if 'energy' in last_effects:
            self.game_state.energy = max(0, min(100, self.game_state.energy - last_effects['energy']))
        if 'time_cost' in last_effects:
            self.game_state.current_time = max(8.0, self.game_state.current_time - last_effects['time_cost'])

        self.game_state.add_message("Последнее событие отменено!", 'success')
        self.game_state.last_event_effects = None
        return True

    def activate_event_reversal(self):
        """Activate the next negative event reversal"""
        if not hasattr(self.game_state, 'event_reversal_active'):
            self.game_state.event_reversal_active = False

        self.game_state.event_reversal_active = True
        self.game_state.add_message("🌀 Контроль хаоса активирован! Следующее негативное событие станет позитивным!",
                                    'success')
        return True

    def activate_activity_move_mode(self):
        """Activate mode to move one activity"""
        if not hasattr(self.game_state, 'activity_move_uses'):
            self.game_state.activity_move_uses = 0

        self.game_state.activity_move_uses += 1
        self.game_state.add_message("⏱️ Идеальный тайминг: Можно переместить одну активность без ограничений!",
                                    'success')
        return True

    def activate_card_recycling(self):
        """Restore the last used card if it was common, uncommon, or rare"""
        # Check if there was a last used card recorded
        if not hasattr(self.game_state, 'last_used_card') or not self.game_state.last_used_card:
            self.game_state.add_message("Нет недавно использованной карты для восстановления", 'warning')
            return False

        last_card = self.game_state.last_used_card

        # Check if the last used card can be restored (only common, uncommon, rare)
        if last_card['rarity'] not in ['common', 'uncommon', 'rare']:
            self.game_state.add_message(f"Нельзя восстановить легендарную карту: '{last_card['name']}'", 'warning')
            return False

        # Add the last used card back to deck
        if not hasattr(self.game_state, 'player_deck'):
            self.game_state.player_deck = []

        restored_card = last_card.copy()
        self.game_state.player_deck.append(restored_card)

        self.game_state.add_message(f"🧩 Усиление памяти: восстановлена карта '{restored_card['name']}'!", 'success')

        # Clear the last used card reference to prevent multiple restorations
        self.game_state.last_used_card = None

        return True

    def generate_random_cards(self, count):
        """Generate random cards and add to deck"""
        if not hasattr(self.game_state, 'player_deck'):
            self.game_state.player_deck = []

        available_cards = [card for card in self.game_state.all_cards
                           if self.game_state.day >= card['unlock_day']]

        if not available_cards:
            self.game_state.add_message("Нет доступных карт для генерации", 'warning')
            return False

        added_cards = []
        for _ in range(count):
            new_card = random.choice(available_cards).copy()
            self.game_state.player_deck.append(new_card)
            added_cards.append(new_card['name'])

        self.game_state.add_message(f"Получены случайные карты: {', '.join(added_cards)}", 'success')
        return True

    def apply_random_positive_effect(self):
        """Apply a random positive effect that player actually needs"""
        # Обычные эффекты
        basic_effects = [
            ('stress', -20, 'Внезапное успокоение!'),
            ('card_points', 20, 'Бонусные очки карт!')
        ]

        # Позитивные статусы (шанс 50%)
        positive_status_effects = [
            ('status', 'inspired', 'Воодушевление! Получен позитивный статус'),
            ('status', 'focused', 'Концентрация! Получен позитивный статус'),
            ('status', 'confident', 'Уверенность! Получен позитивный статус'),
            # Дублируем статусы для увеличения шанса
            ('status', 'inspired', 'Воодушевление! Получен позитивный статус'),
            ('status', 'focused', 'Концентрация! Получен позитивный статус'),
            ('status', 'confident', 'Уверенность! Получен позитивный статус'),
            # Добавляем ещё больше копий для сохранения высокого шанса статусов
            ('status', 'inspired', 'Воодушевление! Получен позитивный статус'),
            ('status', 'focused', 'Концентрация! Получен позитивный статус')
        ]

        # Объединяем все эффекты
        all_effects = basic_effects + positive_status_effects

        # Фильтруем эффекты, которые действительно принесут пользу
        beneficial_effects = []

        for effect_tuple in all_effects:
            effect_type = effect_tuple[0]

            if effect_type == 'stress' and self.game_state.stress > 10:  # Есть стресс для снижения
                beneficial_effects.append(effect_tuple)
            elif effect_type == 'card_points':  # Очки карт всегда полезны
                beneficial_effects.append(effect_tuple)
            elif effect_type == 'status':  # Позитивные статусы если их нет или мало времени осталось
                status_id = effect_tuple[1]
                should_add = True

                # Проверяем есть ли уже такой статус
                if hasattr(self.game_state, 'status_effects') and status_id in self.game_state.status_effects:
                    existing_status = self.game_state.status_effects[status_id]
                    current_time = getattr(self.game_state, 'current_time', 8.0)

                    # Вычисляем оставшееся время
                    time_passed = current_time - existing_status['start_time']
                    remaining_time = existing_status['duration_hours'] - time_passed

                    # Добавляем только если осталось мало времени (меньше 3 часов)
                    should_add = remaining_time < 3.0

                if should_add:
                    beneficial_effects.append(effect_tuple)

        # Если нет полезных эффектов, выбираем из всех (на случай идеального состояния)
        if not beneficial_effects:
            beneficial_effects = all_effects

        chosen_effect = random.choice(beneficial_effects)
        effect_type = chosen_effect[0]

        if effect_type == 'status':
            # Применяем позитивный статус
            status_id = chosen_effect[1]
            message = chosen_effect[2]
            self.apply_positive_status(status_id)
        else:
            # Обычные эффекты
            value = chosen_effect[1]
            message = chosen_effect[2]

            if effect_type == 'stress':
                self.game_state.stress = max(0, self.game_state.stress + value)
            elif effect_type == 'card_points':
                self.game_state.card_points += value

        self.game_state.add_message(f"✨ Счастливый случай: {message}", 'success')
        return True

    def apply_positive_status(self, status_id):
        """Применяет позитивный статус эффект или продляет существующий"""
        positive_statuses = {
            'inspired': {
                'name': 'Воодушевление',
                'icon': '🎆',
                'description': 'Ощущение воодушевления и мотивации. Отрицательные события на 30% слабее',
                'duration': 12.0,
                'effects': {'negative_event_resistance': 0.7}
            },
            'focused': {
                'name': 'Концентрация',
                'icon': '🎯',
                'description': 'Повышенная концентрация и ясность мыслей. Меньше нарастания паранойи',
                'duration': 12.0,
                'effects': {'paranoia_resistance': 0.5}
            },
            'confident': {
                'name': 'Уверенность',
                'icon': '💪',
                'description': 'Повышенная уверенность в себе. Социальные активности дают дополнительное спокойствие',
                'duration': 12.0,
                'effects': {'social_stress_resistance': 0.6}
            },
            'energized': {
                'name': 'Энергичность',
                'icon': '⚡',
                'description': 'Повышенная энергия и бодрость. Активности тратят на 20% меньше энергии',
                'duration': 12.0,
                'effects': {'energy_efficiency': 0.8}
            }
        }

        if status_id in positive_statuses:
            status_info = positive_statuses[status_id]

            # Проверяем есть ли уже такой статус
            if hasattr(self.game_state, 'status_effects') and status_id in self.game_state.status_effects:
                existing_status = self.game_state.status_effects[status_id]
                current_time = getattr(self.game_state, 'current_time', 8.0)

                # Вычисляем оставшееся время
                time_passed = current_time - existing_status['start_time']
                remaining_time = existing_status['duration_hours'] - time_passed

                if remaining_time < 3.0:  # Если осталось меньше 3 часов - продляем
                    # 🚨 ИСПРАВЛЕНИЕ: Правильное обновление времени начала для продления
                    existing_status['start_time'] = current_time
                    existing_status['duration_hours'] = status_info['duration']
                    self.game_state.add_message(
                        f"✨ {status_info['name']}: эффект продлён на полную длительность ({status_info['duration']:.1f}ч)!",
                        'success')
                else:
                    # Статус уже активен и времени достаточно - ничего не делаем
                    self.game_state.add_message(f"🔄 {status_info['name']} уже активен (осталось {remaining_time:.1f}ч)",
                                                'info')
            else:
                # Используем стандартный метод добавления нового статуса
                self.game_state.add_status_effect(
                    status_id,
                    status_info['name'],
                    status_info['icon'],
                    status_info['description'],
                    status_info['duration'],
                    None,  # condition_check = None для позитивных статусов
                    status_info['effects']
                )
                self.game_state.add_message(f"✨ Получен новый статус: {status_info['name']}!", 'success')

    def cleanse_negative_effects(self):
        """Remove all negative status effects caused by events"""
        if not hasattr(self.game_state, 'status_effects') or not self.game_state.status_effects:
            self.game_state.add_message("Нет активных негативных эффектов для очищения", 'info')
            return True

        # List of negative status effects that should be removed by this card
        negative_effects_to_remove = []

        # Identify negative effects from events (paranoia-related statuses)
        for status_id, status in self.game_state.status_effects.items():
            status_name = status['name'].lower()
            # Remove paranoia-related effects from events
            if any(keyword in status_name for keyword in [
                'теневая паранойя', 'ощущение слежки', 'информационная тревога',
                'паранойя слежки', 'страх вторжения', 'страх саботажа',
                'surveillance_paranoia', 'shadow_paranoia', 'stalked_feeling',
                'information_anxiety', 'home_invasion_fear', 'tech_sabotage_fear'
            ]):
                negative_effects_to_remove.append(status_id)

        if not negative_effects_to_remove:
            self.game_state.add_message("Нет негативных эффектов от событий для очищения", 'info')
            return True

        # Remove the identified negative effects
        removed_effects = []
        for status_id in negative_effects_to_remove:
            if status_id in self.game_state.status_effects:
                effect_name = self.game_state.status_effects[status_id]['name']
                removed_effects.append(effect_name)
                del self.game_state.status_effects[status_id]

        if removed_effects:
            effects_list = ", ".join(removed_effects)
            self.game_state.add_message(f"✨ Очищение разума: удалены эффекты {effects_list}", 'success')

            # Small bonus for cleansing - reduce paranoia a bit
            self.game_state.paranoia = max(0, self.game_state.paranoia - 10)
            self.game_state.add_message("Дополнительно: -10 паранойи от очищения", 'success')

        return True

    def activate_perfect_day(self):
        """Remove all negative effects and set good mental state"""
        # Clear all negative status effects
        if hasattr(self.game_state, 'status_effects'):
            negative_effects = []
            for status_id, status in self.game_state.status_effects.items():
                if any(word in status['name'].lower() for word in
                       ['истощение', 'перенапряжение', 'паранойя', 'критическое', 'выгорание', 'тревожность']):
                    negative_effects.append(status_id)

            for status_id in negative_effects:
                del self.game_state.status_effects[status_id]

        # Set optimal mental state
        self.game_state.stress = min(20, self.game_state.stress)
        self.game_state.paranoia = min(15, self.game_state.paranoia)
        self.game_state.energy = max(70, self.game_state.energy)

        self.game_state.add_message("Идеальный день! Все негативные эффекты сняты!", 'success')
        return True

    def activate_event_protection(self, effect):
        """Activate protection for the next event"""
        if 'block_stress' in effect:
            if not hasattr(self.game_state, 'stress_protection_active'):
                self.game_state.stress_protection_active = False
            self.game_state.stress_protection_active = True
            self.game_state.add_message("Защита от стресса активирована!", 'success')

        if 'universal_protection' in effect:
            if not hasattr(self.game_state, 'universal_protection_active'):
                self.game_state.universal_protection_active = False
            self.game_state.universal_protection_active = True
            self.game_state.add_message("Универсальная защита активирована!", 'success')

        return True

    def activate_next_activity_buff(self, effect):
        """Activate buff for the next activity"""
        if 'activity_multiplier' in effect:
            if not hasattr(self.game_state, 'next_activity_multiplier'):
                self.game_state.next_activity_multiplier = 1.0
            self.game_state.next_activity_multiplier = effect['activity_multiplier']
            self.game_state.add_message(
                f"Следующая активность будет в {effect['activity_multiplier']}x раз эффективнее!", 'success')

        if 'motivation_multiplier' in effect:
            if not hasattr(self.game_state, 'motivation_boost_active'):
                self.game_state.motivation_boost_active = False
            self.game_state.motivation_boost_active = True
            self.game_state.motivation_multiplier = effect['motivation_multiplier']
            self.game_state.add_message("Мотивация резко повышена! Выберите активность для усиления!", 'success')

        return True

    def activate_category_protection(self, effect):
        """Activate protection from specific event categories"""
        protections = {
            'protect_social': 'social_protection_active',
            'protect_technical': 'technical_protection_active',
            'protect_weather': 'weather_protection_active'
        }

        for protect_key, attr_name in protections.items():
            if protect_key in effect:
                setattr(self.game_state, attr_name, True)
                category = protect_key.replace('protect_', '').title()
                self.game_state.add_message(f"Защита от {category.lower()} событий активирована!", 'success')

        return True

    def activate_activity_type_bonus(self, effect):
        """Activate bonus for specific activity types"""
        bonuses = {
            'social_bonus': ('социальных', 'social_activities_bonus'),
            'physical_bonus': ('физических', 'physical_activities_bonus'),
            'mental_bonus': ('умственных', 'mental_activities_bonus')
        }

        for bonus_key, (activity_type, attr_name) in bonuses.items():
            if bonus_key in effect:
                setattr(self.game_state, attr_name, effect[bonus_key])
                self.game_state.add_message(f"Бонус к {activity_type} активностям активирован!", 'success')

        return True

    def reveal_upcoming_events(self, count):
        """Reveal upcoming events to the player"""
        # Проверяем новую систему событий с назначенным временем
        if not hasattr(self.game_state, 'daily_events') or not self.game_state.daily_events:
            self.game_state.add_message("Сегодня больше событий не запланировано", 'info')
            return True

        # Фильтруем события, которые ещё не произошли
        future_events = [
            event for event in self.game_state.daily_events
            if not event.get('triggered', False)
        ]

        if not future_events:
            self.game_state.add_message("Все предстоящие события дня уже произошли", 'info')
            return True

        events_to_show = future_events[:count]

        # События уже имеют назначенное время из generate_random_events

        # Создаём сообщение с точными временами
        event_times = []
        for event in events_to_show:
            event_time = event.get('time', 12)
            time_str = f"{int(event_time):02d}:00"
            event_times.append(f"{event['name']} в {time_str}")

        # Сохраняем данные предсказания для отображения
        self.game_state.prediction_data = {
            'events': [{
                'name': event['name'],
                'icon': event.get('icon', '❓'),
                'time': event.get('time', 12.0)
            } for event in events_to_show],
            'day_activated': self.game_state.day,
            'phase_activated': self.game_state.phase
        }

        self.game_state.add_message(f"🔮 Предвидение: {', '.join(event_times)}", 'info')
        return True

    def apply_time_dependent_effect(self, effect):
        """Apply effects that depend on available free time"""
        # Check if we're in execution phase and can calculate free time
        if self.game_state.phase != 'execution':
            self.game_state.add_message("Эта карта доступна только во время выполнения дня", 'warning')
            return False

        # Check if we have required free time
        required_time = effect.get('time_cost', 1)
        if not self.has_free_time(required_time):
            self.game_state.add_message(f"Недостаточно свободного времени (нужно {required_time}ч)", 'warning')
            return False

        # Apply immediate effects
        if 'energy' in effect:
            self.game_state.energy = min(100, self.game_state.energy + effect['energy'])
            self.game_state.add_message(f"Короткий сон: +{effect['energy']} энергии", 'success')

        if 'stress' in effect:
            self.game_state.stress = max(0, self.game_state.stress + effect['stress'])

        if 'paranoia' in effect:
            self.game_state.paranoia = max(0, self.game_state.paranoia + effect['paranoia'])

        # Advance time
        if 'time_cost' in effect:
            self.game_state.current_time += effect['time_cost']
            self.game_state.add_message(f"Потрачено времени: {effect['time_cost']}ч", 'info')

        return True

    def has_free_time(self, required_hours):
        """Check if there's enough free time available"""
        if self.game_state.phase != 'execution':
            return False

        # Get current and next activity
        scheduled_activities = self.game_state.get_planned_schedule()

        # If no more activities, check against end of day (22:00)
        if self.game_state.current_activity_index >= len(scheduled_activities):
            end_of_day = 22.0
            available_time = end_of_day - self.game_state.current_time
            return available_time >= required_hours

        # Check time until next activity
        next_activity = scheduled_activities[self.game_state.current_activity_index]
        time_until_next = next_activity.start_time - self.game_state.current_time

        return time_until_next >= required_hours

    def silence_inner_voice(self):
        """Temporarily silence the inner voice"""
        if not hasattr(self.game_state, 'voice_silenced_until'):
            self.game_state.voice_silenced_until = 0

        self.game_state.voice_silenced_until = self.game_state.day + 1  # Silence for one day
        self.game_state.add_message("Внутренний голос замолчал до завтра...", 'info')
        return True

    def draw_voice_panel(self):
        """Draw inner voice management panel with tasks"""
        if not self.game_state.show_voice_panel or self.game_state.day < 3:
            return

        panel_rect = pygame.Rect(720, 180, 450, 500)
        pygame.draw.rect(self.screen, COLORS['panel'], panel_rect)
        pygame.draw.rect(self.screen, COLORS['accent'], panel_rect, 2)

        # Title
        title_surface = FONTS['medium'].render("Внутренний голос", True, COLORS['text'])
        self.screen.blit(title_surface, (735, 195))

        # Voice relationship indicator with color coding - размещаем в два ряда
        relationship = self.game_state.inner_voice_relationship
        if relationship >= 50:
            rel_color = COLORS['success']
            rel_status = "Доверительные"
        elif relationship >= 20:
            rel_color = COLORS['accent']
            rel_status = "Дружественные"
        elif relationship >= 0:
            rel_color = COLORS['text']
            rel_status = "Нейтральные"
        elif relationship >= -30:
            rel_color = COLORS['warning']
            rel_status = "Напряжённые"
        else:
            rel_color = COLORS['danger']
            rel_status = "Враждебные"

        # Первый ряд - отношения
        relationship_text = f"Отношения: {rel_status} ({relationship:+d})"
        rel_surface = FONTS['small'].render(relationship_text, True, rel_color)
        self.screen.blit(rel_surface, (735, 220))

        # Trust level indicator - размещаем справа, но на той же строке если помещается
        trust_level = "Базовый"
        if relationship >= 50:
            trust_level = "Продвинутый"
        elif relationship >= 20:
            trust_level = "Доверительный"

        trust_text = f"Доверие: {trust_level}"
        trust_surface = FONTS['small'].render(trust_text, True, COLORS['accent'])

        # Проверяем, помещается ли справа от отношений
        relationship_width = rel_surface.get_width()
        trust_width = trust_surface.get_width()
        available_width = 420  # ширина панели - отступы

        if relationship_width + trust_width + 20 <= available_width:
            # Помещается на той же строке
            self.screen.blit(trust_surface, (735 + relationship_width + 20, 220))
            trust_y = 220
        else:
            # Переносим на следующую строку
            self.screen.blit(trust_surface, (735, 240))
            trust_y = 240

        # Voice interactions counter - размещаем с учетом положения trust_level
        voice_interactions_text = f"Взаимодействий сегодня: {self.game_state.daily_voice_interactions}/{self.game_state.max_daily_voice_interactions}"
        interactions_surface = FONTS['small'].render(voice_interactions_text, True, COLORS['text_dim'])
        interactions_y = trust_y + 20  # 20px ниже уровня доверия
        self.screen.blit(interactions_surface, (735, interactions_y))

        # Voice tasks section - динамическая позиция
        tasks_y = interactions_y + 25  # 25px ниже счетчика взаимодействий
        tasks_title = FONTS['medium'].render("📋 Задания от голоса:", True, COLORS['accent'])
        self.screen.blit(tasks_title, (735, tasks_y))

        # Draw current tasks
        y_pos = tasks_y + 30
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = pygame.mouse.get_pressed()[0]

        if hasattr(self.game_state, 'voice_tasks') and self.game_state.voice_tasks:
            for i, task in enumerate(self.game_state.voice_tasks):
                if y_pos > panel_rect.bottom - 50:
                    break

                task_rect = pygame.Rect(735, y_pos, 420, 50)

                # Check if task is completed
                is_completed = task['id'] in getattr(self.game_state, 'completed_voice_tasks', [])

                # Task background
                if is_completed:
                    bg_color = COLORS['success']
                    text_color = COLORS['text']
                    border_color = COLORS['success']
                else:
                    bg_color = COLORS['panel_light']
                    text_color = COLORS['text']
                    border_color = COLORS['accent']

                pygame.draw.rect(self.screen, bg_color, task_rect, border_radius=5)
                pygame.draw.rect(self.screen, border_color, task_rect, 2, border_radius=5)

                # Task content с проверкой размещения
                task_name = task['name']
                if is_completed:
                    task_name += " ✓"

                # Проверяем длину названия задания
                name_surface = FONTS['small'].render(task_name, True, text_color)
                max_name_width = 280  # оставляем место для награды

                if name_surface.get_width() > max_name_width:
                    # Сокращаем название
                    while len(task_name) > 10 and name_surface.get_width() > max_name_width:
                        task_name = task_name[:-4] + "..."
                        name_surface = FONTS['small'].render(task_name, True, text_color)

                self.screen.blit(name_surface, (745, y_pos + 5))

                # Описание с переносом
                desc_text = task['description']
                desc_words = desc_text.split()
                desc_lines = []
                current_desc_line = []

                for word in desc_words:
                    test_desc_line = ' '.join(current_desc_line + [word])
                    test_desc_surface = FONTS['tiny'].render(test_desc_line, True, text_color)

                    if test_desc_surface.get_width() <= max_name_width:
                        current_desc_line.append(word)
                    else:
                        if current_desc_line:
                            desc_lines.append(' '.join(current_desc_line))
                            current_desc_line = [word]
                        else:
                            desc_lines.append(word[:20] + "...")
                            current_desc_line = []

                if current_desc_line:
                    desc_lines.append(' '.join(current_desc_line))

                # Показываем первую строку описания
                if desc_lines:
                    desc_surface = FONTS['tiny'].render(desc_lines[0], True, text_color)
                    self.screen.blit(desc_surface, (745, y_pos + 22))

                # Reward info - размещаем справа
                reward = task['reward']
                reward_text = f"💎{reward.get('card_points', 0)} 💖{reward.get('voice_relationship', 0):+d}"
                reward_surface = FONTS['tiny'].render(reward_text, True, COLORS['warning'])
                reward_x = task_rect.right - reward_surface.get_width() - 10
                self.screen.blit(reward_surface, (reward_x, y_pos + 5))

                # Status indicator (no manual check button)
                if not is_completed:
                    status_text = "В процессе..."
                    status_surface = FONTS['tiny'].render(status_text, True, COLORS['text_dim'])
                    status_x = task_rect.right - status_surface.get_width() - 10
                    self.screen.blit(status_surface, (status_x, y_pos + 25))

                y_pos += 55
        elif self.game_state.inner_voice_relationship < -50:
            # Show message about needing to improve relationship
            no_tasks_bg = pygame.Rect(735, y_pos, 420, 60)
            pygame.draw.rect(self.screen, COLORS['panel_light'], no_tasks_bg, border_radius=5)
            pygame.draw.rect(self.screen, COLORS['danger'], no_tasks_bg, 2, border_radius=5)

            no_tasks_title = FONTS['small'].render("❌ Отношения слишком плохие", True, COLORS['danger'])
            self.screen.blit(no_tasks_title, (745, y_pos + 5))

            no_tasks_desc = FONTS['tiny'].render("Голос отказывается давать задания.", True, COLORS['text_dim'])
            self.screen.blit(no_tasks_desc, (745, y_pos + 22))

            no_tasks_hint = FONTS['tiny'].render("Улучшите отношения через диалог (слушайте, не спорьте)", True,
                                                 COLORS['text_dim'])
            self.screen.blit(no_tasks_hint, (745, y_pos + 38))

            y_pos += 70
        else:
            no_tasks_surface = FONTS['small'].render("Сегодня заданий нет", True, COLORS['text_dim'])
            self.screen.blit(no_tasks_surface, (735, y_pos))
            y_pos += 30

        # Voice state and interaction
        voice_y = y_pos + 20
        if voice_y < panel_rect.bottom - 120:
            voice_state = self.get_voice_state()

            # Voice message section
            voice_bg = pygame.Rect(735, voice_y, 420, 80)
            pygame.draw.rect(self.screen, COLORS['panel_light'], voice_bg, border_radius=5)
            pygame.draw.rect(self.screen, COLORS['accent'], voice_bg, 1, border_radius=5)

            voice_title = FONTS['small'].render("🗣️ Голос говорит:", True, COLORS['accent'])
            self.screen.blit(voice_title, (745, voice_y + 5))

            # Voice message с умной разбивкой на строки
            voice_message = voice_state['message']

            # Разбиваем сообщение на слова для лучшего переноса
            words = voice_message.split()
            lines = []
            current_line = []
            line_width = 0
            max_width = 400  # Максимальная ширина строки в пикселях

            for word in words:
                # Проверяем, поместится ли слово в текущую строку
                test_line = ' '.join(current_line + [word])
                test_surface = FONTS['small'].render(test_line, True, voice_state['color'])

                if test_surface.get_width() <= max_width:
                    current_line.append(word)
                else:
                    if current_line:  # Если в строке есть слова, сохраняем её
                        lines.append(' '.join(current_line))
                        current_line = [word]
                    else:  # Если слово слишком длинное, обрезаем его
                        lines.append(word[:30] + "...")
                        current_line = []

            # Добавляем последнюю строку
            if current_line:
                lines.append(' '.join(current_line))

            # Показываем максимум 3 строки
            msg_y = voice_y + 25
            max_lines = 3
            for i, line in enumerate(lines[:max_lines]):
                if i == max_lines - 1 and len(lines) > max_lines:
                    # Если строк больше чем помещается, добавляем многоточие
                    line = line[:-3] + "..."
                message_surface = FONTS['small'].render(line, True, voice_state['color'])
                self.screen.blit(message_surface, (745, msg_y))
                msg_y += 16

            # Action buttons - адаптивное размещение
            buttons_y = voice_y + 85
            available_button_width = 420  # ширина панели
            num_buttons = 3 if (hasattr(self.game_state, 'voice_tasks') and
                                self.game_state.voice_tasks and
                                self.game_state.inner_voice_relationship >= -50) else 2

            # Рассчитываем оптимальные размеры кнопок
            button_spacing = 5
            button_width = (available_button_width - (num_buttons - 1) * button_spacing) // num_buttons

            # Check if interactions are still available
            interactions_available = self.game_state.daily_voice_interactions < self.game_state.max_daily_voice_interactions

            # Action buttons with individual protection
            # Listen button
            listen_text = "Послушать" if interactions_available else "Послушать (лимит)"
            listen_btn = Button(735, buttons_y, button_width, 30, listen_text,
                                'tiny' if not interactions_available else 'small')

            if interactions_available:
                if (mouse_clicked and listen_btn.update(mouse_pos, True) and
                        self.can_click_button('listen_voice')):
                    self.listen_to_voice()
                else:
                    listen_btn.update(mouse_pos, False)
                listen_btn.draw(self.screen)
            else:
                # Draw disabled button
                disabled_color = tuple(c // 3 for c in COLORS['button'])
                pygame.draw.rect(self.screen, disabled_color, listen_btn.rect, border_radius=5)
                pygame.draw.rect(self.screen, COLORS['text_dim'], listen_btn.rect, 2, border_radius=5)
                text_surface = FONTS['tiny'].render("Послушать", True, COLORS['text_dim'])
                text_rect = text_surface.get_rect(center=listen_btn.rect.center)
                self.screen.blit(text_surface, text_rect)

            # Argue button (moved to second position)
            argue_text = "Поспорить" if interactions_available else "Поспорить (лимит)"
            argue_btn = Button(735 + button_width + button_spacing, buttons_y, button_width, 30, argue_text,
                               'tiny' if not interactions_available else 'small')

            if interactions_available:
                if (mouse_clicked and argue_btn.update(mouse_pos, True) and
                        self.can_click_button('argue_voice')):
                    self.argue_with_voice()
                else:
                    argue_btn.update(mouse_pos, False)
                argue_btn.draw(self.screen)
            else:
                # Draw disabled button
                disabled_color = tuple(c // 3 for c in COLORS['button'])
                pygame.draw.rect(self.screen, disabled_color, argue_btn.rect, border_radius=5)
                pygame.draw.rect(self.screen, COLORS['text_dim'], argue_btn.rect, 2, border_radius=5)
                text_surface = FONTS['tiny'].render("Поспорить", True, COLORS['text_dim'])
                text_rect = text_surface.get_rect(center=argue_btn.rect.center)
                self.screen.blit(text_surface, text_rect)

            # Replace random task button (moved to third position)
            # Only show if there are tasks and relationship is good enough
            if (hasattr(self.game_state, 'voice_tasks') and self.game_state.voice_tasks and
                    self.game_state.inner_voice_relationship >= -50):
                replace_task_btn = Button(735 + (button_width + button_spacing) * 2, buttons_y, button_width, 30,
                                          "Заменить", 'small')
                if (mouse_clicked and replace_task_btn.update(mouse_pos, True) and
                        self.can_click_button('replace_voice_task')):
                    self.replace_random_voice_task()
                else:
                    replace_task_btn.update(mouse_pos, False)
                replace_task_btn.draw(self.screen)

    def draw_dream_popup(self):
        """Отображение попапа со сном"""
        if not self.game_state.show_dream_popup or not self.game_state.current_dream:
            return

        # Полупрозрачный оверлей
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(160)
        overlay.fill((5, 5, 15))  # Тёмный оверлей для сна
        self.screen.blit(overlay, (0, 0))

        # Окно попапа
        popup_rect = pygame.Rect(150, 200, 900, 400)
        pygame.draw.rect(self.screen, COLORS['panel'], popup_rect, border_radius=10)

        dream = self.game_state.current_dream

        # Цвет рамки в зависимости от типа сна
        if dream['type'] == 'warning':
            border_color = COLORS['danger']
            icon = "⚠️🌙"  # Предупреждение
            title = "Тревожный сон"
        else:
            border_color = COLORS['success']
            icon = "✨🌙"  # Мотивация
            title = "Вдохновляющий сон"

        pygame.draw.rect(self.screen, border_color, popup_rect, 3, border_radius=10)

        # Заголовок
        icon_surface = FONTS['title'].render(icon, True, border_color)
        self.screen.blit(icon_surface, (170, 230))

        title_surface = FONTS['large'].render(title, True, border_color)
        self.screen.blit(title_surface, (250, 235))

        # Описание сна с переносом строк
        description = dream['description']
        words = description.split()
        lines = []
        current_line = []
        max_width = 850

        for word in words:
            test_line = ' '.join(current_line + [word])
            test_surface = FONTS['medium'].render(test_line, True, COLORS['text'])

            if test_surface.get_width() <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    lines.append(word)
                    current_line = []

        if current_line:
            lines.append(' '.join(current_line))

        # Отрисовка описания
        y_pos = 290
        for line in lines:
            line_surface = FONTS['medium'].render(line, True, COLORS['text'])
            self.screen.blit(line_surface, (170, y_pos))
            y_pos += 30

        # Эффекты сна
        y_pos += 20

        if dream['type'] == 'warning':
            effect_header = FONTS['medium'].render("⚠️ Если не послушаться сна:", True, COLORS['warning'])
            self.screen.blit(effect_header, (170, y_pos))
            y_pos += 30

            # Показываем штрафы
            penalty = dream['penalty']
            penalty_text = []
            if 'stress' in penalty:
                penalty_text.append(f"+{penalty['stress']} стресса")
            if 'paranoia' in penalty:
                penalty_text.append(f"+{penalty['paranoia']} паранойи")
            if 'energy' in penalty:
                penalty_text.append(f"{penalty['energy']} энергии")

            penalty_str = ", ".join(penalty_text)

            # Указываем что нужно избегать
            if dream['target'] == 'location':
                target_text = f"Избегайте: {dream['location']} ({penalty_str})"
            else:
                target_text = f"Избегайте: {dream['activity']} ({penalty_str})"

            target_surface = FONTS['small'].render(target_text, True, COLORS['danger'])
            self.screen.blit(target_surface, (190, y_pos))

        else:  # motivating
            effect_header = FONTS['medium'].render("✨ Если послушаться сна:", True, COLORS['success'])
            self.screen.blit(effect_header, (170, y_pos))
            y_pos += 30

            # Показываем бонусы
            bonus = dream['bonus']
            bonus_text = []
            if 'stress' in bonus:
                bonus_text.append(f"{bonus['stress']} стресса")
            if 'paranoia' in bonus:
                bonus_text.append(f"{bonus['paranoia']} паранойи")
            if 'energy' in bonus:
                bonus_text.append(f"+{bonus['energy']} энергии")

            bonus_str = ", ".join(bonus_text)

            # Указываем что нужно сделать
            if dream['target'] == 'location':
                target_text = f"Посетите: {dream['location']} ({bonus_str})"
            else:
                target_text = f"Сделайте: {dream['activity']} ({bonus_str})"

            target_surface = FONTS['small'].render(target_text, True, COLORS['success'])
            self.screen.blit(target_surface, (190, y_pos))
            y_pos += 25

            # Показываем штраф за невыполнение
            penalty_if_not = dream['penalty_if_not_done']
            penalty_text = []
            if 'stress' in penalty_if_not:
                penalty_text.append(f"+{penalty_if_not['stress']} стресса")
            if 'paranoia' in penalty_if_not:
                penalty_text.append(f"+{penalty_if_not['paranoia']} паранойи")
            if 'energy' in penalty_if_not:
                penalty_text.append(f"{penalty_if_not['energy']} энергии")

            penalty_str = ", ".join(penalty_text)
            warning_text = f"⚠️ Если не выполнить: {penalty_str}"
            warning_surface = FONTS['small'].render(warning_text, True, COLORS['warning'])
            self.screen.blit(warning_surface, (190, y_pos))

        # Кнопка закрытия
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = pygame.mouse.get_pressed()[0]

        close_btn = Button(popup_rect.centerx - 60, popup_rect.bottom - 60, 120, 40, "Проснуться", 'medium')

        if (close_btn.update(mouse_pos, mouse_clicked) and
                self.can_click_button('dream_close')):
            self.register_button_click('dream_close')
            self.game_state.show_dream_popup = False
            self.game_state.current_dream = None
        else:
            close_btn.update(mouse_pos, False)

        close_btn.draw(self.screen)

    def draw_voice_message_popup(self):
        """Draw voice message popup window (like event popup)"""
        if not self.game_state.show_voice_message_popup or not self.game_state.current_voice_message:
            return

        # Semi-transparent overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        # Popup window - slightly larger for voice messages
        popup_rect = pygame.Rect(200, 150, 800, 500)
        pygame.draw.rect(self.screen, COLORS['panel'], popup_rect, border_radius=10)
        pygame.draw.rect(self.screen, COLORS['accent'], popup_rect, 3, border_radius=10)

        voice_message = self.game_state.current_voice_message
        tone = voice_message.get('tone', 'neutral')

        # Voice icon based on tone
        if tone in ['impressed', 'encouraging', 'supportive']:
            voice_icon = "😊"
            title_color = COLORS['success']
        elif tone in ['angry', 'paranoid']:
            voice_icon = "😠"
            title_color = COLORS['danger']
        elif tone in ['concerned', 'disappointed']:
            voice_icon = "😐"
            title_color = COLORS['warning']
        elif tone == 'grudging_respect':
            voice_icon = "🤔"
            title_color = COLORS['accent']
        else:
            voice_icon = "💭"
            title_color = COLORS['text']

        # Title
        icon_surface = FONTS['title'].render(voice_icon, True, title_color)
        self.screen.blit(icon_surface, (220, 180))

        title_text = f"Внутренний голос - День {voice_message.get('day', 1)}"
        title_surface = FONTS['large'].render(title_text, True, title_color)
        self.screen.blit(title_surface, (270, 185))

        # Show performance indicator and task statistics for end-of-day messages
        stats_y = 220
        if 'performance_score' in voice_message:
            performance = voice_message.get('performance_score', 0)
            if performance >= 5:
                perf_text = "Отличное выступление!"
                perf_color = COLORS['success']
            elif performance >= 2:
                perf_text = "Хорошая работа"
                perf_color = COLORS['accent']
            elif performance >= 0:
                perf_text = "Средний результат"
                perf_color = COLORS['warning']
            else:
                perf_text = "Неудачный день"
                perf_color = COLORS['danger']

            perf_surface = FONTS['medium'].render(perf_text, True, perf_color)
            self.screen.blit(perf_surface, (220, stats_y))
            stats_y += 30

            # Summary stats for end-of-day messages
            stats = [
                f"Энергия: {int(self.game_state.energy)}%",
                f"Стресс: {int(self.game_state.stress)}%",
                f"Паранойя: {int(self.game_state.paranoia)}%"
            ]

            stats_x = 220
            for stat in stats:
                stat_surface = FONTS['small'].render(stat, True, COLORS['text'])
                self.screen.blit(stat_surface, (stats_x, stats_y))
                stats_x += stat_surface.get_width() + 30

            stats_y += 25

        # Task statistics section - теперь размещаем ПОСЛЕ основного сообщения
        # (код перенесен в конец, после отрисовки основного сообщения)

        # Voice message with improved word wrapping
        message_text = voice_message['message']

        # Улучшенный перенос слов с учетом реальной ширины текста
        words = message_text.split()
        lines = []
        current_line = []
        max_width = 750  # Максимальная ширина строки в пикселях

        for word in words:
            # Проверяем, поместится ли слово в текущую строку
            test_line = ' '.join(current_line + [word])
            test_surface = FONTS['medium'].render(test_line, True, COLORS['text'])

            if test_surface.get_width() <= max_width:
                current_line.append(word)
            else:
                if current_line:  # Если в строке есть слова, сохраняем её
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:  # Если слово слишком длинное
                    lines.append(word)
                    current_line = []

        # Добавляем последнюю строку
        if current_line:
            lines.append(' '.join(current_line))

        # Draw message lines с лучшим расчетом позиции
        message_start_y = 290 if 'performance_score' in voice_message else 250
        message_y_pos = message_start_y
        line_height = 25  # Уменьшаем межстрочный интервал

        # Рассчитаем место для основного сообщения (оставим место для отчёта по заданиям)
        reserved_space_for_tasks = 150 if 'task_statistics' in voice_message else 0
        max_message_height = popup_rect.bottom - 120 - reserved_space_for_tasks  # Оставляем место для кнопки и заданий

        for i, line in enumerate(lines):
            if message_y_pos + line_height > max_message_height:
                # Если строки не помещаются, показываем многоточие
                if i > 0:  # Если уже показали хотя бы одну строку
                    ellipsis_surface = FONTS['medium'].render("...", True, COLORS['text'])
                    self.screen.blit(ellipsis_surface, (220, message_y_pos))
                break

            line_surface = FONTS['medium'].render(line, True, COLORS['text'])
            self.screen.blit(line_surface, (220, message_y_pos))
            message_y_pos += line_height

        # Теперь рисуем отчёт по заданиям ПОСЛЕ основного сообщения
        tasks_start_y = max(message_y_pos + 20,
                            max_message_height + 10)  # Начинаем после сообщения или в зарезервированном месте

        # Task statistics section (only if voice system is active and there are task stats)
        # Размещаем ПОСЛЕ основного сообщения
        if 'task_statistics' in voice_message and self.game_state.day >= 3:
            task_stats = voice_message['task_statistics']

            # Task summary header
            task_header_surface = FONTS['medium'].render("📋 Отчёт по заданиям:", True, COLORS['accent'])
            self.screen.blit(task_header_surface, (220, tasks_start_y))
            current_y = tasks_start_y + 25

            # Task completion summary
            completed_count = len(task_stats['completed_tasks'])
            failed_count = len(task_stats['failed_tasks'])
            total_tasks = completed_count + failed_count

            if total_tasks > 0:
                # Summary line
                summary_text = f"Выполнено: {completed_count}/{total_tasks}"
                summary_color = COLORS['success'] if completed_count == total_tasks else COLORS[
                    'warning'] if completed_count > 0 else COLORS['danger']
                summary_surface = FONTS['small'].render(summary_text, True, summary_color)
                self.screen.blit(summary_surface, (230, current_y))
                current_y += 18

                # Rewards earned
                if task_stats['total_card_points_earned'] > 0 or task_stats['total_relationship_gained'] > 0:
                    rewards_text = f"✅ Награды: +{task_stats['total_card_points_earned']} очков карт, +{task_stats['total_relationship_gained']} отношений"
                    rewards_surface = FONTS['small'].render(rewards_text, True, COLORS['success'])
                    self.screen.blit(rewards_surface, (230, current_y))
                    current_y += 16

                # Penalties applied
                paranoia_penalty = task_stats.get('total_paranoia_penalty', 0)
                if task_stats['total_relationship_lost'] > 0 or paranoia_penalty > 0:
                    penalties_text = f"❌ Штрафы: -{task_stats['total_relationship_lost']} отношений, +{paranoia_penalty} паранойи"
                    penalties_surface = FONTS['small'].render(penalties_text, True, COLORS['danger'])
                    self.screen.blit(penalties_surface, (230, current_y))
                    current_y += 16

                # Detailed task list - показываем ВСЕ задания
                button_y_position = popup_rect.bottom - 60  # Позиция кнопки
                available_space = button_y_position - current_y - 20  # Доступное место

                # Completed tasks - показываем ВСЕ выполненные
                if task_stats['completed_tasks']:
                    completed_header = FONTS['small'].render("✅ Выполненные:", True, COLORS['success'])
                    self.screen.blit(completed_header, (240, current_y))
                    current_y += 16

                    for task in task_stats['completed_tasks']:  # Показываем ВСЕ выполненные задания
                        if current_y + 14 > button_y_position - 20:
                            break  # Останавливаемся если места не хватает
                        task_line = f"  • {task['name']}"
                        if len(task_line) > 50:  # Немного увеличил лимит
                            task_line = task_line[:47] + "..."
                        task_surface = FONTS['tiny'].render(task_line, True, COLORS['text'])
                        self.screen.blit(task_surface, (250, current_y))
                        current_y += 14

                # Failed tasks - показываем ВСЕ проваленные
                if task_stats['failed_tasks'] and current_y + 30 < button_y_position:  # Проверяем что есть место
                    failed_header = FONTS['small'].render("❌ Провалены:", True, COLORS['danger'])
                    self.screen.blit(failed_header, (240, current_y))
                    current_y += 16

                    for task in task_stats['failed_tasks']:  # Показываем ВСЕ проваленные задания
                        if current_y + 14 > button_y_position - 20:
                            break  # Останавливаемся если места не хватает
                        task_line = f"  • {task['name']}"
                        if len(task_line) > 50:  # Немного увеличил лимит
                            task_line = task_line[:47] + "..."
                        task_surface = FONTS['tiny'].render(task_line, True, COLORS['text'])
                        self.screen.blit(task_surface, (250, current_y))
                        current_y += 14
            else:
                no_tasks_surface = FONTS['small'].render("Заданий сегодня не было", True, COLORS['text_dim'])
                self.screen.blit(no_tasks_surface, (230, current_y))

        # Close button
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = pygame.mouse.get_pressed()[0]

        close_btn = Button(popup_rect.centerx - 60, popup_rect.bottom - 60, 120, 40, "Хорошо", 'medium')

        if (close_btn.update(mouse_pos, mouse_clicked) and
                self.can_click_button('voice_message_close')):
            self.register_button_click('voice_message_close')
            self.game_state.show_voice_message_popup = False
            self.game_state.current_voice_message = None

            # 🌙 Генерируем и показываем сон сразу после закрытия голосового сообщения
            dream = self.game_state.dream_system.generate_dream(
                self.game_state.stress,
                self.game_state.paranoia,
                self.game_state.energy
            )

            if dream:
                self.game_state.current_dream = dream
                self.game_state.show_dream_popup = True

                # Устанавливаем предупреждения или мотивацию
                if dream['type'] == 'warning':
                    self.game_state.dream_warnings = {
                        'type': dream['target'],
                        'penalty': dream['penalty']
                    }
                    if dream['target'] == 'location':
                        self.game_state.dream_warnings['location'] = dream['location']
                    elif dream['target'] == 'activity':
                        self.game_state.dream_warnings['activity'] = dream['activity']
                    print(f"⚠️ Предупреждающий сон: {dream}")

                elif dream['type'] == 'motivating':
                    self.game_state.dream_motivations = {
                        'type': dream['target'],
                        'bonus': dream['bonus'],
                        'penalty_if_not_done': dream['penalty_if_not_done']
                    }
                    if dream['target'] == 'location':
                        self.game_state.dream_motivations['location'] = dream['location']
                    elif dream['target'] == 'activity':
                        self.game_state.dream_motivations['activity'] = dream['activity']
                    # Устанавливаем флаг для проверки в конце дня
                    self.game_state.dream_system.pending_motivation_check = True
                    print(f"✨ Мотивирующий сон: {dream}")
            else:
                print("🛌 Снов не приснилось сегодня")
        else:
            close_btn.update(mouse_pos, False)

        close_btn.draw(self.screen)

    def replace_random_voice_task(self):
        """Replace a random voice task with a new one - WITH INDIVIDUAL BUTTON PROTECTION"""
        if not self.can_click_button('replace_voice_task'):
            return

        # Check if voice system is unlocked
        if self.game_state.day < 3:
            self.game_state.add_message("Система внутреннего голоса ещё не активна", 'warning')
            return

        self.register_button_click('replace_voice_task')

        if not hasattr(self.game_state, 'voice_tasks') or len(self.game_state.voice_tasks) == 0:
            self.game_state.add_message("Нет заданий для замены", 'warning')
            return

        if self.game_state.inner_voice_relationship < -20:
            self.game_state.add_message("Голос слишком враждебен для замены заданий", 'warning')
            return

        # Cost for replacing a task (increased)
        cost = max(3, len(self.game_state.voice_tasks) + 1)  # increased base cost
        if self.game_state.card_points < cost:
            self.game_state.add_message(f"Нужно {cost} очков для замены задания", 'warning')
            return

        self.game_state.card_points -= cost

        # Select a random task to replace (exclude completed tasks)
        available_tasks = [task for task in self.game_state.voice_tasks
                           if task['id'] not in getattr(self.game_state, 'completed_voice_tasks', [])]

        if not available_tasks:
            self.game_state.add_message("Все задания уже выполнены, нечего заменять", 'warning')
            return

        # Remove random task
        task_to_replace = random.choice(available_tasks)
        old_task_name = task_to_replace['name']
        self.game_state.voice_tasks.remove(task_to_replace)

        # Generate new task to replace it
        original_tasks = self.game_state.voice_tasks.copy()

        # Temporarily create new game state for task generation
        temp_game_state = GameState()
        temp_game_state.day = self.game_state.day
        temp_game_state.inner_voice_relationship = self.game_state.inner_voice_relationship
        temp_game_state.timeline_activities = self.game_state.timeline_activities
        temp_game_state.generate_voice_tasks()

        # Take first new task and add it to original list
        if temp_game_state.voice_tasks:
            new_task = temp_game_state.voice_tasks[0]
            # Make sure new task has unique ID to avoid conflicts
            new_task['id'] = f"{new_task['id']}_replacement_{self.game_state.day}"
            self.game_state.voice_tasks = original_tasks + [new_task]
            self.game_state.add_message(f"🔄 Заменено: '{old_task_name}' → '{new_task['name']}'", 'success')
        else:
            # Fallback if generation failed
            self.game_state.voice_tasks = original_tasks
            self.game_state.add_message("Не удалось сгенерировать новое задание", 'warning')

    def toggle_music(self):
        """Toggle music on/off"""
        if hasattr(self, 'music_enabled') and not self.music_enabled:
            # Turn music on
            self.music_enabled = True
            self.music_manager.start_playlist('normal')
            self.game_state.add_message("Музыка включена", 'success')
        else:
            # Turn music off
            self.music_enabled = False
            self.music_manager.stop()
            self.game_state.add_message("Музыка выключена", 'info')

    def save_current_schedule(self):
        """Save current timeline activities"""
        if not self.game_state.timeline_activities:
            self.game_state.add_message("Нет активностей для сохранения", 'warning')
            return

        # Create a deep copy of current schedule
        self.game_state.saved_schedule = []
        for ta in self.game_state.timeline_activities:
            saved_activity = {
                'activity': ta.activity.copy(),  # Copy the activity dict
                'start_time': ta.start_time,
                'end_time': ta.end_time
            }
            self.game_state.saved_schedule.append(saved_activity)

        self.game_state.add_message(f"Сохранён распорядок с {len(self.game_state.saved_schedule)} активностями",
                                    'success')

    def load_saved_schedule(self):
        """Load previously saved timeline activities"""
        if not hasattr(self.game_state, 'saved_schedule') or not self.game_state.saved_schedule:
            self.game_state.add_message("Нет сохранённого распорядка", 'warning')
            return

        # Clear current timeline
        self.game_state.timeline_activities.clear()

        # Restore saved activities
        loaded_count = 0
        failed_count = 0

        for saved_activity in self.game_state.saved_schedule:
            activity = saved_activity['activity']
            start_time = saved_activity['start_time']

            # Check if activity is available on current day of week
            if not self.game_state.is_activity_available_today(activity):
                failed_count += 1
                continue

            # Try to place the activity
            if self.game_state.can_place_activity_at_time(activity, start_time):
                end_time = start_time + activity['duration']

                # Calculate position and size with precise alignment
                x = self.game_state.get_hour_x_position(start_time)
                width = self.game_state.get_hour_x_position(end_time) - x
                y = self.game_state.timeline_rect.y + 60
                height = 50

                # Create timeline activity
                timeline_activity = TimelineActivity(activity, start_time, end_time, x, y, width, height)
                self.game_state.timeline_activities.append(timeline_activity)
                loaded_count += 1
            else:
                failed_count += 1

        # Update conflicts
        self.game_state.update_timeline_conflicts()

        # Report results
        if failed_count == 0:
            self.game_state.add_message(f"Загружен распорядок: {loaded_count} активностей", 'success')
        else:
            self.game_state.add_message(f"Загружено: {loaded_count} активностей, не удалось: {failed_count}", 'warning')

    def run(self):
        """Main game loop"""
        while self.running:
            # Handle events
            self.handle_events()

            # Update game state
            self.game_state.update_messages()

            # Update status effects - always call this since the system should always be available
            self.game_state.update_status_effects()

            # Постоянная проверка событий в основном цикле
            if self.game_state.phase == 'playing':
                if hasattr(self.game_state, 'show_event_popup') and self.game_state.show_event_popup:
                    pass  # Событие уже активно, не вызываем ещё
                else:
                    # print(f"🔍 Основной цикл: проверка событий в {self.game_state.current_time:.1f}")
                    self.check_for_events()

            # Check for game over conditions in main loop
            if (self.game_state.phase not in ['game_over', 'game_ending'] and
                    self.check_game_over_conditions()):
                # Skip further updates if game is over
                pass
            else:
                # Update music based on mental state (only if enabled)
                if self.music_enabled:
                    self.music_manager.update(self.game_state.stress, self.game_state.paranoia)

            # Clear screen
            self.screen.fill(COLORS['bg'])

            # Check if we're in restart transition
            if self.handle_restart_transition():
                # Draw transition screen and skip normal UI
                self.draw_restart_transition()
            else:
                # Reset tooltip data for this frame
                self.pending_tooltip = None
                self.pending_event_tooltip = None

                # Check if we should draw the ending screen
                if self.game_state.phase == 'game_ending':
                    self.draw_game_ending_screen()
                elif self.game_state.phase == 'dreaming':
                    # 🌙 Отрисовка фазы сновидения
                    self.draw_dream_screen()
                else:
                    # Draw normal UI components
                    self.draw_header()
                    self.draw_activities_panel()
                    self.draw_timeline()
                    self.draw_status_effects_bar()
                    self.draw_prediction_panel()  # Draw prediction panel on top
                    self.draw_phase_instructions()
                    self.draw_buttons()
                    self.draw_messages()
                    self.draw_help_panel()
                    self.draw_event_popup()
                    self.draw_voice_message_popup()
                    self.draw_dream_popup()  # 🌙 Отрисовка сна
                    self.draw_cards_panel()
                    self.draw_voice_panel()

                    # Draw activity tooltips LAST so they appear on top of everything else
                    self.draw_activity_tooltips()

            # Update display
            pygame.display.flip()
            self.clock.tick(FPS)

        # Clean up
        self.music_manager.stop()
        pygame.quit()
        sys.exit()


def main():
    """Main function to start the game"""
    try:
        game = VisualDayPlanningGame()
        game.run()
    except Exception as e:
        print(f"Ошибка запуска игры: {e}")
        pygame.quit()
        sys.exit(1)


if __name__ == "__main__":
    main()
