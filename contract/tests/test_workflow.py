#!/usr/bin/python3

import os
import sys
from os import path

import pytest

import brownie
from broker import cfg, config
from broker._utils._log import console_ruler
from broker.config import setup_logger
from broker.eblocbroker_scripts import Contract
from broker.eblocbroker_scripts.job import Job
from broker.utils import CacheType, StorageID, ipfs_to_bytes32, log
from brownie import accounts, web3
from brownie.network.state import Chain
from contract.scripts.lib import mine, new_test
from contract.tests.test_overall_eblocbroker import register_provider, register_requester

# from brownie.test import given, strategy

COMMITMENT_BLOCK_NUM = 600
Contract.eblocbroker = Contract.Contract(is_brownie=True)

setup_logger("", True)
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
cwd = os.getcwd()
provider_gmail = "provider_test@gmail.com"
fid = "ee14ea28-b869-1036-8080-9dbd8c6b1579@b2drop.eudat.eu"

available_core = 128
price_core_min = 1
price_data_transfer = 1
price_storage = 1
price_cache = 1
prices = [price_core_min, price_data_transfer, price_storage, price_cache]

GPG_FINGERPRINT = "0359190A05DF2B72729344221D522F92EFA2F330"
ipfs_address = "/ip4/79.123.177.145/tcp/4001/ipfs/QmWmZQnb8xh3gHf9ZFmVQC4mLEav3Uht5kHJxZtixG3rsf"
Ebb = None
chain = None
ebb = None

gas_costs = {}
gas_costs["registerRequester"] = []
gas_costs["registerProvider"] = []
gas_costs["setJobStateRunning"] = []
gas_costs["refund"] = []
gas_costs["setDataVerified"] = []
gas_costs["processPayment"] = []
gas_costs["withdraw"] = []
gas_costs["authenticateOrcID"] = []
gas_costs["depositStorage"] = []
gas_costs["updateProviderInfo"] = []
gas_costs["updataDataPrice"] = []
gas_costs["updateProviderPrices"] = []
gas_costs["registerData"] = []


def to_gwei(value):
    return web3.toWei(value, "gwei")


@pytest.fixture(scope="module", autouse=True)
def my_own_session_run_at_beginning(_Ebb):
    global Ebb  # noqa
    global chain  # noqa
    global ebb  # noqa

    cfg.IS_BROWNIE_TEST = True
    config.Ebb = Ebb = Contract.Contract(is_brownie=True)
    config.ebb = _Ebb
    cfg.Ebb.eBlocBroker = Contract.eblocbroker.eBlocBroker = _Ebb
    ebb = _Ebb
    Ebb.w3 = web3
    if not config.chain:
        config.chain = Chain()

    chain = config.chain


@pytest.fixture(autouse=True)
def run_around_tests():
    new_test()


def check_price_keys(price_keys, provider, code_hash):
    res = ebb.getRegisteredDataBlockNumbers(provider, code_hash)
    for key in price_keys:
        if key > 0:
            assert key in res, f"{key} does no exist in price keys({res}) for the registered data{code_hash}"


def remove_zeros_gpg_fingerprint(_gpg_fingerprint):
    return str(_gpg_fingerprint).replace("0x000000000000000000000000", "").upper()


def get_block_number():
    log(f"block_number={web3.eth.blockNumber} | contract_bn={web3.eth.blockNumber + 1}", "bold")
    return web3.eth.blockNumber


def get_block_timestamp():
    return web3.eth.getBlock(get_block_number()).timestamp


def withdraw(address, amount):
    temp = address.balance()
    assert ebb.balanceOf(address) == amount
    tx = ebb.withdraw({"from": address, "gas_price": 0})
    gas_costs["withdraw"].append(tx.__dict__["gas_used"])
    received = address.balance() - temp
    assert to_gwei(amount) == received
    assert ebb.balanceOf(address) == 0


