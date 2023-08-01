#!/bin/bash

# Link: https://stackoverflow.com/questions/43449165/could-slurm-trigger-a-scriptimplemented-by-the-frontend-slurm-user-when-any-jo

_HOME="/home/username"  # may differ for each providerget from the file name
# EMAIL=""
VENV_PATH=${_HOME}"/venv"
BROKER_PATH=${_HOME}"/ebloc-broker/broker"
LOG_FILE=${_HOME}"/.ebloc-broker/slurm_script.log"
SEP="~"
a=$0
b=$1
c=$2
event=$(echo $c | awk '{print $8}')
msg="==> [$(date)] $a $b $c \n$event"
# echo $msg | mail -s "Message Subject" $EMAIL
echo "-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-" >> $LOG_FILE
echo $msg >> $LOG_FILE
slurm_job_id=$(echo "$c" | grep -o -P '(?<=Job_id=).*(?= Name)')
if [[ $c == *" Began, "* ]]; then
    name=$(echo "$c"  | grep -o -P '(?<=Name=).*(?=.sh Began)')
    arg0=$(echo $name | cut -d "$SEP" -f 1)  # job_key
    arg1=$(echo $name | cut -d "$SEP" -f 2)  # index
    arg2=$(echo $name | cut -d "$SEP" -f 3)  # jobid

    msg="JOB_STARTED fn=$name\n"
    msg="${msg}${BROKER_PATH}/start_code.py $arg0 $arg1 $slurm_job_id"
    # echo $msg | mail -s "Message Subject" $EMAIL
    echo -e $msg >> $LOG_FILE
    if [ "$arg0" != "$arg1" ]; then  # job_key and index should not be same
        . $VENV_PATH/bin/activate
        nohup $BROKER_PATH/start_code.py $arg0 $arg1 $arg2 $slurm_job_id >/dev/null 2>&1
    fi
fi

if [[ $event == *"COMPLETED"* ]] || [[ $event == *"FAILED"* ]]; then
    name=$(echo "$c"  | grep -o -P '(?<=Name=).*(?=.sh Ended)')
    if [[ $event == *"COMPLETED"* ]]; then
        state="COMPLETED"
        name=$(echo "$c" | grep -o -P '(?<=Name=).*(?=.sh Ended)')
    fi

    if [[ $event == *"FAILED"* ]]; then
        state="FAILED"
        name=$(echo "$c" | grep -o -P '(?<=Name=).*(?=.sh Failed)')
    fi
    arg0=$(echo $name | cut -d "$SEP" -f 1)  # job_key
    arg1=$(echo $name | cut -d "$SEP" -f 2)  # index
    arg2=$(echo $name | cut -d "$SEP" -f 3)  # received_bn
    arg3=$(echo $name | cut -d "$SEP" -f 4)  # jobid

    msg="$state fn=$name\n"
    msg="${msg}${BROKER_PATH}/end_code.py $arg0 $arg1 $arg2 $arg3 \"$name\" $slurm_job_id"
    # echo $msg | mail -s "Message Subject" $EMAIL
    echo -e $msg >> $LOG_FILE
    if [ "$arg0" != "$arg1" ]; then  # job_key and index should not be same
        . $VENV_PATH/bin/activate
        nohup $BROKER_PATH/end_code.py $arg0 $arg1 $arg2 $arg3 $name $slurm_job_id >/dev/null 2>&1
    fi
fi

if [[ $event == *"TIMEOUT"* ]]; then
    name=$(echo "$c"   | grep -o -P '(?<=Name=).*(?=.sh Failed)')
    arg0=$(echo $name | cut -d "$SEP" -f 1)  # job_key
    arg1=$(echo $name | cut -d "$SEP" -f 2)  # index
    arg2=$(echo $name | cut -d "$SEP" -f 3)  # received_bn
    arg3=$(echo $name | cut -d "$SEP" -f 4)  # jobid

    msg="TIMEOUT fn=$name\n"
    msg="${msg}${BROKER_PATH}/end_code.py $arg0 $arg1 $arg2 $arg3 \"$name\" $slurm_job_id"
    # echo $msg | mail -s "Message Subject" $EMAIL
    echo -e $msg >> $LOG_FILE
    if [ "$arg0" != "$arg1" ]; then  # job_key and index should not be same
        . $VENV_PATH/bin/activate
        $BROKER_PATH/end_code.py $arg0 $arg1 $arg2 $arg3 $name $slurm_job_id
    fi
fi

if [[ $event == *"CANCELLED"* ]]; then
    name=$(echo "$c"  | grep -o -P '(?<=Name=).*(?=.sh Ended)')
    arg0=$(echo $name | cut -d "$SEP" -f 1)  # job_key
    arg1=$(echo $name | cut -d "$SEP" -f 2)  # index
    arg2=$(echo $name | cut -d "$SEP" -f 3)  # received_bn
    arg3=$(echo $name | cut -d "$SEP" -f 4)  # jobid

    msg="CANCELLED fn=$name\n"
    msg="${msg}${BROKER_PATH}/end_code.py $arg0 $arg1 $arg2 $arg3 \"$name\" $slurm_job_id"
    # echo $msg | mail -s "Message Subject" $EMAIL
    echo -e $msg >> $LOG_FILE
    if [ "$arg0" != "$arg1" ]; then  # job_key and index should not be same
        . $VENV_PATH/bin/activate
        nohup $BROKER_PATH/end_code.py $arg0 $arg1 $arg2 $arg3 $name $slurm_job_id >/dev/null 2>&1
    fi
fi
