from django.shortcuts import render
from django.http import HttpResponseRedirect,JsonResponse
from django.core.urlresolvers import reverse
from django.views.generic import View
from django.contrib.auth import authenticate,login,logout
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import LoginForm
from  dashboard.models import  UserProfile
from django.db.models import Count, Q
from collections import Counter
import  time
from django.utils.timezone import now, timedelta
from datetime import datetime,timedelta, date


''' 登录模块 '''
class LoginView(View):
    def get(self, request):
        return render(request, "login.html")

    def post(self, request):
        res = {"code": 0}
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            username = request.POST.get("username", None)
            password = request.POST.get("password", None)
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    res['next_url'] = '/'
                else:
                    res['code'] = 1
                    res['errmsg'] = '用户被禁用'
            else:
                res['code'] = 1
                res['errmsg'] = '用户名或密码错误'
        else:
            res['code'] = 1
            res['errmsg'] = "用户名或密码不能为空"
        return JsonResponse(res, safe=True)


class LogoutView(LoginRequiredMixin,View):
    """
        登出

        关于用户登录验证两种方式：
        1：基于全类所有方法生效的可以利用LoginRequiredMixin
        2：基于类里面某个函数的可以用login_required
    """
    @method_decorator(login_required)
    def get(self, request):
        logout(request)
        return HttpResponseRedirect(reverse("login"))

''' 首页'''
class IndexView(View):
    @method_decorator(login_required(login_url="login"))
    def get(self, request, **kwargs):
        # print(order_counts)
        return render(request, 'index.html')


