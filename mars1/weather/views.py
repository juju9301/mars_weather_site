from django.shortcuts import render, get_object_or_404, redirect
from .models import Weather
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from matplotlib import pyplot as plt
from django.urls import reverse
from django.http import HttpResponseBadRequest

import matplotlib.pyplot as plt
from io import BytesIO
import base64

def weather_list(request):
    sol_query = request.GET.get('sol')
    date_query = request.GET.get('terrestrial_date')
    
    if sol_query:
        soles = Weather.objects.filter(sol=sol_query)
    elif date_query:
        soles = Weather.objects.filter(terrestrial_date=date_query)
    else:
        soles = Weather.objects.all()
    
    paginator = Paginator(soles, 10)  # Show 10 sols per page
    page_number = request.GET.get('page')
    
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    
    return render(request, 'weather/weather_list.html', {'soles': soles, 'page_obj': page_obj})

# class WeatherListView(ListView):
#     queryset = Weather.objects.all()
#     context_object_name = 'soles'
#     paginate_by = 10
#     template_name = 'weather/weather_list.html'

def weather_detail(request, sol):
    sol_to_show = get_object_or_404(
        Weather, sol=sol
    )
    return render(request, 'weather/weather_detail.html', {'sol': sol_to_show})

def generate_weather_plot(request):
    sol_from = request.GET.get('sol_from')
    sol_to = request.GET.get('sol_to')
    temp_type = request.GET.get('temp_type')  # New parameter for temperature type

    # Fetch all available sols for dropdown options
    available_sols = Weather.objects.values_list('sol', flat=True).order_by('sol')

    if sol_from and sol_to and temp_type:
        try:
            sol_from = int(sol_from)
            sol_to = int(sol_to)
            terr_dates = {
                'date_from': Weather.objects.get(sol=sol_from).terrestrial_date,
                'date_to': Weather.objects.get(sol=sol_to).terrestrial_date
            }
        except ValueError:
            return HttpResponseBadRequest("Invalid sol range.")

        # Fetch weather data for the given sol range
        weather_data = Weather.objects.filter(sol__gte=sol_from, sol__lte=sol_to).order_by('sol')
        
        if not weather_data.exists():
            return render(request, 'weather/weather_plot.html', {
                'error': f'No weather data available for Sol range {sol_from} to {sol_to}.',
                'available_sols': available_sols,
            })

        # Generate plot for the selected range and temperature type
        plot_image = _generate_plot(weather_data, sol_from, sol_to, temp_type)
        return render(request, 'weather/weather_plot.html', {
            'plot_image': plot_image,
            'sol_from': sol_from,
            'sol_to': sol_to,
            'temp_type': temp_type,
            'available_sols': available_sols,
            'terr_dates': terr_dates
        })

    return render(request, 'weather/weather_plot.html', {
        'available_sols': available_sols,
    })


def _generate_plot(weather_data, sol_from, sol_to, temp_type):
    """
    Generate a plot for the given weather data and temperature type.
    """

    if temp_type == 'min_temp':
        sols = [w.sol for w in weather_data]
        temps = [w.min_temp for w in weather_data]
        temp_label = 'Min Temp'
        color = 'blue'
    elif temp_type == 'max_temp':
        sols = [w.sol for w in weather_data]
        temps = [w.max_temp for w in weather_data]
        temp_label = 'Max Temp'
        color = 'red'
    elif temp_type == 'average_temp':
        # Filter both sols and temps for rows where min_temp and max_temp are not None
        filtered_data = [
            (w.sol, (w.min_temp + w.max_temp) / 2)
            for w in weather_data
            if w.min_temp is not None and w.max_temp is not None
        ]
        sols, temps = zip(*filtered_data)  # Unpack filtered data into two lists
        temp_label = 'Average Temp'
        color = 'green'
    else:
        raise ValueError("Invalid temperature type selected.")

    plt.figure(figsize=(10, 6))
    plt.plot(sols, temps, label=temp_label, color=color)
    plt.xlabel('Sol')
    plt.ylabel('Temperature (°C)')
    plt.title(f'{temp_label} Trend from Sol {sol_from} to Sol {sol_to}')
    plt.legend()
    plt.grid()

    # Save plot to BytesIO buffer
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.close()

    # Convert the buffer to a base64 string for inline rendering
    image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
    buffer.close()

    return f'data:image/png;base64,{image_base64}'

def index(request):
    return render(request, 'index.html', {})
