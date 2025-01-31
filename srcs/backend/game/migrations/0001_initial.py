# Generated by Django 5.1.1 on 2025-01-30 10:53

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='GameDB',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('room_id', models.CharField(max_length=1000)),
                ('player1_id', models.CharField(max_length=1000)),
                ('player2_id', models.CharField(max_length=1000)),
                ('winner_id', models.CharField(max_length=1000)),
                ('create_date', models.CharField(max_length=1000)),
                ('end_date', models.CharField(max_length=1000)),
            ],
        ),
    ]
