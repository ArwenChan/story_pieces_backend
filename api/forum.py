from django.db import IntegrityError
from django.db.models import Q
from rest_framework.decorators import action

from forum.forms import TopicForm, AnswerTopicForm
from forum.models import Message, Likes
from forum.serializers import HotTopicsSerializer, TopicDetailSerializer, AnswerSerializer, TopicsSimpleSerializer
from member.models import UserGroup, UserInGroup
from member.serializers import UserGroupListSerializer, UserGroupSerializer, GroupUsersSerializer, UserDetailSerializer
from member.forms import UserGroupForm
from story_pieces.base.exceptions import BusinessException
from story_pieces.base.utils import success_rsp, check_or_business_error
from story_pieces.base.views import AnonyViewSet, AuthViewSet
from .tasks import raise_heat, add_likes, add_answers


class TopicsViewSet(AnonyViewSet):
    serializer_class = HotTopicsSerializer
    queryset = Message.objects

    def list(self, request):
        query = request.query_params.get('q')
        q = Q(is_topic=True)
        if query:
            q = q & Q(title__contains=query)

        messages = self.get_queryset().filter(q).order_by('-heat', '-create_time')
        page = self.paginate_queryset(messages)
        data = self.get_serializer(page, many=True).data
        return self.get_paginated_response(data)


    def retrieve(self, request, *args, **kwargs):
        topic = self.get_object()
        page_replies = self.paginate_queryset(topic.replies.all().order_by('create_time'))
        topic_data = TopicDetailSerializer(topic).data
        replies_data = AnswerSerializer(page_replies, many=True).data
        replies_data = {
                'count': self.paginator.page.paginator.count,
                'data': replies_data
        }
        like_data = []
        if request.user.is_authenticated:
            q = Q(message=topic) | Q(message__in=page_replies)
            like_data = request.user.likes_set.filter(q).values_list('message', flat=True)

        ret = {
            'topic': topic_data,
            'replies': replies_data,
            'likes': like_data
        }
        return success_rsp(ret)


class MyTopicsViewSet(AuthViewSet):
    queryset = Message.objects

    def get_serializer_class(self):
        if self.query_type == 'hot':
            return HotTopicsSerializer
        return TopicsSimpleSerializer

    def _my_group_topics(self, request):
        messages = self.get_queryset().filter(is_topic=True,
            group__in=request.user.member_groups.all()).order_by('-heat', '-create_time')
        return self.paginate_queryset(messages)

    def _my_create_topics(self, request):
        messages = self.get_queryset().filter(is_topic=True,
            create_user=request.user).order_by('-heat', '-create_time')
        return self.paginate_queryset(messages)

    def _my_answer_topics(self, request):
        messages = self.get_queryset().filter(create_user=request.user,
            is_topic=False, answer_to_topic__isnull=False).order_by('-heat', '-create_time')
        messages = messages.order_by(
                '-answer_to_topic').distinct('answer_to_topic')
        query_messages = self.paginate_queryset(messages)
        query_messages = [message.answer_to_topic for message in query_messages]
        return query_messages

    def _my_like_topics(self, request):
        likes = Likes.objects.filter(user=request.user, message__is_topic=True).order_by('-create_time')
        likes = self.paginate_queryset(likes)
        topics = [like.message for like in likes]
        return topics

    def list(self, request):
        q_map = {
            'my_group': self._my_group_topics,
            'my_create': self._my_create_topics,
            'my_reply': self._my_answer_topics,
            'my_like': self._my_like_topics,
        }
        self.query_type = request.query_params.get('type', '')
        query_func = q_map.get(request.query_params.get('filter', 'my_group'))

        query_messages = query_func(request)

        data = self.get_serializer(query_messages, many=True).data
        return self.get_paginated_response(data)


    @action(detail=True, url_path='answer-topic', methods=['POST'])
    def answer_topic(self, request, *args, **kwargs):
        topic = self.get_object()
        form = AnswerTopicForm(data=request.data)
        check_or_business_error(form.is_valid(), '1000', error_data=form.errors)
        answer_message = form.validated_data.get('answer_to_message')
        if answer_message:
            check_or_business_error(answer_message.answer_to_topic == topic, '1012')
        answer = form.save(create_user=request.user, answer_to_topic=topic,
            group=topic.group, is_topic=False)
        data = AnswerSerializer(answer).data

        add_answers.delay(topic.id)
        raise_heat.delay(topic.id, 'Message', 2)
        return success_rsp(data)

    @action(detail=True, methods=['POST'])
    def like(self, request, *args, **kwargs):
        message = self.get_object()
        try:
            Likes.objects.create(message=message, user=request.user)
            add_likes.delay(message.id)
            raise_heat.delay(message.id, 'Message', 1)
        except IntegrityError as e:
            raise BusinessException('1011')
        return success_rsp()



