#!/bin/bash

nor=$(cat nor.txt) 
let nor=$nor+1  
echo "$nor" > nor.txt
number_of_runs=$(cat nor.txt)


#------------GENERAL GUI SETINGS-------------
HEIGHT=23
WIDTH=43
BACKTITLE="Data miner for Planetlab"
#------------GUI SETINGS MENUS-------------

main_menu_gui () {

	CHOICE_HEIGHT=5
	TITLE="MAIN MENU"
	MENU="Choose one of the following options:"

	OPTIONS=(1 "Search nodes"
	         2 "Measure Menu"
	         3 "Map Menu"
	         4 "Settings")

	CHOICE=$(dialog --clear \
	                --backtitle "$BACKTITLE" \
	                --title "$TITLE" \
	                --menu "$MENU" \
	                $HEIGHT $WIDTH $CHOICE_HEIGHT \
	                "${OPTIONS[@]}" \
	                2>&1 >/dev/tty)
	clear
	case $CHOICE in

			1)
				
				node_menu
				main_menu_gui;;

	        2)
	            
	            measure_menu
	            main_menu_gui;;
	        3)
	            
	            map_menu
	            main_menu_gui;;

	        4)
				settings_menu
				main_menu_gui;;    
	esac

}

settings_menu () {
	
	CHOICE_HEIGHT=6
	TITLE="SETTINGS MENU"
	MENU="Choose one of the following options:"

	OPTIONS=(1 "Plb web username (for all servers monitoring)"
	         2 "Plb web password (for all servers monitoring)"
	         3 "Plb slice name (for working with servers)"
	         4 "Plb slice private key (for working with servers)")

	CHOICE=$(dialog --clear \
	                --backtitle "$BACKTITLE" \
	                --title "$TITLE" \
	                --menu "$MENU" \
	                $HEIGHT 57 $CHOICE_HEIGHT \
	                "${OPTIONS[@]}" \
	                2>&1 >/dev/tty)
	clear
	case $CHOICE in
	        1)
	            
	            pl_name_input
	            settings_menu;;
	        2)	
				
	            pl_pass_input
	            settings_menu;;
	        3)	
				
	            sl_name_input
	            settings_menu;;
	    
	        4) 
	        	
	        	ssh_input
	        	settings_menu;;
	esac

}

measure_menu () {

	CHOICE_HEIGHT=4
	TITLE="MEASURE MENU"
	MENU="Choose one of the following options:"

	OPTIONS=(
	         1 "Set monitoring period"
	         2 "Set monitored elements"
	         3 "Monitor now")

	CHOICE=$(dialog --clear \
	                --backtitle "$BACKTITLE" \
	                --title "$TITLE" \
	                --menu "$MENU" \
	                $HEIGHT $WIDTH $CHOICE_HEIGHT \
	                "${OPTIONS[@]}" \
	                2>&1 >/dev/tty)
	clear
	case $CHOICE in
	        
	        1)
	            set_cron
	            measure_menu;;
	        2)
				set_elements
				build_script_for_cron
				measure_menu;;
			3)
	            pl_down
	            main_menu_gui;;
	esac

}

map_menu () {

	CHOICE_HEIGHT=4
	TITLE="MAP MENU"
	MENU="Choose one of the following options:"

	OPTIONS=(1 "Generate map"
	         2 "Select map elements")

	CHOICE=$(dialog --clear \
	                --backtitle "$BACKTITLE" \
	                --title "$TITLE" \
	                --menu "$MENU" \
	                $HEIGHT $WIDTH $CHOICE_HEIGHT \
	                "${OPTIONS[@]}" \
	                2>&1 >/dev/tty)
	clear
	case $CHOICE in
	        1)	
				generate_map
				map_menu;;
	        2)
	            map_elements
	            map_menu;;
	       
	esac
}

set_cron () {


	CHOICE_HEIGHT=4
	TITLE="Crontab menu"
	MENU="Choose one of the following options:"

	OPTIONS=(1 "Run measurement now"
	         2 "Set measurement daily"
	         3 "Set measurement weekly"
	         4 "Set measurement monthly"
	         5 "remove all measurement from cron")

	CHOICE=$(dialog --clear \
	                --backtitle "$BACKTITLE" \
	                --title "$TITLE" \
	                --menu "$MENU" \
	                $HEIGHT $WIDTH $CHOICE_HEIGHT \
	                "${OPTIONS[@]}" \
	                2>&1 >/dev/tty)
	clear
	case $CHOICE in
	        1)
	            now
	            set_cron;;
	        2)
	            daily
	            set_cron;;

	        3)
	            weekly
	            set_cron;;

	        4)
				monthly
				set_cron;;    

	        5)
				remove_cron
				set_cron;;    
	esac



}

