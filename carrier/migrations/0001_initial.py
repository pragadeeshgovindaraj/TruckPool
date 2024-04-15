# Generated by Django 5.0.1 on 2024-02-01 12:17

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CarrierPlan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_of_plan', models.DateField()),
                ('start_location', models.CharField(max_length=255)),
                ('start_address', models.CharField(max_length=255)),
                ('end_location', models.CharField(max_length=255)),
                ('end_address', models.CharField(max_length=255)),
                ('space_available', models.FloatField(help_text='Space available in van in cubic meters')),
                ('desired_rate', models.DecimalField(decimal_places=4, help_text='Desired rate per cubic meter', max_digits=10)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]