import json
import logging

from django.core.cache import cache
from mock import mock
from parameterized import parameterized
from django.contrib.auth import SESSION_KEY

from member.models import User, UserInGroup, UserGroup
from story_pieces.base.test_base import BaseAPITestCase
from story_pieces.base.utils import SMSClient
from member.factories import UserFactory, UserGroupFactory
from forum.factories import MessageFactory, LikesFactory

logger = logging.getLogger('django')



class TopicsAPITestCase(BaseAPITestCase):
    def setUp(self):
        super().setUp()
        self.url = '/api/forum/topics/'
        self.user = UserFactory(password='test')
        self.group1 = UserGroupFactory(create_user=self.user)
        self.group2 = UserGroupFactory(create_user=self.user)

    def test_get_topics_list(self):
        topics1 = MessageFactory.create_batch(3, create_user=self.user, group=self.group1, is_topic=True)
        topics2 = MessageFactory.create_batch(3, create_user=self.user, group=self.group2, is_topic=True)
        not_topics = MessageFactory.create_batch(4, create_user=self.user, group=self.group1, is_topic=False)
        rsp = self.client.get(self.url)
        self.assertResponseRaiseCode(rsp, '0')
        self.assertEqual(rsp.data['result']['count'], 6)

    def test_search_topics_with_q(self):
        topics1 = MessageFactory.create_batch(3, create_user=self.user, group=self.group1, is_topic=True, title='abcd')
        topics2 = MessageFactory.create_batch(3, create_user=self.user, group=self.group2, is_topic=True)
        not_topics = MessageFactory.create_batch(4, create_user=self.user, group=self.group1, is_topic=False)
        url = self.url + '?q=ab&size=2'
        rsp = self.client.get(url)
        self.assertResponseRaiseCode(rsp, '0')
        self.assertEqual(rsp.data['result']['count'], 3)
        self.assertEqual(len(rsp.data['result']['data']), 2)

    def test_retrieve_topic(self):
        out = self.client.login(username=self.user.mobile, password='test')
        topic = MessageFactory(create_user=self.user, group=self.group1, is_topic=True)
        reply = MessageFactory(create_user=self.user, group=self.group1, is_topic=False, answer_to_topic=topic)
        LikesFactory(user=self.user, message=topic)
        url = self.url + str(topic.id) + '/'
        rsp = self.client.get(url)
        self.assertResponseRaiseCode(rsp, '0')
        self.assertEqual(len(rsp.data['result']['likes']), 1)
        self.assertEqual(rsp.data['result']['likes'][0], topic.id)
        # print(rsp.content)


