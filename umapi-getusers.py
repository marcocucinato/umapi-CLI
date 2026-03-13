#!/usr/bin/env python3
import argparse
import csv
import json
import os
from typing import Dict, List, Optional

from umapi_client import Connection, UsersQuery, OAuthS2S  # v3 API

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

def normalize_user_record(u: Dict) -> Dict:
    # UsersQuery yields a dict-like record. Example fields shown in docs include:
    # email, username, domain, status, type, firstname, lastname, country, groups, etc. [2](https://adobe-apiplatform.github.io/umapi-client.py/v3/)
    return {
        "id": u.get("id"),
        "email": u.get("email"),
        "username": u.get("username"),
        "domain": u.get("domain"),
        "status": u.get("status"),
        "type": u.get("type"),
        "firstname": u.get("firstname"),
        "lastname": u.get("lastname"),
        "country": u.get("country"),
        "businessAccount": u.get("businessAccount"),
        "orgSpecific": u.get("orgSpecific"),
        "groups": u.get("groups", []),
    }

def write_json(users: List[Dict], path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2, ensure_ascii=False)

def write_csv(users: List[Dict], path: str) -> None:
    fieldnames = [
        "id", "email", "username", "domain", "status", "type",
        "firstname", "lastname", "country", "businessAccount", "orgSpecific", "groups"
    ]
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for u in users:
            row = dict(u)
            row["groups"] = ";".join(u.get("groups") or [])
            w.writerow(row)

def main():
    parser = argparse.ArgumentParser(description="Export Adobe Admin Console users using umapi-client (v3).")
    parser.add_argument("--config", required=True, help="Path to JSON config with client_id/client_secret/org_id.")
    parser.add_argument("--out", default="adobe_users", help="Output file prefix (default: adobe_users).")
    parser.add_argument("--group", default=None, help="Optional: filter users to members of a specific group.")
    parser.add_argument("--domain", default=None, help="Optional: filter users to a specific domain.")
    args = parser.parse_args()

    config = load_json(args.config)

    conn = build_connection_from_oauth_s2s(config)

    # UsersQuery(conn) returns users in the org; supports in_group / in_domain filters. [2](https://adobe-apiplatform.github.io/umapi-client.py/v3/)
    kwargs = {}
    if args.group:
        kwargs["in_group"] = args.group
    if args.domain:
        kwargs["in_domain"] = args.domain

    exported = [normalize_user_record(u) for u in UsersQuery(conn, **kwargs)]

    json_path = f"{args.out}.json"
    csv_path = f"{args.out}.csv"
    write_json(exported, json_path)
    write_csv(exported, csv_path)

    print(f"Exported {len(exported)} users.")
    print(f"JSON: {os.path.abspath(json_path)}")
    print(f"CSV : {os.path.abspath(csv_path)}")

if __name__ == "__main__":
    main()