selected_choice () {

	CHOICE_HEIGHT=3
	TITLE="Node menu"
	MENU=$(cat choice_info.txt)

	OPTIONS=(1 "Connect via SSH"
	         2 "Connect via MC"
	         3 "Show on map")

	CHOICE=$(dialog --clear \
	                --backtitle "$BACKTITLE" \
	                --title "$TITLE" \
	                --menu "$MENU" \
	                $HEIGHT $WIDTH $CHOICE_HEIGHT \
	                "${OPTIONS[@]}" \
	                2>&1 >/dev/tty)
	clear
	case $CHOICE in
	        1)
	 			connect_ssh
	 			selected_choice;;

	        2)
	            connect_mc
	            selected_choice;;

	        3)
				show_node
				selected_choice;;
   
	esac
}


node_menu () {
	sr_choice=""
	CHOICE_HEIGHT=3
	TITLE="Node menu"
	MENU=

	OPTIONS=(1 "Search by DNS"
	         2 "Search by IP"
	         3 "Search by location")

	CHOICE=$(dialog --clear \
	                --backtitle "$BACKTITLE" \
	                --title "$TITLE" \
	                --menu "$MENU" \
	                $HEIGHT $WIDTH $CHOICE_HEIGHT \
	                "${OPTIONS[@]}" \
	                2>&1 >/dev/tty)
	clear
	case $CHOICE in
	        1)
				sr_choice=3
	 			search_nodes;;

	        2)
	            sr_choice=2
	 			search_nodes;;

	        3)
				sr_choice=4
				search_by_loc;;
   
	esac
}




#------------GUI SETINGS CHECKBOXES-------------

map_elements(){
	map_setter=""
	CHOICE_HEIGHT=2
	TITLE="Map elements menu"
	CHECKLIST="Choose what to display on map(SPACE toggle ON/OFF):"

	
options=(1 "ICMP responds" off   
         2 "SSH time" off)

cmd=(dialog --separate-output --checklist \
	"$CHECKLIST" $HEIGHT $WIDTH $CHOICE_HEIGHT)


choices=$("${cmd[@]}" "${options[@]}" 2>&1 >/dev/tty)
clear
for choice in $choices
do
    case $choice in
        1)	map_ele_icmp
            ;;
        2)	map_ele_ssh
            ;;
        
    esac
done

}

set_elements(){

	cron_setter=""
	CHOICE_HEIGHT=3
	TITLE="Set monitored elements"
	CHECKLIST="Choose what to monitor(SPACE toggle ON/OFF):"

	options=(1 "Test ping" off
			 2 "Test SSH" off
			 3 "Skip non responsive servers for next measurements (reduces processing time)" off)

	cmd=(dialog --separate-output --checklist \
	"$CHECKLIST" $HEIGHT $WIDTH $CHOICE_HEIGHT)

	choices=$("${cmd[@]}" "${options[@]}" 2>&1 >/dev/tty)
clear
for choice in $choices
do
    case $choice in
        1)
			cron_setter_1
            ;;
        2)
			cron_setter_2
            ;;
        
    esac
done


	
}


#------------GUI SETINGS YESNO BOXES-------------


set_default(){

	TITLE="Warning"
	YESNO="This is going to set default login, passwords and ssh key"

	dialog --clear \
		   --backtitle "$BACKTITLE" \
		   --title "$TITLE" \
		   --yesno	"$YESNO" \
		   $HEIGHT $WIDTH \

	case $? in
  		0)
    		default_settings
    		;;
  		1)
    		echo "No chosen."
    		;;
  		255)
    		echo "ESC pressed."
    		;;
		esac

	clear
}

pl_down(){

	TITLE="Warning"
	YESNO="This is going to take around 20 minutes"

	dialog --clear \
		   --backtitle "$BACKTITLE" \
		   --title "$TITLE" \
		   --yesno	"$YESNO" \
		   $HEIGHT $WIDTH \

	case $? in
  		0)
    		download_planet
    		;;
  		1)
    		echo "No chosen."
    		;;
  		255)
    		echo "ESC pressed."
    		;;
		esac

	clear
}

#------------GUI SETINGS USER INPUTS-------------

user_input(){

	OUTPUT="/tmp/input.txt"
	dialog --clear \
		   --backtitle "$BACKTITLE" \
		   --title "$TITLE" \
		   --inputbox "$INPUTBOX" \
		   $HEIGHT $WIDTH \
		   2>$OUTPUT

	input=$(<$OUTPUT)

	trap "rm $OUTPUT; exit" SIGHUP SIGINT SIGTERM
	rm $OUTPUT
	clear

}

