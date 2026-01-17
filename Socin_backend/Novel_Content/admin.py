from django.contrib import admin
from .models import Novel,Chapter,Genre,Tag
# Register your models here.



admin.site.register(Novel)
admin.site.register(Genre)
admin.site.register(Tag)
admin.site.register(Chapter)





