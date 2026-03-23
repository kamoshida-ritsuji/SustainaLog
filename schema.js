// ============================================================
// SustainaLog — Schema & Type Definitions
// ============================================================
// このファイルは「型の唯一の源泉（Single Source of Truth）」です。
// Google Sheetsの列名・承認画面・分析ダッシュボードは
// すべてここの定義を参照してください。
// ============================================================

'use strict';

// ────────────────────────────────────────────
// 1. 記事ステータス定義
// Google Sheets の status 列と完全一致させること
// ────────────────────────────────────────────
const ARTICLE_STATUS = Object.freeze({
  PENDING_REVIEW: 'pending_review',  // 収集済み・未レビュー
  PUBLISHED:      'published',       // 公開済み
  REJECTED:       'rejected',        // 非掲載
});

const ARTICLE_STATUS_LABEL = Object.freeze({
  pending_review: { label: 'レビュー待ち', color: '#c9a84c', bg: '#fef9ef' },
  published:      { label: '公開中',       color: '#2d6a4f', bg: '#d8f3dc' },
  rejected:       { label: '非掲載',       color: '#9a3b1a', bg: '#fde8e0' },
});

// ────────────────────────────────────────────
// 2. CSRテーマ分類（大分類 csr_type）
// ────────────────────────────────────────────
const CSR_TYPE = Object.freeze({
  ENVIRONMENT:       '環境',
  COMMUNITY:         '地域貢献',
  EDUCATION:         '教育支援',
  DISASTER_RELIEF:   '災害支援',
  HR_DEVELOPMENT:    '人材育成',
  DEI:               'DEI',
  HEALTH:            '健康経営',
  HUMAN_RIGHTS:      '人権',
  SUPPLY_CHAIN:      'サプライチェーン',
  GOVERNANCE:        'ガバナンス',
  OTHER:             'その他',
});

// CSR大分類ごとのUI設定（アイコン・カラー）
const CSR_TYPE_META = Object.freeze({
  '環境':           { icon: '🌍', color: '#d8f3dc', accent: '#2d6a4f' },
  '地域貢献':       { icon: '🤝', color: '#f5f0ff', accent: '#6b46c1' },
  '教育支援':       { icon: '🎓', color: '#fff3f0', accent: '#b5522a' },
  '災害支援':       { icon: '🆘', color: '#fff0f0', accent: '#c0392b' },
  '人材育成':       { icon: '🌱', color: '#e8f4ec', accent: '#40916c' },
  'DEI':            { icon: '🌈', color: '#fdf0ff', accent: '#9b59b6' },
  '健康経営':       { icon: '💪', color: '#fff8ec', accent: '#e67e22' },
  '人権':           { icon: '⚖️',  color: '#f0f4ff', accent: '#3b64c8' },
  'サプライチェーン':{ icon: '🔗', color: '#f0f0f0', accent: '#555555' },
  'ガバナンス':     { icon: '🏛️',  color: '#fafafa', accent: '#333333' },
  'その他':         { icon: '📋', color: '#f5f5f5', accent: '#888888' },
});

// ────────────────────────────────────────────
// 3. CSRサブタイプ（小分類 csr_subtype）
// 大分類に対する代表的なサブカテゴリ例
// ────────────────────────────────────────────
const CSR_SUBTYPE = Object.freeze({
  // 環境
  CARBON_NEUTRAL:   '脱炭素・カーボンニュートラル',
  RENEWABLE_ENERGY: '再生可能エネルギー',
  CIRCULAR_ECONOMY: '循環経済・廃棄物削減',
  BIODIVERSITY:     '生物多様性',
  WATER:            '水資源保全',
  FOOD_LOSS:        '食品ロス削減',
  // 地域貢献
  LOCAL_REVITAL:    '地域活性化',
  COMMUNITY_INV:    'コミュニティ投資',
  // 教育支援
  DIGITAL_LITERACY: 'デジタルリテラシー',
  SCHOLARSHIP:      '奨学金・教育支援',
  // 人材育成
  RESKILLING:       'リスキリング',
  WELLBEING:        'ウェルビーイング',
  // DEI
  GENDER_EQUALITY:  'ジェンダー平等',
  DISABILITY:       '障がい者雇用',
  // ガバナンス
  ESG_DISCLOSURE:   'ESG情報開示',
  GREEN_FINANCE:    'グリーンファイナンス',
});

