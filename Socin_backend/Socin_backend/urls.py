
from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('webhook/',include('razorpay_setup.urls')),
    path("api/",include("Novel_Content.urls")),
    path('subscription/',include("subscriptions.urls")),
    path('action/',include('RecommendationSystem.urls')),
    path('AI/',include('AI_Content_Generation.urls')),
    path('user/',include('Custom_user.urls'))

]

