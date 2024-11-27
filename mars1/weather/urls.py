from django.urls import path
from . import views

app_name = 'weather'

urlpatterns = [
    path('', views.WeatherListView.as_view(), name='weather_list'),
    path('<int:sol>', views.weather_detail, name='weather_detail'),
    path('plot', views.plot, name='weather_plot'),
]