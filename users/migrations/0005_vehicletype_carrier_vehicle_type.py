# Generated by Django 5.0.1 on 2024-02-01 12:17

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_remove_shipperindividualuser_groups_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='VehicleType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.TextField()),
                ('capacity_cubic_meters', models.FloatField(help_text='Capacity in cubic meters')),
            ],
        ),
        migrations.AddField(
            model_name='carrier',
            name='vehicle_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='users.vehicletype'),
        ),
    ]
