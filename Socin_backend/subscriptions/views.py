from rest_framework.views import APIView
from .serializer import UserSubscriptionSerializer,SubscriptionPlanSerializer
from .models import SubscriptionPlan,Usersubscription
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_list_or_404

# Create your views here.

RAZORPAY_API_KEY = settings.RAZORPAY_KEY

class GetSubscription_API_VIEW(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        user = request.user # Assign User to the Passed data
        plan_id = request.data['plan_id']
        try:
            subscription = Usersubscription.objects.filter(user=user,plan_id=plan_id).last()
            
            if subscription.status == 'cancelled':
                
                raise ObjectDoesNotExist
            if subscription.status == 'active':
                return Response({"Response":"You have already bought the subscription"})

            return Response({
                "key": RAZORPAY_API_KEY,
                "subscription_id": subscription.subscription_id
            }, status=200)

        except :
            data = {
                "user": user.id,
                'plan_id':plan_id,
            }

            serializer = UserSubscriptionSerializer(data=data)
            if serializer.is_valid():
                subscription = serializer.save()

                return Response({
                    **serializer.data,
                    "key": RAZORPAY_API_KEY
                }, status=201)

            return Response(serializer.errors, status=400)
        
