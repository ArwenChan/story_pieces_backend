from rest_framework import serializers
from story_pieces.base.validators import validate_mobile
from story_pieces.base.utils import check_or_validation_error, SMSClient
from member.models import User


class RegisterForm(serializers.Serializer):
    username = serializers.CharField(max_length=50)
    password = serializers.CharField(max_length=50)
    nickname = serializers.CharField(max_length=50)
    register_type = serializers.ChoiceField(choices=['mobile',])
    verify_code = serializers.CharField(required=False, allow_blank=True)


    def validate(self, attrs):
        if attrs['register_type'] == 'mobile':
            check_or_validation_error(attrs.get('verify_code'),
                'verify_code', '手机验证码未提交')
            validate_mobile(attrs['username'])
            check_or_validation_error(User.objects.filter(mobile=attrs['username']).first() is None,
                'username', '手机号码已注册')

            sms_client = SMSClient(attrs['username'])
            check_or_validation_error(
                sms_client.check_verify_code(attrs['verify_code']),
                'verify_code', '验证码不正确')

            attrs['mobile'] = attrs['username']

        return attrs


class LoginForm(serializers.Serializer):
    username = serializers.CharField(max_length=50)
    password = serializers.CharField(max_length=50)


class UpdateUserForm(serializers.ModelSerializer):
    nickname = serializers.CharField(max_length=50)
    avatar = serializers.URLField()
    country = serializers.CharField(max_length=20)
    province = serializers.CharField(max_length=20)
    city = serializers.CharField(max_length=20)
    email = serializers.EmailField()

    class Meta:
        model = User
        fields = ['nickname', 'avatar', 'country', 'province', 'city', 'email']


class UpdatePasswordForm(serializers.Serializer):
    old_password = serializers.CharField(max_length=50)
    new_password = serializers.CharField(max_length=50)


class ResetPasswordForm(serializers.Serializer):
    mobile = serializers.CharField(max_length=50)
    verify_code = serializers.CharField(max_length=6)
    new_password = serializers.CharField(max_length=50)

    def validate(self, attrs):
        validate_mobile(attrs['mobile'])
        sms_client = SMSClient(attrs['mobile'])
        check_or_validation_error(
            sms_client.check_verify_code(attrs['verify_code']),
            'verify_code', '验证码不正确')
        return attrs


class CheckPasswordForm(serializers.Serializer):
    password = serializers.CharField(max_length=50)


class ChangeMobileForm(serializers.Serializer):
    mobile = serializers.CharField(max_length=50)
    verify_code = serializers.CharField(max_length=6)

    def validate(self, attrs):
        validate_mobile(attrs['mobile'])
        check_or_validation_error(User.objects.filter(mobile=attrs['mobile']).first() is None,
            'username', '手机号码已注册')
        sms_client = SMSClient(attrs['mobile'])
        check_or_validation_error(
            sms_client.check_verify_code(attrs['verify_code']),
            'verify_code', '验证码不正确')
        return attrs


class UserGroupForm(serializers.Serializer):
    name = serializers.CharField(max_length=30)
    brief = serializers.CharField(max_length=500)
    icon = serializers.URLField()
    tags = serializers.ListField(child=serializers.CharField(max_length=10), max_length=5)