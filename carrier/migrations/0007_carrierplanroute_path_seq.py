# Generated by Django 5.0.1 on 2024-04-04 08:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('carrier', '0006_carrierplanroute'),
    ]

    operations = [
        migrations.AddField(
            model_name='carrierplanroute',
            name='path_seq',
            field=models.JSONField(default=[]),
            preserve_default=False,
        ),
    ]