def test_workflow():
    job = Job()
    provider = accounts[0]
    requester = accounts[1]
    register_provider()
    register_requester(requester)
    job_key = "QmQv4AAL8DZNxZeK3jfJGJi63v1msLMZGan7vSsCDXzZud"
    code_hash = ipfs_to_bytes32(job_key)
    with brownie.reverts():
        ebb.updataDataPrice(code_hash, 20, 100, {"from": provider})

    tx = ebb.registerData(code_hash, 20, cfg.ONE_HOUR_BLOCK_DURATION, {"from": provider})
    gas_costs["registerData"].append(tx.__dict__["gas_used"])

    ebb.removeRegisteredData(code_hash, {"from": provider})  # should submitJob fail if it is not removed
    code_hash1 = "0x68b8d8218e730fc2957bcb12119cb204"
    ebb.registerData(code_hash1, 20, cfg.ONE_HOUR_BLOCK_DURATION, {"from": provider})
    gas_costs["registerData"].append(tx.__dict__["gas_used"])
    mine(6)
    with brownie.reverts():
        ebb.registerData(code_hash1, 21, 1000, {"from": provider})

    tx = ebb.updataDataPrice(code_hash1, 250, cfg.ONE_HOUR_BLOCK_DURATION, {"from": provider})
    gas_costs["updataDataPrice"].append(tx.__dict__["gas_used"])
    tx = ebb.updataDataPrice(code_hash1, 251, cfg.ONE_HOUR_BLOCK_DURATION + 1, {"from": provider})
    gas_costs["updataDataPrice"].append(tx.__dict__["gas_used"])
    data_block_numbers = ebb.getRegisteredDataBlockNumbers(provider, code_hash1)
    log(f"get_registered_data_block_numbers={data_block_numbers[1]}", "bold")
    get_block_number()
    data_prices = ebb.getRegisteredDataPrice(provider, code_hash1, 0)
    assert data_prices[0] == 20
    output = ebb.getRegisteredDataPrice(provider, code_hash1, data_block_numbers[-1])
    assert output[0] == 251
    mine(cfg.ONE_HOUR_BLOCK_DURATION - 10)
    output = ebb.getRegisteredDataPrice(provider, code_hash1, 0)
    log(f"register_data_price={output}", "bold")
    assert output[0] == 20
    mine(1)
    output = ebb.getRegisteredDataPrice(provider, code_hash1, 0)
    log(f"register_data_price={output}", "bold")
    assert output[0] == 251

    job.code_hashes = [code_hash, code_hash1]  # Hashed of the data file in array
    job.storage_hours = [0, 0]
    job.data_transfer_ins = [100, 0]
    job.data_transfer_out = 100

    # job.data_prices_set_block_numbers = [0, 253]  # TODO: check this ex 253 exists or not
    job.data_prices_set_block_numbers = [0, data_block_numbers[1]]  # TODO: check this ex 253 exists or not
    check_price_keys(job.data_prices_set_block_numbers, provider, code_hash1)
    job.cores = [2, 4, 2]
    job.run_time = [10, 15, 20]
    job.storage_ids = [StorageID.IPFS.value, StorageID.NONE.value]
    job.cache_types = [CacheType.PUBLIC.value, CacheType.PUBLIC.value]
    args = [
        provider,
        ebb.getProviderSetBlockNumbers(accounts[0])[-1],
        job.storage_ids,
        job.cache_types,
        job.data_prices_set_block_numbers,
        job.cores,
        job.run_time,
        job.data_transfer_out,
    ]
    job_price, cost = job.cost(provider, requester)
    tx = ebb.submitJob(  # first submit
        job_key,
        job.data_transfer_ins,
        args,
        job.storage_hours,
        job.code_hashes,
        {"from": requester, "value": to_gwei(job_price)},
    )
    for idx in range(0, 3):
        log(ebb.getJobInfo(provider, job_key, 0, idx))

    console_ruler(character="-=")
    assert (
        tx.events["LogRegisteredDataRequestToUse"][0]["registeredDataHash"]
        == "0x0000000000000000000000000000000068b8d8218e730fc2957bcb12119cb204"
    ), "registered data should be used"

    with brownie.reverts():
        log(ebb.getJobInfo(provider, job_key, 1, 2))
        log(ebb.getJobInfo(provider, job_key, 0, 3))

    # setJobState for the workflow:
    index = 0
    job_id = 0
    start_timestamp = 10
    tx = ebb.setJobStateRunning(job_key, index, job_id, start_timestamp, {"from": accounts[0]})
    gas_costs["setJobStateRunning"].append(tx.__dict__["gas_used"])
    index = 0
    job_id = 1
    start_timestamp = 20
    tx = ebb.setJobStateRunning(job_key, index, job_id, start_timestamp, {"from": accounts[0]})
    gas_costs["setJobStateRunning"].append(tx.__dict__["gas_used"])
    # process_payment for the workflow
    index = 0
    job_id = 0
    elapsed_time = 10
    data_transfer = [100, 0]
    ended_timestamp = 20
    result_ipfs_hash = ipfs_to_bytes32("QmWmyoMoctfbAaiEs2G46gpeUmhqFRDW6KWo64y5r581Ve")
    received_sums = []
    refunded_sums = []
    received_sum = 0
    refunded_sum = 0
    args = [
        index,
        job_id,
        ended_timestamp,
        data_transfer[0],
        data_transfer[1],
        elapsed_time,
        job.cores,
        job.run_time,
        False,
    ]
    tx = ebb.processPayment(job_key, args, result_ipfs_hash, {"from": accounts[0]})
    gas_costs["processPayment"].append(tx.__dict__["gas_used"])
    # log(tx.events['LogProcessPayment'])
    received_sums.append(tx.events["LogProcessPayment"]["receivedGwei"])
    refunded_sums.append(tx.events["LogProcessPayment"]["refundedGwei"])
    received_sum += tx.events["LogProcessPayment"]["receivedGwei"]
    refunded_sum += tx.events["LogProcessPayment"]["refundedGwei"]
    log(f"received_sum={received_sum} | refunded_sum={refunded_sum} | job_price={job_price}", "bold")
    index = 0
    job_id = 1
    elapsed_time = 15
    data_transfer = [0, 0]
    ended_timestamp = 39
    result_ipfs_hash = ipfs_to_bytes32("QmWmyoMoctfbAaiEs2G46gpeUmhqFRDW6KWo64y5r581Ve")
    args = [
        index,
        job_id,
        ended_timestamp,
        data_transfer[0],
        data_transfer[1],
        elapsed_time,
        job.cores,
        job.run_time,
        False,
    ]
    tx = ebb.processPayment(job_key, args, result_ipfs_hash, {"from": accounts[0]})
    assert tx.events["LogProcessPayment"]["elapsedTime"] == elapsed_time
    gas_costs["processPayment"].append(tx.__dict__["gas_used"])
    received_sums.append(tx.events["LogProcessPayment"]["receivedGwei"])
    refunded_sums.append(tx.events["LogProcessPayment"]["refundedGwei"])
    received_sum += tx.events["LogProcessPayment"]["receivedGwei"]
    refunded_sum += tx.events["LogProcessPayment"]["refundedGwei"]
    log(f"received_sum={received_sum} | refunded_sum={refunded_sum} | job_price={job_price}", "bold")
    index = 0
    job_id = 2
    elapsed_time = 20
    data_transfer = [0, 100]
    ended_timestamp = 39
    result_ipfs_hash = ipfs_to_bytes32("QmWmyoMoctfbAaiEs2G46gpeUmhqFRDW6KWo64y5r581Ve")
    with brownie.reverts():  # processPayment should revert, setRunning is not called for the job=2
        args = [
            index,
            job_id,
            ended_timestamp,
            data_transfer[0],
            data_transfer[1],
            elapsed_time,
            job.cores,
            job.run_time,
            False,
        ]
        tx = ebb.processPayment(job_key, args, result_ipfs_hash, {"from": accounts[0]})
        gas_costs["processPayment"].append(tx.__dict__["gas_used"])

    index = 0
    job_id = 2
    start_timestamp = 20
    tx = ebb.setJobStateRunning(job_key, index, job_id, start_timestamp, {"from": accounts[0]})
    gas_costs["setJobStateRunning"].append(tx.__dict__["gas_used"])
    args = [
        index,
        job_id,
        ended_timestamp,
        data_transfer[0],
        data_transfer[1],
        elapsed_time,
        job.cores,
        job.run_time,
        True,
    ]
    tx = ebb.processPayment(job_key, args, result_ipfs_hash, {"from": accounts[0]})
    assert tx.events["LogProcessPayment"]["elapsedTime"] == elapsed_time
    gas_costs["processPayment"].append(tx.__dict__["gas_used"])
    # log(tx.events['LogProcessPayment'])
    received_sums.append(tx.events["LogProcessPayment"]["receivedGwei"])
    refunded_sums.append(tx.events["LogProcessPayment"]["refundedGwei"])
    received_sum += tx.events["LogProcessPayment"]["receivedGwei"]
    refunded_sum += tx.events["LogProcessPayment"]["refundedGwei"]
    log(f"received_sum={received_sum} | refunded_sum={refunded_sum} | job_price={job_price}", "bold")
    log(f"received_sums={received_sums}", "bold")
    log(f"refunded_sums={refunded_sums}", "bold")
    assert job_price - cost["storage"] == received_sum + refunded_sum
    withdraw(accounts[0], received_sum)
    withdraw(requester, refunded_sum)