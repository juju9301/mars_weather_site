from django.urls import path
from . import views

app_name = 'weather'

urlpatterns = [
    path('list', views.weather_list, name='weather_list'),
    path('<int:sol>', views.weather_detail, name='weather_detail'),
    path('plot', views.generate_weather_plot, name='generate_weather_plot'),
    path('update_weather_data', views.update_weather_data, name='update_weather_data'),
    path('api/get_weather_data', views.WeatherGetApiView.as_view(), name='get_weather_data'),

]