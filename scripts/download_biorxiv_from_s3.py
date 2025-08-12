# scripts/download_biorxiv_from_s3.py
import os, gzip, json, boto3, pathlib

BUCKET = "watspeed-data-gr-project"
KEY    = "biorxiv_2024-08-07.json"   # or .jsonl / .gz variants
OUTDIR = pathlib.Path("data"); OUTDIR.mkdir(exist_ok=True)
OUT    = OUTDIR / KEY.replace(".gz","")

s3 = boto3.client("s3", region_name=os.getenv("AWS_REGION","us-east-1"))
obj = s3.get_object(Bucket=BUCKET, Key=KEY)
body = obj["Body"].read()
if KEY.endswith(".gz"):
    body = gzip.decompress(body)

# just save the raw file to data/
OUT.write_bytes(body)
print(f"Saved -> {OUT.resolve()}")
# (optional quick check)
try:
    _ = json.loads(body.decode("utf-8", "ignore"))
    print("Looks like valid JSON/JSONL ✅")
except Exception as e:
    print("Saved, but JSON parse check failed (maybe JSONL). That's okay.", e)
