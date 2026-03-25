#!/usr/bin/env python3
"""
SustainaLog Collector - main.py
国内企業のCSR・サステナビリティ情報を収集し、Google Sheetsに書き込む

使い方:
  python main.py --init    # シートヘッダー初期化・接続確認
  python main.py --daily   # 日次収集実行
  python main.py --test    # 1社だけテスト収集（動作確認用）

必要な環境変数（GitHub Actions Secrets に設定）:
  ANTHROPIC_API_KEY   : Claude API キー
  SPREADSHEET_ID      : Google SheetsのID
  GAS_WEBHOOK_URL     : GASウェブアプリのURL（書き込み用）
"""

import argparse
import hashlib
import json
import os
import re
import time
import traceback
from datetime import datetime, timezone, timedelta
from typing import Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

# ============================================================
# 設定（環境変数から取得）
# ============================================================

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
SPREADSHEET_ID    = os.environ.get("SPREADSHEET_ID", "")
GAS_WEBHOOK_URL   = os.environ.get("GAS_WEBHOOK_URL", "")

JST = timezone(timedelta(hours=9))

# ============================================================
# 収集対象企業リスト
# ============================================================

TARGET_COMPANIES = [
    {
        "company_name": "トヨタ自動車",
        "ticker": "7203",
        "market": "prime",
        "industry": "自動車",
        "news_url": "https://global.toyota/jp/newsroom/sustainability/",
        "official_url": "https://global.toyota",
        "ir_url": "https://global.toyota/jp/ir/",
        "sustainability_url": "https://global.toyota/jp/sustainability/",
    },
    {
        "company_name": "ソニーグループ",
        "ticker": "6758",
        "market": "prime",
        "industry": "電機・精密",
        "news_url": "https://www.sony.com/ja/articles/sustainability-news/",
        "official_url": "https://www.sony.com/ja/",
        "ir_url": "https://www.sony.com/ja/SonyInfo/IR/",
        "sustainability_url": "https://www.sony.com/ja/SonyInfo/sustainability/",
    },
    {
        "company_name": "キリンホールディングス",
        "ticker": "2503",
        "market": "prime",
        "industry": "食品・飲料",
        "news_url": "https://www.kirinholdings.com/jp/newsroom/",
        "official_url": "https://www.kirinholdings.com/jp/",
        "ir_url": "https://www.kirinholdings.com/jp/investors/",
        "sustainability_url": "https://www.kirinholdings.com/jp/impact/",
    },
    {
        "company_name": "花王",
        "ticker": "4452",
        "market": "prime",
        "industry": "化学・化粧品",
        "news_url": "https://www.kao.com/jp/newsroom/news/",
        "official_url": "https://www.kao.com/jp/",
        "ir_url": "https://www.kao.com/jp/corporate/investors/",
        "sustainability_url": "https://www.kao.com/jp/corporate/sustainability/",
    },
    {
        "company_name": "NTT",
        "ticker": "9432",
        "market": "prime",
        "industry": "通信",
        "news_url": "https://group.ntt/jp/newsrelease/",
        "official_url": "https://group.ntt/jp/",
        "ir_url": "https://group.ntt/jp/ir/",
        "sustainability_url": "https://group.ntt/jp/sustainability/",
    },
    {
        "company_name": "イオン",
        "ticker": "8267",
        "market": "prime",
        "industry": "小売",
        "news_url": "https://www.aeon.info/news/",
        "official_url": "https://www.aeon.info/",
        "ir_url": "https://www.aeon.info/ir/",
        "sustainability_url": "https://www.aeon.info/sustainability/",
    },
    {
        "company_name": "積水ハウス",
        "ticker": "1928",
        "market": "prime",
        "industry": "建設・不動産",
        "news_url": "https://www.sekisuihouse.co.jp/company/news/",
        "official_url": "https://www.sekisuihouse.co.jp/",
        "ir_url": "https://www.sekisuihouse.co.jp/company/ir/",
        "sustainability_url": "https://www.sekisuihouse.co.jp/sustainable/",
    },
    {
        "company_name": "リコー",
        "ticker": "7752",
        "market": "prime",
        "industry": "電機・精密",
        "news_url": "https://jp.ricoh.com/release/",
        "official_url": "https://jp.ricoh.com/",
        "ir_url": "https://jp.ricoh.com/IR/",
        "sustainability_url": "https://jp.ricoh.com/sustainability/",
    },
    {
        "company_name": "パナソニック",
        "ticker": "6752",
        "market": "prime",
        "industry": "電機・精密",
        "news_url": "https://news.panasonic.com/jp/topics",
        "official_url": "https://holdings.panasonic/jp/",
        "ir_url": "https://holdings.panasonic/jp/corporate/ir/",
        "sustainability_url": "https://holdings.panasonic/jp/corporate/sustainability/",
    },
    {
        "company_name": "住友化学",
        "ticker": "4005",
        "market": "prime",
        "industry": "化学",
        "news_url": "https://www.sumitomo-chem.co.jp/news/",
        "official_url": "https://www.sumitomo-chem.co.jp/",
        "ir_url": "https://www.sumitomo-chem.co.jp/ir/",
        "sustainability_url": "https://www.sumitomo-chem.co.jp/sustainability/",
    },
]

