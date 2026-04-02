#!/usr/bin/env python3
import argparse
import csv
import json
import os
from typing import Dict, List, Optional

from umapi_client import Connection, GroupsQuery, OAuthS2S  # v3 API

def load_json(path: str) -> Dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def build_connection_from_oauth_s2s(config: Dict) -> Connection:
    # v3: OAuthS2S takes client_id + client_secret; org_id is passed to Connection. [1](https://adobe-apiplatform.github.io/umapi-client.py/v3/connecting.html)
    oauth = OAuthS2S(
        client_id=config["client_id"],
        client_secret=config["client_secret"],
    )
    return Connection(org_id=config["org_id"], auth=oauth)

def normalize_groups_record(g: Dict) -> Dict:
    # GroupsQuery yields a dict-like record. Example fields shown in docs include:
    # groupId, groupName, type, memberCount, etc. [2](https://adobe-apiplatform.github.io/umapi-client.py/v3/)
    print(g)
    return {
        "type": g.get("type"),
        "groupId": g.get("groupId"),
        "groupName": g.get("groupName"),
        "memberCount": g.get("memberCount"),
        "adminGroupName": g.get("adminGroupName"),
        "productName": g.get("productName"),
        "licenseQuota": g.get("licenseQuota"),
        "singleApp": g.get("singleApp"),
        "profileGroupName": g.get("profileGroupName"),
        "userGroupName": g.get("userGroupName"),
        "contractName": g.get("contractName"),
    }

def write_json(groups: List[Dict], path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(groups, f, indent=2, ensure_ascii=False)

def write_csv(groups: List[Dict], path: str) -> None:
    fieldnames = [
        "type", "groupId", "groupName", "memberCount",
        "adminGroupName", "productName", "licenseQuota",
        "singleApp", "profileGroupName", "userGroupName", "contractName"
    ]
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for g in groups:
            w.writerow(g)

def main():
    parser = argparse.ArgumentParser(description="Export Adobe Admin Console groups and profiles using umapi-client (v3).")
    parser.add_argument("--config", required=True, help="Path to JSON config with client_id/client_secret/org_id.")
    parser.add_argument("--out", default="adobe_groups", help="Output file prefix (default: adobe_groups).")
    args = parser.parse_args()

    config = load_json(args.config)

    conn = build_connection_from_oauth_s2s(config)

    # GroupsQuery(conn) returns groups in the org. [2](https://adobe-apiplatform.github.io/umapi-client.py/v3/)
    exported = [normalize_groups_record(u) for u in GroupsQuery(conn)]

    json_path = f"{args.out}.json"
    csv_path = f"{args.out}.csv"
    write_json(exported, json_path)
    write_csv(exported, csv_path)

    print(f"Exported {len(exported)} groups.")
    print(f"JSON: {os.path.abspath(json_path)}")
    print(f"CSV : {os.path.abspath(csv_path)}")

if __name__ == "__main__":
    main()
