import hashlib
import os
import sys
import time
from pathlib import Path
from dotenv import load_dotenv
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
import urllib.request
import json

load_dotenv()
"""
Uploads backup files from local directory to Backblaze B2 (S3-compatible).

Required environment variables:
- B2_ENDPOINT_URL (S3-compatible endpoint from your bucket details)
- B2_KEY_ID (Backblaze keyID)
- B2_APPLICATION_KEY (Backblaze applicationKey)
- B2_BUCKET_NAME

Optional environment variables:
- B2_BUCKET_PREFIX (default: chroma-backups/)
- BACKUPS_DIR (default: ./data/backups)
- UPLOAD_MODE (latest | all; default: latest)
- BACKUP_DUP_CHECK_COUNT (default: 5)  # how many most-recent backups to compare

Usage:
  python scripts/upload_backups_b2.py
"""


def get_env(name: str, default: str | None = None, required: bool = False) -> str:
    val = os.getenv(name, default)
    if required and not val:
        print(f"Missing required env: {name}", file=sys.stderr)
        sys.exit(2)
    return val


def s3_client():
    endpoint = get_env("B2_ENDPOINT_URL", required=True)
    key_id = get_env("B2_KEY_ID", required=True)
    secret = get_env("B2_APPLICATION_KEY", required=True)
    
    # Add https:// if scheme is missing
    if not endpoint.startswith(("http://", "https://")):
        endpoint = f"https://{endpoint}"
    
    print(f"Using B2 endpoint: {endpoint}")
    print(f"Using keyID: {key_id[:8]}...")

    cfg = Config(signature_version="s3v4", retries={"max_attempts": 3, "mode": "standard"})
    return boto3.client(
        "s3",
        region_name="auto",
        endpoint_url=endpoint,
        aws_access_key_id=key_id,
        aws_secret_access_key=secret,
        config=cfg,
    )


def list_local_backups(backups_dir: Path) -> list[Path]:
    if not backups_dir.exists():
        return []
    return sorted(backups_dir.glob("chroma-*.sqlite3"), key=lambda p: p.stat().st_mtime, reverse=True)


def sha256sum(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def emit_notice(severity: str, component: str, code: str, message: str) -> None:
    """Send a notice to the brain service."""
    brain_url = get_env("BRAIN_URL", "http://brain:7000")
    notice_url = f"{brain_url}/v1/notices"
    
    payload = {
        "severity": severity,
        "component": component,
        "code": code,
        "message": message,
    }
    
    try:
        req = urllib.request.Request(
            notice_url,
            data=json.dumps(payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            if response.status == 200:
                print(f"Notice emitted: [{component}.{code}] {message[:50]}...")
            else:
                print(f"Failed to emit notice: HTTP {response.status}", file=sys.stderr)
    except Exception as e:
        print(f"Failed to emit notice: {e}", file=sys.stderr)


def check_duplicates(backups: list[Path], check_count: int) -> None:
    """Warn if the most-recent backups are identical (size + hash)."""
    subset = backups[:check_count]
    if len(subset) < 2:
        return

    fingerprints: list[tuple[int, str]] = []
    for p in subset:
        fingerprints.append((p.stat().st_size, sha256sum(p)))

    unique = set(fingerprints)
    if len(unique) == 1:
        msg = (
            f"The last {len(subset)} backups are identical (size + hash). "
            "The database may not be changing or backups may be misconfigured. "
            "Please investigate backup integrity."
        )
        print(f"WARNING: {msg}", file=sys.stderr)
        emit_notice(
            severity="warning",
            component="backup",
            code="duplicate_detected",
            message=f"ACTION REQUIRED: {msg}"
        )


def file_exists_in_b2(client, bucket: str, key: str) -> bool:
    """Check if a file already exists in B2 bucket."""
    try:
        client.head_object(Bucket=bucket, Key=key)
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            return False
        # Re-raise other errors (permissions, etc.)
        raise


def upload_file(client, bucket: str, local_path: Path, key: str) -> None:
    # Check if already uploaded
    if file_exists_in_b2(client, bucket, key):
        print(f"Already exists (skipping): s3://{bucket}/{key}")
        return
    
    try:
        client.upload_file(
            Filename=str(local_path),
            Bucket=bucket,
            Key=key,
            ExtraArgs={"ContentType": "application/octet-stream"},
        )
        print(f"Uploaded: {local_path} -> s3://{bucket}/{key}")
    except ClientError as e:
        print(f"Failed upload {local_path}: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    backups_dir = Path(get_env("BACKUPS_DIR", "./data/backups"))
    bucket = get_env("B2_BUCKET_NAME", required=True)
    prefix = get_env("B2_BUCKET_PREFIX", "chroma-backups/")
    mode = get_env("UPLOAD_MODE", "latest").lower()
    dup_check_count = int(get_env("BACKUP_DUP_CHECK_COUNT", "5"))

    client = s3_client()

    backups = list_local_backups(backups_dir)
    if not backups:
        print(f"No backups found in {backups_dir}")
        return

    check_duplicates(backups, dup_check_count)

    # Mode determines which backups to check (all backups will be uploaded if not already in B2)
    targets = backups[:1] if mode == "latest" else backups
    print(f"Checking {len(targets)} backup(s) for upload...")

    # Ensure prefix has trailing slash semantics
    if prefix and not prefix.endswith("/"):
        prefix = prefix + "/"

    for p in targets:
        ts = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime(p.stat().st_mtime))
        # Preserve original filename; also include date folder for organization
        key = f"{prefix}{ts}/{p.name}"
        upload_file(client, bucket, p, key)


if __name__ == "__main__":
    main()
