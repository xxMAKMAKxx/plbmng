#! /usr/bin/env python3
#Authors: Martin Kacmarcik, Filip Suba, Tomas Andrasov
#License: MIT
#For my Diploma thesis at Faculty of Electrical Engineering -- Brno, University of Technology


import locale,os,re
from dialog import Dialog

#Initial settings
locale.setlocale(locale.LC_ALL, '')
d = Dialog(dialog="dialog")
d.set_background_title("Planetlab Server Manager")

#Main GUI function

def clear():
    os.system("clear")

def initInterface():
    while True:
        #Main menu
        code, tag = d.menu("Choose one of the following options:",
                           choices=[("1", "Access servers"),
                                    ("2", "Monitor servers"),
                                    ("3", "Plot servers on map"),
                                    ("4", "Set credentials")],
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
                print("3")
            #Set crdentials
            elif(tag == "4"):
                #TODO: re-design this
                os.system("gedit bin/plbmng.conf")
        else:
            clear()
            exit(0)

#Monitor servers part of GUI
def monitorServersGui():
    while True:
        code, tag = d.menu("Choose one of the following options:",
                           choices=[("1", "Set cron for monitoring"),
                                    ("2", "Set monitoring elements"),
                                    ("3", "Monitor now")],
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
    initInterface()
    exit(0)


# In pythondialog 3.x, you can compare the return code to d.OK, Dialog.OK or
# "ok" (same object). In pythondialog 2.x, you have to use d.DIALOG_OK, which
# is deprecated since version 3.0.0.
if d.yesno("Are you REALLY sure you want to see this?") == d.OK:
    d.msgbox("You have been warned...")

    # We could put non-empty items here (not only the tag for each entry)
    code, tags = d.checklist("What sandwich toppings do you like?",
                             choices=[("Catsup", "",             False),
                                      ("Mustard", "",            False),
                                      ("Pesto", "",              False),
                                      ("Mayonnaise", "",         True),
                                      ("Horse radish","",        True),
                                      ("Sun-dried tomatoes", "", True)],
                             title="Do you prefer ham or spam?",
                             backtitle="And now, for something "
                             "completely different...")
    if code == d.OK:
        # 'tags' now contains a list of the toppings chosen by the user
        pass
else:
    code, tag = d.menu("OK, then you have two options:",
                       choices=[("(1)", "Leave this fascinating example"),
                                ("(2)", "Leave this fascinating example")])
    if code == d.OK:
        # 'tag' is now either "(1)" or "(2)"
        pass
