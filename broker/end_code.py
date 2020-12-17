#!/usr/bin/env python3

import base64
import getpass
import os
import pprint
import sys
import time
from contextlib import suppress
from pathlib import Path
from time import sleep
from typing import Dict, List

from broker import cfg
from broker._utils._log import br, log
from broker._utils.tools import mkdir
from broker.config import env, logging, setup_logger
from broker.errors import QuietExit
from broker.imports import connect
from broker.lib import (
    calculate_folder_size,
    eblocbroker_function_call,
    get_tx_status,
    is_dir,
    remove_files,
    run,
    run_stdout_to_file,
    state,
    subprocess_call,
)
from broker.libs import _git, eudat, gdrive, slurm
from broker.utils import (
    WHERE,
    StorageID,
    _remove,
    byte_to_mb,
    bytes32_to_ipfs,
    eth_address_to_md5,
    is_dir_empty,
    print_tb,
    read_file,
    read_json,
    remove_empty_files_and_folders,
)

connect()
Ebb = cfg.Ebb


class Common:
    """Prevent "Class" has no attribute "method" mypy warnings."""

    def __init__(self) -> None:
        self.results_folder: Path = Path("")
        self.results_folder_prev: Path = Path("")
        self.patch_file: Path = Path("")
        self.requester_gpg_fingerprint = ""
        self.patch_upload_name = ""
        self.data_transfer_out = 0.0

    def initialize(self):
        pass


class IpfsGPG(Common):
    def upload(self, *_) -> bool:
        """Upload files right after all the patchings are completed."""
        try:
            cfg.ipfs.gpg_encrypt(self.requester_gpg_fingerprint, self.patch_file)
        except Exception as e:
            print_tb(e)
            _remove(self.patch_file)
            sys.exit(1)
        return True


class Ipfs(Common):
    def upload(self, *_) -> bool:
        """Upload files after all the patchings are completed."""
        return True


class Eudat(Common):
    def __init__(self) -> None:
        self.encoded_share_tokens = {}  # type: Dict[str, str]
        self.patch_folder: Path = Path("")

    def initialize(self):
        with suppress(Exception):
            eudat.login(env.OC_USER, env.LOG_PATH.joinpath(".eudat_provider.txt"), env.OC_CLIENT)

        try:
            self.get_shared_tokens()
        except:
            sys.exit(1)

    def upload(self, source_code_hash, *_) -> bool:
        with suppress(Exception):
            # first time uploading
            uploaded_file_size = eudat.get_size(f_name=f"{source_code_hash}/{self.patch_upload_name}")
            size_in_bytes = calculate_folder_size(self.patch_file, _type="bytes")
            if uploaded_file_size == float(size_in_bytes):
                log(f"==> {self.patch_file} is already uploaded")
                return True

        _data_transfer_out = calculate_folder_size(self.patch_file)
        log(f"==> {br(source_code_hash)}.data_transfer_out={_data_transfer_out}MB")
        self.data_transfer_out += _data_transfer_out
        return eudat.upload_results(
            self.encoded_share_tokens[source_code_hash], self.patch_upload_name, self.patch_folder, max_retries=5
        )


class Gdrive(Common):
    def upload(self, key, is_job_key) -> bool:
        """Upload result into gdrive.

        :param key: key of the shared gdrive file
        :returns: True if upload is successful
        """
        try:
            if not is_job_key:
                meta_data = gdrive.get_data_key_ids(self.results_folder_prev)
                try:
                    key = meta_data[key]
                except:
                    logging.error(f"E: {key} does not have a match in meta_data.json {WHERE(1)}")
                    return False

            cmd = [env.GDRIVE, "info", "--bytes", key, "-c", env.GDRIVE_METADATA]
            gdrive_info = subprocess_call(cmd, 5)
        except Exception as e:
            logging.error(f"{WHERE(1)} E: {key} does not have a match. meta_data={meta_data}. {e}")
            return False

        mime_type = gdrive.get_file_info(gdrive_info, "Mime")
        logging.info(f"mime_type={mime_type}")
        self.data_transfer_out += calculate_folder_size(self.patch_file)
        logging.info(f"data_transfer_out={self.data_transfer_out} MB =>" f" rounded={int(self.data_transfer_out)} MB")
        if "folder" in mime_type:
            cmd = [env.GDRIVE, "upload", "--parent", key, self.patch_file, "-c", env.GDRIVE_METADATA]
        elif "gzip" in mime_type or "/zip" in mime_type:
            cmd = [env.GDRIVE, "update", key, self.patch_file, "-c", env.GDRIVE_METADATA]
        else:
            logging.error("E: Files could not be uploaded")
            return False

        try:
            log(subprocess_call(cmd, 5))
        except Exception as e:
            print_tb(e)
            log("E: gdrive could not upload the file")
            return False

        return True


