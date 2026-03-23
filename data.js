// ============================================================
// SustainaLog — UI Rendering Functions
// ============================================================
// このファイルはUIレンダリング関数のみを持ちます。
// データは dummy-data.js、型定義は schema.js を参照。
//
// 読み込み順: schema.js → dummy-data.js → data.js
// ============================================================

'use strict';

function formatDate(dateStr) {
  if (!dateStr) return '—';
  const d = new Date(dateStr);
  return d.toLocaleDateString('ja-JP', { year: 'numeric', month: 'long', day: 'numeric' });
}

function renderCardImgPlaceholder(csrType) {
  const gradients = {
    '環境':           ['#1f5235','#40916c'],
    '地域貢献':       ['#2a1a3a','#8a5ac8'],
    '教育支援':       ['#4a1a1a','#c85a2a'],
    '災害支援':       ['#4a1a1a','#c0392b'],
    '人材育成':       ['#1a3a2e','#52b788'],
    'DEI':            ['#3a1a4a','#9b59b6'],
    '健康経営':       ['#3a2a1a','#e67e22'],
    '人権':           ['#1a2a4a','#3b64c8'],
    'サプライチェーン':['#2a2a2a','#888888'],
    'ガバナンス':     ['#1a1a2a','#555555'],
    'その他':         ['#2a2a2a','#888888'],
  };
  const meta = (typeof CSR_TYPE_META !== 'undefined' && CSR_TYPE_META[csrType]) || {};
  const [c1, c2] = gradients[csrType] || ['#1f5235','#40916c'];
  const icon = meta.icon || '🌏';
  return `<div style="background:linear-gradient(135deg,${c1},${c2});width:100%;height:100%;display:flex;align-items:center;justify-content:center;font-size:3rem;">${icon}</div>`;
}

function renderScoreBar(total) {
  const rank = (typeof scoreToRank === 'function') ? scoreToRank(total) : { label: '-', color: '#888' };
  const max  = (typeof SCORE_MAX_TOTAL !== 'undefined') ? SCORE_MAX_TOTAL : 25;
  const pct  = Math.round((total / max) * 100);
  return `
    <div style="display:flex;align-items:center;gap:8px;">
      <span style="font-family:var(--font-mono);font-weight:700;font-size:0.9rem;color:${rank.color};min-width:20px;">${rank.label}</span>
      <div style="flex:1;height:6px;background:var(--ink-100);border-radius:3px;overflow:hidden;">
        <div style="width:${pct}%;height:100%;background:${rank.color};border-radius:3px;"></div>
      </div>
      <span style="font-family:var(--font-mono);font-size:0.75rem;color:var(--ink-300);">${total}/${max}</span>
    </div>
  `;
}

function renderStatusBadge(status) {
  const map = (typeof ARTICLE_STATUS_LABEL !== 'undefined') ? ARTICLE_STATUS_LABEL : {};
  const s = map[status] || { label: status, color: '#888', bg: '#f0f0f0' };
  return `<span style="font-size:0.7rem;font-weight:700;padding:3px 9px;border-radius:99px;background:${s.bg};color:${s.color};">${s.label}</span>`;
}

function renderCard(article) {
  const total   = article.total_score || 0;
  const rank    = (typeof scoreToRank === 'function') ? scoreToRank(total) : { label: '-', color: '#888' };
  const csrMeta = (typeof CSR_TYPE_META !== 'undefined' && CSR_TYPE_META[article.csr_type]) || {};
  const relMap  = (typeof RELATION_TYPE_LABEL !== 'undefined') ? RELATION_TYPE_LABEL : {};
  const relLabel= relMap[article.relation_type] || null;
  const slug    = article.slug;
  const name    = article.company_name || article.company || '';
  const industry= article.industry || '';
  const title   = article.translated_title || article.title || '';
  const summary = article.summary || '';
  const date    = article.published_at || article.publishedAt || '';
  const src     = article.source_name || article.sourceName || '';

  return `
    <a href="article.html?slug=${slug}" class="card animate-in">
      <div class="card-img-wrap">
        ${renderCardImgPlaceholder(article.csr_type)}
      </div>
      <div class="card-body">
        <div class="card-meta">
          <a href="company.html?name=${encodeURIComponent(name)}" class="tag tag-company" onclick="event.preventDefault();event.stopPropagation();location.href=this.href;">${name}</a>
          <span class="tag tag-industry">${industry}</span>
          ${relLabel ? `<span class="tag" style="background:rgba(0,0,0,0.05);color:${relLabel.color};font-size:0.68rem;">${relLabel.label}</span>` : ''}
        </div>
        <div style="display:flex;gap:6px;flex-wrap:wrap;margin-bottom:4px;">
          <span class="tag tag-theme" style="background:${csrMeta.color||'#d8f3dc'};color:${csrMeta.accent||'#2d6a4f'};" onclick="event.preventDefault();event.stopPropagation();location.href='theme.html?name='+encodeURIComponent('${article.csr_type||''}');cursor:pointer;">
            ${csrMeta.icon||''} ${article.csr_type||''}
          </span>
          ${article.csr_subtype ? `<span class="tag" style="background:var(--cream);color:var(--ink-500);font-size:0.68rem;">${article.csr_subtype}</span>` : ''}
        </div>
        <h3 class="card-title" style="margin-top:8px">${title}</h3>
        <p class="card-summary">${summary}</p>
        <div style="margin-top:12px;">${renderScoreBar(total)}</div>
        <div class="card-footer">
          <span class="card-date">${formatDate(date)}</span>
          <span class="card-source">${src}</span>
          <span class="read-more">読む →</span>
        </div>
      </div>
    </a>
  `;
}

