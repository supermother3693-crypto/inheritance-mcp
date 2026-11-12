# -*- coding: utf-8 -*-
"""رشتوں کی فہرست (Relation catalogue) — اردو / گجراتی / عربی نام اور متبادل الفاظ۔

ہر رشتے کا ایک کوڈ ہے۔ `ORDER` نقشے میں وارثوں کی ترتیب طے کرتا ہے
(شوہر/بیوی دائیں سے شروع، پھر والدین، اولاد، بہن بھائی ... بالکل نمونوں کی طرح)۔
"""
import re

# code: (gender, ur, gu, ar, [aliases...])
_REL = [
    ("husband", "M", "شوہر", "પતિ", "زوج", ["شوہر", "خاوند", "میاں", "زوج", "husband", "પતિ"]),
    ("wife", "F", "بیوی", "પત્ની", "زوجہ", ["بیوی", "زوجہ", "بیگم", "wife", "પત્ની", "wives", "بیویاں"]),
    ("father", "M", "باپ", "પિતા", "اب", ["باپ", "والد", "ابا", "ابو", "اب", "father", "પિતા", "બાપ"]),
    ("mother", "F", "ماں", "માતા", "ام", ["ماں", "والدہ", "امی", "ام", "mother", "માતા", "મા", "માં"]),
    ("grandfather", "M", "دادا", "દાદા", "جد صحیح", ["دادا", "جد", "جد صحیح", "paternal grandfather", "grandfather", "દાદા"]),
    ("grandmother_m", "F", "نانی", "નાની", "جدہ لامی", ["نانی", "جدہ لامی", "جده لامیه", "جدہ صحیحہ مادری", "maternal grandmother", "નાની"]),
    ("grandmother_p", "F", "دادی", "દાદી", "جدہ ابوی", ["دادی", "جدہ ابوی", "جده ابویه", "جدہ صحیحہ پدری", "paternal grandmother", "દાદી"]),
    ("son", "M", "بیٹا", "દીકરો", "ابن", ["بیٹا", "بیٹے", "ابن", "پسر", "son", "sons", "દીકરો"]),
    ("daughter", "F", "بیٹی", "દીકરી", "بنت", ["بیٹی", "بیٹیاں", "بنت", "دختر", "daughter", "daughters", "દીકરી"]),
    ("grandson", "M", "پوتا", "પૌત્ર", "ابن الابن", ["پوتا", "پوتے", "ابن الابن", "grandson", "son's son", "પૌત્ર"]),
    ("granddaughter", "F", "پوتی", "પૌત્રી", "بنت الابن", ["پوتی", "پوتیاں", "بنت الابن", "granddaughter", "son's daughter", "પૌત્રી"]),
    ("full_brother", "M", "حقیقی بھائی", "ભાઈ", "اخ شقیق", ["بھائی", "حقیقی بھائی", "سگا بھائی", "عینی بھائی", "اخ شقیق", "اخ لاب وام", "full brother", "brother", "ભાઈ"]),
    ("full_sister", "F", "حقیقی بہن", "બહેન", "اخت شقیقہ", ["بہن", "حقیقی بہن", "سگی بہن", "عینی بہن", "اخت شقیقہ", "اخت لاب وام", "full sister", "sister", "બહેન"]),
    ("cons_brother", "M", "علاتی بھائی", "અલાતી ભાઈ", "اخ لاب", ["علاتی بھائی", "باپ شریک بھائی", "اخ لاب", "consanguine brother", "half brother paternal", "અલાતી ભાઈ"]),
    ("cons_sister", "F", "علاتی بہن", "અલાતી બહેન", "اخت لاب", ["علاتی بہن", "باپ شریک بہن", "اخت لاب", "consanguine sister", "half sister paternal", "અલાતી બહેન"]),
    ("ut_brother", "M", "اخیافی بھائی", "અખ્યાફી ભાઈ", "اخ لام", ["اخیافی بھائی", "ماں شریک بھائی", "اخ لام", "uterine brother", "અખ્યાફી ભાઈ"]),
    ("ut_sister", "F", "اخیافی بہن", "અખ્યાફી બહેન", "اخت لام", ["اخیافی بہن", "ماں شریک بہن", "اخت لام", "uterine sister", "અખ્યાફી બહેન"]),
    ("full_nephew", "M", "بھتیجا", "ભત્રીજો", "ابن الاخ", ["بھتیجا", "بھتیجے", "حقیقی بھتیجا", "ابن الاخ", "ابن اخ شقیق", "nephew", "brother's son", "ભત્રીજો"]),
    ("cons_nephew", "M", "علاتی بھتیجا", "અલાતી ભત્રીજો", "ابن الاخ لاب", ["علاتی بھتیجا", "ابن اخ لاب", "consanguine nephew", "અલાતી ભત્રીજો"]),
    ("full_uncle", "M", "چچا", "કાકા", "عم", ["چچا", "حقیقی چچا", "عم", "uncle", "paternal uncle", "કાકા"]),
    ("cons_uncle", "M", "علاتی چچا", "અલાતી કાકા", "عم لاب", ["علاتی چچا", "عم لاب", "consanguine uncle", "અલાતી કાકા"]),
    ("full_cousin", "M", "چچازاد بھائی", "કાકા નો છોકરો", "ابن العم", ["چچازاد", "چچا زاد", "چچازاد بھائی", "چچا زاد بھائی", "چچا کا بیٹا", "ابن العم", "cousin", "uncle's son", "કાકા નો છોકરો"]),
    ("cons_cousin", "M", "علاتی چچا کا بیٹا", "અલાતી કાકા નો છોકરો", "ابن العم لاب", ["علاتی چچازاد", "علاتی چچا کا بیٹا", "ابن العم لاب", "consanguine cousin", "અલાતી કાકા નો છોકરો"]),
]

ORDER = [r[0] for r in _REL]
INFO = {r[0]: {"gender": r[1], "ur": r[2], "gu": r[3], "ar": r[4]} for r in _REL}


def norm(s: str) -> str:
    s = s.strip().lower()
    s = s.replace("ي", "ی").replace("ى", "ی").replace("ك", "ک").replace("ہ", "ه").replace("ۃ", "ه")
    s = s.replace("ە", "ه").replace("ة", "ه").replace("ۂ", "ه")
    s = re.sub(r"[‌‍ً-ٰٟ]", "", s)
    s = re.sub(r"\s+", " ", s)
    return s


ALIASES = {}
for code, g, ur, gu, ar, al in _REL:
    for a in al + [ur, gu, ar, code]:
        ALIASES[norm(a)] = code


def rel_code(word: str) -> str:
    k = norm(word)
    if k in ALIASES:
        return ALIASES[k]
    raise KeyError(word)


def rel_label(code: str, lang: str = "ur") -> str:
    return INFO[code][lang if lang in ("ur", "gu", "ar") else "ur"]


def rel_gender(code: str) -> str:
    return INFO[code]["gender"]