# ============================================================
# ユーティリティ
# ============================================================

def now_jst_str() -> str:
    return datetime.now(JST).strftime("%Y-%m-%dT%H:%M:%S+09:00")

def today_jst_str() -> str:
    return datetime.now(JST).strftime("%Y-%m-%d")

def make_article_id(company: str, url: str) -> str:
    raw = f"{company}:{url}"
    return "ART-" + hashlib.md5(raw.encode()).hexdigest()[:10].upper()

def make_slug(company: str, title: str) -> str:
    base = re.sub(r"[^\w\s-]", "", f"{company} {title}", flags=re.UNICODE)
    base = re.sub(r"\s+", "-", base.strip()).lower()
    date = datetime.now(JST).strftime("%Y%m%d")
    return base[:60] + "-" + date

def log(msg: str):
    ts = datetime.now(JST).strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)

# ============================================================
# スクレイピング
# ============================================================

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; SustainaLogBot/1.0; "
        "+https://github.com/kamoshida-ritsuji/SustainaLog)"
    ),
    "Accept-Language": "ja,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

def fetch_html(url: str, timeout: int = 20) -> Optional[str]:
    try:
        resp = requests.get(url, headers=HEADERS, timeout=timeout, allow_redirects=True)
        resp.raise_for_status()
        resp.encoding = resp.apparent_encoding or "utf-8"
        return resp.text
    except Exception as e:
        log(f"  ⚠ fetch error [{url}]: {e}")
        return None

def extract_news_links(html: str, base_url: str) -> list:
    """ニュースページからリンク一覧を抽出（最大5件）"""
    soup = BeautifulSoup(html, "lxml")
    results = []
    seen = set()

    candidate_selectors = [
        "article",
        "li.news-item", "li.release-item", "li.press-item",
        ".news-list li", ".release-list li", ".pressrelease-list li",
        "[class*='news-item']", "[class*='release-item']",
        "div.news", "div.release",
    ]

    for sel in candidate_selectors:
        for el in soup.select(sel):
            a_tag = el.find("a", href=True)
            if not a_tag:
                continue
            href = a_tag["href"].strip()
            if not href or href.startswith("#") or href.startswith("javascript"):
                continue
            full_url = href if href.startswith("http") else urljoin(base_url, href)
            if full_url in seen:
                continue
            seen.add(full_url)

            # タイトル抽出
            title = ""
            for title_sel in ["h1", "h2", "h3", "h4", "p"]:
                title_el = el.find(title_sel)
                if title_el and len(title_el.get_text(strip=True)) > 10:
                    title = title_el.get_text(strip=True)
                    break
            if not title:
                title = a_tag.get_text(strip=True)
            if len(title) < 8:
                continue

            # 日付抽出
            date_str = ""
            date_el = el.find("time")
            if date_el:
                date_str = date_el.get("datetime", "") or date_el.get_text(strip=True)

            results.append({"url": full_url, "title": title[:200], "date": date_str[:30]})
            if len(results) >= 5:
                break
        if len(results) >= 5:
            break

    # フォールバック: キーワード含むリンクを拾う
    if not results:
        keywords = ["サステナ", "csr", "環境", "社会", "esg", "脱炭素",
                    "carbon", "sustain", "social", "environment", "sdg"]
        for a_tag in soup.find_all("a", href=True):
            text = a_tag.get_text(strip=True)
            href = a_tag["href"]
            if any(kw in text.lower() or kw in href.lower() for kw in keywords):
                full_url = href if href.startswith("http") else urljoin(base_url, href)
                if full_url in seen or len(text) < 8:
                    continue
                seen.add(full_url)
                results.append({"url": full_url, "title": text[:200], "date": ""})
                if len(results) >= 3:
                    break

    log(f"  → {len(results)} 件のリンク検出")
    return results

