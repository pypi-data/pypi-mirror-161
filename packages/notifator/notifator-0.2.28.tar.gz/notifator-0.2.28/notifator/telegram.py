#!/usr/bin/env python3
# -fire CLI
from fire import Fire
from notifator.version import __version__

import cv2
import requests
import os

#----------------- text config file --------
from configparser import ConfigParser

import numpy as np
import datetime as dt

import re  # escape markdown


"""
Practical:
 - In botfather do /newbot
 - NAME
 - NAMEbot
 - Click the bot link in telegram and start it (big button is ok)
 - https://api.telegram.org/bot123456789:AA..4Q/getUpdates
 - if started, it shows info... also "chat":{"id":133760184,...
 - but, all my chats have the same id....
 - the link to it seems to be t.me/NAMEbot
------------------------------------------

The trick:  In Botfather, create /newbot,
 - select a name Btrfs
 - select a username Btrfsbot

- start the bot in telegram - in @Father /mybots,
  click @Brtfsbot, press start or /start

1- remember the API key
from API on web
https://api.telegram.org/bot123456789:AA..4Q/getUpdates
- already after start it should give chatid
- chatid seems be the same for all

LEVEL2:
==================================================
pip3 install python-telegram-bot


OLD:
==================================================
- start the bot in telegram - /mybots...
- possibly send some text from phone...
/start
neco
/getUpdates
https://api.telegram.org/bot123456789:AA..J4Q/getMe
-
2- remember the chat_id
3- put APIkey and chat_id to ~/.telegram.token
...
markdown doesnt work with multiline
YES, just give double \n\n
"""


# print("i... module notifator/telegram is being run")

def func():
    print("D... function defined in notifator:telegram")
    return True

def test_func():
    print("D... test function ... run pytest")
    assert func()==True




def load_config( mysection ):
    configur = ConfigParser()
    tokenpath = "~/.telegram.token"
    ok  = False
    try:
        print("D... confing path",os.path.expanduser(tokenpath))
        configur.read(os.path.expanduser(tokenpath) )
        ok = True
    except:
        print("X... cannot read the config from file ",tokenpath)
    if not ok:
        quit()

    sections=configur.sections()
    if mysection in sections:
        token = configur.get( mysection, "token")
        chatid = configur.get( mysection, "chatid")
        return token, chatid
    else:
        print("X... section not found: ", mysection)
        print("X... possible sections:", sections)
        quit()



# def get_token():
#     tokenpath="~/.telegram.token"
#     try:
#         with open( os.path.expanduser(tokenpath) ) as f:
#             res=f.readlines()
#     except:
#         print("X... cannot read",tokenpath)
#         quit()
#     res=[ x.strip() for x in res]
#     token,chat_id=res
#     print( token, chat_id)
#     return token, chat_id


def bot_send(section, bot_message, bot_photo="" , parsemode = "markdown"):
    """
    Telegram send. Parameters: Bot (Btrfs), Message (Blabla)
   parsemode markdown makes lot of problems
    """
    if bot_message=="":
        print("X... zero message")
        quit()
#    bot_token, bot_chatID= get_token()
    bot_token, bot_chatID= load_config(section)
    #    bot_token = ''
    #    bot_chatID = ''



    #bot_message = re.escape( bot_message )
# '_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!'


    ### filename = ""
    if (type(bot_photo)==np.ndarray):
        filename = f"/tmp/flashcam_{dt.datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        print(f"i... (tele:) writing ndarr image {filename}")
        cv2.imwrite(filename, bot_photo)
        bot_photo = filename

    if (bot_photo==""): #======= NO PHOTO =============
        url='https://api.telegram.org/bot' + bot_token + '/sendMessage'
        payload = {'chat_id':bot_chatID,
#                   "parse_mode": parsemode,  # "markdown"
                   'text':bot_message}
#        send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=MarkdownV2&text=' + bot_message

        print("i... ",url)
        print("i... ",payload)
        requests.packages.urllib3.disable_warnings()
        response = requests.post(url,  data=payload, verify=False)
        #response = requests.get(send_text)


    else: #====================YES PHOTO================
        if not os.path.isfile(bot_photo):
            print("X... cannot find picture", bot_photo)
            quit()

        files = {'photo': open(bot_photo, 'rb')}
        payload = {'chat_id':bot_chatID,
#                   "parse_mode": "markdown",
                   'caption':bot_message}
        url='https://api.telegram.org/bot' + bot_token + '/sendPhoto'
        print("i... ",url)
        print("i... ",payload)
        response = requests.post(url, files=files, data=payload, verify=False)
        # print( response )
    #----------------------
    print("D... returning response")
    return response.json()














if __name__=="__main__":
#    print("D... in main of project/module:  notifator/telegram ")
    print("D... notifator version :", __version__ )
    #Fire(  )
    Fire({"send":bot_send,
 #         "get_token":get_token,
          "load":load_config,
    }
    )
