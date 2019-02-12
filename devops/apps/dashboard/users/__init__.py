from django.views.generic import ListView, DetailView, CreateView,TemplateView, View
from django.db.models import Q
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse, QueryDict,Http404
from django.core.urlresolvers import reverse
from django.shortcuts import render
from pure_pagination.mixins import PaginationMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import  Permission,Group
from django.core import serializers
import json
import logging
import traceback

''' 导入自定义模块 '''
from django.conf import settings
from dashboard.models import UserProfile
from dashboard.forms import UserProfileForm, UserUpdateForm, UserPwdForm

logger = logging.getLogger('opsweb')


'''  用户列表'''
class UserListView(LoginRequiredMixin, PaginationMixin, ListView):
    model = UserProfile
    template_name = "dashboard/user/user_list.html"
    context_object_name = "userlist"
    paginate_by = 10
    keyword = ''

    def get_queryset(self):
        queryset = super(UserListView, self).get_queryset()
        self.keyword = self.request.GET.get('keyword', '').strip()
        if self.keyword:
            queryset = queryset.filter(Q(username__icontains=self.keyword) |
                                       Q(name_cn__icontains=self.keyword))
        return queryset


    def get_context_data(self, **kwargs):
        context = super(UserListView, self).get_context_data(**kwargs)
        context['keyword'] = self.keyword
        return context

    def post(self, request):
        data = (request.POST.dict())
        password = data['password']
        data['password'] = make_password(data['password'])
        webdata  =  UserProfileForm(data)
        if webdata.is_valid():
            webdata.save()
            res = {'code': 0, 'result': '用户添加成功'}
        else:
            res = {'code': 1, 'errmsg': webdata.errors}
        return JsonResponse(res)

    def delete(self, request, *args, **kwargs):
        try:
            idc_obj = UserProfile.objects.get(pk=QueryDict(request.body)['id']).delete()
            res = {"code": 0,'result':'用户删除成功'}
        except UserProfile.DoesNotExist:
            res = {"code": 1, "errmsg": "用户不存在"}
        return JsonResponse(res)



''' 更新用户信息'''
class UserDetailView(LoginRequiredMixin, DetailView):
    model = UserProfile
    template_name = "dashboard/user/user_edit.html"
    context_object_name = 'user'
    next_url = '/dashboard/userlist/'

    def post(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        p = self.model.objects.get(pk=pk)
        form = UserUpdateForm(request.POST, instance=p)
        if form.is_valid():
            form.save()
            res = {"code": 0, "result": "更新成功", 'next_url': self.next_url}
        else:
            res = {"code": 1, "errmsg": form.errors, 'next_url': self.next_url}
            logger.error("delete power  error: %s" % traceback.format_exc())
        return render(request, settings.JUMP_PAGE, res)


''' 修改密码'''
class ModifyPwdView(LoginRequiredMixin, TemplateView):
    model =  UserProfile
    next_url = '/dashboard/userlist/'
    template_name = "dashboard/user/change_passwd.html"
    
    def get_context_data(self, **kwargs):
        context = super(ModifyPwdView, self).get_context_data(**kwargs)
        uid = self.request.GET.get("uid", None)
        try:
            user_obj = self.model.objects.get(pk=uid)
            context['user'] = user_obj
            context['uid'] = uid
        except BaseException as e:
            context['msg'] = '用户ID 不存在'
        return context

    def post(self, request, **kwargs):
        pk = self.request.POST.get("uid", None)
        data = (request.POST.dict())

        if pk and data['password1'] == data['password2']:
            data['password'] = make_password(data['password1'])
            user_obj = UserProfile.objects.get(pk=pk)
            form = UserPwdForm(data, instance=user_obj)
            if form.is_valid():
                form.save()
                res = {"code": 0, "result": "更新成功", 'next_url': self.next_url}
            else:
                res = {"code": 1, "errmsg": form.errors, 'next_url': self.next_url}

        else:
            res = {"code": 1, "errmsg": '两次密码不一致 或 用户不存在', 'next_url': self.next_url}
        return render(request, settings.JUMP_PAGE, res)


'''修改用户权限'''
class  UserGroupPowerView(LoginRequiredMixin, DetailView):
    model =  UserProfile
    next_url = '/dashboard/userlist/'
    template_name = "dashboard/user/user_group_power.html"
    context_object_name =  'user'

    def get_context_data(self, **kwargs):
        context = super(UserGroupPowerView, self).get_context_data(**kwargs)
        context['user_has_groups'], context['user_has_permissions'] = self.get_user_group()
        context['user_not_groups'], context['user_not_permissions'] = self.get_user_not_group()
        return context
    def get_user_group(self):
        pk = self.kwargs.get(self.pk_url_kwarg)
        try:
            user = self.model.objects.get(pk=pk)
            return user.groups.all(), user.user_permissions.all()
        except self.model.DoesNotExist:
            raise   Http404

    def get_user_not_group(self):
        pk = self.kwargs.get(self.pk_url_kwarg)
        try:
            user = self.model.objects.get(pk=pk)
            all_group = Group.objects.all()
            groups = [group for group in  all_group if group not in user.groups.all()]
            all_perms = Permission.objects.all()
            perms = [perm for perm  in all_perms if  perm not in user.user_permissions.all()]
            return  groups, perms
        except:
            return  JsonResponse([], safe=False)

    def post(self, request, *args, **kwargs):
        group_id_list = request.POST.getlist('groups_selected',[])
        permission_id_list =  request.POST.getlist('perms_selected',[])
        pk = kwargs.get('pk')
        try:
            user = self.model.objects.get(pk=pk)
            user.groups = group_id_list
            user.user_permissions = permission_id_list
            res = {"code": 0, "result": "用户角色权限更新成功", 'next_url': self.next_url}
        except:
            res = {"code": 1, "errmsg": "用户角色权限更新失败", 'next_url': self.next_url}
            logger.error('edit user group pwoer error: %s' % traceback.format_exc())

        return render(request, settings.JUMP_PAGE, res)



''' 修改用户状态（正常/禁用）'''
class ModifyUserStatusView(View):
    def post(self, request):
        uid = request.POST.get("uid","")
        ret = {"status":0}
        try:
            user_obj = UserProfile.objects.get(id=uid)
            if user_obj.is_active:
                user_obj.is_active = False 
            else:
                user_obj.is_active = True
            user_obj.save()
        except UserProfile.DoesNotExist:
            ret['status'] = 1
            ret['errmsg'] = "用户不存在"
        return JsonResponse(ret, safe=True)


class UserListApiView(View):
    def get(self, request):
        users = UserProfile.objects.all()
        return HttpResponse(serializers.serialize('json', users), content_type='application/json')
