from datetime import timedelta
from django.utils import timezone
from django.db.models.signals import post_save
from django.contrib.auth import get_user_model
from django.dispatch import receiver
from django.contrib.auth.models import Group
from .models import UserDailyUsage_Model

User = get_user_model()

@receiver(post_save, sender=User)
def handle_User_creation(sender, instance, created, **kwargs):
    if created:

        # Add Free plan to the newly created user
        group, _ = Group.objects.get_or_create(name="free_plan")
        instance.groups.add(group)
        
        # Create Daily Usage 
        UserDailyUsage_Model.objects.create(
            user=instance,
            next_reset_date=timezone.now() + timedelta(days=1)
        )