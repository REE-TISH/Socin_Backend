from django.urls import path
from . import views
from rest_framework_simplejwt.views import (
                    TokenObtainPairView,
                    TokenRefreshView,
)

urlpatterns = [
    path("auth/google/", views.GoogleAuthView.as_view()),# Login through google
    path('create-user/',views.Create_User_API_VIEW.as_view(),name='create_user'),# Create User 
                    # User Account changes
    path('change-password/',views.change_password_API_VIEW,name="change_pass"),# set Password
    path('delete-account/',views.delete_account_API_VIEW,name="delete_user"),
    path('user-profile/',views.get_your_profile_data_API_VIEW,name="user_profile"),
    path('edit-profile/',views.edit_user_info_api,name="edit_profile"),
                  # JWT Authentication
    path('token/',TokenObtainPairView.as_view(),name="get_token"), 
    path('token/refresh/',TokenRefreshView.as_view(),name="refresh_token")
]