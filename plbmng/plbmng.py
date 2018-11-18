#! /usr/bin/env python3
#Authors: Martin Kacmarcik, Filip Suba, Tomas Andrasov
#License: MIT
#For my Diploma thesis at Faculty of Electrical Engineering -- Brno, University of Technology


import locale,os,re,signal,sys,subprocess,paramiko,socket,folium,webbrowser
from dialog import Dialog
from platform   import system
from paramiko.ssh_exception import BadHostKeyException, AuthenticationException, SSHException

#Constant definition
OPTION_LOCATION=0
OPTION_IP=1
OPTION_DNS=2
OPTION_CONTINENT=3
OPTION_COUNTRY=4
OPTION_REGION=5
OPTION_CITY=6
OPTION_URL=7
OPTION_NAME=8
OPTION_LAT=9
OPTION_LON=10

#Initial settings
locale.setlocale(locale.LC_ALL, '')
d = Dialog(dialog="dialog")
d.set_background_title("Planetlab Server Manager (v. 1.1)")
path=""

def signal_handler(sig, frame):
    clear()
    print('You pressed Ctrl+C!')
    exit(0)

def getPath():
    global path
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    pythonVersionCmd="ls ../lib | grep python3"
    if(os.path.exists("../lib")):
        pythonVersion = subprocess.check_output(pythonVersionCmd, shell=True)
        path="../lib/"+pythonVersion+"/site-packages/plbmng"
    else:
        path=os.getcwd()

def clear():
    os.system("clear")

def crontabScript():
    os.system(path+'/cron_script.sh')
    exit(0)

def testPing(target):
    if system().lower()=='windows':
        pingParam='-n'
    else:
        pingParam='-c'
    command = ['ping', pingParam, '1', target]
    p = subprocess.Popen(command, stdout = subprocess.PIPE)
    if system().lower()=='windows':
        avg=re.compile('Average = ([0-9]+)ms')
    else:
        avg=re.compile('min/avg/max/mdev = [0-9.]+/([0-9.]+)/[0-9.]+/[0-9.]+')
    avgStr=avg.findall(str(p.communicate()[0]))
    if(p.returncode != 0):
        return "N/A"
    p.kill()
    return avgStr[0]

def testSsh(target):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    user=getSshUser()
    key=getSshKey()
    try:
        ssh.connect(target, username=user, key_filename=key,timeout=2)
        return True
    except (BadHostKeyException, AuthenticationException, 
        SSHException, socket.error) as e:
        print(e)
        return False
    exit(0)

def getSshKey():
    sshPath=""
    with open (path+"/bin/plbmng.conf",'r') as config:
        for line in config:
            if(re.search('SSH_KEY',line)):
                sshPath=(re.sub('SSH_KEY=','',line)).rstrip()
    return sshPath

def getSshUser():
    user=""
    with open (path+"/bin/plbmng.conf",'r') as config:
        for line in config:
            if(re.search('SLICE=',line)):
                user=(re.sub('SLICE=','',line)).rstrip()
    return user

def getUser():
    user=""
    with open (path+"/bin/plbmng.conf",'r') as config:
        for line in config:
            if(re.search('USERNAME=',line)):
                user=(re.sub('USERNAME=','',line)).rstrip()
    return user

def getPasswd():
    passwd=""
    with open (path+"/bin/plbmng.conf",'r') as config:
        for line in config:
            if(re.search('PASSWORD=',line)):
                passwd=(re.sub('PASSWORD=','',line)).rstrip()
    return passwd

def getNodes(nodeFile=None):
    if nodeFile == None:
        nodeFile=path+'/default.node'
    nodes=[]
    with open(nodeFile, 'r') as defaultNodeFile:
        lines=defaultNodeFile.readlines()[1:]
        for line in lines:
            nodes.append(line.strip().split())
    return nodes

def getAllNodes():
    user=getUser()
    passwd=getPasswd()
    if(user != "") and (passwd != ""):
        os.system("myPwd=$(pwd); cd "+path+"; python3 python_scripts/planetlab_list_creator.py -u \""+user+"\" -p \""+passwd+"\" -o ./; cd $(echo $myPwd)")
    else:
        needToFillPasswdFirstInfo()

