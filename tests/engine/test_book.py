# -*- coding: utf-8 -*-
"""کتاب الفرائض (آسان سراجی) کی مثالیں — صفحہ نمبر چھپے ہوئے صفحات کے ہیں۔"""
from book_helper import check

CASES = []
def C(*a, **k): CASES.append(check(*a, **k))

# ---- عول (ص 160-164) ----
C("ص160 (1) شوہر+2 حقیقی بہنیں → 6 عول 7", {"husband":1,"full_sister":2}, "F", asl=7, shares={"husband":3,"full_sister":4})
C("ص160 (2) شوہر+2 علاتی+1 اخیافی → 6 عول 8", {"husband":1,"cons_sister":2,"ut_sister":1}, "F", asl=8, shares={"husband":3,"cons_sister":4,"ut_sister":1})
C("ص160 (3) شوہر+2 حقیقی+2 اخیافی بہنیں → عول 9", {"husband":1,"full_sister":2,"ut_sister":2}, "F", asl=9, shares={"husband":3,"full_sister":4,"ut_sister":2})
C("ص161 (4) شوہر+ماں+2 علاتی+2 اخیافی → عول 10", {"husband":1,"mother":1,"cons_sister":2,"ut_sister":2}, "F", asl=10, shares={"husband":3,"mother":1,"cons_sister":4,"ut_sister":2})
C("ص162 (1) بیوی+2 حقیقی بہنیں+1 اخیافی → 12 عول 13", {"wife":1,"full_sister":2,"ut_sister":1}, "M", asl=13, shares={"wife":3,"full_sister":8,"ut_sister":2})
C("ص162 (2) بیوی+2 علاتی+2 اخیافی → عول 15", {"wife":1,"cons_sister":2,"ut_sister":2}, "M", asl=15, shares={"wife":3,"cons_sister":8,"ut_sister":4})
C("ص162 (3) ماں+بیوی+2 حقیقی+2 اخیافی → عول 17", {"mother":1,"wife":1,"full_sister":2,"ut_sister":2}, "M", asl=17, shares={"mother":2,"wife":3,"full_sister":8,"ut_sister":4})
C("ص163 منبریہ: بیوی+2 بیٹیاں+ماں+باپ → 24 عول 27", {"wife":1,"daughter":2,"mother":1,"father":1}, "M", asl=27, shares={"wife":3,"daughter":16,"mother":4,"father":4})

# ---- تصحیح (ص 173-177) ----
C("ص173 ماں+باپ+2 بیٹیاں → 6، بغیر ضرب", {"mother":1,"father":1,"daughter":2}, "F", asl=6, total=6, shares={"mother":1,"father":1,"daughter":4})
C("ص174 ماں+باپ+10 بیٹیاں → تصحیح 30 مضروب 5", {"mother":1,"father":1,"daughter":10}, "F", asl=6, total=30, shares={"mother":5,"father":5,"daughter":20})
C("ص174 شوہر+6 بیٹیاں+ماں+باپ → 12 عول 15 تصحیح 45", {"husband":1,"daughter":6,"mother":1,"father":1}, "F", asl=15, total=45, shares={"husband":9,"daughter":24,"mother":6,"father":6})
C("ص175 5 بیٹیاں+ماں+باپ → تصحیح 30", {"daughter":5,"mother":1,"father":1}, "M", asl=6, total=30, shares={"daughter":20,"mother":5,"father":5})
C("ص176 شوہر+5 حقیقی بہنیں → عول 7 تصحیح 35", {"husband":1,"full_sister":5}, "F", asl=7, total=35, shares={"husband":15,"full_sister":20})

