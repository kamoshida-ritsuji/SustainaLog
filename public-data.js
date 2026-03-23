// ============================================================
// SustainaLog — 公開用データレイヤー
// ============================================================
// 本番サイト（index / articles / article）専甮。
// Google Sheets から published 記事だけを取得し、
// キャッシュして各ページに提供する。
//
// 読み込み順: schema.js → dummy-data.js → sheets-api.js → public-data.js → data.js
// ============================================================

'use strict';

let _publicArticles = null;
let _publicSource = 'loading';
let _publicError = null;

function ensureSlug(article) {
  if (article.slug && article.slug.trim() !== '') return article;
  const base = (article.article_id || 'article').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
  return { ...article, slug: base };
}

function filterPublished(articles) {
  return articles.filter(a => a.status === ARTICLE_STATUS.PUBLISHED && String(a.publish_flag).toUpperCase() === 'TRUE').map(ensureSlug);
}

async function loadPublicArticles() {
  if (_publicArticles !== null) return;
  if (!isSheetsConfigured()) {
    _publicArticles = filterPublished(typeof DUMMY_ARTICLES !== 'undefined' ? DUMMY_ARTICLES : []);
    _publicSource = 'fallback'; _publicError = 'SPREADSHEET_ID 朊譭定'; return;
  }
  try {
    const result = await fetchArticlesFromSheets();
    _publicArticles = filterPublished(result.data || []);
    _publicSource = result.source || 'sheets'; _publicError = result.error || null;
    console.info('[PublicData]', _publicArticles.length, '六阯記事込み中');
  } catch (err) {
    console.error('[PublicData]取得権向:', err.message);
    _publicArticles = filterPublished(typeof DUMMY_ARTICLES !== 'undefined' ? DUMMY_ARTICLES : []);
    _publicSource = 'fallback'; _publicError = err.message;
  }
}

function getPublicArticles() { return _publicArticles === null ? [] : _publicArticles; }
function getPublicArticleBySlug(s) { return getPublicArticles().find(a => a.slug === s) || null; }
function getPublicArticlesByCsrType(t) { return getPublicArticles().filter(a => a.csr_type === t); }
function getPublicArticlesByCompany(n) { return getPublicArticles().filter(a => a.company_name === n); }
function getPublicDataSource() { return { source: _publicSource, error: _publicError }; }

async function initPublicPage(mountId, onLoad) {
  const el = document.getElementById(mountId);
  if (el) el.innerHTML = '<div style="text-align:center;padding:64px 0;"><div style="width:36px;height:36px;border:3px solid var(--ink-100);border-top-color:var(--green-500);border-radius:50%;animation:spin .7s linear infinite;margin:0 auto 16px;"></div></div>';
  await loadPublicArticles();
  onLoad(getPublicArticles());
}

function getPublishedArticles() {
  const l = getPublicArticles();
  if (l.length > 0) return l;
  return typeof DUMMY_ARTICLES !== 'undefined' ? filterPublished(DUMMY_ARTICLES) : [];
}
function getArticleBySlug(s) { return getPublicArticleBySlug(s); }

// 朂業�f�計
function getCompanySummaries() {
  const articles = getPublicArticles();
  if (articles.length === 0) {
    if (typeof COMPANY_MASTER !== 'undefined')
      return COMPANY_MASTER.map(c => ({...c,article_count:0,avg_score:0,themes:[],latest_date:null,articles:[]}));
    return [];
  }
  const map = {};
  articles.forEach(a => {
    const key = a.company_name; if (!key) return;
    if (!map[key]) {
      const m = typeof COMPANY_MASTER !== 'undefined'
        ? COMPANY_MASTER.find(c => c.company_name===key||(c.aliases&&c.aliases.includes(key))) : null;
      map[key] = {company_name:key,ticker:a.ticker||(m&&m.ticker)||null,market:a.market||(m&&m.market)||null,industry:a.industry||(m&&m.industry)||'',icon:(m&&m.icon)||'🏢',official_url:(m&&m.official_url)||null,sustainability_url:(m&&m.sustainability_url)||null,ir_url:(m&&m.ir_url)||null,articles:[],scores:[],theme_count:{}};
    }
    map[key].articles.push(a);
    if (a.total_score) map[key].scores.push(Number(a.total_score)||0);
    const t = a.csr_type; if (t) map[key].theme_count[t] = (map[key].theme_count[t]||0)+1;
  });
  return Object.values(map).map(c => {
    const sorted=c.articles.slice().sort((a,b)=>(b.published_at||b.fetched_at||'')>(a.published_at||a.fetched_at||'')?1:-1);
    const avg=c.scores.length?Math.round(c.scores.reduce((s,v)=>s+v,0)/c.scores.length):0;
    const themes=Object.entries(c.theme_count).sort((a,b)=>b[1]-a[1]).slice(0,4).map(e=>e[0]);
    const latest=sorted[0]?(sorted[0].published_at||sorted[0].fetched_at||null):null;
    return {company_name:c.company_name,ticker:c.ticker,industry:c.industry,market:c.market,icon:c.icon,official_url:c.official_url,sustainability_url:c.sustainability_url,ir_url:c.ir_url,article_count:c.articles.length,avg_score:avg,themes:themes,latest_date:latest,articles:sorted};
  }).sort((a,b)=>b.article_count-a.article_count);
}
function getCompanySummaryByName(n) { return getCompanySummaries().find(c=>c.company_name===n)||null; }
function getCompanySummariesByIndustry(i) { return getCompanySummaries().filter(c=>c.industry===i); }

// テーマi��計
function getThemeSummaries() {
  const articles = getPublicArticles();
  const meta = (typeof CSR_TYPE_META !== 'undefined') ? CSR_TYPE_META : {};
  const map = {};
  Object.keys(meta).forEach(t => { map[t] = {articles:[],scores:[],companies:new Set()}; });
  articles.forEach(a => {
    const t=a.csr_type; if(!t)return;
    if(!map[t])map[t]={articles:[],scores:[],companies:new Set()};
    map[t].articles.push(a);
    if(a.total_score)map[t].scores.push(Number(a.total_score)||0);
    if(a.company_name)map[t].companies.add(a.company_name);
  });
  return Object.entries(map).map(([name,c])=>{
    const m=meta[name]||{icon:'📋',color:'#f5f5f5',accent:'#888888'};
    const sorted=c.articles.slice().sort((a,b)=>(b.published_at||b.fetched_at||'')>(a.published_at||a.fetched_at||'')?1:-1);
    const avg=c.scores.length?Math.round(c.scores.reduce((s,v)=>s+v,0)/c.scores.length):0;
    return {name,icon:m.icon,color:m.color,accent:m.accent,article_count:c.articles.length,avg_score:avg,companies:[...c.companies],articles:sorted,latest_date:sorted[0]?(sorted[0].published_at||sorted[0].fetched_at||null):null};
  }).sort((a,b)=>b.article_count-a.article_count);
}
function getThemeSummaryByName(n) { return getThemeSummaries().find(t=>t.name===n)||null; }
