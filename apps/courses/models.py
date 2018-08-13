# coding:utf-8
from __future__ import unicode_literals
from datetime import datetime

from django.db import models
from organization.models import CourseOrg, Teacher
# Create your models here.


class Course(models.Model):
    DEGREE_CHOICES = (
        ('cj', u"初级"),
        ('zj', u"中级"),
        ('gj', u"高级")
    )
    teacher = models.ForeignKey(Teacher,verbose_name=u"讲师", null=True, blank=True)
    course_org = models.ForeignKey(CourseOrg, verbose_name=u"所属机构", null=True, blank=True)
    category = models.CharField(max_length=20, default=u"", verbose_name=u"课程类别")
    tag = models.CharField(max_length=15, verbose_name=u"课程标签", default=u"")
    name = models.CharField(max_length=50, verbose_name=u"课程名")
    desc = models.CharField(max_length=300, verbose_name=u"课程描述")
    detail = models.TextField(verbose_name=u"课程详情")
    degree = models.CharField(choices=DEGREE_CHOICES, max_length=2)
    learn_times = models.IntegerField(default=0, verbose_name=u"学习时长(分钟数)")
    students = models.IntegerField(default=0, verbose_name=u"学习人数")
    fav_nums = models.IntegerField(default=0, verbose_name=u"收藏人数")
    you_need_know = models.CharField(max_length=300, default=u"好好学习，天天向上", verbose_name=u"课程须知")
    teacher_tell = models.CharField(max_length=300, default=u"不能开小差", verbose_name=u"老师提醒")
    is_banner = models.BooleanField(default=False, verbose_name=u"是否轮播")
    image = models.ImageField(
        upload_to='courses/%Y/%m',
        verbose_name=u"封面图",
        max_length=100
    )
    click_nums = models.IntegerField(default=0, verbose_name=u"点击数")
    add_time = models.DateTimeField(default=datetime.now, verbose_name=u"添加时间")

    class Meta:
        verbose_name = u"课程"
        verbose_name_plural = verbose_name

    def get_zj_nums(self):
        return self.lesson_set.all().count()

    def get_learn_users(self):
        return self.usercourse_set.all()[:5]

    def get_learn_users_count(self):
        return self.usercourse_set.all().count()

    def __unicode__(self):
        return self.name


class Lesson(models.Model):

    course = models.ForeignKey(Course, verbose_name=u"课程")
    name = models.CharField(max_length=100, verbose_name=u"章节名")
    add_time = models.DateTimeField(default=datetime.now, verbose_name=u"添加时间")

    class Meta:
        verbose_name = u"章节"
        verbose_name_plural = verbose_name

    def __unicode__(self):
        return '<{0} 课程章节 >>{1}>'.format(self.course, self.name)


class Video(models.Model):
    lesson = models.ForeignKey(Lesson, verbose_name=u"章节")
    name = models.CharField(max_length=100, verbose_name=u"视频名")
    add_time = models.DateTimeField(default=datetime.now, verbose_name=u"添加时间")
    url = models.CharField(max_length=200, default="www.baidu.com", verbose_name=u"访问地址")
    learn_times = models.IntegerField(default=0, verbose_name=u"学习时长(分钟数)")

    class Meta:
        verbose_name = u"视频"
        verbose_name_plural = verbose_name

    def __unicode__(self):
        return '<{0}章节 >>{1}>'.format(self.lesson, self.name)


class CourseResource(models.Model):
    course = models.ForeignKey(Course, verbose_name=u"课程")
    name = models.CharField(max_length=100, verbose_name=u"名称")

    download = models.FileField(
        upload_to="course/resource/%y/%m",
        verbose_name=u"资源文件",
        max_length=100
    )
    add_time = models.DateTimeField(default=datetime.now, verbose_name=u"添加时间")

    class Meta:
        verbose_name = u"课程资源"
        verbose_name_plural = verbose_name

    def __unicode__(self):
        return '<{0} 课程>>{1}资源>'.format(self.course, self.name)