# ---- متعدد اعداد رؤوس (ص 178-185) ----
C("ص178 بیوی+6 چچا → اصل 4 تصحیح 8 (تداخل)", {"wife":1,"full_uncle":6}, "M", asl=4, total=8, shares={"wife":2,"full_uncle":6})
C("ص180 6 بیٹیاں+3 دادیاں+3 چچا → 6 تصحیح 18 (تماثل)", {"daughter":6,"grandmother_p":3,"full_uncle":3}, "M", asl=6, total=18, shares={"daughter":12,"grandmother_p":3,"full_uncle":3})
C("ص181 4 بیویاں+3 دادیاں+12 چچا → 12 تصحیح 144 مضروب 12", {"wife":4,"grandmother_p":3,"full_uncle":12}, "M", asl=12, total=144, shares={"wife":36,"grandmother_p":24,"full_uncle":84})
C("ص183 4 بیویاں+18 بیٹیاں+15 دادیاں+6 چچا → 24 تصحیح 4320 مضروب 180", {"wife":4,"daughter":18,"grandmother_p":15,"full_uncle":6}, "M", asl=24, total=4320, shares={"wife":540,"daughter":2880,"grandmother_p":720,"full_uncle":180})
C("ص185 2 بیویاں+6 دادیاں+10 بیٹیاں+7 چچا → 24 تصحیح 5040 مضروب 210", {"wife":2,"grandmother_p":6,"daughter":10,"full_uncle":7}, "M", asl=24, total=5040, shares={"wife":630,"grandmother_p":840,"daughter":3360,"full_uncle":210})

# ---- رد: قسم اول تا سوم (ص 209-216) ----
C("ص209 2 بیٹیاں → 2", {"daughter":2}, "M", asl=2, shares={"daughter":2})
C("ص210 دادی+اخیافی بہن → رد 2", {"grandmother_p":1,"ut_sister":1}, "M", asl=2, shares={"grandmother_p":1,"ut_sister":1})
C("ص211 ماں+2 اخیافی بہنیں → رد 3", {"mother":1,"ut_sister":2}, "F", asl=3, shares={"mother":1,"ut_sister":2})
C("ص211 ماں+بیٹی → رد 4", {"mother":1,"daughter":1}, "M", asl=4, shares={"mother":1,"daughter":3})
C("ص211 ماں+2 بیٹیاں → رد 5", {"mother":1,"daughter":2}, "M", asl=5, shares={"mother":1,"daughter":4})
C("ص212 بیٹی+پوتی+ماں → رد 5", {"daughter":1,"granddaughter":1,"mother":1}, "M", asl=5, shares={"daughter":3,"granddaughter":1,"mother":1})
C("ص212 حقیقی بہن+ماں → رد 5", {"full_sister":1,"mother":1}, "M", asl=5, shares={"full_sister":3,"mother":2})
C("ص214 شوہر+3 بیٹیاں → 4", {"husband":1,"daughter":3}, "F", asl=4, total=4, shares={"husband":1,"daughter":3})
C("ص214 بیوی+7 بیٹیاں → 8", {"wife":1,"daughter":7}, "M", asl=8, total=8, shares={"wife":1,"daughter":7})
C("ص215 شوہر+6 بیٹیاں → 4 تصحیح 8", {"husband":1,"daughter":6}, "F", asl=4, total=8, shares={"husband":2,"daughter":6})
C("ص215 شوہر+5 بیٹیاں → 4 تصحیح 20", {"husband":1,"daughter":5}, "F", asl=4, total=20, shares={"husband":5,"daughter":15})
C("ص216 بیوی+10 بیٹیاں → 8 تصحیح 80", {"wife":1,"daughter":10}, "M", asl=8, total=80, shares={"wife":10,"daughter":70})

# ---- رد: قسم رابع (ص 217-220) ----
C("ص218 بیوی+4 دادیاں+6 اخیافی بہنیں → 4، رد، تصحیح 48", {"wife":1,"grandmother_p":4,"ut_sister":6}, "M", total=48, shares={"wife":12,"grandmother_p":12,"ut_sister":24})
C("ص218 بیوی+ماں+اخیافی بھائی+اخیافی بہن → 4", {"wife":1,"mother":1,"ut_brother":1,"ut_sister":1}, "M", total=4, shares={"wife":1,"mother":1,"ut_brother":1,"ut_sister":1})
C("ص220 4 بیویاں+9 بیٹیاں+6 دادیاں → تصحیح 1440 مضروب 36", {"wife":4,"daughter":9,"grandmother_p":6}, "M", total=1440, shares={"wife":180,"daughter":1008,"grandmother_p":252})

if __name__ == "__main__":
    bad = 0
    for n, ok, m in CASES:
        print(("OK  " if ok else "FAIL"), n, "|", m)
        bad += (not ok)
    print(f"\n{len(CASES)-bad}/{len(CASES)} درست")
    raise SystemExit(1 if bad else 0)
