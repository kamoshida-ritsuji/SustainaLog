// ==============================================
// SustainaLog — Google Sheets 読み取り&書き込みライブラリ
// ==============================================
'use strict';

const SHEET_CONFIG = {
  SPREADSHEET_ID: '13gnNz6wLTOOVF66V0fVT489drmmZF6J_0nGo4cTXQm0',
  GAS_ENDPOINT: 'https://script.google.com/macros/s/AKfycbyjr9un3qZYaFSPFxkgE3Ii_XKYoBh3OZK3SKVjekkcxaPD4Ssp1UP9Q7oCEnO9aL35OA/exec',
  ARTICLES_SHEET_NAME: 'articles',
  COMPANIES_SHEET_NAME: 'companies',
  TIMEOUT_MS: 10000,
};

// GAS経由でarticlesを取得
async function fetchArticlesFromSheets() {
  if (!SHEET_CONFIG.GAS_ENDPOINT || SHEET_CONFIG.GAS_ENDPOINT === 'YOUR_GAS_ENDPOINT_HERE') {
    console.warn('[SheetsAPI] GAS_ENDPOINT未設定。ローカルのみ。');
    return { data: typeof DUMMY_ARTICLES !== 'undefined' ? DUMMY_ARTICLES : [], source: 'fallback', error: 'GAS_ENDPOINT未設定' };
  }
  try {
    const url = SHEET_CONFIG.GAS_ENDPOINT + '?sheet=articles';
    const ctrl = new AbortController();
    const timer = setTimeout(() => ctrl.abort(), SHEET_CONFIG.TIMEOUT_MS);
    const resp = await fetch(url, { signal: ctrl.signal });
    clearTimeout(timer);
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    const json = await resp.json();
    if (json.error) throw new Error(json.error);
    const articles = json.articles || [];
    console.log(`[SheetsAPI] GAS経由で${articles.length}件取得`);
    return { data: articles, source: 'sheets', error: null };
  } catch (e) {
    console.warn('[SheetsAPI] GAS取得エラー:', e.message);
    return { data: typeof DUMMY_ARTICLES !== 'undefined' ? DUMMY_ARTICLES : [], source: 'fallback', error: e.message };
  }
}

// GAS経由でステータス更新
async function updateStatusInSheets(articleId, newStatus) {
  if (!SHEET_CONFIG.GAS_ENDPOINT || SHEET_CONFIG.GAS_ENDPOINT === 'YOUR_GAS_ENDPOINT_HERE') {
    return { success: false, error: 'GAS_ENDPOINT未設定' };
  }
  try {
    const resp = await fetch(SHEET_CONFIG.GAS_ENDPOINT, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'updateStatus', article_id: articleId, status: newStatus }),
    });
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    const json = await resp.json();
    if (json.error) throw new Error(json.error);
    return { success: true };
  } catch (e) {
    console.warn('[SheetsAPI] updateStatus エラー:', e.message);
    return { success: false, error: e.message };
  }
}

// GAS経由でcompaniesを取得
async function fetchCompaniesFromSheets() {
  if (!SHEET_CONFIG.GAS_ENDPOINT || SHEET_CONFIG.GAS_ENDPOINT === 'YOUR_GAS_ENDPOINT_HERE') {
    return { data: typeof COMPANY_MASTER !== 'undefined' ? COMPANY_MASTER : [], source: 'fallback' };
  }
  try {
    const url = SHEET_CONFIG.GAS_ENDPOINT + '?sheet=companies';
    const resp = await fetch(url);
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    const json = await resp.json();
    return { data: json.articles || [], source: 'sheets' };
  } catch (e) {
    return { data: typeof COMPANY_MASTER !== 'undefined' ? COMPANY_MASTER : [], source: 'fallback' };
  }
}

function isWriteEnabled() {
  return !!(SHEET_CONFIG.GAS_ENDPOINT && SHEET_CONFIG.GAS_ENDPOINT !== 'YOUR_GAS_ENDPOI

