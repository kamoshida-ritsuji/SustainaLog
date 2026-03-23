// ============================================================
// SustainaLog — 公開用データレイヤー
// ============================================================
// 本番サイト（index / articles / article）専用。
// Google Sheets から published 記事だけを取得し、
// キャッシュして各ページに提供する。
//
// 読み込み順: schema.js → dummy-data.js → sheets-api.js → public-data.js → data.js
// ============================================================

'use strict';

// ────────────────────────────────────────────
// 内部キャッシュ
// ────────────────────────────────────────────
let _publicArticles = null;   // null = 未ロード
let _publicSource   = 'loading'; // 'sheets' | 'fallback' | 'loading'
let _publicError    = null;

// ────────────────────────────────────────────
// slug 自動生成ユーティリティ
// ────────────────────────────────────────────
function ensureSlug(article) {
  if (article.slug && article.slug.trim() !== '') return article;
  const base = (article.article_id || 'article')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '');
  return { ...article, slug: base };
}

// ────────────────────────────────────────────
// published フィルタ
// ────────────────────────────────────────────
function filterPublished(articles) {
  return articles
    .filter(a =>
      a.status === ARTICLE_STATUS.PUBLISHED &&
      String(a.publish_flag).toUpperCase() === 'TRUE'
    )
    .map(ensureSlug);
}

// ────────────────────────────────────────────
// Sheets から公開記事を取得（メイン）
// ────────────────────────────────────────────
async function loadPublicArticles() {
  if (_publicArticles !== null) return;

  if (!isSheetsConfigured()) {
    _publicArticles = filterPublished(
      typeof DUMMY_ARTICLES !== 'undefined' ? DUMMY_ARTICLES : []
    );
    _publicSource = 'fallback';
    _publicError  = 'SPREADSHEET_ID 未設定';
    return;
  }

  try {
    const result = await fetchArticlesFromSheets();
    _publicArticles = filterPublished(result.data || []);
    _publicSource   = result.source || 'sheets';
    _publicError    = result.error  || null;
    console.info('[PublicData] ' + _publicArticles.length + '件の公開記事を読み込みました（ソース: ' + _publicSource + '）');
  } catch (err) {
    console.error('[PublicData] 取得エラー:', err.message);
    _publicArticles = filterPublished(
      typeof DUMMY_ARTICLES !== 'undefined' ? DUMMY_ARTICLES : []
    );
    _publicSource = 'fallback';
    _publicError  = err.message;
  }
}

// ────────────────────────────────────────────
// 公開API
// ────────────────────────────────────────────

function getPublicArticles() {
  if (_publicArticles === null) return [];
  return _publicArticles;
}

function getPublicArticleBySlug(slug) {
  return getPublicArticles().find(a => a.slug === slug) || null;
}

function getPublicArticlesByCsrType(csrType) {
  return getPublicArticles().filter(a => a.csr_type === csrType);
}

function getPublicArticlesByCompany(companyName) {
  return getPublicArticles().filter(a => a.company_name === companyName);
}

function getPublicDataSource() {
  return { source: _publicSource, error: _publicError };
}

// ────────────────────────────────────────────
// 既存API の差し替え（後方互換シム）
// ────────────────────────────────────────────
function getPublishedArticles() {
  const loaded = getPublicArticles();
  if (loaded.length > 0) return loaded;
  if (typeof DUMMY_ARTICLES !== 'undefined') return filterPublished(DUMMY_ARTICLES);
  return [];
}

function getArticleBySlug(slug) {
  return getPublicArticleBySlug(slug);
}