class MyTopicsAPITestCase(BaseAPITestCase):
    def setUp(self):
        super().setUp()
        self.url = '/api/forum/topics/my/'
        self.user = UserFactory(password='test')
        self.group = UserGroupFactory(create_user=self.user)

    def test_get_my_group_topics(self):
        self.client.login(username=self.user.mobile, password='test')
        other_user = UserFactory()
        group1 = UserGroupFactory(create_user=other_user)
        group2 = UserGroupFactory(create_user=other_user)
        UserInGroup.objects.add_user(self.user, group1)
        my_topics = MessageFactory.create_batch(3, create_user=self.user, group=self.group, is_topic=True)
        my_group_topics = MessageFactory.create_batch(3, create_user=other_user, group=group1, is_topic=True)
        not_topics = MessageFactory.create_batch(4, create_user=self.user, group=self.group, is_topic=False)
        not_my_topics = MessageFactory.create_batch(5, create_user=other_user, group=group2, is_topic=True)
        url = self.url + '?filter=my_group'
        rsp = self.client.get(url)
        self.assertResponseRaiseCode(rsp, '0')
        self.assertEqual(rsp.data['result']['count'], 6)

    def test_get_my_create_topics(self):
        self.client.login(username=self.user.mobile, password='test')
        other_user = UserFactory()
        UserInGroup.objects.add_user(other_user, self.group)
        my_topics = MessageFactory.create_batch(3, create_user=self.user, group=self.group, is_topic=True)
        my_group_topics = MessageFactory.create_batch(3, create_user=other_user, group=self.group, is_topic=True)
        not_topics = MessageFactory.create_batch(4, create_user=self.user, group=self.group, is_topic=False)
        url = self.url + '?filter=my_create'
        rsp = self.client.get(url)
        self.assertResponseRaiseCode(rsp, '0')
        self.assertEqual(rsp.data['result']['count'], 3)

    def test_get_my_reply_topics(self):
        self.client.login(username=self.user.mobile, password='test')
        other_user = UserFactory()
        UserInGroup.objects.add_user(other_user, self.group)
        my_group_topics = MessageFactory.create_batch(4, create_user=other_user, group=self.group, is_topic=True)
        my_answer1 = MessageFactory.create_batch(3, create_user=self.user, group=self.group,
            is_topic=False, answer_to_topic=my_group_topics[0])
        my_answer2 = MessageFactory.create_batch(3, create_user=self.user, group=self.group,
            is_topic=False, answer_to_topic=my_group_topics[1])
        not_topics = MessageFactory.create_batch(4, create_user=self.user, group=self.group, is_topic=False)
        url = self.url + '?filter=my_reply'
        rsp = self.client.get(url)
        self.assertResponseRaiseCode(rsp, '0')
        self.assertEqual(rsp.data['result']['count'], 2)
        self.assertEqual(rsp.data['result']['data'][0]['id'], my_group_topics[1].id)

    def test_get_my_like_topics(self):
        self.client.login(username=self.user.mobile, password='test')
        other_user = UserFactory()
        UserInGroup.objects.add_user(other_user, self.group)

        topics = MessageFactory.create_batch(3, create_user=other_user, group=self.group,
            is_topic=True)
        non_topics = MessageFactory.create_batch(4, create_user=other_user, group=self.group,
            is_topic=False)
        LikesFactory(user=self.user, message=topics[1])
        LikesFactory(user=self.user, message=topics[0])
        LikesFactory(user=self.user, message=non_topics[0])
        LikesFactory(user=other_user, message=topics[2])
        url = self.url + '?filter=my_like'
        rsp = self.client.get(url)
        self.assertResponseRaiseCode(rsp, '0')
        self.assertEqual(rsp.data['result']['count'], 2)
        self.assertEqual(rsp.data['result']['data'][0]['id'], topics[0].id)

    def test_answer_topic_success(self):
        self.client.login(username=self.user.mobile, password='test')
        topic = MessageFactory.create(create_user=self.user, group=self.group, is_topic=True)
        url = self.url + str(topic.id) + '/answer-topic/'
        content = '你说的不对'
        data = {
            'content': content
        }
        rsp = self.client.post(url, data=data, format='json')
        self.assertResponseRaiseCode(rsp, '0')
        self.assertEqual(rsp.data['result']['content'], content)

    def test_answer_topic_with_message_fail_wrong_message_and_topic(self):
        self.client.login(username=self.user.mobile, password='test')
        topic = MessageFactory.create(create_user=self.user, group=self.group, is_topic=True)
        message = MessageFactory.create(create_user=self.user, group=self.group, is_topic=False)
        url = self.url + str(topic.id) + '/answer-topic/'
        content = '你说的不对'
        data = {
            'content': content,
            'answer_to_message': message.id
        }
        rsp = self.client.post(url, data=data, format='json')
        self.assertResponseRaiseCode(rsp, '1012')

    def test_answer_topic_with_message_success(self):
        self.client.login(username=self.user.mobile, password='test')
        topic = MessageFactory.create(create_user=self.user, group=self.group, is_topic=True)
        message = MessageFactory.create(create_user=self.user, group=self.group, is_topic=False, answer_to_topic=topic)
        url = self.url + str(topic.id) + '/answer-topic/'
        content = '你说的不对'
        data = {
            'content': content,
            'answer_to_message': message.id
        }
        rsp = self.client.post(url, data=data, format='json')
        self.assertResponseRaiseCode(rsp, '0')
        self.assertEqual(rsp.data['result']['content'], content)

    def test_like_message_fail_already_likes(self):
        self.client.login(username=self.user.mobile, password='test')
        topic = MessageFactory.create(create_user=self.user, group=self.group, is_topic=True)
        LikesFactory(user=self.user, message=topic)
        url = self.url + str(topic.id) + '/like/'
        rsp = self.client.post(url)
        self.assertResponseRaiseCode(rsp, '1011')

    def test_like_message_success(self):
        self.client.login(username=self.user.mobile, password='test')
        topic = MessageFactory.create(create_user=self.user, group=self.group, is_topic=True)
        url = self.url + str(topic.id) + '/like/'
        rsp = self.client.post(url)
        self.assertResponseRaiseCode(rsp, '0')


