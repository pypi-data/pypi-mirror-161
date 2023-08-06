#!/usr/bin/env python3
#
###https://projects.raspberrypi.org/en/projects/getting-started-with-the-sense-hat
#
# MERGE OF pix2 and later tricks
#
#
#from sense_emu import SenseHat
#from sense_emu import SenseHat
#
# show_num
# show_number
# make_color
#

try:
    from sense_hat import *
except:
    from sense_emu import *

import time
import sys
import colorsys
import datetime

import os
import subprocess as s

#import os
import signal  # to kill
import datetime #  running until timeout

import argparse

from fire import Fire


#####################################
#  FROM DISPTEMP.PY
####################################
#one row per 5x3 digit - 0 to 9 and T
nums =[1,1,1,1,0,1,1,0,1,1,0,1,1,1,1, # 0
       0,1,0,0,1,0,0,1,0,0,1,0,0,1,0,
       1,1,1,0,0,1,0,1,0,1,0,0,1,1,1,
       1,1,1,0,0,1,1,1,1,0,0,1,1,1,1,
       1,0,0,1,0,1,1,1,1,0,0,1,0,0,1,
       1,1,1,1,0,0,1,1,1,0,0,1,1,1,1,
       1,1,1,1,0,0,1,1,1,1,0,1,1,1,1,
       1,1,1,0,0,1,0,1,0,1,0,0,1,0,0,
       1,1,1,1,0,1,1,1,1,1,0,1,1,1,1,
       1,1,1,1,0,1,1,1,1,0,0,1,0,0,1, # 9
       1,1,1,0,1,0,0,1,0,0,1,0,0,1,0] # T

def show_num(val,xd,yd,r,g,b,  sense):
    offset = val * 15
    for p in range(offset,offset + 15):
        if nums[p] == 1:
            xt = p % 3
            yt = (p-offset) // 3
            sense.set_pixel(xt+xd,yt+yd,r,g,b)

def show_number(val,  rgb , sense):
    abs_val = abs(val)
    tens = abs_val // 10
    units = abs_val % 10
    sense.clear()
    if (abs_val > 9): show_num(tens,0,2,rgb[0],rgb[1],rgb[2],  sense)
    show_num(units,4,2,rgb[0],rgb[1],rgb[2], sense)
    if abs_val == 100:
        sense.clear()
        show_num(10,3,2,rgb[0],rgb[1],rgb[2], sense) # 'T' for ton = 100
    if val < 0 :
        for i in range(0,8):
            #sense.set_pixel(i,0,0,0,128)
            sense.set_pixel(i,0, rgb[0],rgb[1],rgb[2])


######################
#
#  color creation ... 0-1.0
#
#########################
def make_color( aa ):
    if aa==-1: # White
        colorRGB=[ 255,255,255 ]
        return colorRGB
    color=colorsys.hsv_to_rgb( aa , 1.0, 0.8 ) # hue,  grayness,  blackness
    colorRGB=[ int(255*i) for i in color ]
    #print( "colorRGB={}".format(colorRGB ))
    return colorRGB




