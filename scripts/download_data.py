from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import json

import kagglehub

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"

DATASET = "olistbr/brazilian-ecommerce/versions/2"

RAW_DIR.mkdir(parents=True, exist_ok=True)

download_path = Path(
    kagglehub.dataset_download(
        DATASET,
        output_dir=str(RAW_DIR)
    )
)

csv_files = sorted(download_path.rglob("*.csv"))
if not csv_files:
    raise RuntimeError(f"No CSV files found in {download_path}")

manifest = {
    "dataset": DATASET,
    "source_url": "https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce",
    "downloaded_at_utc": datetime.now(timezone.utc).isoformat(),
    "files": [],
}

for file in csv_files:
    checksum = sha256()
    with file.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            checksum.update(chunk)

    manifest["files"].append({
        "filename": str(file.relative_to(download_path)),
        "size_bytes": file.stat().st_size,
        "sha256": checksum.hexdigest(),
    })
    print(f"Downloaded: {file.name}")

manifest_path = download_path / "download_manifest.json"
manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

print(f"\nData directory: {download_path}")
print(f"CSV files: {len(csv_files)}")
print(f"Manifest: {manifest_path}")