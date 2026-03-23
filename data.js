// ================================================
// SustainaLog — Dummy Data & Utilities
// ================================================

const ARTICLES = [
  {
    slug: "toyota-carbon-neutral-2050",
    title: "トヨタ自動車、2050年カーボンニュートラル達成に向けた新ロードマップを発表",
    company: "トヨタ自動車",
    industry: "自動車",
    themes: ["気候変動・脱炭素", "製品・技術革新"],
    summary: "トヨタ自動車は2050年までにカーボンニュートラルを達成するための詳細なロードマップを発表した。2030年までにEV・FCVを合計350万台以上販売する目標を掲げ、バッテリーや水素技術への投資を大幅に拡大する方針を示した。また、サプライチェーン全体でのCO2削減に向けてサプライヤーとの連携強化も明言した。",
    aiComment: "本活動はパリ協定の1.5℃目標に整合する取組みと評価できます。特にサプライチェーン全体を含むScope3排出量の削減に踏み込んでいる点は、同業他社と比較しても先進的な姿勢です。水素技術との組み合わせによりトランジションリスクを分散させている点も注目に値します。ただし、中期目標（2030年）の具体的な検証手段の開示が今後の課題となるでしょう。",
    sourceUrl: "https://global.toyota/jp/sustainability/",
    sourceName: "トヨタ自動車 サステナビリティサイト",
    publishedAt: "2024-11-15",
    featured: true,
  },
  {
    slug: "sony-ocean-plastic-packaging",
    title: "ソニーグループ、製品包装材の100%サステナブル素材化を2025年までに実現へ",
    company: "ソニーグループ",
    industry: "電機・精密機器",
    themes: ["循環経済・プラスチック削減", "製品・技術革新"],
    summary: "ソニーグループは全製品の包装材を2025年度末までに100%サステナブル素材（再生紙・植物由来プラスチック・海洋プラスチック再生材など）へ切り替えると発表した。すでに国内主要製品では新素材の採用が進んでおり、海外展開も加速する。",
    aiComment: "単なる「環境対応」にとどまらず、サプライヤー評価基準にサステナブル調達を組み込む点が注目されます。消費者の購買意欲にも直接訴えられるため、ブランド価値向上にも寄与する可能性が高いと見られます。",
    sourceUrl: "https://www.sony.com/ja/SonyInfo/csr/",
    sourceName: "ソニーグループ CSRレポート",
    publishedAt: "2024-10-22",
    featured: false,
  },
  {
    slug: "recruit-digital-inclusion",
    title: "リクルートホールディングス、デジタルデバイド解消に向けた無料IT教育プログラムを全国展開",
    company: "リクルートホールディングス",
    industry: "サービス・HR",
    themes: ["教育・人材育成", "デジタル包摂"],
    summary: "リクルートHDは、デジタルスキルを持たない求職者や高齢者を対象に無料のITリテラシー教育プログラムを開始した。全国47都道府県のハローワークおよびオンラインで受講可能とし、初年度10万人の受講を目指す。",
    aiComment: "労働市場の「デジタル格差」は社会課題として急速に顕在化しており、本施策は自社の事業ドメイン（人材サービス）と社会貢献が直接連動するビジネスモデル型CSRの好例です。ESG投資家からの評価向上にも寄与する可能性があります。",
    sourceUrl: "https://recruit-holdings.com/ja/sustainability/",
    sourceName: "リクルートホールディングス サステナビリティ",
    publishedAt: "2024-09-30",
    featured: false,
  },
  {
    slug: "mizuho-green-bond",
    title: "みずほフィナンシャルグループ、国内最大級グリーンボンド5000億円を発行",
    company: "みずほフィナンシャルグループ",
    industry: "金融・銀行",
    themes: ["ESG金融", "気候変動・脱炭素"],
    summary: "みずほFGは再生可能エネルギーや省エネ事業向けのグリーンボンドを5000億円規模で発行すると発表した。調達資金は国内外の太陽光・洋上風力発電プロジェクトへの融資に充当される。ICMAグリーンボンド原則に準拠しており、第三者検証も実施済み。",
    aiComment: "金融機関によるグリーンボンド発行は、実体経済のサステナビリティ移行を金融面から支える「触媒機能」として重要です。グリーンウォッシングリスクを避けるため第三者検証を徹底している点は評価できます。",
    sourceUrl: "https://www.mizuho-fg.co.jp/sustainability/",
    sourceName: "みずほフィナンシャルグループ サステナビリティ",
    publishedAt: "2024-09-10",
    featured: false,
  },
  {
    slug: "panasonic-biodiversity",
    title: "パナソニック、国内工場敷地での生物多様性保全プロジェクトを開始",
    company: "パナソニックホールディングス",
    industry: "電機・精密機器",
    themes: ["生物多様性", "地域社会・コミュニティ"],
    summary: "パナソニックは全国15か所の工場・研究所の緑地を活用し、在来植物の保護・育成や昆虫モニタリングを行う生物多様性保全プロジェクトを開始した。TNFD（自然関連財務情報開示タスクフォース）フレームワークに基づく情報開示も進める予定。",
    aiComment: "TNFDへの対応は日本企業では先進的な取組みであり、2030年のネイチャーポジティブ目標に向けた自然資本リスク管理の好事例です。従業員参加型のプログラムとしてエンゲージメント向上にも貢献する構造となっています。",
    sourceUrl: "https://holdings.panasonic/jp/corporate/sustainability.html",
    sourceName: "パナソニック サステナビリティ",
    publishedAt: "2024-08-20",
    featured: false,
  },
  {
    slug: "familymart-food-loss",
    title: "ファミリーマート、食品ロス削減に向けAIを活用した発注最適化システムを全店導入",
    company: "ファミリーマート",
    industry: "小売・コンビニ",
    themes: ["食品ロス削減", "AI・テクノロジー活用"],
    summary: "ファミリーマートは独自開発のAI発注支援システムを全国約16,000店舗に展開完了した。リアルタイムの天気・イベント情報と販売データを組み合わせた需要予測により、食品廃棄ロスを従来比で約20%削減することを目指す。",
    aiComment: "小売業における食品ロスはサプライチェーン全体のCO2排出にも直結する重大課題です。AI活用による構造的解決策は、単発のキャンペーン型CSRとは異なり持続的な効果が期待できます。フランチャイジーへの展開が鍵となるでしょう。",
    sourceUrl: "https://www.family.co.jp/sustainability.html",
    sourceName: "ファミリーマート サステナビリティ",
    publishedAt: "2024-08-05",
    featured: false,
  },
  {
    slug: "asahi-water-stewardship",
    title: "アサヒグループ、水資源保全に向けた「ウォーター・スチュワードシップ」戦略を策定",
    company: "アサヒグループホールディングス",
    industry: "食品・飲料",
    themes: ["水・資源保全", "気候変動・脱炭素"],
    summary: "アサヒグループHDは2030年に向けた水資源保全戦略を発表。水ストレスの高い地域にある工場での取水量削減、地域コミュニティとの集水域管理、そしてAWS（アライアンス・フォー・ウォーター・スチュワードシップ）認証取得を進める。",
    aiComment: "飲料業界にとって水は事業基盤そのものであり、水リスク管理はビジネス継続性に直結します。AWSなどの国際的な認証基準を活用することで、グローバル投資家への信頼性も担保できる設計となっています。",
    sourceUrl: "https://www.asahigroup-holdings.com/sustainability/",
    sourceName: "アサヒグループ サステナビリティ",
    publishedAt: "2024-07-18",
    featured: false,
  },
  {
    slug: "ntt-renewable-energy-100",
    title: "NTTグループ、2030年までに使用電力の100%を再生可能エネルギーで賄う目標を設定",
    company: "NTTグループ",
    industry: "通信・IT",
    themes: ["気候変動・脱炭素", "ESG金融"],
    summary: "NTTグループはRE100に加盟し、2030年までに国内外のグループ全体で使用電力を再生可能エネルギー100%にする目標を設定した。自社での太陽光・風力発電所の開発に加え、コーポレートPPAによる長期調達も組み合わせる。データセンターの省エネ化も並行して推進する。",
    aiComment: "通信・データセンター業界は世界の電力消費の2〜3%を占めるとされており、大規模なRE100達成は業界全体への波及効果が期待できます。自社開発＋PPA組み合わせ戦略は調達リスク分散の観点からも適切な設計です。",
    sourceUrl: "https://www.ntt.com/about-us/csr.html",
    sourceName: "NTTグループ CSR・環境",
    publishedAt: "2024-06-28",
    featured: false,
  },
];

