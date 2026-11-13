"""Public pages required for app-store submission: privacy policy, terms, support.

Contact email comes from env SUPPORT_EMAIL (set it on Render); nothing personal is hard-coded.
"""
import os

APP = "Faraid – Hanafi Inheritance Calculator (فرائض)"

CSS = ("body{font-family:system-ui,'Noto Nastaliq Urdu',sans-serif;max-width:46rem;margin:0 auto;"
       "padding:1rem 16px 3rem;line-height:1.7;color:#1d2b24;background:#fbfaf6}"
       "h1{color:#1f5e45}h2{margin-top:2rem;color:#1f5e45}.ur{direction:rtl;text-align:right;"
       "border-top:1px solid #ccc;margin-top:2rem;padding-top:1rem}a{color:#1f5e45}"
       "@media(prefers-color-scheme:dark){body{background:#14201a;color:#e6efe9}h1,h2,a{color:#8fd3b0}}")


def _page(title: str, en: str, ur: str) -> str:
    return (f"<!doctype html><html lang='en'><head><meta charset='utf-8'>"
            f"<meta name='viewport' content='width=device-width,initial-scale=1'>"
            f"<title>{title}</title><style>{CSS}</style></head><body>"
            f"<h1>{title}</h1>{en}<div class='ur' lang='ur'>{ur}</div></body></html>")


def _email() -> str:
    e = os.environ.get("SUPPORT_EMAIL", "").strip()
    return f"<a href='mailto:{e}'>{e}</a>" if e else "(support email to be added by the operator)"


def privacy() -> str:
    en = f"""
<p><b>{APP}</b> is a calculator that divides an estate among heirs according to Hanafi fiqh.
Last updated: 13 November 2026.</p>
<h2>What we receive</h2>
<p>Only what you type or your AI assistant sends for a calculation: which heirs exist and how many,
optional names you give them, optional amounts (estate, funeral costs, debts, bequest) and a title.
We do <b>not</b> receive your chat history, your account, location, contacts, passwords, payment
card data, health data or government ID numbers, and the tool asks for none of them.</p>
<h2>How it is used</h2>
<p>Solely to compute the shares and to produce the Excel file and printable naqsha page you asked for.
No advertising, no profiling, no sale or sharing of data, no use for model training.</p>
<h2>Retention</h2>
<p>Calculations are done in memory and not stored in a database. If a naqsha file is created, it is kept
on the server for <b>24 hours</b> under a random private link and then deleted automatically.
Anyone who has the link can open it during that time, so share it carefully.
Our hosting provider (Render) may keep ordinary technical server logs (time, URL, IP address) for a short period.</p>
<h2>Your control</h2>
<p>Do not create a naqsha file if you do not want one stored. To have a file deleted earlier, contact us
with its link. No account or sign-in exists, so there is nothing else to delete.</p>
<h2>Children</h2><p>The service is not directed at children.</p>
<h2>Contact</h2><p>{_email()}</p>"""
    ur = f"""
<h2>رازداری کی پالیسی</h2>
<p>یہ سروس صرف وہی معلومات لیتی ہے جو حساب کے لیے بھیجی جائیں: ورثاء اور ان کی تعداد، اختیاری نام، اختیاری رقوم
(ترکہ، تجہیز و تکفین، قرض، وصیت) اور عنوان۔ آپ کی چیٹ، اکاؤنٹ، مقام، پاس ورڈ، کارڈ، صحت یا شناختی نمبر نہیں لیے جاتے۔</p>
<p>معلومات صرف حساب اور نقشہ بنانے کے لیے استعمال ہوتی ہیں؛ اشتہار، پروفائلنگ، فروخت یا تربیتِ ماڈل کے لیے نہیں۔</p>
<p>حساب میموری میں ہوتا ہے، ڈیٹا بیس میں محفوظ نہیں۔ نقشے کی فائل ایک بے ترتیب نجی لنک پر <b>24 گھنٹے</b> رہتی ہے،
پھر خود حذف ہو جاتی ہے؛ لنک جس کے پاس ہو وہ اس دوران کھول سکتا ہے۔ جلد حذف کرانے کے لیے رابطہ کریں: {_email()}</p>"""
    return _page("Privacy Policy", en, ur)


def terms() -> str:
    en = f"""
<p>{APP} is a <b>calculation aid, not a fatwa and not legal advice</b>. Results follow the Hanafi school
(as in Aasan Siraji) and rely on the facts you provide. Not covered: dhawil-arham, unborn child, missing person,
khuntha, mawla, impediments to inheritance (murder, slavery, difference of religion), the Sahibayn muqasama with a
grandfather, great-grandchildren. Before dividing a real estate, confirm the result with a qualified mufti and, where
required, a lawyer. The service is provided "as is", without warranty; the operator is not liable for decisions made
from its output.</p><p>Contact: {_email()}</p>"""
    ur = """
<p>یہ سروس صرف حساب میں مدد ہے، <b>فتویٰ یا قانونی مشورہ نہیں</b>۔ نتیجہ حنفی فقہ پر اور آپ کی دی ہوئی معلومات پر مبنی ہے۔
حقیقی ترکے کی تقسیم سے پہلے کسی مستند مفتی (اور ضرورت ہو تو وکیل) سے تصدیق ضرور کروائیں۔</p>"""
    return _page("Terms of Use", en, ur)


def support() -> str:
    en = f"""
<p>Questions, bugs or deletion requests: {_email()}</p>
<p>How to use: ask your AI assistant, e.g. "Wife, 2 sons, 1 daughter and mother; estate 1,000,000; make the naqsha."
For several deaths in a row (munasakha) describe who died in which order.</p>"""
    ur = f"<p>سوال، خرابی یا فائل حذف کرنے کی درخواست: {_email()}</p>"
    return _page("Support", en, ur)


def home() -> str:
    en = """
<p>Calculates Islamic inheritance (faraid) according to Hanafi fiqh: fixed shares, asaba, exclusion, awl, radd,
Umariyyatayn, and several deaths in a row (munasakha) with one combined naqsha as Excel and a printable page.</p>
<h2>Use it in ChatGPT or Claude</h2>
<p>Add this MCP server URL as a custom connector (no sign-in needed):</p>
<p><code>https://inheritance-mcp.onrender.com/mcp</code></p>
<p>Then ask, for example: "Wife, two sons, one daughter and mother survive; estate 1,000,000; make the naqsha."</p>
<p><b><a href='/calculator'>Open the web calculator (no AI needed) / ویب کیلکولیٹر کھولیں</a></b></p>
<p>Not a fatwa: confirm with a qualified mufti.</p>
<p><a href='/privacy'>Privacy</a> · <a href='/terms'>Terms</a> · <a href='/support'>Support</a></p>"""
    ur = """
<p>حنفی فقہ کے مطابق وراثت (فرائض) اور مناسخہ کا حساب، ایکسل اور پرنٹ ہونے والے نقشے کے ساتھ۔
اوپر دیا گیا MCP لنک ChatGPT یا Claude میں کسٹم کنیکٹر کے طور پر شامل کریں اور اپنا مسئلہ لکھیں۔
یہ فتویٰ نہیں؛ مستند مفتی سے تصدیق کروائیں۔</p>"""
    return _page("Faraid – Hanafi Inheritance Calculator", en, ur)
