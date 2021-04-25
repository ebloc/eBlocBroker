# Slurm Emulator Mode Setup

## [Guide1]( http://wildflower.diablonet.net/~scaron/slurmsetup.html )
## [Guide2]( https://slurm.schedmd.com/faq.html#multi_slurmd )

1. Package install

```
sudo apt-get update
sudo apt-get install build-essential gcc libmunge-dev libmunge2 munge mysql-server
sudo apt-get install mysql-client libmysqlclient-dev
sudo apt-get install default-libmysqlclient-dev
#
# apt-cache search mysql | grep "dev"
# sudo apt-get install libmysqld-dev
# sudo apt-get install libmysqlclient
```

```bash
cd ~/
git clone https://github.com/SchedMD/slurm
cd slurm

# In order to emulate a larger cluster
./configure --enable-debug --enable-multiple-slurmd  # ./configure --enable-debug --enable-front-end
sudo make
sudo make install

sudo cp ~/eBlocBroker/slurm_guide/emulator_mode/slurm.conf /usr/local/etc/slurm.conf
sudo cp ~/eBlocBroker/slurm_guide/emulator_mode/slurmdbd.conf /usr/local/etc/slurmdbd.conf

sudo chmod 0600 /usr/local/etc/slurmdbd.conf /usr/local/etc/slurm.conf
```

2. HOSTNAME Setup

```
_HOSTNAME="home"
sudo hostnamectl set-hostname $_HOSTNAME
hostname
```

3. Setup

```
sudo mkdir -p /var/log/slurm
```

4. Set things up for slurmdbd (the SLURM accounting daemon) in MySQL. !(slurm == $(username))!

Should run `sudo slurmdbd` on the background in order to register the slurm-user.

```
sudo /etc/init.d/mysql start

sudo su
mysql -u root -p  [ENTER]

create database slurm_acct_db;
CREATE USER 'slurm'@'localhost' IDENTIFIED BY '12345'; | create user 'slurm'@'localhost';
                                                       | ALTER USER 'slurm'@'localhost' IDENTIFIED BY '12345';
CREATE USER alper'@'localhost' IDENTIFIED BY '12345';
grant usage on *.* to 'slurm'@'localhost';
grant all privileges on slurm_acct_db.* to 'slurm'@'localhost';
flush privileges;

SHOW DATABASES;
DROP DATABASE slurm_acct_db;
```

```
SELECT User FROM mysql.user;
CREATE USER 'slurm'@'localhost' IDENTIFIED BY '12345';
CREATE USER 'alper'@'localhost' IDENTIFIED BY '12345';  # 'slurm'=> $(whoami)
```

--------------------------------------

5. Cont

Should run `sudo slurmdbd` on the background in order to register the slurm-user.

```
user_name=$(whoami)

sacctmgr add cluster home
sacctmgr add account $user_name
sacctmgr create user $user_name defaultaccount=$user_name adminlevel=None

# Following line is required only to remove
sacctmgr remove user where user=user_name
```

### Check registered provider and users

```
sacctmgr list cluster
sacctmgr show assoc format=account
sacctmgr show assoc format=account,user,partition where user=<user_name>

sacctmgr show user -s
```

--------------------------------------------------------------------------------------------------------

# Provider

Version of slurmctld should be same between frontend node and compute nodes.

Solution: munge key must be identical both in master and computing nodes.

```
SlurmctldPort=3002 ==> Controllers that port should be open.
SlurmdPort=6821    ==> Compute nodes all that port should be open.

id -u username
pkill -U UID
sudo usermod -u 1000 username
```