pass_input(){

	OUTPUT="/tmp/input.txt"
	dialog --clear \
		   --backtitle "$BACKTITLE" \
		   --title "$TITLE" \
		   --backtitle "$BACKTITLE" \
		   --passwordbox "$PASSBOX" \
		   $HEIGHT $WIDTH \
		   2>$OUTPUT

	pass=$(<$OUTPUT)

	trap "rm $OUTPUT; exit" SIGHUP SIGINT SIGTERM
	rm $OUTPUT
	clear
}

fselecte() {

dir=$(cd -P -- "$(dirname -- "$0")" && pwd -P)

	OUTPUT="/tmp/input.txt"
	dialog --clear \
	--backtitle "$BACKTITLE" \
	--title "ssh key" \
	--stdout \
	--title "Please choose a ssh key" \
	--fselect $dir 14 48 2>$OUTPUT

	fil=$(<$OUTPUT)
	
	trap "rm $OUTPUT; exit" SIGHUP SIGINT SIGTERM
	rm $OUTPUT
	clear

#
#	OUTPUT="/tmp/input.txt"
#	dialog --clear \
#		   --title "$TITLE" \
#		   --stdout \
#		   --fselect $pwd \
#		   $HEIGHT $WIDTH \
#		    2>$OUTPUT
#
#	fil=$(<$OUTPUT)
#	trap "rm $OUTPUT; exit" SIGHUP SIGINT SIGTERM
#	rm $OUTPUT
#	clear
}

search_input() {

	TITLE="Search"
	INPUTBOX="Search for:"
	user_input
	sr_input=$input
}

pl_name_input(){
	TITLE="WEB login"
	INPUTBOX="Login for Planetlab:"
	user_input
	sed -i -e"s/^USERNAME=.*/USERNAME=$input/" $CONF_PATH
}

sl_name_input(){
	TITLE="Slice login"
	INPUTBOX="Login to PL servers:"
	user_input
	sed -i -e"s/^SLICE=.*/SLICE=$input/" $CONF_PATH
}

pl_pass_input(){
	TITLE="WEB Password"
	PASSBOX="Password:"
	pass_input
	sed -i -e"s/^PASSWORD=.*/PASSWORD=$input/" $CONF_PATH
}

ssh_input(){

	TITLE="SSH key"
	fselecte
	ssh_key=$fil
	sed -i -e"s/^SSH_KEY=.*/SSH_KEY=$fil/" $CONF_PATH
}


#-----------BACKEND----------------
#---variables-----
path=$(pwd)
CONF_PATH="$path/bin/plbmng.conf"
planet_data=$(find $path -type f -name "default.node")


#---functions-----


#---check the internet-------

is_it_on () {

if ping -q -c 1 -W 1 8.8.8.8 >/dev/null
	then
	  	echo "ok"
	else
	 	 dialog --title "ERROR" --msgbox 'No internet connection detected ! program will not work properly ' $HEIGHT $WIDTH
	fi


}

first_run() {

	 	 dialog --title "Hello" --msgbox "$(cat bin/hello.txt)" $HEIGHT $WIDTH
	 	 settings_menu

}


#---search nodes functions-------------------------------------------------------------------------------------------------
search_nodes(){

	search_input

	if [ -z "$sr_input" ]
		then
	    	echo "VAR is empty"
	    	main_menu_gui

		else
			build_sr_out
			generate_node_info
			selected_choice
	fi	

	#rm choice_info.txt choice_temp.txt
	trap "rm choice_temp.txt choice_info.txt; exit" SIGHUP SIGINT SIGTERM
	sr_choice=""
}

build_sr_out(){

	counter=1

	cat $path/bin/search_nodes_prebuild.dat > search_function.sh

	cat $planet_data | cut -f$sr_choice | awk 'NR>1' | \
	grep $input | head -10 | while read line

	do 
		echo "\"$line\" \"$counter\" \\" >> search_function.sh
		let counter=counter+1
	done


	cat $path/bin/search_nodes_postbuild.dat >> search_function.sh

	chmod +x search_function.sh
	./search_function.sh
	rm search_function.sh 
}

build_sr_out_specy(){

	counter=1

	cat $path/bin/search_nodes_prebuild.dat > search_function.sh

	cat $planet_data | cut -f$sr_choice | awk 'NR>1' | sort | uniq \
	| while read line

	do
		echo "\"$line\" \"$counter\" \\" >> search_function.sh
		let counter=counter+1
	done


	cat $path/bin/search_nodes_postbuild.dat >> search_function.sh

	chmod +x search_function.sh
	./search_function.sh
	rm search_function.sh
}

