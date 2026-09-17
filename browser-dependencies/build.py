"""Build only the manually redacted public summary; never read private evidence."""
from pathlib import Path
import html
import json

ROOT = Path(__file__).resolve().parent
r = json.loads((ROOT / 'report.json').read_text())
e = lambda value: html.escape(str(value), quote=True)
LABELS = {
    'audit': {'complete': '審核完成', 'in_progress': '審核進行中'},
    'deployment': {'not_deployed': '修補尚未部署', 'deployed': '修補已部署'},
    'tests': {'pending': '測試待完成', 'passed': '限定範圍測試通過'},
    'browser_cleanup': {'not_performed': '瀏覽器清理未執行', 'partial': '瀏覽器清理部分完成', 'complete': '已確認範圍清理完成'},
}
state = {key: LABELS[key][value] for key, value in r['state'].items()}
status = f"{state['audit']}；{state['deployment']}／{state['tests']}"
packages = r['packages']
advisories = {a['id']: a for a in r['advisories']}
assert len(advisories) == len(r['advisories']), 'Duplicate advisory ID'
assert len({p['name'].lower() for p in packages}) == len(packages)
refs = [key for p in packages for key in p['advisories']]
assert set(refs) == set(advisories), 'Missing or unreferenced advisory'
version_key = lambda v: tuple(int(x) for x in v.split('.'))
counts = {**r['counts'], 'packages': len(packages), 'advisories': len(advisories), 'matches': len(refs),
          'lock_fixed_installed_old': sum(version_key(p['locked']) >= version_key(p['fixed']) > version_key(p['installed']) for p in packages)}

def link(url, title):
    assert url.startswith('https://'), 'Only HTTPS public source links allowed'
    return f'<a href="{e(url)}" target="_blank" rel="noopener noreferrer">{e(title)} ↗</a>'

def advisory_card(a):
    links = [link(a['url'], '原始／維護者公告'), link('https://api.osv.dev/v1/vulns/' + a.get('osv_id', a['id']), 'OSV 範圍')]
    links += [link(s['url'], s['title']) for s in a.get('extra_sources', [])]
    return f'<article class="advisory"><h4>{e(a["title"])}</h4><p class="micro">{e(a["id"])} · 此項修復 {e(a["fixed"])}</p><p>{e(a["condition"])}</p><div class="source-links">{"".join(links)}</div></article>'

cards = []
for p in packages:
    cards.append(f'''<details class="package" id="pkg-{e(p['name'].lower())}"><summary><span class="package-name">{e(p['name'])}</span><span class="package-meta">實裝 {e(p['installed'])} → 修復界線 {e(p['fixed'])}</span><span class="micro">{len(p['advisories'])} 筆命中 · 展開前提與來源</span></summary><div class="package-body"><p class="version">審核時 lock：{e(p['locked'])}。修復界線不是已驗收的升級目標。</p><p>{e(p['context'])}</p><p class="recommendation"><strong>建議</strong>{e(p['recommendation'])}</p>{''.join(advisory_card(advisories[key]) for key in p['advisories'])}</div></details>''')

stats = ''.join(f'<div><b>{value}</b><span>{label}</span></div>' for value, label in [
    (counts['browser_daemons'], '背景 daemon'), (counts['public_packages_scanned'], '公共套件實掃'),
    (counts['packages'], '命中套件'), (counts['advisories'], '去重安全公告')])
