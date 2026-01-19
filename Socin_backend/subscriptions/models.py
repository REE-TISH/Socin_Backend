from django.db import models
from django.contrib.auth import get_user_model
from decouple import config
from razorpay_setup.utils import client
from django.contrib.auth.models import Group
# Create your models here.

User = get_user_model() #User model



# Different SubscriptionPlan bought by users
class SubscriptionPlan(models.Model):

    name = models.CharField(max_length=50, unique=True,default='free')
    plan_id = models.CharField(max_length=100, unique=True,blank=True,null=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    interval = models.IntegerField(default=1)  # how many months
    period = models.CharField(max_length=20, default='monthly')  # e.g., 'month', 'year'
    description = models.TextField(blank=True)
    currency = models.CharField(max_length=10, default='INR')
    group = models.ManyToManyField(Group, related_name='plans', blank=True)
    class Meta:
        permissions = [
            ("premium_plan", "Gets premium features"),
            ("free_plan", "Get Limited features Only"),
        ]

    def save(self, *args, **kwargs):
        if not self.plan_id:
            response = client.plan.create({
                "period":self.period,
                "interval":int(self.interval),
                "item": {
                    "name":self.name,
                    "amount":int(self.price)*100,  # amount in paise
                    "currency":self.currency,
                    "description":self.description
                }
            })
            self.plan_id = response['id']
        
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


# Subscription Model : contains the information about the user who have subscribed
class Usersubscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL,blank=True,null=True,related_name="subscription") 
    subscription_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    plan_id = models.CharField(max_length=100, null=True, blank=True)
    start_at = models.IntegerField(null=True, blank=True)
    end_at = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=50, blank=True)
    # payment_success = models.BooleanField(default=False)
    def save(self, *args, **kwargs):
        if not self.subscription_id: # If user doesn't have a subscription id
            response = client.subscription.create({
                "plan_id": self.plan_id,
                "customer_notify": 1,
                "total_count": 12,
                "notes": {
                    "username":self.user.username,
                    "user_id": str(self.user.id)}
            })
            self.subscription_id = response['id']
            self.start_at = response['created_at']
            self.end_at = response['expire_by']
            self.status = response['status']
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user} - {self.status}"