# coding:utf-8
from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic.base import View
from django.db.models import Q

from courses.models import Course
from operation.models import UserFavorite
from .models import CourseOrg, CityDict, Teacher
from .forms import UserAskForm

from pure_pagination import Paginator, EmptyPage, PageNotAnInteger
# Create your views here.


class OrgView(View):
    def get(self, request):

        all_orgs = CourseOrg.objects.all()
        for org in all_orgs:
            org.course_nums = org.course_set.count()
            org.save()

        all_citys = CityDict.objects.all()
        hot_orgs = all_orgs.order_by("-click_nums")[:3]

        search_keywords = request.GET.get('keywords', '')
        if search_keywords:
            all_orgs = all_orgs.filter(Q(name__icontains=search_keywords) | Q(desc__contains=search_keywords)
                                       | Q(address__icontains=search_keywords))
        city_id = request.GET.get('city', '')
        category = request.GET.get('ct', '')
        sort = request.GET.get('sort', '')

        if sort:
            if sort == 'students':
                all_orgs = all_orgs.order_by("-students")
            if sort == "courses":
                all_orgs = all_orgs.order_by("-course_nums")

        if city_id:
            all_orgs = all_orgs.filter(city_id=int(city_id))
        if category:
            all_orgs = all_orgs.filter(category=category)
        org_nums = all_orgs.count()

        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        p = Paginator(all_orgs, 4, request=request)
        orgs = p.page(page)

        context = {'all_orgs': orgs, "all_citys": all_citys, 'org_nums': org_nums,
                   "city_id": city_id, "category": category, "hot_orgs": hot_orgs, "sort": sort,
                   "search_keywords": search_keywords}
        return render(request, "org-list.html", context=context)


class AddUserAskView(View):
    def post(self,request):
        userask_form = UserAskForm(request.POST)
        if userask_form.is_valid():
            user_ask = userask_form.save(commit=True)
            return HttpResponse('{"status":"success"}', content_type='application/json')
        else:
            return HttpResponse('{"status":"fail", "msg":"您的字段有错误,请检查"}',
                                content_type='application/json')


class OrgHomeView(View):
    def get(self, request, org_id):
        course_org = CourseOrg.objects.get(id=int(org_id))
        all_courses = course_org.course_set.all()[:4]
        all_teachers = course_org.teacher_set.all()[:2]
        current_page = 'home'
        has_fav = False
        course_org.click_nums += 1
        course_org.save()

        if request.user.is_authenticated():
            if UserFavorite.objects.filter(user=request.user, fav_id=int(org_id), fav_type=2):
                has_fav = True
        return render(request, 'org-detail-homepage.html', {
            'course_org': course_org,
            'all_courses': all_courses,
            'all_teacher': all_teachers,
            'current_page': current_page,
            'has_fav': has_fav,
        })


class OrgCourseView(View):
    def get(self, request, org_id):
        course_org = CourseOrg.objects.get(id=int(org_id))
        all_course = course_org.course_set.all()
        current_page = 'course'
        has_fav = False
        if request.user.is_authenticated():
            if UserFavorite.objects.filter(user=request.user, fav_id=int(org_id), fav_type=2):
                has_fav = True
        return render(request, 'org-detail-course.html', {
            'all_courses': all_course,
            'course_org': course_org,
            'current_page': current_page,
            'has_fav': has_fav,
        })


class OrgDescView(View):
    def get(self, request, org_id):
        current_page = 'desc'
        course_org = CourseOrg.objects.get(id=int(org_id))
        has_fav = False
        if request.user.is_authenticated():
            if UserFavorite.objects.filter(user=request.user, fav_id=int(org_id), fav_type=2):
                has_fav = True
        return render(request, 'org-detail-desc.html', {
            'course_org': course_org,
            'current_page': current_page,
            'has_fav': has_fav,
        })


class OrgTeacherView(View):
    def get(self, request, org_id):
        current_pgae = "teacher"
        course_org = CourseOrg.objects.get(id=int(org_id))
        all_teachers = course_org.teacher_set.all()
        has_fav = False
        if request.user.is_authenticated():
            if UserFavorite.objects.filter(user=request.user, fav_id=int(org_id), fav_type=2):
                has_fav = True
        return render(request, 'org-detail-teachers.html', {
            'all_teachers': all_teachers,
            'course_org': course_org,
            'current_page': current_pgae,
            'has_fav': has_fav,
        })