build_sr_out_specy_2(){

	counter=1

	cat $path/bin/search_nodes_prebuild.dat > search_function.sh

	cat $planet_data  | awk 'NR>1'|grep $choice |cut -f$sr_choice | sort | uniq \
	| while read line

	do 
		echo "\"$line\" \"$counter\" \\" >> search_function.sh
		let counter=counter+1
	done


	cat $path/bin/search_nodes_postbuild.dat >> search_function.sh

	chmod +x search_function.sh
	./search_function.sh
	rm search_function.sh 
}

search_by_loc (){
build_sr_out_specy
choice=$(cat choice_temp.txt)
rm choice_temp.txt
sr_choice=5
build_sr_out_specy_2
choice=$(cat choice_temp.txt)
rm choice_temp.txt
sr_choice=3
build_sr_out_specy_2
generate_node_info
selected_choice
sr_choice=""

rm choice_info.txt choice_temp.txt
trap "rm choice_temp.txt choice_info.txt; exit" SIGHUP SIGINT SIGTERM

}

generate_node_info(){
	# useless use of cat gonna fix someday

	echo "Getting data"

	choice=$(cat choice_temp.txt)

	node=$(cat $planet_data | grep $choice | cut -f3)
	node_ip=$(cat $planet_data | grep $choice | cut -f2)
	continent=$(cat $planet_data | grep $choice | cut -f4)
	country=$(cat $planet_data | grep $choice | cut -f5)
	region=$(cat $planet_data | grep $choice | cut -f6)
	city=$(cat $planet_data | grep $choice | cut -f7)
	URL=$(cat $planet_data | grep $choice | cut -f8)
	name=$(cat $planet_data | grep $choice | cut -f9)
	lat=$(cat $planet_data | grep $choice | cut -f10)
	long=$(cat $planet_data | grep $choice | cut -f11)


	fping -C 2 -q $node_ip &> fpingout.txt
	icmp=$(cat fpingout.txt | awk '{print$4}')

    ssh -q\
    	-o "PreferredAuthentications=publickey"\
    	-o "PasswordAuthentication=no"\
    	-o "ConnectTimeout=20"\
    	-o "UserKnownHostsFile=/dev/null"\
    	-o "StrictHostKeyChecking=no"\
    	-i $ssh_key $sl_name@$node_ip exit

			if [ $? == 0 ]; then

         		ssh_status=AVAILABLE

 			else
        		ssh_status=UNAVAILABLE
 			fi
	rm fpingout.txt

	echo "
	NODE: $node
	IP: $node_ip
	CONTINENT: $continent
	COUNTRY: $country
	REGION: $region
	CITY: $city
	URL: $URL
	FULL NAME: $name
	LATITUDE: $lat  
	LONGITUDE: $long 
	ICMP RESPOND ($(date +%d-%b-%y_%H-%M)): $icmp
	SSH AVAILABILITY: $ssh_status" >choice_info.txt


}

#----end of search functions-------------------------------------------------------------------------------------
cron_setter_1(){

	cron_setter="1"

}

cron_setter_2(){

	cron_setter="${cron_setter}2"
}

now(){
    sh ${path}/cron_script.sh
}

daily(){

	 crontab -l | { cat; echo "@daily ${path}/bin/cron_script.sh"; } | crontab -

}

weekly(){

	crontab -l | { cat; echo "@weekly ${path}/bin/cron_script.sh"; } | crontab -
}

monthly(){

	crontab -l | { cat; echo "@monthly ${path}/bin/cron_script.sh"; } | crontab -
}

remove_cron(){

	crontab -l | grep -v cron_script | crontab -
}

build_script_for_cron(){

	rm cron_script.sh
	touch cron_script.sh
	chmod +x cron_script.sh

	echo "sl_name=$sl_name" >> cron_script.sh
	echo "ssh_key=$ssh_key" >> cron_script.sh

	if [ "$cron_setter" == "1" ]
		then
			cat $path/bin/icmp_build.dat >> cron_script.sh
			cat $path/bin/cron_postbuild_1.dat >> cron_script.sh
	fi

	if [ "$cron_setter" == "2" ]
		then
			cat $path/bin/ssh_build.dat >> cron_script.sh
			cat $path/bin/cron_postbuild_2.dat >> cron_script.sh
	fi			

	if [ "$cron_setter" == "12" ]
		then
			cat $path/bin/ssh_build.dat >> cron_script.sh
			cat $path/bin/icmp_build.dat >> cron_script.sh
			cat $path/bin/cron_postbuild_12.dat >> cron_script.sh
	fi			
}

