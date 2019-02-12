#!/usr/bin/env python
#coding=utf-8   

from binascii import hexlify
from paramiko.py3compat import input
from audit.models import SessionLog
import base64, getpass, os, sys, time, select
import traceback, paramiko, socket


try:
    import interactive
except ImportError:
    from . import interactive

# 密钥认证
def manual_auth(t, username):
    #path = os.path.join(os.environ["HOME"], ".ssh", "id_rsa")
    path = os.path.join("/root", ".ssh", "id_rsa")
    print("path:",path)
    try:
        key = paramiko.RSAKey.from_private_key_file(path)
    except paramiko.PasswordRequiredException:
        password = getpass.getpass("RSA key password: ")
        key = paramiko.RSAKey.from_private_key_file(path, password)
    t.auth_publickey(username, key)


def ssh_session(bind_host_user, user_obj):
    hostname = bind_host_user.host.ip_addr
    port = bind_host_user.host.port
    username = bind_host_user.host_user.username
    password = bind_host_user.host_user.password
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((hostname, port))
    except Exception as e:
        print("\033[31;2m*** Connect Failed: %s\033[0m" %str(e))
        traceback.print_exc()
        sys.exit(1)

    try:
        t = paramiko.Transport(sock)
        try:
            t.start_client()
        except paramiko.SSHException:
            print("\033[33;2m*** SSH negotiation failed. ***\033[0m")
            sys.exit(1)
        try:
            keys = paramiko.util.load_host_keys(os.path.expanduser("~/.ssh/known_hosts"))
        except IOError:
            try:
                keys = paramiko.util.load_host_keys(os.path.expanduser("~/ssh/known_hosts"))
            except IOError:
                print("\033[31;2m*** Unable to open host keys file ***\033[0m")
                keys = {}

        key = t.get_remote_server_key()
        if hostname not in keys:
            pass
        elif key.get_name() not in keys[hostname]:
            pass
        elif keys[hostname][key.get_name()] != key:
            print("\033[33;2m*** WARNING: Host key has changed! ***\033[0m")
            sys.exit(1)
        else:
            print("\033[32;2m*** Host key OK. ***\033[0m")

        if not t.is_authenticated():
            manual_auth(t, username)
        if not t.is_authenticated():
            print("\033[31;2m*** Authentication failed. ***\033[0m")
            t.close()
            sys.exit(1)
        chan = t.open_session()
        chan.get_pty()
        chan.invoke_shell()
        print("\033[32;2m*** Welcome to login %s ...\033[0m" %hostname)

        session_obj = SessionLog.objects.create(account=user_obj.account,host_user_bind=bind_host_user)
        interactive.interactive_shell(chan, session_obj)
        chan.close()
        t.close()

    except Exception as e:
        print("\033[33;2m*** Caught exception: \033[0m" + str(e.__class__) + ": " + str(e))
        traceback.print_exc()
        try:
            t.close()
        except:
            pass
        sys.exit(1)
