from django.shortcuts import render, get_object_or_404
from .models import Weather
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Max, Min
from .serializers import WeatherSerializer
from .forms import PLOT_METRIC_CHOICES, PlotForm
from rest_framework import generics, status
from rest_framework.response import Response
from datetime import datetime

from io import BytesIO
import base64
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
from matplotlib.ticker import FuncFormatter


PLOT_METRIC_LABELS = dict(PLOT_METRIC_CHOICES)
PLOT_Y_AXIS_LABELS = {
    'ls': 'Solar longitude (°)',
    'max_temp': 'Air temperature (°C)',
    'min_temp': 'Air temperature (°C)',
    'max_gts_temp': 'Ground temperature (°C)',
    'min_gts_temp': 'Ground temperature (°C)',
    'pressure': 'Pressure (Pa)',
    'sunrise': 'Local true solar time (LTST)',
    'sunset': 'Local true solar time (LTST)',
}
PLOT_COLORS = {
    'ls': 'darkorange',
    'max_temp': 'firebrick',
    'min_temp': 'royalblue',
    'max_gts_temp': 'saddlebrown',
    'min_gts_temp': 'peru',
    'pressure': 'slateblue',
    'sunrise': 'darkorange',
    'sunset': 'midnightblue',
}
LTST_METRICS = frozenset(('sunrise', 'sunset'))


def weather_list(request):
    sol_query = request.GET.get('sol')
    date_query = request.GET.get('terrestrial_date')
    
    if sol_query:
        soles = Weather.objects.filter(sol=sol_query)
    elif date_query:
        soles = Weather.objects.filter(terrestrial_date=date_query)
    else:
        soles = Weather.objects.all()
    
    paginator = Paginator(soles, 50)  # Show 50 sols per page
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
    quality_summary = sol_to_show.rems_quality_summary or {}
    metric_labels = (
        ("air_temperature", "Air temperature"),
        ("ground_temperature", "Ground temperature (GTS)"),
        ("pressure", "Pressure"),
        ("uv_abc_daylight", "Daylight UV_ABC irradiance"),
    )
    metrics = quality_summary.get("metrics", {})
    quality_metrics = []
    for metric_key, label in metric_labels:
        metric = metrics.get(metric_key)
        if not isinstance(metric, dict):
            continue
        flags = metric.get("confidence_flag_counts", {})
        quality_metrics.append({
            "label": label,
            "valid_samples": metric.get("valid_samples"),
            "total_samples": metric.get("total_samples"),
            "daylight_samples": metric.get("daylight_samples"),
            "burst_count": metric.get("burst_count"),
            "coldest_burst_valid_samples": metric.get(
                "coldest_burst_valid_samples"
            ),
            "coldest_burst_mean_celsius": metric.get(
                "coldest_burst_mean_celsius"
            ),
            "confidence_flags": list(flags.items())
            if isinstance(flags, dict)
            else [],
        })
    return render(
        request,
        'weather/weather_detail.html',
        {
            'sol': sol_to_show,
            'quality_summary': quality_summary,
            'quality_metrics': quality_metrics,
        },
    )

def generate_weather_plot(request):
    sol_bounds = Weather.objects.aggregate(min_sol=Min('sol'), max_sol=Max('sol'))
    form = PlotForm(
        request.GET if request.GET else None,
        min_sol=sol_bounds['min_sol'],
        max_sol=sol_bounds['max_sol'],
    )
    context = {
        'form': form,
        'available_min_sol': sol_bounds['min_sol'],
        'available_max_sol': sol_bounds['max_sol'],
    }

    if request.GET and form.is_valid():
        sol_from = form.cleaned_data['sol_from']
        sol_to = form.cleaned_data['sol_to']
        metric = form.cleaned_data['metric']
        weather_data = list(
            Weather.objects.filter(sol__gte=sol_from, sol__lte=sol_to)
            .only('sol', 'terrestrial_date', metric)
            .order_by('sol')
        )
        plot_image = _generate_plot(weather_data, sol_from, sol_to, metric)
        if plot_image is None:
            metric_label = PLOT_METRIC_LABELS[metric]
            context['error'] = (
                f'No {metric_label.lower()} data is available between '
                f'Sol {sol_from} and Sol {sol_to}.'
            )
        else:
            records_by_sol = {record.sol: record for record in weather_data}
            context.update({
                'plot_image': plot_image,
                'sol_from': sol_from,
                'sol_to': sol_to,
                'metric_label': PLOT_METRIC_LABELS[metric],
                'date_from': records_by_sol[sol_from].terrestrial_date,
                'date_to': records_by_sol[sol_to].terrestrial_date,
            })

    return render(request, 'weather/weather_plot.html', context)


