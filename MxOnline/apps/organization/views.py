from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.views.generic.base import View
from pure_pagination import Paginator,PageNotAnInteger
from django.db.models import Q
from .models import CourseOrg,CityDict,Teacher
from .forms import UserAskForm
from operation.models import UserFavorite
from course.models import Course


class OrgView(View):
    def get(self,request):
        #取出所有课程机构
        all_orgs = CourseOrg.objects.all()

        search_keywords = request.GET.get('keywords', '')
        if search_keywords:
            # 在name字段进行操作,做like语句的操作。i代表不区分大小写
            # or操作使用Q
            all_orgs = all_orgs.filter(Q(name__icontains=search_keywords) | Q(desc__icontains=search_keywords))

        category = request.GET.get('ct','')
        current_page = 'org'
        if category:
            all_orgs = all_orgs.filter(category=category)
        #热门机构
        hot_orgs = all_orgs.order_by('-click_nums')[:3]
        #机构数量
        org_nums = all_orgs.count()
        #取出所有城市
        all_cities = CityDict.objects.all()
        #字符串转成整数

        city_id = request.GET.get('city','')
        if city_id:
            all_orgs = all_orgs.filter(city_id=int(city_id))

        sort = request.GET.get('sort','')
        if sort:
            if sort == "students":
                all_orgs = all_orgs.order_by("-students")
            elif sort == "courses":
                all_orgs = all_orgs.order_by("-course_nums")

        #分页
        try:
            page = request.GET.get('page',1)
        except PageNotAnInteger:
            page = 1
        # 这里指从all_orgs中取五个出来，每页显示5个
        p = Paginator(all_orgs,5,request=request)
        orgs = p.page(page)

        return render(request,'org-list.html',{
            "all_orgs": orgs,
            "all_cities": all_cities,
            "org_nums": org_nums,
            "city_id":city_id,
            "category":category,
            "hot_orgs":hot_orgs,
            "sort":sort,
            "current_page":current_page,
        })


class AddUserAskView(View):
    """
    用户添加咨询
    """
    def post(self, request):
        userask_form = UserAskForm(request.POST)
        if userask_form.is_valid():
            user_ask = userask_form.save(commit=True)
            # 如果保存成功,返回json字符串,后面content type是告诉浏览器返回的数据类型
            return HttpResponse('{"status":"success"}', content_type='application/json')
        else:
            # 如果保存失败，返回json字符串,并将form的报错信息通过msg传递到前端
            return HttpResponse('{"status":"fail", "msg":"添加出错"}', content_type='application/json')


class OrgHomeView(View):
    """
    机构首页
    """

    def get(self,request,org_id):
        # 当前页面
        current_page = 'home'
        # 根据id找到课程机构
        course_org = CourseOrg.objects.get(id=int(org_id))

        course_org.click_nums += 1
        course_org.save()

        # 判断收藏状态
        has_fav = False
        if request.user.is_authenticated:
            if UserFavorite.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2):
                has_fav = True

        all_courses = course_org.course_set.all()[:3]
        all_teachers = course_org.teacher_set.all()[:1]
        return render(request,'org-detail-homepage.html',{
            "all_courses":all_courses,
            "all_teachers":all_teachers,
            "course_org":course_org,
            "current_page":current_page,
            "has_fav":has_fav,
        })


class OrgCourseView(View):
    """
    机构课列表页
    """

    def get(self,request,org_id):
        #当前页面
        current_page = 'course'
        # 根据id找到课程机构
        course_org = CourseOrg.objects.get(id=int(org_id))
        # 判断收藏状态
        has_fav = False
        if request.user.is_authenticated:
            if UserFavorite.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2):
                has_fav = True

        all_courses = course_org.course_set.all()[:3]
        return render(request,'org-detail-course.html',{
            "all_courses":all_courses,
            "course_org":course_org,
            "current_page":current_page,
            "has_fav": has_fav,
        })


