# Generated by Django 2.0.7 on 2018-12-05 02:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0009_auto_20181128_1702'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='update_time',
            field=models.DateTimeField(auto_now=True, verbose_name='最后更新时间'),
        ),
    ]
