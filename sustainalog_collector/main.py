#!/usr/bin/env python3
"""
SustainaLog Collector - main.py
国内企業のCSR・サステナビリティ情報を収集し、Google Sheetsに書き込む

使い方:
    python main.py --init      # シートヘッダー初期化・接続確認
    python main.py --daily     # 日次収集実行（日付ベースで20社ローテーション）
    python main.py --test      # 1社だけテスト収集（動作確認用）

必要な環境変数（GitHub Actions Secrets に設定）:
    ANTHROPIC_API_KEY : Claude API キー
    SPREADSHEET_ID    : Google SheetsのID
    GAS_WEBHOOK_URL   : GASウェブアプリのURL（書き込み用）
"""

import argparse
import hashlib
import json
import os
import re
import time
import traceback
from datetime import datetime, timezone, timedelta, date
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
# ローテーション設定
# ============================================================
COMPANIES_PER_DAY = 20            # 1日あたりの収集対象企業数
ROTATION_EPOCH = date(2026, 1, 1) # ローテーションの基準日

# ============================================================
# 収集対象企業リスト（100社）
# 日経225・TOPIX Core30を中心に業界バランスで選定
# ============================================================
TARGET_COMPANIES = [
    # --- 自動車・輸送機器 (10社) ---
    {"company_name": "トヨタ自動車", "ticker": "7203", "market": "prime", "industry": "自動車",
     "news_url": "https://global.toyota/jp/newsroom/sustainability/",
     "official_url": "https://global.toyota",
     "ir_url": "https://global.toyota/jp/ir/",
     "sustainability_url": "https://global.toyota/jp/sustainability/"},
    {"company_name": "ホンダ", "ticker": "7267", "market": "prime", "industry": "自動車",
     "news_url": "https://www.honda.co.jp/news/",
     "official_url": "https://www.honda.co.jp/",
     "ir_url": "https://www.honda.co.jp/investors/",
     "sustainability_url": "https://www.honda.co.jp/sustainability/"},
    {"company_name": "日産自動車", "ticker": "7201", "market": "prime", "industry": "自動車",
     "news_url": "https://global.nissannews.com/ja-JP/releases",
     "official_url": "https://www.nissan-global.com/JP/",
     "ir_url": "https://www.nissan-global.com/JP/IR/",
     "sustainability_url": "https://www.nissan-global.com/JP/SUSTAINABILITY/"},
    {"company_name": "スズキ", "ticker": "7269", "market": "prime", "industry": "自動車",
     "news_url": "https://www.suzuki.co.jp/release/",
     "official_url": "https://www.suzuki.co.jp/",
     "ir_url": "https://www.suzuki.co.jp/ir/",
     "sustainability_url": "https://www.suzuki.co.jp/about/csr/"},
    {"company_name": "マツダ", "ticker": "7261", "market": "prime", "industry": "自動車",
     "news_url": "https://www.mazda.com/ja/publicity/release/",
     "official_url": "https://www.mazda.com/ja/",
     "ir_url": "https://www.mazda.com/ja/investors/",
     "sustainability_url": "https://www.mazda.com/ja/sustainability/"},
    {"company_name": "SUBARU", "ticker": "7270", "market": "prime", "industry": "自動車",
     "news_url": "https://www.subaru.co.jp/news/",
     "official_url": "https://www.subaru.co.jp/",
     "ir_url": "https://www.subaru.co.jp/ir/",
     "sustainability_url": "https://www.subaru.co.jp/csr/"},
    {"company_name": "デンソー", "ticker": "6902", "market": "prime", "industry": "自動車部品",
     "news_url": "https://www.denso.com/jp/ja/news/",
     "official_url": "https://www.denso.com/jp/ja/",
     "ir_url": "https://www.denso.com/jp/ja/investors/",
     "sustainability_url": "https://www.denso.com/jp/ja/about-us/sustainability/"},
    {"company_name": "ブリヂストン", "ticker": "5108", "market": "prime", "industry": "ゴム",
     "news_url": "https://www.bridgestone.co.jp/corporate/news/",
     "official_url": "https://www.bridgestone.co.jp/",
     "ir_url": "https://www.bridgestone.co.jp/ir/",
     "sustainability_url": "https://www.bridgestone.co.jp/csr/"},
    {"company_name": "ヤマハ発動機", "ticker": "7272", "market": "prime", "industry": "輸送機器",
     "news_url": "https://global.yamaha-motor.com/jp/news/",
     "official_url": "https://global.yamaha-motor.com/jp/",
     "ir_url": "https://global.yamaha-motor.com/jp/ir/",
     "sustainability_url": "https://global.yamaha-motor.com/jp/sustainability/"},
    {"company_name": "川崎重工業", "ticker": "7012", "market": "prime", "industry": "輸送機器",
     "news_url": "https://www.khi.co.jp/pressrelease/",
     "official_url": "https://www.khi.co.jp/",
     "ir_url": "https://www.khi.co.jp/ir/",
     "sustainability_url": "https://www.khi.co.jp/sustainability/"},

    # --- 電機・精密 (15社) ---
    {"company_name": "ソニーグループ", "ticker": "6758", "market": "prime", "industry": "電機・精密",
     "news_url": "https://www.sony.com/ja/articles/sustainability-news/",
     "official_url": "https://www.sony.com/ja/",
     "ir_url": "https://www.sony.com/ja/SonyInfo/IR/",
     "sustainability_url": "https://www.sony.com/ja/SonyInfo/sustainability/"},
    {"company_name": "パナソニック", "ticker": "6752", "market": "prime", "industry": "電機・精密",
     "news_url": "https://news.panasonic.com/jp/topics",
     "official_url": "https://holdings.panasonic/jp/",
     "ir_url": "https://holdings.panasonic/jp/corporate/ir/",
     "sustainability_url": "https://holdings.panasonic/jp/corporate/sustainability/"},
    {"company_name": "日立製作所", "ticker": "6501", "market": "prime", "industry": "電機・精密",
     "news_url": "https://www.hitachi.co.jp/New/cnews/",
     "official_url": "https://www.hitachi.co.jp/",
     "ir_url": "https://www.hitachi.co.jp/IR/",
     "sustainability_url": "https://www.hitachi.co.jp/sustainability/"},
    {"company_name": "三菱電機", "ticker": "6503", "market": "prime", "industry": "電機・精密",
     "news_url": "https://www.mitsubishielectric.co.jp/news/",
     "official_url": "https://www.mitsubishielectric.co.jp/",
     "ir_url": "https://www.mitsubishielectric.co.jp/ir/",
     "sustainability_url": "https://www.mitsubishielectric.co.jp/sustainability/"},
    {"company_name": "キヤノン", "ticker": "7751", "market": "prime", "industry": "電機・精密",
     "news_url": "https://global.canon/ja/news/",
     "official_url": "https://global.canon/ja/",
     "ir_url": "https://global.canon/ja/ir/",
     "sustainability_url": "https://global.canon/ja/csr/"},
    {"company_name": "ニコン", "ticker": "7731", "market": "prime", "industry": "電機・精密",
     "news_url": "https://www.jp.nikon.com/company/news/",
     "official_url": "https://www.jp.nikon.com/",
     "ir_url": "https://www.nikon.co.jp/ir/",
     "sustainability_url": "https://www.nikon.co.jp/sustainability/"},
    {"company_name": "富士フイルム", "ticker": "4901", "market": "prime", "industry": "電機・精密",
     "news_url": "https://holdings.fujifilm.com/ja/news",
     "official_url": "https://holdings.fujifilm.com/ja/",
     "ir_url": "https://holdings.fujifilm.com/ja/investors",
     "sustainability_url": "https://holdings.fujifilm.com/ja/sustainability"},
    {"company_name": "リコー", "ticker": "7752", "market": "prime", "industry": "電機・精密",
     "news_url": "https://jp.ricoh.com/release/",
     "official_url": "https://jp.ricoh.com/",
     "ir_url": "https://jp.ricoh.com/IR/",
     "sustainability_url": "https://jp.ricoh.com/sustainability/"},
    {"company_name": "東芝", "ticker": "6502", "market": "prime", "industry": "電機・精密",
     "news_url": "https://www.global.toshiba/jp/news/corporate.html",
     "official_url": "https://www.global.toshiba/jp/top.html",
     "ir_url": "https://www.global.toshiba/jp/ir.html",
     "sustainability_url": "https://www.global.toshiba/jp/sustainability.html"},
    {"company_name": "シャープ", "ticker": "6753", "market": "prime", "industry": "電機・精密",
     "news_url": "https://corporate.jp.sharp/news/",
     "official_url": "https://corporate.jp.sharp/",
     "ir_url": "https://corporate.jp.sharp/ir/",
     "sustainability_url": "https://corporate.jp.sharp/eco/"},
    {"company_name": "村田製作所", "ticker": "6981", "market": "prime", "industry": "電子部品",
     "news_url": "https://corporate.murata.com/ja-jp/newsroom",
     "official_url": "https://corporate.murata.com/ja-jp",
     "ir_url": "https://corporate.murata.com/ja-jp/ir",
     "sustainability_url": "https://corporate.murata.com/ja-jp/sustainability"},
    {"company_name": "京セラ", "ticker": "6971", "market": "prime", "industry": "電子部品",
     "news_url": "https://www.kyocera.co.jp/newsroom/",
     "official_url": "https://www.kyocera.co.jp/",
     "ir_url": "https://www.kyocera.co.jp/ir/",
     "sustainability_url": "https://www.kyocera.co.jp/sustainability/"},
    {"company_name": "東京エレクトロン", "ticker": "8035", "market": "prime", "industry": "半導体製造装置",
     "news_url": "https://www.tel.co.jp/news/",
     "official_url": "https://www.tel.co.jp/",
     "ir_url": "https://www.tel.co.jp/ir/",
     "sustainability_url": "https://www.tel.co.jp/sustainability/"},
    {"company_name": "ファナック", "ticker": "6954", "market": "prime", "industry": "電機・精密",
     "news_url": "https://www.fanuc.co.jp/ja/news/index.html",
     "official_url": "https://www.fanuc.co.jp/",
     "ir_url": "https://www.fanuc.co.jp/ja/ir/",
     "sustainability_url": "https://www.fanuc.co.jp/ja/sustainability/"},
    {"company_name": "オムロン", "ticker": "6645", "market": "prime", "industry": "電機・精密",
     "news_url": "https://www.omron.com/jp/ja/news/",
     "official_url": "https://www.omron.com/jp/ja/",
     "ir_url": "https://www.omron.com/jp/ja/ir/",
     "sustainability_url": "https://sustainability.omron.com/jp/"},

    # --- 化学・素材 (10社) ---
    {"company_name": "花王", "ticker": "4452", "market": "prime", "industry": "化学・化粧品",
     "news_url": "https://www.kao.com/jp/newsroom/news/",
     "official_url": "https://www.kao.com/jp/",
     "ir_url": "https://www.kao.com/jp/corporate/investors/",
     "sustainability_url": "https://www.kao.com/jp/corporate/sustainability/"},
    {"company_name": "資生堂", "ticker": "4911", "market": "prime", "industry": "化粧品",
     "news_url": "https://corp.shiseido.com/jp/news/",
     "official_url": "https://corp.shiseido.com/jp/",
     "ir_url": "https://corp.shiseido.com/jp/ir/",
     "sustainability_url": "https://corp.shiseido.com/jp/sustainability/"},
    {"company_name": "住友化学", "ticker": "4005", "market": "prime", "industry": "化学",
     "news_url": "https://www.sumitomo-chem.co.jp/news/",
     "official_url": "https://www.sumitomo-chem.co.jp/",
     "ir_url": "https://www.sumitomo-chem.co.jp/ir/",
     "sustainability_url": "https://www.sumitomo-chem.co.jp/sustainability/"},
    {"company_name": "三菱ケミカル", "ticker": "4188", "market": "prime", "industry": "化学",
     "news_url": "https://www.mcgc.com/news_release/",
     "official_url": "https://www.mcgc.com/",
     "ir_url": "https://www.mcgc.com/ir/",
     "sustainability_url": "https://www.mcgc.com/sustainability/"},
    {"company_name": "旭化成", "ticker": "3407", "market": "prime", "industry": "化学",
     "news_url": "https://www.asahi-kasei.com/jp/news/",
     "official_url": "https://www.asahi-kasei.com/jp/",
     "ir_url": "https://www.asahi-kasei.com/jp/ir/",
     "sustainability_url": "https://www.asahi-kasei.com/jp/sustainability/"},
    {"company_name": "信越化学工業", "ticker": "4063", "market": "prime", "industry": "化学",
     "news_url": "https://www.shinetsu.co.jp/jp/news/",
     "official_url": "https://www.shinetsu.co.jp/jp/",
     "ir_url": "https://www.shinetsu.co.jp/jp/ir/",
     "sustainability_url": "https://www.shinetsu.co.jp/jp/sustainability/"},
    {"company_name": "東レ", "ticker": "3402", "market": "prime", "industry": "化学・繊維",
     "news_url": "https://www.toray.co.jp/news/",
     "official_url": "https://www.toray.co.jp/",
     "ir_url": "https://www.toray.co.jp/ir/",
     "sustainability_url": "https://www.toray.co.jp/sustainability/"},
    {"company_name": "日本製鉄", "ticker": "5401", "market": "prime", "industry": "鉄鋼",
     "news_url": "https://www.nipponsteel.com/news/",
     "official_url": "https://www.nipponsteel.com/",
     "ir_url": "https://www.nipponsteel.com/ir/",
     "sustainability_url": "https://www.nipponsteel.com/csr/"},
    {"company_name": "JFEホールディングス", "ticker": "5411", "market": "prime", "industry": "鉄鋼",
     "news_url": "https://www.jfe-holdings.co.jp/release/",
     "official_url": "https://www.jfe-holdings.co.jp/",
     "ir_url": "https://www.jfe-holdings.co.jp/investor/",
     "sustainability_url": "https://www.jfe-holdings.co.jp/sustainability/"},
    {"company_name": "住友金属鉱山", "ticker": "5713", "market": "prime", "industry": "非鉄金属",
     "news_url": "https://www.smm.co.jp/news/",
     "official_url": "https://www.smm.co.jp/",
     "ir_url": "https://www.smm.co.jp/ir/",
     "sustainability_url": "https://www.smm.co.jp/csr/"},
  # --- 食品・飲料 (8社) ---
    {"company_name": "キリンホールディングス", "ticker": "2503", "market": "prime", "industry": "食品・飲料",
     "news_url": "https://www.kirinholdings.com/jp/newsroom/",
     "official_url": "https://www.kirinholdings.com/jp/",
     "ir_url": "https://www.kirinholdings.com/jp/investors/",
     "sustainability_url": "https://www.kirinholdings.com/jp/impact/"},
    {"company_name": "アサヒグループホールディングス", "ticker": "2502", "market": "prime", "industry": "食品・飲料",
     "news_url": "https://www.asahigroup-holdings.com/newsroom/",
     "official_url": "https://www.asahigroup-holdings.com/",
     "ir_url": "https://www.asahigroup-holdings.com/ir/",
     "sustainability_url": "https://www.asahigroup-holdings.com/csr/"},
    {"company_name": "サントリーホールディングス", "ticker": "", "market": "unlisted", "industry": "食品・飲料",
     "news_url": "https://www.suntory.co.jp/news/",
     "official_url": "https://www.suntory.co.jp/",
     "ir_url": "",
     "sustainability_url": "https://www.suntory.co.jp/company/csr/"},
    {"company_name": "味の素", "ticker": "2802", "market": "prime", "industry": "食品",
     "news_url": "https://www.ajinomoto.co.jp/company/jp/presscenter/",
     "official_url": "https://www.ajinomoto.co.jp/",
     "ir_url": "https://www.ajinomoto.co.jp/company/jp/ir/",
     "sustainability_url": "https://www.ajinomoto.co.jp/company/jp/activity/"},
    {"company_name": "明治ホールディングス", "ticker": "2269", "market": "prime", "industry": "食品",
     "news_url": "https://www.meiji.com/news/",
     "official_url": "https://www.meiji.com/",
     "ir_url": "https://www.meiji.com/investor/",
     "sustainability_url": "https://www.meiji.com/sustainability/"},
    {"company_name": "日清食品ホールディングス", "ticker": "2897", "market": "prime", "industry": "食品",
     "news_url": "https://www.nissin.com/jp/news/",
     "official_url": "https://www.nissin.com/jp/",
     "ir_url": "https://www.nissin.com/jp/ir/",
     "sustainability_url": "https://www.nissin.com/jp/sustainability/"},
    {"company_name": "キッコーマン", "ticker": "2801", "market": "prime", "industry": "食品",
     "news_url": "https://www.kikkoman.com/jp/news/",
     "official_url": "https://www.kikkoman.com/jp/",
     "ir_url": "https://www.kikkoman.com/jp/ir/",
     "sustainability_url": "https://www.kikkoman.com/jp/csr/"},
    {"company_name": "日本たばこ産業", "ticker": "2914", "market": "prime", "industry": "食品・嗜好品",
     "news_url": "https://www.jti.co.jp/investors/press_releases/",
     "official_url": "https://www.jti.co.jp/",
     "ir_url": "https://www.jti.co.jp/investors/",
     "sustainability_url": "https://www.jti.co.jp/sustainability/"},

    # --- 小売・サービス (10社) ---
    {"company_name": "イオン", "ticker": "8267", "market": "prime", "industry": "小売",
     "news_url": "https://www.aeon.info/news/",
     "official_url": "https://www.aeon.info/",
     "ir_url": "https://www.aeon.info/ir/",
     "sustainability_url": "https://www.aeon.info/sustainability/"},
    {"company_name": "セブン&アイ・ホールディングス", "ticker": "3382", "market": "prime", "industry": "小売",
     "news_url": "https://www.7andi.com/company/news/release.html",
     "official_url": "https://www.7andi.com/",
     "ir_url": "https://www.7andi.com/ir.html",
     "sustainability_url": "https://www.7andi.com/sustainability/"},
    {"company_name": "ファーストリテイリング", "ticker": "9983", "market": "prime", "industry": "小売・アパレル",
     "news_url": "https://www.fastretailing.com/jp/group/news/",
     "official_url": "https://www.fastretailing.com/jp/",
     "ir_url": "https://www.fastretailing.com/jp/ir/",
     "sustainability_url": "https://www.fastretailing.com/jp/sustainability/"},
    {"company_name": "良品計画", "ticker": "7453", "market": "prime", "industry": "小売",
     "news_url": "https://www.ryohin-keikaku.jp/news/",
     "official_url": "https://www.ryohin-keikaku.jp/",
     "ir_url": "https://ryohin-keikaku.jp/ir/",
     "sustainability_url": "https://ryohin-keikaku.jp/sustainability/"},
    {"company_name": "ニトリホールディングス", "ticker": "9843", "market": "prime", "industry": "小売",
     "news_url": "https://www.nitorihd.co.jp/news/",
     "official_url": "https://www.nitorihd.co.jp/",
     "ir_url": "https://www.nitorihd.co.jp/ir/",
     "sustainability_url": "https://www.nitorihd.co.jp/sustainability/"},
    {"company_name": "ローソン", "ticker": "2651", "market": "prime", "industry": "小売",
     "news_url": "https://www.lawson.co.jp/company/news/",
     "official_url": "https://www.lawson.co.jp/",
     "ir_url": "https://www.lawson.co.jp/company/ir/",
     "sustainability_url": "https://www.lawson.co.jp/company/activity/"},
    {"company_name": "リクルートホールディングス", "ticker": "6098", "market": "prime", "industry": "サービス",
     "news_url": "https://recruit-holdings.com/ja/newsroom/",
     "official_url": "https://recruit-holdings.com/ja/",
     "ir_url": "https://recruit-holdings.com/ja/ir/",
     "sustainability_url": "https://recruit-holdings.com/ja/sustainability/"},
    {"company_name": "オリエンタルランド", "ticker": "4661", "market": "prime", "industry": "サービス",
     "news_url": "https://www.olc.co.jp/ja/news/",
     "official_url": "https://www.olc.co.jp/ja/",
     "ir_url": "https://www.olc.co.jp/ja/ir/",
     "sustainability_url": "https://www.olc.co.jp/ja/sustainability/"},
    {"company_name": "ヤマトホールディングス", "ticker": "9064", "market": "prime", "industry": "運輸",
     "news_url": "https://www.yamato-hd.co.jp/news/",
     "official_url": "https://www.yamato-hd.co.jp/",
     "ir_url": "https://www.yamato-hd.co.jp/investors/",
     "sustainability_url": "https://www.yamato-hd.co.jp/csr/"},
    {"company_name": "ZOZO", "ticker": "3092", "market": "prime", "industry": "小売・EC",
     "news_url": "https://corp.zozo.com/news/",
     "official_url": "https://corp.zozo.com/",
     "ir_url": "https://corp.zozo.com/ir/",
     "sustainability_url": "https://corp.zozo.com/about/sustainability/"},

    # --- 金融・保険 (8社) ---
    {"company_name": "三菱UFJフィナンシャル・グループ", "ticker": "8306", "market": "prime", "industry": "銀行",
     "news_url": "https://www.mufg.jp/pressrelease/",
     "official_url": "https://www.mufg.jp/",
     "ir_url": "https://www.mufg.jp/ir/",
     "sustainability_url": "https://www.mufg.jp/csr/"},
    {"company_name": "三井住友フィナンシャルグループ", "ticker": "8316", "market": "prime", "industry": "銀行",
     "news_url": "https://www.smfg.co.jp/news/",
     "official_url": "https://www.smfg.co.jp/",
     "ir_url": "https://www.smfg.co.jp/investor/",
     "sustainability_url": "https://www.smfg.co.jp/sustainability/"},
    {"company_name": "みずほフィナンシャルグループ", "ticker": "8411", "market": "prime", "industry": "銀行",
     "news_url": "https://www.mizuho-fg.co.jp/release/",
     "official_url": "https://www.mizuho-fg.co.jp/",
     "ir_url": "https://www.mizuho-fg.co.jp/investors/",
     "sustainability_url": "https://www.mizuho-fg.co.jp/sustainability/"},
    {"company_name": "野村ホールディングス", "ticker": "8604", "market": "prime", "industry": "証券",
     "news_url": "https://www.nomura.com/jp/news/",
     "official_url": "https://www.nomura.com/jp/",
     "ir_url": "https://www.nomura.com/jp/investor-relations/",
     "sustainability_url": "https://www.nomura.com/jp/sustainability/"},
    {"company_name": "東京海上ホールディングス", "ticker": "8766", "market": "prime", "industry": "保険",
     "news_url": "https://www.tokiomarinehd.com/release_topics/",
     "official_url": "https://www.tokiomarinehd.com/",
     "ir_url": "https://www.tokiomarinehd.com/ir/",
     "sustainability_url": "https://www.tokiomarinehd.com/sustainability/"},
    {"company_name": "MS&ADインシュアランスグループ", "ticker": "8725", "market": "prime", "industry": "保険",
     "news_url": "https://www.ms-ad-hd.com/ja/news/",
     "official_url": "https://www.ms-ad-hd.com/ja/",
     "ir_url": "https://www.ms-ad-hd.com/ja/ir.html",
     "sustainability_url": "https://www.ms-ad-hd.com/ja/group/sustainability.html"},
    {"company_name": "SOMPOホールディングス", "ticker": "8630", "market": "prime", "industry": "保険",
     "news_url": "https://www.sompo-hd.com/news/",
     "official_url": "https://www.sompo-hd.com/",
     "ir_url": "https://www.sompo-hd.com/ir/",
     "sustainability_url": "https://www.sompo-hd.com/csr/"},
    {"company_name": "第一生命ホールディングス", "ticker": "8750", "market": "prime", "industry": "保険",
     "news_url": "https://www.dai-ichi-life-hd.com/news/",
     "official_url": "https://www.dai-ichi-life-hd.com/",
     "ir_url": "https://www.dai-ichi-life-hd.com/investor/",
     "sustainability_url": "https://www.dai-ichi-life-hd.com/sustainability/"},

    # --- 通信・IT (8社) ---
    {"company_name": "NTT", "ticker": "9432", "market": "prime", "industry": "通信",
     "news_url": "https://group.ntt/jp/newsrelease/",
     "official_url": "https://group.ntt/jp/",
     "ir_url": "https://group.ntt/jp/ir/",
     "sustainability_url": "https://group.ntt/jp/sustainability/"},
    {"company_name": "KDDI", "ticker": "9433", "market": "prime", "industry": "通信",
     "news_url": "https://news.kddi.com/kddi/corporate/newsrelease/",
     "official_url": "https://www.kddi.com/",
     "ir_url": "https://www.kddi.com/corporate/ir/",
     "sustainability_url": "https://www.kddi.com/corporate/sustainability/"},
    {"company_name": "ソフトバンク", "ticker": "9434", "market": "prime", "industry": "通信",
     "news_url": "https://www.softbank.jp/corp/news/press/",
     "official_url": "https://www.softbank.jp/corp/",
     "ir_url": "https://www.softbank.jp/corp/ir/",
     "sustainability_url": "https://www.softbank.jp/corp/sustainability/"},
    {"company_name": "ソフトバンクグループ", "ticker": "9984", "market": "prime", "industry": "投資・IT",
     "news_url": "https://group.softbank/news",
     "official_url": "https://group.softbank/",
     "ir_url": "https://group.softbank/ir",
     "sustainability_url": "https://group.softbank/sustainability"},
    {"company_name": "楽天グループ", "ticker": "4755", "market": "prime", "industry": "IT・EC",
     "news_url": "https://corp.rakuten.co.jp/news/press/",
     "official_url": "https://corp.rakuten.co.jp/",
     "ir_url": "https://corp.rakuten.co.jp/investors/",
     "sustainability_url": "https://corp.rakuten.co.jp/sustainability/"},
    {"company_name": "LINEヤフー", "ticker": "4689", "market": "prime", "industry": "IT",
     "news_url": "https://www.lycorp.co.jp/ja/news/",
     "official_url": "https://www.lycorp.co.jp/ja/",
     "ir_url": "https://www.lycorp.co.jp/ja/ir/",
     "sustainability_url": "https://www.lycorp.co.jp/ja/sustainability/"},
    {"company_name": "メルカリ", "ticker": "4385", "market": "prime", "industry": "IT",
     "news_url": "https://about.mercari.com/press/news/",
     "official_url": "https://about.mercari.com/",
     "ir_url": "https://about.mercari.com/ir/",
     "sustainability_url": "https://about.mercari.com/sustainability/"},
    {"company_name": "サイバーエージェント", "ticker": "4751", "market": "prime", "industry": "IT",
     "news_url": "https://www.cyberagent.co.jp/news/",
     "official_url": "https://www.cyberagent.co.jp/",
     "ir_url": "https://www.cyberagent.co.jp/ir/",
     "sustainability_url": "https://www.cyberagent.co.jp/sustainability/"},

    # --- 建設・不動産 (8社) ---
    {"company_name": "積水ハウス", "ticker": "1928", "market": "prime", "industry": "建設・不動産",
     "news_url": "https://www.sekisuihouse.co.jp/company/news/",
     "official_url": "https://www.sekisuihouse.co.jp/",
     "ir_url": "https://www.sekisuihouse.co.jp/company/ir/",
     "sustainability_url": "https://www.sekisuihouse.co.jp/sustainable/"},
    {"company_name": "大和ハウス工業", "ticker": "1925", "market": "prime", "industry": "建設・不動産",
     "news_url": "https://www.daiwahouse.co.jp/news/",
     "official_url": "https://www.daiwahouse.co.jp/",
     "ir_url": "https://www.daiwahouse.co.jp/ir/",
     "sustainability_url": "https://www.daiwahouse.co.jp/sustainable/"},
    {"company_name": "清水建設", "ticker": "1803", "market": "prime", "industry": "建設",
     "news_url": "https://www.shimz.co.jp/company/about/news-release/",
     "official_url": "https://www.shimz.co.jp/",
     "ir_url": "https://www.shimz.co.jp/ir/",
     "sustainability_url": "https://www.shimz.co.jp/company/csr/"},
    {"company_name": "大林組", "ticker": "1802", "market": "prime", "industry": "建設",
     "news_url": "https://www.obayashi.co.jp/news/",
     "official_url": "https://www.obayashi.co.jp/",
     "ir_url": "https://www.obayashi.co.jp/ir/",
     "sustainability_url": "https://www.obayashi.co.jp/sustainability/"},
    {"company_name": "鹿島建設", "ticker": "1812", "market": "prime", "industry": "建設",
     "news_url": "https://www.kajima.co.jp/news/press/",
     "official_url": "https://www.kajima.co.jp/",
     "ir_url": "https://www.kajima.co.jp/ir/",
     "sustainability_url": "https://www.kajima.co.jp/csr/"},
    {"company_name": "三井不動産", "ticker": "8801", "market": "prime", "industry": "不動産",
     "news_url": "https://www.mitsuifudosan.co.jp/corporate/news/",
     "official_url": "https://www.mitsuifudosan.co.jp/",
     "ir_url": "https://www.mitsuifudosan.co.jp/corporate/ir/",
     "sustainability_url": "https://www.mitsuifudosan.co.jp/esg_csr/"},
    {"company_name": "三菱地所", "ticker": "8802", "market": "prime", "industry": "不動産",
     "news_url": "https://www.mec.co.jp/j/news/",
     "official_url": "https://www.mec.co.jp/",
     "ir_url": "https://www.mec.co.jp/j/investor/",
     "sustainability_url": "https://www.mec.co.jp/j/sustainability/"},
    {"company_name": "住友不動産", "ticker": "8830", "market": "prime", "industry": "不動産",
     "news_url": "https://www.sumitomo-rd.co.jp/corporate/news/",
     "official_url": "https://www.sumitomo-rd.co.jp/",
     "ir_url": "https://www.sumitomo-rd.co.jp/ir/",
     "sustainability_url": "https://www.sumitomo-rd.co.jp/csr/"},
  # --- 医薬・ヘルスケア (8社) ---
    {"company_name": "武田薬品工業", "ticker": "4502", "market": "prime", "industry": "医薬品",
     "news_url": "https://www.takeda.com/jp/newsroom/",
     "official_url": "https://www.takeda.com/jp/",
     "ir_url": "https://www.takeda.com/jp/investors/",
     "sustainability_url": "https://www.takeda.com/jp/sustainability/"},
    {"company_name": "アステラス製薬", "ticker": "4503", "market": "prime", "industry": "医薬品",
     "news_url": "https://www.astellas.com/jp/news",
     "official_url": "https://www.astellas.com/jp/",
     "ir_url": "https://www.astellas.com/jp/investors",
     "sustainability_url": "https://www.astellas.com/jp/sustainability"},
    {"company_name": "第一三共", "ticker": "4568", "market": "prime", "industry": "医薬品",
     "news_url": "https://www.daiichisankyo.co.jp/media/press_release/",
     "official_url": "https://www.daiichisankyo.co.jp/",
     "ir_url": "https://www.daiichisankyo.co.jp/investors/",
     "sustainability_url": "https://www.daiichisankyo.co.jp/sustainability/"},
    {"company_name": "エーザイ", "ticker": "4523", "market": "prime", "industry": "医薬品",
     "news_url": "https://www.eisai.co.jp/news/",
     "official_url": "https://www.eisai.co.jp/",
     "ir_url": "https://www.eisai.co.jp/ir/",
     "sustainability_url": "https://www.eisai.co.jp/sustainability/"},
    {"company_name": "大塚ホールディングス", "ticker": "4578", "market": "prime", "industry": "医薬品",
     "news_url": "https://www.otsuka.com/jp/release/",
     "official_url": "https://www.otsuka.com/jp/",
     "ir_url": "https://www.otsuka.com/jp/ir/",
     "sustainability_url": "https://www.otsuka.com/jp/csr/"},
    {"company_name": "中外製薬", "ticker": "4519", "market": "prime", "industry": "医薬品",
     "news_url": "https://www.chugai-pharm.co.jp/news/",
     "official_url": "https://www.chugai-pharm.co.jp/",
     "ir_url": "https://www.chugai-pharm.co.jp/ir/",
     "sustainability_url": "https://www.chugai-pharm.co.jp/sustainability/"},
    {"company_name": "オリンパス", "ticker": "7733", "market": "prime", "industry": "医療機器",
     "news_url": "https://www.olympus.co.jp/news/",
     "official_url": "https://www.olympus.co.jp/",
     "ir_url": "https://www.olympus.co.jp/ir/",
     "sustainability_url": "https://www.olympus.co.jp/sustainability/"},
    {"company_name": "テルモ", "ticker": "4543", "market": "prime", "industry": "医療機器",
     "news_url": "https://www.terumo.co.jp/newsrelease/",
     "official_url": "https://www.terumo.co.jp/",
     "ir_url": "https://www.terumo.co.jp/investors/",
     "sustainability_url": "https://www.terumo.co.jp/sustainability/"},

    # --- 商社 (5社) ---
    {"company_name": "三菱商事", "ticker": "8058", "market": "prime", "industry": "商社",
     "news_url": "https://www.mitsubishicorp.com/jp/ja/pr/",
     "official_url": "https://www.mitsubishicorp.com/jp/ja/",
     "ir_url": "https://www.mitsubishicorp.com/jp/ja/ir/",
     "sustainability_url": "https://www.mitsubishicorp.com/jp/ja/csr/"},
    {"company_name": "三井物産", "ticker": "8031", "market": "prime", "industry": "商社",
     "news_url": "https://www.mitsui.com/jp/ja/release/",
     "official_url": "https://www.mitsui.com/jp/ja/",
     "ir_url": "https://www.mitsui.com/jp/ja/ir/",
     "sustainability_url": "https://www.mitsui.com/jp/ja/sustainability/"},
    {"company_name": "伊藤忠商事", "ticker": "8001", "market": "prime", "industry": "商社",
     "news_url": "https://www.itochu.co.jp/ja/news/",
     "official_url": "https://www.itochu.co.jp/ja/",
     "ir_url": "https://www.itochu.co.jp/ja/ir/",
     "sustainability_url": "https://www.itochu.co.jp/ja/csr/"},
    {"company_name": "住友商事", "ticker": "8053", "market": "prime", "industry": "商社",
     "news_url": "https://www.sumitomocorp.com/ja/jp/news",
     "official_url": "https://www.sumitomocorp.com/ja/jp",
     "ir_url": "https://www.sumitomocorp.com/ja/jp/ir",
     "sustainability_url": "https://www.sumitomocorp.com/ja/jp/sustainability"},
    {"company_name": "丸紅", "ticker": "8002", "market": "prime", "industry": "商社",
     "news_url": "https://www.marubeni.com/jp/news/",
     "official_url": "https://www.marubeni.com/jp/",
     "ir_url": "https://www.marubeni.com/jp/ir/",
     "sustainability_url": "https://www.marubeni.com/jp/sustainability/"},

    # --- エネルギー・資源 (5社) ---
    {"company_name": "ENEOSホールディングス", "ticker": "5020", "market": "prime", "industry": "石油",
     "news_url": "https://www.hd.eneos.co.jp/newsrelease/",
     "official_url": "https://www.hd.eneos.co.jp/",
     "ir_url": "https://www.hd.eneos.co.jp/ir/",
     "sustainability_url": "https://www.hd.eneos.co.jp/sustainability/"},
    {"company_name": "出光興産", "ticker": "5019", "market": "prime", "industry": "石油",
     "news_url": "https://www.idemitsu.com/jp/news/",
     "official_url": "https://www.idemitsu.com/jp/",
     "ir_url": "https://www.idemitsu.com/jp/ir/",
     "sustainability_url": "https://www.idemitsu.com/jp/sustainability/"},
    {"company_name": "東京電力ホールディングス", "ticker": "9501", "market": "prime", "industry": "電力",
     "news_url": "https://www.tepco.co.jp/press/",
     "official_url": "https://www.tepco.co.jp/",
     "ir_url": "https://www.tepco.co.jp/ir/",
     "sustainability_url": "https://www.tepco.co.jp/sustainability/"},
    {"company_name": "関西電力", "ticker": "9503", "market": "prime", "industry": "電力",
     "news_url": "https://www.kepco.co.jp/corporate/pr/",
     "official_url": "https://www.kepco.co.jp/",
     "ir_url": "https://www.kepco.co.jp/corporate/ir/",
     "sustainability_url": "https://www.kepco.co.jp/sustainability/"},
    {"company_name": "東京ガス", "ticker": "9531", "market": "prime", "industry": "ガス",
     "news_url": "https://www.tokyo-gas.co.jp/news/",
     "official_url": "https://www.tokyo-gas.co.jp/",
     "ir_url": "https://www.tokyo-gas.co.jp/IR/",
     "sustainability_url": "https://www.tokyo-gas.co.jp/sustainability/"},

    # --- 運輸・その他 (5社) ---
    {"company_name": "JR東日本", "ticker": "9020", "market": "prime", "industry": "運輸",
     "news_url": "https://www.jreast.co.jp/press/",
     "official_url": "https://www.jreast.co.jp/",
     "ir_url": "https://www.jreast.co.jp/investor/",
     "sustainability_url": "https://www.jreast.co.jp/eco/"},
    {"company_name": "JR東海", "ticker": "9022", "market": "prime", "industry": "運輸",
     "news_url": "https://jr-central.co.jp/news/",
     "official_url": "https://jr-central.co.jp/",
     "ir_url": "https://jr-central.co.jp/ir/",
     "sustainability_url": "https://jr-central.co.jp/sustainability/"},
    {"company_name": "ANAホールディングス", "ticker": "9202", "market": "prime", "industry": "運輸",
     "news_url": "https://www.ana.co.jp/group/pr/",
     "official_url": "https://www.ana.co.jp/group/",
     "ir_url": "https://www.ana.co.jp/group/investors/",
     "sustainability_url": "https://www.ana.co.jp/group/csr/"},
    {"company_name": "日本郵船", "ticker": "9101", "market": "prime", "industry": "海運",
     "news_url": "https://www.nyk.com/news/",
     "official_url": "https://www.nyk.com/",
     "ir_url": "https://www.nyk.com/ir/",
     "sustainability_url": "https://www.nyk.com/esg/"},
    {"company_name": "電通グループ", "ticker": "4324", "market": "prime", "industry": "メディア・広告",
     "news_url": "https://www.group.dentsu.com/jp/news/",
     "official_url": "https://www.group.dentsu.com/jp/",
     "ir_url": "https://www.group.dentsu.com/jp/ir/",
     "sustainability_url": "https://www.group.dentsu.com/jp/sustainability/"},
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
    date_str = datetime.now(JST).strftime("%Y%m%d")
    return base[:60] + "-" + date_str

def log(msg: str):
    ts = datetime.now(JST).strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)

