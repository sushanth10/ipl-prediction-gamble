"""
generate_html_reports.py
Generates one self-contained HTML report per human participant.
All data is embedded as JSON — fully offline, mobile-friendly.

Usage:
    python generate_html_reports.py
"""

import os
import sys
import json
import math
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ExtractAndTransform

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE        = os.path.dirname(os.path.abspath(__file__))
SCHEDULE    = os.path.join(BASE, "The Schedule/ipl_2026_schedule.csv")
PREDS_PATH  = os.path.join(BASE, "The 2026 Gambles")
RESULTS     = os.path.join(BASE, "The 2026 Results")
OUTPUT_DIR  = os.path.join(BASE, "The Visuals/html_reports")


# ── Data helpers ───────────────────────────────────────────────────────────────

def load_all():
    schedule_df = pd.read_csv(SCHEDULE)
    schedule_df.columns = schedule_df.columns.str.strip()
    results_df  = ExtractAndTransform.load_results(RESULTS)
    predictions = ExtractAndTransform.load_predictions(PREDS_PATH)
    return schedule_df, results_df, predictions


def compute_stats(schedule_df, results_df, predictions):
    lb_df, prog = ExtractAndTransform.calculate_scores(results_df, predictions)
    lb_df["Rank"] = lb_df["Points"].rank(method="dense", ascending=False).astype(int)
    lb_df = lb_df.sort_values("Rank").reset_index(drop=True)
    adv_df   = ExtractAndTransform.get_advanced_metrics(results_df, predictions)
    lb_df    = pd.merge(lb_df, adv_df, on="Participant", how="left")
    agree_mx = ExtractAndTransform.get_agreement_matrix(predictions, results_df)
    return lb_df, adv_df, prog, agree_mx


def _clean_str(s: str) -> str:
    """Remove surrogate characters that break UTF-8 encoding."""
    return s.encode("utf-8", errors="ignore").decode("utf-8")


def make_serializable(obj):
    """Recursively convert non-JSON-serializable types."""
    if isinstance(obj, float) and (math.isnan(obj) or math.isinf(obj)):
        return None
    if isinstance(obj, (bool, type(None))):
        return obj
    if isinstance(obj, str):
        return _clean_str(obj)
    if isinstance(obj, (int, float)):
        return obj
    if isinstance(obj, (list, tuple)):
        return [make_serializable(i) for i in obj]
    if isinstance(obj, dict):
        return {k: make_serializable(v) for k, v in obj.items()}
    try:
        return float(obj)
    except Exception:
        return _clean_str(str(obj))


# ── Static CSS (plain string — no f-string so curly braces are literal) ───────

