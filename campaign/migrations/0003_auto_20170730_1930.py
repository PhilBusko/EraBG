# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2017-07-30 19:30
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('campaign', '0002_auto_20170730_1928'),
    ]

    operations = [
        migrations.AlterField(
            model_name='livegame',
            name='Player1FK',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='player_one', to='campaign.PlayerInGame'),
        ),
        migrations.AlterField(
            model_name='livegame',
            name='Player2FK',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='player_two', to='campaign.PlayerInGame'),
        ),
        migrations.AlterField(
            model_name='playeringame',
            name='UserFK',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='progress',
            name='UserFK',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
