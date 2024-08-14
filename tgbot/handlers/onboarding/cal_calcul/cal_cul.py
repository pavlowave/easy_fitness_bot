import asyncio
import logging
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from tgbot.handlers.onboarding.keyboards import *
from tgbot.handlers.utils.info import extract_user_data_from_update
from tgbot.handlers.onboarding.manage_data import *

from tgbot.handlers.onboarding.keyboards import make_keyboard_for_start_command

from tgbot.handlers.onboarding.keyboards import activity_coefficient
from tgbot.handlers.onboarding.manage_data import WOMAN_BUTTON, MAN_BUTTON, ACTIVITY_COEFFICIENT_12_BUTTON, \
    ACTIVITY_COEFFICIENT_13_BUTTON, ACTIVITY_COEFFICIENT_15_BUTTON, ACTIVITY_COEFFICIENT_17_BUTTON, \
    ACTIVITY_COEFFICIENT_19_BUTTON

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
    user_id = extract_user_data_from_update(update)['user_id']
    current_state = context.user_data.get('current_state')

    if query:
        data = query.data
        if data in [MAN_BUTTON, WOMAN_BUTTON]:
            context.user_data['gender'] = 'male' if data == MAN_BUTTON else 'female'

            await asyncio.sleep(0.4)
            await query.message.delete()

            await asyncio.sleep(0.4)
            new_message = await context.bot.send_message(
                chat_id=user_id,
                text='Введите вес в кг, на который Вы хотите посчитать калорийность:',
                parse_mode=ParseMode.HTML,
            )
            context.user_data['current_state'] = AWAITING_WEIGHT
            context.user_data['current_message_id'] = new_message.message_id
            return

    if update.message:
        user_text = update.message.text.title()
        old_message_id = context.user_data.get('current_message_id')

        if old_message_id:
            await asyncio.sleep(0.4)
            try:
                await context.bot.delete_message(chat_id=user_id, message_id=old_message_id)
            except Exception as e:
                logging.error(f"Failed to delete message: {e}")

        if current_state == AWAITING_WEIGHT:
            if not user_text.isdigit():
                new_message = await context.bot.send_message(
                    chat_id=user_id,
                    text='Введенный текст не содержит цифры. Пожалуйста, введите Ваш вес в цифрах:',
                    parse_mode=ParseMode.HTML,
                )
                context.user_data['current_message_id'] = new_message.message_id
                return

            weight = int(user_text)
            if weight > 250 or weight <= 5:
                new_message = await context.bot.send_message(
                    chat_id=user_id,
                    text=f'Введен некорректный вес. Пожалуйста, введите значение {"до 250 кг" if weight > 250 else "более 5 кг"}:',
                    parse_mode=ParseMode.HTML,
                )
                context.user_data['current_message_id'] = new_message.message_id
                return

            context.user_data['weight'] = weight
            new_message = await context.bot.send_message(
                chat_id=user_id,
                text='Введите ваш рост в сантиметрах:',
                parse_mode=ParseMode.HTML,
            )
            context.user_data['current_state'] = AWAITING_HEIGHT
            context.user_data['current_message_id'] = new_message.message_id

        elif current_state == AWAITING_HEIGHT:
            if not user_text.isdigit():
                new_message = await context.bot.send_message(
                    chat_id=user_id,
                    text='Введенный текст не содержит цифры. Пожалуйста, введите Ваш рост в цифрах:',
                    parse_mode=ParseMode.HTML,
                )
                context.user_data['current_message_id'] = new_message.message_id
                return

            height = int(user_text)
            if height > 300 or height <= 30:
                new_message = await context.bot.send_message(
                    chat_id=user_id,
                    text=f'Введен некорректный рост. Пожалуйста, введите значение {"до 300 см" if height > 300 else "более 30 см"}:',
                    parse_mode=ParseMode.HTML,
                )
                context.user_data['current_message_id'] = new_message.message_id
                return

            context.user_data['height'] = height
            new_message = await context.bot.send_message(
                chat_id=user_id,
                text='Введите ваш возраст:',
                parse_mode=ParseMode.HTML,
            )
            context.user_data['current_state'] = AWAITING_AGE
            context.user_data['current_message_id'] = new_message.message_id

        elif current_state == AWAITING_AGE:
            if not user_text.isdigit():
                new_message = await context.bot.send_message(
                    chat_id=user_id,
                    text='Введенный текст не содержит цифры. Пожалуйста, введите Ваш возраст в цифрах:',
                    parse_mode=ParseMode.HTML,
                )
                context.user_data['current_message_id'] = new_message.message_id
                return

            age = int(user_text)
            if age > 120 or age <= 1:
                new_message = await context.bot.send_message(
                    chat_id=user_id,
                    text=f'Введен некорректный возраст. Пожалуйста, введите значение {"до 120 лет" if age > 120 else "более 1 года"}:',
                    parse_mode=ParseMode.HTML,
                )
                context.user_data['current_message_id'] = new_message.message_id
                return

            context.user_data['age'] = age
            gender = context.user_data.get('gender')
            weight = context.user_data.get('weight')
            height = context.user_data.get('height')

            basal_metabolism = int(10 * weight) + (6.25 * height) - (5 * age) + (5 if gender == 'male' else -161)
            context.user_data['basal_metabolism'] = basal_metabolism

            new_message = await context.bot.send_message(
                chat_id=user_id,
                text=(f'Ваш основной обмен ≈ {basal_metabolism} ккал\n'
                      f'Теперь выберите уровень вашей физической активности:'),
                parse_mode=ParseMode.HTML,
                reply_markup=activity_coefficient()
            )
            context.user_data['current_state'] = AWAITING_ACTIVITY_COEFFICIENT
            context.user_data['current_message_id'] = new_message.message_id

    elif current_state == AWAITING_ACTIVITY_COEFFICIENT:
        data = query.data
        coefficients = {
            ACTIVITY_COEFFICIENT_12_BUTTON: 1.2,
            ACTIVITY_COEFFICIENT_13_BUTTON: 1.375,
            ACTIVITY_COEFFICIENT_15_BUTTON: 1.55,
            ACTIVITY_COEFFICIENT_17_BUTTON: 1.725,
            ACTIVITY_COEFFICIENT_19_BUTTON: 1.9
        }

        coefficient = coefficients.get(data)
        basal_metabolism = context.user_data.get('basal_metabolism')

        # Удаляем предыдущее сообщение, содержащее коэффициенты
        old_message_id = context.user_data.get('current_message_id')

        if old_message_id:
            await asyncio.sleep(0.4)
            try:
                await context.bot.delete_message(chat_id=user_id, message_id=old_message_id)
            except Exception as e:
                logging.error(f"Failed to delete message: {e}")

        if coefficient is not None:
            calorie_intake = int(coefficient * basal_metabolism)
            new_message = await context.bot.send_message(
                chat_id=user_id,
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
                parse_mode=ParseMode.HTML,
                reply_markup=make_keyboard_for_start_command()
            )
            context.user_data['current_message_id'] = new_message.message_id

