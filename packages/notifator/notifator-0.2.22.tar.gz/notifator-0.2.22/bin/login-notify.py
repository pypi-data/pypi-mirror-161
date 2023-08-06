#!/usr/bin/python3
#login-notify.sh
#https://askubuntu.com/questions/179889/how-do-i-set-up-an-email-alert-when-a-ssh-login-is-successful
#
# chmod +x login-notify.sh
# EDIT: /etc/pam.d/sshd  AND APPEND
# session optional pam_exec.so seteuid /path/to/login-notify.sh
#session optional pam_exec.so seteuid /etc/postfix/login-notify.py
#
#$PAM_USER from $PAM_RHOST on $host"
#subject="LOGIN: $PAM_USER from $PAM_RHOST on $host"
#subject="$PAM_USER@$host from $PAM_RHOST"

with open("/tmp/login-notify.log","a") as f:
    f.write("Ahoj1-----------------------------------\n")
import os
import socket
import requests


from notifator import telegram
from fire import Fire



def sendmess():
    host=socket.gethostname()
    rhost="unknown"
    user="unknown"
    print("D... host=",host)
    if 'PAM_RHOST' in os.environ:
        rhost=os.environ['PAM_RHOST']
    if 'PAM_USER' in os.environ:
        user=os.environ['PAM_USER']

    telegram.bot_send("Logins", user +"@"+host+" from *"+rhost+"*")

    with open("/tmp/login-notify.log","a") as f:
        f.write(user+host+rhost+"FINALE===============\n")


##################################################
##################################################
##################################################
##################################################
##################################################
if __name__=="__main__":
    Fire( sendmess )
