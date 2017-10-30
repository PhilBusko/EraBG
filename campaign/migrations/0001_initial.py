# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2017-07-30 19:25
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('members', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='LiveGame',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Stage', models.CharField(max_length=20, null=True)),
                ('CreateDate', models.DateTimeField(default=django.utils.timezone.now)),
                ('Round', models.IntegerField(default=1)),
                ('PlayerTurn', models.IntegerField(default=0)),
                ('Phase', models.CharField(default='setup', max_length=10)),
                ('FirstPlayer', models.IntegerField(default=0)),
                ('PhaseStart', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='PlayerInGame',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Deck', models.CharField(default='[]', max_length=1000)),
                ('Hand', models.CharField(default='[]', max_length=1000)),
                ('Discard', models.CharField(default='[]', max_length=1000)),
                ('Power', models.CharField(default='', max_length=20)),
                ('LifePnts', models.IntegerField(null=True)),
                ('Status', models.CharField(default='[]', max_length=100)),
                ('RosterFK', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='members.UserDeck')),
                ('UserFK', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Progress',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('NextStage', models.CharField(default='stage 1', max_length=20)),
                ('UserFK', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='livegame',
            name='Player1FK',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='campaign.PlayerInGame'),
        ),
        migrations.AddField(
            model_name='livegame',
            name='Player2FK',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='campaign.PlayerInGame'),
        ),
    ]