_CSS = (
    "*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }\n"
    "html { scroll-behavior: smooth; }\n"
    "body {\n"
    "  background: #08090f;\n"
    "  color: #f0f2f6;\n"
    "  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', Arial, system-ui, sans-serif;\n"
    "  min-height: 100vh; overflow-x: hidden; -webkit-font-smoothing: antialiased;\n"
    "}\n"
    ".bg-canvas { position:fixed; inset:0; z-index:0; pointer-events:none; overflow:hidden; }\n"
    ".orb { position:absolute; border-radius:50%; filter:blur(90px); animation:orb-drift 10s ease-in-out infinite alternate; }\n"
    ".orb-1 { width:420px; height:420px; background:radial-gradient(circle,#7c5cff 0%,transparent 70%); opacity:0.13; top:-140px; right:-100px; }\n"
    ".orb-2 { width:320px; height:320px; background:radial-gradient(circle,#f97316 0%,transparent 70%); opacity:0.10; top:55%; left:-80px; animation-delay:-4s; }\n"
    ".orb-3 { width:260px; height:260px; background:radial-gradient(circle,#22c55e 0%,transparent 70%); opacity:0.08; bottom:5%; right:5%; animation-delay:-7s; }\n"
    "@keyframes orb-drift { from { transform:translate(0,0) scale(1); } to { transform:translate(18px,-22px) scale(1.1); } }\n"
    ".wrap { position:relative; z-index:1; max-width:500px; margin:0 auto; padding:20px 16px 40px; }\n"
    ".fade-up { opacity:0; transform:translateY(20px); animation:fade-up-in 0.55s ease forwards; }\n"
    "@keyframes fade-up-in { to { opacity:1; transform:translateY(0); } }\n"
    ".section-lbl { font-size:10.5px; font-weight:800; letter-spacing:3px; text-transform:uppercase; color:#3d4259; margin:28px 0 12px 2px; }\n"

    # ── Hero ──
    ".hero { background:linear-gradient(145deg,#110e20 0%,#161228 40%,#0d1624 100%); border:1px solid rgba(124,92,255,0.22); border-radius:26px; padding:28px 22px 22px; position:relative; overflow:hidden; }\n"
    ".hero::before { content:''; position:absolute; inset:0; background:radial-gradient(ellipse at 85% 15%,rgba(124,92,255,0.14) 0%,transparent 55%); pointer-events:none; }\n"
    ".hero::after { content:''; position:absolute; bottom:0; left:0; right:0; height:1px; background:linear-gradient(90deg,transparent,rgba(124,92,255,0.35),transparent); }\n"
    ".hero-eyebrow { font-size:10px; font-weight:700; letter-spacing:3.5px; text-transform:uppercase; color:#3d4259; margin-bottom:12px; }\n"
    ".hero-name { font-size:clamp(34px,9vw,44px); font-weight:900; line-height:1; letter-spacing:-1.5px; color:#ffffff; margin-bottom:14px; }\n"
    ".rank-badge { display:inline-flex; align-items:center; gap:7px; padding:6px 16px; border-radius:50px; font-size:13px; font-weight:800; margin-bottom:22px; letter-spacing:0.3px; }\n"
    ".r-gold   { background:rgba(255,215,0,0.12);  border:1px solid rgba(255,215,0,0.35);  color:#FFD700; }\n"
    ".r-silver { background:rgba(192,192,192,0.10); border:1px solid rgba(192,192,192,0.30); color:#C0C0C0; }\n"
    ".r-bronze { background:rgba(205,127,50,0.10);  border:1px solid rgba(205,127,50,0.30);  color:#CD7F32; }\n"
    ".r-n      { background:rgba(124,92,255,0.10);  border:1px solid rgba(124,92,255,0.28);  color:#a78bfa; }\n"
    ".hero-points-row { display:flex; align-items:baseline; gap:6px; margin-bottom:4px; }\n"
    ".hero-pts-big { font-size:clamp(48px,13vw,60px); font-weight:900; line-height:1; letter-spacing:-2.5px; color:#ffffff; }\n"
    ".hero-pts-label { font-size:18px; font-weight:500; color:#5a6078; }\n"
    ".hero-accuracy { font-size:14.5px; font-weight:600; color:#a78bfa; margin-bottom:18px; }\n"
    ".hero-badge { display:inline-flex; align-items:center; gap:7px; background:rgba(124,92,255,0.12); border:1px solid rgba(124,92,255,0.30); border-radius:50px; padding:7px 16px; font-size:12.5px; font-weight:700; color:#c4b5fd; margin-bottom:16px; }\n"
    ".hero-verdict { background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.07); border-radius:14px; padding:14px 16px; font-size:13.5px; line-height:1.55; color:#9ba3c0; font-style:italic; }\n"
    ".hero-verdict::before { content:'\\201C'; font-size:20px; color:rgba(124,92,255,0.5); font-style:normal; margin-right:3px; }\n"
    ".hero-verdict::after  { content:'\\201D'; font-size:20px; color:rgba(124,92,255,0.5); font-style:normal; margin-left:3px; }\n"

    # ── KPI Grid ──
    ".kpi-grid { display:grid; grid-template-columns:1fr 1fr; gap:10px; }\n"
    ".kpi-card { background:#0f1118; border:1px solid rgba(255,255,255,0.055); border-radius:18px; padding:18px 16px 14px; position:relative; overflow:hidden; transition:transform 0.18s ease,box-shadow 0.18s ease; -webkit-tap-highlight-color:transparent; }\n"
    ".kpi-card:active { transform:scale(0.96); box-shadow:0 0 0 2px rgba(124,92,255,0.25); }\n"
    ".kpi-card::before { content:''; position:absolute; top:0; left:0; right:0; height:2.5px; border-radius:18px 18px 0 0; }\n"
    ".c-green::before  { background:linear-gradient(90deg,#22c55e 0%,transparent 80%); }\n"
    ".c-red::before    { background:linear-gradient(90deg,#ef4444 0%,transparent 80%); }\n"
    ".c-gray::before   { background:linear-gradient(90deg,#6b7280 0%,transparent 80%); }\n"
    ".c-purple::before { background:linear-gradient(90deg,#7c5cff 0%,transparent 80%); }\n"
    ".c-gold::before   { background:linear-gradient(90deg,#FFD700 0%,transparent 80%); }\n"
    ".c-blue::before   { background:linear-gradient(90deg,#3b82f6 0%,transparent 80%); }\n"
    ".c-green  { box-shadow:inset 0 0 30px rgba(34,197,94,0.04); }\n"
    ".c-red    { box-shadow:inset 0 0 30px rgba(239,68,68,0.04); }\n"
    ".c-purple { box-shadow:inset 0 0 30px rgba(124,92,255,0.04); }\n"
    ".c-gold   { box-shadow:inset 0 0 30px rgba(255,215,0,0.04); }\n"
    ".c-blue   { box-shadow:inset 0 0 30px rgba(59,130,246,0.04); }\n"
    ".kpi-label { font-size:9.5px; font-weight:800; letter-spacing:2px; text-transform:uppercase; color:#3d4259; margin-bottom:10px; }\n"
    ".kpi-val { font-size:36px; font-weight:900; line-height:1; letter-spacing:-1.5px; }\n"
    ".c-green  .kpi-val { color:#22c55e; }\n"
    ".c-red    .kpi-val { color:#ef4444; }\n"
    ".c-gray   .kpi-val { color:#9ca3af; }\n"
    ".c-purple .kpi-val { color:#a78bfa; }\n"
    ".c-gold   .kpi-val { color:#fbbf24; }\n"
    ".c-blue   .kpi-val { color:#60a5fa; }\n"
    ".kpi-sub { font-size:11px; color:#3d4259; margin-top:5px; line-height:1.4; }\n"
    ".kpi-icon { position:absolute; bottom:10px; right:12px; font-size:26px; opacity:0.15; user-select:none; }\n"
    ".kpi-wide { grid-column:span 2; }\n"
    ".kpi-wide .kpi-val { font-size:46px; }\n"
    ".kpi-wide-inner { display:flex; align-items:center; gap:16px; }\n"
    ".kpi-wide-right { flex:1; }\n"
    ".kpi-wide-period { font-size:11.5px; color:#4a5070; margin-top:4px; line-height:1.4; }\n"
    ".footer { text-align:center; font-size:10.5px; letter-spacing:1.5px; color:#1e2234; margin-top:36px; text-transform:uppercase; }\n"

    # ── Feature 3: Chart ──
    ".chart-card { background:#0f1118; border:1px solid rgba(255,255,255,0.055); border-radius:18px; padding:18px 14px 14px; position:relative; overflow:hidden; }\n"
    ".chart-card::before { content:''; position:absolute; top:0; left:0; right:0; height:2.5px; border-radius:18px 18px 0 0; background:linear-gradient(90deg,#7c5cff 0%,transparent 80%); }\n"
    ".chart-header { display:flex; align-items:center; justify-content:space-between; margin-bottom:14px; gap:10px; }\n"
    ".chart-title { font-size:10px; font-weight:800; letter-spacing:2px; text-transform:uppercase; color:#3d4259; flex:1; }\n"
    ".compare-wrap { position:relative; flex-shrink:0; }\n"
    ".compare-select { appearance:none; -webkit-appearance:none; background:#161924; border:1px solid rgba(124,92,255,0.25); border-radius:10px; color:#a78bfa; font-size:11px; font-weight:600; padding:7px 26px 7px 11px; cursor:pointer; outline:none; max-width:145px; transition:border-color 0.2s; }\n"
    ".compare-select:focus { border-color:rgba(124,92,255,0.55); }\n"
    ".compare-arrow { position:absolute; right:8px; top:50%; transform:translateY(-50%); pointer-events:none; color:#5a6078; font-size:9px; }\n"
    ".chart-svg-wrap { position:relative; width:100%; }\n"
    ".chart-svg { width:100%; height:auto; display:block; }\n"
    ".chart-tooltip { position:absolute; background:#1a1d2a; border:1px solid rgba(124,92,255,0.30); border-radius:10px; padding:8px 12px; font-size:11px; pointer-events:none; white-space:nowrap; transform:translateX(-50%); z-index:10; box-shadow:0 4px 20px rgba(0,0,0,0.5); min-width:130px; }\n"
    ".tt-match { color:#5a6078; font-size:10px; margin-bottom:5px; font-weight:700; letter-spacing:1px; }\n"
    ".tt-row { display:flex; align-items:center; gap:6px; margin-top:4px; }\n"
    ".tt-dot { width:8px; height:8px; border-radius:50%; flex-shrink:0; }\n"
    ".tt-val { font-weight:800; font-size:12px; }\n"
    ".tt-name { color:#5a6078; font-size:10px; }\n"
    ".chart-legend { display:flex; flex-wrap:wrap; gap:14px; margin-top:12px; }\n"
    ".legend-item { display:flex; align-items:center; gap:7px; font-size:11px; color:#6b7280; font-weight:600; }\n"
    ".legend-line { width:22px; height:3px; border-radius:2px; flex-shrink:0; }\n"

    # ── Feature 4: Team Performance ──
    ".tp-best { display:flex; align-items:center; justify-content:space-between; gap:12px; padding:4px 0 16px; }\n"
    ".tp-best-left { flex:1; min-width:0; }\n"
    ".tp-best-lbl { font-size:9.5px; font-weight:800; letter-spacing:2px; text-transform:uppercase; color:#3d4259; margin-bottom:6px; }\n"
    ".tp-best-team { font-size:17px; font-weight:800; line-height:1.2; word-break:break-word; }\n"
    ".tp-best-sub { font-size:11px; color:#4a5070; margin-top:4px; }\n"
    ".tp-best-pts { font-size:46px; font-weight:900; line-height:1; letter-spacing:-2px; flex-shrink:0; }\n"
    ".tp-divider { height:1px; background:rgba(255,255,255,0.06); margin-bottom:14px; }\n"
    ".tp-svg { width:100%; height:auto; display:block; overflow:visible; }\n"

    # ── Feature 6: Best Match ──
    ".bm-header { display:flex; align-items:center; justify-content:space-between; margin-bottom:14px; }\n"
    ".bm-eyebrow { font-size:9.5px; font-weight:800; letter-spacing:2px; text-transform:uppercase; color:#3d4259; }\n"
    ".bm-points { font-size:38px; font-weight:900; color:#10b981; letter-spacing:-1.5px; line-height:1; }\n"
    ".bm-match-title { font-size:18px; font-weight:800; color:#f3f4f6; margin-bottom:6px; line-height:1.3; }\n"
    ".bm-date { font-size:11px; color:#5a6078; font-weight:600; margin-bottom:16px; }\n"
    ".bm-details { display:flex; gap:16px; background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.04); border-radius:12px; padding:12px 14px; }\n"
    ".bm-detail-col { flex:1; min-width:0; }\n"
    ".bm-detail-lbl { font-size:9px; font-weight:700; color:#4a5070; text-transform:uppercase; letter-spacing:1px; margin-bottom:4px; }\n"
    ".bm-detail-val { font-size:12px; font-weight:700; color:#e5e7eb; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }\n"
    ".bm-detail-val.correct { color:#10b981; }\n"
)


