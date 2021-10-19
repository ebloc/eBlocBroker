#!/usr/bin/env python3

import broker.cfg as cfg
from broker._utils.tools import QuietExit, log, print_tb
from broker.config import env
from broker.lib import get_tx_status


def update_provider_info(self, gpg_fingerprint, email, federation_cloud_id, ipfs_id):
    """Update provider info."""
    if len(federation_cloud_id) >= 128:
        log("E: federation_cloud_id could be lesser than 128")
        raise

    if len(email) >= 128:
        log("E: e-mail should be less than 128")
        raise

    if gpg_fingerprint[:2] == "0x":
        log(f"E: gpg_fingerprint={gpg_fingerprint} should not start with 0x")
        raise QuietExit

    if len(gpg_fingerprint) != 40:
        log(f"E: gpg_fingerprint={gpg_fingerprint} length should be 40")
        raise QuietExit

    try:
        provider_info = self.get_provider_info(env.PROVIDER_ID)
        if (
            # TODO: control does gpg_finderprint starts with 0x
            provider_info["gpg_fingerprint"] == gpg_fingerprint.lower()
            and provider_info["email"] == email
            and provider_info["f_id"] == federation_cloud_id
            and provider_info["ipfs_id"] == ipfs_id
        ):
            log(provider_info)
            raise QuietExit("Warning: Given information is same with the cluster's saved info. Nothing to do.")

        tx = self._update_provider_info(f"0x{gpg_fingerprint}", email, federation_cloud_id, ipfs_id)
        return self.tx_id(tx)
    except Exception as e:
        raise e


if __name__ == "__main__":
    Ebb = cfg.Ebb
    email = "alper.alimoglu.research@gmail.com"
    # email = "alper.alimoglu@gmail.com"
    gpg_fingerprint = "2AF4FEB13EA98C83D94150B675D5530929E05CEB"
    federation_cloud_id = "5f0db7e4-3078-4988-8fa5-f066984a8a97@b2drop.eudat.eu"
    ipfs_id = "/ip4/85.96.79.178/tcp/4001/p2p/12D3KooW9s3zzzafmoZ79dRLX3TBFGYHiADPDtxoo4SeiN8B1qGs"  # TODO: delete
    try:
        tx_hash = Ebb.update_provider_info(gpg_fingerprint, email, federation_cloud_id, ipfs_id)
        receipt = get_tx_status(tx_hash)
    except Exception as e:
        print_tb(e)
