from django.shortcuts import render, get_object_or_404, redirect
from .models import Weather, Plot
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from matplotlib import pyplot as plt
from django.urls import reverse
from django.views.generic import ListView
from .forms import PlotForm
import io 
from django.core.files.base import ContentFile

# def weather_list(request):
#     soles = Weather.objects.all()
#     paginator = Paginator(soles, 10)
#     page = request.GET.get('page')
#     try:
#         soles = paginator.page(page)
#     except PageNotAnInteger:
#         soles = paginator.page(1)
#     except EmptyPage:
#         soles = paginator.page(paginator.num_pages)
#     return render(request, 'weather/weather_list.html', 
#                   {'soles': soles,
#                    'page': page})

class WeatherListView(ListView):
    queryset = Weather.objects.all()
    context_object_name = 'soles'
    paginate_by = 10
    template_name = 'weather/weather_list.html'

def weather_detail(request, sol):
    sol_to_show = get_object_or_404(
        Weather, sol=sol
    )
    return render(request, 'weather/weather_detail.html', {'sol': sol_to_show})

def plot(request):
    graph = None
    if request.method == 'POST':
        form = PlotForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            param = cd['param']
            soles = Weather.objects.filter(sol__gte=cd['sol_from'], sol__lte=cd['sol_to'])
            sol_list = soles.values_list(['sol'], flat=True).order_by('sol')
            field_list = soles.values_list([param], flat=True).order_by('sol')

            plt.figure() 
            plt.plot(sol_list, field_list) 
            plt.title('Plot Graph') 
            plt.xlabel('Sol') 
            plt.ylabel(param) 
            plt.grid(True)

            # Save the plot to a bytes buffer 
            buffer = io.BytesIO() 
            plt.savefig(buffer, format='png') 
            plt.close() 
            image_file = ContentFile(buffer.getvalue()) 
            
            slug = f'{cd['sol_from']} - {cd['sol_to']} - {param}'
            # Save the image to the model 
            generated_image = Plot(slug=slug, sol_from=cd['sol_from'], sol_to=cd['sol_to'], param=param) 
            generated_image.image.save(f'{slug}.png', image_file)

            return redirect('weather_plot')
            # return render(request, 'weather/plot.html', {
            #     'sol_from': cd['sol_from'],
            #     'sol_to': cd['sol_to'],
            #     'param': param,
            #     'graph': graph
            # })
    else:
        form = PlotForm()
    sol_from_choices = Weather.objects.values_list('sol').order_by('sol')
    print(sol_from_choices)
    return render(request, 'weather/plot.html', {
        'form': form,
        'graph': graph})
    
