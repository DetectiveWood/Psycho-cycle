import random, time, pygame
import sys, os
import threading

# Инициализация pygame и микшера для управления звуком
pygame.init()
pygame.mixer.init()

# Устанавливаем обработчик события окончания композиции
pygame.mixer.music.set_endevent(pygame.USEREVENT)
music_thread_running = True

# Глобальные переменные для учёта прогрессии, психического состояния и паранойи
task_progress = {}  # Словарь для хранения прогресса по задачам
total_sanity = 100  # Начальное психическое состояние (максимум 100)
total_paranoia = 0  # Начальный уровень паранойи

# Альбомы с музыкой (замените на реальные файлы)
CALM_ALBUM = [
    "Family.ogg",
    "Alice.ogg",
    "Rain.ogg"
]

TENSE_ALBUM = [
    "Fear.ogg",
    "Silent.ogg",
    "Lily.ogg",
]

PARANOID_ALBUM = [
    "Anthropocene.ogg",
    "Birthday.ogg",
    "TheEnd.ogg",
    "Crystals.ogg"
]

# Текущий альбом и индекс текущей композиции
current_album = CALM_ALBUM
current_track_index = 0

# Список карточек
CARDS = [
    {
        "name": "Превозмогание",
        "effect": "extend_day",  # Позволяет закончить день в 24:00
        "description": "Позволяет закончить день в 24:00 вместо 20:00.",
    },
    {
        "name": "Божественная чистота сознания",
        "effect": "remove_paranoia_effect",  # Убирает влияние паранойи на один день
        "description": "Полностью убирает влияние паранойи на один день.",
    },
    {
        "name": "Затишье перед бурей",
        "effect": "restore_sanity",  # Восстанавливает 50 единиц рассудка, но увеличивает паранойю на 10
        "description": "Восстанавливает 50 единиц рассудка, но увеличивает паранойю на 10.",
    },
    {
        "name": "Пламенное очищение",
        "effect": "restore_paranoia",  # Уменьшает паранойю на 35 единиц, но уменьшает рассудок на 65
        "description": "Уменьшает паранойю на 35 единиц, но уменьшает рассудок на 65.",
    },
    {
        "name": "Ради высшей цели",
        "effect": "delete_task",  # Убирает текущее задание без штрафов.
        "description": "Убирает текущее задание без штрафов.",
    },
    {
        "name": "Величайшее испытание",
        "effect": "restore_all_sanity",  # На протяжении всего дня урон по рассудку будет увеличен в два раза. В конце дня восстанавливает 100 рассудка и уменьшает паранойю на 15.
        "description": "На протяжении всего дня урон по рассудку будет увеличен в два раза. В конце дня восстанавливает 100 рассудка и уменьшает паранойю на 15.",
    },
    {
        "name": "Абсолютное опустошение",
        "effect": "restore_all_paranoia",  # На протяжении всего дня урон по рассудку будет увеличен в два раза. В конце дня восстанавливает 30 рассудка и уменьшает паранойю на 75.
        "description": "На протяжении всего дня восстановление рассудка будет отключено. В конце дня восстанавливает 30 рассудка и уменьшает паранойю на 75.",
    }
]

# Инвентарь игрока (карточки)
player_inventory = {"Превозмогание": 1}

day_extended = False
paranoia_effect_disabled = False
task_activated = False
double_damage = False
no_restore = False

max_day_time = 960 if day_extended else 720

# Заранее подготовленные задачи
TASKS = [
    {"description": "Выпить чай", "time": 15, "mandatory": False, "sanity": 5, "location": "дом", "time_window": None, "required_steps": 1, "current_steps": 0},
    {"description": "Погулять с собакой", "time": 30, "mandatory": False, "sanity": 10, "location": "улица", "time_window": None, "required_steps": 1, "current_steps": 0},
    {"description": "Сделать зарядку", "time": 20, "mandatory": False, "sanity": 15, "location": "дом", "time_window": None, "required_steps": 1, "current_steps": 0},
    {"description": "Приготовить завтрак", "time": 30, "mandatory": True, "sanity": -5, "location": "дом", "time_window": (0, 2 * 60), "required_steps": 1, "current_steps": 0},  # Только с 8:00 до 10:00
    {"description": "Почитать книгу", "time": 45, "mandatory": False, "sanity": 20, "location": "дом", "time_window": None, "required_steps": 1, "current_steps": 0},
    {"description": "Сходить на учебу", "time": 360, "mandatory": True, "sanity": -40, "location": "школа", "time_window": (1 * 60, 7 * 60), "required_steps": 1, "current_steps": 0},
    {"description": "Поиграть на компьютере", "time": 60, "mandatory": False, "sanity": -10, "location": "дом", "time_window": None, "required_steps": 1, "current_steps": 0},  # Обязательная задача
    {"description": "Сходить в магазин", "time": 45, "mandatory": True, "sanity": -15, "location": "улица", "time_window": None, "required_steps": 1, "current_steps": 0},
    {"description": "Посмотреть фильм", "time": 90, "mandatory": False, "sanity": 25, "location": "дом", "time_window": None, "required_steps": 1, "current_steps": 0},
    {"description": "Убраться в комнате", "time": 40, "mandatory": False, "sanity": -10, "location": "дом", "time_window": None, "required_steps": 1, "current_steps": 0},
    {"description": "Позвонить другу", "time": 20, "mandatory": False, "sanity": 10, "location": "дом", "time_window": None, "required_steps": 1, "current_steps": 0},
    {"description": "Сделать проект по учебе", "time": 75, "mandatory": False, "sanity": -25, "location": "дом", "time_window": None, "required_steps": 5, "current_steps": 0},
]