def _generate_plot(weather_data, sol_from, sol_to, metric):
    points = []
    has_data = False
    for record in weather_data:
        value = getattr(record, metric)
        if metric in LTST_METRICS:
            value = _ltst_to_hours(value)
        if value is not None:
            has_data = True
        points.append((record.sol, value if value is not None else float('nan')))
    if not has_data:
        return None

    sols, values = zip(*points)
    figure, axis = plt.subplots(figsize=(10, 6))
    buffer = BytesIO()
    try:
        axis.plot(
            sols,
            values,
            label=PLOT_METRIC_LABELS[metric],
            color=PLOT_COLORS[metric],
            marker='o',
        )
        axis.set_xlabel('Sol')
        axis.set_ylabel(PLOT_Y_AXIS_LABELS[metric])
        axis.set_title(
            f'{PLOT_METRIC_LABELS[metric]} from Sol {sol_from} to Sol {sol_to}'
        )
        if metric in LTST_METRICS:
            axis.set_ylim(0, 24)
            axis.set_yticks(range(0, 24, 2))
            axis.yaxis.set_major_formatter(
                FuncFormatter(lambda value, _: _format_ltst_tick(value))
            )
        axis.legend()
        axis.grid()
        figure.savefig(buffer, format='png')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        return f'data:image/png;base64,{image_base64}'
    finally:
        plt.close(figure)
        buffer.close()


def _ltst_to_hours(value):
    if not isinstance(value, str) or ':' not in value:
        return None
    try:
        hour_text, minute_text = value.split(':', maxsplit=1)
        hour = int(hour_text)
        minute = int(minute_text)
    except ValueError:
        return None
    if not 0 <= hour < 24 or not 0 <= minute < 60:
        return None
    return hour + minute / 60


def _format_ltst_tick(hours):
    total_minutes = round(hours * 60)
    return f'{total_minutes // 60:02d}:{total_minutes % 60:02d}'

# API views

class WeatherGetApiView(generics.ListAPIView):
    serializer_class = WeatherSerializer

    def get_queryset(self):
        queryset = Weather.objects.all()
        ids = self.request.data.get('ids')
        sols = self.request.data.get('sols')
        terrestrial_dates = self.request.data.get('terrestrial_dates')

        if ids:
            if not isinstance(ids, list):
                raise ValueError("'ids' must be a list of integers")
            if not all(isinstance(id, int) for id in ids):
                raise ValueError("All values in 'ids' must be integers")
            queryset = queryset.filter(id__in=ids)

        if sols:
            if not isinstance(sols, list):
                raise ValueError("'sols' must be a list of integers")
            if not all(isinstance(sol, int) for sol in sols):
                raise ValueError("All values in 'sols' must be integers")
            queryset = queryset.filter(sol__in=sols)

        if terrestrial_dates:
            if not isinstance(terrestrial_dates, list):
                raise ValueError("'terrestrial_dates' must be a list of strings")
            if not all(isinstance(date, str) for date in terrestrial_dates):
                raise ValueError("All values in 'terrestrial_dates' must be strings")
            # Validate date format (YYYY-MM-DD)
            for date in terrestrial_dates:
                try:
                    datetime.strptime(date, '%Y-%m-%d')
                except ValueError:
                    raise ValueError(f"Invalid date format: {date}. Expected format: YYYY-MM-DD")
            queryset = queryset.filter(terrestrial_date__in=terrestrial_dates)

        return queryset

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

