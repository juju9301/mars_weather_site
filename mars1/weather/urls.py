from django.urls import path
from . import views

app_name = 'weather'

urlpatterns = [
    path('list', views.weather_list, name='weather_list'),
    path('<int:sol>', views.weather_detail, name='weather_detail'),
    path('plot', views.generate_weather_plot, name='generate_weather_plot'),
    path('', views.index, name='index'),
]