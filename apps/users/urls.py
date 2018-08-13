# coding:utf-8

from .views import UserInfoView, MyCourseView, MyFavOrgView, MyFavTeacherView, MyFavCourseView, MyMessageView
from django.conf.urls import url

urlpatterns = [
    url('^info/$', UserInfoView.as_view(), name="user_info"),
    url(r'^mycourse/$', MyCourseView.as_view(), name="mycourse"),
    url(r'^myfav/org/$', MyFavOrgView.as_view(), name="myfav_org"),
    url(r'^myfav/teacher/$', MyFavTeacherView.as_view(), name="myfav_teacher"),
    url(r'^myfav/course/$', MyFavCourseView.as_view(), name="myfav_course"),
    url(r'^my_message/$', MyMessageView.as_view(), name="my_message"),
]
