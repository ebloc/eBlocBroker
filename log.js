var nodePaths = require('./nodePaths');
var mylib     = require(nodePaths.EBLOCBROKER + '/eBlocBrokerHeader.js');

console.log('' + mylib.getDeployedBlockNumber())

readFrom = 1799549; //mylib.getDeployedBlockNumber();

mylib.LogJob(readFrom, nodePaths.LOG_PATH + '/queuedJobs.txt' ); /* Prints jobs, which are not COMPLETED */

//mylib.LogReceipt(readFrom, nodePaths.LOG_PATH + '/queuedJobs.txt');