# ============================================================
# ローテーション
# ============================================================
def get_today_companies() -> list:
    """
    日付を基準に、本日収集対象の企業リストを返す。
    決定論的: 同じ日付なら必ず同じ企業セットになる。
    ウィンドウは循環する: 末尾に達したらリストの先頭に戻る。
    """
    total = len(TARGET_COMPANIES)
    if total <= COMPANIES_PER_DAY:
        return TARGET_COMPANIES

    today = datetime.now(JST).date()
    day_number = (today - ROTATION_EPOCH).days
    start = (day_number * COMPANIES_PER_DAY) % total
    end = start + COMPANIES_PER_DAY

    if end <= total:
        window = TARGET_COMPANIES[start:end]
    else:
        window = TARGET_COMPANIES[start:] + TARGET_COMPANIES[:end - total]

    log(f"🔄 ローテーション: day #{day_number}, 企業 {start}〜{(end - 1) % total} / 全{total}社")
    return window

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
        "article", "li.news-item", "li.release-item", "li.press-item",
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

            date_str = ""
            date_el = el.find("time")
            if date_el:
                date_str = date_el.get("datetime", "") or date_el.get_text(strip=True)

            results.append({"url": full_url, "title": title[:200], "date": date_str[:30]})
            if len(results) >= 5:
                break
        if len(results) >= 5:
            break

    if not results:
        keywords = ["サステナ", "csr", "環境", "社会", "esg", "脱炭素", "carbon", "sustain", "social", "environment", "sdg"]
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
        soup.find("main")
        or soup.find("article")
        or soup.find(id=re.compile(r"content|main|body|article", re.I))
        or soup.find(class_=re.compile(r"content|main|body|article", re.I))
        or soup.body
    )
    text = main.get_text(separator="\n", strip=True) if main else ""
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text[:2500]

