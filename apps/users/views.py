# coding:utf-8
import json
from django.http import HttpResponseRedirect, HttpResponse
from django.views.generic.base import View
from django.shortcuts import render
from django.db.models import Q
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.hashers import make_password
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import UserProfile, EmailVerifyRecord, Banner
from operation.models import UserCourse, UserFavorite, UserMessage
from courses.models import CourseOrg, Course
from organization.models import Teacher
from .forms import LoginForm, RegisterForm, ActiveForm, ForgetForm, ModifyPwdForm, UploadImageForm, UserInfoForm
from utils.email_send import send_register_email

from pure_pagination import Paginator, PageNotAnInteger
# Create your views here.


class CustomBackend(ModelBackend):
    def authenticate(self, username=None, password=None, **kwargs):
        try:
            user = UserProfile.objects.get(Q(username=username)|Q(email = username))
            if user.check_password(password):
                return user
        except Exception as e:
            return None


class LoginView(View):
    def get(self, request):
        return render(request, "login.html", {})

    def post(self, request):
        login_form = LoginForm(request.POST)
        if login_form.is_valid():

            user_name = request.POST.get("username", "")
            pass_word = request.POST.get('password', "")

            user = authenticate(username=user_name, password=pass_word)

            if user is not None:
                login(request, user)
                return render(request, "index.html")
            else:
                return render(request, "login.html", {"msg": "用户名或密码错误", "login_form": login_form})
        else:
            return render(request, "login.html", {"login_form": login_form})


class LogoutView(View):
    def get(self, request):
        logout(request)
        return HttpResponseRedirect(reverse('index'))


class RegisterView(View):
    def get(self, request):
        register_form = RegisterForm()
        return render(request, "register.html", {'register_form': register_form})

    def post(self, request):
        register_form = RegisterForm(request.POST)
        if register_form.is_valid():
            user_name = request.POST.get("email", "")
            pass_word = request.POST.get("password", "")

            user_profile = UserProfile()
            user_profile.username = user_name
            user_profile.email = user_name

            user_profile.password = make_password(pass_word)
            user_profile.is_active = False
            user_profile.save()

            user_message = UserMessage()
            user_message.user = user_profile.id
            user_message.message = "欢迎注册！！哈哈哈哈哈"
            user_message.save()

            send_register_email(user_name, "register")
            return render(request, "login.html")
        else:
            return render(request, "register.html", {"register_form": register_form})


class ForgetPwdView(View):
    def get(self, request):
        forget_form = ForgetForm()
        return render(request, "forgetpwd.html", {"forget_form":forget_form})

    def post(self, request):
        forget_form = ForgetForm(request.POST)
        if forget_form.is_valid():
            email = request.POST.get("email", '')
            send_register_email(email, "forget")
            return render(request, "login.html", {"msg": "重置密码邮件已发送，请注意查收"})
        else:
            return render(request, "forgetpwd.html", {"forget_form": forget_form})


class ResetView(View):
    def get(self, request, active_code):
        all_record = EmailVerifyRecord.objects.filter(code=active_code)
        active_form = ActiveForm(request.GET)
        if all_record:
            for record in all_record:
                email = record.email
                return render(request, "password_reset.html", {"email": email})
        else:
            return render(
                request, "forgetpwd.html", {
                    "msg": "您的充值密码连接无效，请重新请求", "active_form":active_form
                }
            )


class ModifyPwdView(View):
    def post(self, request):
        modiypwd_form = ModifyPwdForm(request.POST)
        if modiypwd_form.is_valid():
            pwd1 = request.POST.get("password1", "")
            pwd2 = request.POST.get("password2", "")
            email = request.POST.get("email", "")

            if pwd1 != pwd2:
                return render(request, "password_reset.html", {"email": email, "msg": "密码不一致"})
            user = UserProfile.objects.get(email=email)
            user.password = make_password(pwd2)
            user.save()
            return render(request, "login.html", {"msg": "密码修改成功，请登录"})

        else:
            email = request.POST.get("email", "")
            return render(request, "password_reset.html", {"email": email, "modiypwd_form": modiypwd_form})


class ActiveUserView(View):
    def get(self, request, active_code):
        all_record = EmailVerifyRecord.objects.filter(code=active_code)
        active_form = ActiveForm(request.GET)

        if all_record:
            for record in all_record:
                email = record.email
                user = UserProfile.objects.get(email=email)
                user.is_active = True
                user.save()
                return render(request, "login.html", {"msg": "您的激活成功"})
        else:
            return render(request, "register.html", {"msg": "您的激活链接无效", "active_form": active_form})


