import paramiko

def op_game( host_ip, cmd_str):
    port = 36000
    username = 'root'
    key_file = '/root/.ssh/id_rsa'
    key = paramiko.RSAKey.from_private_key_file(key_file)
    try:
        ssh = paramiko.SSHClient()
        ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        pkey = paramiko.RSAKey.from_private_key_file(key_file)
        ssh.connect(host_ip, port, username, pkey=key, timeout=30)
        stdin, stdout, stderr = ssh.exec_command(cmd_str)
    except Exception as e:
        print("\033[31m%s login faild!\033[0m" % host_ip)
    finally:
        ssh.close()
