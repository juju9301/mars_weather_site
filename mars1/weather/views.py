from django.shortcuts import render, get_object_or_404, redirect
from .models import Weather, Post, Comment
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from matplotlib import pyplot as plt
from django.urls import reverse
from django.http import HttpResponseBadRequest, JsonResponse
from django.contrib.auth.decorators import login_required
from .forms import PostForm, CommentForm
from django.core.files.base import ContentFile
from django.conf import settings

from io import BytesIO
import base64
import requests

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

    if (sol_from and sol_to and temp_type):
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
    posts_list = Post.objects.all().order_by('-created_at')
    paginator = Paginator(posts_list, 3)  # Show 3 posts per page

    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)

    recent_sol = Weather.objects.latest('sol') if Weather.objects.exists() else None
    return render(request, 'index.html', {'posts': posts, 'recent_sol': recent_sol, 'nasa_api_key': settings.NASA_API_KEY})

@login_required
def add_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            random_mars_image_url = form.cleaned_data.get('random_mars_image_url')
            if random_mars_image_url:
                response = requests.get(random_mars_image_url)
                if response.status_code == 200:
                    post.image.save(f"random_mars_image_{post.id}.jpg", ContentFile(response.content), save=False)
            post.save()
            return redirect('weather:index')
    else:
        form = PostForm()
    return render(request, 'add_post.html', {'form': form, 'nasa_api_key': settings.NASA_API_KEY})

@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            return redirect('weather:index')
    else:
        form = CommentForm()
    return render(request, 'add_comment.html', {'form': form, 'post': post, 'comments': post.comments.all()})

def update_weather_data(request):
    if request.method == 'POST':
        response = requests.get('http://cab.inta-csic.es/rems/wp-content/plugins/marsweather-widget/api.php')
        if response.status_code == 200:
            data = response.json()
            for entry in data['soles']:
                sol = entry['sol']
                if not Weather.objects.filter(sol=sol).exists():
                    Weather.objects.create(
                        orig_id=entry['id'],
                        terrestrial_date=entry['terrestrial_date'],
                        sol=entry['sol'],
                        ls=entry['ls'],
                        season=entry['season'],
                        min_temp=entry['min_temp'],
                        max_temp=entry['max_temp'],
                        pressure=entry['pressure'],
                        pressure_string=entry['pressure_string'],
                        abs_humidity=entry['abs_humidity'],
                        wind_speed=entry['wind_speed'],
                        wind_direction=entry['wind_direction'],
                        atmo_opacity=entry['atmo_opacity'],
                        sunrise=entry['sunrise'],
                        sunset=entry['sunset'],
                        local_uv_irradiance_index=entry['local_uv_irradiance_index'],
                        min_gts_temp=entry['min_gts_temp'],
                        max_gts_temp=entry['max_gts_temp']
                    )
            return redirect('weather:weather_list')
        else:
            return JsonResponse({'error': 'Failed to fetch data from the API'}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)
