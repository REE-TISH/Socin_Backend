# Functions to upgrade the user and downgrade the user
from django.contrib.auth import get_user_model
from subscriptions.models import SubscriptionPlan, Usersubscription
from django.contrib.auth.models import Group
from .utils import client

# Activates user subscription
def activate_subscription(user, plan_id):
    if not user:
        return
    plan = SubscriptionPlan.objects.get(plan_id=plan_id)
    user.groups.clear()
    for group in plan.group.all():
        user.groups.add(group)
    user.save()

# remove all the premium features and downgrade to free plan
def downgrade_to_free(user):
    if not user:
        return
    user.groups.clear()
    group = Group.objects.get(name="free_plan")
    user.groups.add(group)
    user.save()

# If user deleted it account then end it subscription
def delete_user_subscription(sub_id):
    options = {
        "cancel_at_cycle_end":0
    }
    try:
        response = client.subscription.cancel(sub_id, options)
        print(response)
    except Exception as e:
        print(e)
