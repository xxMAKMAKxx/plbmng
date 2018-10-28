#! /usr/bin/env python3
#Authors: Martin Kacmarcik, Filip Suba, Tomas Andrasov
#License: MIT
#For my Diploma thesis at Faculty of Electrical Engineering -- Brno, University of Technology


import locale,os,re
from dialog import Dialog

#Initial settings
locale.setlocale(locale.LC_ALL, '')
d = Dialog(dialog="dialog")
d.set_background_title("Planetlab server manager")

#Main GUI function

def clear():
    os.system("clear")

def initInterface():
    while True:
        code, tag = d.menu("Choose one of the following options:",
                           choices=[("1", "Access servers"),
                                    ("2", "Measure servers"),
                                    ("3", "Plot servers on map")],
                           title="MAIN MENU")

        if code == d.OK:
            if(tag == "1"):
                code, tag = d.menu("Choose one of the following options:",
                           choices=[("1", "Serach by DNS"),
                                    ("2", "Search by IP"),
                                    ("3", "Search by location")],
                           title="ACCESS SERVERS")
                if code == d.OK:
                    code, answer = d.inputbox("Search for:",title="Search")
                    if code == d.OK:
                        print("lol")
                    else:
                        continue
                else:
                    continue
            elif(tag == "2"):
                print("2")
            elif(tag == "#"):
                print("3")
        else:
            clear()
            exit(0)

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
