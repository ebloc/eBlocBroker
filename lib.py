#!/usr/bin/env python3

import os, sys, subprocess, time, json, errno, glob, pwd, shutil
import binascii, base58

from lib_mongodb import addItem
from shutil  import copyfile
from dotenv  import load_dotenv
from os.path import expanduser
from colored import stylize, fg
from enum    import Enum

# enum: https://stackoverflow.com/a/1695250/2402577
def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    reverse = dict((value, key) for key, value in enums.items())
    enums['reverse_mapping'] = reverse
    return type('Enum', (), enums)

home = expanduser("~")
load_dotenv(os.path.join(home + '/.eBlocBroker/', '.env')) # Load .env from the given path

WHOAMI      = os.getenv('WHOAMI')
EBLOCPATH   = os.getenv('EBLOCPATH')
LOG_PATH    = os.getenv('LOG_PATH') 
PROVIDER_ID = os.getenv('PROVIDER_ID')
GDRIVE      = os.getenv('GDRIVE')
RPC_PORT    = os.getenv('RPC_PORT')
POA_CHAIN   = os.getenv('POA_CHAIN')
OC_USER     = os.getenv('OC_USER')
IPFS_USE    = os.getenv('IPFS_USE') # Should be "True/1", if caching into IPFS is open
EUDAT_USE   = os.getenv('EUDAT_USE')

if IPFS_USE == '0':
    IPFS_USE = False
else:
    IPFS_USE = True

if EUDAT_USE == '0':
    EUDAT_USE = False
else:
    EUDAT_USE = True

GDRIVE_CLOUD_PATH = '/home/' + WHOAMI + '/foo'
GDRIVE_METADATA   = '/home/' + WHOAMI + '/.gdrive'
IPFS_REPO         = '/home/' + WHOAMI + '/.ipfs'
HOME              = '/home/' + WHOAMI
OWN_CLOUD_PATH    = '/oc'

PROGRAM_PATH                = '/var/eBlocBroker' 
JOBS_READ_FROM_FILE         = LOG_PATH + '/test.txt'
CANCEL_JOBS_READ_FROM_FILE  = LOG_PATH + '/cancelledJobs.txt'
BLOCK_READ_FROM_FILE        = LOG_PATH + '/blockReadFrom.txt' 
CANCEL_BLOCK_READ_FROM_FILE = LOG_PATH + '/cancelledBlockReadFrom.txt'

class StorageID(Enum):
    IPFS = 0
    EUDAT = 1
    IPFS_MINILOCK = 2
    GITHUB = 3
    GDRIVE = 4
    
class CacheType(Enum):
    PRIVATE = 0
    PUBLIC = 1
    NONE = 2
    IPFS = 3
   
## Creates the hashmap.
job_state_code = {} 

# Add keys to the hashmap # https://slurm.schedmd.com/squeue.html
job_state_code['SUBMITTED']  = 0 # Initial state
job_state_code['PENDING']    = 1 # Job is awaiting resource allocation.
job_state_code['RUNNING']    = 2 # The job currently is allocated to a node and is running.
job_state_code['COMPLETED']  = 3 # Job has terminated all processes on all nodes with an exit code of zero.
job_state_code['REFUNDED']   = 4
job_state_code['CANCELLED']  = 5 # Job was explicitly cancelled by the user or system administrator. The job may or may not have been initiated.
job_state_code['TIMEOUT']    = 6 # Job terminated upon reaching its time limit.

inv_job_state_code = {v: k for k, v in job_state_code.items()}

Qm = b'\x12 '

def getIpfsHash(ipfsHash, resultsFolder, cacheType):
    # TODO try -- catch yap code run olursa ayni dosya'ya get ile dosyayi cekemiyor
    # cmd: ipfs get $ipfsHash --output=$resultsFolder
    res = subprocess.check_output(['ipfs', 'get', ipfsHash, '--output=' + resultsFolder]).decode('utf-8').strip() # Wait Max 5 minutes.
    print(res)

    if cacheType == CacheType.NONE.value: # TODO: pin if storage is paid
        res = subprocess.check_output(['ipfs', 'pin', 'add', ipfsHash]).decode('utf-8').strip() # pin downloaded ipfs hash
        log(res)

