from rest_framework import serializers

from forum.models import Message


class TopicForm(serializers.ModelSerializer):
    title = serializers.CharField(max_length=100)
    brief = serializers.CharField(max_length=120, allow_blank=True)
    content = serializers.CharField(max_length=None)
    index_pic = serializers.URLField(allow_blank=True)

    class Meta:
        model = Message
        fields = ['content', 'title', 'brief', 'index_pic']


class AnswerTopicForm(serializers.ModelSerializer):
    content = serializers.CharField(max_length=None)
    answer_to_message = serializers.PrimaryKeyRelatedField(queryset=Message.objects,
        allow_null=True, required=False)

    class Meta:
        model = Message
        fields = ['content', 'answer_to_message']