import pandas as pd

# UCI - الفواصل منقوطة في هذه المجموعة
df = pd.read_csv("student-mat.csv", sep=";")

print("عدد الصفوف:", df.shape[0])
print("عدد الأعمدة:", df.shape[1])
print()

print("=== أسماء الأعمدة ===")
for col in df.columns:
    print("-", col)

print()
print("=== القيم المفقودة ===")
print(df.isnull().sum().sum())

print()
print("=== الصفوف المكررة ===")
print(df.duplicated().sum())


# --- فحص الارتباط بين الميزات والهدف ---
print()
print("=== الارتباط مع الدرجة النهائية G3 ===")
features = ["absences", "studytime", "G1", "G2"]
for f in features:
    print(f, ":", round(df[f].corr(df["G3"]), 3))