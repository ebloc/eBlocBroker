#!/bin/bash

alias sudo='nocorrect sudo'
echo "==> logname="$(logname)
_LOGNAME=$(whoami)
if [[ $(whoami) == "root" ]] ; then
    _LOGNAME="alper"
fi

verbose=false
# verbose=true
sudo killall slurmd slurmdbd slurmctld > /dev/null 2>&1
sudo rm -f /var/run/slurmdbd.pid
sudo chown $_LOGNAME -R /var/log/slurm/
DIR="$( cd "$( dirname "$0" )" && pwd )"
sudo $DIR/run_munge.sh
sudo /usr/local/sbin/slurmd
# sudo /usr/local/sbin/slurmd -N $(hostname -s)  # emulate mode
sudo /usr/local/sbin/slurmdbd &
sleep 2.0
sudo -u $_LOGNAME mkdir -p /tmp/slurmstate
sudo chown -R $_LOGNAME /tmp/slurmstate
if [ "$verbose" = true ] ; then
    sudo /usr/local/sbin/slurmctld -cDvvvvvv  # verbose
    # sudo -u $(logname) /usr/local/sbin/slurmctld -cDvvvvvv
else
    sudo -u $_LOGNAME /usr/local/sbin/slurmctld -c
    sleep 1.0
    squeue | tail -n+2 | awk '{print $1}' | xargs scancel 2> /dev/null
    /usr/local/bin/sinfo -N -l
    echo ""
    scontrol show node
fi
