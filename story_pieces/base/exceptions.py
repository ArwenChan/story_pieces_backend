from django.utils.encoding import force_text


ERROR_PHRASES = {
    '1000': '参数格式错误',
    '1001': '用户名不存在',
    '1002': '密码不正确',
    '1003': '注册失败',
    # '1004': '短信发送频繁',
    '1005': '验证码错误',
    '1006': '发送短信失败',
    '1007': '创建组失败',
    '1008': '无此权限',
    '1009': '不明短信请求',
    '1010': '非小组成员不可以发言',
    '1011': '重复点赞',
    '1012': '回复业务错误',
    '1014': '手机号未注册',
}


class BusinessException(Exception):
    default_error_code = "9000"
    default_error_message = "系统错误"

    def __init__(self, error_code=None, error_message=None, error_data=None):
        if error_code is not None and error_message is not None:
            self.error_code = error_code
            self.error_message = error_message
        elif error_code is not None:
            self.error_code = error_code
            self.error_message = force_text(ERROR_PHRASES.get(error_code))
        else:
            self.error_code = self.default_error_code
            self.error_message = force_text(self.default_error_message)
        self.error_data = error_data

    def __str__(self):
        return self.error_message


