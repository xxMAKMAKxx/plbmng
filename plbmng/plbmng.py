#! /usr/bin/env python3
#Authors: Martin Kacmarcik, Filip Suba, Tomas Andrasov
#License: MIT
#For my Diploma thesis at Faculty of Electrical Engineering -- Brno, University of Technology


import locale,os,re,signal,sys
from dialog import Dialog

#Initial settings
locale.setlocale(locale.LC_ALL, '')
d = Dialog(dialog="dialog")
d.set_background_title("Planetlab Server Manager (v. 1.1)")

def signal_handler(sig, frame):
    clear()
    print('You pressed Ctrl+C!')
    exit(0)

def clear():
    os.system("clear")

def initInterface():
    while True:
        #Main menu
        code, tag = d.menu("Choose one of the following options:",
                           choices=[("1", "Access servers"),
                                    ("2", "Monitor servers"),
                                    ("3", "Plot servers on map"),
                                    ("4", "Set credentials"),
                                    ("5", "About")],
                           title="MAIN MENU")

        if code == d.OK:
            #Acess servers
            if(tag == "1"):
                accessServersGui()
            #Meausre servers
            elif(tag == "2"):
                monitorServersGui()
            #Plot servers on map
            elif(tag == "3"):
                plotServersOnMapGui()
            #Set crdentials
            elif(tag == "4"):
                #TODO: re-design this
                os.system("gedit bin/plbmng.conf")
            elif(tag == "5"):
                aboutGui()
        else:
            clear()
            exit(0)

def aboutGui():
    d.msgbox("""
            Authors:
                Tomas Andrasov
                Filip Suba
                doc. Ing. Dan Komosny Ph.D.
                Martin Kacmarcik

            Version 1.1
            This application is under MIT license.
            """, width=0, height=0, title="About")

#Plot servers on map part of GUI
def plotServersOnMapGui():
    while True:
        code, tag = d.menu("Choose one of the following options:",
                           choices=[("1", "Generate map"),
                                    ("2", "Select map elements")],
                           title="Map menu")
        if code == d.OK:
            if(tag == "1"):
                #TODO generate map func
                print("TBD")
            if(tag == "2"):
                code, t = d.checklist(
                          "Press SPACE key to choose map elements", height=0, width=0, list_height=0,
                choices=[("1", "ICMP response", False),
                         ("2", "SSH time", False) ],)
        else:
            return

#Monitor servers part of GUI
def monitorServersGui():
    while True:
        code, tag = d.menu("Choose one of the following options:",
                           choices=[("1", "Set cron for monitoring"),
                                    ("2", "Set monitoring elements"),
                                    ("3", "Get nodes")],
                           title="Monitoring menu")
        if code == d.OK:
            if(tag == "1"):
                code, tag = d.menu("Choose one of the following options:",
                               choices=[("1", "Run monitoring now"),
                                        ("2", "Set monitoring daily"),
                                        ("3", "Set monitoring weekly"),
                                        ("4", "Set monitoring monthly"),
                                        ("5", "Remove all monitoring from cron")],
                               title="Crontab menu")
                if code == d.OK:
                    if(tag == "1"):
                        #TODO func
                        print("TBD")
                    elif(tag == "2"):
                        #TODO func
                        print("TBD")
                    elif(tag == "3"):
                        #TODO func
                        print("TBD")
                    elif(tag == "4"):
                        #TODO func
                        print("TBD")
                    elif(tag == "5"):
                        #TODO func
                        print("TBD")
                else:
                    continue
            elif(tag == "2"):
                code, t = d.checklist(
                         "Press SPACE key to choose what to monitor", height=0, width=0, list_height=0,
                choices=[ ("1", "Test ping", True),
                        ("2", "Test SSH", False),
                        ("3", "Skip non responsive servers", False) ],)
            elif(tag == "3"):
                if d.yesno("This is going to take around 20 minutes") == d.OK:
                    #TBD func
                    print("TBD")
                else:
                    continue
        else:
            return


#Acess servers part of GUI
def accessServersGui():
    while True:
        code, tag = d.menu("Choose one of the following options:",
                       choices=[("1", "Serach by DNS"),
                                ("2", "Search by IP"),
                                ("3", "Search by location")],
                       title="ACCESS SERVERS")
        if code == d.OK:
            #Search by DNS
            if(tag == "1"):
                code, answer = d.inputbox("Search for:",title="Search")
                if code == d.OK:
                    #TODO func
                    print("lol")
                else:
                    continue
            #Search by IP
            elif(tag == "2"):
                code, answer = d.inputbox("Search for:",title="Search")
                if code == d.OK:
                    #TODO func
                    print("tbd")
                else:
                    continue
            #Search by location
            elif(tag == "3"):
                #TODO func for search by func
                #Grepuje se default node
                print("tbd")


        else:
            return

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    initInterface()
    exit(0)