def isIpfsHashExists(ipfsHash, attemptCount):
    ipfsCallCounter = 0
    for attempt in range(attemptCount):
        log('Attempting to check IPFS file "' + ipfsHash + '"', 'light_salmon_3b')
        # IPFS_PATH=$HOME"/.ipfs" && export IPFS_PATH TODO: Probably not required
        # cmd: timeout 300 ipfs object stat $jobKey
        status, ipfsStat = executeShellCommand(['timeout', '300', 'ipfs', 'object', 'stat', ipfsHash]) # Wait Max 5 minutes.
        if not status:
            log('Error: Failed to find IPFS file "' + ipfsHash + '"', 'red')
        else:
            log(ipfsStat)
            for item in ipfsStat.split("\n"):
                if "CumulativeSize" in item:
                    cumulativeSize = item.strip().split()[1]                    
            return ipfsStat, status, cumulativeSize # Success
    else:
        return None, False, None

def calculateFolderSize(path, pathType):
    """Return the size of the given path in MB."""
    dataTransferOut = 0
    if pathType == 'f':
        p1 = subprocess.Popen(['ls', '-ln', path], stdout=subprocess.PIPE)
        p2 = subprocess.Popen(['awk', '{print $5}'], stdin=p1.stdout, stdout=subprocess.PIPE)
        p1.stdout.close()
        dataTransferOut = p2.communicate()[0].decode('utf-8').strip() # Retunrs downloaded files size in bytes
    elif pathType == 'd':
        p1 = subprocess.Popen(['du', '-sb', path], stdout=subprocess.PIPE)
        p2 = subprocess.Popen(['awk', '{print $1}'], stdin=p1.stdout, stdout=subprocess.PIPE)
        p1.stdout.close()
        dataTransferOut = p2.communicate()[0].decode('utf-8').strip() # Retunrs downloaded files size in bytes           
    
    dataTransferOut =  int(dataTransferOut) * 0.000001
    return dataTransferOut

def convertStringToBytes32(hash_string):
    bytes_array = base58.b58decode(hash_string)
    return binascii.hexlify(bytes_array).decode("utf-8")

def convertBytes32ToString(bytes_array):
    return base58.b58encode(bytes_array).decode("utf-8")

def convertBytes32ToIpfs(bytes_array):
    """Convert bytes_array into IPFS hash format."""
    merge = Qm + bytes_array
    return base58.b58encode(merge).decode("utf-8")

def convertIpfsToBytes32(hash_string):
    bytes_array = base58.b58decode(hash_string)
    b = bytes_array[2:]
    return binascii.hexlify(b).decode("utf-8")

def log(my_string, color='', newLine=True, file_name=LOG_PATH + '/transactions/providerOut.txt'): 
    if color != '':
        if newLine:
            print(stylize(my_string, fg(color)))
        else:
            print(stylize(my_string, fg(color)), end='')
    else:
        if newLine:
            print(my_string)
        else:
            print(my_string, end='')

    f = open(file_name, 'a')
    if newLine:
        f.write(my_string + '\n')
    else:
        f.write(my_string)
        
    f.close()

def subprocessCallAttempt(command, attemptCount, printFlag=0):    
    for i in range(attemptCount):
       try:
           result = subprocess.check_output(command).decode('utf-8').strip()
       except Exception as e:
           time.sleep(0.1)
           if i == 0 and printFlag == 0:
               log(str(e), 'red')
       else:
           return True, result
    else:
       return False, ""

def executeShellCommand(command, my_env=None, exitFlag=False):
    try:
        if my_env is None:
            result = subprocess.check_output(command).decode('utf-8').strip()
        else:
            result = subprocess.check_output(command, env=my_env).decode('utf-8').strip()
    except Exception as e:
        import traceback
        log(str(e), 'red')
        log(traceback.format_exc(), 'red')
        if exitFlag:
            sys.exit()
        return False, ""    

    return True, result


'''
def executeShellCommand(command, my_env=None, exitFlag=False):
    status=True
    try:
        if my_env is None:
            print('doo')
            p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print('doo')
        else:
            p = subprocess.Popen(command, env=my_env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        log("FAILED. " + e.output.decode('utf-8').strip(), 'red')

        print('doo')
    output, err = p.communicate()
    print('doo')
    if p.returncode != 0:
        status=False
        err = err.decode('utf-8')
        if err != '':
            log(err, 'red')
        if exitFlag:
            sys.exit()
            
    return output.strip().decode('utf-8'), status
'''

def silentremove(filename): # https://stackoverflow.com/a/10840586/2402577   
    try:
        os.remove(filename)
    except OSError as e: # this would be "except OSError, e:" before Python 2.6
        # if e.errno != errno.ENOENT: # errno.ENOENT = no such file or directory
        log(str(e), 'red')
        # raise # re-raise exception if a different error occurred

def removeFiles(filename):
   if "*" in filename: 
       for fl in glob.glob(filename):
           # print(fl)
           silentremove(fl) 
   else:
       silentremove(filename) 
       
