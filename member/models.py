import logging
from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.contrib.postgres.fields import ArrayField
from django.db.models import F
from django.db.transaction import atomic

from sentry_sdk import capture_exception
from story_pieces.base.utils import uuid4_hex

logger = logging.getLogger('django')

GROUP_STATUS = (
    ('verifying', '审核中'),
    ('normal', '使用中'),
)

GROUP_ROLE = (
    ('user', '组员'),
    ('create_user', '组长'),
    ('manager', '管理员')
)


class UserGroupManager(models.Manager):
    @atomic
    def create_group(self, create_user, **kwargs):
        try:
            group = self.create(**kwargs)
            UserInGroup.objects.add_user(create_user, group, role='create_user')
            group.refresh_from_db()
            return group
        except Exception as e:
            capture_exception(e)
            return None

    def update_group(self, group, **kwargs):
        group.name = kwargs.get('name', group.name)
        group.brief = kwargs.get('brief', group.brief)
        group.icon = kwargs.get('icon', group.icon)
        group.tags = kwargs.get('tags', group.tags)
        group.save()


class UserGroup(models.Model):
    name = models.CharField('小组名', max_length=30)
    icon = models.URLField('头像')
    brief = models.TextField('简介')
    tags = ArrayField(models.CharField(max_length=10), size=5, verbose_name='标签', blank=True)
    count = models.PositiveIntegerField('人数', default=0, editable=False)
    heat = models.PositiveIntegerField('热度', default=0)
    status = models.CharField(choices=GROUP_STATUS, default='verifying', max_length=10)
    create_time = models.DateTimeField('创建时间', auto_now_add=True)

    objects = UserGroupManager()

    class Meta:
        verbose_name = '小组'
        verbose_name_plural = '小组'

    def __str__(self):
        return self.name

    @property
    def create_user(self):
        the_member_ship = UserInGroup.objects.filter(group=self, role='create_user').first()
        if the_member_ship:
            return the_member_ship.user
        return None


class MyUserManager(UserManager):
    def create_user(self, mobile, password, nickname=''):
        try:
            nickname = nickname if nickname else mobile
            user = User(
                username=uuid4_hex(),
                mobile=mobile,
                nickname=nickname,
            )
            user.set_password(password)
            user.save()
            return user
        except Exception as e:
            capture_exception(e)
            return None


class User(AbstractUser):
    nickname = models.CharField('昵称', max_length=50, blank=True)
    mobile = models.CharField('电话', max_length=11, unique=True)
    avatar = models.URLField('用户头像', blank=True)
    country = models.CharField('国家', blank=True, max_length=20)
    province = models.CharField('省份', blank=True, max_length=20)
    city = models.CharField('城市', blank=True, max_length=20)
    member_groups = models.ManyToManyField(UserGroup, through='UserInGroup', related_name='members')

    objects = MyUserManager()

    def __str__(self):
        if self.nickname:
            return self.nickname
        return self.username


class UserInGroupManager(models.Manager):
    @atomic
    def add_user(self, user, group, role='user', is_invite=False):
        self.create(user=user, group=group, role=role, is_invite=is_invite)
        group.count = F('count') + 1
        group.save()

    @atomic
    def remove_user(self, user, group):
        self.filter(user=user, group=group).delete()
        group.count = F('count') - 1
        group.save()


class UserInGroup(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(UserGroup, on_delete=models.CASCADE)
    date_joined = models.DateField('加入时间', auto_now_add=True)
    is_invite = models.BooleanField('是否邀请加入', default=False)
    role = models.CharField('角色', choices=GROUP_ROLE, default='user',
        db_index=True, max_length=15)

    objects = UserInGroupManager()

    class Meta:
        verbose_name = '组员关系'
        verbose_name_plural = '组员关系'
        unique_together = [('user', 'group'),]

