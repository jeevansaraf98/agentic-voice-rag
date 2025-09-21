# WireGuard on Windows — Client Guide (GUI)

## Install
1. Download **WireGuard for Windows** from the official site.
2. Run the installer and launch **WireGuard**.

## Add a tunnel
- Click **Add Tunnel** → **Add empty tunnel** to generate keys, or **Import tunnel(s) from file** to load a `.conf`.
- Typical client config (`client-wg0.conf`):
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

## Connect / Disconnect
- Select the tunnel → **Activate**. Toggle off to disconnect.

## Tips
- **QR import**: if provided by admin, use **Add Tunnel → Add from QR code**.
- **MTU**: if you see timeouts, edit tunnel → set **MTU 1280**.
- **Kill-switch**: use Windows firewall rules or enable per-app “Block if WireGuard down” with 3rd-party tools.
- **Logs**: Right-click the tunnel → **Log** for handshake and packet stats.
