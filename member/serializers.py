from rest_framework import serializers

from .models import UserGroup, User, UserInGroup


class Userserializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'nickname', 'avatar', 'city']

class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'nickname', 'avatar', 'mobile', 'country', 'province', 'city', 'member_groups']

class UserGroupListSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserGroup
        fields = ('id', 'name', 'icon', 'count', 'status')

class UserGroupSerializer(serializers.ModelSerializer):
    create_user = Userserializer()
    create_time = serializers.DateTimeField()
    class Meta:
        model = UserGroup
        fields = ('id', 'name', 'icon', 'brief', 'count', 'tags', 'create_user', 'status', 'create_time')


class GroupUsersSerializer(serializers.ModelSerializer):
    user = Userserializer()
    class Meta:
        model = UserInGroup
        fields = ['user', 'role']
