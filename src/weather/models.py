from django.db import models
from django.urls import reverse

class Weather(models.Model):
    orig_id = models.IntegerField()
    terrestrial_date = models.DateField()
    sol = models.IntegerField(unique=True)
    ls = models.IntegerField(null=True)
    season = models.CharField(max_length=20, null=True)
    min_temp = models.IntegerField(null=True)
    max_temp = models.IntegerField(null=True)
    pressure = models.IntegerField(null=True)
    pressure_string = models.CharField(max_length=100, null=True)
    abs_humidity = models.CharField(max_length=100, null=True)
    wind_speed = models.CharField(max_length=20, null=True)
    wind_direction = models.CharField(max_length=100, null=True)
    atmo_opacity = models.CharField(max_length=20, null=True)
    sunrise = models.CharField(max_length=6)
    sunset = models.CharField(max_length=6)
    local_uv_irradiance_index = models.CharField(max_length=20, null=True)
    min_gts_temp = models.IntegerField(null=True)
    max_gts_temp = models.IntegerField(null=True)
    # created_at = models.DateTimeField(auto_now_add=True)
    # updated_at = models.DateTimeField(auto_now=True)
    source = models.CharField(max_length=100, default='inta-csic')   

    def get_absolute_url(self):
        return reverse("weather:weather_detail", args=[self.sol])
    
    def __str__(self):
        return f'Sol {self.sol}'

    class Meta:
        ordering = ('-sol',)

