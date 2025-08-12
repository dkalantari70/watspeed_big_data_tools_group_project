import os, io, tarfile, glob, boto3
from botocore.exceptions import ClientError, NoCredentialsError, BotoCoreError

def _find_local_adapters(root="models"):
    for path in glob.glob(os.path.join(root, "**"), recursive=True):
        if os.path.isdir(path) and os.path.exists(os.path.join(path, "adapter_config.json")):
            return path
    return None

def get_or_download_adapters(
    bucket: str | None,
    key: str | None,
    local_dir: str = "models/lora_model_unsloth",
    region: str = "us-east-1",
    profile: str | None = None,
):
    # 1) prefer exact local_dir
    if os.path.isdir(local_dir):
        print(f"✅ Using local adapters: {local_dir}")
        return local_dir

    # 2) scan models/ for any adapters
    found = _find_local_adapters("models")
    if found:
        print(f"✅ Found adapters in: {found}")
        return found

    # 3) try S3 (only if bucket/key provided)
    if not (bucket and key):
        print("ℹ️ No S3 bucket/key set; skipping download.")
        return None
    try:
        s3 = boto3.Session(profile_name=profile, region_name=region).client("s3")
        print(f"Downloading s3://{bucket}/{key} …")
        body = s3.get_object(Bucket=bucket, Key=key)["Body"].read()
        os.makedirs("models", exist_ok=True)
        with tarfile.open(fileobj=io.BytesIO(body), mode="r:gz") as tar:
            tar.extractall("models")
        # re-scan after extract
        return _find_local_adapters("models")
    except (NoCredentialsError, BotoCoreError, ClientError) as e:
        print("⚠️ S3 unavailable:", e)
        return None
