from django.db import models
from django.contrib.auth import get_user_model
from Novel_Content.models import Novel,Chapter

# Create your models here.
User = get_user_model()
class ChapterBeingCreated(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    novel = models.ForeignKey(Novel,on_delete=models.CASCADE)
    content = models.TextField()
    chapter_name = models.CharField(default="",max_length=255)
    chapter_summary = models.TextField(default="")
    ultra_short_summary = models.CharField(default="",max_length=512)



    def __str__(self):
        return f"Chapter being created by {self.user.username} for novel {self.novel.name}"