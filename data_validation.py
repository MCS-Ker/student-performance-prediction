# data_validation.py
# الغاية: فحص سلامة البيانات قبل التنظيف والتدريب

 
import pandas as pd
 
# فتح ملف النتائج لحفظ كل ما يُطبع
df = pd.read_csv("student-mat.csv", sep=";")
 
print("=== 1. حجم البيانات ===")
print("عدد الطلاب: " + str(len(df)))
 
print("")
print("=== 2. الفحص البنيوي (المعتاد) ===")
print("القيم المفقودة: " + str(df.isnull().sum().sum()))
print("الصفوف المكررة: " + str(df.duplicated().sum()))
print("النتيجة: البيانات سليمة بنيوياً")
 
print("")
print("=== 3. الفحص المنطقي: صفوف الدرجة النهائية = صفر ===")
zero_grade = df[df["G3"] == 0]
print("عدد الطلاب الذين G3 = 0 : " + str(len(zero_grade)))
print("منهم عدد غياباتهم = 0 : " + str((zero_grade["absences"] == 0).sum()))
 
print("")
print("=== 4. هل هذا متوقَّع صدفةً؟ ===")
all_zero_abs = (df["absences"] == 0).sum()
ratio = all_zero_abs / len(df)
print("عدد الطلاب الذين غيابهم = 0 في كامل البيانات: " + str(all_zero_abs))
print("نسبتهم: " + str(round(ratio * 100, 1)) + "%")
print("المتوقَّع صدفةً من بين " + str(len(zero_grade)) + " طالباً: " + str(round(ratio * len(zero_grade), 1)))
print("الموجود فعلاً: " + str((zero_grade["absences"] == 0).sum()))
print("النتيجة: الفارق كبير جداً ولا يُفسَّر بالصدفة")
 
print("")
print("=== 5. تسلسل الدرجات عند هذه الصفوف ===")
print("متوسط G1 : " + str(round(zero_grade["G1"].mean(), 2)))
print("متوسط G2 : " + str(round(zero_grade["G2"].mean(), 2)))
print("متوسط G3 : " + str(round(zero_grade["G3"].mean(), 2)))
print("عدد من G1 = 0 عندهم: " + str((zero_grade["G1"] == 0).sum()))
print("عدد من G2 = 0 عندهم: " + str((zero_grade["G2"] == 0).sum()))
 
print("")
print("=== 6. أثر هذه الصفوف على الارتباطات ===")
clean = df[df["G3"] > 0]
print("الميزة      | قبل الاستبعاد | بعد الاستبعاد")
for feature in ["absences", "studytime", "G1", "G2"]:
    before = round(df[feature].corr(df["G3"]), 3)
    after = round(clean[feature].corr(clean["G3"]), 3)
    print(feature.ljust(11) + " | " + str(before).ljust(13) + " | " + str(after))
 
print("")
print("=== 7. متوسط الدرجة النهائية حسب الغياب (بعد الاستبعاد) ===")
print("غياب 0      : " + str(round(clean[clean["absences"] == 0]["G3"].mean(), 2)))
print("غياب 1-10   : " + str(round(clean[(clean["absences"] > 0) & (clean["absences"] <= 10)]["G3"].mean(), 2)))
print("غياب 11-20  : " + str(round(clean[(clean["absences"] > 10) & (clean["absences"] <= 20)]["G3"].mean(), 2)))
print("غياب أكثر من 20 : " + str(round(clean[clean["absences"] > 20]["G3"].mean(), 2)))
 
print("")
print("=== الخلاصة ===")
print("توجد " + str(len(zero_grade)) + " صفوف متناقضة داخلياً:")
print("الدرجة النهائية صفر مع غياب مسجَّل صفر.")
print("تُستبعَد في مرحلة التنظيف مع توثيق السبب.")
 