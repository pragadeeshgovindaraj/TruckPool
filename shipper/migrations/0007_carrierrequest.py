# Generated by Django 5.0.1 on 2024-03-03 12:46

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shipper', '0006_alter_shipment_shipper_user'),
        ('users', '0005_vehicletype_carrier_vehicle_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='CarrierRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')], default='pending', max_length=20)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('carrier', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.carrier')),
                ('shipment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shipper.shipment')),
            ],
        ),
    ]