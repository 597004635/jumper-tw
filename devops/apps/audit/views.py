from django.shortcuts import render, redirect,HttpResponse
# from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import json, os, random, string, datetime
import zipfile
from wsgiref.util import FileWrapper #from django.core.servers.basehttp import FileWrapper

from django.conf import settings
from audit.models import Host, HostUser, HostGroup, HostUserBind, Account, AuditLog, SessionLog, Task, TaskLog, Token
from audit.unit import task_handler

from django.contrib.auth.mixins import LoginRequiredMixin
from pure_pagination.mixins import PaginationMixin
from django.views.generic import ListView
from django.db.models import Q

@login_required
def host_list(request):
    return render(request,'audit/hostlist.html')


"""api接口：获取主机列表"""
@login_required
def get_host_list(request):
    gid = request.GET.get('gid')
    if gid:
        if gid == '-1':   # 未分组
            host_list = request.user.account.host_user_binds.all()
        else:
            group_obj = request.user.account.host_groups.get(id=gid)
            host_list = group_obj.host_user_binds.all()
        data = json.dumps(list(host_list.values('id','host__hostname','host__ip_addr','host__port','host_user__username')))
        return HttpResponse(data)

"""生成token"""
@login_required
def get_token(request):
    bind_host_id = request.POST.get('bind_host_id')
    # 设置token过期时间 3H
    time_obj = datetime.datetime.now() - datetime.timedelta(seconds=10800)
    exist_token_objs = Token.objects.filter(account_id=request.user.account.id,host_user_bind_id=bind_host_id,date__gt=time_obj)
    if exist_token_objs:
        token_data = {'token':exist_token_objs[0].val}
    else:
        token_val = ''.join(random.sample(string.ascii_lowercase+string.digits,16))
        token_obj = Token.objects.create(host_user_bind_id = bind_host_id, account = request.user.account, val = token_val )
        token_data = {'token':token_val}
    return HttpResponse(json.dumps(token_data))



"""审计日志"""
class AuditLogView(LoginRequiredMixin, PaginationMixin, ListView):
    model = AuditLog
    template_name = "audit/audit_log.html"
    context_object_name = "auditlogs"
    paginate_by = 10
    keyword = ''

    def get_queryset(self):
        queryset = super(AuditLogView, self).get_queryset()
        self.keyword = self.request.GET.get('keyword', '').strip()
        if self.keyword:
            queryset = queryset.filter(Q(cmd__icontains=self.keyword)|Q(session__host_user_bind__host__hostname__icontains=self.keyword)|Q(session__account__user__username__icontains=self.keyword))
        return queryset

    def get_context_data(self, **kwargs):
        context = super(AuditLogView, self).get_context_data(**kwargs)
        context['keyword'] = self.keyword
        context['sessionLog'] = SessionLog.objects.all()
        return context


"""登录日志"""
class SessionLogView(LoginRequiredMixin, PaginationMixin, ListView):
    model = SessionLog
    template_name = "audit/session_log.html"
    context_object_name = "sessionlogs"
    paginate_by = 10
    keyword = ''

    def get_queryset(self):
        queryset = super(SessionLogView, self).get_queryset()
        self.keyword = self.request.GET.get('keyword', '').strip()
        if self.keyword:
            queryset = queryset.filter(Q(host_user_bind__host__hostname__icontains=self.keyword)|Q(account__user__username__icontains=self.keyword))
        return queryset

    def get_context_data(self, **kwargs):
        context = super(SessionLogView, self).get_context_data(**kwargs)
        context['keyword'] = self.keyword
        return context


"""任务日志"""
class TaskLogView(LoginRequiredMixin, PaginationMixin, ListView):
    model = TaskLog
    template_name = "audit/task_log.html"
    context_object_name = "tasklogs"
    paginate_by = 10
    keyword = ''

    def get_queryset(self):
        queryset = super(TaskLogView, self).get_queryset()
        self.keyword = self.request.GET.get('keyword', '').strip()
        if self.keyword:
            queryset = queryset.filter(Q(host_user_bind__host__hostname__icontains=self.keyword))
        return queryset

    def get_context_data(self, **kwargs):
        context = super(TaskLogView, self).get_context_data(**kwargs)
        context['keyword'] = self.keyword
        return context



"""批量命令"""
@login_required
def multi_cmd(request):
    return render(request,'audit/multi_cmd.html')


"""任务"""
@login_required
def multitask(request):
    task_obj = task_handler.TaskHandle(request)
    if task_obj.is_valid():
        task_obj = task_obj.run()
        return HttpResponse(json.dumps({'task_id':task_obj.id, 'timeout':task_obj.timeout}))
    return HttpResponse(json.dumps(task_obj.errors))


"""获取任务结果"""
@login_required
def multitask_result(request):
    task_id = request.GET.get('task_id')
    task_obj = Task.objects.get(id=task_id)
    results = list(task_obj.tasklog_set.values('id','status','host_user_bind__host__hostname','host_user_bind__host__ip_addr','result'))
    return HttpResponse(json.dumps(results))
