from django.shortcuts import render, get_object_or_404
from .models import Weather

def weather_list(request):
    soles = Weather.objects.all()
    return render(request, 'weather/weather_list.html', {'soles': soles})

def weather_detail(request, sol):
    sol_to_show = get_object_or_404(
        Weather, sol=sol
    )
    return render(request, 'weather/weather_detail.html', {'sol': sol_to_show})
