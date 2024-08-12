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
(START, AWAITING_HELP_TEXT, AWAITING_EMAIL_STATE,
    AWAITING_WEIGHT, AWAITING_HEIGHT,
    AWAITING_AGE, AWAITING_ACTIVITY_COEFFICIENT) = range(7)


async def start(update: Update, context: CallbackContext):
    user_data = extract_user_data_from_update(update)
    user_id = user_data['user_id']
    # Получение пользователя из базы данных асинхронно
    user = await sync_to_async(lambda: User.objects.filter(user_id=user_id).first())()
    if not user:
        # Если пользователя нет, создаем нового
        user, created = await sync_to_async(User.get_user_and_created)(update, context)
    text = "Привет. Я фитнес бот. Твой помощник."
    await context.bot.send_message(
        chat_id=user_id,
        text=text,
        reply_markup=make_keyboard_for_start_command(),
    )
    context.user_data.clear()


async def open_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = extract_user_data_from_update(update)['user_id']
    text = "Привет. Я фитнес бот. Твой помощник."
    await context.bot.edit_message_text(
        chat_id=user_id,
        message_id=update.callback_query.message.message_id,
        text=text,
        parse_mode=ParseMode.HTML,
        reply_markup=make_keyboard_for_start_command()
    )


async def go_back(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = extract_user_data_from_update(update)['user_id']
    await context.bot.send_message(
        chat_id=user_id,
        reply_markup=make_keyboard_for_start_command()
    )
    context.user_data['current_state'] = START
    return START


async def button_base_click(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info(f"User data: {extract_user_data_from_update(update)}")
    query = update.callback_query
    data = query.data
    user_id = extract_user_data_from_update(update)['user_id']

    if data == DIRECTORY_BUTTON:
        text = 'Справочник:'
        await context.bot.edit_message_text(
            chat_id=user_id,
            message_id=query.message.message_id,
            text=text,
            parse_mode=ParseMode.HTML,
            reply_markup=make_keyboard_for_directory()
        )

    elif data == MY_PROFILE_BUTTON:

        try:

            # Получение пользователя из базы данных асинхронно

            user_s: QuerySet[User] = User.objects.filter(user_id=user_id)

            if await user_s.aexists():  # Необходимо использовать await

                user = await user_s.afirst()  # Необходимо использовать await

                has_email = bool(user.email)

                has_subscription = user.subscription

                if has_email and has_subscription:

                    expiration_date_str = user.subscription_expiration_date.strftime(

                        '%d.%m.%Y') if user.subscription_expiration_date else "неизвестно"

                    text = f'Ваша подписка активна до {expiration_date_str}\nВаш email: {user.email}'

                    reply_markup = make_keyboard_for_action_have_em_and_s()


                elif has_email:

                    text = f'У Вас нет подписки\nВаш email: {user.email}'

                    reply_markup = make_keyboard_for_action_have_em_and_d_have_s()

                    print('У пользователя есть email, но нет подписки.')


                elif has_subscription:

                    expiration_date_str = user.subscription_expiration_date.strftime(

                        '%d.%м.%Y') if user.subscription_expiration_date else "неизвестно"

                    text = f'Ваша подписка активна до {expiration_date_str}\nУ Вас не привязан email'

                    reply_markup = make_keyboard_for_action_d_have_em_and_have_s()

                    print('У пользователя есть подписка, но нет email.')


                else:

                    text = 'У Вас нет подписки и не привязан email'

                    reply_markup = make_keyboard_for_action_d_have_em_and_d_have_s()

                await context.bot.edit_message_text(

                    chat_id=user_id,

                    message_id=query.message.message_id,

                    text=text,

                    parse_mode=ParseMode.HTML,

                    reply_markup=reply_markup

                )


            else:

                print('Пользователь не найден в базе данных.')

        except Exception as e:

            logger.error(f"Error occurred: {e}")

    elif data == CALCULATION_CALORIES:
        text = 'Я умею рассчитывать норму калорий по формуле Миффлина-Сан Жеора, выберите свой пол:'
        await context.bot.edit_message_text(
            chat_id=user_id,
            message_id=query.message.message_id,
            text=text,
            parse_mode=ParseMode.HTML,
            reply_markup=make_keyboard_for_get_gender()
        )

    elif data == HELP_BUTTON:
        text = 'Наши специалисты поддержки всегда открыты и готовы ответить на любые ваши вопросы.'
        await context.bot.edit_message_text(
            chat_id=user_id,
            message_id=query.message.message_id,
            text=text,
            parse_mode=ParseMode.HTML,
            reply_markup=make_keyboard_for_get_help()
        )


async def calorie_calculation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    data = query.data
    user_id = extract_user_data_from_update(update)['user_id']

    if data in [MAN_BUTTON, WOMAN_BUTTON]:
        if data == MAN_BUTTON:
            context.user_data['gender'] = 'male'
        else:
            context.user_data['gender'] = 'female'

        text = 'Введите вес в кг, на который Вы хотите посчитать калорийность:'
        state = AWAITING_WEIGHT

        await context.bot.edit_message_text(
            text=text,
            chat_id=user_id,
            message_id=update.callback_query.message.message_id,
            parse_mode=ParseMode.HTML,
        )
        context.user_data['current_state'] = state


async def handle_user_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global true_weight
    global true_height
    global true_age
    global basal_metabolism
    user_id = extract_user_data_from_update(update)['user_id']
    user_text = update.message.text.title()
    gender = context.user_data.get('gender')
    if context.user_data.get('current_state') == AWAITING_HELP_TEXT:
        # Логика для обработки вопроса пользователя
        await context.bot.send_message(
            text=f'Спасибо. Передал ваш вопрос "{user_text}" специалистам. Очень скоро они свяжутся с вами.',
            chat_id=user_id,
            parse_mode=ParseMode.HTML,
        )
    elif context.user_data.get('current_state') == AWAITING_EMAIL_STATE:
        # Проверяем, содержит ли введенный текст пробелы
        if ' ' in user_text:
            await context.bot.send_message(
                text='Введенный текст содержит пробелы. Пожалуйста, введите email без пробелов.',
                chat_id=user_id,
                parse_mode=ParseMode.HTML,
            )
            # Возвращаем текущее состояние, чтобы продолжить ожидание ввода email
            return AWAITING_EMAIL_STATE

        # Проверяем, что введенный текст является валидным email
        if re.match(r"[^@]+@[^@]+\.[^@]+", user_text):
            await context.bot.send_message(
                text=f'Спасибо. Теперь ваш email: "{user_text}".',
                chat_id=user_id,
                parse_mode=ParseMode.HTML,
            )
        else:
            await context.bot.send_message(
                text='Введенный текст не похож на email. Пожалуйста, введите корректный email.',
                chat_id=user_id,
                parse_mode=ParseMode.HTML,
            )
            return AWAITING_EMAIL_STATE

    elif context.user_data.get('current_state') == AWAITING_WEIGHT:
        if not user_text.isdigit():
            await context.bot.send_message(
                text='Введенный текст не содержит цифры. Пожалуйста, введите Ваш вес в цифрах:',
                chat_id=update.message.chat_id,
                parse_mode=ParseMode.HTML,
            )
            return AWAITING_WEIGHT
        else:
            weight = int(user_text)

            if weight > 250:
                await context.bot.send_message(
                    text='Введен некорректный вес. Пожалуйста, введите значение до 250 кг:',
                    chat_id=update.message.chat_id,
                    parse_mode=ParseMode.HTML,
                )
                return AWAITING_WEIGHT
            elif weight <= 5:
                await context.bot.send_message(
                    text='Введен некорректный вес. Пожалуйста, введите значение более 5 кг:',
                    chat_id=update.message.chat_id,
                    parse_mode=ParseMode.HTML,
                )
                return AWAITING_WEIGHT

            true_weight = weight

            await context.bot.send_message(
                text='Введите ваш рост в сантимертах:',
                chat_id=update.message.chat_id,
                parse_mode=ParseMode.HTML,
            )
            context.user_data['current_state'] = AWAITING_HEIGHT
            return AWAITING_HEIGHT

    elif context.user_data.get('current_state') == AWAITING_HEIGHT:
        if not user_text.isdigit():
            await context.bot.send_message(
                text='Введенный текст не содержит цифры. Пожалуйста, введите Ваш рост в цифрах:',
                chat_id=update.message.chat_id,
                parse_mode=ParseMode.HTML,
            )
            return AWAITING_HEIGHT
        else:
            height = int(user_text)
            if height > 300:
                await context.bot.send_message(
                    text='Введен некорректный рост. Пожалуйста, введите корректные данные:',
                    chat_id=update.message.chat_id,
                    parse_mode=ParseMode.HTML,
                )
                return AWAITING_HEIGHT
            elif height <= 30:
                await context.bot.send_message(
                    text='Введен некорректный рост. Пожалуйста, введите значение более 30 см:',
                    chat_id=update.message.chat_id,
                    parse_mode=ParseMode.HTML,
                )
                return AWAITING_HEIGHT

            true_height = height

            await context.bot.send_message(
                text='Введите ваш возраст:',
                chat_id=update.message.chat_id,
                parse_mode=ParseMode.HTML,
            )
            context.user_data['current_state'] = AWAITING_AGE
            return AWAITING_AGE

    elif context.user_data.get('current_state') == AWAITING_AGE:
        if not user_text.isdigit():
            await context.bot.send_message(
                text='Введенный текст не содержит цифры. Пожалуйста, введите Ваш возраст в цифрах:',
                chat_id=update.message.chat_id,
                parse_mode=ParseMode.HTML,
            )
            return AWAITING_AGE
        else:
            age = int(user_text)
            if age > 120:
                await context.bot.send_message(
                    text='Введен некорректный возраст. Пожалуйста, введите корректные данные:',
                    chat_id=update.message.chat_id,
                    parse_mode=ParseMode.HTML,
                )
                return AWAITING_AGE
            elif age <= 1:
                await context.bot.send_message(
                    text='Введен некорректный возраст. Пожалуйста, введите значение более 1 года:',
                    chat_id=update.message.chat_id,
                    parse_mode=ParseMode.HTML,
                )
                return AWAITING_AGE
            true_age = age
            if gender == 'male':
                basal_metabolism = int(10 * true_weight) + (6.25 * true_height) - (5 * true_age) + 5
                basal_metabolism = int(basal_metabolism)
            elif gender == 'female':
                basal_metabolism = int(10 * true_weight) + (6.25 * true_height) - (5 * true_age) - 161
                basal_metabolism = int(basal_metabolism)
            await context.bot.send_message(
                text=(f'Ваш основной обмен ≈ {basal_metabolism} ккал\n'
                      f'Теперь выберите уровень вашей физической активности:'),
                chat_id=update.message.chat_id,
                parse_mode=ParseMode.HTML,
                reply_markup=activity_coefficient()
            )
            context.user_data['current_state'] = AWAITING_ACTIVITY_COEFFICIENT
            return AWAITING_ACTIVITY_COEFFICIENT




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



async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Hello {update.effective_user.first_name}')


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Извините, я не понимаю эту команду."
    )
