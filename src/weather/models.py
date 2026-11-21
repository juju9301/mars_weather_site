from django.db import models
from django.urls import reverse

class Weather(models.Model):
    orig_id = models.IntegerField(null=True, blank=True)
    terrestrial_date = models.DateField()
    sol = models.IntegerField(unique=True)
    ls = models.IntegerField(null=True)
    season = models.CharField(max_length=20, null=True)
    min_temp = models.IntegerField(null=True)
    max_temp = models.IntegerField(null=True)
    mean_temp = models.FloatField(null=True, help_text="Mean air temperature in °C.")
    pressure = models.IntegerField(null=True)
    min_pressure = models.FloatField(null=True, help_text="Minimum pressure in Pa.")
    max_pressure = models.FloatField(null=True, help_text="Maximum pressure in Pa.")
    pressure_string = models.CharField(max_length=100, null=True)
    sunrise = models.CharField(max_length=6)
    sunset = models.CharField(max_length=6)
    local_uv_irradiance_index = models.CharField(max_length=20, null=True)
    min_gts_temp = models.IntegerField(null=True)
    max_gts_temp = models.IntegerField(null=True)
    mean_gts_temp = models.FloatField(
        null=True, help_text="Mean ground brightness temperature in °C."
    )
    raw_min_gts_temp = models.FloatField(
        null=True, help_text="Raw minimum ground brightness temperature in °C."
    )
    uv_abc_daylight_mean = models.FloatField(
        null=True, help_text="Daylight mean UV_ABC irradiance in W/m²."
    )
    uv_abc_daylight_peak = models.FloatField(
        null=True, help_text="Daylight peak UV_ABC irradiance in W/m²."
    )
    rems_quality_summary = models.JSONField(default=dict, blank=True)
    # created_at = models.DateTimeField(auto_now_add=True)
    # updated_at = models.DateTimeField(auto_now=True)
    source = models.CharField(max_length=100, default='inta-csic')   

    def get_absolute_url(self):
        return reverse("weather:weather_detail", args=[self.sol])
    
    def __str__(self):
        return f'Sol {self.sol}'

    class Meta:
        ordering = ('-sol',)

