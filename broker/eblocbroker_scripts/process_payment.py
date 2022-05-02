#!/usr/bin/env python3

import sys
from typing import Any, Union

from broker import cfg
from broker._utils.tools import log, print_tb
from broker.config import env
from broker.lib import state
from broker.utils import StorageID, ipfs_to_bytes32


def process_payment(
    self,
    job_key,
    index,
    job_id,
    elapsed_time,
    result_ipfs_hash,
    cloud_storage_ids,
    end_time,
    data_transfer_in,
    data_transfer_out,
    core,
    run_time,
    received_block_number=0,
):
    """Process payment of the received job."""
    log(
        f"~/ebloc-broker/broker/eblocbroker_scripts/process_payment.py {job_key} {index} {job_id} {elapsed_time}"
        f" {result_ipfs_hash} '{cloud_storage_ids}' {end_time} {data_transfer_in} {data_transfer_out} '{core}'"
        f" '{run_time}'",
        "bold blue",
    )

    for cloud_storage_id in cloud_storage_ids:
        if len(result_ipfs_hash) != 46 and cloud_storage_id in (StorageID.IPFS, StorageID.IPFS_GPG):
            raise Exception("Result ipfs's length does not match with its original length, check your job_key")

    self.get_job_info(env.PROVIDER_ID, job_key, index, job_id, received_block_number, is_print=False)
    if self.job_info["stateCode"] == state.code["COMPLETED"]:
        log(f"warning: job ({job_key},{index},{job_id}) is completed and already get paid")
        sys.exit(1)

    """
    if self.job_info["stateCode"] == str(state.code["COMPLETED"]):
        log("Job is completed and already get paid")
        sys.exit(1)
    """
    try:
        if result_ipfs_hash == b"" or not result_ipfs_hash:
            result_ipfs_hash = ""
        else:
            result_ipfs_hash = ipfs_to_bytes32(result_ipfs_hash)

        final_job = True  # true only for the final job
        args = [
            int(index),
            int(job_id),
            int(end_time),
            int(data_transfer_in),
            int(data_transfer_out),
            core,
            run_time,
            final_job,
        ]
        tx = self._process_payment(job_key, args, int(elapsed_time), result_ipfs_hash)  # tx is not returned
    except Exception as e:
        print_tb(e)
        raise e

    return self.tx_id(tx)


if __name__ == "__main__":
    Ebb = cfg.Ebb
    if len(sys.argv) == 12:
        args = sys.argv[1:]
        my_args = []  # type: Union[Any]
        for arg in args:
            if arg.startswith("[") and arg.endswith("]"):
                arg = arg.replace("[", "").replace("]", "")
                my_args.append(arg.split(","))
            else:
                my_args.append(arg)

        job_key = str(my_args[0])
        index = int(my_args[1])
        job_id = int(my_args[2])
        elapsed_time = int(my_args[3])
        result_ipfs_hash = str(my_args[4])
        cloud_storage_id = my_args[5]
        end_time = int(my_args[6])
        data_transfer_in = float(my_args[7])
        data_transfer_out = float(my_args[8])
        core = my_args[9]
        run_time = my_args[10]
        # convert all strings in a list to int of the following arguments
        cloud_storage_id = list(map(int, cloud_storage_id))
        core = list(map(int, core))
        run_time = list(map(int, run_time))
    else:
        log("E: wrong number of arguments provided")
        sys.exit(1)

    try:
        tx_hash = Ebb.process_payment(
            job_key,
            index,
            job_id,
            elapsed_time,
            result_ipfs_hash,
            cloud_storage_id,
            end_time,
            data_transfer_in,
            data_transfer_out,
            core,
            run_time,
        )
        log(f"tx_hash={tx_hash}")
    except:
        sys.exit(1)
