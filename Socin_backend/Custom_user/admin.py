from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomNovelUser_Model, UserDailyUsage_Model

class CustomUserAdmin(UserAdmin):
    model = CustomNovelUser_Model
    list_display = ['username', 'email',]

    fieldsets = UserAdmin.fieldsets + (
        ("Custom Fields", {
            "fields": ("avatar","bio","user_id"),
        }),
    )

admin.site.register(CustomNovelUser_Model, CustomUserAdmin)
admin.site.register(UserDailyUsage_Model)