function renderHeader(activePage = '') {
  const pages = [
    { href: 'index.html',     label: '最新情報' },
    { href: 'articles.html',  label: '記事一覧' },
    { href: 'companies.html', label: '企業別' },
    { href: 'themes.html',    label: 'テーマ別' },
    { href: 'about.html',     label: 'About' },
  ];
  const navHtml = pages.map(p =>
    `<a href="${p.href}" class="nav-link${activePage === p.href ? ' active' : ''}">${p.label}</a>`
  ).join('');
  const mobileNavHtml = pages.map(p =>
    `<a href="${p.href}" class="mobile-nav-link">${p.label}</a>`
  ).join('');
  return `
    <header class="site-header">
      <div class="container">
        <div class="header-inner">
          <a href="index.html" class="site-logo">
            <span class="logo-main">SustainaLog</span>
            <span class="logo-badge">β</span>
          </a>
          <nav class="site-nav">${navHtml}</nav>
          <a href="articles.html" class="header-cta">記事を探す</a>
          <button class="hamburger" aria-label="メニュー" onclick="toggleMobileNav()">
            <span></span><span></span><span></span>
          </button>
        </div>
      </div>
      <nav class="mobile-nav" id="mobileNav">${mobileNavHtml}</nav>
    </header>
  `;
}

function renderFooter() {
  return `
    <footer class="site-footer">
      <div class="container">
        <div class="footer-main">
          <div class="footer-brand">
            <a href="index.html" class="site-logo">
              <span class="logo-main">SustainaLog</span>
              <span class="logo-badge">β</span>
            </a>
            <p class="footer-desc">国内上場企業のCSR・サステナビリティ・社会貢献活動を収集・整理・可視化する情報プラットフォーム。</p>
          </div>
          <div>
            <div class="footer-col-title">コンテンツ</div>
            <div class="footer-links">
              <a href="articles.html">記事一覧</a>
              <a href="companies.html">企業別</a>
              <a href="themes.html">テーマ別</a>
            </div>
          </div>
          <div>
            <div class="footer-col-title">サイト情報</div>
            <div class="footer-links">
              <a href="about.html">About</a>
              <a href="#">お問い合わせ</a>
              <a href="#">プライバシーポリシー</a>
            </div>
          </div>
          <div>
            <div class="footer-col-title">テーマ</div>
            <div class="footer-links">
              <a href="themes.html">環境</a>
              <a href="themes.html">地域貢献</a>
              <a href="themes.html">教育支援</a>
              <a href="themes.html">DEI</a>
              <a href="themes.html">ガバナンス</a>
            </div>
          </div>
        </div>
        <div class="footer-bottom">
          <p class="footer-copy">© 2024 SustainaLog. All rights reserved.</p>
          <div class="footer-tags">
            <span class="footer-tag">CSR</span>
            <span class="footer-tag">サステナビリティ</span>
            <span class="footer-tag">ESG</span>
            <span class="footer-tag">社会貢献</span>
          </div>
        </div>
      </div>
    </footer>
  `;
}

function toggleMobileNav() {
  const nav = document.getElementById('mobileNav');
  if (nav) nav.classList.toggle('open');
}

function initScrollAnimations() {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) entry.target.style.animationPlayState = 'running';
    });
  }, { threshold: 0.08 });
  document.querySelectorAll('.animate-in').forEach(el => {
    el.style.animationPlayState = 'paused';
    observer.observe(el);
  });
}

document.addEventListener('DOMContentLoaded', () => { initScrollAnimations(); });
