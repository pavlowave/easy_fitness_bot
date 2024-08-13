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
(START) = range(1)


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



async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Hello {update.effective_user.first_name}')


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Извините, я не понимаю эту команду."
    )
