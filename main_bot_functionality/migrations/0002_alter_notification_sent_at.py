# Generated by Django 5.1.4 on 2024-12-18 06:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_bot_functionality', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='sent_at',
            field=models.DateTimeField(),
        ),
    ]
