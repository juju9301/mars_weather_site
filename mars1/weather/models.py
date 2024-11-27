from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Weather(models.Model):
    orig_id = models.IntegerField()
    terrestrial_date = models.CharField(max_length=100)
    sol = models.IntegerField()
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
    
    class Meta:
        ordering = ('-sol',)


class Plot(models.Model):
    image = models.ImageField(upload_to='images/plots/')
    sol_from = models.IntegerField()
    sol_to = models.IntegerField()
    slug = models.SlugField()
    param = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f'{self.sol_from}-{self.sol_to}-{self.param}')
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse("weather:plot", args=[self.slug])
    