const COMPANIES = [
  { name: "トヨタ自動車",         industry: "自動車",       count: 12, icon: "🚗" },
  { name: "ソニーグループ",       industry: "電機・精密",   count: 9,  icon: "🎮" },
  { name: "リクルートHD",         industry: "サービス",     count: 7,  icon: "💼" },
  { name: "みずほFG",             industry: "金融・銀行",   count: 6,  icon: "🏦" },
  { name: "パナソニックHD",       industry: "電機・精密",   count: 8,  icon: "⚡" },
  { name: "ファミリーマート",     industry: "小売",         count: 5,  icon: "🏪" },
  { name: "アサヒグループHD",     industry: "食品・飲料",   count: 4,  icon: "🍺" },
  { name: "NTTグループ",          industry: "通信・IT",     count: 11, icon: "📡" },
];

const THEMES = [
  { name: "気候変動・脱炭素",     icon: "🌡️",  count: 24, color: "#d8f3dc", accent: "#2d6a4f" },
  { name: "循環経済・廃棄物削減", icon: "♻️",  count: 18, color: "#fef9ef", accent: "#c9a84c" },
  { name: "生物多様性",           icon: "🌿",  count: 11, color: "#e8f4ec", accent: "#40916c" },
  { name: "ESG金融",              icon: "📊",  count: 15, color: "#f0f4ff", accent: "#3b64c8" },
  { name: "教育・人材育成",       icon: "🎓",  count: 9,  color: "#fff3f0", accent: "#b5522a" },
  { name: "水・資源保全",         icon: "💧",  count: 8,  color: "#e8f6ff", accent: "#2b6cb0" },
];

