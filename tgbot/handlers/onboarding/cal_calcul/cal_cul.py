import asyncio
import logging
import re
from asgiref.sync import sync_to_async
from django.db.models import QuerySet
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, CallbackContext

from tgbot.handlers.onboarding.keyboards import *
from tgbot.handlers.utils.info import extract_user_data_from_update
from users.models import User
from tgbot.handlers.onboarding.manage_data import *

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Определение состояний
(AWAITING_WEIGHT, AWAITING_HEIGHT,
    AWAITING_AGE, AWAITING_ACTIVITY_COEFFICIENT) = range(4)

async def calorie_calculation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    data = query.data
    user_id = extract_user_data_from_update(update)['user_id']
    message = update.callback_query.message

    if data in [MAN_BUTTON, WOMAN_BUTTON]:
        if data == MAN_BUTTON:
            context.user_data['gender'] = 'male'
        else:
            context.user_data['gender'] = 'female'

        # Задержка перед удалением старого сообщения
        await asyncio.sleep(0.4)
        # Удаление старого сообщения
        await context.bot.delete_message(
            chat_id=user_id,
            message_id=message.message_id
        )

        # Задержка перед отправкой нового сообщения
        await asyncio.sleep(0.4)

        # Отправка нового сообщения
        text = 'Введите вес в кг, на который Вы хотите посчитать калорийность:'
        new_message = await context.bot.send_message(
            chat_id=user_id,
            text=text,
            parse_mode=ParseMode.HTML,
        )

        # Обновление состояния пользователя
        context.user_data['current_state'] = AWAITING_WEIGHT


async def handle_user_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global true_weight, true_height, true_age, basal_metabolism
    user_id = extract_user_data_from_update(update)['user_id']
    user_text = update.message.text.title()
    gender = context.user_data.get('gender')
    current_state = context.user_data.get('current_state')

    # Сохранение идентификатора старого сообщения
    old_message_id = context.user_data.get('current_message_id')

    if old_message_id:
        # Удаление старого сообщения
        await asyncio.sleep(0.4)
        try:
            await context.bot.delete_message(
                chat_id=user_id,
                message_id=old_message_id
            )
        except Exception as e:
            logging.error(f"Failed to delete message: {e}")

    if current_state == AWAITING_WEIGHT:
        if not user_text.isdigit():
            new_message = await context.bot.send_message(
                text='Введенный текст не содержит цифры. Пожалуйста, введите Ваш вес в цифрах:',
                chat_id=user_id,
                parse_mode=ParseMode.HTML,
            )
            context.user_data['current_message_id'] = new_message.message_id
            context.user_data['current_state'] = AWAITING_WEIGHT
            return

        weight = int(user_text)

        if weight > 250:
            new_message = await context.bot.send_message(
                text='Введен некорректный вес. Пожалуйста, введите значение до 250 кг:',
                chat_id=user_id,
                parse_mode=ParseMode.HTML,
            )
            context.user_data['current_message_id'] = new_message.message_id
            context.user_data['current_state'] = AWAITING_WEIGHT
            return
        elif weight <= 5:
            new_message = await context.bot.send_message(
                text='Введен некорректный вес. Пожалуйста, введите значение более 5 кг:',
                chat_id=user_id,
                parse_mode=ParseMode.HTML,
            )
            context.user_data['current_message_id'] = new_message.message_id
            context.user_data['current_state'] = AWAITING_WEIGHT
            return

        true_weight = weight
        new_message = await context.bot.send_message(
            text='Введите ваш рост в сантиметрах:',
            chat_id=user_id,
            parse_mode=ParseMode.HTML,
        )
        context.user_data['current_message_id'] = new_message.message_id
        context.user_data['current_state'] = AWAITING_HEIGHT

    elif current_state == AWAITING_HEIGHT:
        if not user_text.isdigit():
            new_message = await context.bot.send_message(
                text='Введенный текст не содержит цифры. Пожалуйста, введите Ваш рост в цифрах:',
                chat_id=user_id,
                parse_mode=ParseMode.HTML,
            )
            context.user_data['current_message_id'] = new_message.message_id
            context.user_data['current_state'] = AWAITING_HEIGHT
            return

        height = int(user_text)
        if height > 300:
            new_message = await context.bot.send_message(
                text='Введен некорректный рост. Пожалуйста, введите корректные данные:',
                chat_id=user_id,
                parse_mode=ParseMode.HTML,
            )
            context.user_data['current_message_id'] = new_message.message_id
            context.user_data['current_state'] = AWAITING_HEIGHT
            return
        elif height <= 30:
            new_message = await context.bot.send_message(
                text='Введен некорректный рост. Пожалуйста, введите значение более 30 см:',
                chat_id=user_id,
                parse_mode=ParseMode.HTML,
            )
            context.user_data['current_message_id'] = new_message.message_id
            context.user_data['current_state'] = AWAITING_HEIGHT
            return

        true_height = height
        new_message = await context.bot.send_message(
            text='Введите ваш возраст:',
            chat_id=user_id,
            parse_mode=ParseMode.HTML,
        )
        context.user_data['current_message_id'] = new_message.message_id
        context.user_data['current_state'] = AWAITING_AGE

    elif current_state == AWAITING_AGE:
        if not user_text.isdigit():
            new_message = await context.bot.send_message(
                text='Введенный текст не содержит цифры. Пожалуйста, введите Ваш возраст в цифрах:',
                chat_id=user_id,
                parse_mode=ParseMode.HTML,
            )
            context.user_data['current_message_id'] = new_message.message_id
            context.user_data['current_state'] = AWAITING_AGE
            return

        age = int(user_text)
        if age > 120:
            new_message = await context.bot.send_message(
                text='Введен некорректный возраст. Пожалуйста, введите корректные данные:',
                chat_id=user_id,
                parse_mode=ParseMode.HTML,
            )
            context.user_data['current_message_id'] = new_message.message_id
            context.user_data['current_state'] = AWAITING_AGE
            return
        elif age <= 1:
            new_message = await context.bot.send_message(
                text='Введен некорректный возраст. Пожалуйста, введите значение более 1 года:',
                chat_id=user_id,
                parse_mode=ParseMode.HTML,
            )
            context.user_data['current_message_id'] = new_message.message_id
            context.user_data['current_state'] = AWAITING_AGE
            return

        true_age = age
        if gender == 'male':
            basal_metabolism = int(10 * true_weight) + (6.25 * true_height) - (5 * true_age) + 5
        elif gender == 'female':
            basal_metabolism = int(10 * true_weight) + (6.25 * true_height) - (5 * true_age) - 161

        new_message = await context.bot.send_message(
            text=(f'Ваш основной обмен ≈ {basal_metabolism} ккал\n'
                  f'Теперь выберите уровень вашей физической активности:'),
            chat_id=user_id,
            parse_mode=ParseMode.HTML,
            reply_markup=activity_coefficient()
        )
        context.user_data['current_message_id'] = new_message.message_id
        context.user_data['current_state'] = AWAITING_ACTIVITY_COEFFICIENT