SPECIAL_TASKS = [
    {
        "description": "Убирать комнату три дня подряд",
        "condition": "clean_room_3_days",  # Условие выполнения
        "days_required": 3,  # Количество дней для выполнения
        "days_completed": 0,  # Текущее количество выполненных дней
        "reward": {"sanity": 20},  # Награда за выполнение
        "penalty": {"sanity": -30},  # Штраф за невыполнение
        "active": False  # Активно ли задание
    },
    {
        "description": "Встретиться с другом ровно в 18:00",
        "condition": "meet_friend_at_18",  # Условие выполнения
        "time_required": 18 * 60,  # Время выполнения (18:00 в минутах)
        "reward": {"sanity": 15},  # Награда за выполнение
        "penalty": {"sanity": -20},  # Штраф за невыполнение
        "active": False  # Активно ли задание
    }
]

EVENTS = [
    {
        "description": "Тебе позвонил друг и предложил встретиться.",
        "location": "дом",
        "options": [
            {"description": "Встретиться с другом", "time_impact": -30, "sanity_impact": 10, "paranoia_impact": 0},
            {"description": "Отказаться от встречи", "time_impact": 0, "sanity_impact": -10, "paranoia_impact": 0},
        ],
        "chance": 0.2,
    },
    {
        "description": "Ты услышал невнятное бормотание за своей спиной. Обернувшись ты понял, что сзади никого нет, но шепот не пропал...",
        "location": "дом",
        "options": [
            {"description": "Быстро уйти", "time_impact": 0, "sanity_impact": -5, "paranoia_impact": 10},
            {"description": "Прислушаться", "time_impact": -10, "sanity_impact": -10, "paranoia_impact": -5},
        ],
        "chance": 0.2,
    },
    {
        "description": "В углу комнаты мелькнула странная, скорченная, поломанная и неправильная тень.",
        "location": "дом",
        "options": [
            {"description": "Рассмотреть поближе", "time_impact": -10, "sanity_impact": -5, "paranoia_impact": -10},
            {"description": "Не обращать внимания", "time_impact": 0, "sanity_impact": -15, "paranoia_impact": 10},
        ],
        "chance": 0.2,
    },
    {
        "description": "Внезапно тебя посещает чувство абсолютного опустошения.",
        "location": "дом",
        "options": [
            {"description": "Отдохнуть и собраться с мыслями", "time_impact": -30, "sanity_impact": 20, "paranoia_impact": -10},
            {"description": "Продолжить заниматься делами не смотря ни на что", "time_impact": 0, "sanity_impact": -20, "paranoia_impact": 5},
        ],
        "chance": 0.2,
    },
    {
        "description": "Проходя по улице ты замечаешь человека, который очень подозрительно похож на тебя...",
        "location": "улица",
        "options": [
            {"description": "Немного проследовать за ним, чтобы рассмотреть получше", "time_impact": -20, "sanity_impact": 10, "paranoia_impact": -10},
            {"description": "Попытаться проигнорировать его и быстро уйти", "time_impact": 0, "sanity_impact": -15, "paranoia_impact": 10},
        ],
        "chance": 0.2,
    },
    {
        "description": "Ты встретил старого знакомого на улице.",
        "location": "улица",
        "options": [
            {"description": "Поговорить", "time_impact": -30, "sanity_impact": 10, "paranoia_impact": 0},
            {"description": "Сделать вид, что не заметил", "time_impact": 0, "sanity_impact": -10, "paranoia_impact": 5},
        ],
        "chance": 0.2,
    },
    {
        "description": "На улице пошёл дождь, и ты промок.",
        "location": "улица",
        "options": [
            {"description": "Вернуться домой и переодеться", "time_impact": -15, "sanity_impact": -5, "paranoia_impact": 0},
            {"description": "Продолжить путь под дождём", "time_impact": 0, "sanity_impact": -10, "paranoia_impact": 0},
        ],
        "chance": 0.1,
    },
    {
        "description": "Ты нашёл деньги на улице.",
        "location": "улица",
        "options": [
            {"description": "Потратить деньги на что-то приятное", "time_impact": -30, "sanity_impact": 15, "paranoia_impact": 0},
            {"description": "Оставить деньги на месте", "time_impact": 0, "sanity_impact": 0, "paranoia_impact": 0},
        ],
        "chance": 0.1   ,
    },
    {
        "description": "Ты случайно удалил важный файл.",
        "location": "дом",
        "options": [
            {"description": "Попытаться восстановить файл", "time_impact": -45, "sanity_impact": -10, "paranoia_impact": 5},
            {"description": "Смириться с потерей", "time_impact": 0, "sanity_impact": -20, "paranoia_impact": 0},
        ],
        "chance": 0.05,
    },
    {
        "description": "Ты услышал странные звуки за окном.",
        "location": "дом",
        "options": [
            {"description": "Посмотреть, что происходит", "time_impact": -10, "sanity_impact": -5, "paranoia_impact": 0},
            {"description": "Игнорировать звуки", "time_impact": 0, "sanity_impact": -10, "paranoia_impact": 10},
        ],
        "chance": 0.05 + (total_paranoia/250) + ((100-total_sanity)/250),
    },
    {
        "description": "Еще мгновенье назад все было как всегда, а теперь пространство вокруг вас заполонила черная мгла.",
        "location": "дом",
        "options": [
            {"description": "ПАРАНОЙЯ не должна захватить сознание - сосредоточиться на себе и успокоиться", "time_impact": -80, "sanity_impact": 30, "paranoia_impact": -20},
            {"description": "Нельзя допустить потерю драгоценного ВРЕМЕНИ - поглотить весь мрак, тем самым избавившись от него", "time_impact": 0, "sanity_impact": -30, "paranoia_impact": 20},
        ],
        "chance": 0.05 + (total_paranoia/250) + ((100-total_sanity)/250),
    },
    {
        "description": "Ты был абсолютно уверен, что идешь по знакомой улице, но осмотревшись понял, что потерялся.",
        "location": "улица",
        "options": [
            {"description": "Напрячь голову и попытаться вспомнить правильный путь", "time_impact": 10, "sanity_impact": -10, "paranoia_impact": 0},
            {"description": "Поддаться 6 чувству и побежать наугад", "time_impact": -15, "sanity_impact": 0, "paranoia_impact": 0},
        ],
        "chance": 0.05 + (total_paranoia/250) + ((100-total_sanity)/250),
    },
    {
        "description": "Ты заметил, что за тобой следят.",
        "location": "улица",
        "options": [
            {"description": "Ускорить шаг", "time_impact": -10, "sanity_impact": -20, "paranoia_impact": -15},
            {"description": "Игнорировать", "time_impact": 0, "sanity_impact": -10, "paranoia_impact": -5},
        ],
        "chance": 0.05 + (total_paranoia/250) + ((100-total_sanity)/250),
    },
]

