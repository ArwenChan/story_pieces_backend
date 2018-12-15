# Generated by Django 2.0.7 on 2018-11-22 07:28

import django.contrib.postgres.fields
from django.db import migrations, models
import member.models


class Migration(migrations.Migration):

    dependencies = [
        ('member', '0002_auto_20181119_1717'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='user',
            managers=[
                ('objects', member.models.MyUserManager()),
            ],
        ),
        migrations.AddField(
            model_name='user',
            name='city',
            field=models.CharField(blank=True, max_length=20, verbose_name='城市'),
        ),
        migrations.AddField(
            model_name='user',
            name='country',
            field=models.CharField(blank=True, max_length=20, verbose_name='国家'),
        ),
        migrations.AddField(
            model_name='user',
            name='province',
            field=models.CharField(blank=True, max_length=20, verbose_name='省份'),
        ),
        migrations.AddField(
            model_name='usergroup',
            name='heat',
            field=models.PositiveIntegerField(default=0, verbose_name='热度'),
        ),
        migrations.AddField(
            model_name='usergroup',
            name='tags',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=10), blank=True, default=[], size=5, verbose_name='标签'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='user',
            name='mobile',
            field=models.CharField(max_length=11, unique=True, verbose_name='电话'),
        ),
        migrations.AlterField(
            model_name='usergroup',
            name='count',
            field=models.PositiveIntegerField(default=1, editable=False, verbose_name='人数'),
        ),
    ]
