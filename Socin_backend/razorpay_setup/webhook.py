import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from decouple import config
from razorpay.errors import SignatureVerificationError
from subscriptions.models import Usersubscription
from .services import activate_subscription, downgrade_to_free
from .utils import client
from django.shortcuts import get_object_or_404

#TODO : Add your webhook processing logic here

@csrf_exempt
def razorpay_webhook(request):
    payload = request.body.decode("utf-8") # data received from razorpay
    signature = request.headers.get("X-Razorpay-Signature")
    try:
        client.utility.verify_webhook_signature(
            payload,
            signature,
            config('RAZORPAY_WEBHOOK_SECRET')
        )
    except SignatureVerificationError:
        return HttpResponse(status=400)
    
    event = json.loads(payload)
    event_type = event["event"]


    if event_type == "subscription.activated":
        handle_subscription_activated(event)

    if event_type == "invoice.payment_failed":
        handle_payment_failed(event)

    if event_type == "subscription.cancelled":
        handle_subscription_cancelled(event)

    return HttpResponse(status=200)


#TODO : User Subscription handler to activate user subscription

def handle_subscription_activated(event):
    sub_id = event["payload"]["subscription"]["entity"]["id"]

    subscription = Usersubscription.objects.get(
        subscription_id=sub_id
    )

    subscription.status = "active"
    subscription.save()

    activate_subscription(
        subscription.user,
        subscription.plan_id
    )

#TODO : If paymenet failed then downgrade the user to free plan

def handle_payment_failed(event):
    sub_id = event["payload"]["subscription"]["entity"]["id"]

    subscription = Usersubscription.objects.get(
        subscription_id=sub_id
    )

    subscription.status = "failed"
    subscription.save()

    downgrade_to_free(subscription.user)

#TODO:   IF SUBSCRIPTION IS CANCELLED IN RAZORPAY THEN DOWNGRADE THE USER TO FREE PLAN

def handle_subscription_cancelled(event):
    sub_id = event["payload"]["subscription"]["entity"]["id"]

    try:
        subscription = Usersubscription.objects.get(
            subscription_id=sub_id
        )

        subscription.status = "cancelled"
        subscription.save()

        downgrade_to_free(subscription.user)
    except Exception as e:
        print(e)


# Delete User Subscription
# def delete_user_subscription(event):
#     sub_id = event['payload']['subscription']['entity']['id']
#     subscription = get_object_or_404(Usersubscription,subscription_id=sub_id)
#     subscription.delete()