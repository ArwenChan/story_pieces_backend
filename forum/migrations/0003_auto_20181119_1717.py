# Generated by Django 2.0.7 on 2018-11-19 09:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0002_auto_20181119_1437'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='clicks_num',
            field=models.PositiveIntegerField(default=0, verbose_name='点击数'),
        ),
        migrations.AddField(
            model_name='message',
            name='index_pic',
            field=models.URLField(blank=True, verbose_name='展示图'),
        ),
        migrations.AddField(
            model_name='message',
            name='likes_num',
            field=models.PositiveIntegerField(default=0, verbose_name='点赞数'),
        ),
    ]
