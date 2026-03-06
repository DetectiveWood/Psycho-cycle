# -*- coding: utf-8 -*-
import pygame
import random
import time
from .dreams import DreamSystem
from timeline import TimelineActivity
from constants import COLORS, FONTS, WINDOW_WIDTH, WINDOW_HEIGHT, FPS

class GameState:
    def __init__(self):
        self.day = 15
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
        self.card_points = 0  # Always start with 0 points

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
                'effect': {'stress': -25},
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
                'effect': {'paranoia': -18},
                'unlock_day': 2
            },
            {
                'id': 'meditation',
                'name': 'Глубокая медитация',
                'icon': '🕯️',
                'description': 'Значительно снижает стресс и паранойю',
                'cost': 21,
                'rarity': 'uncommon',
                'effect_type': 'immediate',
                'effect': {'stress': -35, 'paranoia': -28},
                'unlock_day': 4
            },
            {
                'id': 'coffee_break',
                'name': 'Кофе-пауза',
                'icon': '☕',
                'description': 'Небольшое восстановление энергии и снижение стресса',
                'cost': 15,
                'rarity': 'common',
                'effect_type': 'immediate',
                'effect': {'energy': 17, 'stress': -13},
                'unlock_day': 1
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
                'cost': 15,
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
            ##{
            ##'id': 'perfect_timing',
            ##'name': 'Идеальный тайминг',
            ##'icon': '⏱️',
            ##'description': 'Позволяет переместить любую активность',
            ##'cost': 0,
            ##'rarity': 'uncommon',
            ##'effect_type': 'time_manipulation',
            ##'effect': {'move_activity': True},
            ##'unlock_day': 6
            ##},

            # Специальные карты (9 карт)
            {
                'id': 'time_rewind',
                'name': 'Возврат времени',
                'icon': '⏪',
                'description': 'Отменяет последнее событие',
                'cost': 17,
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
                'cost': 13,
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
                'cost': 24,
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
                'cost': 14,
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
                'cost': 16,
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
            },

            # Карты постепенного восстановления (6 карт)
            {
                'id': 'slow_stress_relief',
                'name': 'Глубокий релакс',
                'icon': '🧘‍♀️',
                'description': 'Снижает стресс на 5 каждый час в течение 10 часов (-50 всего)',
                'cost': 18,
                'rarity': 'uncommon',
                'effect_type': 'status',
                'effect': {'status_id': 'deep_relaxation', 'status_name': 'Глубокий релакс', 'status_icon': '🧘‍♀️',
                           'duration_hours': 10, 'effects': {'hourly_stress': -5}},
                'unlock_day': 4
            },
            {
                'id': 'sustained_energy',
                'name': 'Долгая бодрость',
                'icon': '⚡🔋',
                'description': 'Восстанавливает 6 энергии каждый час в течение 8 часов (+48 всего)',
                'cost': 20,
                'rarity': 'uncommon',
                'effect_type': 'status',
                'effect': {'status_id': 'energy_surge', 'status_name': 'Долгая бодрость', 'status_icon': '⚡🔋',
                           'duration_hours': 8, 'effects': {'hourly_energy': 6}},
                'unlock_day': 5
            },
            {
                'id': 'paranoia_drain',
                'name': 'Успокоение умов',
                'icon': '🧠💫',
                'description': 'Снижает паранойю на 4 каждый час в течение 12 часов (-48 всего)',
                'cost': 22,
                'rarity': 'uncommon',
                'effect_type': 'status',
                'effect': {'status_id': 'mind_calm', 'status_name': 'Успокоение умов', 'status_icon': '🧠💫',
                           'duration_hours': 12, 'effects': {'hourly_paranoia': -4}},
                'unlock_day': 6
            },
            {
                'id': 'harmony_balance',
                'name': 'Гармоничный баланс',
                'icon': '☯️',
                'description': 'Одновременно восстанавливает: -4 стресса, -2 паранойи, +3 энергии в час (6 часов)',
                'cost': 25,
                'rarity': 'rare',
                'effect_type': 'status',
                'effect': {'status_id': 'harmony_state', 'status_name': 'Гармоничный баланс', 'status_icon': '☯️',
                           'duration_hours': 6,
                           'effects': {'hourly_stress': -4, 'hourly_paranoia': -2, 'hourly_energy': 3}},
                'unlock_day': 8
            },
            {
                'id': 'fortress_of_peace',
                'name': 'Крепость мира',
                'icon': '🏰💎',
                'description': 'Мощная защита: -6 стресса, -3 паранойи каждый час (8 часов)',
                'cost': 28,
                'rarity': 'rare',
                'effect_type': 'status',
                'effect': {'status_id': 'peace_fortress', 'status_name': 'Крепость мира', 'status_icon': '🏰💎',
                           'duration_hours': 8, 'effects': {'hourly_stress': -6, 'hourly_paranoia': -3}},
                'unlock_day': 10
            },
            {
                'id': 'total_renewal',
                'name': 'Полное возрождение',
                'icon': '✨🌟',
                'description': 'Легендарная карта: полное восстановление всех ресурсов на час (+30 энергии, -8 стресса, -5 паранойи, повторяется 5 часов)',
                'cost': 35,
                'rarity': 'legendary',
                'effect_type': 'status',
                'effect': {'status_id': 'total_renewal_state', 'status_name': 'Полное возрождение', 'status_icon': '✨🌟',
                           'duration_hours': 5,
                           'effects': {'hourly_energy': 8, 'hourly_stress': -8, 'hourly_paranoia': -5}},
                'unlock_day': 14
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
                'check': lambda game: game.energy >= 50 and game.stress <= 30 and game.paranoia <= 30
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
                'reward': {'card_points': 12, 'voice_relationship': 20},
                'difficulty': 5,
                'check': lambda game: len(set(ta.activity['name'] for ta in game.timeline_activities)) >= 12
            },
            {
                'id': 'perfectionist',
                'name': 'Перфекционист',
                'description': 'Идеальный день: энергия >80%, стресс <20%',
                'reward': {'card_points': 12, 'voice_relationship': 25},
                'difficulty': 5,
                'check': lambda game: (game.energy > 80 and game.stress < 20 and
                                       not any(ta.has_conflict for ta in game.timeline_activities))
            },
            {
                'id': 'zen_master',
                'name': 'Мастер дзен',
                'description': 'Закончи день с паранойей <10% и стрессом <25%',
                'reward': {'card_points': 12, 'voice_relationship': 20},
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
        selected_activities = set()  # Track activities required by tasks
        selected_activity_counts = {}  # Track count requirements (exactly_X_activities)

        # Create a copy of available tasks to avoid modifying the original
        available_copy = available_tasks.copy()

        # Helper function to check if two time ranges overlap
        def times_overlap(start1, end1, start2, end2):
            return not (end1 <= start2 or start1 >= end2)

        # Helper function to check if task conflicts with already selected ones
        def task_conflicts_with_selected(task, selected):
            """Check if a task creates logical conflicts with already selected tasks"""

            # Check for conflicting 'exactly_X_activities' tasks
            if task['id'].startswith('exactly_') and 'activities' in task['id']:
                # Extract the number from task ID (e.g., 'exactly_9_activities' -> 9)
                try:
                    if 'activities' in task['id']:
                        # Handle cases like 'exactly_9_activities' or 'twelve_different_activities'
                        if 'exactly' in task['id']:
                            num_str = task['id'].split('_')[1]  # 'exactly_9_activities' -> '9'
                            required_count = int(num_str)
                        else:
                            # twelve_different_activities doesn't have a number in ID
                            return False

                        # Check if we already have a different 'exactly_X_activities' task
                        for selected_task in selected:
                            if selected_task['id'].startswith('exactly_') and 'activities' in selected_task['id']:
                                try:
                                    selected_num_str = selected_task['id'].split('_')[1]
                                    selected_count = int(selected_num_str)
                                    if selected_count != required_count:
                                        # Conflict! Two different 'exactly_X_activities' tasks
                                        return True
                                except:
                                    pass
                except:
                    pass

            # Check for multiple forbidden_activity tasks (can't forbid the same activity twice with different meanings)
            if 'forbidden_activity' in task:
                for selected_task in selected:
                    if 'forbidden_activity' in selected_task:
                        if task['forbidden_activity'] == selected_task['forbidden_activity']:
                            # Same forbidden activity - redundant
                            return True

            return False

        # Select tasks ensuring no duplicates and no time conflicts
        for _ in range(num_tasks):
            if not available_copy:
                break

            # Try to find a task that doesn't conflict with already selected tasks
            attempts = 0
            max_attempts = 15  # Increased to find non-conflicting tasks

            while attempts < max_attempts and available_copy:
                chosen_task = random.choice(available_copy)

                # Skip if this task conflicts with already selected ones
                if task_conflicts_with_selected(chosen_task, selected_tasks):
                    available_copy = [task for task in available_copy if task['id'] != chosen_task['id']]
                    attempts += 1
                    continue

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
                    # Not a specific time task, check for logical conflicts
                    selected_tasks.append(task_copy)
                    available_copy = [task for task in available_copy if task['id'] != chosen_task['id']]
                    break

                attempts += 1

        # Ensure we clear existing tasks before adding new ones
        if not hasattr(self, 'voice_tasks'):
            self.voice_tasks = []

        # Debug logging for task selection
        if selected_tasks:
            print(f"\n🎙️ ГОЛОСОВЫЕ ЗАДАНИЯ (День {self.day}, отношения: {relationship}):")
            for task in selected_tasks:
                print(f"   📌 {task['name']}: {task['description']}")
                if 'required_time' in task:
                    print(f"      ⏰ Время: {task['required_time']}")
        else:
            print(f"\n🎙️ ГОЛОСОВЫЕ ЗАДАНИЯ (День {self.day}): Нет доступных заданий")

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
                    'accept': {'stress': 10, 'paranoia': 15, 'energy': -20},
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
                    'accept': {'stress': -10, 'paranoia': -5, 'energy': -20},
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

            # Apply hourly effects for all status types
            effects = status.get('effects', {})
            if 'hourly_stress' in effects or 'hourly_paranoia' in effects or 'hourly_energy' in effects:
                # Check if a full hour has passed since last application
                if 'last_hourly_application' not in status:
                    status['last_hourly_application'] = status['start_time']

                hours_since_last = current_time - status['last_hourly_application']
                # Apply effects only once per full hour (1.0 game hour = 60 real seconds)
                if hours_since_last >= 1.0:  # At least 1 hour passed
                    if 'hourly_stress' in effects:
                        stress_increase = effects['hourly_stress']
                        old_stress = self.stress
                        self.stress = min(100, max(0, self.stress + stress_increase))

                        # 🖥️ КОНСОЛЬНЫЙ ВЫВОД: Почасовой стресс от статусов
                        print(
                            f"📊 СТРЕСС ОТ СТАТУСА '{status['name']}': {old_stress}→{self.stress} ({stress_increase:+d})")

                        # 📝 Лог событий
                        message_type = 'success' if stress_increase < 0 else 'warning'
                        self.add_message(
                            f"📱 {status['name']}: {old_stress}→{self.stress} стресса ({stress_increase:+d})",
                            message_type
                        )

                    if 'hourly_paranoia' in effects:
                        paranoia_increase = effects['hourly_paranoia']
                        old_paranoia = self.paranoia
                        self.paranoia = min(100, max(0, self.paranoia + paranoia_increase))

                        # 📝 Лог событий
                        message_type = 'success' if paranoia_increase < 0 else 'warning'
                        self.add_message(
                            f"📱 {status['name']}: {old_paranoia}→{self.paranoia} паранойи ({paranoia_increase:+d})",
                            message_type
                        )

                    if 'hourly_energy' in effects:
                        energy_increase = effects['hourly_energy']
                        old_energy = self.energy
                        self.energy = min(100, max(0, self.energy + energy_increase))

                        # 📝 Лог событий
                        message_type = 'success' if energy_increase > 0 else 'warning'
                        self.add_message(
                            f"📱 {status['name']}: {old_energy}→{self.energy} энергии ({energy_increase:+d})",
                            message_type
                        )

                    # Update last application time - move it forward by exactly 1 hour
                    # This prevents the effect from triggering multiple times per hour
                    status['last_hourly_application'] += 1.0

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
                "Помнишь, что я тебе говорил о 30 дне? Он все ближе и ближе. Осталось всего 20 дней. Надеюсь ты уже освоил все, что я тебе показал? "
                "Кстати, есть ещё кое-что интересное, что ты пока не знаешь. Оно откроется позже. Готовься к неожиданностям...")
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
