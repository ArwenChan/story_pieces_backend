import factory

from story_pieces.base.utils import uuid4_hex
from .models import User, UserGroup, UserInGroup


class UserGroupFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UserGroup

    name = factory.Sequence(lambda n: "Group #%s" % n)
    icon = factory.Faker('image_url')
    brief = factory.Sequence(lambda n: "Group #%s brief" % n)
    tags = []
    status = 'normal'

    @factory.post_generation
    def create_user(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A password passed in, use it
            UserInGroup.objects.add_user(extracted, self, role='create_user')


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.LazyAttribute(lambda obj: uuid4_hex())
    nickname = factory.Faker('name')
    mobile = factory.Faker('phone_number', locale='zh_CN')
    avatar = factory.Faker('image_url')

    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A password passed in, use it
            self.set_password(extracted)
            self.save()