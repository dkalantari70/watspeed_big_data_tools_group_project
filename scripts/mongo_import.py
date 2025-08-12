import json, argparse
from pymongo import MongoClient

def load_file(path):
    if path.endswith(".jsonl"):
        with open(path, "r", encoding="utf-8") as f:
            return [json.loads(line) for line in f if line.strip()]
    data = json.load(open(path, "r", encoding="utf-8"))
    return data if isinstance(data, list) else [data]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--uri", default="mongodb://localhost:27018/")
    ap.add_argument("--db", default="semantic_nlp")
    ap.add_argument("--coll", default="biorxiv_articles")
    ap.add_argument("--file", required=True)
    args = ap.parse_args()

    docs = load_file(args.file)
    client = MongoClient(args.uri, uuidRepresentation="standard")
    coll = client[args.db][args.coll]
    if docs:
        coll.insert_many(docs)
        print(f"Inserted {len(docs)} docs into {args.db}.{args.coll}")

if __name__ == "__main__":
    main()