# ── Static JS (plain string — JSON injected via __JSON__ placeholder) ──────────

_JS = """
var D = __JSON__;

var RANK_META = {
  1: { cls: 'r-gold',   label: '1st Place' },
  2: { cls: 'r-silver', label: '2nd Place' },
  3: { cls: 'r-bronze', label: '3rd Place' }
};

function rankMeta(r) {
  return RANK_META[r] || { cls: 'r-n', label: '#' + r + ' Place' };
}

function countUp(el, target, ms, suffix) {
  if (!el || target == null) return;
  var isFloat = (target % 1 !== 0);
  var t0 = performance.now();
  function tick(now) {
    var p  = Math.min((now - t0) / ms, 1);
    var ep = 1 - Math.pow(1 - p, 3);
    var v  = ep * target;
    el.textContent = (isFloat ? v.toFixed(1) : Math.round(v)) + (suffix || '');
    if (p < 1) requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);
}

/* Remove characters outside printable Latin + common punctuation */
function clean(str) {
  if (!str) return '';
  return str.replace(/[^\u0020-\u00FF\u2013-\u2026]/g, '').trim();
}

function renderHero() {
  document.getElementById('h-name').textContent = D.participant;

  var rm = rankMeta(D.rank);
  document.getElementById('h-rank').innerHTML =
    '<span class="rank-badge ' + rm.cls + '">' +
      '#' + D.rank + '&nbsp;&nbsp;' + rm.label + '&nbsp;of&nbsp;' + D.total_participants +
    '</span>';

  countUp(document.getElementById('h-pts'), D.points, 1400, '');

  document.getElementById('h-acc').textContent =
    D.accuracy.toFixed(1) + '% accuracy \u00B7 ' +
    D.correct + ' correct of ' + D.total_matches + ' matches';

  var badge = D.primary_badge || ['The Predictor', 'A true cricket analyst'];
  document.getElementById('h-badge').textContent = clean(badge[0]) + '  \u2014  ' + badge[1];

  document.getElementById('h-verdict').textContent = clean(D.verdict);
}

function renderKPIs() {
  var grid = document.getElementById('kpi-grid');
  var rankCls = (D.rank === 1) ? 'c-gold' : 'c-blue';

  var CARDS = [
    { label:'Correct',           cls:'c-green',  icon:'\u2705', val:D.correct,             sub:'predictions hit' },
    { label:'Wrong',             cls:'c-red',    icon:'\u274C', val:D.wrong,               sub:'predictions missed' },
    { label:'No Result',         cls:'c-gray',   icon:'\u2796', val:D.nr_count,            sub:'washed-out matches' },
    { label:'Bonus Points',      cls:'c-gold',   icon:'\u2B50', val:D.bonus_pts,           sub:'from special matches' },
    { label:'Accuracy',          cls:'c-purple', icon:'\uD83C\uDFAF', val:D.accuracy, sub:D.correct+' of '+D.total_matches+' matches', suffix:'%' },
    { label:'Total Points',      cls:rankCls,    icon:'\uD83C\uDFC6', val:D.points,  sub:'Rank #'+D.rank+' of '+D.total_participants },
    { label:'Best Win Streak',   cls:'c-green',  icon:'\uD83D\uDD25', val:D.longest_win_streak,  sub:'matches in a row',
      period:(D.winning_period||'').replace(/, 2026/g,''), wide:true },
    { label:'Worst Loss Streak', cls:'c-red',    icon:'\u2744\uFE0F', val:D.longest_loss_streak, sub:'matches in a row',
      period:(D.losing_period||'').replace(/, 2026/g,''),  wide:true }
  ];

  CARDS.forEach(function(card, i) {
    var el    = document.createElement('div');
    var delay = (0.28 + i * 0.07).toFixed(2);

    if (card.wide) {
      el.className = 'kpi-card kpi-wide ' + card.cls + ' fade-up';
      el.style.animationDelay = delay + 's';
      el.innerHTML =
        '<div class="kpi-label">' + card.label + '</div>' +
        '<div class="kpi-wide-inner">' +
          '<div class="kpi-val" id="kv-' + i + '">0</div>' +
          '<div class="kpi-wide-right">' +
            '<div class="kpi-sub">' + card.sub + '</div>' +
            '<div class="kpi-wide-period">' + (card.period || '') + '</div>' +
          '</div>' +
        '</div>' +
        '<div class="kpi-icon">' + card.icon + '</div>';
    } else {
      el.className = 'kpi-card ' + card.cls + ' fade-up';
      el.style.animationDelay = delay + 's';
      el.innerHTML =
        '<div class="kpi-label">' + card.label + '</div>' +
        '<div class="kpi-val" id="kv-' + i + '">0</div>' +
        '<div class="kpi-sub">' + card.sub + '</div>' +
        '<div class="kpi-icon">' + card.icon + '</div>';
    }
    grid.appendChild(el);

    (function(idx, c) {
      setTimeout(function() {
        countUp(document.getElementById('kv-' + idx), c.val, 1100, c.suffix || '');
      }, 280 + idx * 70);
    })(i, card);
  });
}

// ── Feature 3: Points Journey Chart ─────────────────────────────────────────
var ALL_PROGS = D.all_progressions || {};
var P_COL = '#a78bfa';   // player colour
var C_COL = '#f97316';   // compare colour
var CW = 560, CH = 230;  // SVG viewBox size
var PL = 48, PR = 12, PT = 15, PB = 32;  // padding
var IW = CW - PL - PR, IH = CH - PT - PB;
var activeCompare = null;
var tooltipEl = null;

function niceMax(v) {
  if (!v) return 100;
  var mag = Math.pow(10, Math.floor(Math.log10(v)));
  return Math.ceil(v / mag) * mag;
}
function px(i, n) { return PL + (i / Math.max(n - 1, 1)) * IW; }
function py(v, yMax) { return PT + IH - (v / yMax) * IH; }

function catmull(pts) {
  if (pts.length < 2) return '';
  var d = 'M' + pts[0][0].toFixed(1) + ' ' + pts[0][1].toFixed(1);
  for (var i = 0; i < pts.length - 1; i++) {
    var p0 = pts[Math.max(0, i - 1)], p1 = pts[i];
    var p2 = pts[i + 1], p3 = pts[Math.min(pts.length - 1, i + 2)];
    var c1x = (p1[0] + (p2[0] - p0[0]) / 6).toFixed(1);
    var c1y = (p1[1] + (p2[1] - p0[1]) / 6).toFixed(1);
    var c2x = (p2[0] - (p3[0] - p1[0]) / 6).toFixed(1);
    var c2y = (p2[1] - (p3[1] - p1[1]) / 6).toFixed(1);
    d += ' C' + c1x + ' ' + c1y + ',' + c2x + ' ' + c2y + ',' + p2[0].toFixed(1) + ' ' + p2[1].toFixed(1);
  }
  return d;
}

function buildSVG(prog, yMax, col, gradId, showFill) {
  var n = prog.length;
  var pts = prog.map(function(v, i) { return [px(i, n), py(v, yMax)]; });
  var lp  = catmull(pts);
  var out = [];
  if (showFill) {
    var fp = lp + ' L' + pts[n-1][0].toFixed(1) + ' ' + (PT+IH) + ' L' + PL + ' ' + (PT+IH) + ' Z';
    out.push('<defs><linearGradient id="' + gradId + '" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="' + col + '" stop-opacity="0.25"/><stop offset="100%" stop-color="' + col + '" stop-opacity="0"/></linearGradient></defs>');
    out.push('<path d="' + fp + '" fill="url(#' + gradId + ')" stroke="none"/>');
  }
  out.push('<path d="' + lp + '" fill="none" stroke="' + col + '" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>');
  var last = pts[n - 1];
  out.push('<circle cx="' + last[0].toFixed(1) + '" cy="' + last[1].toFixed(1) + '" r="4" fill="' + col + '" stroke="#0f1118" stroke-width="2"/>');
  return { svg: out.join(''), pts: pts };
}

function buildGrid(yMax, n) {
  var out = [], ticks = 5, step = yMax / ticks;
  for (var t = 0; t <= ticks; t++) {
    var v = t * step, y = py(v, yMax).toFixed(1);
    out.push('<line x1="' + PL + '" y1="' + y + '" x2="' + (CW-PR) + '" y2="' + y + '" stroke="rgba(255,255,255,0.045)" stroke-width="1"/>');
    out.push('<text x="' + (PL-5) + '" y="' + y + '" text-anchor="end" dominant-baseline="middle" fill="#3d4259" font-size="9" font-family="system-ui,sans-serif">' + Math.round(v) + '</text>');
  }
  var xStep = Math.max(1, Math.ceil(n / 8));
  for (var i = 0; i < n; i += xStep) {
    var x = px(i, n).toFixed(1);
    out.push('<text x="' + x + '" y="' + (CH-6) + '" text-anchor="middle" fill="#3d4259" font-size="9" font-family="system-ui,sans-serif">' + i + '</text>');
  }
  return out.join('');
}

function renderChart() {
  var container = document.getElementById('chart-container');
  if (!container) return;
  var pp = D.progression || [];
  var cp = activeCompare ? (ALL_PROGS[activeCompare] || []) : null;
  var allVals = pp.concat(cp || []);
  var yMax = niceMax(allVals.length ? Math.max.apply(null, allVals) : 100);
  var grid = buildGrid(yMax, pp.length);
  var pr   = buildSVG(pp, yMax, P_COL, 'pg', true);
  var cr   = cp ? buildSVG(cp, yMax, C_COL, null, false) : null;
  var cur  = '<line id="cur" x1="0" y1="' + PT + '" x2="0" y2="' + (PT+IH) + '" stroke="rgba(255,255,255,0.15)" stroke-width="1" stroke-dasharray="4 3" opacity="0"/>';
  var ov   = '<rect id="ov" x="' + PL + '" y="' + PT + '" width="' + IW + '" height="' + IH + '" fill="transparent" style="cursor:crosshair"/>';
  var svg  = '<svg class="chart-svg" viewBox="0 0 ' + CW + ' ' + CH + '" xmlns="http://www.w3.org/2000/svg">' + grid + pr.svg + (cr ? cr.svg : '') + cur + ov + '</svg>';
  container.innerHTML = '<div class="chart-svg-wrap">' + svg + '</div>';

  var leg = document.getElementById('chart-legend');
  if (leg) {
    var lh = '<div class="legend-item"><div class="legend-line" style="background:' + P_COL + '"></div>' + D.participant + '</div>';
    if (activeCompare) lh += '<div class="legend-item"><div class="legend-line" style="background:' + C_COL + '"></div>' + activeCompare + '</div>';
    leg.innerHTML = lh;
  }
  attachInteraction(pr.pts, cr ? cr.pts : null, pp, cp);
}

function attachInteraction(pPts, cPts, pp, cp) {
  var ov  = document.getElementById('ov');
  var cur = document.getElementById('cur');
  var wrap = document.querySelector('.chart-svg-wrap');
  if (!ov || !cur || !wrap) return;
  if (!tooltipEl) { tooltipEl = document.createElement('div'); tooltipEl.className = 'chart-tooltip'; }
  tooltipEl.style.opacity = '0'; tooltipEl.style.top = '-9999px';
  if (!wrap.contains(tooltipEl)) wrap.appendChild(tooltipEl);

  function show(idx) {
    if (idx < 0 || idx >= pPts.length) return;
    cur.setAttribute('x1', pPts[idx][0].toFixed(1)); cur.setAttribute('x2', pPts[idx][0].toFixed(1)); cur.setAttribute('opacity', '1');
    var html = '<div class="tt-match">MATCH ' + idx + '</div>';
    html += '<div class="tt-row"><div class="tt-dot" style="background:' + P_COL + '"></div><span class="tt-val" style="color:' + P_COL + '">' + pp[idx] + ' pts</span>&nbsp;<span class="tt-name">' + D.participant + '</span></div>';
    if (cp && cPts) html += '<div class="tt-row"><div class="tt-dot" style="background:' + C_COL + '"></div><span class="tt-val" style="color:' + C_COL + '">' + (cp[idx]||0) + ' pts</span>&nbsp;<span class="tt-name">' + activeCompare + '</span></div>';
    tooltipEl.innerHTML = html;
    var svgEl = wrap.querySelector('svg');
    var ratio = svgEl ? svgEl.getBoundingClientRect().width / CW : 1;
    var xPx   = pPts[idx][0] * ratio;
    var tipW  = tooltipEl.offsetWidth || 140;
    var left  = Math.min(Math.max(xPx, tipW/2 + 4), wrap.offsetWidth - tipW/2 - 4);
    tooltipEl.style.left = left + 'px'; tooltipEl.style.top = '2px'; tooltipEl.style.opacity = '1';
  }
  function hide() { cur.setAttribute('opacity','0'); tooltipEl.style.opacity='0'; }
  function indexFromX(clientX) {
    var svgEl = wrap.querySelector('svg');
    var rect  = svgEl ? svgEl.getBoundingClientRect() : wrap.getBoundingClientRect();
    var ratio = rect.width / CW;
    var relX  = clientX - rect.left;
    var svgX  = relX / ratio;
    var i     = Math.round((svgX - PL) / IW * (pPts.length - 1));
    return Math.max(0, Math.min(pPts.length - 1, i));
  }
  ov.addEventListener('mousemove', function(e) { show(indexFromX(e.clientX)); });
  ov.addEventListener('mouseleave', hide);
  ov.addEventListener('touchmove',  function(e) { e.preventDefault(); show(indexFromX(e.touches[0].clientX)); }, { passive: false });
  ov.addEventListener('touchend',   hide);
}

function renderCompareDropdown() {
  var sel = document.getElementById('compare-select');
  if (!sel) return;
  var others = Object.keys(ALL_PROGS).filter(function(k) { return k !== D.participant; }).sort();
  var opts = '<option value="">Compare with...</option>';
  others.forEach(function(k) { opts += '<option value="' + k + '">' + k + '</option>'; });
  sel.innerHTML = opts;
  sel.addEventListener('change', function() {
    activeCompare = this.value || null;
    renderChart();
  });
}

// ── Feature 4: Team Performance ─────────────────────────────────────────────
var TEAM_COLORS = {
  'Chennai Super Kings':'#F9CD05', 'Delhi Capitals':'#17449B',
  'Gujarat Titans':'#6db0e0', 'Kolkata Knight Riders':'#8b5cf6',
  'Lucknow Super Giants':'#00ADEF', 'Mumbai Indians':'#3b82f6',
  'Punjab Kings':'#ef4444', 'Rajasthan Royals':'#EA1A84',
  'Royal Challengers Bengaluru':'#ef4444', 'Sunrisers Hyderabad':'#f97316'
};
var TEAM_SHORT = {
  'Chennai Super Kings':'CSK', 'Delhi Capitals':'DC',
  'Gujarat Titans':'GT', 'Kolkata Knight Riders':'KKR',
  'Lucknow Super Giants':'LSG', 'Mumbai Indians':'MI',
  'Punjab Kings':'PBKS', 'Rajasthan Royals':'RR',
  'Royal Challengers Bengaluru':'RCB', 'Sunrisers Hyderabad':'SRH'
};

function renderTeamPerf() {
  var container = document.getElementById('team-perf-card');
  if (!container || !D.team_points) return;

  // Sort entries descending by points
  var entries = Object.keys(D.team_points).map(function(t) {
    return [t, D.team_points[t]];
  }).sort(function(a, b) { return b[1] - a[1]; });

  if (!entries.length) { container.style.display = 'none'; return; }

  var best = entries[0], bestTeam = best[0], bestPts = best[1];
  var bestCol = TEAM_COLORS[bestTeam] || '#a78bfa';
  var maxPts  = bestPts;
  var BAR_MAX = 330;   // max bar pixel width in SVG units
  var ROW_H   = 36;
  var svgH    = entries.length * ROW_H + 4;

  // ── Best team hero ──
  var hero =
    '<div class="tp-best">' +
      '<div class="tp-best-left">' +
        '<div class="tp-best-lbl">Best Franchise</div>' +
        '<div class="tp-best-team" style="color:' + bestCol + '">' + bestTeam + '</div>' +
        '<div class="tp-best-sub">Your most profitable team this season</div>' +
      '</div>' +
      '<div class="tp-best-pts" style="color:' + bestCol + '">' + bestPts + '<span style="font-size:16px;font-weight:500;color:#5a6078"> pts</span></div>' +
    '</div>' +
    '<div class="tp-divider"></div>';

  // ── SVG bar chart ──
  var bars = '';
  entries.forEach(function(e, i) {
    var team = e[0], pts = e[1];
    var col  = TEAM_COLORS[team] || '#a78bfa';
    var abbr = TEAM_SHORT[team]  || team.substring(0, 3).toUpperCase();
    var barW = Math.max(6, (pts / maxPts) * BAR_MAX);
    var y    = i * ROW_H;
    var midY = (y + ROW_H / 2).toFixed(1);

    // Team abbrev
    bars += '<text x="0" y="' + midY + '" dominant-baseline="middle" fill="#6b7280" font-size="10.5" font-weight="700" font-family="system-ui,sans-serif">' + abbr + '</text>';
    // Background track
    bars += '<rect x="52" y="' + (y + 8) + '" width="' + BAR_MAX + '" height="20" rx="5" fill="rgba(255,255,255,0.04)"/>';
    // Colored bar
    bars += '<rect x="52" y="' + (y + 8) + '" width="' + barW.toFixed(1) + '" height="20" rx="5" fill="' + col + '" opacity="0.88"/>';
    // Points label
    bars += '<text x="' + (52 + barW + 7).toFixed(1) + '" y="' + midY + '" dominant-baseline="middle" fill="#9ca3af" font-size="10.5" font-weight="700" font-family="system-ui,sans-serif">' + pts + '</text>';
  });

  var svg = '<svg class="tp-svg" viewBox="0 0 ' + (52 + BAR_MAX + 45) + ' ' + svgH + '">' + bars + '</svg>';
  var note = '<div style="font-size:10px;color:#5a6078;margin-top:14px;font-style:italic;font-weight:600;text-align:center;border-top:1px dashed rgba(255,255,255,0.04);padding-top:10px;">' +
             '* Excludes ' + (D.nr_points || 0) + ' pts earned from ' + (D.nr_count || 0) + ' No Result (NR) matches</div>';
  container.innerHTML = hero + svg + note;
}

// ── Feature 5: Team Accuracy ────────────────────────────────────────────
function renderTeamAccuracy() {
  var container = document.getElementById('team-acc-card');
  if (!container || !D.team_accuracy) return;

  // Sort entries descending by accuracy; require at least 2 matches for best-team
  var entries = Object.keys(D.team_accuracy).map(function(t) {
    return [t, D.team_accuracy[t]];
  }).sort(function(a, b) {
    if (a[1].total === 0 && b[1].total > 0) return 1;
    if (b[1].total === 0 && a[1].total > 0) return -1;
    return b[1].accuracy - a[1].accuracy;
  });

  if (!entries.length) { container.style.display = 'none'; return; }

  // Pick best with >= 2 matches if possible
  var best = entries.find(function(e) { return e[1].total >= 2; }) || entries.find(function(e) { return e[1].total > 0; }) || entries[0];
  var bestTeam = best[0], bestData = best[1];
  var bestCol  = TEAM_COLORS[bestTeam] || '#a78bfa';
  var BAR_MAX  = 330, ROW_H = 36;
  var svgH     = entries.length * ROW_H + 4;

  // ── Best team hero ──
  var hero =
    '<div class="tp-best">' +
      '<div class="tp-best-left">' +
        '<div class="tp-best-lbl">Best Accuracy Franchise</div>' +
        '<div class="tp-best-team" style="color:' + bestCol + '">' + bestTeam + '</div>' +
        '<div class="tp-best-sub">' + bestData.correct + ' correct from ' + bestData.total + ' matches</div>' +
      '</div>' +
      '<div class="tp-best-pts" style="color:' + bestCol + '">' + bestData.accuracy.toFixed(0) + '<span style="font-size:22px;font-weight:700;color:' + bestCol + '">%</span></div>' +
    '</div>' +
    '<div class="tp-divider"></div>';

  // ── SVG accuracy bar chart ──
  var bars = '';
  entries.forEach(function(e, i) {
    var team = e[0], data = e[1];
    var col  = TEAM_COLORS[team] || '#a78bfa';
    var abbr = TEAM_SHORT[team]  || team.substring(0, 3).toUpperCase();
    var barW = Math.max(6, (data.accuracy / 100) * BAR_MAX);
    var y    = i * ROW_H;
    var midY = (y + ROW_H / 2).toFixed(1);
    var lbl  = data.accuracy.toFixed(0) + '% (' + data.correct + '/' + data.total + ')';

    bars += '<text x="0" y="' + midY + '" dominant-baseline="middle" fill="#6b7280" font-size="10.5" font-weight="700" font-family="system-ui,sans-serif">' + abbr + '</text>';
    bars += '<rect x="52" y="' + (y + 8) + '" width="' + BAR_MAX + '" height="20" rx="5" fill="rgba(255,255,255,0.04)"/>';
    bars += '<rect x="52" y="' + (y + 8) + '" width="' + barW.toFixed(1) + '" height="20" rx="5" fill="' + col + '" opacity="0.88"/>';
    bars += '<text x="' + (52 + barW + 7).toFixed(1) + '" y="' + midY + '" dominant-baseline="middle" fill="#9ca3af" font-size="10.5" font-weight="700" font-family="system-ui,sans-serif">' + lbl + '</text>';
  });

  var svg = '<svg class="tp-svg" viewBox="0 0 ' + (52 + BAR_MAX + 90) + ' ' + svgH + '">' + bars + '</svg>';
  container.innerHTML = hero + svg;
}

// ── Feature 6: Best Matches ──────────────────────────────────────────────
function renderBestMatches() {
  renderBestMatchCard('best-league-card', D.best_league_match, 'Best League Match');
  renderBestMatchCard('best-overall-card', D.best_overall_match, 'Best Match (Overall)');
}

function renderBestMatchCard(elementId, bm, title) {
  var container = document.getElementById(elementId);
  if (!container || !bm) return;

  var ptsText = '+' + bm.points;
  var col = TEAM_COLORS[bm.winner] || '#10b981';

  var html =
    '<div class="bm-header">' +
      '<div class="bm-eyebrow">' + title + '</div>' +
      '<div class="bm-points" style="color:' + col + '">' + ptsText + '<span style="font-size:14px;font-weight:700;color:#5a6078"> pts</span></div>' +
    '</div>' +
    '<div class="bm-match-title">' + bm.home + ' vs ' + bm.away + '</div>' +
    '<div class="bm-date">Match #' + bm.match_no + ' &middot; ' + bm.date + '</div>' +
    '<div class="bm-details">' +
      '<div class="bm-detail-col">' +
        '<div class="bm-detail-lbl">Your Prediction</div>' +
        '<div class="bm-detail-val correct">' + (bm.prediction || '—') + '</div>' +
      '</div>' +
      '<div class="bm-detail-col">' +
        '<div class="bm-detail-lbl">Match Winner</div>' +
        '<div class="bm-detail-val" style="color:' + col + '">' + bm.winner + '</div>' +
      '</div>' +
    '</div>';

  container.innerHTML = html;
}

// ── Feature 7: Stadium Stats ─────────────────────────────────────────────
function renderStadiumStats() {
  var container = document.getElementById('stadium-stats-card');
  if (!container || !D.stadium_stats) return;

  var entries = D.stadium_stats.slice();
  if (!entries.length) { container.style.display = 'none'; return; }

  // Sort descending by Points first, then by Win %
  entries.sort(function(a, b) {
    if (b.Points !== a.Points) return b.Points - a.Points;
    return b['Win %'] - a['Win %'];
  });

  var best = entries[0];
  var bestCol = '#10b981'; // Green for success
  var BAR_MAX = 330, ROW_H = 36;
  var svgH = entries.length * ROW_H + 4;
  var maxPts = Math.max(10, entries[0].Points);

  var totalMatches = best.Wins + best.Losses;
  var hero =
    '<div class="tp-best">' +
      '<div class="tp-best-left">' +
        '<div class="tp-best-lbl">Luckiest Stadium</div>' +
        '<div class="tp-best-team" style="color:' + bestCol + '">' + best.Stadium + '</div>' +
        '<div class="tp-best-sub">' + best.City + ' &middot; ' + best.Wins + ' wins / ' + totalMatches + ' matches (' + best['Win %'].toFixed(0) + '% Win Rate)</div>' +
      '</div>' +
      '<div class="tp-best-pts" style="color:' + bestCol + '">' + best.Points + '<span style="font-size:16px;font-weight:500;color:#5a6078"> pts</span></div>' +
    '</div>' +
    '<div class="tp-divider"></div>';

  var bars = '';
  entries.forEach(function(e, i) {
    var name = e.Stadium, pts = e.Points, wins = e.Wins, losses = e.Losses;
    var total = wins + losses;
    var barW = Math.max(6, (pts / maxPts) * BAR_MAX);
    var y = i * ROW_H;
    var midY = (y + ROW_H / 2).toFixed(1);
    
    var shortName = name.replace(' Cricket Stadium', '').replace(' Stadium', '').replace(' International', ' Intl.');
    var lbl = pts + ' pts (' + wins + '/' + total + ' W/M)';

    bars += '<text x="0" y="' + midY + '" dominant-baseline="middle" fill="#6b7280" font-size="10.5" font-weight="700" font-family="system-ui,sans-serif">' + shortName.toUpperCase() + '</text>';
    bars += '<rect x="110" y="' + (y + 8) + '" width="' + BAR_MAX + '" height="20" rx="5" fill="rgba(255,255,255,0.04)"/>';
    bars += '<rect x="110" y="' + (y + 8) + '" width="' + barW.toFixed(1) + '" height="20" rx="5" fill="#3b82f6" opacity="0.88"/>';
    bars += '<text x="' + (110 + barW + 7).toFixed(1) + '" y="' + midY + '" dominant-baseline="middle" fill="#9ca3af" font-size="10.5" font-weight="700" font-family="system-ui,sans-serif">' + lbl + '</text>';
  });

  var svg = '<svg class="tp-svg" viewBox="0 0 540 ' + svgH + '">' + bars + '</svg>';
  var note = '<div style="font-size:10px;color:#5a6078;margin-top:14px;font-style:italic;font-weight:600;text-align:center;border-top:1px dashed rgba(255,255,255,0.04);padding-top:10px;">' +
             '* Excludes ' + (D.nr_points || 0) + ' pts earned from ' + (D.nr_count || 0) + ' No Result (NR) matches</div>';
  container.innerHTML = hero + svg + note;
}

// ── Feature 8: Stadium Accuracy ──────────────────────────────────────────
function renderStadiumAccuracy() {
  var container = document.getElementById('stadium-acc-card');
  if (!container || !D.stadium_stats) return;

  var entries = D.stadium_stats.slice();
  if (!entries.length) { container.style.display = 'none'; return; }

  // Sort descending by Win % first, then by total matches played, and push 0-match entries to bottom
  entries.sort(function(a, b) {
    var totalA = a.Wins + a.Losses;
    var totalB = b.Wins + b.Losses;
    if (totalA === 0 && totalB > 0) return 1;
    if (totalB === 0 && totalA > 0) return -1;
    if (b['Win %'] !== a['Win %']) return b['Win %'] - a['Win %'];
    return totalB - totalA;
  });

  // Require at least 3 matches for the best stadium highlight, fallback to 2, then fallback to first
  var best = entries.filter(function(e) { return (e.Wins + e.Losses) >= 3; })[0] ||
             entries.filter(function(e) { return (e.Wins + e.Losses) >= 2; })[0] ||
             entries[0];

  var bestCol = '#10b981'; // Green for success / accuracy
  var BAR_MAX = 330, ROW_H = 36;
  var svgH = entries.length * ROW_H + 4;

  var bestTotal = best.Wins + best.Losses;
  var hero =
    '<div class="tp-best">' +
      '<div class="tp-best-left">' +
        '<div class="tp-best-lbl">Luckiest Stadium by Win %</div>' +
        '<div class="tp-best-team" style="color:' + bestCol + '">' + best.Stadium + '</div>' +
        '<div class="tp-best-sub">' + best.City + ' &middot; ' + best.Wins + ' correct / ' + bestTotal + ' matches</div>' +
      '</div>' +
      '<div class="tp-best-pts" style="color:' + bestCol + '">' + best['Win %'].toFixed(0) + '<span style="font-size:16px;font-weight:700;color:#5a6078">%</span></div>' +
    '</div>' +
    '<div class="tp-divider"></div>';

  var bars = '';
  entries.forEach(function(e, i) {
    var name = e.Stadium, winRate = e['Win %'], wins = e.Wins, losses = e.Losses;
    var total = wins + losses;
    var barW = Math.max(6, (winRate / 100) * BAR_MAX);
    var y = i * ROW_H;
    var midY = (y + ROW_H / 2).toFixed(1);
    
    var shortName = name.replace(' Cricket Stadium', '').replace(' Stadium', '').replace(' International', ' Intl.');
    var lbl = winRate.toFixed(0) + '% (' + wins + '/' + total + ' W/M)';

    bars += '<text x="0" y="' + midY + '" dominant-baseline="middle" fill="#6b7280" font-size="10.5" font-weight="700" font-family="system-ui,sans-serif">' + shortName.toUpperCase() + '</text>';
    bars += '<rect x="110" y="' + (y + 8) + '" width="' + BAR_MAX + '" height="20" rx="5" fill="rgba(255,255,255,0.04)"/>';
    bars += '<rect x="110" y="' + (y + 8) + '" width="' + barW.toFixed(1) + '" height="20" rx="5" fill="#10b981" opacity="0.88"/>';
    bars += '<text x="' + (110 + barW + 7).toFixed(1) + '" y="' + midY + '" dominant-baseline="middle" fill="#9ca3af" font-size="10.5" font-weight="700" font-family="system-ui,sans-serif">' + lbl + '</text>';
  });

  var svg = '<svg class="tp-svg" viewBox="0 0 540 ' + svgH + '">' + bars + '</svg>';
  var note = '<div style="font-size:10px;color:#5a6078;margin-top:14px;font-style:italic;font-weight:600;text-align:center;border-top:1px dashed rgba(255,255,255,0.04);padding-top:10px;">' +
             '* Highlighted luckiest stadium requires a minimum of 3 matches played</div>';
  container.innerHTML = hero + svg + note;
}

// ── Feature 9: Prediction Similarity ─────────────────────────────────────
function renderSimilarity() {
  var container = document.getElementById('similarity-card');
  if (!container || !D.similarity_stats) return;

  var entries = D.similarity_stats;
  if (!entries.length) { container.style.display = 'none'; return; }

  var best = entries[0];
  var bestCol = '#8b5cf6'; // Violet theme for similarity
  var ROW_H = 46;
  var svgH = entries.length * ROW_H + 4;
  var BAR_MAX = 220;
  var X_START = 110;

  var hero =
    '<div class="tp-best">' +
      '<div class="tp-best-left">' +
        '<div class="tp-best-lbl">Prediction Twin</div>' +
        '<div class="tp-best-team" style="color:' + bestCol + '">' + best.participant + '</div>' +
        '<div class="tp-best-sub">Most similar predictions (' + best.agreed_count + ' / ' + best.total_matches + ' agreed)</div>' +
      '</div>' +
      '<div class="tp-best-pts" style="color:' + bestCol + '">' + best.similarity_pct.toFixed(0) + '<span style="font-size:16px;font-weight:700;color:#5a6078">%</span></div>' +
    '</div>' +
    '<div class="tp-divider"></div>';

  var bars = '';
  entries.forEach(function(e, i) {
    var other = e.participant;
    var pct = e.similarity_pct;
    var agreed = e.agreed_count;
    var total = e.total_matches;
    var diag = e.disagreed_count;
    var pCorrect = e.correct_p;
    var oCorrect = e.correct_o;
    
    var barW = Math.max(6, (pct / 100) * BAR_MAX);
    var y = i * ROW_H;
    var midY1 = y + 16;
    var midY2 = y + 34;

    // Opponent name
    bars += '<text x="0" y="' + midY1 + '" fill="#e5e7eb" font-size="11" font-weight="700" font-family="system-ui,sans-serif">' + other.toUpperCase() + '</text>';
    // Track
    bars += '<rect x="' + X_START + '" y="' + (y + 4) + '" width="' + BAR_MAX + '" height="16" rx="4" fill="rgba(255,255,255,0.04)"/>';
    // Bar
    bars += '<rect x="' + X_START + '" y="' + (y + 4) + '" width="' + barW.toFixed(1) + '" height="16" rx="4" fill="' + bestCol + '" opacity="0.88"/>';
    // Pct label
    bars += '<text x="' + (X_START + BAR_MAX + 10) + '" y="' + midY1 + '" fill="#e5e7eb" font-size="11" font-weight="700" font-family="system-ui,sans-serif">' + pct.toFixed(0) + '% (' + agreed + '/' + total + ')</text>';
    // Disagreed details line
    var disMsg = 'Disagreed: You ' + pCorrect + ' - ' + oCorrect + ' ' + other + ' (' + diag + ' matches)';
    bars += '<text x="' + X_START + '" y="' + midY2 + '" fill="#9ca3af" font-size="10" font-weight="600" font-family="system-ui,sans-serif">' + disMsg + '</text>';
  });

  var svg = '<svg class="tp-svg" viewBox="0 0 540 ' + svgH + '">' + bars + '</svg>';
  container.innerHTML = hero + svg;
}

document.addEventListener('DOMContentLoaded', function() {
  renderHero();
  renderKPIs();
  renderCompareDropdown();
  renderChart();
  renderTeamPerf();
  renderTeamAccuracy();
  renderBestMatches();
  renderStadiumStats();
  renderStadiumAccuracy();
  renderSimilarity();
});
"""


