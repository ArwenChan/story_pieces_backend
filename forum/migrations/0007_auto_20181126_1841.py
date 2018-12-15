# Generated by Django 2.0.7 on 2018-11-26 10:41

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('forum', '0006_auto_20181126_1603'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='likes',
            options={'verbose_name': '点赞', 'verbose_name_plural': '点赞'},
        ),
        migrations.RemoveField(
            model_name='message',
            name='answer_to_user',
        ),
        migrations.AlterUniqueTogether(
            name='likes',
            unique_together={('message', 'user')},
        ),
    ]