class GroupsAPITestCase(BaseAPITestCase):
    def setUp(self):
        super().setUp()
        self.url = '/api/forum/groups/'

    def test_get_groups_list(self):
        groups1 = UserGroupFactory.create_batch(3, heat=1)
        groups2 = UserGroupFactory.create_batch(3, heat=2)
        rsp = self.client.get(self.url)
        self.assertResponseRaiseCode(rsp, '0')
        self.assertEqual(rsp.data['result']['count'], 6)

    def test_search_groups_with_q(self):
        groups1 = UserGroupFactory.create_batch(4, heat=1, tags=['小说', 'abc', '大家好'])
        groups2 = UserGroupFactory.create_batch(3, heat=2, tags=['哦哦', '气质'])
        groups3 = UserGroupFactory(heat=1, name='小说那么长')
        url = self.url + '?q=小说'
        rsp = self.client.get(url)
        self.assertResponseRaiseCode(rsp, '0')
        self.assertEqual(rsp.data['result']['count'], 5)

    def test_retrieve_group(self):
        group = UserGroupFactory()
        url = self.url + str(group.id) + '/'
        rsp = self.client.get(url)
        self.assertResponseRaiseCode(rsp, '0')
        self.assertEqual(rsp.data['result']['id'], group.id)

    def test_get_group_users(self):
        user1 = UserFactory()
        user2 = UserFactory()
        user3 = UserFactory()
        group = UserGroupFactory(create_user=user1)
        UserInGroup.objects.add_user(user2, group)
        url = self.url + str(group.id) + '/group-users/'
        rsp = self.client.get(url)
        self.assertResponseRaiseCode(rsp, '0')
        self.assertEqual(rsp.data['result']['count'], 2)



class MyGroupsAPITestCase(BaseAPITestCase):
    def setUp(self):
        super().setUp()
        self.url = '/api/forum/groups/my/'
        self.user = UserFactory(password='test')

    def test_get_groups_list(self):
        self.client.login(username=self.user.mobile, password='test')
        groups1 = UserGroupFactory.create_batch(4, create_user=self.user)
        groups2 = UserGroupFactory.create_batch(3, heat=2)
        groups3 = UserGroupFactory.create_batch(2, heat=2)
        UserInGroup.objects.add_user(self.user, groups2[1])
        rsp = self.client.get(self.url)
        self.assertResponseRaiseCode(rsp, '0')
        self.assertEqual(rsp.data['result']['count'], 5)

    @parameterized.expand([
        ({},),
        ({'name': '123', 'brief': 123, 'tags': ['nihao']},),
        ({'name': '123', 'brief': 123, 'tags': ['nihao'], 'icon': 'not link'},),
    ])
    def test_create_group_with_invalid_params(self, data):
        self.client.login(username=self.user.mobile, password='test')
        rsp = self.client.post(self.url, data=data, format='json')
        self.assertResponseRaiseCode(rsp, '1000')

    def test_create_group_success(self):
        self.client.login(username=self.user.mobile, password='test')
        data = {
            'name': '123',
            'brief': '123',
            'icon': 'http://www.img.com',
            'tags': ['haha', '他们']
        }
        rsp = self.client.post(self.url, data=data, format='json')
        self.assertResponseRaiseCode(rsp, '0')
        group = UserGroup.objects.filter(name='123').first()
        self.assertIsNotNone(group)
        self.assertEqual(rsp.data['result']['name'], '123')

    def test_update_group_has_no_perm(self):
        self.client.login(username=self.user.mobile, password='test')
        group = UserGroupFactory()
        url = self.url + str(group.id) + '/'
        data = {
            'brief': 'wooo'
        }
        rsp = self.client.put(url, data=data, format='json')
        self.assertResponseRaiseCode(rsp, '1008')

    def test_update_group_success(self):
        self.client.login(username=self.user.mobile, password='test')
        group = UserGroupFactory(create_user=self.user)
        url = self.url + str(group.id) + '/'
        data = {
            'brief': 'wooo'
        }
        rsp = self.client.put(url, data=data, format='json')
        self.assertResponseRaiseCode(rsp, '0')

    def test_add_user_to_group(self):
        self.client.login(username=self.user.mobile, password='test')
        group = UserGroupFactory()
        url = self.url + str(group.id) + '/add-user/'
        rsp = self.client.post(url)
        self.assertResponseRaiseCode(rsp, '0')
        self.assertTrue(group in self.user.member_groups.all())

    def test_add_topic_to_group_raise_1010_when_not_group_member(self):
        self.client.login(username=self.user.mobile, password='test')
        group = UserGroupFactory()
        url = self.url + str(group.id) + '/add-topic/'
        content = '哟哟呀我黑'
        data = {
            'title': 'lala拉',
            'content': content,
            'index_pic': 'https://wulala.com'
        }
        rsp = self.client.post(url, data=data, format='json')
        self.assertResponseRaiseCode(rsp, '1010')

    def test_add_topic_to_group_success(self):
        self.client.login(username=self.user.mobile, password='test')
        group = UserGroupFactory(create_user=self.user)
        url = self.url + str(group.id) + '/add-topic/'
        content = '哟哟呀我黑'
        data = {
            'title': 'lala拉',
            'brief': '哦哦',
            'content': content,
            'index_pic': 'https://wulala.com'
        }
        rsp = self.client.post(url, data=data, format='json')
        self.assertResponseRaiseCode(rsp, '0')
        self.assertEqual(rsp.data['result']['content'], content)


