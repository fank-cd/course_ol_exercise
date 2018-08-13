"""shop URL Configuration

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
from shop.settings import MEDIA_ROOT

from django.conf.urls import url, include
from django.views.static import serve
from django.views.generic import TemplateView
from users.views import LoginView, RegisterView, ActiveUserView, ForgetPwdView, \
    ResetView, ModifyPwdView, LogoutView, IndexView
from organization.views import OrgView
import xadmin


urlpatterns = [
    #url(r'^admin/', admin.site.urls),
    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^logout/$', LogoutView.as_view(), name='logout'),
    url(r'^login/$', LoginView.as_view(), name="login"),
    url(r'^register/', RegisterView.as_view(), name="register"),
    url(r'^forget/$', ForgetPwdView.as_view(), name='forget_pwd'),
    url(r'^modify_pwd/$', ModifyPwdView.as_view(), name="modify_pwd"),
    url(r'^xadmin/', xadmin.site.urls),
]


urlpatterns += [
    url(r'^captcha/', include('captcha.urls')),
    url(r'^active/(?P<active_code>.*)/$', ActiveUserView.as_view(), name="user_active"),
    url(r'^reset/(?P<active_code>.*)/$', ResetView.as_view(), name="reset_pwd"),
]


urlpatterns += [
    url(r'^org/', include('organization.urls', namespace="org")),
]

urlpatterns += [
    url(r'^course/', include('courses.urls', namespace="course")),
]


urlpatterns += [
    url(r'^media/(?P<path>.*)$', serve, {"document_root": MEDIA_ROOT})
]

urlpatterns += [
    url(r'^users/', include('users.urls', namespace="users"))
]


handler404 = 'users.views.page_not_found'
handler500 = 'users.views.page_error'
