from django.contrib import admin
from .models import Novel,Chapter,Genre,Tag,UserLikes_Bookmarks
# Register your models here.



admin.site.register(Novel)
admin.site.register(Genre)
admin.site.register(Tag)
admin.site.register(Chapter)
admin.site.register(UserLikes_Bookmarks)




