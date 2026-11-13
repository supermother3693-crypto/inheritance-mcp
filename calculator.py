"""Web calculator (no AI needed): a mobile-friendly Urdu form that calls the SAME engine as the MCP tools."""
import json
import time
from collections import defaultdict, deque

from faraid.engine import FaraidError
from faraid.relations import INFO, ORDER
from service import solve_munasakha, solve_simple

LIMIT_PER_MIN = 30
_hits: dict[str, deque] = defaultdict(deque)


def allowed(ip: str) -> bool:
    """Tiny per-IP rate limit so the free server cannot be flooded."""
    now = time.time()
    q = _hits[ip]
    while q and now - q[0] > 60:
        q.popleft()
    if len(q) >= LIMIT_PER_MIN:
        return False
    q.append(now)
    if len(_hits) > 5000:
        _hits.clear()
    return True


def _num(v, default=0.0) -> float:
    try:
        x = float(v or 0)
    except (TypeError, ValueError):
        raise FaraidError("رقم درست نہیں۔")
    if x < 0 or x > 1e15:
        raise FaraidError("رقم درست نہیں۔")
    return x


def api_simple(data: dict) -> dict:
    counts = {}
    for rel, n in (data.get("counts") or {}).items():
        if rel not in ORDER:
            raise FaraidError("نامعلوم وارث۔")
        n = int(n or 0)
        if n < 0 or n > 30:
            raise FaraidError("تعداد 0 سے 30 کے درمیان ہو۔")
        counts[rel] = n
    return solve_simple(
        counts, data.get("deceased", ""), _num(data.get("estate")), _num(data.get("funeral")),
        _num(data.get("debts")), _num(data.get("bequest")), naqsha=bool(data.get("naqsha")),
        lang="ur", title=str(data.get("title", ""))[:80], deceased_name=str(data.get("name", ""))[:60],
    )


def api_munasakha(data: dict) -> dict:
    text = str(data.get("text", ""))
    if not text.strip() or len(text) > 20000:
        raise FaraidError("متن خالی یا بہت لمبا ہے۔")
    return solve_munasakha(text, _num(data.get("estate")), _num(data.get("funeral")),
                           _num(data.get("debts")), _num(data.get("bequest")),
                           make_naqsha=bool(data.get("naqsha", True)), lang="ur")


SAMPLE = """مورث: زید | جنس: مرد
بیوی: سارہ
بیٹا: بکر، عمر
بیٹی: مریم

مورث: بکر
بیوی: ہاجرہ
بیٹا: خالد
بیٹی: آمنہ"""


def page() -> str:
    rels = json.dumps([[k, INFO[k]["ur"]] for k in ORDER], ensure_ascii=False)
    return PAGE.replace("__RELS__", rels).replace("__SAMPLE__", json.dumps(SAMPLE, ensure_ascii=False))


