# Generated by Django 2.0.7 on 2018-11-23 05:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0004_auto_20181122_1528'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='message',
            options={'verbose_name': '帖子', 'verbose_name_plural': '帖子'},
        ),
    ]
