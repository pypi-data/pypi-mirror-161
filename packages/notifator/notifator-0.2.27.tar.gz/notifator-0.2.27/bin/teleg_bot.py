#!/usr/bin/env python3
"""
A simple telegram bot -  use as "say ahoj".
Commands /saytime /bustime /who ...
can be defined via /setcommands in @Fatherbot -
- see /help
"""

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import os
from configparser import ConfigParser

from fire import Fire

import socket

from notifator import notify
import datetime

def load_config( mysection ):
    configur = ConfigParser()
    tokenpath = "~/.telegram.token"
    ok  = False
    try:
        print(os.path.expanduser(tokenpath))
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



# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update, context):
    """Send a message when the command /start is issued."""
    myname=socket.gethostname()
    print("D... starting, myname", myname)
    update.message.reply_text('Hi, '+myname +" ready!")


def help_command(update, context):
    """Send a message when the command /help is issued."""
    hlp = """ Define these commands in @Fatherbot via /setcommand :
saytime - say time
bustime - dbus time show
who - who is listenning
say_hello - say it
bus_hello - dbus message
    """
    update.message.reply_text('help_command launched \n\n'+hlp)


def say(update, argument):
    myname=socket.gethostname()
    print("D... argument", argument)
    notify.issue_sound(argument)
    update.message.reply_text("from:"+myname+" ... I tried to read it")


def bus(update, argument):
    myname=socket.gethostname()
    print("D... argument", argument)
    notify.issue_dbus(argument)
    update.message.reply_text("from:"+myname+" ... I tried to display it on dbus")



def say_command(update, context):
    """Send a message when the command /say is issued."""
    #update.message.reply_text('say_command  launched '+update.message.text)
    say(update,"halo!")

def saytime_command(update, context):
    """Send a message when the command /say is issued."""
    #update.message.reply_text('say_command  launched '+update.message.text)
    hour = datetime.datetime.now().strftime("%H:%M")
    say(update, hour )


def bus_command(update, context):
    """Send a message when the command /bus is issued."""
    #update.message.reply_text('bus_command  launched '+update.message.text)
    bus(update,"halo!")

def bustime_command(update, context):
    """Send a message when the command /bus is issued."""
    #update.message.reply_text('bus_command  launched '+update.message.text)
    hour = datetime.datetime.now().strftime("%H:%M")
    bus(update,hour)


def who_command(update, context):
    """Send a message when the command /who is issued."""
    #update.message.reply_text('who_command  launched '+update.message.text)
    myname=socket.gethostname()
    #print("D... argument", argument)
    update.message.reply_text(myname+": is ready")


def echo(update, context):
    """Echo the user message."""
    pic=os.path.expanduser('~/Figure_1.png')
    # PIC HERE
    # context.bot.send_photo(chat_id=update.effective_chat.id, photo=open(pic,'rb'))
    ###context.message.sendPhoto(photo="url_of_image",
    ###                      caption="This is the test photo caption")

    mmm = update.message.text
    print("D... message",mmm, mmm.lower().find("say "))
    if mmm.lower().find("say ")==0:
        argument = mmm[4:]
        say(update, argument)
    elif mmm.lower().find("bus ")==0:
        argument = mmm[4:]
        bus(update,argument)
    else:
        myname=socket.gethostname()
        update.message.reply_text("echo from:"+myname+": "+mmm)


def main(section):
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary

    token,chatid=load_config(section)
    updater = Updater(token,
                      use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("say_hello", say_command))
    dp.add_handler(CommandHandler("saytime", saytime_command))
    dp.add_handler(CommandHandler("bus_hello", bus_command))
    dp.add_handler(CommandHandler("bustime", bustime_command))
    dp.add_handler(CommandHandler("who", who_command))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    Fire( main )