def searchNodes(option,regex=None):
    nodes = getNodes()
    answers = []
    choices=[]
    counter=1
    #parse data based on incoming regex
    if option != 0:
        for item in nodes:
            if re.search(regex,item[option]):
                answers.append(item)
        if len(answers) == 0:
            returnedChoice=searchNodesGui(False)
        else:
            #prepare choices for GUI
            for item in answers:
                choices.append((str(counter),item[option]))
                counter+=1
            returnedChoice=searchNodesGui(choices)
    else:
        for item in nodes:
            answers.append(item[OPTION_CONTINENT])
        continents=sorted(set(answers))
        #prepare choices for GUI
        for item in continents:
            choices.append((str(counter),item))
            counter+=1
        returnedChoice=searchNodesGui(choices)
        if returnedChoice == None:
            return
        answers=[]
        choices=[]
        counter=1
        for item in nodes:
            if re.search(continents[int(returnedChoice)-1],item[OPTION_CONTINENT]):
                answers.append(item[OPTION_COUNTRY])
        countries=sorted(set(answers))
        #prepare choices for GUI
        for item in countries:
            choices.append((str(counter),item))
            counter+=1
        returnedChoice=searchNodesGui(choices)
        if returnedChoice == None:
            return
        answers=[]
        choices=[]
        counter=1
        for item in nodes:
            if re.search(countries[int(returnedChoice)-1],item[OPTION_COUNTRY]):
                answers.append(item[OPTION_DNS])
        hostnames=sorted(set(answers))
        #prepare choices for GUI
        for item in hostnames:
            choices.append((str(counter),item))
            counter+=1
        returnedChoice=searchNodesGui(choices)
    if(returnedChoice == None):
        return
    else:
        returnedChoice,chosenNode = getServerInfo(choices[int(returnedChoice)-1][1], option, nodes)
    if(returnedChoice == None):
        return
    elif(int(returnedChoice) == 1):
        connect(int(returnedChoice),chosenNode)
    elif(int(returnedChoice) == 2):
        connect(int(returnedChoice),chosenNode)
    elif(int(returnedChoice) == 3):
        showOnMap(chosenNode)

def connect(mode,node):
    clear()
    key = getSshKey()
    user = getSshUser()
    if(mode == 1):
        os.system("ssh -o \"StrictHostKeyChecking=no\" -o \"UserKnownHostsFile=/dev/null\" -i "+key+" "+user+"@"+node[OPTION_IP])
    elif(mode ==2 ):
        os.system("mc sh://"+user+"@"+node[OPTION_IP]+":/home")
    else:
        return



def showOnMap(node):
    _stderr = os.dup(2)
    os.close(2)
    _stdout = os.dup(1)
    os.close(1)
    fd = os.open(os.devnull, os.O_RDWR)
    os.dup2(fd, 2)
    os.dup2(fd, 1)
    latitude = float(node[-2])
    longitude = float(node[-1])
    name = node[OPTION_DNS]

    map = folium.Map(location=[latitude, longitude],
                       zoom_start=2)
    folium.Marker([latitude, longitude], popup=name).add_to(map)
    map.save('/tmp/map_plbmng.html')
    try:
        webbrowser.get().open('file://' + os.path.realpath('/tmp/map_plbmng.html'))
    finally:
        os.close(fd)
        os.dup2(_stderr, 2)
        os.dup2(_stdout, 1)

def plotServersOnMap(mode):
    _stderr = os.dup(2)
    os.close(2)
    _stdout = os.dup(1)
    os.close(1)
    fd = os.open(os.devnull, os.O_RDWR)
    os.dup2(fd, 2)
    os.dup2(fd, 1)
    os.system("cat "+path+"/default.node | awk 'NR>1' |sort| uniq| cut -f10,11,3 | sort -k2 -u > "+path+"/python_scripts/base_data.txt")
    if(int(mode)==1):
        os.system("myPwd=$(pwd); cd "+path+"; python3 python_scripts/icmp_map.py; cd $(echo $myPwd)")
        mapFile="map_icmp.html"
    elif(int(mode)==2):
        os.system("myPwd=$(pwd); cd "+path+"; python3 python_scripts/ssh_map.py; cd $(echo $myPwd)")
        mapFile="map_ssh.html"
    else:
        os.system("myPwd=$(pwd); cd "+path+"; python3 python_scripts/full_map.py; cd $(echo $myPwd)")
        mapFile="map_full.html"
    try:
        webbrowser.get().open('file://' + os.path.realpath(path+"/"+mapFile))
    finally:
        os.close(fd)
        os.dup2(_stderr, 2)
        os.dup2(_stdout, 1)


def getServerInfo(serverId,option,nodes=None):
    if nodes == None:
        nodes = getNodes()
    if option == 0:
        option=OPTION_DNS
    if isinstance(serverId,str):
        for item in nodes:
            if re.search(serverId,item[option]):
                chosenOne=item
                break
        return printServerInfo(chosenOne),chosenOne


