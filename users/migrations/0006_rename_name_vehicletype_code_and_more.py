# Generated by Django 5.0.1 on 2024-03-21 19:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_vehicletype_carrier_vehicle_type'),
    ]

    operations = [
        migrations.RenameField(
            model_name='vehicletype',
            old_name='name',
            new_name='code',
        ),
        migrations.RemoveField(
            model_name='vehicletype',
            name='capacity_cubic_meters',
        ),
        migrations.AddField(
            model_name='vehicletype',
            name='height',
            field=models.FloatField(default=10, help_text='height of vehicle'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='vehicletype',
            name='length',
            field=models.FloatField(default=5, help_text='length of vehicle'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='vehicletype',
            name='weight',
            field=models.FloatField(default=5, help_text='weight'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='vehicletype',
            name='width',
            field=models.FloatField(default=5, help_text='width of vehicle'),
            preserve_default=False,
        ),
    ]