class RegisterAPITestCase(BaseAPITestCase):
    def setUp(self):
        super().setUp()
        self.url = '/register/'

    @parameterized.expand([
        ({'username': '123', 'password': '123'},),  # no nickname
        ({'username': '123', 'password': '123', 'nickname': '1'},),  # no register_type
        ({'username': '123', 'password': '123', 'nickname': '1', 'register_type': '0'},), # wrong register_type
        ({'username': '13909893456', 'password': '123', 'nickname': '1', 'register_type': 'mobile'},), # no verify_code
        ({'username': '123', 'password': '123', 'nickname': '1', 'register_type': 'mobile', 'verify_code': '4023'},), # wrong number
        ({'username': '123', 'password': '123', 'nickname': '1', 'register_type': 'email'},), # wrong email
    ])
    @mock.patch.object(SMSClient, 'check_verify_code')
    def test_register_with_params_invalid(self, data, mock_check_verify_code):
        mock_check_verify_code.return_value = True
        rsp = self.client.post(self.url, data=data, format='json')
        self.assertResponseRaiseCode(rsp, '1000')
        # print(rsp.data.get('error_data'))

    def test_register_with_duplicate_user(self):
        User.objects.create_user(mobile='13908980767', password='123456')
        data = {
            'username': '13908980767',
            'password': '123456',
            'register_type': 'mobile',
            'verify_code': '1234'
        }
        rsp = self.client.post(self.url, data=data, format='json')
        self.assertResponseRaiseCode(rsp, '1000')

    @mock.patch.object(SMSClient, 'check_verify_code')
    def test_register_success(self, mock_check_verify_code):
        data = {
            'username': '13908980767',
            'password': '123456',
            'register_type': 'mobile',
            'verify_code': '1234',
            'nickname': '张阿三'
        }
        rsp = self.client.post(self.url, data=data, format='json')
        self.assertTrue(mock_check_verify_code.called)
        self.assertResponseRaiseCode(rsp, '0')
        user = User.objects.filter(mobile='13908980767').first()
        self.assertEqual(int(self.client.session[SESSION_KEY]), user.pk)

    def test_register_success_with_cache(self):
        cache_key = SMSClient.SMS_CODE.format('13908980767')
        cache.set(cache_key, '1234')
        data = {
            'username': '13908980767',
            'password': '123456',
            'register_type': 'mobile',
            'verify_code': '1234',
            'nickname': '张阿三'
        }
        rsp = self.client.post(self.url, data=data, format='json')
        self.assertResponseRaiseCode(rsp, '0')
        user = User.objects.filter(mobile='13908980767').first()
        self.assertEqual(int(self.client.session[SESSION_KEY]), user.pk)


