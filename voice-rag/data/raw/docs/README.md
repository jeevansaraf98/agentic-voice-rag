# VPN Voice RAG Dataset — Extended (All OSes)
This pack adds platform-specific, original how-tos for **WireGuard** and **OpenVPN** across Windows, macOS, Linux, iOS and Android.
Use it to power a Voice RAG Agent that can guide users hands-free.

Folders:
- `docs/` — original guides (free to use internally for RAG).
- `third_party/` — a fetch script to pull official references (keep `attribution.txt` updated).

How to use:
1) Drop `docs/` and `third_party/` into your project's `data/raw/`.
2) (Optional) `bash third_party/fetch_docs.sh` to download official docs for richer context.
3) `python ingest.py` to rebuild your FAISS index.
