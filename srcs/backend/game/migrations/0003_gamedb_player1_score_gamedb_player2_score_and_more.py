# Generated by Django 5.1.1 on 2025-01-30 18:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0002_tmpgamedb'),
    ]

    operations = [
        migrations.AddField(
            model_name='gamedb',
            name='player1_score',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='gamedb',
            name='player2_score',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='tmpgamedb',
            name='player1_score',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='tmpgamedb',
            name='player2_score',
            field=models.IntegerField(default=0),
        ),
    ]
