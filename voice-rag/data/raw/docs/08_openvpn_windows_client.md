# OpenVPN on Windows — Client Guide

## Install
- Download **OpenVPN Connect** (Windows) and install.

## Import profile
- Import `client.ovpn` via the UI or double-click the file if registered.
- Confirm it embeds certs/keys or references local files correctly.

## Connect
- Right-click the tray icon → select your profile → **Connect**.
- Approve UAC driver prompts on first run.

## Tips
- **TAP/TUN**: modern profiles use `dev tun` (routed). Avoid TAP unless bridging is required.
- **DNS leaks**: ensure server pushes DNS; consider setting “Block internet if VPN disconnects” in client settings.
- **Logs**: view Connection Log; increase `verb` in the profile if needed.
