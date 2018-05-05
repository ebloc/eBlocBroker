#!/bin/bash

a=$(echo $0)
b=$(echo $1)
c=$(echo $2)
event=$(echo $c | awk '{print $8}')
echo "Your message | $a | $b | $c //$event ." | mail -s "Message Subject" alper.alimoglu@gmail.com
EBLOCBROKER_PATH="/home/alper/eBlocBroker"

if [[ $c == *" Began, "* ]]; then    
    jobID=$(echo "$c"   | grep -o -P '(?<=Job_id=).*(?= Name)')
    name=$(echo "$c"  | grep -o -P '(?<=Name=).*(?=.sh Began)')
    arg0=$(echo $name | cut -d "*" -f 1)
    arg1=$(echo $name | cut -d "*" -f 2)    
    
    echo "JOB STARTED: $name |$arg0 $arg1 jobID: $jobID" | mail -s "Message Subject" alper.alimoglu@gmail.com
    
    if [ "$argu0" != "$argu0" ]; then # jobKey and index should not be same
	. $EBLOCBROKER_PATH/venv/bin/activate && python3 -uB $EBLOCBROKER_PATH/startCode.py $arg0 $arg1 $jobID
    fi
fi

if [[ $event == *"COMPLETED"* ]]; then # Completed slurm jobs are catched here
    jobID=$(echo "$c"   | grep -o -P '(?<=Job_id=).*(?= Name)')
    
    name=$(echo "$c"   | grep -o -P '(?<=Name=).*(?=.sh Ended)')
    argu0=$(echo $name | cut -d "*" -f 1)
    argu1=$(echo $name | cut -d "*" -f 2)
    argu2=$(echo $name | cut -d "*" -f 3) 
    argu3=$(echo $name | cut -d "*" -f 4)
            
    echo "COMPLETED fileName:$name |argu0:$argu0 argu1:$argu1 argu2:$argu2 argu3:$argu3 jobID: $jobID" | mail -s "Message Subject" alper.alimoglu@gmail.com

    if [ "$argu0" != "$argu0" ]; then # jobKey and index should not be same
	. $EBLOCBROKER_PATH/venv/bin/activate && python3 -uB $EBLOCBROKER_PATH/endCode.py $argu0 $argu1 $argu2 $argu3 $name $jobID
    fi
fi

if [[ $event == *"TIMEOUT"* ]]; then # Timeouted slurm jobs are catched here
    jobID=$(echo "$c"   | grep -o -P '(?<=Job_id=).*(?= Name)')
    
    name=$(echo "$c"   | grep -o -P '(?<=Name=).*(?=.sh Failed)')
    argu0=$(echo $name | cut -d "*" -f 1)
    argu1=$(echo $name | cut -d "*" -f 2)
    argu2=$(echo $name | cut -d "*" -f 3) 
    argu3=$(echo $name | cut -d "*" -f 4) 
    
    echo "TIMEOUT fileName:$name |argu0:$argu0 argu1:$argu1 argu2:$argu2 argu3:$argu3 jobID: $jobID" | mail -s "Message Subject" alper.alimoglu@gmail.com

    if [ "$argu0" != "$argu0" ]; then # jobKey and index should not be same
	. $EBLOCBROKER_PATH/venv/bin/activate && python3 -uB $EBLOCBROKER_PATH/endCode.py $argu0 $argu1 $argu2 $argu3 $name $jobID
    fi
fi

if [[ $event == *" Failed, "* ]]; then # Cancelled job won't catched here

fi