default_settings(){
    . $CONF_PATH
    pl_name=$USERNAME
    pl_pass=$PASSWORD
    sl_name=$SLICE
	ssh_key=$SSH_KEY
}

connect_ssh(){

	echo "trying to connect to $node via SSH"
	ssh $sl_name@$node \
		-o "PreferredAuthentications=publickey"\
    	-o "PasswordAuthentication=no"\
    	-o "ConnectTimeout=20"\
    	-o "UserKnownHostsFile=/dev/null"\
    	-o "StrictHostKeyChecking=no"\
    	-o "IdentityFile=$ssh_key"
}

connect_mc(){

	echo "trying to conncet to $node via GNU midnight commander"
	ssh-add $ssh_key
	mc sh://$sl_name@$node:/home
}

show_node(){

	python3 $path/python_scripts/map_one.py $lat $long $node

	python3 -m webbrowser "map_1.html" > /dev/null 2>&1

	trap "rm map_1.html ; exit" SIGHUP SIGINT SIGTERM
}

map_ele_ssh(){

	map_setter="${map_setter}2"
}

map_ele_icmp(){

	map_setter=1
}

generate_map(){

	if [ "$map_setter" == "1" ]
		then
		data_prep_icmp
		python3 $path/python_scripts/icmp_map.py	
		python3 -m webbrowser "map_icmp.html" > /dev/null 2>&1
	fi

	if [ "$map_setter" == "2" ]
		then
		data_prep_ssh
		python3 $path/python_scripts/ssh_map.py	
		python3 -m webbrowser "map_ssh.html" > /dev/null 2>&1
	fi			

	if [ "$map_setter" == "12" ]
		then
		data_prep_full
		python3 $path/python_scripts/full_map.py	
		python3 -m webbrowser "map_full.html" > /dev/null 2>&1
	fi			

	
}

data_prep_icmp(){

	cat $planet_data| awk 'NR>1' |sort| uniq| cut -f10,11,3 | sort -k2 -u > python_scripts/base_data.txt
}

data_prep_ssh (){

	cat $planet_data| awk 'NR>1' |sort| uniq| cut -f10,11,3 | sort -k2 -u > python_scripts/base_data.txt

}

data_prep_full(){

	cat $planet_data| awk 'NR>1' |sort| uniq| cut -f10,11,3 | sort -k2 -u > python_scripts/base_data.txt

}

download_planet(){
    if [ $pl_name != "" ] && [ $pl_pass != "" ]; then
	    python3 $path/python_scripts/planetlab_list_creator.py -u $pl_name -p $pl_pass -o $path
	    ret=$?
	    if [ $ret != 0 ]; then
	        dialog --title "ERROR" --msgbox 'There was an error. There might be problem with your credentials.' $HEIGHT $WIDTH
	    fi
	else
	    echo "Please add your credentials into the config file(plbmng.conf located in bin folder)."
	fi
	backup_date=$(date +%d-%b-%y_%H-%M)
	cp $path/default.node $path/planetlab_$backup_date.node
}

run_full_measure(){

	echo "running full measure wait please"
	cat $planet_data |awk 'NR>1'| cut -f2 > IP.txt
	echo "testing ICMP responces"
	icmp_test
	rm IP.txt

	echo "runing SSH test"
	cat $planet_data |awk 'NR>1'| cut -f3 > hosts.txt
	ssh_test
	rm hosts.txt

}


icmp_test(){

	fping -C 2 -q < IP.txt  &> fpingout_all.txt

}

ssh_test (){

	pssh -h hosts.txt -l $sl_name\
		-O "PreferredAuthentications=publickey"\
    	-O "PasswordAuthentication=no"\
    	-O "UserKnownHostsFile=/dev/null"\
    	-O "StrictHostKeyChecking=no"\
    	-O "IdentityFile=$ssh_key"\
    	-t 0\
    	-o ssh_tst_out.txt\
    	-i "hostname"
}

#-----RUNING-----------

default_settings #for testing, can be commented out

if [ "$number_of_runs" == "1" ]; then
	first_run
fi

is_it_on
main_menu_gui
rm map_1.html map_full.html map_ssh.html map_icmp.html map_ssh.html map_full.html python_scripts/base_data.txt \
python_scripts/vega.json choice_info.txt choice_temp.txt > /dev/null 2>&1
rm full_measure.sh > /dev/null 2>&1





#---------------------------------------------------------------------------
