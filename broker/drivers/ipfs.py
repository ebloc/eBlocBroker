#!/usr/bin/env python3

import os
import shutil
import time

from broker import cfg
from broker._utils._log import br, ok
from broker._utils.tools import _remove, mkdir, print_tb
from broker.config import ThreadFilter, env, setup_logger  # noqa: F401
from broker.drivers.storage_class import Storage
from broker.lib import calculate_size
from broker.libs import _git
from broker.utils import CacheType, StorageID, byte_to_mb, bytes32_to_ipfs, get_date, is_ipfs_on, log, start_ipfs_daemon


class IpfsClass(Storage):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        #: if storage class is IPFS, then `cache_type` is always public
        self.cache_type = CacheType.PUBLIC
        self.ipfs_hashes = []
        self.cumulative_sizes = {}
        self.requester_info = self.Ebb.get_requester_info(self.job_infos[0]["job_owner"])

    def check(self, ipfs_hash) -> None:
        """Check whether ipfs-hash is online."""
        try:
            ipfs_stat, cumulative_size = cfg.ipfs.is_hash_exists_online(
                ipfs_hash, self.requester_info["ipfs_address"], is_verbose=True
            )
            if "CumulativeSize" not in ipfs_stat:
                raise Exception("Markle not found! Timeout for the IPFS object stat retrieve")
        except Exception as e:
            print_tb(e)
            raise e

        self.ipfs_hashes.append(ipfs_hash)
        self.cumulative_sizes[self.job_key] = cumulative_size
        data_size_mb = byte_to_mb(cumulative_size)
        log(f" * data_transfer_out={data_size_mb} MB | rounded={int(data_size_mb)} MB")

    def ipfs_get(self, ipfs_hash, target, is_storage_paid) -> None:
        """Wrap ipfs get call."""
        cfg.ipfs.get(ipfs_hash, target, is_storage_paid)
        self.verified_data[ipfs_hash] = True

    def print_data_transfer_in(self) -> None:
        dt_in = self.data_transfer_in_to_download_mb
        log(f" * data_transfer_in={dt_in} MB | rounded={int(dt_in)} MB")

    def run(self) -> bool:
        self.start_timestamp = time.time()
        if cfg.IS_THREADING_ENABLED:
            self.thread_log_setup()

        start_ipfs_daemon()
        log(f"{br(get_date())} job's source code has been sent through ", "bold cyan", end="")
        if self.cloudStorageID[0] == StorageID.IPFS:
            log("[bg]IPFS")
        else:
            log("[bg]IPFS_GPG")

        if not is_ipfs_on():
            return False

        log(f"==> is_hash_locally_cached={cfg.ipfs.is_hash_locally_cached(self.job_key)}")
        if not os.path.isdir(self.results_folder):
            os.makedirs(self.results_folder)

        _remove(f"{self.results_folder}/{self.job_key}")
        try:
            self.check(self.job_key)
        except:
            return False

        self.registered_data_hashes = []
        for idx, source_code_hash in enumerate(self.code_hashes):
            if self.cloudStorageID[idx] == StorageID.NONE:
                self.registered_data_hashes.append(source_code_hash)
            else:
                ipfs_hash = bytes32_to_ipfs(source_code_hash)
                if ipfs_hash not in self.ipfs_hashes:
                    try:  # job_key as data hash already may added to the list
                        self.check(ipfs_hash)
                    except:
                        return False

        initial_folder_size = calculate_size(self.results_folder)
        for idx, ipfs_hash in enumerate(self.ipfs_hashes):
            # here scripts knows that provided IPFS hashes exists online
            is_hashed = False
            log(f"## attempting to get IPFS file: {ipfs_hash} ... ", end="")
            if cfg.ipfs.is_hash_locally_cached(ipfs_hash):
                is_hashed = True
                log(ok("already cached"))
            else:
                log()

            if idx == 0:
                target = self.results_folder
            else:
                #  "_" added before the filename in case $ ipfs get <ipfs_hash>
                target = f"{self.results_data_folder}/_{ipfs_hash}"
                mkdir(target)

            is_storage_paid = False  # TODO: should be set before by user input
            self.ipfs_get(ipfs_hash, target, is_storage_paid)
            if idx > 0:
                # https://stackoverflow.com/a/31814223/2402577
                dst_fn = os.path.join(self.results_data_folder, os.path.basename(ipfs_hash))
                if os.path.exists(dst_fn):
                    _remove(dst_fn)

                shutil.move(target, dst_fn)
                target = dst_fn

            if self.cloudStorageID[idx] == StorageID.IPFS_GPG:
                cfg.ipfs.decrypt_using_gpg(f"{target}/{ipfs_hash}", target)

            try:
                _git.initialize_check(target)
            except Exception as e:
                raise e

            if not is_hashed:
                folder_size = calculate_size(self.results_folder)
                self.data_transfer_in_to_download_mb += folder_size - initial_folder_size
                initial_folder_size = folder_size

            if idx == 0 and not self.check_run_sh():
                self.full_refund()
                return False

        self.print_data_transfer_in()
        return self.sbatch_call()
