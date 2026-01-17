# Functions to upgrade the user and downgrade the user
from django.contrib.auth import get_user_model
from subscriptions.models import SubscriptionPlan, Usersubscription
from django.contrib.auth.models import Group

# Activates user subscription
def activate_subscription(user, plan_id):
    plan = SubscriptionPlan.objects.get(plan_id=plan_id)
    user.groups.clear()
    for group in plan.group.all():
        user.groups.add(group)
    user.save()

# remove all the premium features and downgrade to free plan
def downgrade_to_free(user):
    user.groups.clear()
    group = Group.objects.get(name="free_plan")
    user.groups.add(group)
    user.save()

# Check if the user has paid the money but didn't get the subscription activated
# def check_and_activate_subscription(user):
#     usersubscription = Usersubscription.objects.filter(user=user, payment_success=True, status='active')
