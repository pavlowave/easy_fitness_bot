from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from tgbot.handlers.onboarding.manage_data import *

def make_keyboard_for_start_command() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton('Справочник', callback_data=f'{DIRECTORY_BUTTON}')],
        [InlineKeyboardButton('Мой профиль', callback_data=f'{MY_PROFILE_BUTTON}')],
        [InlineKeyboardButton('Норма калорий', callback_data=f'{CALCULATION_CALORIES}')],
        [InlineKeyboardButton('Помощь', callback_data=f'{HELP_BUTTON}')]
    ]

    return InlineKeyboardMarkup(buttons)


def make_keyboard_for_directory() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton('Упражнения', callback_data=f'{EXERCISES_BUTTON}')],
        [InlineKeyboardButton('Спортивное питание', callback_data=f'{SPORTS_NUTRITION_BUTTON}')],
        [InlineKeyboardButton('Состав и таблица ккал продуктов', callback_data=f'{COMPOSITION_BUTTON}')],
        [InlineKeyboardButton('Энциклопедия', callback_data=f'{ENCYCLOPEDIA_BUTTON}')],
        [InlineKeyboardButton("Вернуться в начало", callback_data=BACK_BUTTON)],
    ]

    return InlineKeyboardMarkup(buttons)


def make_keyboard_for_get_help() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton('Обратиться в поддержку', callback_data=f'{HELP_TEXT_BUTTON}'),
         InlineKeyboardButton('Про наш VPN', callback_data=f'11')],
        [InlineKeyboardButton('Инструкции', callback_data=f'11'),
         InlineKeyboardButton('Документы', callback_data=f'11')],
        [InlineKeyboardButton("Вернуться в начало", callback_data=BACK_BUTTON)],
    ]

    return InlineKeyboardMarkup(buttons)



def make_keyboard_for_get_gender() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton('Мужчина', callback_data=f'{MAN_BUTTON}'),
         InlineKeyboardButton('Женщина', callback_data=f'{WOMAN_BUTTON}')],
        [InlineKeyboardButton("Вернуться в начало", callback_data=BACK_BUTTON)],
    ]

    return InlineKeyboardMarkup(buttons)

# У пользователя нет ни email, ни подписки.
def make_keyboard_for_action_d_have_em_and_d_have_s() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton('Оформить подписку', callback_data=f'Оформить подписку')],
        [InlineKeyboardButton('Привязать email', callback_data=f'{EMAIL_BUTTON}')],
        [InlineKeyboardButton('Пригласить друга', callback_data='Пригласить друга')],
        [InlineKeyboardButton('Замеры', callback_data=f'{MEASUREMENTS_BUTTON}')],
        [InlineKeyboardButton('Вернуться в начало', callback_data=BACK_BUTTON)],
    ]
    return InlineKeyboardMarkup(keyboard)

# У пользователя есть и email, и подписка.
def make_keyboard_for_action_have_em_and_s() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton('Продлить подписку', callback_data=f'11'),
        InlineKeyboardButton('Изменить email', callback_data=f'{EMAIL_BUTTON}')],
        [InlineKeyboardButton('Пригласить друга', callback_data='invite_friend_action')],
        [InlineKeyboardButton('Вернуться в начало', callback_data=BACK_BUTTON)],
    ]
    return InlineKeyboardMarkup(keyboard)

#У пользователя есть email, но нет подписки.
def make_keyboard_for_action_have_em_and_d_have_s() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton('Оформить подписку', callback_data=f'11'),
        InlineKeyboardButton('Изменить email', callback_data=f'{EMAIL_BUTTON}')],
        [InlineKeyboardButton('Пригласить друга', callback_data='invite_friend_action')],
        [InlineKeyboardButton('Вернуться в начало', callback_data=BACK_BUTTON)],
    ]
    return InlineKeyboardMarkup(keyboard)

# У пользователя есть подписка, но нет email.
def make_keyboard_for_action_d_have_em_and_have_s() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton('Продлить подписку', callback_data=f'11'),
        InlineKeyboardButton('Привязать email', callback_data=f'{EMAIL_BUTTON}')],
        [InlineKeyboardButton('Пригласить друга', callback_data='invite_friend_action')],
        [InlineKeyboardButton('Вернуться в начало', callback_data=BACK_BUTTON)],
    ]
    return InlineKeyboardMarkup(keyboard)