class GroupsViewSet(AnonyViewSet):
    queryset = UserGroup.objects

    def get_serializer_class(self):
        if self.action == 'list':
            return UserGroupListSerializer
        return UserGroupSerializer

    def list(self, request):
        query = request.query_params.get('q')
        groups = self.get_queryset().filter(status='normal')
        if query:
            q = Q(tags__contains=[query]) | Q(name__contains=query)
            groups = groups.filter(q)

        groups = groups.order_by('-heat')
        query_groups = self.paginate_queryset(groups)
        data = UserGroupListSerializer(query_groups, many=True).data
        return self.get_paginated_response(data)

    def retrieve(self, request, *args, **kwargs):
        group = self.get_object()
        data = self.get_serializer(group).data

        raise_heat.delay(group.id, 'UserGroup', 1)
        return success_rsp(data)

    @action(detail=True, url_path='group-users', methods=['GET'])
    def group_users(self, request, *args, **kwargs):
        group = self.get_object()
        members = UserInGroup.objects.filter(group=group).order_by('role', '-date_joined')
        page_members = self.paginate_queryset(members)
        data = GroupUsersSerializer(page_members, many=True).data
        return self.get_paginated_response(data)

    @action(detail=True, url_path='group-topics', methods=['GET'])
    def group_topics(self, request, *args, **kwargs):
        group = self.get_object()
        order_by_query = request.query_params.get('order', '-create_time')
        topics = Message.objects.filter(is_topic=True, group=group)
        if order_by_query in ('create_time', 'heat'):
            order = '-' + order_by_query
            topics = topics.order_by(order)
        page_topics = self.paginate_queryset(topics)
        data = TopicsSimpleSerializer(page_topics, many=True).data
        return self.get_paginated_response(data)


class MyGroupsViewSet(AuthViewSet):
    queryset = UserGroup.objects

    def get_serializer_class(self):
        if self.action == 'list':
            return UserGroupListSerializer
        return UserGroupSerializer

    def list(self, request):
        groups = request.user.member_groups.order_by('-heat')
        query_groups = self.paginate_queryset(groups)
        data = self.get_serializer(query_groups, many=True).data
        return self.get_paginated_response(data)

    def create(self, request, *args, **kwargs):
        form = UserGroupForm(data=request.data)
        check_or_business_error(form.is_valid(), '1000', error_data=form.errors)
        group = UserGroup.objects.create_group(request.user, **form.validated_data)
        check_or_business_error(group is not None, '1007')
        data = self.get_serializer(group).data
        return success_rsp(data)

    def update(self, request, *args, **kwargs):
        group = self.get_object()
        check_or_business_error(group.create_user == request.user, '1008')
        form = UserGroupForm(data=request.data, partial=True)
        check_or_business_error(form.is_valid(), '1000', error_data=form.errors)
        UserGroup.objects.update_group(group, **form.validated_data)
        return success_rsp()

    @action(detail=True, methods=['POST'], url_path='add-user')
    def add_user(self, request, *args, **kwargs):
        group = self.get_object()
        UserInGroup.objects.add_user(request.user, group)

        raise_heat.delay(group.id, 'UserGroup', 1)
        request.user.refresh_from_db()
        ret = UserDetailSerializer(request.user).data
        return success_rsp(ret)

    @action(detail=True, methods=['POST'], url_path='remove-user')
    def remove_user(self, request, *args, **kwargs):
        group = self.get_object()
        UserInGroup.objects.remove_user(request.user, group)

        request.user.refresh_from_db()
        ret = UserDetailSerializer(request.user).data
        return success_rsp(ret)

    @action(detail=True, methods=['POST'], url_path='add-topic')
    def add_topic(self, request, *args, **kwargs):
        group = self.get_object()
        check_or_business_error(group in request.user.member_groups.all(), '1010')
        form = TopicForm(data=request.data)
        check_or_business_error(form.is_valid(), '1000', error_data=form.errors)
        topic = form.save(group=group, create_user=request.user, is_topic=True)
        data = TopicDetailSerializer(topic).data

        raise_heat.delay(group.id, 'UserGroup', 2)
        return success_rsp(data)