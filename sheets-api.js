'use strict';
const SHEET_CONFIG = {
  SPREADSHEET_ID: '13gnNz6wLTOOVF66V0fVT489drmmZF6J_0nGo4cTXQm0',
  GAS_ENDPOINT: 'https://script.google.com/macros/s/AKfycbyjr9un3qZYaFSPFxkgE3Ii_XKYoBh3OZK3SKVjekkcxaPD4Ssp1UP9Q7oCEnO9aL35OA/exec',
  ARTICLES_SHEET_NAME: 'articles',
  COMPANIES_SHEET_NAME: 'companies',
  TIMEOUT_MS: 10000,
};
async function fetchArticlesFromSheets() {
  if (!SHEET_CONFIG.GAS_ENDPOINT || SHEET_CONFIG.GAS_ENDPOINT === 'YOUR_GAS_ENDPOINT_HERE') {
    return { data: typeof DUMMY_ARTICLES !== 'undefined' ? DUMMY_ARTICLES : [], source: 'fallback', error: 'GAS未設定' };
  }
  try {
    const ctrl = new AbortController();
    const timer = setTimeout(() => ctrl.abort(), SHEET_CONFIG.TIMEOUT_MS);
    const resp = await fetch(SHEET_CONFIG.GAS_ENDPOINT + '?sheet=articles', { signal: ctrl.signal });
    clearTimeout(timer);
    if (!resp.ok) throw new Error('HTTP ' + resp.status);
    const json = await resp.json();
    if (json.error) throw new Error(json.error);
    return { data: json.articles || [], source: 'sheets', error: null };
  } catch (e) {
    return { data: typeof DUMMY_ARTICLES !== 'undefined' ? DUMMY_ARTICLES : [], source: 'fallback', error: e.message };
  }
}
async function fetchCompaniesFromSheets() {
  try {
    const resp = await fetch(SHEET_CONFIG.GAS_ENDPOINT + '?sheet=companies');
    const json = await resp.json();
    return { data: json.articles || [], source: 'sheets' };
  } catch (e) {
    return { data: typeof COMPANY_MASTER !== 'undefined' ? COMPANY_MASTER : [], source: 'fallback' };
  }
}
async function updateStatusInSheets(articleId, newStatus) {
  try {
    const resp = await fetch(SHEET_CONFIG.GAS_ENDPOINT, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'updateStatus', article_id: articleId, status: newStatus }),
    });
    const json = await resp.json();
    if (json.error) throw new Error(json.error);
    return { success: true };
  } catch (e) {
    return { success: false, error: e.message };
  }
}
function isSheetsConfigured() {
  return !!(SHEET_CONFIG.GAS_ENDPOINT && SHEET_CONFIG.GAS_ENDPOINT !== 'YOUR_GAS_ENDPOINT_HERE');
}
function isWriteEnabled() {
  return isSheetsConfigured();
}
