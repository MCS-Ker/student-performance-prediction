# hypothesis_testing.py
# الغاية: اختبار الفرضيات البديلة قبل استبعاد الصفوف المتناقضة

 
import pandas as pd
 
df = pd.read_csv("student-mat.csv", sep=";")
 
# عمود مساعد: هل درجة الطالب النهائية صفر؟
df["zero"] = (df["G3"] == 0)
 
# عمود مساعد: وسطي الفترتين الأولى والثانية
df["avg"] = (df["G1"] + df["G2"]) / 2
 
def test_threshold(column_name, title):
    """تفحص وجود عتبة فاصلة في عمود معيّن.
    العتبة موجودة إذا كان أعلى قيمة عند المصفَّرين
    أقلّ من أدنى قيمة عند غير المصفَّرين."""
    print("")
    print("=== " + title + " ===")
    highest_zero = df[df["zero"]][column_name].max()
    lowest_normal = df[~df["zero"]][column_name].min()
    print("أعلى قيمة عند المصفَّرين    : " + str(highest_zero))
    print("أدنى قيمة عند غير المصفَّرين : " + str(lowest_normal))
    if highest_zero < lowest_normal:
        print("النتيجة: توجد عتبة فاصلة - الفرضية مقبولة")
    else:
        overlap = ((~df["zero"]) & (df[column_name] <= highest_zero)).sum()
        print("النتيجة: تداخل - الفرضية مرفوضة")
        print("عدد غير المصفَّرين داخل مجال المصفَّرين: " + str(overlap))
 
print("=== اختبار الفرضيات البديلة ===")
print("السؤال: هل يوجد سبب في البيانات يفسّر تصفير الدرجة النهائية؟")
 
# الفرضية الأولى والثانية والثالثة
test_threshold("G2", "الفرضية 1: عتبة على درجة الفترة الثانية G2")
test_threshold("G1", "الفرضية 2: عتبة على درجة الفترة الأولى G1")
test_threshold("avg", "الفرضية 3: عتبة على وسطي الفترتين")
 
# تفصيل الفرضية الثالثة
print("")
print("=== تفصيل الفرضية 3: التوزيع حسب الوسطي ===")
print("الوسطي | مصفَّر | غير مصفَّر")
for value in sorted(df["avg"].unique()):
    group = df[df["avg"] == value]
    zero_count = group["zero"].sum()
    normal_count = len(group) - zero_count
    if value <= 11:
        print(str(value).ljust(6) + " | " + str(zero_count).ljust(6) + " | " + str(normal_count))
 
# الفرضية الرابعة: المقارنة المطابَقة
print("")
print("=== الفرضية 4: المقارنة المطابَقة ===")
print("نقارن طلاباً وسطيهم متطابق لكن مصيرهم مختلف")
print("")
print("الوسطي | مصفَّر | غير مصفَّر | غياب المصفَّرين | غياب الآخرين | دراسة المصفَّرين | دراسة الآخرين")
 
for value in sorted(df["avg"].unique()):
    group = df[df["avg"] == value]
    zero_group = group[group["zero"]]
    normal_group = group[~group["zero"]]
    # نعرض المستويات التي تضمّ الفئتين معاً فقط
    if len(zero_group) > 0 and len(normal_group) > 0:
        print(str(value).ljust(6) + " | " +
             str(len(zero_group)).ljust(6) + " | " +
             str(len(normal_group)).ljust(10) + " | " +
             str(round(zero_group["absences"].mean(), 1)).ljust(15) + " | " +
             str(round(normal_group["absences"].mean(), 1)).ljust(12) + " | " +
             str(round(zero_group["studytime"].mean(), 2)).ljust(16) + " | " +
             str(round(normal_group["studytime"].mean(), 2)))
 
print("")
print("=== وقت الدراسة: هل يفرّق بين الفئتين؟ ===")
print("القيمة | نسبتها عند المصفَّرين | نسبتها عند غير المصفَّرين")
for value in [1, 2, 3, 4]:
    zero_ratio = (df[df["zero"]]["studytime"] == value).mean()
    normal_ratio = (df[~df["zero"]]["studytime"] == value).mean()
    print(str(value).ljust(6) + " | " +
         str(round(zero_ratio * 100, 1)).ljust(21) + " | " +
         str(round(normal_ratio * 100, 1)))
 
print("")
print("=== الخلاصة ===")
print("الفرضيات 1 و 2 و 3: مرفوضة - لا توجد عتبة فاصلة في الدرجات")
print("وقت الدراسة: توزيع متقارب - لا يفسّر التصفير")
print("المقارنة المطابَقة: المصفَّرون غيابهم صفر في كل مستوى دون استثناء")
print("بينما زملاؤهم بالدرجة نفسها غيابهم بين 5 و 12")
print("")
print("النتيجة: لا يوجد تفسير سلوكي للتصفير.")
print("والغياب الصفري ليس سبباً بل علامة على خلل في التسجيل.")
print("لذلك يُستبعَد هؤلاء الطلاب استناداً إلى التناقض الداخلي لا إلى النتيجة.")
 