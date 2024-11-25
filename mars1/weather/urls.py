from django.urls import path
from . import views

app_name = 'weather'

urlpatterns = [
    path('', views.weather_list, name='weather_list'),
    path('<int:sol>', views.weather_detail, name='weather_detail'),
]