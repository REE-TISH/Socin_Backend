from django.db import models
from django.contrib.auth import get_user_model
from Novel_Content.models import Novel,Genre,Tag

# Create your models here.
User = get_user_model()
class UserAction(models.Model):
    ACTION_CHOICES = [
        ("view", "View"),
        ("read", "Read"),
        ("like", "Like"),
        ("bookmark", "Bookmark"),
        ("finish", "Finish"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    novel = models.ForeignKey(Novel, on_delete=models.CASCADE)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    weight = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} {self.action} {self.novel.name}"

class UserInterest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, null=True, blank=True, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, null=True, blank=True, on_delete=models.CASCADE)
    score = models.FloatField(default=0)

    def __str__(self):
        return f"{self.user.username} interests"

class UserRecommendations(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    novel_ids = models.JSONField()
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} recommends"