def make_keyboard_for_pay(subscription_price: int) -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(f'Мне не нужен чек, перейти к оплате {subscription_price} ₽', callback_data='payment_without_receipt')],
        [InlineKeyboardButton(f'Мне нужен чек', callback_data='payment_with_receipt')],
        [InlineKeyboardButton('Вернуться в начало', callback_data=BACK_BUTTON)],
    ]
    return InlineKeyboardMarkup(keyboard)


def make_keyboard_for_exercises() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(f'Грудь', callback_data=f'{ACTIVITY_COEFFICIENT_12_BUTTON}')],
        [InlineKeyboardButton(f'Спина', callback_data=f'{ACTIVITY_COEFFICIENT_13_BUTTON}')],
        [InlineKeyboardButton(f'Ноги', callback_data=f'{ACTIVITY_COEFFICIENT_15_BUTTON}')],
        [InlineKeyboardButton(f'Ягодичные', callback_data=f'{ACTIVITY_COEFFICIENT_17_BUTTON}')],
        [InlineKeyboardButton(f'Дельты', callback_data=f'{ACTIVITY_COEFFICIENT_19_BUTTON}')],
        [InlineKeyboardButton(f'Руки Бицепс', callback_data=f'{ACTIVITY_COEFFICIENT_19_BUTTON}')],
        [InlineKeyboardButton(f'Руки Трицепс', callback_data=f'{ACTIVITY_COEFFICIENT_19_BUTTON}')],
        [InlineKeyboardButton(f'Предплечье', callback_data=f'{ACTIVITY_COEFFICIENT_19_BUTTON}')],
        [InlineKeyboardButton(f'Пресс', callback_data=f'{ACTIVITY_COEFFICIENT_19_BUTTON}')],
        [InlineKeyboardButton(f'Функциональные упражнения', callback_data=f'{ACTIVITY_COEFFICIENT_19_BUTTON}')],
        [InlineKeyboardButton(f'Кардио', callback_data=f'{ACTIVITY_COEFFICIENT_19_BUTTON}')],
        [InlineKeyboardButton(f'Растяжка', callback_data=f'{ACTIVITY_COEFFICIENT_19_BUTTON}')],
        [InlineKeyboardButton('Вернуться в начало', callback_data=BACK_BUTTON)],
    ]
    return InlineKeyboardMarkup(keyboard)


def make_keyboard_for_nutrition() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(f'Протеин', callback_data=f'{ACTIVITY_COEFFICIENT_12_BUTTON}')],
        [InlineKeyboardButton(f'Гейнер', callback_data=f'{ACTIVITY_COEFFICIENT_13_BUTTON}')],
        [InlineKeyboardButton(f'Креатин', callback_data=f'{ACTIVITY_COEFFICIENT_15_BUTTON}')],
        [InlineKeyboardButton(f'Аминокислоты', callback_data=f'{ACTIVITY_COEFFICIENT_17_BUTTON}')],
        [InlineKeyboardButton(f'L-карнитин', callback_data=f'{ACTIVITY_COEFFICIENT_19_BUTTON}')],
        [InlineKeyboardButton(f'Витамины и минералы', callback_data=f'{ACTIVITY_COEFFICIENT_19_BUTTON}')],
        [InlineKeyboardButton(f'Средства для суставов и связок', callback_data=f'{ACTIVITY_COEFFICIENT_19_BUTTON}')],
        [InlineKeyboardButton('Вернуться в начало', callback_data=BACK_BUTTON)],
    ]
    return InlineKeyboardMarkup(keyboard)


def activity_coefficient() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(f'Малоподвижный (тренировок мало или они отсутствуют)',
                              callback_data=f'{ACTIVITY_COEFFICIENT_12_BUTTON}')],
        [InlineKeyboardButton(f'Низкая активность (легкие тренировки 1-3 раза в неделю)',
                              callback_data=f'{ACTIVITY_COEFFICIENT_13_BUTTON}')],
        [InlineKeyboardButton(
            f'Умеренная активность (работа средней тяжести либо тренировки умеренной интенсивности 3-5 дней в неделю)',
            callback_data=f'{ACTIVITY_COEFFICIENT_15_BUTTON}')],
        [InlineKeyboardButton(
            f'Высокая активность (физическая работа плюс тренировки либо интенсивные тренировки 6-7 раз в неделю))',
            callback_data=f'{ACTIVITY_COEFFICIENT_17_BUTTON}')],
        [InlineKeyboardButton(
            f'Предельная активность (физическая работа плюс очень интенсивные тренировки/занятия спортом).',
            callback_data=f'{ACTIVITY_COEFFICIENT_19_BUTTON}')],
        [InlineKeyboardButton('Вернуться в начало', callback_data=BACK_BUTTON)],
    ]
    return InlineKeyboardMarkup(keyboard)