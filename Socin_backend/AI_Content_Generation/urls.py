from django.urls import path
from . import views

urlpatterns = [
    path('create-chapter/<str:novel_id>/',views.get_ai_response,name='ai-response'),
    path('test-ai/',views.testing_AI_Response,name='test-ai-response'),
]