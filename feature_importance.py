# feature_importance.py
# الغاية: تحليل أثر كل ميزة في قرار النموذج
 
import pandas as pd
import joblib
 
df = pd.read_csv("clean_data.csv")
features = ["absences", "studytime", "G1", "G2"]
 
model = joblib.load("model.pkl")
 
# coef_ تحتوي معامل كل ميزة
# مصفوفة من صفّ واحد لأن التصنيف ثنائي، لذلك نأخذ [0]
coefficients = model.coef_[0]
 
print("=== 1. المعاملات الخام ===")
print("المعامل الموجب يرفع احتمال النجاح، والسالب يرفع احتمال الرسوب")
print("")
print("الميزة      | المعامل  | الاتجاه")
for name, coef in zip(features, coefficients):
    direction = "يرفع النجاح" if coef > 0 else "يرفع الرسوب"
    print(name.ljust(11) + " | " + str(round(coef, 4)).ljust(8) + " | " + direction)
 
print("")
print("=== 2. لماذا لا تُقارن المعاملات الخام مباشرة؟ ===")
print("لأن كل معامل يصف أثر وحدة واحدة من ميزته، ووحدات الميزات مختلفة")
print("")
print("الميزة      | أصغر قيمة | أكبر قيمة | الانحراف المعياري")
for name in features:
    print(name.ljust(11) + " | " +
         str(df[name].min()).ljust(9) + " | " +
         str(df[name].max()).ljust(9) + " | " +
         str(round(df[name].std(), 2)))
 
print("")
print("=== 3. الأهمية بعد توحيد المقياس ===")
print("نضرب كل معامل بالانحراف المعياري لميزته")
print("فنحصل على أثر تغيّر نموذجي في كل ميزة، وتصبح المقارنة عادلة")
print("")
 
# القيمة المطلقة ، قوة الأثر لا اتجاهه
weights = []
for name, coef in zip(features, coefficients):
    weights.append(abs(coef) * df[name].std())
 
total = sum(weights)
 
print("الميزة      | الأهمية")
for name, weight in zip(features, weights):
    percent = round(weight / total * 100, 1)
    print(name.ljust(11) + " | " + str(percent) + "%")
 
print("")
print("=== 4. أمثلة على قراءة المعاملات ===")
for name, coef in zip(features, coefficients):
    print("كل زيادة بمقدار وحدة في " + name + " تغيّر لوغاريتم الأرجحية بمقدار " + str(round(coef, 4)))
 