# Mobile — iOS & Android Quick Start

## WireGuard
- Install **WireGuard** from App Store/Play Store.
- Tap **Add** → **Create from QR code** or **Import from file**.
- Confirm Allowed IPs (full-tunnel: `0.0.0.0/0, ::/0` or split-tunnel per subnets).

## OpenVPN
- Install **OpenVPN Connect** (iOS/Android).
- Tap **OVPN Profile** → import `.ovpn` via Files/Dropbox/URL.
- Approve VPN configuration permission when prompted.

## Tips
- Enable **On-Demand/Auto-connect** for trusted Wi‑Fi/cellular.
- For battery/roaming, prefer UDP; switch to TCP only if middleboxes block UDP.