class UserInfoView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'next'

    def get(self, request):
        return render(request, "usercenter-info.html",{

        })

    def post(self, request):
        user_info_form = UserInfoForm(request.post, instance=request.user)
        if user_info_form.is_valid():
            user_info_form.save()
            return HttpResponse('{"status":"success"}', content_type='application/json')

        else:
            return HttpResponse(
                json.dumps(user_info_form.errors), content_type='application/json'
            )


class UploadImageView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'next'

    def post(self, request):
        image_form = UploadImageForm(request.post, request.FILES, instance=request.user)

        if image_form.is_valid():
            image_form.save()
            return HttpResponse(
                    '{"status":"success"}', content_type='application/json'
                )
        else:
            return HttpResponse('{"status":"fail"}', content_type='application/json')


class UpdatePwdView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'next'

    def post(self, request):
        modify_form = ModifyPwdForm(request.POST)
        if modify_form.is_valid():
            pwd1 = request.POST.get("password1", "")
            pwd2 = request.POST.get("password2", "")

            if pwd1 != pwd2:
                return HttpResponse(
                    '{"status":"success"}', content_type='application/json'
                )
            else:
                return HttpResponse(
                    json.dumps(modify_form.errors), content_type='application/json'
                )


class SendEmailCodeView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'next'

    def get(self, request):
        email = request.GET.get("mail", "")

        if UserProfile.objects.filter(email=email):
            return HttpResponse('{"email":"邮箱已经存在"}', content_type='application/json')

        send_register_email(email, "update_email")
        return HttpResponse(
            '{"status":"success"}', content_type='application/json'
        )


class UpdateEmailView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'next'

    def post(self, request):
        email = request.POST.get("email", "")
        code = request.POST.get("code", "")

        existed_records = EmailVerifyRecord.objects.filter(
            email=email, code=code, send_type="update_email"
        )
        if existed_records:
            user = request.user
            user.email = email
            user.save()

            return HttpResponse(
                '{"status":"success"}', content_type='application/json'
            )

        else:
            return HttpResponse(
                '{"email":"验证码无效"}', content_type='application/json'
            )


class MyCourseView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'next'

    def get(self, request):
        user_courses = UserCourse.objects.filter(user=request.user)
        return render(request, "usercenter-mycourse.html", {
            "user_courses": user_courses,
        })


class MyFavOrgView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'next'

    def get(self, request):
        org_list = []
        fav_orgs = UserFavorite.objects.filter(user=request.user, fav_type=2)

        for fav_orgs in fav_orgs:
            org_id = fav_orgs.fav_id
            org = CourseOrg.objects.get(id=org_id)
            org_list.append(org)

        return render(request, "usercenter-fav-org.html", {
            "org_list": org_list,
        })


class MyFavTeacherView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'next'

    def get(self, request):
        teacher_list = []
        fav_teachers = UserFavorite.objects.filter(user=request.user, fav_type=3)

        for fav_teacher in fav_teachers:
            teacher_id = fav_teacher.fav_id
            teacher = Teacher.objects.get(id=teacher_id)
            teacher_list.append(teacher)

        return render(request, "usercenter-fav-teacher.html", {
            "teacher_list": teacher_list
        })


class MyFavCourseView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'next'

    def get(self, request):
        course_list = []
        fav_courses = UserFavorite.objects.filter(user=request.user, fav_type=1)

        for fav_course in fav_courses:
            course_id = fav_course.fav_id
            course = Course.objects.get(id=course_id)
            course_list.append(course)

        return render(request, "usercenter-fav-course.html", {
            "course_list": course_list
        })


class MyMessageView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'next'

    def get(self, request):
        all_message = UserMessage.objects.filter(user=request.user.id)
        all_unread_messages = UserMessage.objects.filter(user=request.user.id, has_read=False)
        for unread_message in all_unread_messages:
            unread_message.has_read = True
            unread_message.save()
        try:
            page = request.GET.get('page',1)
        except PageNotAnInteger:
            page = 1
        p = Paginator(all_message,4)
        mesaages = p.page(page)

        return render(request, "usercenter-message.html", {
            "messages": mesaages,
        })


class IndexView(View):
    def get(self,request):
        all_banner = Banner.objects.all().order_by('index')[:5]
        courses = Course.objects.filter(is_banner=False)[:6]
        banner_courses = Course.objects.filter(is_banner=True)[:3]
        course_orgs = CourseOrg.objects.all()[:15]

        return render(request, 'index.html', {
            "all_banner": all_banner,
            "courses": courses,
            "banner_courses": banner_courses,
            "course_orgs": course_orgs,
        })


def page_not_found(request):
    from django.shortcuts import render_to_response
    response = render_to_response('404.html', {})
    response.status_code = 404
    return response


def page_error(request):
    from django.shortcuts import render_to_response
    response = render_to_response('500.html', {})
    response.status_code = 500
    return response