// ────────────────────────────────────────────
// 4. 関係性タイプ（relation_type）
// 活動が「直接」か「間接」か「寄付型」か
// ────────────────────────────────────────────
const RELATION_TYPE = Object.freeze({
  DIRECT:   'direct',    // 自社事業との直接連動
  INDIRECT: 'indirect',  // 社会貢献として独立
  DONATION: 'donation',  // 寄付・資金提供型
});

const RELATION_TYPE_LABEL = Object.freeze({
  direct:   { label: '事業直結型', color: '#2d6a4f' },
  indirect: { label: '独立貢献型', color: '#3b64c8' },
  donation: { label: '寄付・支援型', color: '#c9a84c' },
});

// ────────────────────────────────────────────
// 5. ステークホルダータイプ（stakeholder_type）
// ────────────────────────────────────────────
const STAKEHOLDER_TYPE = Object.freeze({
  INVESTOR:   'investor',    // 投資家向け
  EMPLOYEE:   'employee',    // 従業員向け
  COMMUNITY:  'community',   // 地域社会向け
  CUSTOMER:   'customer',    // 顧客向け
  SUPPLY:     'supply',      // サプライヤー向け
  GOVERNMENT: 'government',  // 行政・規制機関向け
});

// ────────────────────────────────────────────
// 6. 市場区分（market）
// ────────────────────────────────────────────
const MARKET = Object.freeze({
  PRIME:    'prime',     // 東証プライム
  STANDARD: 'standard', // 東証スタンダード
  GROWTH:   'growth',   // 東証グロース
  OTHER:    'other',    // その他・非上場傘下
});

const MARKET_LABEL = Object.freeze({
  prime:    '東証プライム',
  standard: '東証スタンダード',
  growth:   '東証グロース',
  other:    'その他',
});

// ────────────────────────────────────────────
// 7. スコア定義（5項目 × 最大5点 = 合計25点満点）
// ────────────────────────────────────────────
const SCORE_DEFINITION = Object.freeze([
  {
    key:   'score_social_clarity',
    label: '社会的明確性',
    desc:  '課題設定・受益者・変化がどれだけ明確か',
    max:   5,
  },
  {
    key:   'score_continuity',
    label: '継続性',
    desc:  '単発イベントではなく中長期的な取組みか',
    max:   5,
  },
  {
    key:   'score_business_alignment',
    label: '事業連動性',
    desc:  '自社の事業・強みと活動がどれだけ連動しているか',
    max:   5,
  },
  {
    key:   'score_specificity',
    label: '具体性',
    desc:  '数値目標・KPI・検証手段が明示されているか',
    max:   5,
  },
  {
    key:   'score_reference_value',
    label: '参考価値',
    desc:  '他社や研究者にとっての参考・モデル事例としての価値',
    max:   5,
  },
]);

const SCORE_MAX_TOTAL = 25;

// ────────────────────────────────────────────
// 8. Google Sheets 列名マッピング
// スプレッドシートの列ヘッダーとJSのキーを対応させる
// ────────────────────────────────────────────
const SHEETS_COLUMN_MAP = Object.freeze({
  // 記事テーブル（シート名: articles）
  articles: {
    article_id:             'article_id',
    slug:                   'slug',
    company_name:           'company_name',
    ticker:                 'ticker',
    market:                 'market',
    industry:               'industry',
    source_name:            'source_name',
    source_url:             'source_url',
    official_url:           'official_url',
    ir_url:                 'ir_url',
    sustainability_url:     'sustainability_url',
    source_title:           'source_title',
    translated_title:       'translated_title',
    summary:                'summary',
    ai_commentary:          'ai_commentary',
    csr_type:               'csr_type',
    csr_subtype:            'csr_subtype',
    relation_type:          'relation_type',
    stakeholder_type:       'stakeholder_type',
    classification_tags:    'classification_tags',   // カンマ区切り文字列
    score_social_clarity:   'score_social_clarity',
    score_continuity:       'score_continuity',
    score_business_alignment:'score_business_alignment',
    score_specificity:      'score_specificity',
    score_reference_value:  'score_reference_value',
    total_score:            'total_score',
    published_at:           'published_at',
    fetched_at:             'fetched_at',
    status:                 'status',
    publish_flag:           'publish_flag',          // TRUE/FALSE
  },
  // 企業マスタテーブル（シート名: companies）
  companies: {
    company_name:       'company_name',
    ticker:             'ticker',
    market:             'market',
    industry:           'industry',
    official_url:       'official_url',
    ir_url:             'ir_url',
    sustainability_url: 'sustainability_url',
    aliases:            'aliases',                   // カンマ区切り文字列
  },
});