class ENDCODE(IpfsGPG, Ipfs, Eudat, Gdrive):
    def __init__(self, **kwargs) -> None:
        args = " ".join(["{!r}".format(v) for k, v in kwargs.items()])
        self.job_key = kwargs.pop("job_key")
        self.index = int(kwargs.pop("index"))
        self.received_block_number = kwargs.pop("received_block_number")
        self.folder_name = kwargs.pop("folder_name")
        self.slurm_job_id = kwargs.pop("slurm_job_id")
        self.share_tokens = {}  # type: Dict[str, str]
        self.data_transfer_in = 0
        self.data_transfer_out = 0.0
        self.elapsed_time = 0
        self.source_code_hashes_to_process: List[str] = []
        self.source_code_hashes: List[str] = []
        self.result_ipfs_hash: str = ""
        self.requester_gpg_fingerprint: str = ""
        self.end_time_stamp = ""
        self.modified_date = None
        self.encoded_share_tokens = {}  # type: Dict[str, str]
        #: Set environment variables: https://stackoverflow.com/a/5971326/2402577
        os.environ["IPFS_PATH"] = str(env.HOME.joinpath(".ipfs"))
        log_filename = Path(env.LOG_PATH) / "end_code_output" / f"{self.job_key}_{self.index}.log"
        logging = setup_logger(log_filename)
        self.job_id = 0  # TODO: should be mapped slurm_job_id
        log(f"{env.EBLOCPATH}/broker/end_code.py {args}", "bold blue")
        log(f"==> slurm_job_id={self.slurm_job_id}")
        if self.job_key == self.index:
            logging.error("E: Given key and index are equal to each other")
            sys.exit(1)

        try:
            self.job_info = eblocbroker_function_call(
                lambda: Ebb.get_job_info(
                    env.PROVIDER_ID,
                    self.job_key,
                    self.index,
                    self.job_id,
                    self.received_block_number,
                ),
                max_retries=10,
            )
            self.cloud_storage_ids = self.job_info["cloudStorageID"]
            requester_id = self.job_info["job_owner"]
            requester_id_address = eth_address_to_md5(requester_id)
            self.requester_info = Ebb.get_requester_info(requester_id)
        except Exception as e:
            log(f"E: {e}")
            sys.exit(1)

        self.results_folder_prev: Path = env.PROGRAM_PATH / requester_id_address / f"{self.job_key}_{self.index}"
        self.results_folder = self.results_folder_prev / "JOB_TO_RUN"
        if not is_dir(self.results_folder) and not is_dir(self.results_folder_prev):
            sys.exit(1)

        self.results_data_link = Path(self.results_folder_prev) / "data_link"
        self.results_data_folder = Path(self.results_folder_prev) / "data"
        self.private_dir = Path(env.PROGRAM_PATH) / requester_id_address / "cache"
        self.patch_folder = Path(self.results_folder_prev) / "patch"
        self.patch_folder_ipfs = Path(self.results_folder_prev) / "patch_ipfs"
        self.job_status_running_tx = Ebb.mongo_broker.get_job_status_running_tx(self.job_key, self.index)
        mkdir(self.patch_folder)
        mkdir(self.patch_folder_ipfs)
        remove_empty_files_and_folders(self.results_folder)
        log(f"==> whoami={getpass.getuser()} | id={os.getegid()}")
        log(f"==> home={env.HOME}")
        log(f"==> pwd={os.getcwd()}")
        log(f"==> results_folder={self.results_folder}")
        log(f"==> job_key={self.job_key}")
        log(f"==> index={self.index}")
        log(f"==> cloud_storage_ids={self.cloud_storage_ids}")
        log(f"==> folder_name=[white]{self.folder_name}")
        log(f"==> provider_id={env.PROVIDER_ID}")
        log(f"==> requester_id_address={requester_id_address}")
        log(f"==> received={self.job_info['received']}")
        log(f"==> job_status_running_tx={self.job_status_running_tx}")

    def get_shared_tokens(self):
        with suppress(Exception):
            share_ids = read_json(f"{self.private_dir}/{self.job_key}_shareID.json")

        for source_code_hash in self.source_code_hashes_to_process:
            try:
                share_token = share_ids[source_code_hash]["share_token"]
                self.share_tokens[source_code_hash] = share_token
                self.encoded_share_tokens[source_code_hash] = base64.b64encode(
                    (f"{share_token}:").encode("utf-8")
                ).decode("utf-8")
            except KeyError:
                try:
                    share_token = Ebb.mongo_broker.find_key(Ebb.mongo_broker.mc["eBlocBroker"]["shareID"], self.job_key)
                    self.share_tokens[source_code_hash] = share_token
                    self.encoded_share_tokens[source_code_hash] = base64.b64encode(
                        (f"{share_token}:").encode("utf-8")
                    ).decode("utf-8")
                except Exception as e:
                    logging.error(f"E: share_id cannot detected from key={self.job_key}")
                    raise e

        for key in share_ids:
            value = share_ids[key]
            encoded_value = self.encoded_share_tokens[key]
            log("shared_tokens: ({}) => ({}) encoded:({})".format(key, value["share_token"], encoded_value))

    def get_cloud_storage_class(self, _id):
        """Return cloud storage used for the id of the data."""
        if self.cloud_storage_ids[_id] == StorageID.IPFS:
            return Ipfs
        if self.cloud_storage_ids[_id] == StorageID.IPFS_GPG:
            return IpfsGPG
        if self.cloud_storage_ids[_id] == StorageID.EUDAT:
            return Eudat
        if self.cloud_storage_ids[_id] == StorageID.GDRIVE:
            return Gdrive

        raise Exception(f"Corresponding storage_id_class={self.cloud_storage_ids[_id]} does not exist")

    def set_source_code_hashes_to_process(self):
        for idx, source_code_hash in enumerate(self.source_code_hashes):
            if self.cloud_storage_ids[idx] in [StorageID.IPFS, StorageID.IPFS_GPG]:
                ipfs_hash = bytes32_to_ipfs(source_code_hash)
                self.source_code_hashes_to_process.append(ipfs_hash)
            else:
                self.source_code_hashes_to_process.append(cfg.w3.toText(source_code_hash))

    def _ipfs_add_folder(self, folder_path):
        try:
            self.result_ipfs_hash = cfg.ipfs.add(folder_path)
            logging.info(f"==> result_ipfs_hash={self.result_ipfs_hash}")
            cfg.ipfs.pin(self.result_ipfs_hash)
            data_transfer_out = cfg.ipfs.get_cumulative_size(self.result_ipfs_hash)
        except Exception as e:
            print_tb(e)
            raise e

        data_transfer_out = byte_to_mb(data_transfer_out)
        self.data_transfer_out += data_transfer_out

    def process_payment_tx(self):
        try:
            tx_hash = eblocbroker_function_call(
                lambda: Ebb.process_payment(
                    self.job_key,
                    self.index,
                    self.job_id,
                    self.elapsed_time,
                    self.result_ipfs_hash,
                    self.cloud_storage_ids,
                    self.end_time_stamp,
                    self.data_transfer_in,
                    self.data_transfer_out,
                    self.job_info["core"],
                    self.job_info["run_time"],
                    self.received_block_number,
                ),
                max_retries=10,
            )
        except Exception as e:
            print_tb(e)
            sys.exit(1)

        log(f"==> process_payment {self.job_key} {self.index}")
        return tx_hash

    def clean_before_upload(self):
        remove_files(f"{self.results_folder}/.node-xmlhttprequest*")

    def remove_source_code(self):
        """Client's initial downloaded files are removed."""
        timestamp_file = f"{self.results_folder_prev}/timestamp.txt"
        try:
            cmd = ["find", self.results_folder, "-type", "f", "!", "-newer", timestamp_file]
            files_to_remove = run(cmd)
            if files_to_remove:
                log(f"## Files to be removed: \n{files_to_remove}\n")
        except Exception as e:
            print_tb(e)
            sys.exit()

        run(["find", self.results_folder, "-type", "f", "!", "-newer", timestamp_file, "-delete"])

    def git_diff_patch_and_upload(self, source: Path, name, storage_class, is_job_key):
        if is_job_key:
            log(f"==> base_patch={self.patch_folder}")
            log(f"==> sourcecode_patch={name}")
        else:
            log(f"==> datafile_patch={name}")

        try:
            if storage_class is Ipfs or storage_class is IpfsGPG:
                target_path = self.patch_folder_ipfs
            else:
                target_path = self.patch_folder

            self.patch_upload_name, self.patch_file, is_file_empty = _git.diff_patch(
                source, name, self.index, target_path
            )
            if not is_file_empty:
                if not storage_class.upload(self, name, is_job_key):
                    raise
        except Exception as e:
            raise Exception("E: Problem on the git_diff_patch_and_upload() function") from e

    def upload_driver(self):
        self.clean_before_upload()
        try:
            storage_class = self.get_cloud_storage_class(0)
            self.git_diff_patch_and_upload(self.results_folder, self.job_key, storage_class, is_job_key=True)
        except Exception as e:
            raise e

        for idx, name in enumerate(self.source_code_hashes_to_process[1:], 1):
            # starting from 1st index for data files
            source = self.results_data_folder / name
            try:
                storage_class = self.get_cloud_storage_class(idx)
                self.git_diff_patch_and_upload(source, name, storage_class, is_job_key=False)
            except Exception as e:
                print_tb(e)
                raise e

        if not is_dir_empty(self.patch_folder_ipfs):
            # it will upload files after all the patchings are completed
            # in case any file is created via ipfs
            self._ipfs_add_folder(self.patch_folder_ipfs)

    def sacct_result(self):
        """Return sacct results.

        CPUTime = NCPUS * Elapsed
        To get stats about real CPU usage you need to look at SystemCPU and
        UserCPU, but the docs warns that it only measure CPU time for the
        parent process and not for child processes.
        """
        slurm_log_output_fn = f"{self.results_folder}/slurm_job_info.out"
        cmd = ["sacct", "-X", "--job", self.slurm_job_id, "--format"]
        cmd.append("jobID,jobname,user,account,group,cluster,allocCPUS,REQMEM,TotalCPU,elapsed")
        run_stdout_to_file(cmd, slurm_log_output_fn)
        with open(slurm_log_output_fn, "a") as f:
            f.write("\n\n")

        cmd.pop()
        cmd.append("NNodes,NTasks,ncpus,CPUTime,State,ExitCode,End,CPUTime,MaxRSS")
        run_stdout_to_file(cmd, slurm_log_output_fn, mode="a")
        with open(slurm_log_output_fn, "a") as f:
            f.write("\n")

    def get_job_info(self, is_print=False, is_log_print=True):
        self.job_info = eblocbroker_function_call(
            lambda: Ebb.get_job_info(
                env.PROVIDER_ID,
                self.job_key,
                self.index,
                self.job_id,
                self.received_block_number,
                is_print=is_print,
                is_log_print=is_log_print,
            ),
            max_retries=1,
        )

    def attemp_get_job_info(self):
        is_print = True
        sleep_time = 30
        for attempt in range(20):
            # log(self.job_info)
            if self.job_info["stateCode"] == state.code["RUNNING"]:
                # it will come here eventually, when setJob() is deployed. Wait
                # until does values updated on the blockchain
                log("## job has been started")
                return

            if self.job_info["stateCode"] == state.code["COMPLETED"]:
                # detects an error on the slurm side
                log("warning: job is already completed and its money is received")
                self.get_job_info()
                raise QuietExit

            try:
                self.job_info = Ebb.get_job_info(
                    env.PROVIDER_ID, self.job_key, self.index, self.job_id, self.received_block_number, is_print
                )
                log(attempt)
                is_print = False
            except Exception as e:
                print_tb(e)
                # sys.exit(1)

            # sleep here so this loop is not keeping CPU busy due to
            # start_code tx may deploy late into the blockchain.
            log(
                f"==> {br(attempt)} start_code tx of the job is not obtained yet."
                f" Waiting for {sleep_time} seconds to pass... ",
                end="",
            )
            sleep(sleep_time)  # TODO: exits randomly
            log(br(f"sleep ended for {sleep_time}"))

        log("E: failed all the attempts, abort")
        sys.exit(1)

    def run(self):
        try:
            data = read_json(f"{self.results_folder_prev}/data_transfer_in.json")
            self.data_transfer_in = data["data_transfer_in"]
            log(f"==> data_transfer_in={self.data_transfer_in} MB -> rounded={int(self.data_transfer_in)} MB")
        except:
            log("E: data_transfer_in.json file does not exist")

        try:
            self.modified_date = read_file(f"{self.results_folder_prev}/modified_date.txt")
            log(f"==> modified_date={self.modified_date}")
        except:
            log("E: modified_date.txt file could not be read")

        self.requester_gpg_fingerprint = self.requester_info["gpg_fingerprint"]
        log("\njob_owner's info\n================", "bold green")
        log(f"==> email=[white]{self.requester_info['email']}")
        log(f"==> gpg_fingerprint={self.requester_gpg_fingerprint}")
        log(f"==> ipfs_id={self.requester_info['ipfs_id']}")
        log(f"==> f_id={self.requester_info['f_id']}")
        if self.job_info["stateCode"] == str(state.code["COMPLETED"]):
            self.get_job_info()
            log(":beer: job is already completed and its money is received", "bold green")
            raise QuietExit

        run_time = self.job_info["run_time"]
        log(f"==> requested_run_time={run_time[self.job_id]} minutes")
        try:
            Ebb._wait_for_transaction_receipt(self.job_status_running_tx)
            self.get_job_info(is_log_print=False)  # re-fetch job info
            self.attemp_get_job_info()
        except Exception as e:
            print_tb(e)
            raise e

        log("## Received running job status successfully", "bold green")
        try:
            self.job_info = eblocbroker_function_call(
                lambda: Ebb.get_job_source_code_hashes(
                    env.PROVIDER_ID,
                    self.job_key,
                    self.index,
                    # self.job_id,
                    self.received_block_number,
                ),
                max_retries=10,
            )
        except Exception as e:
            print_tb(e)
            sys.exit(1)

        self.source_code_hashes = self.job_info["code_hashes"]
        self.set_source_code_hashes_to_process()
        self.sacct_result()
        self.end_time_stamp = slurm.get_job_end_time(self.slurm_job_id)
        self.elapsed_time = slurm.get_elapsed_time(self.slurm_job_id)
        if self.elapsed_time > int(run_time[self.job_id]):
            self.elapsed_time = run_time[self.job_id]

        logging.info(f"finalized_elapsed_time={self.elapsed_time}")
        _job_info = pprint.pformat(self.job_info)
        log("## job_info:", "bold green")
        log(_job_info, "bold")
        try:
            self.get_cloud_storage_class(0).initialize(self)
            self.upload_driver()
        except Exception as e:
            print_tb(e)
            sys.exit(1)

        data_transfer_sum = self.data_transfer_in + self.data_transfer_out
        log(f"==> data_transfer_in={self.data_transfer_in} MB -> rounded={int(self.data_transfer_in)} MB")
        log(f"==> data_transfer_out={self.data_transfer_out} MB -> rounded={int(self.data_transfer_out)} MB")
        log(f"==> data_transfer_sum={data_transfer_sum} MB -> rounded={int(data_transfer_sum)} MB")
        tx_hash = self.process_payment_tx()
        time.sleep(1)
        get_tx_status(tx_hash)  # TODO: add timeout 15 mins
        self.get_job_info()
        log("SUCCESS")
        # TODO: garbage collector, removed downloaded code from local since it is not needed anymore


