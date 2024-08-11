from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from telegram.ext import ApplicationBuilder
from tgbot.dispatcher import get_handlers

class Command(BaseCommand):
    help = "Запускаем бота"

    def handle(self, *args, **options):
        try:
            application = ApplicationBuilder().token(settings.TOKEN_BOT).build()

            for handler in get_handlers():
                application.add_handler(handler)

            self.stdout.write(self.style.SUCCESS('Бот успешно запущен'))
            application.run_polling()
        except Exception as e:
            raise CommandError(f"Ошибка запуска бота: {e}")