def main(message="Ahoj", timeshow=1, color=1.1, debug=False):
    """PiHAT: send MESSAGE for TIME. If color>1: rotate"""
    message = str(message)
    colorRGB=make_color( float(color) )
    red = (255, 0, 0)
    white = (255, 255, 255)
    black = ( 0,0,0 )

    sense = SenseHat()
    print("D... Sense HAT inited")

    # bb = message
    # 0.05 is fast 0.2 is slow
    speed=0.1* 3/len(message)  # 3 seconds for all
    speed=0.1* timeshow/len(message)  # 3 seconds for all
    speed2=speed
    if speed2<0.04:
        speed2=0.04
        print("D... speed limit 0.04")
    if speed2>0.2:
        speed2=0.2
        print("D... speed limit 0.2")
    speed2=0.1 # I WANT THIS
    print( "D... display speed: wanted {:.2f} will be {:.2f}".format(speed , speed2 ) )

    ###############
    # DISPLAY decisions
    ###############
    SmallDig=False
    Running=True  # alwas possible
    Static=False

    if message.lstrip('-').isdigit():
        print( "D...",message,"is a digit ")
        if len(message.lstrip('-'))<3:
            SmallDig=True
    else:
        print("D... ",message,"not a digit")
    print("D...  bb length is ", len(message) )
    if len(message)==1:
        Static=True

    print("D... Small={} Run={} Stat={}".format(SmallDig, Running, Static) )


    ############################
    # this is pidkilling part... enables new message without clear
    ############################
    PIDFILE="/tmp/rpihat.pid"
    if Static or SmallDig or Running:
        print("i... looking for "+PIDFILE)
        if os.path.isfile( PIDFILE ) :
            #print("i... exists ... killing and deleting")
            with open(PIDFILE,'r') as f:
                pid=f.readlines()[0]#.decode("utf8").rstrip()
                pid=int(pid)
            print("i... file exists, killing ",pid," ", type(pid) )
            try:
                os.kill(pid, signal.SIGTERM) #or signal.SIGKILL
            except:
                print("X... no process like ",pid," nothing killed")
        mypid=os.getpid()
        print("i... writing new PID",mypid)
        with open(PIDFILE,'w') as f:
            f.write( str(mypid)+"\n" )
    #========== pid killing end -----------------------



    ###############
    # DISPLAY:   aa was inicolor
    ###############
    start=datetime.datetime.now()
    sec=0
    if Static or SmallDig:
        if color>1:
            aastart=0.72 # From BLUE TO RED - override
            aa = aastart
        else:
            aastart = color
            aa = aastart
        print("D... static display with sleep: [static/smalldig]", Static, SmallDig,"\n")
        while sec<timeshow:
            colorRGB=make_color(aa)
            if Static and (SmallDig):
                sense.show_letter( message[0], text_colour=colorRGB )
            else: #if SmallDig:
                show_number( int(message) , colorRGB , sense  )
            sec=(datetime.datetime.now()-start).total_seconds()
            if color>1:
                aa=aastart*(timeshow-sec)/timeshow
                if aa<0.:aa=0

            print( "i... {:03.1f}/{} s.   rgb={}".format( sec, timeshow, colorRGB), end="\r" )
            time.sleep( 0.1 )
        Running=False


    #if SmallDig:
    #    print("?small digit display with sleep\n")
    #    #time.sleep( sleep )
    if Running:
        if color > 1.0:
            aastart=0.72 # From BLUE TO RED - override
            aa = aastart
        else:
            aa = color
        deltat = 0
        ndiv = 0
        while sec<timeshow:
            colorrun=make_color(aa)

            print("i.. running message ..{:03.1f}/{} s.,  {}".format(
                sec,
                timeshow,
                colorrun
            ), end="\r")
            sense.show_message( message ,
                            text_colour = colorrun,
                            back_colour=black,
                            scroll_speed=speed2)
            sec=(datetime.datetime.now()-start).total_seconds()
            if deltat == 0:
                deltat = sec
                divs = int(timeshow/deltat)
                if divs == 0: divs = 1
                ndiv=divs # maximal value and go to 0
            ndiv-=1
            if color > 1.0:
                aa = aastart*ndiv/divs # Change color
                if aa<0.:aa=0
    sense.clear()
    print("i... writing NO PID to ",PIDFILE)
    with open(PIDFILE,'w') as f:
        f.write(  "999999\n" )


def hourly():
    while True:
        time.sleep(0.9)
        se = datetime.datetime.now().strftime("%S")
        print(se, end=" ", flush=True)
        if int(se)==0:
            hm = datetime.datetime.now().strftime("%H:%M")
            print("\nD... ",hm )
            mi = datetime.datetime.now().strftime("%M")
            if (int(mi) == 15):
                main(hm, timeshow=13, color=0.2 )
            elif (int(mi) == 30):
                main(hm, timeshow=13, color=0.5 )
            elif (int(mi) == 45):
                main(hm, timeshow=13, color=0.8 )
            elif (int(mi) == 0):
                main(hm, timeshow=13, color=1.1 )
            else:
                main(hm, timeshow=6, color=-1 )
            print()



if __name__ == "__main__":
    Fire( {"main":main,
           "hourly":hourly
    } )
    sys.exit()
