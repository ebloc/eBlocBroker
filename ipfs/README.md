# Enable Port Google-Instance:


- `Navigation Menu` => `VPN Network` => `Firewall` => `Create Firewall Rule`


- Name: `default-ipfs`
- Type: `Ingress`
- Targets: `http-server`
- IP ranges: `0.0.0.0/0`
- TCP: `4001`
- Action: `Allow`
- Priority: `1000`
- default
- Off


- Open instance, Edit, network tags => add `default-ipfs`
- `sudo service network-manager restart` or reboot in case

--------------------------------------------------------------------------------

# Upgrade GO

# Private Networks

- Link: https://github.com/ipfs/go-ipfs/blob/master/docs/experimental-features.md#private-networks
- For the main node:

```
go get github.com/Kubuxu/go-ipfs-swarm-key-gen/ipfs-swarm-key-gen
ipfs-swarm-key-gen > ~/.ipfs/swarm.key

export LIBP2P_FORCE_PNET=1 && IPFS_PATH=~/.ipfs ipfs daemon
```

# All nodes:

- Port check: `nc -v <ip> 4001`

```
killall ipfs
ipfs bootstrap rm --all
ipfs bootstrap add /ip4/35.228.249.124/tcp/4001/p2p/12D3KooWKSE8mdZosQrUEDmnMSFHYXhrypaS15qJQ5rkzjBc9NjT

echo "/key/swarm/psk/1.0.0/  # cat ~/.ipfs/swarm.key  # obtained from the main node
/base16/
c0309d791822a351c291fab0517b51345ad72272bf0e5b5738e4070aa8e78adf" > ~/.ipfs/swarm.key
```

# For home and home2 to make the connect to each other

```
ipfs swarm connect /ip4/192.168.1.3/tcp/4001/p2p/12D3KooWSE6pY7t5NxMLiGd4h7oba6XqxJFD2KNZTQFEjWLeHKsd
```