class OrgDescView(View):
    """
    机构描述页
    """

    def get(self,request,org_id):
        # 当前页面
        current_page = 'desc'
        # 根据id找到课程机构
        course_org = CourseOrg.objects.get(id=int(org_id))

        # 判断收藏状态
        has_fav = False
        if request.user.is_authenticated:
            if UserFavorite.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2):
                has_fav = True
        return render(request,'org-detail-desc.html',{
            "course_org":course_org,
            "current_page":current_page,
            "has_fav": has_fav,
        })


class OrgTeachersView(View):
    """
    机构教师页
    """

    def get(self,request,org_id):
        # 当前页面
        current_page = 'teachers'
        # 根据id找到课程机构
        course_org = CourseOrg.objects.get(id=int(org_id))
        # 判断收藏状态
        has_fav = False
        if request.user.is_authenticated:
            if UserFavorite.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2):
                has_fav = True

        all_teachers = course_org.teacher_set.all()[:1]
        return render(request,'org-detail-teachers.html',{
            "all_teachers":all_teachers,
            "course_org":course_org,
            "current_page":current_page,
            "has_fav": has_fav,
        })


class AddFavView(View):
    """
    用户收藏与取消收藏功能
    """

    def post(self,request):
        # 表明你收藏的不管是课程，讲师，还是机构。他们的id
        # 默认值取0是因为空串转int报错
        id = request.POST.get('fav_id',0)
        type = request.POST.get('fav_type',0)

        # 判断用户是否登录:即使没登录会有一个匿名的user
        if not request.user.is_authenticated:
            return HttpResponse('{"status":"fail","msg":"用户未登录"}',content_type='application/json')
        exist_records = UserFavorite.objects.filter(user=request.user,fav_id=int(id),fav_type=int(type))
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


class TeacherListView(View):
    def get(self, request):
        current_page = 'teacher'
        all_teachers = Teacher.objects.all()
        # 总共有多少老师使用count进行统计
        # 搜索功能
        search_keywords = request.GET.get('keywords', '')
        if search_keywords:
            # 在name字段进行操作,做like语句的操作。i代表不区分大小写
            # or操作使用Q
            all_teachers = all_teachers.filter(Q(name__icontains=search_keywords)|Q(work_company__icontains=search_keywords)|Q(work_position__icontains=search_keywords))

        teacher_nums = all_teachers.count()
        #人气排序
        sort = request.GET.get('sort','')
        if sort:
            all_teachers = Teacher.objects.order_by("-click_nums")
        #讲师排行榜
        sorted_teacher = Teacher.objects.all().order_by("-click_nums")[:3]
        #分页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        p = Paginator(all_teachers,4,request=request)
        teachers = p.page(page)
        return render(request, "teachers-list.html", {
            "all_teachers": teachers,
            "teacher_nums": teacher_nums,
            "current_page":current_page,
            "sorted_teacher":sorted_teacher,
        })


class TeacherDetailView(View):
    def get(self,request,teacher_id):
        teacher = Teacher.objects.get(id=int(teacher_id))
        all_courses = Course.objects.filter(teacher=teacher)

        teacher.click_nums += 1
        teacher.save()

        has_teacher_faved = False
        has_org_faved = False
        if request.user.is_authenticated:
            if UserFavorite.objects.filter(user=request.user,fav_id=teacher.id,fav_type=3):
                has_teacher_faved = True

            if UserFavorite.objects.filter(user=request.user, fav_id=teacher.org.id, fav_type=2):
                has_org_faved = True
        # 讲师排行榜
        sorted_teacher = Teacher.objects.all().order_by("-click_nums")[:3]
        return render(request, 'teacher-detail.html', {
            'teacher': teacher,
            'all_courses': all_courses,
            'sorted_teacher': sorted_teacher,
            "has_teacher_faved":has_teacher_faved,
            "has_org_faved":has_org_faved,
        })