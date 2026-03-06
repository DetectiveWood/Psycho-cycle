# -*- coding: utf-8 -*-
import random

class DreamSystem:
    """Система снов с различными категориями"""

    def __init__(self):
        self.dreams = {
            # Предупреждающие сны (warning) - негативные сны о локациях/действиях
            'warning_restaurant': {
                'type': 'warning',
                'target': 'location',
                'location': 'Ресторан',
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
                'activity': 'Прогулка',  # Будет матчиться с "Утренняя прогулка" и "Вечерняя прогулка"
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
                'location': 'Кинотеатр',
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
                'location': 'Спортзал',
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
            'motivating_park': {
                'type': 'motivating',
                'target': 'location',
                'location': 'Улица',
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