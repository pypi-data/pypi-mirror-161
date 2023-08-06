#!/usr/bin/python3
#myservice_description: global notificator/in development
#
#   I need to combine with the advanced RPIHAT (running invisibly in screen)
#
#
import notify2
#sudo aptitude install python3-notify2

import time
#from multiprocessing import Queue
from queue import LifoQueue, Queue, Empty, Full
import os

import glob
import subprocess

from fire import Fire

from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play

from pydub.utils import make_chunks

import re
from notifator import notihat





class ScreenTool:
    servlist=[]
    def __init__(self):
        res=self.check_myservice()
        print("i... "+str(len(res))+" screens seen for the user")
        print( "i... : {}\n".format(res ) )


    def check_myservice(self):
        #### CMD="screen -ls "+self.screenname
        user_name = os.getenv('USER')
        res=glob.glob( "/var/run/screen/S-"+user_name+"/*" )
        res=[os.path.basename(x) for x in res] # 4321.myservice_
        shortres=["".join(x.split(".")[1:]) for x in res]
        self.servlist=res
        return res


    def run_screen(self, name, cmd):
        self.screenname=name
        print("i... starting screen")
        CMD=cmd
        print("D...  --- ",CMD)
        CMD='/usr/bin/screen -dmS '+self.screenname+' bash -c  "'+CMD+'"'
        print( CMD )
        ok=False
        #try:
        subprocess.check_call( CMD, shell=True )
        ok=True
        print("i...      run ok ")
        print("i...  screen STARTED")
        #except:
        #print("X...      xxx... screen  PROBLEM")






class NotifyClass(object):

    def __init__(self, dest, message, timeshow = 10, color = 1.1):
        print("D... notifator target/message:",dest,"/",message)
        self.dest = dest
        self.message = message
        self.timeshow = timeshow
        self.color = color


    def audio(self, lang="cs"):
        """
Use google etxt to speech, not too frequently. Creates an mp3 in /tmp and reads it
        """
        #print("@"+self.audio.__name__, end='')
        t = re.compile("[a-zA-Z0-9.,_-]")
        #unsafe = "abc∂éåß®∆˚˙©¬ñ√ƒµ©∆∫ø"
        unsafe=self.message
        safe = [ch for ch in unsafe if t.match(ch)]
        safe = "".join(safe)

        outfile="/tmp/msg_"+safe+".mp3"
        if not os.path.isfile(outfile):
            print("D... contacting google...")
            tts=gTTS( self.message+"." , lang=lang)
            tts.save(outfile)
        else:
            print("D... taking sound from /tmp/"+outfile)

        # read it
        path_to_file = outfile
        song = AudioSegment.from_mp3(path_to_file)
        play(song+8)

        return self.message

    def dbus(self):
        #print("@"+self.dbus.__name__+' ', end='')
        notify2.init("--Title--")
        #notice = notify2.Notification(self.dest, self.message)
        notice = notify2.Notification( self.message )
        notice.show()
        time.sleep(0.1)
        return self.message

    def hat(self):
        #print("@"+self.hat.__name__+'  ', end='')
        print("D... HAT ON")
        notihat.main(message=self.message,
                     timeshow=self.timeshow,
                     color = self.color)
        return self.message


    def web(self):
        #print("@"+self.web.__name__+'  ', end='')
        return self.message

    def term(self):
        """
        add the user to tty group to be able to listen
        usermod -a -G tty  user
        """

        #print("@"+self.term.__name__+' ', end='')
        msg=self.message
        print(msg)
        msg=msg.replace('"',' ')
        msg=msg.replace('\\',' ')
        msg=msg.replace('|',' ')
        msg=msg.replace('$',' ')
        msg=msg.replace('#',' ')
        msg=msg.replace('`',' ')
        msg=msg.replace("'",' ')
        os.system('echo "'+msg+'" | wall')
        return self.message

#============ this RUNS the message on destination. Call do
    def do( self ):
        return getattr(NotifyClass, self.dest)(self)




def issueall(message):
    """Issues message to all: audio, dbus, hat, term
    """
    q = Queue(6)   # how does this work?

    q.put( NotifyClass('audio',message) )
    #q.put( NotifyClass('dbus' ,'notify-send way - works with gtk') )
    q.put( NotifyClass('dbus' ,   message  ) )
    q.put( NotifyClass('hat'  , 'Init sense hat and display') )
    #q.put( NotifyClass('web'  , 'connect to webpy.py') )
    q.put( NotifyClass('term' , message) )

    #================== RPIHAT PART
    #s=ScreenTool()
    #s.run_screen("sleeptest","sleep 10") # this can contain rpihat...

    while not q.empty():
        res=q.get().do()
        #print("   ", res)

def issue_hat(message, timeshow = 13, color = 1.1):
    """ Issues a message to RpiHAT (or the emulator)
    """
    print("D... issue_hat")
    q = Queue(6)
    print(q)
    q.put( NotifyClass('hat', message, timeshow , color) )
    print("D... hat in queue")
    while not q.empty():
        res=q.get().do()

def issue_sound(message):
    """Issues a message to speech translator
    """
    q = Queue(6)   # how does this work?

    q.put( NotifyClass('audio',message) )
    #q.put( NotifyClass('dbus' ,'notify-send way - works with gtk') )
    #q.put( NotifyClass('dbus' ,   message  ) )
    #q.put( NotifyClass('hat'  , 'Init sense hat and display') )
    #q.put( NotifyClass('web'  , 'connect to webpy.py') )
    #q.put( NotifyClass('term' , message) )

    while not q.empty():
        res=q.get().do()

def issue_dbus(message):
    """Issues a message to DBUS system (crash on RPi)
    """
    q = Queue(6)   # how does this work?

    #q.put( NotifyClass('audio',message) )
    #q.put( NotifyClass('dbus' ,'notify-send way - works with gtk') )
    q.put( NotifyClass('dbus' ,   message  ) )
    #q.put( NotifyClass('hat'  , 'Init sense hat and display') )
    #q.put( NotifyClass('web'  , 'connect to webpy.py') )
    #q.put( NotifyClass('term' , message) )

    while not q.empty():
        res=q.get().do()


#============================================================
#============================================================
#============================================================
#============================================================
#============================================================

if __name__=="__main__":
    Fire( {"a":issueall,
           "s":issue_sound,
           "h":issue_hat,
           "b":issue_dbus})





    ######################## END END END END END END #################
    ######################## END END END END END END #################
    ######################## END END END END END END #################

    #########################
    # TASK:
    #   local and ip applications need to display stuff. messages.
    #   myservice could work as ip port for receiving messages
    #      and everything else is local...
    #  PLAN:
    #  queue external - via -
    # * notify
    # * sense-hat - small num, rolling number
    # * audio - mp3 or voice
    # * webpage
    #https://pymotw.com/2/multiprocessing/communication.html
    #http://askubuntu.com/questions/108764/how-do-i-send-text-messages-to-the-notification-bubbles
    #====== first attempt  d-bus:
    #
    #https://askubuntu.com/questions/38733/how-to-read-dbus-monitor-output/142888
    ############################