// ================================================
// Utilities
// ================================================

function formatDate(dateStr) {
  const d = new Date(dateStr);
  return d.toLocaleDateString('ja-JP', { year: 'numeric', month: 'long', day: 'numeric' });
}

function getArticleBySlug(slug) {
  return ARTICLES.find(a => a.slug === slug) || null;
}

function renderCardImgPlaceholder(themes) {
  const colors = {
    "気候変動・脱炭素": ["#1f5235","#40916c"],
    "循環経済・プラスチック削減": ["#5c4a1a","#c9a84c"],
    "生物多様性": ["#1a3a2e","#52b788"],
    "ESG金融": ["#1a2a4a","#4a7fd4"],
    "教育・人材育成": ["#4a1a1a","#c85a2a"],
    "水・資源保全": ["#1a2a4a","#4a90c8"],
    "食品ロス削減": ["#3a2a1a","#c8882a"],
    "地域社会・コミュニティ": ["#2a1a3a","#8a5ac8"],
    "デジタル包摂": ["#1a2a2a","#3ab8b8"],
    "AI・テクノロジー活用": ["#1a1a2a","#6a5acd"],
    "製品・技術革新": ["#2a1a2a","#c85ac8"],
  };
  const theme = themes[0] || "";
  const [c1, c2] = colors[theme] || ["#1f5235","#40916c"];
  const emoji = { "気候変動・脱炭素":"🌱","循環経済・プラスチック削減":"♻️","生物多様性":"🌿","ESG金融":"📈","教育・人材育成":"🎓","水・資源保全":"💧","食品ロス削減":"🍱","地域社会・コミュニティ":"🤝","デジタル包摂":"💻","AI・テクノロジー活用":"🤖","製品・技術革新":"⚙️" };
  const icon = emoji[theme] || "🌏";
  return `<div style="background:linear-gradient(135deg,${c1},${c2});width:100%;height:100%;display:flex;align-items:center;justify-content:center;font-size:3rem;">${icon}</div>`;
}

function renderCard(article) {
  const themeTagsHtml = article.themes.map(t =>
    `<span class="tag tag-theme">${t}</span>`
  ).join('');
  return `
    <a href="article.html?slug=${article.slug}" class="card animate-in">
      <div class="card-img-wrap">
        ${renderCardImgPlaceholder(article.themes)}
      </div>
      <div class="card-body">
        <div class="card-meta">
          <span class="tag tag-company">${article.company}</span>
          <span class="tag tag-industry">${article.industry}</span>
        </div>
        ${themeTagsHtml}
        <h3 class="card-title" style="margin-top:8px">${article.title}</h3>
        <p class="card-summary">${article.summary}</p>
        <div class="card-footer">
          <span class="card-date">${formatDate(article.publishedAt)}</span>
          <span class="card-source">${article.sourceName}</span>
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
    `<a href="${p.href}" class="nav-link${activePage===p.href?' active':''}">${p.label}</a>`
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
              <a href="themes.html">気候変動・脱炭素</a>
              <a href="themes.html">循環経済</a>
              <a href="themes.html">生物多様性</a>
              <a href="themes.html">ESG金融</a>
              <a href="themes.html">教育・人材</a>
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
  nav.classList.toggle('open');
}

// Intersection Observer for scroll animations
function initScrollAnimations() {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.style.animationPlayState = 'running';
      }
    });
  }, { threshold: 0.1 });

  document.querySelectorAll('.animate-in').forEach(el => {
    el.style.animationPlayState = 'paused';
    observer.observe(el);
  });
}

document.addEventListener('DOMContentLoaded', () => {
  initScrollAnimations();
});
