import paramiko,os
 
def check_game( host_ip):
    # op_arg = ['ssh',ip,cmd]
    # process = subprocess.Popen(op_arg, shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    port = 36000
    username = 'root'
    key_file = '/root/.ssh/id_rsa'
    cmd_str = 'pgrep -f SharkServer.exe|wc -l'
    #cmd_str = 'ifconfig'
    key = paramiko.RSAKey.from_private_key_file(key_file)
    try:
        ssh = paramiko.SSHClient()
        ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        pkey = paramiko.RSAKey.from_private_key_file(key_file)
        ssh.connect(host_ip, port, username, pkey=key, timeout=30)
        stdin, stdout, stderr = ssh.exec_command(cmd_str)
     #   print("stdin--- ",stdin.readlines())
     #   print("stdout--- ",stdout.readlines())
     #   print("stderr--- ",stderr.readlines())
        result = stdout.read()
        #result1 = stdin.readlines()
        #result2 = stderr.readlines()
        print("check_result: %s" %result)
        #print("check_result: %s" %result)
        #print("stdin: ", result1)
        #print("stderr: ", result2)
        ssh.close()
    except Exception as e:
        print("\033[31m%s login faild!\033[0m" % host_ip)
   # finally:
   #     ssh.close()
    #return result

def c(hostip):
    cmd = '''ssh -p36000 %s "pgrep -f SharkServer.exe|wc -l" ''' %hostip
    r = os.popen(cmd).read().replace("\n","")
   # r = os.popen(cmd).readlines()

    print("c ---------- ",r)
if __name__ == "__main__":
    hostip = "172.16.16.17"
    check_game(hostip)
    c(hostip)
   