def play_next_track():
    global current_album, current_track_index

    # Проверяем состояние игрока и выбираем подходящий альбом
    if total_sanity >= 70:
        if total_paranoia <= 50:
            new_album = CALM_ALBUM
        else:
            new_album = TENSE_ALBUM
    elif total_sanity >= 40:
        if total_paranoia <= 50:
            new_album = TENSE_ALBUM
        else:
            new_album = PARANOID_ALBUM
    else:
        new_album = PARANOID_ALBUM

    # Если состояние изменилось, переключаемся на новый альбом
    if new_album != current_album:
        current_album = new_album
        current_track_index = 0  # Начинаем с первой композиции в новом альбоме

    # Воспроизводим следующую композицию
    if current_track_index >= len(current_album):
        current_track_index = 0  # Если дошли до конца альбома, начинаем сначала

    track = current_album[current_track_index]
    pygame.mixer.music.load(track)
    pygame.mixer.music.play()
    print(f"Сейчас играет: {track}")
    # Увеличиваем индекс для следующей композиции
    current_track_index += 1

# Функция для управления музыкой в отдельном потоке
def music_thread_function():
    global music_thread_running

    while music_thread_running:
        if not pygame.mixer.music.get_busy():  # Если музыка не играет
            play_next_track()  # Воспроизводим следующую композицию
        time.sleep(10)  # Проверяем состояние каждую секунду

# Функция для получения карточки
def give_card(card_name):
    for card in CARDS:
        if card["name"] == card_name:
            if card_name in player_inventory:
                player_inventory[card_name] += 1
            else:
                player_inventory[card_name] = 1
            print(f"Вы получили карточку: {card['name']}!")
            print(f"Описание: {card['description']}")
            print(f"Теперь у вас {player_inventory[card_name]} таких карточек.")
            return
    print("Такой карточки не существует.")

# Функция для использования карточки
def use_card(card_name):
    global total_sanity, total_paranoia, total_time, task_activated, double_damage, no_restore

    if card_name in player_inventory and player_inventory[card_name] > 0:
        card = next(card for card in CARDS if card["name"] == card_name)
        if card["effect"] == "extend_day":
            print("Завтра день ВЕЛИКИХ СВЕРШЕНИЙ. Вы преодолете желание заснуть и окончите день в 24:00")
            day_extended = True
        elif card["effect"] == "remove_paranoia_effect":
            print("Свет БОЖЕСТВЕННОГО ПРОВИДЕНИЯ развеял мглу в вашем рассудке. Больше ни один предатель не сможет повести вас по ложному пути.") # Временно убираем влияние паранойи
            paranoia_effect_disabled = True
        elif card["effect"] == "restore_sanity":
            print("Вас поразило чувство абсолютной безмятежности. Неожидано страхи покинули вас, но... вдруг это все ПРОДЕЛКИ ВАШИХ ВРАГОВ?")
            total_sanity += 50
            if total_sanity > 100:
                total_sanity = 100
            total_paranoia += 10
            if total_paranoia > 100:
                total_paranoia = 100
        elif card["effect"] == "restore_paranoia":
            print("Вас поразило ужасное чувство - мозг будто поразило молнией. Однако уже через пару мгновений эффект прошел. Ваше сознание до сих пор потрясено, но вы точно чувствуете себя легче. ПЛАМЕННОЕ ОЧИЩЕНИЕ выжгло из вашего разума ложные мысли.")
            total_sanity -= 65
            if total_sanity < 0:
                print("\nТвоё психическое состояние достигло нуля. Ты проиграл!")
                return None  # Завершаем игру
            total_paranoia -= 35
            if total_paranoia < 0:
                total_paranoia = 0
        elif card["effect"] == "delete_task":
            print("Завтра у вас есть задание. Однако оно не должно быть выполнено. РАДИ ВЫСШЕЙ ЦЕЛИ вы потратите время на любые другие занятия.")
            task_activated = False
            for task in SPECIAL_TASKS:
                if task["active"]:
                    task["active"] == False
        elif card["effect"] == "restore_all_sanity":
            print("Лишь достойным будет дарована дорога в светлое будущее. Вы докажете БОЖЕСТВЕННОМУ ПРОВИДЕНИЮ свою силу и стойкость.")
            double_damage = True
        elif card["effect"] == "restore_all_paranoia":
            print("Чтобы освободиться от скверны, поглатившей разум, нужно пойти на некоторые... ЖЕРТВЫ.")
            no_restore = True

        player_inventory[card_name] -= 1
        if player_inventory[card_name] == 0:
            del player_inventory[card_name]
    else:
        print("У вас нет такой карточки или она уже использована.")

