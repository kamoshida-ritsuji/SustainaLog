// ============================================================
// SustainaLog — Google Sheets 読み取り＆書き込みライブラリ
// ============================================================
'use strict';

const SHEET_CONFIG = {
  SPREADSHEET_ID: '14iuJbOXao3FnwKsByAgJBzACPIPu2DtZWkhmp0frXQk',
  GAS_ENDPOINT: 'https://script.google.com/macros/s/AKfycby3ZPJ7C6EcdlVyjcQWid7hjkuGyWy2LqEq-pXSKRyJVKXMxJsVv99BZPj8fzOPhows/exec',
  ARTICLES_SHEET_NAME:  'articles',
  COMPANIES_SHEET_NAME: 'companies',
  TIMEOUT_MS: 8000,
};

function buildCsvUrl(sheetName) {
  return 'https://docs.google.com/spreadsheets/d/' + SHEET_CONFIG.SPREADSHEET_ID + '/gviz/tq?tqx=out:csv&sheet=' + encodeURIComponent(sheetName);
}

function parseCsv(text) {
  const rows = [];
  let row = [], field = '', inQuotes = false, i = 0;
  while (i < text.length) {
    const ch = text[i], next = text[i + 1];
    if (inQuotes) {
      if (ch === '"' && next === '"') { field += '"'; i += 2; }
      else if (ch === '"') { inQuotes = false; i++; }
      else { field += ch; i++; }
    } else {
      if (ch === '"') { inQuotes = true; i++; }
      else if (ch === ',') { row.push(field); field = ''; i++; }
      else if (ch === '\r' && next === '\n') { row.push(field); rows.push(row); row = []; field = ''; i += 2; }
      else if (ch === '\n' || ch === '\r') { row.push(field); rows.push(row); row = []; field = ''; i++; }
      else { field += ch; i++; }
    }
  }
  if (field || row.length > 0) { row.push(field); if (row.some(f => f !== '')) rows.push(row); }
  return rows;
}

function csvToObjects(rows) {
  if (!rows || rows.length < 2) return [];
  const headers = rows[0].map(h => h.trim());
  return rows.slice(1).filter(r => r.some(c => c.trim() !== '')).map(row => {
    const obj = {}; headers.forEach((h, i) => { obj[h] = (row[i] || '').trim(); }); return obj;
  });
}

async function fetchWithTimeout(url, ms) {
  const ctrl = new AbortController();
  const t = setTimeout(() => ctrl.abort(), ms);
  try { const r = await fetch(url, { signal: ctrl.signal }); clearTimeout(t); return r; }
  catch(e) { clearTimeout(t); throw e; }
}

async function fetchArticlesFromSheets() {
  if (!SHEET_CONFIG.SPREADSHEET_ID || SHEET_CONFIG.SPREADSHEET_ID === 'YOUR_SPREADSHEET_ID_HERE') {
    console.warn('[SheetsAPI] SPREADSHEET_ID未設定。');
    return { data: typeof DUMMY_ARTICLES !== 'undefined' ? DUMMY_ARTICLES : [], error: 'SPREADSHEET_ID未設定', source: 'fallback' };
  }
  try {
    const res = await fetchWithTimeout(buildCsvUrl(SHEET_CONFIG.ARTICLES_SHEET_NAME), SHEET_CONFIG.TIMEOUT_MS);
    if (!res.ok) throw new Error('HTTP ' + res.status);
    const text = await res.text();
    if (text.includes('<!DOCTYPE') || text.includes('<html')) throw new Error('シートが非公開です。');
    const valid = csvToObjects(parseCsv(text)).map(r => normalizeFromSheets(r)).filter(a => a.article_id && a.translated_title);
    console.info('[SheetsAPI] ' + valid.length + '件取得');
    return { data: valid, error: null, source: 'sheets' };
  } catch(err) {
    console.error('[SheetsAPI] 取得エラー:', err.message);
    return { data: typeof DUMMY_ARTICLES !== 'undefined' ? DUMMY_ARTICLES : [], error: err.message, source: 'fallback' };
  }
}

async function fetchCompaniesFromSheets() {
  if (!SHEET_CONFIG.SPREADSHEET_ID || SHEET_CONFIG.SPREADSHEET_ID === 'YOUR_SPREADSHEET_ID_HERE') {
    return { data: typeof COMPANY_MASTER !== 'undefined' ? COMPANY_MASTER : [], error: 'SPREADSHEET_ID未設定' };
  }
  try {
    const res = await fetchWithTimeout(buildCsvUrl(SHEET_CONFIG.COMPANIES_SHEET_NAME), SHEET_CONFIG.TIMEOUT_MS);
    if (!res.ok) throw new Error('HTTP ' + res.status);
    const text = await res.text();
    if (text.includes('<!DOCTYPE') || text.includes('<html')) throw new Error('非公開');
    return { data: csvToObjects(parseCsv(text)).map(r => normalizeFromSheets(r)), error: null };
  } catch(err) {
    return { data: typeof COMPANY_MASTER !== 'undefined' ? COMPANY_MASTER : [], error: err.message };
  }
}

async function updateStatusInSheets(articleId, newStatus) {
  if (!SHEET_CONFIG.GAS_ENDPOINT || SHEET_CONFIG.GAS_ENDPOINT === 'YOUR_GAS_ENDPOINT_HERE') {
    console.warn('[SheetsAPI] GAS_ENDPOINT未設定。ローカルのみ。');
    return { success: true, error: null, localOnly: true };
  }
  console.info('[SheetsAPI] updateStatus: ' + articleId + ' -> ' + newStatus);
  try {
    await fetch(SHEET_CONFIG.GAS_ENDPOINT, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'updateStatus', article_id: articleId, status: newStatus }),
      mode: 'no-cors',
    });
    console.info('[SheetsAPI] 送信完了: ' + articleId + ' -> ' + newStatus);
    return { success: true, error: null };
  } catch(err) {
    console.error('[SheetsAPI] 更新エラー:', err.message);
    return { success: false, error: err.message };
  }
}

function isSheetsConfigured() {
  return !!(SHEET_CONFIG.SPREADSHEET_ID && SHEET_CONFIG.SPREADSHEET_ID !== 'YOUR_SPREADSHEET_ID_HERE');
}

function isWriteEnabled() {
  return !!(SHEET_CONFIG.GAS_ENDPOINT && SHEET_CONFIG.GAS_ENDPOINT !== 'YOUR_GAS_ENDPOINT_HERE');
}