class AddFavView(View):
    """
    用户收藏与取消收藏功能
    """
    def post(self, request):
        id = request.POST.get('fav_id', 0)
        type = request.POST.get('fav_type', 0)

        if request.user.is_authenticated():
            exist_records = UserFavorite.objects.filter(user=request.user, fav_id=int(id), fav_type=int(type))
            if exist_records:
                # 如果记录已经存在， 则表示用户取消收藏
                exist_records.delete()
                if int(type) == 1:
                    course = Course.objects.get(id=int(id))
                    course.fav_nums -= 1
                    if course.fav_nums < 0:
                        course.fav_nums = 0
                    course.save()
                elif int(type) == 2:
                    org = CourseOrg.objects.get(id=int(id))
                    org.fav_nums -= 1
                    if org.fav_nums < 0:
                        org.fav_nums = 0
                    org.save()
                elif int(type) == 3:
                    teacher = Teacher.objects.get(id=int(id))
                    teacher.fav_nums -= 1
                    if teacher.fav_nums < 0:
                        teacher.fav_nums = 0
                    teacher.save()
                return HttpResponse('{"status":"success", "msg":"收藏"}', content_type='application/json')
            else:
                user_fav = UserFavorite()
                # 过滤掉未取到fav_id type的默认情况
                if int(type) > 0 and int(id) > 0:
                    user_fav.fav_id = int(id)
                    user_fav.fav_type = int(type)
                    user_fav.user = request.user
                    user_fav.save()
                    if int(type) == 1:
                        course = Course.objects.get(id=int(id))
                        course.fav_nums += 1
                        course.save()
                    elif int(type) == 2:
                        org = CourseOrg.objects.get(id=int(id))
                        org.fav_nums += 1
                        org.save()
                    elif int(type) == 3:
                        teacher = Teacher.objects.get(id=int(id))
                        teacher.fav_nums += 1
                        teacher.save()
                    return HttpResponse('{"status":"success", "msg":"已收藏"}', content_type='application/json')
                else:
                    return HttpResponse('{"status":"fail", "msg":"收藏出错"}', content_type='application/json')
        else:
            print "dd"
            return HttpResponse('{"status":"fail", "msg":"用户未登录"}', content_type='application/json')


class TeacherListView(View):
    def get(self, request):
        all_teacher = Teacher.objects.all()
        teacher_nums = all_teacher.count()

        sort = request.GET.get("sort", "")
        if sort:
            if sort == 'hot':
                all_teacher = all_teacher.order_by('-click_nums')

        search_keywords = request.GET.get('keywords', '')
        if search_keywords:
            all_teacher = all_teacher.filter(Q(name__icontains=search_keywords) |
                                             Q(work_company__contains=search_keywords))

        rank_teachers = Teacher.objects.all().order_by("-fav_nums")[:5]

        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1

        p = Paginator(all_teacher, 4, request=request)
        teachers = p.page(page)

        return render(request, "teachers-list.html", {
            "all_teacher": teachers,
            "teacher_nums": teacher_nums,
            'sort': sort,
            "rank_teachers": rank_teachers,
            "search_keywords": search_keywords,
        })


class TeacherDetailView(View):
    def get(self, request, teacher_id):
        teacher = Teacher.objects.get(id=int(teacher_id))
        all_course = teacher.course_set.all()
        teacher.click_nums += 1
        teacher.save()
        rank_teacher = Teacher.objects.all().order_by("fav_nums")[:5]

        has_hav_teacher = False
        has_hav_org = False
        if request.user.is_authenticated():
            if UserFavorite.objects.filter(user=request.user, fav_type=3, fav_id=teacher.id):
                has_hav_teacher = True
            if UserFavorite.objects.filter(user=request.user, fav_type=2, fav_id=teacher.org.id):
                has_hav_org = True

        return render(request, "teacher-detail.html", {
            "teacher": teacher,
            "all_course": all_course,
            "rank_teacher": rank_teacher,
            "has_fav_teacher": has_hav_teacher,
            "has_hav_org": has_hav_org,
        })
