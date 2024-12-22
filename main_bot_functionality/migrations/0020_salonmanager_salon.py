# Generated by Django 5.1.4 on 2024-12-20 18:20

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_bot_functionality', '0019_service_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='salonmanager',
            name='salon',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='salon_managers', to='main_bot_functionality.salon'),
        ),
    ]
