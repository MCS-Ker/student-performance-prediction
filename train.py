import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
 
df = pd.read_csv("clean_data.csv")
 
# الميزات الأربع المعتمدة، والهدف
X = df[["absences", "studytime", "G1", "G2"]]
y = df["Pass"]
 
# تقسيم البيانات: 80% تدريب و 20% اختبار
# stratify=y يحافظ على نسبة الناجحين إلى الراسبين في القسمين
# random_state=42 يثبّت العشوائية ليحصل أي شخص على النتائج نفسها
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y)
 
print("عدد طلاب التدريب: " + str(len(X_train)))
print("عدد طلاب الاختبار: " + str(len(X_test)))
 
def evaluate(name, model):
    """تدرّب النموذج وتقيس أداءه وتطبع النتائج"""
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)
 
    print("")
    print("=== " + name + " ===")
    print("Accuracy  : " + str(round(accuracy_score(y_test, predictions), 3)))
    print("Precision : " + str(round(precision_score(y_test, predictions), 3)))
    print("Recall    : " + str(round(recall_score(y_test, predictions), 3)))
    print("F1-score  : " + str(round(f1_score(y_test, predictions), 3)))
    # نسبة المتعثرين الذين نجح النموذج في اكتشافهم
    print("Recall للمتعثّرين : " + str(round(recall_score(y_test, predictions, pos_label=0), 3)))
    return model
 
print("")
print("========== خط الأساس ==========")
print("نموذج ساذج يتنبأ دائماً بالصنف الأكثر شيوعاً")
print("أي نموذج لا يتفوّق عليه فهو بلا قيمة")
evaluate("Baseline", DummyClassifier(strategy="most_frequent"))
 
print("")
print("========== النماذج الثلاثة ==========")
 
# class_weight="balanced"  وزن أكبر للصنف الأقل عدد (الراسبين)
logistic = evaluate("Logistic Regression",
                    LogisticRegression(class_weight="balanced", max_iter=1000))
 
forest = evaluate("Random Forest",
                  RandomForestClassifier(random_state=42, class_weight="balanced"))
 
# StandardScaler ضروري هنا وحده لأن KNN يعتمد على المسافات
knn = evaluate("K-Nearest Neighbors",
               make_pipeline(StandardScaler(), KNeighborsClassifier()))
 
print("")
print("========== النموذج المعتمد ==========")
print("المعتمد: Logistic Regression")
print("السبب: يكتشف جميع المتعثّرين دون استثناء")
print("وهدف النظام إنذار مبكر، وتفويت متعثّر أخطر من إنذار كاذب")
 
joblib.dump(logistic, "model.pkl")
print("")
print("تم حفظ النموذج في model.pkl")
 