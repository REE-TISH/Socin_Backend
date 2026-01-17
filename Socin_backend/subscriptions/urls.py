from django.urls import path
from . import views

urlpatterns = [
    path('',views.GetSubscription_API_VIEW.as_view(),name="get_subscription"),
]