def getMd5sum(gdriveInfo): 
    # cmd: echo gdriveInfo | grep \'Mime\' | awk \'{print $2}\'
    p1 = subprocess.Popen(['echo', gdriveInfo], stdout=subprocess.PIPE)
    p2 = subprocess.Popen(['grep', 'Md5sum'], stdin=p1.stdout, stdout=subprocess.PIPE)
    p1.stdout.close()
    p3 = subprocess.Popen(['awk', '{print $2}'], stdin=p2.stdout,stdout=subprocess.PIPE)
    p2.stdout.close()
    return p3.communicate()[0].decode('utf-8').strip()    

def getMimeType(gdriveInfo): 
    # cmd: echo gdriveInfo | grep \'Mime\' | awk \'{print $2}\'
    p1 = subprocess.Popen(['echo', gdriveInfo], stdout=subprocess.PIPE)
    p2 = subprocess.Popen(['grep', 'Mime'], stdin=p1.stdout, stdout=subprocess.PIPE)
    p1.stdout.close()
    p3 = subprocess.Popen(['awk', '{print $2}'], stdin=p2.stdout,stdout=subprocess.PIPE)
    p2.stdout.close()
    return p3.communicate()[0].decode('utf-8').strip()    

def getFolderName(gdriveInfo): 
    # cmd: echo gdriveInfo | grep \'Name\' | awk \'{print $2}\'
    p1 = subprocess.Popen(['echo', gdriveInfo], stdout=subprocess.PIPE)
    p2 = subprocess.Popen(['grep', 'Name'], stdin=p1.stdout, stdout=subprocess.PIPE)
    p1.stdout.close()
    p3 = subprocess.Popen(['awk', '{print $2}'], stdin=p2.stdout,stdout=subprocess.PIPE)
    p2.stdout.close()
    return p3.communicate()[0].decode('utf-8').strip()    

def eBlocBrokerFunctionCall(f, _attempt):
    for attempt in range(_attempt):
        status, result = f()
        if status:
            return True, result
        else:
            log("Error: " + result, 'red')
            if result == 'notconnected':
                time.sleep(1)
            else:
                return False, result
    else:
        return False, result

def isIpfsHashCached(ipfsHash):
    # cmd: ipfs refs local | grep -c 'Qmc2yZrduQapeK47vkNeT5pCYSXjsZ3x6yzK8an7JLiMq2'
    p1 = subprocess.Popen(['ipfs', 'refs', 'local'], stdout=subprocess.PIPE)
    p2 = subprocess.Popen(['grep', '-c', ipfsHash], stdin=p1.stdout, stdout=subprocess.PIPE)
    p1.stdout.close()
    out = p2.communicate()[0].decode('utf-8').strip()
    if out == '1':    
        return True
    else:
        return False
      
# Checks whether Slurm runs on the background or not, if not runs slurm
def isSlurmOn():
   while True:
      subprocess.run(['bash', 'checkSinfo.sh'])
      with open(LOG_PATH + '/checkSinfoOut.txt', 'r') as content_file:
         check = content_file.read()

      if not "PARTITION" in str(check):
         log("Error: sinfo returns emprty string, please run:\nsudo ./runSlurm.sh\n", "red")
         log('Error Message: \n' + check, "red")         
         log('Starting Slurm... \n', "green")
         subprocess.run(['sudo', 'bash', 'runSlurm.sh'])
      elif "sinfo: error" in str(check): 
         log("Error on munged: \n" + check)
         log("Please Do:\n")
         log("sudo munged -f")
         log("/etc/init.d/munge start")
      else:
         log('Slurm is on.', 'green')
         break

def preexec_function():
    signal.signal(signal.SIGINT, signal.SIG_IGN)

def isTransactionPassed(w3, tx_hash):
    receipt = w3.eth.getTransactionReceipt(tx_hash)
    if receipt is None:
        return False
    
    if receipt['status'] == 1:
        return True
    else:
        return False
    
