from django.shortcuts import render
from django.views.generic import TemplateView, View, ListView, DetailView
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse, Http404, QueryDict
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin
from pure_pagination.mixins import PaginationMixin
from django.db.models import Q
from django.core.urlresolvers import reverse
import json,logging,traceback
import os


from games.models import GameServer
from django.conf import settings
from games.forms import GameServerfileForm, GameServerUpdateForm
from .shell.ssh_cmd import op_game

logger = logging.getLogger('opsweb')

"""区服列表"""
class GameServerListView(LoginRequiredMixin, PaginationMixin, ListView):
    model = GameServer
    template_name = "games/games_server_list.html"
    context_object_name = "gslist"
    paginate_by = 20
    keyword = ''

    def get_queryset(self):
        queryset = super(GameServerListView, self).get_queryset()
        self.keyword = self.request.GET.get('keyword', '').strip()
        if self.keyword:
            queryset = queryset.filter(Q(channel__icontains=self.keyword) |
                                       Q(servername__icontains=self.keyword) |
                                       Q(inner_ip__icontains=self.keyword))
        return queryset

    def get_context_data(self, **kwargs):
        context = super(GameServerListView, self).get_context_data(**kwargs)
        context['keyword'] = self.keyword
        return context


    def post(self, request):
        data = (request.POST.dict())
        data['status'] = 0
        webdata  =  GameServerfileForm(data)
        if webdata.is_valid():
            webdata.save()
            res = {'code': 0, 'result': '区服添加成功'}
        else:
            res = {'code': 1, 'errmsg': webdata.errors}
        return JsonResponse(res)


    # 删除
    def delete(self, request, *args, **kwargs):
        try:
            server_obj = GameServer.objects.get(pk=QueryDict(request.body)['id']).delete()
            res = {'code': 0, 'result': '删除成功'}
        except self.model.DoesNotExist:
            res = {'code': 1, 'errmsg': '信息不存在'}
        return JsonResponse(res)


"""区服更新"""
class GameServerDetailView(LoginRequiredMixin, DetailView):
    model = GameServer
    template_name = "games/games_server_edit.html"
    context_object_name = "gameserver_obj"
    next_url = '/games/gameslist/'

    def post(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        p = self.model.objects.get(pk=pk)
        form = GameServerUpdateForm(request.POST, instance=p)
        if form.is_valid():
            form.save()
            res = {"code": 0, "result": "更新成功", 'next_url': self.next_url}
        else:
            res = {"code": 1, "errmsg": form.errors, 'next_url': self.next_url}
            logger.error("update idc  error: %s" % traceback.format_exc())
        return render(request, settings.JUMP_PAGE, res)


''' 关停服务'''
class ModifyGameStatusView(View):

    def post(self, request):
        uid = request.POST.get("uid","")
        ret = {"status":0}
        try:
            game_obj = GameServer.objects.get(id=uid)
            hostip = GameServer.objects.get(id=uid).inner_ip
            if game_obj.status:
                cmd_str = "sh /data/games/shark.sh stop"
                game_obj.status = 0
            else:
                cmd_str = "sh /data/games/shark.sh start"
                game_obj.status = 1

            op_game(hostip,cmd_str)
            game_obj.save()
        except GameServer.DoesNotExist:
            ret['status'] = 1
            ret['errmsg'] = "区服不存在"
        return JsonResponse(ret, safe=True)
