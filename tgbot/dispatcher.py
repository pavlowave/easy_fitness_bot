import re
from telegram.ext import CommandHandler, MessageHandler, CallbackQueryHandler, ConversationHandler, filters
from tgbot.handlers.onboarding.handlers import *
from tgbot.handlers.onboarding.manage_data import *
from tgbot.handlers.onboarding.cal_calcul.cal_cul import *

def get_handlers():
    return [
        CommandHandler('start', start),
        CommandHandler('hello', hello),
        CallbackQueryHandler(open_buttons, pattern=f'^{BACK_BUTTON}'),
        MessageHandler(filters.COMMAND, unknown),
        # Используем объединённую функцию calorie_calculation для обработки всех этапов
        CallbackQueryHandler(calorie_calculation, pattern='^' + re.escape(ACTIVITY_COEFFICIENT_12_BUTTON) + '$'),
        CallbackQueryHandler(calorie_calculation, pattern='^' + re.escape(ACTIVITY_COEFFICIENT_13_BUTTON) + '$'),
        CallbackQueryHandler(calorie_calculation, pattern='^' + re.escape(ACTIVITY_COEFFICIENT_15_BUTTON) + '$'),
        CallbackQueryHandler(calorie_calculation, pattern='^' + re.escape(ACTIVITY_COEFFICIENT_17_BUTTON) + '$'),
        CallbackQueryHandler(calorie_calculation, pattern='^' + re.escape(ACTIVITY_COEFFICIENT_19_BUTTON) + '$'),
        CallbackQueryHandler(calorie_calculation, pattern='^' + re.escape(MAN_BUTTON) + '$'),
        CallbackQueryHandler(calorie_calculation, pattern='^' + re.escape(WOMAN_BUTTON) + '$'),
        MessageHandler(filters.TEXT & ~filters.COMMAND, calorie_calculation),

        CallbackQueryHandler(button_base_click),
        ConversationHandler(
            entry_points=[CommandHandler('start', start)],
            states={
                START: [],
                AWAITING_WEIGHT: [
                    MessageHandler(filters.TEXT, calorie_calculation),
                ],
                AWAITING_HEIGHT: [
                    MessageHandler(filters.TEXT, calorie_calculation),
                ],
                AWAITING_AGE: [
                    MessageHandler(filters.TEXT, calorie_calculation),
                ],
                AWAITING_ACTIVITY_COEFFICIENT: [
                    MessageHandler(filters.TEXT, calorie_calculation),
                ],
            },
            fallbacks=[],
        )
    ]
