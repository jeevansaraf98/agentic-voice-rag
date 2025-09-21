# Linux Clients — WireGuard and OpenVPN

## WireGuard (CLI)
```bash
sudo apt install wireguard    # or: sudo dnf install wireguard-tools
umask 077 && wg genkey | tee client.key | wg pubkey > client.pub
sudo wg-quick up client-wg0.conf
sudo wg-quick down client-wg0.conf
```

## WireGuard (NetworkManager)
```bash
sudo apt install network-manager-wireguard
nm-connection-editor  # add WireGuard, paste config
```

## OpenVPN (CLI)
```bash
sudo apt install openvpn
sudo openvpn --config client.ovpn
```

## OpenVPN (NetworkManager)
```bash
sudo apt install network-manager-openvpn
nm-connection-editor  # add OpenVPN, import .ovpn
```
