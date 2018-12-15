from django.core.exceptions import ValidationError

def validate_mobile(value):
    if not (isinstance(value, str) and len(value) == 11 and value.isdigit()):
        raise ValidationError('手机号码格式不规范', code='invalid')
