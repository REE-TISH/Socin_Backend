from django.db import models
from django.contrib.auth.models import AbstractUser,BaseUserManager
from phonenumber_field.modelfields import PhoneNumberField
from django.utils import timezone
from datetime import timedelta

# Create your models here.



class CustomNovelUser_Model(AbstractUser):

    user_id = models.CharField(unique=True,blank=True,null=True)    
    username = models.CharField(max_length=120)
    email = models.EmailField()
    avatar = models.URLField(blank=True)
    bio = models.CharField(max_length=200,blank=True)
    created_at = models.DateField(auto_now_add=True)

    USERNAME_FIELD = 'user_id'

    def __str__(self):
        return self.username

    @property
    def is_premium(self):
        return self.groups.filter(name="premium_plan").exists()

    @property
    def user(self):
        if self.name:
            return self.name
        return ""



class UserDailyUsage_Model(models.Model):
    user = models.OneToOneField(CustomNovelUser_Model,on_delete=models.CASCADE,related_name="daily_usage")
    chapter_creation_requests_made = models.IntegerField(default=0)
    next_reset_date = models.DateTimeField(null=True,blank=True)

    def __str__(self):
        return f"Daily Usage for {self.user.username}"
    
    def reset_if_needed(self):
        if timezone.now() >= self.next_reset_date:
            self.chapter_creation_requests_made = 0
            self.next_reset_date = timezone.now() + timedelta(days=1)
            self.save(update_fields=["chapter_creation_requests_made", "next_reset_date"])

