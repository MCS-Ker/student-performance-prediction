# confusion.py
# الغاية: تحليل أخطاء النموذج المعتمد عبر مصفوفة الالتباس
# يُشغَّل بعد train.py
 
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix
 
df = pd.read_csv("clean_data.csv")
X = df[["absences", "studytime", "G1", "G2"]]
y = df["Pass"]
 
# التقسيم نفسه المستخدَم في التدريب، ليكون التحليل على بيانات لم يرها النموذج
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y)
 
model = joblib.load("model.pkl")
predictions = model.predict(X_test)
 
# labels=[0, 1] تثبّت ترتيب الصفوف والأعمدة
# الصفّ الأول للمتعثّرين والثاني للناجحين
matrix = confusion_matrix(y_test, predictions, labels=[0, 1])
 
# قراءة الخلايا الأربع
# ravel تفكّ المصفوفة إلى أربع قيم متتابعة
caught, missed_alarm, missed_student, correct_pass = matrix.ravel()
 
print("=== مصفوفة الالتباس ===")
print("")
print("                     | تنبّأ: متعثّر | تنبّأ: ناجح")
print("الواقع: متعثّر       | " + str(caught).ljust(12) + " | " + str(missed_alarm))
print("الواقع: ناجح         | " + str(missed_student).ljust(12) + " | " + str(correct_pass))
 
print("")
print("=== قراءة الخلايا ===")
print("متعثّرون اكتُشفوا بنجاح : " + str(caught))
print("متعثّرون فاتوا النظام   : " + str(missed_alarm) + "   <-- الخطأ الأخطر")
print("ناجحون أُنذر عنهم خطأً  : " + str(missed_student) + "   <-- الخطأ الأقل ضرراً")
print("ناجحون صُنّفوا بصواب    : " + str(correct_pass))
 
print("")
print("=== لماذا نميّز بين نوعي الخطأ؟ ===")
print("الخطأ الأول: متعثّر لم يُكتشف، فيُحرم من الدعم وقد يرسب")
print("الخطأ الثاني: ناجح أُنذر عنه، فيتلقى دعماً لا يحتاجه")
print("الأول يضرّ الطالب، والثاني يكلّف المؤسسة وقتاً فقط")
print("ولذلك نُفضّل نموذجاً يقلّل الخطأ الأول ولو زاد الثاني")
 
total_at_risk = caught + missed_alarm
print("")
print("=== الخلاصة ===")
print("عدد المتعثّرين في بيانات الاختبار: " + str(total_at_risk))
print("اكتشف النظام منهم: " + str(caught))
print("نسبة الاكتشاف: " + str(round(caught / total_at_risk * 100, 1)) + "%")
 