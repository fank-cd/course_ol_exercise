# coding:utf-8
from courses.views import CourseListView, CourseDetailView, CourseInfoView, CommentsView, AddCommentView, VideoPlayView
from django.conf.urls import url

urlpatterns = [
    url(r'^list/$', CourseListView.as_view(), name='list'),
    url(r'^course/(?P<course_id>\d+)/$', CourseDetailView.as_view(), name="course_detail"),
    url(r'^info/(?P<course_id>\d+)/$', CourseInfoView.as_view(), name="course_info"),
    url(r'^video/(?P<video_id>\d+)/$', VideoPlayView.as_view(), name="video_play"),
    url(r'^comment/(?P<course_id>\d+)/$', CommentsView.as_view(), name="course_comments"),
    url(r'add_comment/', AddCommentView.as_view(), name='add_comment'),
]