// ────────────────────────────────────────────
// 9. バリデーション関数
// ────────────────────────────────────────────

/**
 * 記事オブジェクトの必須フィールドを検証
 * @param {Object} article
 * @returns {{ valid: boolean, errors: string[] }}
 */
function validateArticle(article) {
  const errors = [];
  const required = ['article_id','slug','company_name','industry','summary','csr_type','status'];
  required.forEach(key => {
    if (!article[key]) errors.push(`必須フィールドが未設定: ${key}`);
  });
  if (article.status && !Object.values(ARTICLE_STATUS).includes(article.status)) {
    errors.push(`不正なステータス値: ${article.status}`);
  }
  if (article.csr_type && !Object.values(CSR_TYPE).includes(article.csr_type)) {
    errors.push(`不正なCSRタイプ: ${article.csr_type}`);
  }
  const scoreTotal = (
    (Number(article.score_social_clarity)    || 0) +
    (Number(article.score_continuity)        || 0) +
    (Number(article.score_business_alignment)|| 0) +
    (Number(article.score_specificity)       || 0) +
    (Number(article.score_reference_value)   || 0)
  );
  if (article.total_score !== undefined && article.total_score !== scoreTotal) {
    errors.push(`total_scoreが各スコアの合計と一致しない (計算値: ${scoreTotal}, 設定値: ${article.total_score})`);
  }
  return { valid: errors.length === 0, errors };
}

/**
 * 企業マスタオブジェクトの必須フィールドを検証
 * @param {Object} company
 * @returns {{ valid: boolean, errors: string[] }}
 */
function validateCompany(company) {
  const errors = [];
  const required = ['company_name','industry'];
  required.forEach(key => {
    if (!company[key]) errors.push(`必須フィールドが未設定: ${key}`);
  });
  return { valid: errors.length === 0, errors };
}

/**
 * スコア合計を計算して返す
 * @param {Object} article
 * @returns {number}
 */
function calcTotalScore(article) {
  return (
    (Number(article.score_social_clarity)    || 0) +
    (Number(article.score_continuity)        || 0) +
    (Number(article.score_business_alignment)|| 0) +
    (Number(article.score_specificity)       || 0) +
    (Number(article.score_reference_value)   || 0)
  );
}

/**
 * スコアを5段階評価ラベルに変換
 * @param {number} total  0〜25
 * @returns {{ label: string, color: string }}
 */
function scoreToRank(total) {
  if (total >= 22) return { label: 'S', color: '#2d6a4f' };
  if (total >= 18) return { label: 'A', color: '#40916c' };
  if (total >= 13) return { label: 'B', color: '#c9a84c' };
  if (total >= 8)  return { label: 'C', color: '#b5522a' };
  return               { label: 'D', color: '#9a3b1a' };
}

/**
 * Google Sheets からインポートした行データを正規化する
 * classification_tags・aliases のカンマ区切り文字列を配列に変換
 * publish_flag の "TRUE"/"FALSE" 文字列をboolに変換
 * @param {Object} row
 * @returns {Object}
 */
function normalizeFromSheets(row) {
  const normalized = { ...row };
  if (typeof normalized.classification_tags === 'string') {
    normalized.classification_tags = normalized.classification_tags
      .split(',').map(s => s.trim()).filter(Boolean);
  }
  if (typeof normalized.aliases === 'string') {
    normalized.aliases = normalized.aliases
      .split(',').map(s => s.trim()).filter(Boolean);
  }
  if (typeof normalized.publish_flag === 'string') {
    normalized.publish_flag = normalized.publish_flag.toUpperCase() === 'TRUE';
  }
  // スコアを数値型に統一
  ['score_social_clarity','score_continuity','score_business_alignment',
   'score_specificity','score_reference_value','total_score'].forEach(k => {
    if (normalized[k] !== undefined) normalized[k] = Number(normalized[k]) || 0;
  });
  return normalized;
}
