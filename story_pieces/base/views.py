import logging
import qiniu

from story_pieces import settings
from rest_framework.authentication import SessionAuthentication
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from story_pieces.base.permissions import IsValidateClient
from story_pieces.base.utils import success_rsp

logger = logging.getLogger('django')


class AuthViewSet(GenericViewSet):
    permission_classes = (IsValidateClient, IsAuthenticated,)
    authentication_classes = (SessionAuthentication,)
    throttle_scope = None if settings.DEBUG else 'default'


class AnonyViewSet(GenericViewSet):
    permission_classes = (IsValidateClient,)
    authentication_classes = (SessionAuthentication,)
    throttle_scope = None if settings.DEBUG else 'default'


class CustomAPIView(APIView):
    permission_classes = (IsValidateClient, IsAuthenticated,)
    authentication_classes = (SessionAuthentication,)
    throttle_scope = None if settings.DEBUG else 'default'


class UploadImageView(CustomAPIView):
    """
    上传图像到七牛，后端上传
    """
    # permission_classes = ()
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):

        file_url = ''
        fileobj = request.data.get('image')
        filename = request.data.get('name')
        if fileobj and filename:
            q = qiniu.Auth(settings.QINIU_KEY, settings.QINIU_SECRET)
            token = q.upload_token(settings.QINIU_IMG_BUCKET, filename)
            ret, info = qiniu.put_data(token, filename, fileobj)
            if info.status_code == 200 and info.exception is None:
                file_url = settings.QINIU_IMG_DOMAIN + filename
            else:
                # logger.info(info)
                logger.error('qiniu error', extra=info)
        return success_rsp({'file': file_url})