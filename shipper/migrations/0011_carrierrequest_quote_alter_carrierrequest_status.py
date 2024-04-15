# Generated by Django 5.0.1 on 2024-03-24 17:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shipper', '0010_carrierrequest_carrier_plan'),
    ]

    operations = [
        migrations.AddField(
            model_name='carrierrequest',
            name='quote',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='carrierrequest',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected'), ('paid', 'paid'), ('completed', 'completed')], default='pending', max_length=20),
        ),
    ]