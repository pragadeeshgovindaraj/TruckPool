# Generated by Django 5.0.1 on 2024-03-24 18:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shipper', '0011_carrierrequest_quote_alter_carrierrequest_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='carrierrequest',
            name='quote',
            field=models.FloatField(),
        ),
    ]
