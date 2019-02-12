from django.conf.urls import url, include
from audit.views import host_list, get_host_list, get_token, AuditLogView, SessionLogView, TaskLogView, multi_cmd, multitask, multitask_result

urlpatterns = [
    url('^hostlist/$', host_list, name='host_list'),
    url('^api/hostlist/$', get_host_list, name='get_host_list'),
    url('^api/token/$', get_token, name='get_token'),
    url('^auditlog/$', AuditLogView.as_view(), name='audit_log'),
    url('^sessionlog/$', SessionLogView.as_view(), name='session_log'),
    url('^tasklog/$', TaskLogView.as_view(), name='task_log'),

    url('^multitask/cmd/$', multi_cmd, name='multi_cmd'),
    url('^multitask/$', multitask, name='multitask'),
    url('^multitask/result/$', multitask_result, name='get_task_result'),
]