# Checks that does IPFS run on the background or not
def isIpfsOn():
   # cmd: ps aux | grep '[i]pfs daemon' | wc -l
   p1 = subprocess.Popen(['ps', 'aux'], stdout=subprocess.PIPE)
   p2 = subprocess.Popen(['grep', '[i]pfs\ daemon'], stdin=p1.stdout, stdout=subprocess.PIPE)
   p1.stdout.close()
   p3 = subprocess.Popen(['wc', '-l'], stdin=p2.stdout,stdout=subprocess.PIPE)
   p2.stdout.close()
   check = p3.communicate()[0].decode('utf-8').strip()
   if int(check) == 0:
      log("Error: IPFS does not work on the background.", 'red') 
      log('* Starting IPFS: nohup ipfs daemon --mount &', 'green')
      with open(LOG_PATH + '/ipfs.out', 'w') as stdout:
         subprocess.Popen(['nohup', 'ipfs', 'daemon', '--mount'],
                          stdout=stdout,
                          stderr=stdout,
                          preexec_fn=os.setpgrp)
         
      time.sleep(5)
      with open(LOG_PATH + '/ipfs.out', 'r') as content_file:
         log(content_file.read(), 'blue')
         
      # IPFS mounted at: /ipfs //cmd: sudo ipfs mount -f /ipfs      
      res = subprocess.check_output(['sudo', 'ipfs', 'mount', '-f', '/ipfs']).decode('utf-8').strip()
      log(res)      
   else:
      log("IPFS is already on.", 'green') 

def isRunExistInTar(tarPath):
    try:
        FNULL = open(os.devnull, 'w')
        print(tarPath)
        res = subprocess.check_output(['tar', 'ztf', tarPath, '--wildcards', '*/run.sh'], stderr=FNULL).decode('utf-8').strip()
        FNULL.close()
        if res.count('/') == 1: # Main folder should contain the 'run.sh' file
            log('./run.sh exists under the parent folder', 'green')
            return True
        else:
            log('run.sh does not exist under the parent folder', 'red')
            sys.exit() # TODO: delete
            return False            
    except:
        log('run.sh does not exist under the parent folder', 'red')
        sys.exit() # TODO: delete
        return False

def compressFolder(folderToShare):
    current_path = os.getcwd()

    base_name = os.path.basename(folderToShare)
    dir_path   = os.path.dirname(folderToShare)
    os.chdir(dir_path)        
    subprocess.run(['chmod', '-R', '777', base_name])
    # Tar produces different files each time: https://unix.stackexchange.com/a/438330/198423
    # find exampleFolderToShare -print0 | LC_ALL=C sort -z | GZIP=-n tar --absolute-names --no-recursion --null -T - -zcvf exampleFolderToShare.tar.gz
    p1 = subprocess.Popen(['find', base_name, '-print0'], stdout=subprocess.PIPE)
    p2 = subprocess.Popen(['sort', '-z'], stdin=p1.stdout, stdout=subprocess.PIPE, env={'LC_ALL': 'C'})
    p1.stdout.close()
    p3 = subprocess.Popen(['tar', '--absolute-names', '--no-recursion', '--null', '-T', '-', '-zcvf', base_name + '.tar.gz'],
                          stdin=p2.stdout,stdout=subprocess.PIPE, env={'GZIP': '-n'})
    p2.stdout.close()
    p3.communicate()
    # subprocess.run(['sudo', 'tar', 'zcf', base_name + '.tar.gz', base_name])
    tarHash = subprocess.check_output(['md5sum', base_name + '.tar.gz']).decode('utf-8').strip()
    tarHash = tarHash.split(' ', 1)[0]    
    print('hash=' + tarHash)   
    shutil.move(base_name + '.tar.gz', tarHash + '.tar.gz')
    os.chdir(current_path)
    return tarHash

