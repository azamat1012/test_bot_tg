# Generated by Django 5.1.4 on 2024-12-20 16:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_bot_functionality', '0018_salon_tg_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='service',
            name='name',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