# ── HTML assembler ─────────────────────────────────────────────────────────────

def build_html(player_data: dict) -> str:
    json_data = json.dumps(make_serializable(player_data), indent=2, ensure_ascii=False)
    name      = player_data["participant"]
    js_block  = _JS.replace("__JSON__", json_data)

    lines = [
        '<!DOCTYPE html>',
        '<html lang="en">',
        '<head>',
        '<meta charset="UTF-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">',
        f'<meta name="description" content="{name}\'s IPL 2026 Prediction Season Report">',
        f'<title>{name} \u00b7 IPL 2026 Season Report</title>',
        '<style>', _CSS, '</style>',
        '</head>',
        '<body>',
        '<div class="bg-canvas">',
        '  <div class="orb orb-1"></div>',
        '  <div class="orb orb-2"></div>',
        '  <div class="orb orb-3"></div>',
        '</div>',
        '<div class="wrap">',

        # ── Feature 1: Hero ──
        '  <div class="hero fade-up" style="animation-delay:0.05s" id="hero">',
        '    <div class="hero-eyebrow">IPL 2026 &middot; Season Report</div>',
        '    <div class="hero-name" id="h-name">\u2014</div>',
        '    <div id="h-rank"></div>',
        '    <div class="hero-points-row">',
        '      <div class="hero-pts-big" id="h-pts">0</div>',
        '      <div class="hero-pts-label">pts</div>',
        '    </div>',
        '    <div class="hero-accuracy" id="h-acc">\u2014</div>',
        '    <div class="hero-badge" id="h-badge">\u2014</div>',
        '    <div class="hero-verdict" id="h-verdict">\u2014</div>',
        '  </div>',

        # ── Feature 2: KPI strip ──
        '  <div class="section-lbl fade-up" style="animation-delay:0.2s">Season Statistics</div>',
        '  <div class="kpi-grid" id="kpi-grid"></div>',

        # ── Feature 3: Points Journey ──
        '  <div class="section-lbl fade-up" style="animation-delay:0.85s">Points Journey</div>',
        '  <div class="chart-card fade-up" style="animation-delay:0.95s">',
        '    <div class="chart-header">',
        '      <div class="chart-title">Cumulative Points Over Season</div>',
        '      <div class="compare-wrap">',
        '        <select class="compare-select" id="compare-select"></select>',
        '        <span class="compare-arrow">&#9660;</span>',
        '      </div>',
        '    </div>',
        '    <div id="chart-container"></div>',
        '    <div class="chart-legend" id="chart-legend"></div>',
        '  </div>',

        # ── Feature 4: Team Performance ──
        '  <div class="section-lbl fade-up" style="animation-delay:1.05s">Team Performance</div>',
        '  <div class="chart-card fade-up" style="animation-delay:1.12s" id="team-perf-card"></div>',

        # ── Feature 5: Team Accuracy ──
        '  <div class="section-lbl fade-up" style="animation-delay:1.18s">Team Accuracy</div>',
        '  <div class="chart-card fade-up" style="animation-delay:1.25s" id="team-acc-card"></div>',

        # ── Feature 6: Best Matches ──
        '  <div class="section-lbl fade-up" style="animation-delay:1.31s">Best Matches</div>',
        '  <div class="chart-card fade-up" style="animation-delay:1.36s" id="best-league-card"></div>',
        '  <div class="chart-card fade-up" style="animation-delay:1.42s" id="best-overall-card" style="margin-top:16px;"></div>',

        # ── Feature 7: Stadium Stats ──
        '  <div class="section-lbl fade-up" style="animation-delay:1.48s">Stadium Performance</div>',
        '  <div class="chart-card fade-up" style="animation-delay:1.55s" id="stadium-stats-card"></div>',

        # ── Feature 8: Stadium Accuracy ──
        '  <div class="section-lbl fade-up" style="animation-delay:1.61s">Stadium Accuracy</div>',
        '  <div class="chart-card fade-up" style="animation-delay:1.68s" id="stadium-acc-card"></div>',

        # ── Feature 9: Prediction Similarity ──
        '  <div class="section-lbl fade-up" style="animation-delay:1.74s">Prediction Similarity</div>',
        '  <div class="chart-card fade-up" style="animation-delay:1.80s" id="similarity-card"></div>',

        '  <div class="footer fade-up" style="animation-delay:1.90s">',
        '    IPL Prediction Game 2026 &middot; Season Report',
        '  </div>',
        '</div>',
        '<script>', js_block, '</script>',
        '</body>',
        '</html>',
    ]
    return '\n'.join(lines)


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("Loading data...")
    schedule_df, results_df, predictions = load_all()

    print("Computing stats...")
    lb_df, adv_df, prog, agree_mx = compute_stats(schedule_df, results_df, predictions)

    human = [p for p in sorted(predictions.keys())
             if p not in ExtractAndTransform.NON_HUMAN_PLAYERS]

    print(f"\nGenerating reports for: {', '.join(human)}\n")

    for participant in human:
        print(f"  -> {participant} ... ", end="", flush=True)

        player_data = ExtractAndTransform.get_player_report_data(
            participant, results_df, predictions, schedule_df,
            lb_df, adv_df, prog, agree_mx,
        )
        # Embed ALL participants' progressions so the compare dropdown works
        player_data["all_progressions"] = {
            p: vals for p, vals in prog.items()
            if p not in ExtractAndTransform.NON_HUMAN_PLAYERS
        }

        # Compute points earned per team for Feature 4
        ALL_TEAMS = [
            "Chennai Super Kings", "Delhi Capitals", "Gujarat Titans",
            "Kolkata Knight Riders", "Lucknow Super Giants", "Mumbai Indians",
            "Punjab Kings", "Rajasthan Royals", "Royal Challengers Bengaluru",
            "Sunrisers Hyderabad"
        ]
        completed = results_df.dropna(subset=["Winner"]).reset_index(drop=True)
        preds_p   = predictions.get(participant, [])
        tp = {t: 0 for t in ALL_TEAMS}
        for idx, row in completed.iterrows():
            actual = row["Winner"]
            if actual == "NR":
                continue
            bonus = int(row.get("Bonus Points", 0) or 0)
            if idx < len(preds_p) and preds_p[idx] == actual:
                tp[actual] = tp.get(actual, 0) + (10 + bonus)
        player_data["team_points"] = tp

        # Compute per-team prediction accuracy for Feature 5 (Definition A: on matches predicted)
        ta = {t: {"correct": 0, "total": 0} for t in ALL_TEAMS}
        for idx, row in completed.iterrows():
            actual = row["Winner"]
            if actual == "NR":
                continue
            pred = preds_p[idx] if idx < len(preds_p) else None
            if pred in ta:
                ta[pred]["total"] += 1
                if pred == actual:
                    ta[pred]["correct"] += 1
        player_data["team_accuracy"] = {
            t: {
                "correct": v["correct"],
                "total": v["total"],
                "accuracy": round(v["correct"] / v["total"] * 100, 1) if v["total"] > 0 else 0.0
            }
            for t, v in ta.items()
        }

        # Compute best league match (index < 70) and best overall match
        best_league_info = None
        max_league_pts = -1
        best_overall_info = None
        max_overall_pts = -1

        for idx, row in completed.iterrows():
            actual = row["Winner"]
            match_no = int(row["Match #"])
            date_str = row["Date"]
            home_t = row["Home Team"]
            away_t = row["Away Team"]
            bonus = int(row.get("Bonus Points", 0) or 0)
            pred = preds_p[idx] if idx < len(preds_p) else None
            
            if actual == "NR":
                pts = 5
            elif pred == actual:
                pts = 10 + bonus
            else:
                pts = 0
                
            # League match (Match # <= 70)
            if match_no <= 70:
                if pts > max_league_pts:
                    max_league_pts = pts
                    best_league_info = {
                        "match_no": match_no,
                        "date": date_str,
                        "home": home_t,
                        "away": away_t,
                        "prediction": pred,
                        "winner": actual,
                        "points": pts
                    }
                elif pts == max_league_pts and best_league_info is not None:
                    best_league_info = {
                        "match_no": match_no,
                        "date": date_str,
                        "home": home_t,
                        "away": away_t,
                        "prediction": pred,
                        "winner": actual,
                        "points": pts
                    }
            
            # Overall match
            if pts > max_overall_pts:
                max_overall_pts = pts
                best_overall_info = {
                    "match_no": match_no,
                    "date": date_str,
                    "home": home_t,
                    "away": away_t,
                    "prediction": pred,
                    "winner": actual,
                    "points": pts
                }
            elif pts == max_overall_pts and best_overall_info is not None:
                best_overall_info = {
                    "match_no": match_no,
                    "date": date_str,
                    "home": home_t,
                    "away": away_t,
                    "prediction": pred,
                    "winner": actual,
                    "points": pts
                }
        player_data["best_league_match"] = best_league_info
        player_data["best_overall_match"] = best_overall_info

        # Compute stadium stats for Feature 7
        stadium_df = ExtractAndTransform.get_user_stadium_stats(
            results_df, predictions, schedule_df, participant
        )
        stadium_df = stadium_df.sort_values(by="Points", ascending=False)
        player_data["stadium_stats"] = stadium_df.to_dict(orient="records")

        # Compute No Result matches count and points (worth 5 pts each)
        nr_count = int((completed["Winner"] == "NR").sum())
        nr_points = nr_count * 5
        player_data["nr_count"] = nr_count
        player_data["nr_points"] = nr_points

        # Compute participant similarity for new feature
        similarity_list = []
        for other in human:
            if other == participant:
                continue
            preds_o = predictions.get(other, [])
            
            agreed_count = 0
            correct_p = 0
            correct_o = 0
            disagreed_count = 0
            
            for idx, row in completed.iterrows():
                actual = row["Winner"]
                # Predictions for index idx
                pred_p = preds_p[idx] if idx < len(preds_p) else None
                pred_o = preds_o[idx] if idx < len(preds_o) else None
                
                if pred_p == pred_o:
                    agreed_count += 1
                else:
                    disagreed_count += 1
                    if actual != "NR":
                        if pred_p == actual:
                            correct_p += 1
                        if pred_o == actual:
                            correct_o += 1
            
            n_comp = len(completed)
            similarity_pct = (agreed_count / n_comp * 100) if n_comp > 0 else 0.0
            similarity_list.append({
                "participant": other,
                "similarity_pct": round(similarity_pct, 1),
                "agreed_count": agreed_count,
                "total_matches": n_comp,
                "disagreed_count": disagreed_count,
                "correct_p": correct_p,
                "correct_o": correct_o
            })
        
        # Sort descending by similarity_pct, then by agreed_count
        similarity_list.sort(key=lambda x: (x["similarity_pct"], x["agreed_count"]), reverse=True)
        player_data["similarity_stats"] = similarity_list

        html = build_html(player_data)

        out = os.path.join(OUTPUT_DIR, f"{participant}_report.html")
        # Strip any surrogate characters that slipped through before writing
        html_safe = html.encode("utf-8", errors="ignore").decode("utf-8")
        with open(out, "w", encoding="utf-8") as f:
            f.write(html_safe)

        size_kb = os.path.getsize(out) / 1024
        print(f"saved ({size_kb:.1f} KB)")

    print(f"\nDone! {len(human)} reports saved in {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