browser_cards = ''.join(f'<article class="note"><h3>{e(x["title"])}</h3><p>{e(x["body"])}</p></article>' for x in r['browser'])
steps = ''.join(f'<li><h3>{e(x["title"])}</h3><p>{e(x["body"])}</p></li>' for x in r['next_steps'])
limits = ''.join(f'<li>{e(x)}</li>' for x in r['limits'])
sources = ''.join(f'<li>{link(x["url"], x["title"])}</li>' for x in r['sources'])
css = '''
:root{--paper:#f4efe4;--ink:#252924;--muted:#60645c;--line:#d8d2c5;--gold:#9a6219;--panel:#fffaf0;--deep:#26392f}
*{box-sizing:border-box}html{scroll-behavior:smooth;scroll-padding-top:28px}body{margin:0;background:var(--paper);color:var(--ink);font:17px/1.85 -apple-system,BlinkMacSystemFont,"PingFang TC","Noto Sans TC",sans-serif;overflow-wrap:anywhere}a{color:var(--gold);text-underline-offset:4px}a:focus-visible,summary:focus-visible{outline:3px solid var(--gold);outline-offset:4px}.wrap{max-width:960px;margin:auto;padding:0 42px}.top{border-bottom:1px solid var(--line)}.top .wrap{display:flex;justify-content:space-between;gap:18px;align-items:center;min-height:64px}.top a{font-size:14px}.top span,.eyebrow{font-size:12px;letter-spacing:.12em;color:var(--muted)}header{padding:52px 0 30px}.eyebrow{color:var(--gold);font-weight:700}h1{font:750 clamp(36px,6vw,60px)/1.25 "Songti TC","Noto Serif TC",serif;letter-spacing:-.03em;margin:18px 0}h2{font-size:27px;line-height:1.45;margin:0 0 18px}h3{font-size:19px;line-height:1.6;margin:0 0 9px}h4{font-size:17px;margin:0 0 5px}p{margin:0 0 16px}.thesis{font-size:25px;line-height:1.6;margin:0 0 20px}.intro,.lead{color:var(--muted)}.status{background:var(--deep);color:#fff9eb;padding:20px 23px;margin:24px 0}.status strong{display:block;color:#e3b56b;font-size:13px;letter-spacing:.1em;margin-bottom:5px}.status p{margin:0}.status small{display:block;margin-top:8px;color:#efe5d2}.stats{display:grid;grid-template-columns:repeat(4,1fr);border-block:1px solid var(--line);margin:28px 0 0}.stats>div{padding:19px 16px;border-right:1px solid var(--line)}.stats>div:last-child{border:0}.stats b{display:block;font-size:32px;line-height:1.4;font-variant-numeric:tabular-nums}.stats span{font-size:13px;color:var(--muted)}.toc{display:flex;flex-wrap:wrap;gap:8px 22px;border-bottom:1px solid var(--line);padding:0 0 25px}.toc a{min-height:44px;display:flex;align-items:center;font-size:15px}.section{padding:38px 0;border-bottom:1px solid var(--line)}.number{display:block;color:var(--gold);font-size:12px;letter-spacing:.14em;margin-bottom:8px}.note{padding:20px 0}.note+.note{border-top:1px solid var(--line)}.note p{margin-bottom:0}.callout{border-left:3px solid var(--gold);padding:8px 0 8px 18px;margin:20px 0;color:var(--muted)}.package{background:var(--panel);border:1px solid var(--line);margin:14px 0}.package summary{cursor:pointer;padding:20px 23px}.package summary::marker{color:var(--gold)}.package-name{font-size:22px;font-weight:700}.package-meta{display:block;margin-top:6px;font-size:15px}.micro{display:block;font-size:13px;color:var(--muted);line-height:1.7}.package-body{padding:0 23px 22px}.version{font-size:14px;color:var(--muted);padding-top:16px;border-top:1px solid var(--line)}.recommendation{border-left:3px solid var(--gold);padding-left:14px}.recommendation strong{display:block;color:var(--gold);font-size:13px}.advisory{padding-top:20px;margin-top:20px;border-top:1px solid var(--line)}.advisory p{margin-bottom:12px}.source-links{display:flex;flex-wrap:wrap;gap:3px 18px}.source-links a{font-size:14px;display:inline-flex;min-height:44px;align-items:center}.steps{list-style:none;counter-reset:step;padding:0}.steps li{counter-increment:step;padding:22px 0;border-top:1px solid var(--line)}.steps h3::before{content:counter(step,decimal-leading-zero) " / ";color:var(--gold)}.limits{padding-left:22px}.limits li{margin:12px 0}footer{padding:30px 0 55px;font-size:14px;color:var(--muted)}footer ul{padding-left:20px}footer li{padding:6px 0}.privacy{border-top:1px solid var(--line);padding-top:20px;margin-top:24px}.pill{font-size:13px;color:var(--gold)}
@media(max-width:760px){body{font-size:16.5px;line-height:1.85}.wrap{padding:0 24px}.top .wrap{gap:12px;flex-wrap:wrap;padding-top:12px;padding-bottom:12px}.top span{font-size:11px}header{padding:35px 0 25px}h1{font-size:36px}h2{font-size:25px}.thesis{font-size:22px}.status{padding:18px}.stats{grid-template-columns:1fr 1fr}.stats>div{padding:17px 15px}.stats>div:nth-child(2){border-right:0}.stats>div:nth-child(-n+2){border-bottom:1px solid var(--line)}.section{padding:32px 0}.package summary{padding:18px}.package-body{padding:0 18px 20px}.package-name{font-size:21px}.package-meta{font-size:14px}.toc{gap:2px 18px}.source-links{gap:2px 14px}}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}}
'''
page = f'''<!doctype html>
<html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><meta name="theme-color" content="#f4efe4"><meta name="description" content="瀏覽器背景程序與 Python 依賴安全審核的公開刪節摘要：區分版本命中、利用前提與尚未部署的修補。"><title>{e(r['title'])} · {e(r['date'])}</title><style>{css}</style></head>
<body><div class="top"><div class="wrap"><a href="../">← 前輪深度清理驗收</a><span>{e(r['date'])} · 後續審核</span></div></div><main class="wrap" id="top"><header><div class="eyebrow">HERMES / FOLLOW-UP REVIEW</div><h1>{e(r['title'])}</h1><p class="thesis">{e(r['subtitle'])}</p><p class="intro">{e(r['scope'])}</p><div class="status" data-audit="{e(r['state']['audit'])}" data-deployment="{e(r['state']['deployment'])}" data-tests="{e(r['state']['tests'])}"><strong>目前狀態</strong><p>{e(status)}</p><small>{e(state['browser_cleanup'])}。狀態依本次審核時點呈現，非即時監控。</small></div><div class="stats">{stats}</div></header>
<nav class="toc" aria-label="章節導覽"><a href="#browser">瀏覽器</a><a href="#dependencies">依賴與公告</a><a href="#next">處理順序</a><a href="#limits">查核界線</a></nav>
<section class="section" id="browser"><span class="number">01 / BROWSER</span><h2>{e(r['browser_heading'])}</h2><p class="lead">{e(r['browser_lead'])}</p>{browser_cards}<p class="callout">判斷核心是目前的工作與資源權屬，不是程序年齡、父程序已退出，或建立來源已結案。</p></section>
<section class="section" id="dependencies"><span class="number">02 / DEPENDENCIES</span><h2>{counts['packages']} 個套件，風險要看前提。</h2><p class="lead">{counts['public_packages_scanned']} 個公共套件實掃，產生 {counts['matches']} 筆「套件 × 公告」命中；httpx2 與 httpcore2 共用一項，因此去重為 {counts['advisories']} 項公告。</p><p>{counts['lock_fixed_installed_old']} 個套件的 lock 已含修復版，正式安裝卻仍舊；httpx2／httpcore2 則連 lock 都停在舊版。<strong>只看 lock 更新或依賴相容檢查通過，不能當成修補已部署。</strong></p><p class="pill">點開套件，看利用條件、修復版本與原始連結。</p>{''.join(cards)}</section>
<section class="section" id="next"><span class="number">03 / NEXT STEPS</span><h2>建議順序，不是已完成事項。</h2><p class="lead">{e(status)}。以下仍是後續處置建議。</p><ol class="steps">{steps}</ol></section>
<section class="section" id="limits"><span class="number">04 / BOUNDARIES</span><h2>哪些已確認，哪些還不知道。</h2><ul class="limits">{limits}</ul></section>
<footer><h3>參考文件</h3><p>每項安全公告的原始連結與 OSV 範圍，放在對應套件的展開卡片內。</p><ul>{sources}</ul><p class="privacy"><strong>這是公開網頁。</strong>noindex 只要求搜尋引擎不收錄，不是存取保護。此頁僅含手工挑選的刪節資料，不含帳號識別、憑證、原始命令、環境、設定或日誌。</p><p>{e(r['date'])} · {e(status)} · {e(state['browser_cleanup'])}</p><a href="../">回到前輪驗收紀錄</a> · <a href="#top">回頁首</a></footer></main></body></html>
'''
(ROOT / 'index.html').write_text(page)
print(json.dumps({'counts': counts, 'state': r['state'], 'bytes': len(page.encode())}, ensure_ascii=False))
