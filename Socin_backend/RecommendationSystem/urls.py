from django.urls import path
from . import views

urlpatterns = [
        path('track-actions/',views.Novel_Liked_OR_Bookmarked_API_VIEW,name='user-like-bookmarks')# To send post request for a like or bookmark
]