def getInfoFromNode(node):
    region=""
    fullname=""
    counter=OPTION_REGION
    isFirst=True
    while(True):
        if(re.search('http://',node[counter+1])):
            city=node[counter]
            counter+=1
            url=node[counter]
            counter+=1
            break
        elif(re.search('www',node[counter+1])):
            city=node[counter]
            counter+=1
            url=node[counter]
            counter+=1
            break
        else:

            if isFirst:
                isFirst=False
            else:
                region+=" "
            region+=node[counter]
        counter+=1
    while(True):
        if(counter == (len(node)-2)):
            lat=node[counter]
            lon=node[counter+1]
            break
        else:
            fullname+=node[counter]
            fullname+=" "
            counter+=1
    return region,city,url,fullname,lat,lon

def removeCron():
    os.system("crontab -l | grep -v plbmng\ crontab | crontab -")

def addToCron(mode):
    if(int(mode) == 2):
        line="@daily plbmng crontab"
    elif(int(mode)==3):
        line="@weekly plbmng crontab"
    elif(int(mode)==4):
        line="@monthly plbmng crontab"
    os.system("echo \"$(crontab -l ; echo "+line+")\" | crontab -")

###################
#  GUI functions  #
###################

def printServerInfo(chosenOne):
    region,city,url,fullname,lat,lon = getInfoFromNode(chosenOne)
    icmp=testPing(chosenOne[OPTION_IP])
    sshAvailable=testSsh(chosenOne[OPTION_IP])
    text="""
        NODE: %s
        IP: %s
        CONTINENT: %s
        COUNTRY: %s
        REGION: %s
        CITY: %s
        URL: %s
        FULL NAME: %s
        LATITUDE: %s
        LONGITUDE: %s
        ICMP RESPOND: %s ms
        SSH AVAILABLE: %r
        """ %  (chosenOne[OPTION_DNS], 
                chosenOne[OPTION_IP], 
                chosenOne[OPTION_CONTINENT],
                chosenOne[OPTION_COUNTRY],
                region,
                city,
                url,
                fullname,
                lat,
                lon,
                icmp,
                sshAvailable)

    preparedChoices=[("1","Connect via SSH"),
                     ("2", "Connect via MC"),
                     ("3", "Show on map")]
    code, tag = d.menu(text, height=0, width=0, menu_height=0, choices=preparedChoices)
    if code == d.OK:
        return tag
    else:
        return None

def searchNodesGui(prepared_choices):
    if not prepared_choices:
        d.msgbox("No results found.", width=0,height=0)
        return None
    while True:
        code, tag = d.menu("These are the results:",
                               choices=prepared_choices,
                               title="Search results")
        if code == d.OK:
            return tag
        else:
            return None

def needToFillPasswdFirstInfo():
    d.msgbox("Credentials are not set. Please go to menu and set them now")
    return

def initInterface():
    getPath()
    signal.signal(signal.SIGINT, signal_handler)
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
                setCredentialasGui()
            elif(tag == "5"):
                aboutGui()
        else:
            clear()
            exit(0)

def setCredentialasGui():
    code,text = d.editbox(path+'/bin/plbmng.conf',height=0, width=0)
    if(code == d.OK):
        with open(path+'/bin/plbmng.conf', "w") as configFile:
            configFile.write(text)


def aboutGui():
    d.msgbox("""
            Project supervisor:
                Dan Komosny
            Authors:
                Tomas Andrasov
                Filip Suba
                Martin Kacmarcik

            Version 1.1
            This application is under MIT license.
            """, width=0, height=0, title="About")

#Plot servers on map part of GUI
def plotServersOnMapGui():
    while True:
        code, tag = d.menu("Choose one of the following options:",
                           choices=[("1", "Generate ICMP map"),
                                    ("2", "Generate SSH map"),
                                    ("3", "Generate full map")],
                           title="Map menu")
        if code == d.OK:
            if(tag == "1"):
                plotServersOnMap(tag)
                return
            if(tag == "2"):
                plotServersOnMap(tag)
                return
            if(tag == "3"):
                plotServersOnMap(tag)
                return
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
                        if d.yesno("This is going to take around 20 minutes") == d.OK:
                            getAllNodes()
                        else:
                            continue
                    elif(tag == "2"):
                        addToCron(tag)
                    elif(tag == "3"):
                        addToCron(tag)
                    elif(tag == "4"):
                        addToCron(tag)
                    elif(tag == "5"):
                        removeCron()
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
                    getAllNodes()
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
                    searchNodes(OPTION_DNS,answer)
                else:
                    continue
            #Search by IP
            elif(tag == "2"):
                code, answer = d.inputbox("Search for:",title="Search")
                if code == d.OK:
                    #TODO func
                    searchNodes(OPTION_IP,answer)
                else:
                    continue
            #Search by location
            elif(tag == "3"):
                #TODO func for search by func
                #Grepuje se default node
                searchNodes(OPTION_LOCATION)

        else:
            return

if __name__ == "__main__":
    initInterface()
    exit(0)