# ============================================================
# Claude API
# ============================================================
CLAUDE_MODEL = "claude-haiku-4-5-20251001"
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
        int(analysis.get("score_social_clarity", 10)),
        int(analysis.get("score_continuity", 10)),
        int(analysis.get("score_business_alignment", 10)),
        int(analysis.get("score_specificity", 10)),
        int(analysis.get("score_reference_value", 10)),
    ]
    total = sum(scores)

    article_id = make_article_id(company["company_name"], item["url"])
    slug = make_slug(company["company_name"], analysis.get("translated_title", item["title"]))

    tags = analysis.get("classification_tags", [])
    tags_str = ",".join(tags) if isinstance(tags, list) else str(tags)

    return [
        article_id, slug, company["company_name"],
        company.get("ticker", ""), company.get("market", "prime"), company.get("industry", ""),
        company["company_name"] + " ニュースリリース",
        item["url"], company.get("official_url", ""), company.get("ir_url", ""),
        company.get("sustainability_url", ""),
        item["title"], analysis.get("translated_title", item["title"]),
        analysis.get("summary", ""), analysis.get("ai_commentary", ""),
        analysis.get("csr_type", "その他CSR"), analysis.get("csr_subtype", ""),
        analysis.get("relation_type", "direct"), analysis.get("stakeholder_type", "全般"),
        tags_str,
        scores[0], scores[1], scores[2], scores[3], scores[4], total,
        item.get("date", today_jst_str()), now_jst_str(),
        "pending_review", "FALSE",
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
    log(f"登録企業総数      : {len(TARGET_COMPANIES)}社")
    log(f"1日の収集対象     : {COMPANIES_PER_DAY}社 (約{(len(TARGET_COMPANIES) + COMPANIES_PER_DAY - 1) // COMPANIES_PER_DAY}日で一巡)")
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
            log("    ⚠ 分析失敗 — スキップ")
            continue
        row = build_row(company, item, analysis)
        rows.append(row)
        log(f"    ✅ スコア:{row[25]}pt CSR:{row[15]}")
        time.sleep(2)
    return rows

def cmd_daily(test_mode: bool = False):
    log("=" * 50)
    log(f"SustainaLog Collector — {'テスト' if test_mode else '日次'}収集")
    log(f"実行日時: {now_jst_str()}")
    log("=" * 50)

    if test_mode:
        targets = TARGET_COMPANIES[:1]
    else:
        targets = get_today_companies()

    log(f"本日の対象: {len(targets)}社")
    for c in targets:
        log(f"  - {c['company_name']} ({c['industry']})")

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
