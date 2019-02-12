import time
import sys ,os, json
import multiprocessing
import paramiko

def cmd_run(tasklog_id, task_id, cmd_str):
    try:
        import django
        django.setup()
        from audit.models import TaskLog
        tasklog_obj = TaskLog.objects.get(id=tasklog_id)
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(tasklog_obj.host_user_bind.host.ip_addr,
                    tasklog_obj.host_user_bind.host.port,
                    tasklog_obj.host_user_bind.host_user.username,
                    tasklog_obj.host_user_bind.host_user.password,
                    timeout=15)
        stdin, stdout, stderr = ssh.exec_command(cmd_str)
        result = stdout.read() + stderr.read()
        ssh.close()
        tasklog_obj.result = result or 'cmd has no result output.'
        tasklog_obj.status = 0
        tasklog_obj.save()

    except Exception as e:
        print("error: ",e)

#def file_transfer(tasklog_id,task_id,task_content): pass

if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))) )
    sys.path.append(BASE_DIR)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "devops.settings")
    import django
    django.setup()

    from audit.models import Task
    task_id = sys.argv[1]

    """
    1. 根据Taskid拿到任务对象.
    2. 拿到任务关联的所有主机.
    3. 根据任务类型调用多进程 执行不同的方法.
    4. 每个子任务执行完毕后，自己把结果写入数据库.
    """
    task_obj = Task.objects.get(id=task_id)
    pool = multiprocessing.Pool(processes=4)

    if task_obj.task_type == 0:
        task_func = cmd_run
    else:
        task_func = file_transfer

    for tasklog_obj in task_obj.tasklog_set.all():
        pool.apply_async(task_func, args=(tasklog_obj.id,task_obj.id,task_obj.content))
    pool.close()
    pool.join()