def can_use_card(card_name):
    return card_name in player_inventory and player_inventory[card_name] > 0

def show_cards():
    if player_inventory:
        print("\nВаши карточки:")
        for card_name, count in player_inventory.items():
            card = next(card for card in CARDS if card["name"] == card_name)
            print(f"- {card_name} (x{count}): {card['description']}")
    else:
        print("\nУ вас нет карточек.")

# Остановка музыки
def stop_music():
    pygame.mixer.music.stop()

# Шанс случайного события (10%)
EVENT_CHANCE = 0.1

# Прогрессия: множитель влияния на рассудок за выполнение/невыполнение задачи несколько дней подряд
PROGRESSION_MULTIPLIER = 1.2

par_agent = 0 # 0 - паранойи ещё не было 1 - был проведен гайд по паранойе

# Функция для форматирования времени в формате HH:MM
def format_time(minutes):
    hours = (8 + minutes // 60) % 24
    minutes = minutes % 60
    return f"{hours:02d}:{minutes:02d}"

def is_task_available(task, current_time):
    if task["time_window"] is None:
        return True
    start, end = task["time_window"]
    if start <= current_time < end:
        return True
    elif not(start <= current_time < end) and task["mandatory"] != True:
        return False
    else:
        print("Упс, кто-то не сделал обязательную задачу. Прийдеться начинать все сначала. Будь внимательней!")
        sys.exit()

#Функция для активации специальных заданий
def activate_special_tasks():
    for task in SPECIAL_TASKS:
        if not task["active"]:
            # Активируем задание с некоторой вероятностью (например, 20%)
            if random.random() < 0.2:
                task["active"] = True
                print(f"\nНовое специальное задание: {task['description']}")

# Функция для проверки выполнения специальных заданий
def check_special_tasks(completed_tasks, current_time):
    global total_sanity, total_paranoia, double_damage, no_restore
    for task in SPECIAL_TASKS:
        if task["active"]:
            if task["condition"] == "clean_room_3_days":
                # Проверяем, выполнена ли задача "Убраться в комнате"
                if any(t["description"] == "Убраться в комнате" for t in completed_tasks):
                    task["days_completed"] += 1
                else:
                    task["days_completed"] = 0  # Сбрасываем счетчик, если задача не выполнена

                # Если задание выполнено
                if task["days_completed"] >= task["days_required"]:
                    print(f"\nЗадание '{task['description']}' выполнено!")
                    if "sanity" in reward:
                        if not no_restore:
                            total_sanity += reward["sanity"]
                        print(f"Ты получил {reward['sanity']} единиц рассудка!")
                    task["active"] = False  # Деактивируем задание

            elif task["condition"] == "meet_friend_at_18":
                # Проверяем, выполнена ли задача "Позвонить другу" в 18:00
                if any(t["description"] == "Позвонить другу" for t in completed_tasks):
                    if current_time >= task["time_required"] - 30 and current_time <= task["time_required"] + 30:
                        print(f"\nЗадание '{task['description']}' выполнено!")
                        if "sanity" in reward:
                            if not no_restore:
                                total_sanity += reward["sanity"]
                            print(f"Ты получил {reward['sanity']} единиц рассудка!")
                        task["active"] = False  # Деактивируем задание

    # Проверяем, не истекли ли задания
    for task in SPECIAL_TASKS:
        if task["active"]:
            if task["condition"] == "clean_room_3_days":
                if task["days_completed"] < task["days_required"]:
                    print(f"\nЗадание '{task['description']}' не выполнено!")
                    if "sanity" in penalty:
                        if double_damage:
                            total_sanity += (penalty["sanity"] * 2)
                        else:
                            total_sanity += penalty["sanity"]
                        print(f"Ты потерял {abs(penalty['sanity'])} единиц рассудка!")
                    task["active"] = False  # Деактивируем задание
            elif task["condition"] == "meet_friend_at_18":
                if current_time > task["time_required"] + 30:
                    print(f"\nЗадание '{task['description']}' не выполнено!")
                    if "sanity" in penalty:
                        if double_damage:
                            total_sanity += (penalty["sanity"] * 2)
                        else:
                            total_sanity += penalty["sanity"]
                        print(f"Ты потерял {abs(penalty['sanity'])} единиц рассудка!")
                    task["active"] = False  # Деактивируем задание

# Функция для составления плана на день
def create_plan():
    global day_extended, max_day_time
    plan = []
    total_plan_time = 0  # Общее время выполнения плана

    while True:
        print("\nТекущий план:")
        if plan:
            for task in plan:
                print(f"- {task['description']} ({task['time']} минут)")
            print(f"Ориентировочное завершение плана: {format_time(total_plan_time)}")
        else:
            print("План пока пуст.")

        print("\nВыбери задачу из списка:")
        for i, task in enumerate(TASKS, 1):
            mandatory_mark = " (обязательная)" if task["mandatory"] else ""
            time_window_mark = ""
            if task["time_window"] is not None:
                start, end = task["time_window"]
                time_window_mark = f" [доступно с {format_time(start)} до {format_time(end)}]"
            print(f"{i}. {task['description']}{mandatory_mark}{time_window_mark} ({task['time']} минут, рассудок: {task['sanity']})")

        choice = input("Введи номер задачи, номера задач через пробел если вы хотите задать сразу несколько (или 'готово', чтобы закончить, или 'пересоздать', чтобы начать заново): ")

        if choice.lower() == 'готово':
            # Проверяем, все ли обязательные задачи добавлены
            mandatory_tasks = [task for task in TASKS if task["mandatory"]]
            missing_mandatory = [task for task in mandatory_tasks if task not in plan]
            if missing_mandatory:
                print("\nОшибка: Ты не добавил все обязательные задачи!")
                print("Необходимо добавить следующие задачи:")
                for task in missing_mandatory:
                    print(f"- {task['description']}")
                continue
            if not plan:
                print("Ты не добавил ни одной задачи. Пожалуйста, выбери хотя бы одну.")
                continue
            break
        elif choice.lower() == 'пересоздать':
            plan = []
            total_plan_time = 0
            print("План очищен. Начни заново.")
            continue

        try:
            choice1 = choice.split()
            for i in range(len(choice1)):
                choice = int(choice1[i]) - 1
                if 0 <= choice < len(TASKS):
                    selected_task = TASKS[choice]
                    # Проверяем, не превышает ли общее время лимит (720 минут = 12 часов)
                    if total_plan_time + selected_task["time"] > max_day_time:
                        print("Добавление этой задачи превысит лимит времени до 20:00. Выбери другую задачу.")
                    else:
                        plan.append(selected_task)
                        total_plan_time += selected_task["time"]
                else:
                    print("Пожалуйста, введи номер из списка.")
        except ValueError:
            print("Пожалуйста, введи число.")

    return plan


# Функция для моделирования случайного события
def random_event():
    # Выбираем событие с учётом индивидуальных шансов
    events = [event["description"] for event in EVENTS]
    chances = [event["chance"] for event in EVENTS]
    chosen_event = random.choices(EVENTS, weights=chances, k=1)[0]
    return chosen_event

def handle_event(event):
    global total_sanity, total_paranoia, total_time, par_agent, paranoia_effect_disabled, double_damage, no_restore

    print(f"\nСлучайное событие: {event['description']}")
    print("Выбери действие:")
    for i, option in enumerate(event["options"], 1):
        # Формируем строку с описанием влияния выбора
        effect_description = []
        if option["time_impact"] != 0:
            effect_description.append(f"время: {option['time_impact'] * (-1)} минут")
        if option["sanity_impact"] != 0:
            effect_description.append(f"рассудок: {option['sanity_impact']}")
        if option["paranoia_impact"] != 0:
            effect_description.append(f"паранойя: {option['paranoia_impact']}")

        # Выводим вариант действия и его влияние
        print(f"{i}. {option['description']} ({', '.join(effect_description)})")

    choice = input("Введи номер действия: ")
    try:
        choice = int(choice) - 1
    except ValueError:
        print("Из-за вышей ошибки выбран первый вариант действия")
        choice = 0
    if 0 <= choice < len(event["options"]):
        selected_option = event["options"][choice]
    else:
        print("Из-за вышей ошибки выбран первый вариант действия")
        selected_option = event["options"][0]
        # Влияние на время
        total_time += selected_option["time_impact"]
    if total_time > (960 if day_extended else 720):
        total_time = (960 if day_extended else 720)
    # Влияние на рассудок
    sanity_impact = selected_option["sanity_impact"]
    if not paranoia_effect_disabled:  # Если эффект паранойи не отключен
        if sanity_impact < 0:  # Урон
            if double_damage:
                sanity_impact *= (1 + total_paranoia / 100) * 2
            sanity_impact *= (1 + total_paranoia / 100)
        elif not no_restore:  # Восстановление
            sanity_impact *= (1 - total_paranoia / 100)
    total_sanity += sanity_impact
    if total_sanity > 100:
        total_sanity = 100
    elif total_sanity <= 0:
        print("\nТвоё психическое состояние достигло нуля. Ты проиграл!")
        return None  # Завершаем игру
    # Влияние на паранойю
    total_paranoia += selected_option["paranoia_impact"]
    if total_paranoia < 0:
        total_paranoia = 0
    if total_paranoia > 100:
        total_paranoia = 100

    if total_paranoia > 0 and par_agent == 0:
        par_agent = 1
        print("\nВижу у кого-то сдают нервы? Нет, это был не я. Честно.")
        time.sleep(2.5)
        print("\nДумаю пришло время объяснить что все это значит...")
        time.sleep(2.5)
        print("\nСейчас твое состояние более менее стабильно, но чем выше будет расти паранойя... Ох, последствий будет много")
        time.sleep(2.5)
        print("\nВо-первых, урон твоему ментальному состоянию будет увеличиваться, а восстановление наоборот - уменьшаться.")
        time.sleep(2.5)
        print("\nВо-вторых, тебе все больше и больше будет... Казаться то, чего на самом деле нет (хотя не все странности, что ты видишь - игра твоего сознания)")
        time.sleep(2.5)
        print("\nА, ну и как только паранойя дойдет до максимума, поглатив твоё сознание... В общем узнаешь, не буду раскрывать все карты.")

    print(f"Твоё психическое состояние: {total_sanity}/100")
    print(f"Твой уровень паранойи: {total_paranoia}/100")


# Функция для выполнения задачи пошагово
def execute_task(task):
    global total_sanity, total_paranoia, task_progres, total_time, par_agent, paranoia_effect_disabled, no_restore, double_damage

    if not is_task_available(task, total_time):
        print(f"Задача '{task['description']}' недоступна в текущее время.")
        return "unavailable"

    time_spent = 0  # Время, потраченное на задачу
    print(f"\nТекущая задача: {task['description']} ({task['time'] - time_spent} минут осталось)")
    choice = input("Что будешь делать? (1 - Потратить 10 минут на задачу, 2 - Пропустить задачу): ")

    if choice == '1':
        # Тратим 10 минут на задачу
        time_spent += 10
        total_time += 10
        print(
            f"Ты потратил 10 минут на задачу '{task['description']}'.")
        print(f"Сейчас время: {format_time(total_time)}.")
    elif choice == '2':
        if task["mandatory"]:
            print("Эту задачу нельзя пропустить, так как она обязательная.")
        else:
            # Пропуск задачи сильно снижает рассудок
            sanity_loss = 30 * (1 + total_paranoia / 100)  # Штраф увеличивается с уровнем паранойи
            total_sanity -= sanity_loss
            if total_sanity <= 0:
                print("\nТвоё психическое состояние достигло нуля. Ты проиграл!")
                return None  # Завершаем игру
            print(f"Ты пропустил задачу '{task['description']}'. Ты потерял {sanity_loss:.1f} рассудка.")
            return "skipped"  # Задача пропущена
    else:
        print("Пожалуйста, выбери 1 или 2.")

    while time_spent < task["time"]:
        print(f"\nТекущая задача: {task['description']} ({task['time'] - time_spent} минут осталось)")

        # Проверяем, произошло ли случайное событие
        if random.random() < EVENT_CHANCE:
            possible_events = [event for event in EVENTS if event["location"] == task["location"]]
            event = random_event()
            handle_event(event)

            # Влияние события на задачи
            ##if event["task_impact"] == "add":
            ##    new_task = {"description": event["task"], "time": event["time"]}
            ##      remaining_tasks.append(new_task)
            ##      print(f"Добавлена новая задача: {new_task['description']} ({new_task['time']} минут).")
            ##  elif event["task_impact"] == "remove":
            ##      if remaining_tasks:
            ##          removed_task = remaining_tasks.pop(0)
            ##          print(f"Задача '{removed_task['description']}' удалена из списка.")

            # Тратим 10 мину
            # После события предлагаем игроку выбор
            choice = input("Что будешь делать? (1 - Потратить 10 минут на задачу, 2 - Пропустить задачу): ")

            if choice == '1':
                # Тратим 10 минут на задачу
                time_spent += 10
                total_time += 10
                print(
                    f"Ты потратил 10 минут на задачу '{task['description']}'.")
                print(f"Сейчас время: {format_time(total_time)}.")
            elif choice == '2':
                if task["mandatory"]:
                    print("Эту задачу нельзя пропустить, так как она обязательная.")
                else:
                    # Пропуск задачи сильно снижает рассудок
                    sanity_loss = 30 * (1 + total_paranoia / 100)  # Штраф увеличивается с уровнем паранойи
                    total_sanity -= sanity_loss
                    if total_sanity <= 0:
                        print("\nТвоё психическое состояние достигло нуля. Ты проиграл!")
                        return None  # Завершаем игру
                    print(f"Ты пропустил задачу '{task['description']}'. Ты потерял {sanity_loss:.1f} рассудка.")
                    return "skipped"  # Задача пропущена
            else:
                print("Пожалуйста, выбери 1 или 2.")
        else:
            # Если случайное событие не произошло, автоматически тратим 10 минут
            time_spent += 10
            total_time += 10
            print(f"Ты потратил 10 минут на задачу '{task['description']}'.")
            time.sleep(1)

    # Задача выполнена (один подход)
    task["current_steps"] += 1
    if task["required_steps"] == 1:
        print(f"Задача '{task['description']}' завершена!")
    else:
        print(f"Ты выполнил один подход задачи '{task['description']}'. Прогресс: {task['current_steps']}/{task['required_steps']}.")
    # Если задача завершена (все подходы выполнены)
    if task["current_steps"] >= task["required_steps"]:
        task["current_steps"] == 0
    return "completed"

# Функция для выполнения плана
def execute_plan(plan):
    global total_sanity, task_progress, total_paranoia, total_time, paranoia_effect_disabled, max_day_time, double_damage, no_restore

    total_time = 0  # Начинаем с 8:00 утра (0 минут с начала дня)
    completed_tasks = []
    remaining_tasks = plan.copy()  # Копируем план, чтобы не изменять оригинал

    print(f"\nСейчас время: {format_time(total_time)}. День начинается!")

    while remaining_tasks and total_time < max_day_time:  # 720 минут = 12 часов (8:00 - 20:00)
        task = remaining_tasks[0]
        result = execute_task(task)

        if result is None:  # Игра завершена из-за нулевого психического состояния
            return None, None, None

        if result == "completed":
            # Обновляем прогрессию и влияние на рассудок
            if task["description"] in task_progress:
                if task_progress[task["description"]] >= 0:
                    task_progress[task["description"]] += 1
                else:
                    task_progress[task["description"]] = 1  # Сбрасываем прогрессию, если задача была пропущена ранее
            else:
                task_progress[task["description"]] = 1

            # Влияние задачи на рассудок с учётом прогрессии и паранойи
            sanity_impact = task["sanity"]
            # Учитываем паранойю: урон увеличивается, восстановление уменьшается
            if not paranoia_effect_disabled:  # Если эффект паранойи не отключен
                if sanity_impact < 0:  # Урон
                    if double_damage:
                        sanity_impact *= (1 + total_paranoia / 100)
                    else:
                        sanity_impact *= (1 + total_paranoia / 100)
                elif not no_restore:  # Восстановление
                    sanity_impact *= (1 - total_paranoia / 100)
                else:
                    sanity_impact = 0
            total_sanity += sanity_impact
            if total_sanity > 100:
                total_sanity = 100
            elif total_sanity <= 0:
                print("\nТвоё психическое состояние достигло нуля. Ты проиграл!")
                return None, None, None  # Завершаем игру

            print(f"Твоё психическое состояние: {total_sanity}/100")
            print(f"Твой уровень паранойи: {total_paranoia}/100")

            # Задача выполнена, добавляем её в список выполненных
            completed_tasks.append(task)
            remaining_tasks.pop(0)
        elif result == "skipped":
            # Задача пропущена, удаляем её из списка
            remaining_tasks.pop(0)
        elif result == "unavailable":
            # Задача недоступна, пропускаем её
            remaining_tasks.pop(0)

        print(f"Сейчас время: {format_time(total_time)}.")

    return completed_tasks, remaining_tasks, total_time

# Функция для подсчёта очков рассудка в конце дня
def calculate_sanity(completed_tasks, remaining_tasks):
    global total_sanity, task_progress, paranoia_effect_disabled

    # Начисляем очки за выполненные задачи
    sanity_gain = 0
    for task in completed_tasks:
        if task["description"] in task_progress:
            progress = task_progress[task["description"]]
        else:
            progress = 1
        sanity_gain = 5 * (PROGRESSION_MULTIPLIER ** (progress - 1))
        if not paranoia_effect_disabled:
            sanity_gain *= (1 - total_paranoia / 100)
        print(f"За выполнение задачи '{task['description']}' ты получил {sanity_gain:.1f} рассудка.")
        total_sanity += sanity_gain

    # Вычитаем очки за пропущенные задачи
    sanity_loss = 0
    for task in remaining_tasks:
        if task["description"] in task_progress:
            progress = abs(task_progress[task["description"]])
        else:
            progress = 1
        sanity_loss = 20 * (PROGRESSION_MULTIPLIER ** (progress - 1))
        if not paranoia_effect_disabled:
            sanity_loss *= (1 + total_paranoia / 100)
        print(f"За пропуск задачи '{task['description']}' ты потерял {sanity_loss:.1f} рассудка.")
        total_sanity -= sanity_loss

    # Ограничиваем рассудок в пределах 0-100
    if total_sanity > 100:
        total_sanity = 100
    elif total_sanity <= 0:
        print("\nТвоё психическое состояние достигло нуля. Ты проиграл!")
        return None

# Основная функция игры
def main(days):
    global total_sanity, total_paranoia, paranoia_effect_disabled, day_extended, music_thread_running, task_activated, no_restore, double_damage

    play_next_track()

    music_thread = threading.Thread(target=music_thread_function)
    music_thread.daemon = True  # Поток завершится вместе с основной программой
    music_thread.start()

    print("Добро пожаловать в игру!")
    while True:
        if days == 0:
            print("\nПросыпайся.")
            time.sleep(1.5)
            print("\nЭй, ты меня слышишь?")
            time.sleep(1.5)
            print("\n... Не говори, что ты опять все забыл...")
            time.sleep(1.5)
            print("\nОх... Хорошо. Это не первый и, видимо, не последний раз. Ты даже не помнишь свой прошлый план?")
            time.sleep(1.5)
            print("\nКакая жалость, видимо придеться составить его заново. Давай быстрее - у нас мало времени.")
        plan = create_plan()
        if days == 0:
            print("\nКажется не очень сложным, не так ли?")
            time.sleep(1.5)
            print("\nНа самом деле все не так просто... Сейчас нет времени, так что  я все объясню вечером")
        print("\nТвой план на день:")
        for task in plan:
            print(f"- {task['description']} ({task['time']} минут)")
        print(f"Ориентировочное завершение плана: {format_time(sum(task['time'] for task in plan))}")

        input("\nНажми Enter, чтобы начать день...")

        completed_tasks, remaining_tasks, total_time = execute_plan(plan)

        if completed_tasks is None:  # Игра завершена из-за нулевого психического состояния
            break

        calculate_sanity(completed_tasks, remaining_tasks)

        os.system('cls' if os.name == 'nt' else 'clear')

        # Проверяем выполнение специальных заданий
        check_special_tasks(completed_tasks, total_time)

        # Активируем специальные задания
        if not task_activated:
            activate_special_tasks()
            task_activated = True

        # Показываем доступные карточки
        if days > 5:
            show_cards()
            # Предложение использовать карточку
            if player_inventory:
                use_card_input = input("Хотите использовать карточку? (да/нет): ")
                if use_card_input.lower() == "да":
                    card_name = input("Введите название карточки: ")
                    if can_use_card(card_name):
                        use_card(card_name)
                    else:
                        print("У вас нет такой карточки или она уже использована.")

        if no_restore:
            no_restore = False
            total_sanity += 30
            total_paranoia -= 75
            print("Великое опустошение закончилось. Жизнь заиграла новыми красками, а паранойя отступила.")
            if total_sanity > 100:
                total_sanity = 100
            if total_paranoia < 0:
                total_paranoia = 0

        if double_damage:
            double_damage = False
            total_sanity += 100
            total_paranoia -= 15
            print("Великое испытание окончено - вы доказали свою стойкость. Самое время наслаждаться наградой")
            if total_sanity > 100:
                total_sanity = 100
            if total_paranoia < 0:
                total_paranoia = 0

        print("\nИтог дня:")
        print(f"Выполнено задач: {len(completed_tasks)}")
        ##total_sanity += 5 * len(completed_tasks)
        print("Выполненные задачи:")
        for task in completed_tasks:
            print(f"- {task['description']} ({task['time']} минут)")

        if remaining_tasks:
            print("\nНевыполненные задачи:")
      ##    total_sanity -= 20 * len(remaining_tasks)
            for task in remaining_tasks:
                print(f"- {task['description']} ({task['time']} минут)")
        else:
            print("\nВсе задачи выполнены!")

        day_extended = False
        paranoia_effect_disabled = False

        if days == 0:
            print(
                '\nЯ вижу ты выполнил план. Время рассказать самое интересное. Как ты успел заметить, каждая задача по своему влияет на твое ментальное состояние.')
            time.sleep(2.5)
            print(
                '\nОднако все на так просто. В зависимости от того, каким образом ты составил план и сколько задач было тобой сделанно в сумме, твое ментальное состояние изменится еще больше.')
            time.sleep(2.5)
            if remaining_tasks:
                print(
                    '\nКак видишь - ты сделал не все задачи. Каждая невыполненная задача очень сильно отражается на твоем ментальном состоянии.')
                time.sleep(2.5)
                print(
                    '\nТы наверное уже подумал о том, чтобы вообще не добавлять некоторые задачи в план, чтобы не грустить от их невыполнения. да? Сейчас объясню чуть подробнее.')
            else:
                print(
                    '\nКак видишь - ты сделал все задачи. Каждая выполненная задача отражается на твоем ментальном состоянии. Сейчас я расскажу все чуть подробнее.')

            time.sleep(2.5)
            print(
                '\nДело в том, что общая тенденция выполнения или невыполнения задач влияет на тебя куда больше, чем разовое выполнение или невыполнение заданий.')
            time.sleep(2.5)
            print(
                '\nК примеру ты каждый день делаешь уборку в комнате. Сама по себе уборка тебе не очень нравится, но сам факт того, что ты из раза в раз не изменяешь своему плану делает тебя счастливее.')
            time.sleep(2.5)
            print(
                '\nОднако есть и обратная сторона медали. Чем больше ты развлекаешься одним и тем же образом (только читаешь книги или только играешь на ПК), тем меньше это тебе приносит удовольствия.')
            time.sleep(2.5)
            print(
                '\nЕщё не стоит забывать, что у тебя будут не только желательные, но и обязательные задачи. Такие задания, вроде обучения, нельзя пропустить ни при каких обстоятельствах (почти)')
            time.sleep(2.5)
            print(
                '\nКак только ты опять что-то забудешь, я приду на помощь! Но на самом деле я с тобой не прощаюсь. Ещё бы - я же просто голос в твоей голове, как я могу попращаться с тобой?')

        print(f"\nСейчас время: {format_time(total_time)}. День закончен!")
        print(f"Твоё психическое состояние: {total_sanity}/100")
        print(f"Твой уровень паранойи: {total_paranoia}/100")
        input("\nНажми Enter, чтобы продолжить...")
        os.system('cls' if os.name == 'nt' else 'clear')  # Очищаем консоль перед началом следующего дня
        days += 1

if __name__ == "__main__":
    days = 0
    random.shuffle(CALM_ALBUM)
    random.shuffle(TENSE_ALBUM)
    random.shuffle(PARANOID_ALBUM)
    main(days)