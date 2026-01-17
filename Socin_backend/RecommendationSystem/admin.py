from django.contrib import admin
from .models import UserAction,UserInterest,UserRecommendations
# Register your models here.

admin.site.register(UserAction)
admin.site.register(UserInterest)
admin.site.register(UserRecommendations)