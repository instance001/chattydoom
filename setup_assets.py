"""Download Freedoom from the official GitHub releases and wire config.yaml."""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
import urllib.request
import zipfile
from pathlib import Path

API_URL = "https://api.github.com/repos/freedoom/freedoom/releases/latest"
DEST_WAD = Path("assets/iwad/freedoom2.wad")
CONFIG_PATH = Path("config.yaml")
IWAD_VALUE = "assets/iwad/freedoom2.wad"
USER_AGENT = {"User-Agent": "chattydoom-setup/1.1"}


def ensure_dest_dir():
    DEST_WAD.parent.mkdir(parents=True, exist_ok=True)


def fetch_latest_zip_url() -> tuple[str, str]:
    req = urllib.request.Request(API_URL, headers=USER_AGENT)
    with urllib.request.urlopen(req) as resp:
        if resp.status != 200:
            raise SystemExit(f"Failed to query releases ({resp.status})")
        data = json.load(resp)
    assets = data.get("assets") or []
    zip_assets = [a for a in assets if str(a.get("name", "")).endswith(".zip")]
    if not zip_assets:
        raise SystemExit("Could not find a .zip asset in the latest Freedoom release.")
    # Prefer the main freedoom bundle over freedm or others
    def _score(asset):
        name = str(asset.get("name", "")).lower()
        # Lower score is better
        if name.startswith("freedoom-"):
            return 0
        if "freedoom" in name:
            return 1
        return 5

    zip_asset = sorted(zip_assets, key=_score)[0]
    return zip_asset["browser_download_url"], zip_asset.get("name", "freedoom.zip")


def download_file(url: str, dest: Path):
    req = urllib.request.Request(url, headers=USER_AGENT)
    with urllib.request.urlopen(req) as resp, dest.open("wb") as fh:
        shutil.copyfileobj(resp, fh)


def extract_wad(zip_path: Path, wad_name: str = "freedoom2.wad") -> Path:
    with zipfile.ZipFile(zip_path) as zf:
        member = next((n for n in zf.namelist() if n.lower().endswith(wad_name)), None)
        if not member:
            raise SystemExit(f"{wad_name} not found in archive {zip_path.name}")
        tmpdir = Path(tempfile.mkdtemp())
        zf.extract(member, tmpdir)
        return tmpdir / member


def place_wad(source: Path, dest: Path):
    ensure_dest_dir()
    shutil.copy2(source, dest)


def update_config_iwad(config_path: Path, new_value: str):
    if not config_path.exists():
        config_path.write_text(f"iwad: {new_value}\n", encoding="utf-8")
        return

    lines = config_path.read_text(encoding="utf-8").splitlines()
    updated = []
    replaced = False
    for line in lines:
        if line.lstrip().startswith("iwad:"):
            updated.append(f"iwad: {new_value}    # point to your IWAD (Freedoom recommended)")
            replaced = True
        else:
            updated.append(line)
    if not replaced:
        updated.insert(0, f"iwad: {new_value}")
    config_path.write_text("\n".join(updated) + "\n", encoding="utf-8")


def main():
    ensure_dest_dir()
    if DEST_WAD.exists():
        print("freedoom2.wad already installed; nothing to do.")
        sys.exit(0)

    print("Fetching latest Freedoom release metadata...")
    zip_url, zip_name = fetch_latest_zip_url()
    with tempfile.TemporaryDirectory() as tmpdir:
        zip_path = Path(tmpdir) / zip_name
        print(f"Downloading {zip_name} ...")
        download_file(zip_url, zip_path)
        print("Extracting freedoom2.wad ...")
        wad_path = extract_wad(zip_path)
        print(f"Copying to {DEST_WAD} ...")
        place_wad(wad_path, DEST_WAD)

    print("Updating config.yaml to point to freedoom2.wad ...")
    update_config_iwad(CONFIG_PATH, IWAD_VALUE)
    print("done")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(1)
