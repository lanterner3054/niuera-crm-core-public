#!/usr/bin/env python3
import argparse
import json
import os
import sys
import time
import urllib.parse
import urllib.request


PLANNED_CHANGES = [
    {
        "group": "Example A: invalid prospect records",
        "updates": [
            ("PR001", "Example Person A", {"status": "已跳过"}),
            ("PR002", "Example Person B", {"status": "已跳过"}),
        ],
    },
    {
        "group": "Example B: duplicate company records",
        "updates": [
            ("PR003", "Example Company Duplicate", {"status": "已跳过"}),
            ("PR004", "Example Charging Co duplicate", {"status": "已跳过"}),
        ],
    },
    {
        "group": "Example C: missing country enrichment",
        "updates": [
            ("PR005", "Example Energy Ltd", {"country": "Germany"}),
            ("PR006", "Example Mobility GmbH", {"country": "Netherlands"}),
        ],
    },
    {
        "group": "Example D: field correction",
        "updates": [
            ("PR007", "Example Power Systems", {"country": "Italy", "status": "待处理", "priority": "高"}),
        ],
    },
]


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def load_config():
    app_id = require_env("FEISHU_APP_ID")
    app_secret = require_env("FEISHU_APP_SECRET")
    app_token = require_env("FEISHU_OUTREACH_APP_TOKEN")
    table_id = require_env("FEISHU_OUTREACH_PROSPECTS_TABLE_ID")
    base_url = (
        "https://open.feishu.cn/open-apis/bitable/v1/apps/"
        f"{app_token}/tables/{table_id}/records"
    )
    return app_id, app_secret, base_url


def get_token(app_id: str, app_secret: str) -> str:
    data = json.dumps({"app_id": app_id, "app_secret": app_secret}).encode("utf-8")
    req = urllib.request.Request(
        "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
        data=data,
        headers={"Content-Type": "application/json"},
    )
    response = json.loads(urllib.request.urlopen(req, timeout=10).read())
    if response.get("code") != 0:
        raise RuntimeError(f"Failed to get Feishu token: {response}")
    return response["tenant_access_token"]


def find_record_id(token: str, base_url: str, prospect_id: str):
    filter_expr = f'CurrentValue.[prospect_id]="{prospect_id}"'
    url = f"{base_url}?page_size=1&filter={urllib.parse.quote(filter_expr)}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    response = json.loads(urllib.request.urlopen(req, timeout=10).read())
    items = response.get("data", {}).get("items", [])
    return items[0]["record_id"] if items else None


def update_record(token: str, base_url: str, record_id: str, fields: dict, label: str) -> bool:
    data = json.dumps({"fields": fields}, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        f"{base_url}/{record_id}",
        data=data,
        method="PUT",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
    )
    response = json.loads(urllib.request.urlopen(req, timeout=10).read())
    ok = response.get("code") == 0
    print(f"  {'✅' if ok else '❌'} {label}" + ("" if ok else f" — {response.get('msg', '')}"))
    return ok


def print_plan():
    total = 0
    print("Planned changes:")
    for group in PLANNED_CHANGES:
        print(f"\n【{group['group']}】")
        for prospect_id, name, fields in group["updates"]:
            total += 1
            print(f"  - {prospect_id} {name}: {fields}")
    print(f"\nTotal planned updates: {total}")


def execute_plan():
    app_id, app_secret, base_url = load_config()
    token = get_token(app_id, app_secret)
    print("Token OK\n")

    success = 0
    failed = 0

    for group in PLANNED_CHANGES:
        print(f"【{group['group']}】")
        for prospect_id, name, fields in group["updates"]:
            record_id = find_record_id(token, base_url, prospect_id)
            if not record_id:
                print(f"  ⚠️ {prospect_id} {name}: 未找到")
                failed += 1
                time.sleep(0.2)
                continue

            ok = update_record(
                token,
                base_url,
                record_id,
                fields,
                f"{prospect_id} {name} → {fields}",
            )
            success += int(ok)
            failed += int(not ok)
            time.sleep(0.2)
        print()

    print(f"完成！成功: {success}, 失败: {failed}")
    return 0 if failed == 0 else 1


def main():
    parser = argparse.ArgumentParser(
        description="Safely review or execute cleanup updates for Outreach prospects."
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually write updates to Feishu. Without this flag, the script only prints planned changes.",
    )
    args = parser.parse_args()

    print_plan()

    if not args.execute:
        print("\nDRY RUN ONLY. No Feishu data was changed.")
        print("To execute, run: python3 scripts/outreach_cleanup.py --execute")
        return 0

    print("\n⚠️ EXECUTE mode will write to Feishu production data.")
    confirmation = input('Type "EXECUTE" to continue: ').strip()
    if confirmation != "EXECUTE":
        print("Cancelled. No Feishu data was changed.")
        return 1

    return execute_plan()


if __name__ == "__main__":
    sys.exit(main())
