from rest_framework.permissions import BasePermission


class IsValidateClient(BasePermission):
    """
    检查请求来源合法客户端
    """

    def has_permission(self, request, view):

        #TODO：验证客户端类型不是微信浏览器
        return True
