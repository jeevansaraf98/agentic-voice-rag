# WireGuard on macOS — Client Guide (App + CLI)

## Install (pick one)
- **App Store**: Install **WireGuard** (official app), then open it.
- **Homebrew**: `brew install --cask wireguard` (GUI) and/or `brew install wireguard-tools` (CLI).

## Add a tunnel (GUI)
- Click **Add Tunnel** → **Create from scratch** (generates keys) or **Import from file/QR**.
- Use a client config like:
  ```ini
  [Interface]
  Address = 10.8.0.2/32
  PrivateKey = <client-private-key>
  DNS = 1.1.1.1

  [Peer]
  PublicKey = <server-public-key>
  Endpoint = your.server.ip:51820
  AllowedIPs = 0.0.0.0/0, ::/0
  PersistentKeepalive = 25
  ```

## CLI (optional)
```bash
umask 077
wg genkey | tee client.key | wg pubkey > client.pub
sudo wg-quick up /path/to/client-wg0.conf
sudo wg-quick down /path/to/client-wg0.conf
```

## Tips
- **On-demand**: enable “Connect on Demand” in the app preferences.
- **DNS leaks**: ensure `DNS =` is set in `[Interface]` or set system DNS while connected.
- **MTU**: try 1280 if fragments/timeouts occur.