class LoginAPITestCase(BaseAPITestCase):
    def setUp(self):
        super().setUp()
        self.url = '/login/'
        self.user = UserFactory(password='123qwe')


    @parameterized.expand([
        ({'username': '123'},),      # no password
        ({'password': '123'},),      # no username
        ({'username': '''
        动画风口浪尖的话费金额为礼盒但是那份麻痹的妇女为交流氛围经典款画风问卷海底温泉哦鹅湖桥渥
        俄方蝴蝶我发货动画风口浪尖的话费金额为礼盒但是那份麻痹的妇女为交流氛围经典款画风问卷海底
        温泉哦鹅湖桥渥俄方蝴蝶我发货
        ''',
          'password': '123'},)  # too long username
    ])
    def test_login_with_params_invalid(self, data):
        rsp = self.client.post(self.url, data=data, format='json')
        self.assertResponseRaiseCode(rsp, '1000')
        # print(rsp.data.get('error_data'))

    def test_login_with_username_not_exists(self):
        data = {
            'username': '123',
            'password': '123'
        }
        rsp = self.client.post(self.url, data=data, format='json')
        self.assertResponseRaiseCode(rsp, '1001')

    def test_login_with_wrong_password(self):
        data = {
            'username': self.user.mobile,
            'password': '123'
        }
        rsp = self.client.post(self.url, data=data, format='json')
        self.assertResponseRaiseCode(rsp, '1002')

    def test_login_success(self):
        data = {
            'username': self.user.mobile,
            'password': '123qwe'
        }
        rsp = self.client.post(self.url, data=data, format='json')
        self.assertResponseRaiseCode(rsp, '0')
        self.assertEqual(int(self.client.session[SESSION_KEY]), self.user.pk)


class VerifyCodeAPITestCase(BaseAPITestCase):
    def setUp(self):
        super().setUp()
        self.url_pre = '/verify/'

    def test_send_verify_code_with_invalid_phone(self):
        url = self.url_pre + '1399780/'
        rsp = self.client.post(url)
        self.assertEqual(rsp.status_code, 404)

    def test_send_verify_code_with_invalid_type(self):
        url = self.url_pre + '13997805623/'
        rsp = self.client.post(url)
        self.assertResponseRaiseCode(rsp, '1009')

    @mock.patch('story_pieces.base.sms_helper.send')
    def test_send_verify_code_fail_return_1006(self, mock_send):
        mock_send.return_value = json.dumps({'wo': 'not ok'})
        url = self.url_pre + '13997805623/?type=register'
        rsp = self.client.post(url)
        self.assertResponseRaiseCode(rsp, '1006')

    @mock.patch('story_pieces.base.sms_helper.send')
    def test_send_verify_code_mock_success(self, mock_send):
        mock_send.return_value = json.dumps({'Code': 'OK'})
        url = self.url_pre + '13997805623/?type=register'
        rsp = self.client.post(url)
        self.assertResponseRaiseCode(rsp, '0')

    # def test_send_verify_code_success(self):
    #     # use own phone to test
    #     url = self.url_pre + '18565589052/?type=register'
    #     rsp = self.client.post(url)
    #     self.assertResponseRaiseCode(rsp, '0')


class UserAPITestCase(BaseAPITestCase):
    def setUp(self):
        super().setUp()
        self.url_pre = '/api/user-info/'
        self.user = UserFactory(nickname='乌啦啦', password='test')
        self.client.login(username=self.user.mobile, password='test')

    def test_put_user_info(self):
        data = {
            'nickname': '张阿三',
            'email': '123@qq.com'
        }
        url = self.url_pre + 'change/'
        rsp = self.client.put(url, data=data, format='json')
        self.assertResponseRaiseCode(rsp, '0')
        self.user.refresh_from_db()
        self.assertEqual(self.user.nickname, '张阿三')
        self.assertEqual(self.user.email, '123@qq.com')

