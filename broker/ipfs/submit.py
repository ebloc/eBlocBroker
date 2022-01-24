#!/usr/bin/env python3

import os
import sys
from pathlib import Path
from web3.logs import DISCARD

from broker import cfg
from broker._utils.tools import _remove, log
from broker._utils.web3_tools import get_tx_status
from broker.config import env
from broker.eblocbroker_scripts.job import Job
from broker.errors import QuietExit
from broker.lib import run
from broker.link import check_link_folders
from broker.utils import (
    StorageID,
    generate_md5sum,
    ipfs_to_bytes32,
    is_bin_installed,
    is_dpkg_installed,
    print_tb,
    run_ipfs_daemon,
)

# TODO: folders_to_share let user directly provide the IPFS hash instead of the folder


def pre_check(job, requester):
    """Pre check jobs to submit."""
    try:
        job.check_account_status(requester)
        is_bin_installed("ipfs")
        if not is_dpkg_installed("pigz"):
            log("E: Install [green]pigz[/green].\nsudo apt install -y pigz")
            sys.exit()

        if not os.path.isfile(env.GPG_PASS_FILE):
            log(f"E: Please store your gpg password in the [magenta]{env.GPG_PASS_FILE}[/magenta]\nfile for decrypting")
            raise QuietExit

        run_ipfs_daemon()
        if job.storage_ids[0] == StorageID.IPFS:
            for storage_id in job.storage_ids[1:]:
                if storage_id in (StorageID.GDRIVE, StorageID.EUDAT):
                    raise Exception(
                        "If source code is submitted via IPFS, data files should be submitted via IPFS or IPFS_GPG"
                    )

    except Exception as e:
        print_tb(e)
        sys.exit()


def submit_ipfs(job: Job, is_pass=False, required_confs=1):
    Ebb = cfg.Ebb
    requester = Ebb.w3.toChecksumAddress(job.requester_addr)
    provider = Ebb.w3.toChecksumAddress(job.provider_addr)
    pre_check(job, requester)
    log("==> Attemptting to submit a job")
    main_storage_id = job.storage_ids[0]
    job.folders_to_share = job.paths
    check_link_folders(job.data_paths, job.registered_data_files, is_pass=is_pass)
    if main_storage_id == StorageID.IPFS:
        log("==> Submitting source code through [blue]IPFS[/blue]")
    elif main_storage_id == StorageID.IPFS_GPG:
        log("==> Submitting source code through [blue]IPFS_GPG[/blue]")
    else:
        log("E: Please provide IPFS or IPFS_GPG storage type for the source code")
        sys.exit(1)

    targets = []
    try:
        provider_info = Ebb.get_provider_info(provider)
    except Exception as e:
        print_tb(e)
        sys.exit(1)

    for idx, folder in enumerate(job.folders_to_share):
        if isinstance(folder, Path):
            target = folder
            if job.storage_ids[idx] == StorageID.IPFS_GPG:
                provider_gpg_finderprint = provider_info["gpg_fingerprint"]
                if not provider_gpg_finderprint:
                    log("E: Provider did not register any GPG fingerprint")
                    sys.exit(1)

                log(f"==> provider_gpg_finderprint={provider_gpg_finderprint}")
                try:
                    # target is updated
                    target = cfg.ipfs.gpg_encrypt(provider_gpg_finderprint, target)
                    log(f"==> gpg_file={target}")
                except Exception as e:
                    print_tb(e)
                    sys.exit(1)

            try:
                ipfs_hash = cfg.ipfs.add(target)
                # ipfs_hash = ipfs.add(folder, True)  # True includes .git/
                run(["ipfs", "refs", ipfs_hash])
            except Exception as e:
                print_tb(e)
                sys.exit(1)

            if idx == 0:
                key = ipfs_hash

            job.source_code_hashes.append(ipfs_to_bytes32(ipfs_hash))
            job.source_code_hashes_str.append(ipfs_hash)
            log(f"==> ipfs_hash={ipfs_hash}")
            log(f"==> md5sum={generate_md5sum(target)}")
            if main_storage_id == StorageID.IPFS_GPG:
                # created gpg file will be removed since its already in ipfs
                targets.append(target)
        else:
            code_hash = folder
            if isinstance(code_hash, bytes):
                job.source_code_hashes.append(code_hash)
                job.source_code_hashes_str.append(code_hash.decode("utf-8"))

            # TODO: if its ipfs
            # if isinstance(code_hash, bytes):
            #     code_hash = code_hash.decode("utf-8")

            # if len(code_hash) == 32:
            #     value = cfg.w3.toBytes(text=code_hash)
            #     job.source_code_hashes.append(value)
            #     job.source_code_hashes_str.append(value.decode("utf-8"))
            # else:
            #     job.source_code_hashes.append(ipfs_to_bytes32(code_hash))
            #     job.source_code_hashes_str.append(code_hash)

        # if idx != len(job.folders_to_share) - 1:
        #     log("-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-", "cyan")

    # requester inputs for testing purpose
    job.price, *_ = job.cost(provider, requester)
    try:
        tx_hash = Ebb.submit_job(provider, key, job, requester=requester, required_confs=required_confs)
        if required_confs >= 1:
            tx_receipt = get_tx_status(tx_hash)
            if tx_receipt["status"] == 1:
                processed_logs = Ebb._eBlocBroker.events.LogJob().processReceipt(tx_receipt, errors=DISCARD)
                try:
                    if processed_logs:
                        log("job_info:", "bold yellow")
                        log(vars(processed_logs[0].args))

                    for target in targets:
                        if ".tar.gz.gpg" in str(target):
                            _remove(target)
                except IndexError:
                    log(f"E: Tx({tx_hash}) is reverted")
        else:
            pass
    except QuietExit:
        pass
    except Exception as e:
        print_tb(e)

    return tx_hash


def main():
    job = Job()
    job.set_config(Path.home() / "ebloc-broker" / "broker" / "ipfs" / "job_simple.yaml")
    submit_ipfs(job)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(1)
    except Exception as e:
        print_tb(e)
