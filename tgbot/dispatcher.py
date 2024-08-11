from telegram.ext import CommandHandler, MessageHandler, CallbackQueryHandler, ConversationHandler, filters
from tgbot.handlers.onboarding.handlers import *
from tgbot.handlers.onboarding.manage_data import *
from tgbot.handlers.onboarding import handlers as onboarding_handlers
import re


def get_handlers():
    return [
        CommandHandler('start', start),
        CommandHandler('hello', hello),
        CallbackQueryHandler(open_buttons, pattern=f'^{BACK_BUTTON}'),

        CallbackQueryHandler(calorie_calculation, pattern='^' + re.escape(MAN_BUTTON) + '$'),
        CallbackQueryHandler(calorie_calculation, pattern='^' + re.escape(WOMAN_BUTTON) + '$'),
        MessageHandler(filters.COMMAND, unknown),

        # Добавляем обработчики для кнопок с уровнями активности
        CallbackQueryHandler(onboarding_handlers.pick_coeff, pattern='^' + re.escape(ACTIVITY_COEFFICIENT_12_BUTTON) + '$'),
        CallbackQueryHandler(onboarding_handlers.pick_coeff, pattern='^' + re.escape(ACTIVITY_COEFFICIENT_13_BUTTON) + '$'),
        CallbackQueryHandler(onboarding_handlers.pick_coeff, pattern='^' + re.escape(ACTIVITY_COEFFICIENT_15_BUTTON) + '$'),
        CallbackQueryHandler(onboarding_handlers.pick_coeff, pattern='^' + re.escape(ACTIVITY_COEFFICIENT_17_BUTTON) + '$'),
        CallbackQueryHandler(onboarding_handlers.pick_coeff, pattern='^' + re.escape(ACTIVITY_COEFFICIENT_19_BUTTON) + '$'),
        MessageHandler(filters.TEXT & ~filters.COMMAND, onboarding_handlers.handle_user_input),
        CallbackQueryHandler(button_base_click),
        ConversationHandler(
            entry_points=[CommandHandler('start', start)],
            states={
                START: [],
                AWAITING_WEIGHT: [
                    MessageHandler(filters.TEXT, onboarding_handlers.handle_user_input),
                ],
                AWAITING_HEIGHT: [
                    MessageHandler(filters.TEXT, onboarding_handlers.handle_user_input),
                ],
                AWAITING_AGE: [
                    MessageHandler(filters.TEXT, onboarding_handlers.handle_user_input),
                ],
                AWAITING_ACTIVITY_COEFFICIENT: [
                    MessageHandler(filters.TEXT, onboarding_handlers.handle_user_input),
                ],
                AWAITING_EMAIL_STATE: [
                    MessageHandler(filters.TEXT, onboarding_handlers.handle_user_input),
                ],
                AWAITING_HELP_TEXT: [
                    MessageHandler(filters.TEXT, onboarding_handlers.handle_user_input),
                ],
            },
            fallbacks=[],
        )
    ]

