"""story_pieces URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.urls import include
from rest_framework import routers

from api.forum import TopicsViewSet, MyTopicsViewSet, GroupsViewSet, MyGroupsViewSet
from api.user import RegisterView, LoginView, VerifyCodeView, LogoutView, UserViewSet
from story_pieces.base.views import UploadImageView

api_router = routers.SimpleRouter()
api_router.register(r'forum/topics/my', MyTopicsViewSet, base_name='my_forum_topics')
api_router.register(r'forum/topics', TopicsViewSet, base_name='forum_topics')
api_router.register(r'forum/groups/my', MyGroupsViewSet, base_name='my_forum_groups')
api_router.register(r'forum/groups', GroupsViewSet, base_name='forum_groups')
api_router.register(r'user-info', UserViewSet, base_name='user_info')

# print(api_router.urls)

admin.site.site_header = '故事王 管理后台'

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api/', include(api_router.urls)),
    url(r'^register/$', RegisterView.as_view()),
    url(r'^login/$', LoginView.as_view()),
    url(r'^logout/$', LogoutView.as_view()),
    url(r'^verify/(?P<phone>[0-9]{11})/$', VerifyCodeView.as_view()),
    url(r'^upload/$', UploadImageView.as_view()),
]
