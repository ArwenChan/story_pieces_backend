# -*- coding: utf-8 -*-
from django.contrib import admin
from .models import Message, Likes
# Register your models here.

admin.site.register(Message)
admin.site.register(Likes)