if __name__ == "__main__":
    kwargs = {
        "job_key": sys.argv[1],
        "index": sys.argv[2],
        "received_block_number": sys.argv[3],
        "folder_name": sys.argv[4],
        "slurm_job_id": sys.argv[5],
    }
    try:
        cloud_storage = ENDCODE(**kwargs)
        cloud_storage.run()
    except QuietExit:
        pass
    except Exception as e:
        print_tb(e)


# cmd = ["tar", "-N", self.modified_date, "-jcvf", self.output_file_name] + glob.glob("*")
# output = run(cmd)
# self.output_file_name = f"result-{PROVIDER_ID}-{self.job_key}-{self.index}.tar.gz"
"""Approach to upload as .tar.gz. Currently not used.
                remove_source_code()
                with open(f"{results_folder_prev}/modified_date.txt') as content_file:
                date = content_file.read().strip()
                cmd = ['tar', '-N', date, '-jcvf', self.output_file_name] + glob.glob("*")
                log.write(run(cmd))
                cmd = ['ipfs', 'add', results_folder + '/result.tar.gz']
                self.result_ipfs_hash = run(cmd)
                self.result_ipfs_hash = self.result_ipfs_hash.split(' ')[1]
                _remove(results_folder + '/result.tar.gz')
# ---------------
# cmd = ["tar", "-N", self.modified_date, "-jcvf", patch_file] + glob.glob("*")
# output = run(cmd)
# logging.info(output)

# self.remove_source_code()
# cmd: tar -jcvf result-$providerID-$index.tar.gz *
# cmd = ['tar', '-jcvf', self.output_file_name] + glob.glob("*")
# cmd = ["tar", "-N", self.modified_date, "-czfj", self.output_file_name] + glob.glob("*")
# output = run(cmd)
# logging.info(f"Files to be archived using tar: \n {output}")
"""
