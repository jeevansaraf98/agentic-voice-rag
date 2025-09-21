# OpenVPN on macOS — Client Guide

## Choose a client
- **OpenVPN Connect** (official GUI).
- **Tunnelblick** (popular open-source GUI).
- (Advanced) **Viscosity** (commercial).

## Install
- OpenVPN Connect: download the macOS installer, run it.
- Tunnelblick: download `.dmg`, drag to Applications.

## Import a profile
- Obtain `client.ovpn` (or `.conf`) plus any referenced `ca`, `cert`, `key` files.
- Double-click the file (Tunnelblick) or import in OpenVPN Connect.
- Ensure the profile includes:
  ```
  client
  dev tun
  remote your.server.ip 1194 udp
  resolv-retry infinite
  nobind
  persist-key
  persist-tun
  <ca>...</ca>
  <cert>...</cert>
  <key>...</key>
  ```

## Connect
- Launch the client → select the profile → **Connect**.
- Approve macOS network extension permission if prompted.

## Tips
- **DNS**: if name resolution fails, ensure the server pushes DNS: `push "dhcp-option DNS 1.1.1.1"`.
- **Kill-switch**: Tunnelblick offers “Disable IPv6” and “Route all IPv4 traffic” options; consider firewall rules for strict blocking.
- **Logs**: show log in client UI; raise `verb 4` for troubleshooting.
