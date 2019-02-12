#coding=utf-8   
from django.contrib.auth import authenticate
from django.conf import settings
from audit.models import Token
from audit.unit.ssh_interactive import ssh_session
import subprocess, random, string, datetime, sys
from django.contrib.auth import get_user_model
User = get_user_model()



class UserShell(object):
    """ 用户登录堡垒机后的shell"""
    def __init__(self,sys_argv):
        self.sys_argv = sys_argv
        self.user = None

    def auth_tgsw(self,user_name):
        dic_pwd = {'tgsw': 'Dsz2q_bReTo2G','denghonglin':'Chujian88@','chendongdong':'Chujian88@','wanghaicheng':'Chujian88@'}
        username = user_name
        password = dic_pwd[username]
        user = authenticate(username=username, password=password)
        if not user:
            print("\033[31;2mInvalid username or password!\033[0m")
        else:
            self.user = user
            return True


        """token登录(略)"""

    def start(self,user_name):
        """用户名密码登录"""
        if self.auth_tgsw(user_name):
            while True:
                host_groups = self.user.account.host_groups.all()
                print("\n\033[36;2m====== 欢迎登录《太古神王》堡垒机 ============\033[0m")
                print("\033[33;2mPlease select group host (Quit: Enter 'exit/q')\033[0m")
                for index, group in enumerate(host_groups):
                    print("%s.\t%s [%s]" %(index, group, group.host_user_binds.count()))
                print("%s.\tOther [%s] " %(len(host_groups),self.user.account.host_user_binds.count()))
                try:
                    choice = input("\033[33;2mPlease select number:\033[0m").strip()
                    if choice.isdigit():
                        choice = int(choice)
                        host_bind_list = None
                        if choice >= 0 and choice < len(host_groups):
                            selected_group = host_groups[choice]
                            host_bind_list = selected_group.host_user_binds.all()
                        elif choice == len(host_groups):
                            host_bind_list = self.user.account.host_user_binds.all()
                        if host_bind_list:
                            while True:
                                print("\n\033[33;3mPlease select host (Quit: Enter 'exit/q')\033[0m")
                                for index, host in enumerate(host_bind_list):
                                    # print("\t\t%s.\t%s" %(index,host))
                                    print("%s.\t%s ( %s )" % (index, host.host.hostname, host.host.ip_addr))
                                choice1 = input("\033[33;2mPlease select number:\033[0m").strip()
                                if choice1.isdigit():
                                    choice1 = int(choice1)
                                    if choice1 >= 0 and choice1 < len(host_bind_list):
                                        selected_host = host_bind_list[choice1]
                                        ssh_session(selected_host,self.user)
                                elif choice1 == 'b':
                                    break
                                elif choice1 == 'q' or choice1 == 'exit':
                                    sys.exit(1)

                    if choice == 'exit'or choice == 'q':
                        break

                except KeyboardInterrupt as e:
                    pass
