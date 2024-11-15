from django.urls import path
from . import views

urlpatterns = [
    path('import/', views.import_emails, name='import_emails'),
    path('', views.import_emails, name='home'),
    path('df/', views.start_import, name='hello'),

    path('start-import/', views.start_import, name='start_import'),
    path('get-import-progress/', views.get_import_progress, name='get_import_progress'),
]
