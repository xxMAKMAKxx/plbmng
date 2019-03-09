#! /usr/bin/env python3
#Author: Martin Kacmarcik
#License: MIT
#For my Diploma thesis at Faculty of Electrical Engineering -- Brno, University of Technology

#Set PATH for local libraries
import sys,os
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))

#system imports
import locale,re,signal,subprocess,paramiko,socket,folium,webbrowser
from dialog import Dialog
from platform   import system
from paramiko.ssh_exception import BadHostKeyException, AuthenticationException, SSHException
import sqlite3
import hashlib
from multiprocessing import Pool, Lock, Value

#local imports
from lib import port_scanner
from lib import full_map

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

#global variables
base = 0
increment = 0

#Initial settings
locale.setlocale(locale.LC_ALL, '')
d = Dialog(dialog="dialog")
d.set_background_title("Planetlab Server Manager (v. 0.2.2)")
path=""

def signal_handler(sig, frame):
    clear()
    print('You pressed Ctrl+C!')
    exit(0)

def getPath():
    global path
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    path=os.path.dirname(os.path.realpath(__file__))

def clear():
    os.system("clear")

def crontabScript():
    os.system(path+'/cron_script.sh')
    exit(0)

def testPing(target, returnbool=False):
    pingPacketWaitTime=300
    if system().lower()=='windows':
        pingParam='-n'
    else:
        pingParam='-c'
    command = ['ping', pingParam, '1', target, '-W', str(pingPacketWaitTime)]
    p = subprocess.Popen(command, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    #prepare the regular expression to get time
    if system().lower()=='windows':
        avg=re.compile('Average = ([0-9]+)ms')
    else:
        avg=re.compile('min/avg/max/[a-z]+ = [0-9.]+/([0-9.]+)/[0-9.]+/[0-9.]+')
    
    avgStr=avg.findall(str(p.communicate()[0]))
    if(p.returncode != 0):
        if returnbool == False:
            return "Not reachable via ICMP"
        else:
            return False
    else:
        p.kill()
        if returnbool == False:
            return avgStr[0]+" ms"
        else:
            return True

def testSsh(target,printwarn=True):
    result = port_scanner.testPortAvailability(target,22)
    if (result is True or result is False):
        return result
    elif result is 98:
        if printwarn is True:
            d.msgbox("Hostname could not be resolved. Either the server has been removed or you have wrongly set DNS.")
        return result
    elif result is 97:
        if printwarn is True:
            d.msgbox("Error while connecting to server. Please check your network settings.")
        return result
        

def verifyApiCredentialsExist():
    with open (path+"/conf/plbmng.conf",'r') as config:
        for line in config:
            if(re.search('USERNAME',line)):
                username=(re.sub('USERNAME="(.*)"',r'\1',line)).rstrip()
                if not username:
                    return False
            elif(re.search('PASSWORD',line)):
                password=(re.sub('PASSWORD="(.*)"',r'\1',line)).rstrip()
                if not password:
                    return False
    return True

def verifySshCredentialsExist():
    with open (path+"/conf/plbmng.conf",'r') as config:
        for line in config:
            if(re.search('SLICE',line)):
                slice=(re.sub('SLICE="(.*)"',r'\1',line)).rstrip()
                if not slice:
                    return False
            elif(re.search('SSH_KEY',line)):
                key=(re.sub('SSH_KEY="(.*)"',r'\1',line)).rstrip()
                if not key:
                    return False
    return True

#parent function to update availability DB that controls multiple processes
def updateAvailabilityDatabaseParent():
    nodes = getNodes()
    increment = Value('f',0)
    increment.value = float(100/len(nodes))
    base = Value('f',0)
    lock = Lock()
    d.gauge_start()
    pool = Pool(50, initializer=multiProcessingInit, initargs=(lock,base,increment,))
    pool.map(updateAvailabilityDatabase, nodes)
    pool.close()
    pool.join()
    d.gauge_update(100, "Completed")
    exit_code = d.gauge_stop()
    d.msgbox("Availability database has been successfully updated")


def multiProcessingInit(l, b, i):
    global lock
    lock = l
    global base
    base = b
    global increment
    increment = i


def updateProgressBarMultiProcessing(increment_number):
    global d
    d.gauge_update(int(increment_number))

def updateAvailabilityDatabase(node):
    #inint block
    db = sqlite3.connect('database/internal.db')
    cursor = db.cursor()
    #action block
    hash_object = hashlib.md5(node[2].encode())
    ssh_result='T' if testSsh(node[2], False) == True else 'F'
    ping_result='T' if testPing(node[1], True) == True else 'F'
    #find if object exists in the database
    cursor.execute('SELECT nkey from AVAILABILITY where shash = \"'+str(hash_object.hexdigest())+'\";')
    if(cursor.fetchone() is None):
        #the object yet doesn't exist
        cursor.execute("INSERT into AVAILABILITY(shash,shostname,bssh,bping) VALUES (\""+hash_object.hexdigest()+"\", \""+node[2]+"\", \""+ssh_result+"\", \""+ping_result+"\")")
    else:
        #object exists, just update results
        cursor.execute("UPDATE availability SET bssh=\""+ssh_result+"\", bping=\""+ping_result+"\" WHERE shash=\""+hash_object.hexdigest()+"\"")
    lock.acquire()
    base.value = base.value + increment.value
    updateProgressBarMultiProcessing(base.value)
    lock.release()
    #clean up
    db.commit()
    db.close()
    

def getSshKey():
    sshPath=""
    with open (path+"/conf/plbmng.conf",'r') as config:
        for line in config:
            if(re.search('SSH_KEY',line)):
                sshPath=(re.sub('SSH_KEY=','',line)).rstrip()
    return sshPath

def getSshUser():
    user=""
    with open (path+"/conf/plbmng.conf",'r') as config:
        for line in config:
            if(re.search('SLICE=',line)):
                user=(re.sub('SLICE=','',line)).rstrip()
    return user

def getUser():
    user=""
    with open (path+"/conf/plbmng.conf",'r') as config:
        for line in config:
            if(re.search('USERNAME=',line)):
                user=(re.sub('USERNAME=','',line)).rstrip()
    return user

def getPasswd():
    passwd=""
    with open (path+"/conf/plbmng.conf",'r') as config:
        for line in config:
            if(re.search('PASSWORD=',line)):
                passwd=(re.sub('PASSWORD=','',line)).rstrip()
    return passwd

def getNodes(nodeFile=None):
    if nodeFile == None:
        nodeFile=path+'/database/default.node'
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
        os.system("myPwd=$(pwd); cd "+path+"; python3 lib/planetlab_list_creator.py -u \""+user+"\" -p \""+passwd+"\" -o ./; cd $(echo $myPwd)")
    else:
        needToFillPasswdFirstInfo()

def isFirstRun():
    isFirst=path+'/database/first.boolean'
    with open(isFirst, 'r') as isFirstFile:
        bIsFirst=isFirstFile.read().strip('\n')
        print(bIsFirst)
    if(bIsFirst == "True"):
        with open(isFirst, 'w') as isFirstFile:
            isFirstFile.write("False")
        return True
    else:
        return False

def lastServerMenu():
    printServerInfo(getLastServerAccess())

def updateLastServerAccess(infoAboutNodeDic):
    lastServerFile=path+'/database/last_server.node'
    with open(lastServerFile, 'w') as lastServerFile:
        lastServerFile.write(repr(infoAboutNodeDic))

def getLastServerAccess():
    lastServerFile=path+'/database/last_server.node'
    with open(lastServerFile, 'r') as lastServerFile:
        lastServer=eval(lastServerFile.read().strip('\n'))
    return lastServer

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
        returnedChoice,infoAboutNodeDic,chosenNode = getServerInfo(choices[int(returnedChoice)-1][1], option, nodes)
    if(returnedChoice == None):
        return
    elif(returnedChoice == False):
        return
    elif(int(returnedChoice) == 1):
        connect(int(returnedChoice),chosenNode)
    elif(int(returnedChoice) == 2):
        connect(int(returnedChoice),chosenNode)
    elif(int(returnedChoice) == 3):
        showOnMap(chosenNode,infoAboutNodeDic)

def connect(mode,node):
    clear()
    key = getSshKey()
    user = getSshUser()
    if(mode == 1):
        return_value = os.system("ssh -o \"StrictHostKeyChecking=no\" -o \"UserKnownHostsFile=/dev/null\" -i "+key+" "+user+"@"+node[OPTION_IP])
        if return_value is not 0:
            d.msgbox("Error while connecting. Please verify your credentials.")
    elif(mode ==2 ):
        return_value = os.system("mc sh://"+user+"@"+node[OPTION_IP]+":/home")
        if return_value is not 0:
            d.msgbox("Error while connecting. Please verify your credentials.")
    else:
        return

def showOnMap(node,nodeInfo=""):
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
    nodeMap = folium.Map(location=[latitude, longitude],
                       zoom_start=2,min_zoom=2)
    if (nodeInfo == ""):
        folium.Market([latitude,longitude],popup=name).add_to(nodeMap)
    else:
        folium.Marker([latitude, longitude],popup=(nodeInfo["text"].replace('\n','<br>'))).add_to(nodeMap)
    nodeMap.save('/tmp/map_plbmng.html')
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
    #update base_data.txt file based on latest database with nodes
    os.system("cat "+path+"/database/default.node | awk 'NR>1' |sort| uniq| cut -f10,11,3 | sort -k2 -u > "+path+"/lib/base_data.txt")
    full_map.plot_server_on_map()
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
            #in nodes find the chosenONe node
            chosenOne=""
            for item in nodes:
                if re.search(serverId,item[option]):
                    chosenOne=item
                    break
            if(chosenOne == ""):
                print("Internal error, please file a bug report via PyPi")
                exit(99)
            #get information about servers
            infoAboutNodeDic = dict()
            region,city,url,fullname,lat,lon = getInfoFromNode(chosenOne)
            infoAboutNodeDic["region"] = region
            infoAboutNodeDic["city"] = city
            infoAboutNodeDic["url"] = url
            infoAboutNodeDic["fullname"] = fullname
            infoAboutNodeDic["lat"] = lat
            infoAboutNodeDic["lon"] = lon
            infoAboutNodeDic["icmp"]=testPing(chosenOne[OPTION_IP])
            infoAboutNodeDic["sshAvailable"]=testSsh(chosenOne[OPTION_DNS])
            infoAboutNodeDic["text"]="""
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
            ICMP RESPOND: %s
            SSH AVAILABLE: %r
            """ %  (chosenOne[OPTION_DNS],
                chosenOne[OPTION_IP],
                chosenOne[OPTION_CONTINENT],
                chosenOne[OPTION_COUNTRY],
                infoAboutNodeDic["region"],
                infoAboutNodeDic["city"],
                infoAboutNodeDic["url"],
                infoAboutNodeDic["fullname"],
                infoAboutNodeDic["lat"],
                infoAboutNodeDic["lon"],
                infoAboutNodeDic["icmp"],
                infoAboutNodeDic["sshAvailable"])   
            if(infoAboutNodeDic["sshAvailable"] is True or infoAboutNodeDic["sshAvailable"] is False):
                #update last server access database
                updateLastServerAccess(infoAboutNodeDic)
                return printServerInfo(infoAboutNodeDic),infoAboutNodeDic,chosenOne
            else:
                return False,False,False


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

def printServerInfo(infoAboutNodeDic):
    if not verifySshCredentialsExist():
        preparedChoices=[("1","Connect via SSH (Credentials not set!)"),
                         ("2", "Connect via MC (Credentials not set!)"),
                         ("3", "Show on map")]
    else:
        preparedChoices=[("1","Connect via SSH"),
                         ("2", "Connect via MC"),
                         ("3", "Show on map")]
    code, tag = d.menu(infoAboutNodeDic["text"], height=0, width=0, menu_height=0, choices=preparedChoices)
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

def firstRunMessage():
    d.msgbox("This is your first run of the application. Please go to 'Set Credentials' menu and set your credentials now.",height=0, width=0)
    return

def needToFillPasswdFirstInfo():
    d.msgbox("Credentials are not set. Please go to menu and set them now")
    return

def initInterface():
    getPath()
    signal.signal(signal.SIGINT, signal_handler)
    if isFirstRun() == True:
        firstRunMessage()
    while True:
        #Main menu
        code, tag = d.menu("Choose one of the following options:",
                           choices=[("1", "Access servers"),
                                    ("2", "Monitor servers"),
                                    ("3", "Plot map"),
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
    code,text = d.editbox(path+'/conf/plbmng.conf',height=0, width=0)
    if(code == d.OK):
        with open(path+'/conf/plbmng.conf', "w") as configFile:
            configFile.write(text)


def aboutGui():
    d.msgbox("""
            Project supervisor:
                Dan Komosny
            Authors:
                Tomas Andrasov
                Filip Suba
                Martin Kacmarcik

            Version 0.2.2
            This application is under MIT license.
            """, width=0, height=0, title="About")

#Plot servers on map part of GUI
def plotServersOnMapGui():
    while True:
        code, tag = d.menu("Choose one of the following options:",
                           choices=[("1", "Plot servers reponding to ping"),
                                    ("2", "Plot ssh available servers"),
                                    ("3", "Plot all servers")],
                           title="Map menu")
        if code == d.OK:
            plotServersOnMap(tag)
            return
        else:
            return

#Monitor servers part of GUI
def monitorServersGui():
    if not verifyApiCredentialsExist():
        d.msgbox("Warning! Your credentials for PlanetLab API are not set. Please use 'Set credentials' option in main menu to set them.")
    while True:
        code, tag = d.menu("Choose one of the following options:",
                           choices=[("1", "Set cron for monitoring"),
                                    ("2", "Set monitoring elements"),
                                    ("3", "Get nodes"),
                                    ("4", "Update availability database")],
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
            elif(tag == "4"):
                if d.yesno("This can take few minutes. Do you want to continue?") == d.OK:
                    if not verifySshCredentialsExist():
                        d.msgbox("Error! Your ssh credentials are not set. Please use 'Set credentials' option in main menu to set them.")
                        continue
                    else:
                        updateAvailabilityDatabaseParent()
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
                                ("3", "Search by location"),
                                ("4", "Access last server")],
                       title="ACCESS SERVERS")
        if code == d.OK:
            #Search by DNS
            if(tag == "1"):
                code, answer = d.inputbox("Search for:",title="Search")
                if code == d.OK:
                    searchNodes(OPTION_DNS,answer)
                else:
                    continue
            #Search by IP
            elif(tag == "2"):
                code, answer = d.inputbox("Search for:",title="Search")
                if code == d.OK:
                    searchNodes(OPTION_IP,answer)
                else:
                    continue
            #Search by location
            elif(tag == "3"):
                #Grepuje se default node
                searchNodes(OPTION_LOCATION)
            elif(tag == "4"):
                lastServerMenu()

        else:
            return

if __name__ == "__main__":
    initInterface()
    exit(0)
