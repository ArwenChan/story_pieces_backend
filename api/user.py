from story_pieces import settings
from django.contrib.auth import authenticate, login, logout
from rest_framework import status
from rest_framework.decorators import action

from member.forms import RegisterForm, LoginForm, UpdateUserForm, UpdatePasswordForm, CheckPasswordForm, \
    ChangeMobileForm, ResetPasswordForm
from member.models import User
from member.serializers import UserDetailSerializer
from story_pieces.base.utils import success_rsp, error_rsp, SMSClient
from story_pieces.base.permissions import IsValidateClient
from story_pieces.base.utils import check_or_business_error
from story_pieces.base.views import AuthViewSet, CustomAPIView as APIView


class RegisterView(APIView):
    permission_classes = (IsValidateClient,)


    def post(self, request, *args, **kwargs):
        form = RegisterForm(data=request.data)
        check_or_business_error(form.is_valid(),
            error_code='1000', error_data=form.errors)
        user = User.objects.create_user(
            form.validated_data['mobile'],
            form.validated_data['password'],
            form.validated_data['nickname'],
        )
        check_or_business_error(user is not None, '1003')
        login(request, user)
        user_data = UserDetailSerializer(user).data
        return success_rsp(user_data)


class LoginView(APIView):
    permission_classes = (IsValidateClient,)


    def post(self, request, *args, **kwargs):
        form = LoginForm(data=request.data)
        check_or_business_error(form.is_valid(),
            error_code='1000', error_data=form.errors)
        differ = {'exist': True}
        user = authenticate(request,
            username=form.validated_data['username'],
            password=form.validated_data['password'],
            differ=differ
        )
        if not user:
            if differ['exist']:
                return error_rsp('1002', u'密码错误')
            else:
                return error_rsp('1001', u'用户名不存在')
        login(request, user)
        user_data = UserDetailSerializer(user).data
        return success_rsp(user_data)


class LogoutView(APIView):

    def post(self, request, *args, **kwargs):
        logout(request)
        return success_rsp()


class VerifyCodeView(APIView):
    permission_classes = (IsValidateClient,)
    throttle_scope = None if settings.DEBUG else 'sms'

    def post(self, request, *args, **kwargs):
        phone_number = kwargs.get('phone')
        sms_client = SMSClient(phone_number)
        sms_type = request.query_params.get('type')
        check_or_business_error(sms_type in ('register', 'change_mobile', 'reset_password'), '1009')
        sms_client.send_sms(sms_type)
        return success_rsp()


class UserViewSet(AuthViewSet):

    @action(detail=False, methods=['GET'])
    def details(self, request, *args, **kwargs):
        ret = UserDetailSerializer(request.user).data
        return success_rsp(ret)

    @action(detail=False, methods=['PUT'])
    def change(self, request, *args, **kwargs):
        form = UpdateUserForm(request.user, data=request.data, partial=True)
        check_or_business_error(form.is_valid(), '1000', error_data=form.errors)
        form.save()
        request.user.refresh_from_db()
        ret = UserDetailSerializer(request.user).data
        return success_rsp(ret)

    @action(detail=False, methods=['POST'], url_path='set-password')
    def set_password(self, request, *args, **kwargs):
        form = UpdatePasswordForm(data=request.data)
        check_or_business_error(form.is_valid(), '1000', error_data=form.errors)
        check_or_business_error(request.user.check_password(
            form.validated_data.get('old_password')), '1002')
        request.user.set_password(form.validated_data.get('new_password'))
        request.user.save()
        return success_rsp()

    @action(detail=False, methods=['POST'], url_path='reset-password', permission_classes=[IsValidateClient])
    def reset_password(self, request, *args, **kwargs):
        form = ResetPasswordForm(data=request.data)
        check_or_business_error(form.is_valid(), '1000', error_data=form.errors)
        user = User.objects.filter(mobile=form.validated_data.get('mobile')).first()
        check_or_business_error(user, '1014')
        user.set_password(form.validated_data.get('new_password'))
        user.save()
        return success_rsp()

    @action(detail=False, methods=['POST'], url_path='check-password')
    def check_password(self, request, *args, **kwargs):
        form = CheckPasswordForm(data=request.data)
        check_or_business_error(form.is_valid(), '1000', error_data=form.errors)
        check_or_business_error(request.user.check_password(
            form.validated_data.get('password')), '1002')
        return success_rsp()

    @action(detail=False, methods=['POST'], url_path='change-mobile')
    def change_mobile(self, request, *args, **kwargs):
        form = ChangeMobileForm(data=request.data)
        check_or_business_error(form.is_valid(), '1000', error_data=form.errors)
        request.user.mobile = form.validated_data.get('mobile')
        request.user.save()
        request.user.refresh_from_db()
        ret = UserDetailSerializer(request.user).data
        return success_rsp(ret)
