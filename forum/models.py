# -*- coding: utf-8 -*-
from django.db import models

from member.models import User, UserGroup


class Message(models.Model):
    group = models.ForeignKey(UserGroup, on_delete=models.CASCADE,
        verbose_name='小组')
    content = models.TextField('内容')
    brief = models.CharField('简介', blank=True, max_length=120)
    create_user = models.ForeignKey(User, on_delete=models.SET_NULL,
        null=True, verbose_name='留言人')
    create_time = models.DateTimeField('创建时间', auto_now_add=True)
    update_time = models.DateTimeField('最后更新时间', auto_now=True)
    is_topic = models.BooleanField('是否话题')
    title = models.CharField('标题', max_length=100, blank=True)
    answer_to_message = models.ForeignKey('self', verbose_name='回应的帖子',
        on_delete=models.CASCADE, null=True, related_name='answers', blank=True)
    answer_to_topic = models.ForeignKey('self', verbose_name='回应的话题',
        on_delete=models.CASCADE, null=True, related_name='replies', blank=True)
    heat = models.PositiveIntegerField('热度', default=0)
    likes_num = models.PositiveIntegerField('点赞数', default=0)
    answers_num = models.PositiveIntegerField('回应数', default=0)
    index_pic = models.URLField('展示图', blank=True)


    class Meta:
        verbose_name = '帖子'
        verbose_name_plural = '帖子'


    def __str__(self):
        if self.is_topic:
            return self.title
        return self.content[:15]


class Likes(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE,
        verbose_name='帖子')
    user = models.ForeignKey(User, on_delete=models.SET_NULL,
        null=True, verbose_name='点赞人')
    create_time = models.DateTimeField('创建时间', auto_now_add=True)

    def __str__(self):
        return 'like ' + str(self.message)

    class Meta:
        verbose_name = '点赞'
        verbose_name_plural = '点赞'
        unique_together = [('message', 'user'),]
