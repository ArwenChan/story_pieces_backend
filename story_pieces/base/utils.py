import json
import random
import uuid
import logging

from django.core.cache import cache
from django.http import HttpResponse

from rest_framework.exceptions import ValidationError
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import set_rollback

from story_pieces.base.exceptions import BusinessException


logger = logging.getLogger('django')

def success_rsp(obj=None, http_rsp=False, **kwargs):
    if obj is not None:
        rsp_data = {'error_code': '0', 'error_message': '', 'result': obj}
    else:
        rsp_data = {'error_code': '0', 'error_message': '', 'result': {}}


    if http_rsp:
        return HttpResponse(JSONRenderer().render(rsp_data),
            content_type='application/json', **kwargs)
    else:
        return Response(rsp_data, **kwargs)


def error_rsp(code, msg, data=None, http_rsp=False, **kwargs):
    if data:
        rsp_data = {'error_code': code, 'error_message': msg, 'error_data': data}
    else:
        rsp_data = {'error_code': code, 'error_message': msg}
    if http_rsp:
        return HttpResponse(JSONRenderer().render(rsp_data),
            content_type='application/json', **kwargs)
    return Response(rsp_data, **kwargs)


def business_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    set_rollback()
    response = error_rsp(exc.error_code, exc.error_message, exc.error_data)
    return response


def check_or_validation_error(condition, field, message):
    if not condition:
        raise ValidationError({field: message})


def check_or_business_error(condition, error_code=None, error_message=None, error_data=None):
    """
    检查条件, 如果不为真, 则抛出BusinessException
    """
    if not condition:
        raise BusinessException(error_code, error_message, error_data)


def _page(request, query, size=20):
    """按照分页参数获取相应的查询结果
    """
    page = request.GET.get('page', 1)
    if page:
        _page = int(page)
        if _page <= 0:
            _page = 1
        _size = int(request.GET.get('size', '0'))
        if _size <= 0:
            _size = size
        return query[(_page - 1) * _size: _page * _size], len(query)
    return query, len(query)


def uuid4_hex():
    return uuid.uuid4().hex



class SMSClient:

    # 短信验证码 cache key 前缀, 完整 key 为 SMS_CODE:13800000000
    SMS_CODE = 'SMS_CODE:{}'

    # 短信模板
    template_map = {
        'register': 'SMS_151578403',
        'change_mobile': 'SMS_151771220',
        'reset_password': 'SMS_152212475',
    }

    def __init__(self, phone):
        from .sms_helper import send

        self.phone = phone
        self.key = self.SMS_CODE.format(phone)
        self.send = send

    def _generate_code(self):
        code = str(random.randint(1000, 9999))
        cache.set(self.key, code)
        return code

    def send_sms(self, type):
        template = self.template_map.get(type)
        business_id = uuid.uuid1()
        params = {'code': self._generate_code()}
        answer = json.loads(self.send(business_id, self.phone, "故事王", template, json.dumps(params)))
        if answer.get('Code') != 'OK':
            logger.error('sms service error', extra=answer)
            # logger.error('sms service error:{}'.format(answer))
            raise BusinessException('1006')

    def check_verify_code(self, code):
        cache_code = cache.get(self.key)
        if cache_code != code:
            logging.info('code:', code)
            logging.info('cache_code:', cache_code)
            return False
        return True