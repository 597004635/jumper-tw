https://github.com/317828332/LuffyAudit/tree/master/audit
https://github.com/triaquae/CrazyEye
1、安装shellinbox yum -y install git openssl-devel pam-devel zlib-devel autoconf automake libtool git clone https://github.com/shellinabox/shellinabox.git && cd shellinabox autoreconf -i ./configure && make ; make install

shellinaboxd -d -t # 在后台启动，不以https模式启动
堡垒机账号修改家目录下的.bashrc，最后增加几行 
echo "---------欢迎登录运维堡垒机------------" /home/denghonglin/env/py35/bin/python3 /home/denghonglin/demo/devops/audit_shell.py echo "Bye." logout