def sbatchCall(loggedJob, shareToken, requesterID, resultsFolder, resultsFolderPrev, dataTransferIn, sourceCodeHash_list, jobInfo, eBlocBroker, w3):
   jobKey    = loggedJob.args['jobKey']
   index     = loggedJob.args['index']
   storageID = loggedJob.args['storageID']
    
   from contractCalls.getJobInfo import getJobInfo
   from datetime import datetime, timedelta   
   # cmd: date --date=1 seconds +%b %d %k:%M:%S %Y
   date = subprocess.check_output(['date', '--date=' + '1 seconds', '+%b %d %k:%M:%S %Y'], env={'LANG': 'en_us_88591'}).decode('utf-8').strip()
   log('Date=' + date)
   f = open(resultsFolderPrev + '/modifiedDate.txt', 'w') 
   f.write(date + '\n' )    
   f.close()   
   # cmd: echo date | date +%s
   p1 = subprocess.Popen(['echo', date], stdout=subprocess.PIPE)
   p2 = subprocess.Popen(['date', '+%s'], stdin=p1.stdout, stdout=subprocess.PIPE)
   p1.stdout.close()
   timestamp = p2.communicate()[0].decode('utf-8').strip()
   log('Timestamp=' + timestamp)
   f = open(resultsFolderPrev + '/timestamp.txt', 'w') 
   f.write(timestamp + '\n')      
   f.close()

   log('job_receivedBlockNumber=' + str(loggedJob.blockNumber))
   f = open(resultsFolderPrev + '/receivedBlockNumber.txt', 'w') 
   f.write(str(loggedJob.blockNumber) + '\n')      
   f.close()   

   log('Adding recevied job into mongodb database.', 'green')
   # Adding jobKey info along with its cacheTime into mongodb
   addItem(jobKey, sourceCodeHash_list, requesterID, timestamp, storageID, jobInfo)
   
   if os.path.isfile(resultsFolderPrev + '/dataTransferIn.txt'):
       with open(resultsFolderPrev + '/dataTransferIn.txt') as json_file:
           data = json.load(json_file)
           dataTransferIn = data['dataTransferIn']
   else:
       data = {}
       data['dataTransferIn'] = dataTransferIn
       with open(resultsFolderPrev + '/dataTransferIn.txt', 'w') as outfile:
           json.dump(data, outfile)
           
   # print(dataTransferIn) 
   time.sleep(0.25)
   if not os.path.isfile(resultsFolder + '/run.sh'):
       log(resultsFolder + '/run.sh does not exist', 'red')
       return False
   
   copyfile(resultsFolder + '/run.sh', resultsFolder + '/' + jobKey + '*' + str(index) + '*' + str(storageID) + '*' + shareToken + '.sh')

   jobID = 0 # Base jobID
   status, jobInfo = getJobInfo(PROVIDER_ID, jobKey, int(index), jobID, eBlocBroker, w3)   
   jobCoreNum    = str(jobInfo['core'])
   executionTimeSecond = timedelta(seconds=int((jobInfo['executionTimeMin'] + 1) * 60))  # Client's requested seconds to run his/her job, 1 minute additional given.
   d         = datetime(1,1,1) + executionTimeSecond 
   timeLimit = str(int(d.day)-1) + '-' + str(d.hour) + ':' + str(d.minute) 
   log("timeLimit=" + str(timeLimit) + "| RequestedCoreNum=" + jobCoreNum)
   # Give permission to user that will send jobs to Slurm.
   subprocess.check_output(['sudo', 'chown', '-R', requesterID, resultsFolder])

   for attempt in range(10):
       try:
           ## SLURM submit job, Real mode -N is used. For Emulator-mode -N use 'sbatch -c'   
           ## cmd: sudo su - $requesterID -c "cd $resultsFolder && sbatch -c$jobCoreNum $resultsFolder/${jobKey}*${index}*${storageID}*$shareToken.sh --mail-type=ALL   
           jobID = subprocess.check_output(['sudo', 'su', '-', requesterID, '-c',
                                            'cd' + ' ' + resultsFolder + ' && ' + 'sbatch -N' + jobCoreNum + ' ' + 
                                            resultsFolder + '/' + jobKey + '*' + str(index) + '*' + str(storageID) + '*' + shareToken + '.sh' + ' ' + 
                                            '--mail-type=ALL']).decode('utf-8').strip()
           time.sleep(1) # Wait 1 second for Slurm idle core to be updated. 
       except subprocess.CalledProcessError as e:
           log(e.output.decode('utf-8').strip(), 'red')
           # sacctmgr remove user where user=$USERNAME --immediate
           status, res = executeShellCommand(['sacctmgr', 'remove', 'user', 'where', 'user=' + requesterID, '--immediate'])
           ## sacctmgr add account $USERNAME --immediate
           status, res = executeShellCommand(['sacctmgr', 'add', 'account', requesterID, '--immediate'])
           ## sacctmgr create user $USERNAME defaultaccount=$USERNAME adminlevel=[None] --immediate
           status, res = executeShellCommand(['sacctmgr', 'create', 'user', requesterID, 'defaultaccount=' + requesterID, 'adminlevel=[None]', '--immediate'])
       else:
           break
   else:
       sys.exit()
           
   slurmJobID = jobID.split()[3]
   log('slurmJobID=' + slurmJobID)
   try:
       # cmd: scontrol update jobid=$slurmJobID TimeLimit=$timeLimit
       subprocess.run(['scontrol', 'update', 'jobid=' + slurmJobID, 'TimeLimit=' + timeLimit], stderr=subprocess.STDOUT)
   except subprocess.CalledProcessError as e:
       log(e.output.decode('utf-8').strip(), 'red')
      
   if not slurmJobID.isdigit():
       # Detects an error on the SLURM side
       log("Error: slurm_jobID is not a digit.", 'red')
       return False

   return True
