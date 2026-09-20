# cross_dataset.py
# الغاية: اختبار النموذج على مجموعة بيانات مختلفة
# التدريب على طلاب الرياضيات، والاختبار على طلاب اللغة البرتغالية
 
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.dummy import DummyClassifier
from sklearn.metrics import accuracy_score, recall_score
 
features = ["absences", "studytime", "G1", "G2"]
 
# بيانات التدريب: الرياضيات، بعد تطبيق معيار التنظيف
math = pd.read_csv("student-mat.csv", sep=";")
math = math[~((math["G3"] == 0) & (math["absences"] == 0))]
math["Pass"] = (math["G3"] >= 10).astype(int)
 
# بيانات الاختبار: البرتغالية، بالمعيار نفسه
port = pd.read_csv("student-por.csv", sep=";")
 
print("=== فحص الاتساق في الملف البرتغالي ===")
print("عدد الطلاب:", len(port))
print("درجتهم النهائية صفر:", (port["G3"] == 0).sum())
print("ومنهم غيابهم صفر:", ((port["G3"] == 0) & (port["absences"] == 0)).sum())
 
port = port[~((port["G3"] == 0) & (port["absences"] == 0))]
port["Pass"] = (port["G3"] >= 10).astype(int)
 
# استبعاد الطلاب المسجلين في المادتين، منعاً لتسريب البيانات
shared_keys = ["school", "sex", "age", "address", "famsize", "Pstatus",
               "Medu", "Fedu", "Mjob", "Fjob", "reason", "nursery", "internet"]
 
# indicator يضيف عموداً يبيّن هل وُجد نظير الطالب في ملف الرياضيات
combined = port.merge(math[shared_keys], on=shared_keys, how="left", indicator=True)
port_only = combined[combined["_merge"] == "left_only"].drop_duplicates()
 
print()
print("=== استبعاد الطلاب المشتركين ===")
print("مسجلون في المادتين:", len(port) - len(port_only))
print("البرتغالية فقط:", len(port_only))
 
X_train = math[features]
y_train = math["Pass"]
X_test = port_only[features]
y_test = port_only["Pass"]
 
model = LogisticRegression(class_weight="balanced", max_iter=1000)
model.fit(X_train, y_train)
predictions = model.predict(X_test)
 
baseline = DummyClassifier(strategy="most_frequent")
baseline.fit(X_train, y_train)
 
print()
print("=== النتائج ===")
print("خط الأساس:", round(accuracy_score(y_test, baseline.predict(X_test)), 3))
print("النموذج  :", round(accuracy_score(y_test, predictions), 3))
print("اكتشاف المتعثّرين:", round(recall_score(y_test, predictions, pos_label=0), 3))
 