async def pick_coeff(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    query.answer()
    data = query.data
    print(basal_metabolism)
    if context.user_data.get('current_state') == AWAITING_ACTIVITY_COEFFICIENT:
        coefficients = {
            ACTIVITY_COEFFICIENT_12_BUTTON: 1.2,
            ACTIVITY_COEFFICIENT_13_BUTTON: 1.375,
            ACTIVITY_COEFFICIENT_15_BUTTON: 1.55,
            ACTIVITY_COEFFICIENT_17_BUTTON: 1.725,
            ACTIVITY_COEFFICIENT_19_BUTTON: 1.9
        }
        coefficient = coefficients.get(data)  # Получаем соответствующий коэффициент из словаря
        if coefficient is not None:
            calorie_intake = coefficient * basal_metabolism
            calorie_intake = int(calorie_intake)
            user_id = extract_user_data_from_update(update)['user_id']
            await context.bot.send_message(
                text=(
                    f'Рекомендуемая калорийность рациона: {calorie_intake} ккал.\n'
                    f'Полученные цифры позволяют рассчитать необходимую калорийность рациона:\n'
                    f'- для поддержания массы тела поступление калорий должно равняться рассчитанным затратам;\n'
                    f'- для снижения веса за счет жира необходим дефицит примерно в 500 ккал/день;\n'
                    f'- в периоды роста и развития (дети, беременные женщины) необходим профицит калорий.\n'
                    f'Остальным людям следует осторожно относиться к профициту.\n'
                    f'Если нужно увеличить мышечную массу или набрать недостающий вес, '
                    f'излишек энергии должен составлять 200 ккал/день. В противном случае возможно образование жировых отложений.\n'
                    f'Важно понимать, что ни формулы, ни другие методы оценки энергозатрат (биоимпедансный анализ, фитнес-трекеры ит.д.)'
                    f' не дают абсолютно точных результатов, поэтому любые расчеты требуют практической проверки:\n'
                    f'10-14 дней нужно потреблять рассчитанное количество калорий и после этого оценить изменение массы тела.\n'
                    f'Если масса стабильна, рацион сбалансирован по энергии.\n'
                    f'Если она уменьшается — имеется дефицит калорий, если растет — профицит.'
                ),
                chat_id=user_id,
                parse_mode=ParseMode.HTML,
                reply_markup=make_keyboard_for_start_command(),
            )
        else:
            pass