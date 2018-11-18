sl_name=cesnetple_vut_utko
ssh_key=/home/mak/.ssh/students_planetlab.pub

SSH_TEST () {


	Time_a=$(($(date +%s%N)/1000000))
   
    ssh -q\
    	-o "PreferredAuthentications=publickey"\
    	-o "PasswordAuthentication=no"\
    	-o "ConnectTimeout=20"\
    	-o "UserKnownHostsFile=/dev/null"\
    	-o "StrictHostKeyChecking=no"\
    	-i $ssh_key $sl_name@$1 exit


			if [ $? -eq 0 ]; then

         		Time_b=$(($(date +%s%N)/1000000))
         		ssh_time=`expr $Time_b - $Time_a`
        
 			else
        		ssh_time=-1
 			fi
ping_avg=-1
}
PING_TEST () {

	IP=$(nslookup $1 | awk '/^Address: / { print $2 ; exit }')

	if [[ -z "$IP" ]]; then
		ping_avg=-1
	else	

	ping -c 1 $IP > /dev/null

		if [ $? -eq 0 ]; then

			ping_avg=$(ping -c 3 $IP | tail -1| awk '{print $4}' | cut -d '/' -f 2)

		else
			ping_avg=-1
		fi
	fi
}
NOW=$(date +"%Y-%m-%d")
LOGFILE="logs/log-$NOW.log"

OUTPUT_WRITE () {

	echo "$1 $ping_avg $ssh_time" >> "$LOGFILE"

}



for i in $(cat default.node | awk 'NR>1 {print$3}')
  do
    echo $i
  	PING_TEST $i
  	SSH_TEST $i
  	OUTPUT_WRITE $i
done