PAGE = r"""<!doctype html><html lang="ur" dir="rtl"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>فرائض کیلکولیٹر</title>
<style>
:root{--g:#1f5e45;--bg:#fbfaf6;--fg:#1d2b24;--card:#fff;--bd:#d9d6c9}
@media(prefers-color-scheme:dark){:root{--bg:#14201a;--fg:#e6efe9;--card:#1b2b23;--bd:#34473c;--g:#8fd3b0}}
body{margin:0;font-family:system-ui,'Noto Nastaliq Urdu','Jameel Noori Nastaleeq',sans-serif;background:var(--bg);color:var(--fg);line-height:1.9}
main{max-width:46rem;margin:0 auto;padding:12px 16px 60px}h1{color:var(--g);font-size:1.5rem}
.tabs{display:flex;gap:8px;margin:12px 0}.tabs button{flex:1;padding:10px;border:1px solid var(--bd);background:var(--card);color:var(--fg);border-radius:10px;font:inherit}
.tabs button.on{background:var(--g);color:#fff;border-color:var(--g)}
.card{background:var(--card);border:1px solid var(--bd);border-radius:12px;padding:12px;margin:10px 0}
.row{display:flex;align-items:center;justify-content:space-between;gap:8px;padding:4px 0}
input,select,textarea{font:inherit;padding:8px;border:1px solid var(--bd);border-radius:8px;background:var(--bg);color:var(--fg);box-sizing:border-box}
input[type=number]{width:5.5rem;text-align:center}textarea{width:100%;min-height:14rem;direction:rtl}
.money input{width:100%}.money label{display:block;margin-top:6px}
.go{width:100%;padding:12px;margin-top:10px;background:var(--g);color:#fff;border:0;border-radius:10px;font:inherit;font-size:1.1rem}
table{width:100%;border-collapse:collapse}td,th{border-bottom:1px solid var(--bd);padding:6px 4px;text-align:right}
.err{color:#b3261e;font-weight:bold}.note{font-size:.9rem;opacity:.85}a{color:var(--g)}.hide{display:none}
</style></head><body><main>
<h1>فرائض کیلکولیٹر (حنفی)</h1>
<p class="note">حنفی فقہ کے مطابق وراثت کا حساب۔ یہ فتویٰ نہیں؛ تقسیم سے پہلے مستند مفتی سے تصدیق کروائیں۔</p>
<div class="tabs"><button id="t1" class="on">ایک وفات</button><button id="t2">مناسخہ (کئی وفات)</button></div>

<section id="p1"><div class="card"><b>میت</b>
<div class="row"><span>جنس</span><select id="gender"><option value="">خود طے ہو (شوہر/بیوی سے)</option><option value="male">مرد</option><option value="female">عورت</option></select></div></div>
<div class="card"><b>زندہ ورثاء کی تعداد</b><div id="rels"></div></div></section>

<section id="p2" class="hide"><div class="card"><b>مناسخہ کا متن</b>
<p class="note">ہر وفات کا ایک حصہ: «مورث: نام»، پھر رشتے۔ بعد والا مورث پہلے حصے میں وارث ہونا چاہیے۔ نیچے نمونہ بھرا ہوا ہے، اسے بدل لیں۔</p>
<textarea id="text"></textarea></div></section>

<div class="card money"><b>رقم (اختیاری)</b>
<label>کل ترکہ<input id="estate" type="number" inputmode="decimal" min="0"></label>
<label>تجہیز و تکفین<input id="funeral" type="number" inputmode="decimal" min="0"></label>
<label>قرض<input id="debts" type="number" inputmode="decimal" min="0"></label>
<label>وصیت (ایک تہائی تک)<input id="bequest" type="number" inputmode="decimal" min="0"></label>
<label><input id="naqsha" type="checkbox"> ایکسل اور پرنٹ ہونے والا نقشہ بھی بنائیں</label></div>
<button class="go" id="go">حساب کریں</button>
<div id="out"></div>
<p class="note"><a href="/">ہوم</a> · <a href="/privacy">رازداری</a> · <a href="/terms">شرائط</a> · <a href="/support">رابطہ</a></p>
</main>
<script>
const RELS=__RELS__, SAMPLE=__SAMPLE__;
let mode=1;const $=id=>document.getElementById(id);
$('rels').innerHTML=RELS.map(([k,u])=>`<div class="row"><span>${u}</span><input type="number" min="0" max="30" value="0" data-r="${k}"></div>`).join('');
$('text').value=SAMPLE;
function tab(m){mode=m;$('p1').classList.toggle('hide',m!=1);$('p2').classList.toggle('hide',m!=2);$('t1').classList.toggle('on',m==1);$('t2').classList.toggle('on',m==2);$('out').innerHTML='';if(m==2)$('naqsha').checked=true}
$('t1').onclick=()=>tab(1);$('t2').onclick=()=>tab(2);
const esc=s=>String(s??'').replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]));
const money=v=>Number(v).toLocaleString('en-IN',{maximumFractionDigits:2});
function files(f){if(!f)return'';let h='<div class="card"><b>نقشہ</b><br>';
 h+=`<a href="${f.naqsha_page_url}" target="_blank">نقشہ کھولیں اور PDF محفوظ کریں</a><br><a href="${f.excel_url}">Excel ڈاؤن لوڈ کریں</a>`;
 if(f.pdf_url)h+=`<br><a href="${f.pdf_url}">PDF ڈاؤن لوڈ</a>`;return h+'<br><span class="note">لنک 24 گھنٹے کارآمد ہیں۔</span></div>'}
function showSimple(r){const hasAmt=r.estate&&r.estate.distributable>0;
 let h=`<div class="card"><b>نتیجہ</b><br>اصل مسئلہ: ${r.result.asl_masala} · تصحیح: ${r.result.tashih}`+(r.result.awl?' · عول':'')+(r.result.radd?' · رد':'')+'</div>';
 h+='<div class="card"><table><tr><th>وارث</th><th>تعداد</th><th>حصہ</th><th>فیصد</th>'+(hasAmt?'<th>رقم</th>':'')+'</tr>';
 for(const x of r.heirs){h+=`<tr><td>${esc(x.label_ur)}${x.status=='محروم'?' (محروم: '+esc(x.reason)+')':''}</td><td>${x.count}</td><td dir="ltr">${x.share_fraction}</td><td>${x.share_percent}%</td>`+(hasAmt?`<td>${money(x.amount)}</td>`:'')+'</tr>'}
 h+='</table></div>';if(r.notes&&r.notes.length)h+='<div class="card note">'+r.notes.map(esc).join('<br>')+'</div>';
 return h+files(r.files)}
function showMun(r){const hasAmt=r.estate&&r.estate.distributable>0;
 let h=`<div class="card"><b>جامعہ: ${r.jamia}</b></div><div class="card"><table><tr><th>وارث</th><th>سہام</th><th>حصہ</th>`+(hasAmt?'<th>رقم</th>':'')+'</tr>';
 for(const p of r.people){h+=`<tr><td>${esc(p.name)}<br><span class="note">${esc(p.relation_ur)} — ${esc(p.heir_of)}</span></td><td>${p.parts}</td><td dir="ltr">${p.share_fraction}</td>`+(hasAmt?`<td>${money(p.amount)}</td>`:'')+'</tr>'}
 h+='</table></div>';const bad=r.verification.filter(v=>!v.ok);
 h+=`<div class="card note">${bad.length?'<span class="err">جانچ میں مسئلہ: '+bad.map(v=>esc(v.check)).join('، ')+'</span>':'تمام جانچیں کامیاب۔'}</div>`;
 return h+files(r.files)}
$('go').onclick=async()=>{const out=$('out');out.innerHTML='<p>حساب ہو رہا ہے… (پہلی بار سرور جاگنے میں ایک منٹ لگ سکتا ہے)</p>';
 const base={estate:$('estate').value,funeral:$('funeral').value,debts:$('debts').value,bequest:$('bequest').value,naqsha:$('naqsha').checked};
 let url,body;
 if(mode==1){const counts={};document.querySelectorAll('[data-r]').forEach(i=>{if(+i.value>0)counts[i.dataset.r]=+i.value});
  url='/api/simple';body={...base,counts,deceased:$('gender').value}}
 else{url='/api/munasakha';body={...base,text:$('text').value}}
 try{const res=await fetch(url,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
  const j=await res.json();if(!res.ok||j.error){out.innerHTML='<p class="err">'+esc(j.error||'خرابی')+'</p>';return}
  out.innerHTML=(mode==1?showSimple(j):showMun(j))+'<p class="note">'+esc(j.disclaimer)+'</p>'}
 catch(e){out.innerHTML='<p class="err">سرور سے رابطہ نہیں ہو سکا، دوبارہ کوشش کریں۔</p>'}};
</script></body></html>"""
