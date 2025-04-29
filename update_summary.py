import os
import datetime
from notion_client import Client

# ── 1. Notion クライアント初期化 ─────────────────────────
notion = Client(auth=os.environ["NOTION_TOKEN"])

DB_ID   = os.environ["DATABASE_ID"]      # 振り返りログDB
PAGE_ID = os.environ["SUMMARY_PAGE_ID"]  # サマリー書き込み先ページ

# ── 2. 過去 7 日間のログを取得 ────────────────────────
since = (datetime.date.today() - datetime.timedelta(days=7)).isoformat()

resp = notion.databases.query(
    database_id = DB_ID,
    filter = {
        "property": "Date",
        "date": { "on_or_after": since }
    }
)

rows = resp["results"]

# ── 3. カテゴリ別に件数を集計 ─────────────────────────
tally = {"概念理解": 0, "実装": 0, "応用アイデア": 0}

for r in rows:
    cat = r["properties"]["Category"]["select"]["name"]
    tally[cat] += 1

total = sum(tally.values())
today = datetime.date.today().isoformat()

# ── 4. Markdown テキストを生成 ───────────────────────
md = f"## Week {since} – {today}\n"
for k, v in tally.items():
    pct = (v / total * 100) if total else 0
    md += f"- **{k}**: {v}件 ({pct:.1f}%)\n"

# ── 5. サマリーページを上書き更新 ─────────────────────
notion.pages.update(
    page_id = PAGE_ID,
    children = [{
        "object": "block",
        "type": "paragraph",
        "paragraph": {
            "rich_text": [{
                "text": { "content": md }
            }]
        }
    }]
)

print("✓ Notion サマリー更新完了")
