from rest_framework import serializers

from member.serializers import Userserializer, UserGroupListSerializer
from .models import Message


class HotTopicsSerializer(serializers.ModelSerializer):
    group = serializers.SlugField('name')
    class Meta:
        model = Message
        fields = ('id', 'title', 'brief', 'group', 'create_time', 'likes_num')

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if instance.index_pic:
            ret['index_pic'] = instance.index_pic
        return ret


class TopicsSimpleSerializer(serializers.ModelSerializer):
    group = serializers.SlugField('name')
    create_user = serializers.SlugField('nickname')
    class Meta:
        model = Message
        fields = ('id', 'title', 'group', 'answers_num', 'create_time', 'update_time', 'create_user')


class RecursiveField(serializers.Serializer):
    def to_representation(self, value):
        serializer_class = self.parent.parent.__class__
        serializer_class.fields = ('id', 'content', 'create_time', 'likes_num', 'create_user')
        serializer = serializer_class(value, context=self.context)
        return serializer.data


class AnswerInSerializer(serializers.ModelSerializer):
    create_user = serializers.SlugField('nickname')
    class Meta:
        model = Message
        fields = ('id', 'content', 'create_user')


class AnswerSerializer(serializers.ModelSerializer):
    create_user = Userserializer()
    answer_to_message = AnswerInSerializer()
    class Meta:
        model = Message
        fields = ('id', 'content', 'create_time', 'likes_num', 'create_user', 'answer_to_message')



class TopicDetailSerializer(serializers.ModelSerializer):
    create_user = Userserializer()
    group = UserGroupListSerializer()
    class Meta:
        model = Message
        fields = ('id', 'title', 'content', 'create_time', 'likes_num', 'group', 'create_user')
