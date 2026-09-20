# cross_validation.py
# الغاية: التحقق من ثبات النتائج عبر تقسيمات متعددة
# يُشغَّل بعد train.py

import pandas as pd
from sklearn.model_selection import cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import make_scorer, recall_score

df = pd.read_csv("clean_data.csv")
X = df[["absences", "studytime", "G1", "G2"]]
y = df["Pass"]

# مقياس مخصّص: نسبة اكتشاف المتعثّرين
# pos_label=0 لأن الراسب يحمل القيمة صفر في عمود الهدف
risk_recall = make_scorer(recall_score, pos_label=0)

print("=== لماذا التحقق المتقاطع؟ ===")
print("في train.py قسّمنا البيانات مرة واحدة فقط")
print("وقد يكون ذلك التقسيم محظوظاً أو سيّئ الحظ بالصدفة")
print("فالتحقق المتقاطع يقسّم البيانات خمسة أجزاء")
print("ويستخدم كل جزء للاختبار مرة، والباقي للتدريب")
print("فيُختبر كل طالب مرة واحدة بالضبط، وتُحسب النتيجة خمس مرات")

models = {
    "Logistic Regression": LogisticRegression(class_weight="balanced", max_iter=1000),
    "Random Forest": RandomForestClassifier(random_state=42, class_weight="balanced"),
}

for name, model in models.items():
    accuracy_scores = cross_val_score(model, X, y, cv=5)
    recall_scores = cross_val_score(model, X, y, cv=5, scoring=risk_recall)

    print("")
    print("=== " + name + " ===")
    print("الدقة في الطيّات الخمس: " + str([round(float(score), 3) for score in accuracy_scores]))
    print("المتوسط: " + str(round(accuracy_scores.mean(), 3)))
    print("الانحراف المعياري: " + str(round(accuracy_scores.std(), 3)))
    print("")
    print("اكتشاف المتعثّرين في الطيّات الخمس: " + str([round(float(score), 3) for score in recall_scores]))
    print("المتوسط: " + str(round(recall_scores.mean(), 3)))

print("")
print("=== الخلاصة ===")
print("الانحراف المعياري الصغير يعني نتائج ثابتة لا تعتمد على التقسيم")
print("والفارق في اكتشاف المتعثّرين هو مبرر اختيار الانحدار اللوجستي")
print("فهو يكتشف نسبة أعلى منهم في كل طيّة تقريباً")