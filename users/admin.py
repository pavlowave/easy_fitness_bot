from django.contrib import admin
from django.db.models import ManyToOneRel

from users.models import User


# Register your models here.
def get_fields_for_model(db_model) -> list[str]:
    fields = []
    for field in db_model._meta.get_fields():
        if isinstance(field, ManyToOneRel):
            continue
        fields.append(field.name)
    return fields



@admin.register(User)
class BotUserAdmin(admin.ModelAdmin):
    list_display = get_fields_for_model(User)
    search_fields = ['telegram_id', 'username', 'email', 'first_name', 'last_name']