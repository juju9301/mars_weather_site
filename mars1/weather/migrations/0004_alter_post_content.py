# Generated by Django 5.1.3 on 2024-12-24 14:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('weather', '0003_post'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='content',
            field=models.CharField(blank=True, max_length=280, null=True),
        ),
    ]
