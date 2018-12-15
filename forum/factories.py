import factory

from member.factories import UserFactory
from .models import Message, Likes



class MessageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Message

    group = factory.SubFactory('member.factories.UserGroupFactory')
    content = factory.Sequence(lambda n: '这就是内容%s' % n)
    create_user = factory.SubFactory('member.factories.UserFactory')
    title = factory.Sequence(lambda n: "标题#%s" % n)
    index_pic = factory.Faker('image_url')


class LikesFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Likes

    message = factory.SubFactory(MessageFactory)
    user = factory.SubFactory(UserFactory)