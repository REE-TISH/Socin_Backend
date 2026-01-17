from django.urls import path
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path("novel-content",views.All_Novels_API_VIEW.as_view(),name="novel_list"),# gets all the novels
    path('novel/<str:pk>/',views.Get_Novel_Data_API_VIEW.as_view(),name='novel_data'),
    path("novel/<str:novel_id>/chapter/<str:pk>/",views.getNovelChapter_API_VIEW,name="novel_chapter"),
    path("personal-novels/",views.Personal_Novels_API_VIEW.as_view(),name="personal_novels"),# Retreive All the Users personal novels
    path("create-novel/",views.Create_Novel_API_VIEW.as_view(),name="create_novel"),
    path("novel/<str:novel_id>/create-chapter/",views.Publish_Chapter_API_VIEW.as_view(),name="create_chapter"),# Create the chapter of the novel
    path('novel/<str:novel_id>/chapter-user-working-on/',views.Chapter_User_WorkingOn,name="chapter_user_working_on"),# If the user has chapter that he is working on but hasn't published yet and want to customize the chapter content

]