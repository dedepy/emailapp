from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('email/', include('emailapp.urls')),  # Маршруты для приложения emailapp
    path('', include('emailapp.urls')),  # Главная страница, перенаправляем на форму импорта
]
