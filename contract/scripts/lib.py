#!/usr/bin/env python3

from os import path, sys
from pdb import set_trace as bp  # noqa: F401

from lib import CacheType, StorageID

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))


class DataStorage:
    def __init__(self, eB, w3, provider, source_code_hash, brownie=False) -> None:
        if brownie:
            output = eB.getJobStorageTime(provider, source_code_hash)
        else:
            if not w3.isChecksumAddress(provider):
                provider = w3.toChecksumAddress(provider)

            output = eB.functions.getJobStorageTime(provider, source_code_hash).call({"from": provider})

        self.received_block = output[0]
        self.storage_duration = output[1]
        self.is_private = output[2]
        self.is_verified_used = output[3]


class Job:
    def __init__(
        self,
        provider,
        requester,
        cores,
        core_execution_durations,
        source_code_hashes,
        storage_hours,
        storage_ids,
        cache_types,
        dataTransferIn,
        dataTransferOut,
        data_prices_set_block_numbers,
    ) -> None:
        assert len(cores) == len(core_execution_durations)
        assert len(source_code_hashes) == len(storage_hours)
        assert len(storage_hours) == len(storage_ids)
        assert len(cache_types) == len(storage_ids)

        for idx, storage_id in enumerate(storage_ids):
            assert storage_id <= 4
            if storage_id == StorageID.IPFS:
                assert cache_types[idx] == CacheType.PUBLIC.value

        self.provider = provider
        self.requester = requester
        self.cores = cores
        self.core_execution_durations = core_execution_durations
        self.source_code_hashes = source_code_hashes
        self.storage_hours = storage_hours
        self.storage_ids = storage_ids
        self.cache_types = cache_types
        self.dataTransferIn = dataTransferIn
        self.dataTransferOut = dataTransferOut
        self.data_prices_set_block_numbers = data_prices_set_block_numbers


class JobPrices:
    def __init__(self, eB, w3, job, msg_sender, is_brownie=False):
        self.eB = eB
        self.w3 = w3
        self.msg_sender = msg_sender
        self.is_brownie = is_brownie
        self.computational_cost = 0
        self.job_price_value = 0
        self.cache_cost = 0
        self.storage_cost = 0
        self.dataTransferIn_sum = 0
        self.job_price = 0
        self.cost = {}

        if is_brownie:
            provider_info = eB.getProviderInfo(job.provider, 0)
        else:
            provider_info = eB.functions.getProviderInfo(job.provider, 0).call()

        provider_price_info = provider_info[1]
        self.job = job
        self.price_core_min = provider_price_info[2]
        self.price_data_transfer = provider_price_info[3]
        self.price_storage = provider_price_info[4]
        self.price_cache = provider_price_info[5]

    def set_computational_cost(self):
        self.computational_cost = 0
        for idx, core in enumerate(self.job.cores):
            self.computational_cost += int(self.price_core_min * core * self.job.core_execution_durations[idx])

    def set_storage_cost(self):
        """ Calculating the cache cost """
        self.storage_cost = 0
        self.cache_cost = 0
        dataTransferIn_sum = 0
        block_number = self.w3.eth.blockNumber

        for idx, source_code_hash in enumerate(self.job.source_code_hashes):
            ds = DataStorage(self.eB, self.w3, self.job.provider, source_code_hash, self.is_brownie)

            if self.is_brownie:
                received_storage_deposit = self.eB.getReceivedStorageDeposit(
                    self.job.provider, self.job.requester, source_code_hash
                )
            else:
                received_storage_deposit = self.eB.functions.getReceivedStorageDeposit(
                    self.job.provider, self.job.requester, source_code_hash
                ).call({"from": self.msg_sender})

            if ds.received_block + ds.storage_duration < self.w3.eth.blockNumber:
                # Storage time is completed
                received_storage_deposit = 0

            print(f"is_private:{ds.is_private}")
            # print(received_block + storage_duration >= block_number)
            # if received_storage_deposit > 0 or
            if (
                received_storage_deposit > 0 and ds.received_block + ds.storage_duration >= self.w3.eth.blockNumber
            ) or (
                ds.received_block + ds.storage_duration >= block_number and not ds.is_private and ds.is_verified_used
            ):
                print(f"For {source_code_hash} no storage_cost is paid")
            else:
                if self.job.data_prices_set_block_numbers[idx] > 0:
                    # If true, registered data's price should be considered for storage
                    output = self.eB.getRegisteredDataPrice(
                        self.job.provider, source_code_hash, self.job.data_prices_set_block_numbers[idx],
                    )
                    data_price = output[0]
                    self.storage_cost += data_price
                    break

                #  if not received_storage_deposit and (received_block + storage_duration < w3.eth.blockNumber):
                if not received_storage_deposit:
                    dataTransferIn_sum += self.job.dataTransferIn[idx]

                    if self.job.storage_hours[idx] > 0:
                        self.storage_cost += (
                            self.price_storage * self.job.dataTransferIn[idx] * self.job.storage_hours[idx]
                        )
                    else:
                        self.cache_cost += self.price_cache * self.job.dataTransferIn[idx]

        self.dataTransfer_cost = self.price_data_transfer * (dataTransferIn_sum + self.job.dataTransferOut)

    def set_job_price(self):
        self.job_price = self.computational_cost + self.dataTransfer_cost + self.cache_cost + self.storage_cost
        print(
            f"\njob_price_value={self.job_price_value} <=> "
            f"cache_cost={self.cache_cost} | storage_cost={self.storage_cost} | dataTransfer_cost={self.dataTransfer_cost} | computational_cost={self.computational_cost}"
        )
        self.cost["computational_cost"] = self.computational_cost
        self.cost["dataTransfer_cost"] = self.dataTransfer_cost
        self.cost["cache_cost"] = self.cache_cost
        self.cost["storage_cost"] = self.storage_cost


def cost(
    cores,
    core_execution_durations,
    provider,
    requester,
    source_code_hashes,
    dataTransferIn,
    dataTransferOut,
    storage_hours,
    storage_ids,
    cache_types,
    data_prices_set_block_numbers,
    eB,
    w3,
    is_brownie=True,
):
    print("\nEntered into cost calculation...")
    job = Job(
        provider,
        requester,
        cores,
        core_execution_durations,
        source_code_hashes,
        storage_hours,
        storage_ids,
        cache_types,
        dataTransferIn,
        dataTransferOut,
        data_prices_set_block_numbers,
    )
    jp = JobPrices(eB, w3, job, provider, is_brownie)

    jp.set_computational_cost()
    jp.set_storage_cost()
    jp.set_job_price()

    return jp.job_price, jp.cost