def fetch_article_body(url: str) -> str:
    """記事本文を取得（最大2500文字）"""
    html = fetch_html(url)
    if not html:
        return ""
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["nav", "footer", "header", "script", "style", "aside", "noscript"]):
        tag.decompose()
    main = (
        soup.find("main") or
        soup.find("article") or
        soup.find(id=re.compile(r"content|main|body|article", re.I)) or
        soup.find(class_=re.compile(r"content|main|body|article", re.I)) or
        soup.body
    )
    text = main.get_text(separator="\n", strip=True) if main else ""
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text[:2500]

# ============================================================
# Claude API
# ============================================================

CLAUDE_MODEL   = "claude-sonnet-4-20250514"
CLAUDE_API_URL = "https://api.anthropic.com/v1/messages"

ANALYSIS_SYSTEM = """あなたは日本企業のCSR・サステナビリティ活動を分析する専門アナリストです。
与えられた記事情報を分析し、以下のJSON形式のみで回答してください。
マークダウン記法・コードブロック・説明文は不要です。JSONだけ返してください。

{
  "translated_title": "日本語タイトル（原文が英語なら翻訳、日本語ならそのまま）",
  "summary": "活動内容の要約（150字以内、体言止め）",
  "ai_commentary": "投資家・研究者向けのAI解説（200字以内。社会的意義・業界文脈・今後の展望を含む）",
  "csr_type": "環境・脱炭素 / ダイバーシティ・労働 / 地域社会・教育 / ガバナンス・コンプライアンス / サプライチェーン / 製品・サービス安全 / 健康・医療支援 / デジタル・イノベーション / 人権・児童保護 / その他CSR のいずれか1つ",
  "csr_subtype": "より具体的なサブカテゴリ（例: CO2削減、女性活躍推進など）",
  "relation_type": "direct / indirect / neutral のいずれか",
  "stakeholder_type": "投資家 / 従業員 / 消費者 / 地域社会 / 取引先 / 行政・規制当局 / NGO・NPO / メディア / 全般 のいずれか",
  "classification_tags": ["タグ1", "タグ2", "タグ3"],
  "score_social_clarity": 社会的明確性スコア(0-20の整数),
  "score_continuity": 継続性スコア(0-20の整数),
  "score_business_alignment": 事業連携スコア(0-20の整数),
  "score_specificity": 具体性スコア(0-20の整数),
  "score_reference_value": 参照価値スコア(0-20の整数)
}"""

def call_claude(system: str, user_msg: str, max_tokens: int = 1500) -> Optional[str]:
    if not ANTHROPIC_API_KEY:
        log("  ❌ ANTHROPIC_API_KEY 未設定")
        return None
    try:
        resp = requests.post(
            CLAUDE_API_URL,
            headers={
                "x-api-key": ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": CLAUDE_MODEL,
                "max_tokens": max_tokens,
                "system": system,
                "messages": [{"role": "user", "content": user_msg}],
            },
            timeout=90,
        )
        resp.raise_for_status()
        return resp.json()["content"][0]["text"]
    except Exception as e:
        log(f"  ❌ Claude API error: {e}")
        return None

