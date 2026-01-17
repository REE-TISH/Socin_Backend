from rest_framework import serializers
from .models import Usersubscription,SubscriptionPlan



class UserSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usersubscription
        fields = ['user','subscription_id','plan_id']


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields= ['name','plan_id']