def analyze_article(company: dict, item: dict, body: str) -> Optional[dict]:
    user_msg = f"""以下の企業CSR記事を分析してください。

企業名: {company['company_name']}
業界: {company['industry']}
記事URL: {item['url']}
記事タイトル: {item['title']}
公開日: {item.get('date', '不明')}

記事本文（抜粋）:
{body if body else '（本文取得不可）'}
"""
    raw = call_claude(ANALYSIS_SYSTEM, user_msg)
    if not raw:
        return None
    raw = raw.strip()
    raw = re.sub(r"^```json\s*", "", raw)
    raw = re.sub(r"^```\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        log(f"  ⚠ JSON parse error: {e} / raw: {raw[:200]}")
        return None

# ============================================================
# 行データ構築
# ============================================================

def build_row(company: dict, item: dict, analysis: dict) -> list:
    """Sheetsの30カラム順に合わせた行データを生成"""
    scores = [
        int(analysis.get("score_social_clarity",    10)),
        int(analysis.get("score_continuity",         10)),
        int(analysis.get("score_business_alignment", 10)),
        int(analysis.get("score_specificity",        10)),
        int(analysis.get("score_reference_value",    10)),
    ]
    total = sum(scores)
    article_id = make_article_id(company["company_name"], item["url"])
    slug = make_slug(company["company_name"],
                     analysis.get("translated_title", item["title"]))
    tags = analysis.get("classification_tags", [])
    tags_str = ",".join(tags) if isinstance(tags, list) else str(tags)

    return [
        article_id,
        slug,
        company["company_name"],
        company.get("ticker", ""),
        company.get("market", "prime"),
        company.get("industry", ""),
        company["company_name"] + " ニュースリリース",
        item["url"],
        company.get("official_url", ""),
        company.get("ir_url", ""),
        company.get("sustainability_url", ""),
        item["title"],
        analysis.get("translated_title", item["title"]),
        analysis.get("summary", ""),
        analysis.get("ai_commentary", ""),
        analysis.get("csr_type", "その他CSR"),
        analysis.get("csr_subtype", ""),
        analysis.get("relation_type", "direct"),
        analysis.get("stakeholder_type", "全般"),
        tags_str,
        scores[0],
        scores[1],
        scores[2],
        scores[3],
        scores[4],
        total,
        item.get("date", today_jst_str()),
        now_jst_str(),
        "pending_review",
        "FALSE",
    ]

# ============================================================
# Google Sheets 書き込み（GAS経由）
# ============================================================

def push_to_sheets(rows: list) -> bool:
    if not GAS_WEBHOOK_URL:
        log("  ⚠ GAS_WEBHOOK_URL 未設定 → ローカルJSON保存へ")
        return False
    try:
        resp = requests.post(
            GAS_WEBHOOK_URL,
            json={"action": "appendRows", "rows": rows},
            timeout=30,
        )
        resp.raise_for_status()
        result = resp.json()
        if result.get("status") == "ok":
            log(f"  ✅ Sheets書き込み成功: {len(rows)}件")
            return True
        log(f"  ❌ Sheets書き込み失敗: {result}")
        return False
    except Exception as e:
        log(f"  ❌ GAS webhook error: {e}")
        return False

# ============================================================
# ローカルJSON保存（フォールバック）
# ============================================================

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

COLUMNS = [
    "article_id","slug","company_name","ticker","market","industry",
    "source_name","source_url","official_url","ir_url","sustainability_url",
    "source_title","translated_title","summary","ai_commentary",
    "csr_type","csr_subtype","relation_type","stakeholder_type",
    "classification_tags","score_social_clarity","score_continuity",
    "score_business_alignment","score_specificity","score_reference_value",
    "total_score","published_at","fetched_at","status","publish_flag",
]

def save_local(rows: list):
    os.makedirs(DATA_DIR, exist_ok=True)
    path = os.path.join(DATA_DIR, f"articles_{today_jst_str()}.json")
    records = [dict(zip(COLUMNS, row)) for row in rows]

    existing = []
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            existing = json.load(f)

    existing_ids = {r["article_id"] for r in existing}
    new_records = [r for r in records if r["article_id"] not in existing_ids]
    all_records = existing + new_records

    with open(path, "w", encoding="utf-8") as f:
        json.dump(all_records, f, ensure_ascii=False, indent=2)

    log(f"  💾 ローカル保存完了: {path} (+{len(new_records)}件 / 合計{len(all_records)}件)")

# ============================================================
# コマンド
# ============================================================

def cmd_init():
    log("=" * 50)
    log("SustainaLog Collector — 初期化チェック")
    log("=" * 50)
    log(f"ANTHROPIC_API_KEY : {'✅ 設定済み' if ANTHROPIC_API_KEY else '❌ 未設定'}")
    log(f"SPREADSHEET_ID    : {'✅ 設定済み' if SPREADSHEET_ID else '❌ 未設定（読み取り不要）'}")
    log(f"GAS_WEBHOOK_URL   : {'✅ 設定済み' if GAS_WEBHOOK_URL else '⚠ 未設定（ローカル保存モード）'}")
    os.makedirs(DATA_DIR, exist_ok=True)
    log(f"data/ ディレクトリ: {DATA_DIR}")

    if GAS_WEBHOOK_URL:
        log("GAS接続テスト中...")
        try:
            resp = requests.post(GAS_WEBHOOK_URL, json={"action": "ping"}, timeout=15)
            resp.raise_for_status()
            log(f"  ✅ GAS接続OK: {resp.text[:100]}")
        except Exception as e:
            log(f"  ❌ GAS接続失敗: {e}")

    log("初期化完了 ✅")

def collect_company(company: dict) -> list:
    log(f"\n📦 {company['company_name']} ({company['ticker']}) 収集開始")
    rows = []

    html = fetch_html(company["news_url"])
    if not html:
        log("  ⚠ ページ取得失敗 — スキップ")
        return rows

    items = extract_news_links(html, company["news_url"])
    if not items:
        log("  ⚠ リンク0件 — スキップ")
        return rows

    for i, item in enumerate(items):
        log(f"  [{i+1}/{len(items)}] {item['title'][:50]}...")
        body = fetch_article_body(item["url"])
        time.sleep(1)

        analysis = analyze_article(company, item, body)
        if not analysis:
            log("  ⚠ 分析失敗 — スキップ")
            continue

        row = build_row(company, item, analysis)
        rows.append(row)
        log(f"  ✅ スコア:{row[25]}pt  CSR:{row[15]}")
        time.sleep(2)

    return rows

def cmd_daily(test_mode: bool = False):
    log("=" * 50)
    log(f"SustainaLog Collector — {'テスト' if test_mode else '日次'}収集")
    log(f"実行日時: {now_jst_str()}")
    log("=" * 50)

    targets = TARGET_COMPANIES[:1] if test_mode else TARGET_COMPANIES
    all_rows = []
    errors = 0

    for company in targets:
        try:
            rows = collect_company(company)
            all_rows.extend(rows)
        except Exception as e:
            log(f"  ❌ {company['company_name']} エラー: {e}")
            traceback.print_exc()
            errors += 1
        time.sleep(3)

    log(f"\n{'=' * 50}")
    log(f"収集完了: {len(all_rows)}件 / {errors}社エラー")

    if not all_rows:
        log("収集データなし — 終了")
        return

    if not push_to_sheets(all_rows):
        save_local(all_rows)

    log("全処理完了 ✅")

# ============================================================
# エントリーポイント
# ============================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SustainaLog Collector")
    parser.add_argument("--init",  action="store_true", help="初期化・接続確認")
    parser.add_argument("--daily", action="store_true", help="日次収集実行")
    parser.add_argument("--test",  action="store_true", help="1社だけテスト実行")
    args = parser.parse_args()

    if args.init:
        cmd_init()
    elif args.daily:
        cmd_daily(test_mode=False)
    elif args.test:
        cmd_daily(test_mode=True)
    else:
        parser.print_help()
