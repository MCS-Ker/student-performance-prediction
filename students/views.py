from django.shortcuts import render
from django.http import HttpResponse
import joblib
import os
import csv
from .models import Student, Course, StudentRecord
from django.contrib.auth.decorators import login_required


# تحميل النموذج المدرب مرة واحدة عند تشغيل الخادم
MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "model.pkl")
model = joblib.load(MODEL_PATH)

# عتبات تصنيف الخطر وحد الغياب، معرفة في مكان واحد
HIGH_RISK_THRESHOLD = 60
MEDIUM_RISK_THRESHOLD = 40
ABSENCE_LIMIT = 15


def get_fail_probability(record):
    """تحسب احتمال الرسوب لسجل واحد بالنسبة المئوية"""
    features = [[record.absences, record.studytime, record.g1(), record.g2()]]
    return round(model.predict_proba(features)[0][0] * 100, 1)


def classify_risk(fail_percent):
    """تصنف مستوى الخطر وتعيد التسمية وأصناف التنسيق"""
    if fail_percent >= HIGH_RISK_THRESHOLD:
        return "خطر مرتفع", "table-danger", "bg-danger"
    elif fail_percent >= MEDIUM_RISK_THRESHOLD:
        return "خطر متوسط", "table-warning", "bg-warning text-dark"
    else:
        return "وضع مستقر", "", "bg-success"


@login_required
def predict_all(request):
    """صفحة نتائج التنبؤ لجميع السجلات"""
    results = []

    for record in StudentRecord.objects.all():
        fail_percent = get_fail_probability(record)
        risk_level, css_class, badge = classify_risk(fail_percent)

        results.append({
            "student": record.student.name,
            "course": record.course.title,
            "absences": record.absences,
            # تنبيه إداري مستقل عن النموذج، يُطلق عند تجاوز الحد المسموح
            "absences_alert": record.absences > ABSENCE_LIMIT,
            "g1": record.g1(),
            "g2": record.g2(),
            "fail_probability": fail_percent,
            "risk_level": risk_level,
            "css_class": css_class,
            "badge": badge,
        })

    return render(request, "students/predictions.html", {"results": results})


@login_required
def export_csv(request):
    """تصدير نتائج التنبؤ إلى ملف CSV يفتح في إكسل"""

    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="predictions.csv"'

    # علامة ترتيب البايتات، تجبر إكسل على قراءة النص العربي بترميز UTF-8
    # بدونها تظهر الحروف العربية مشوهة عند الفتح في إكسل
    response.write("\ufeff")

    writer = csv.writer(response)

    writer.writerow([
        "الرقم الجامعي", "الطالب", "المقرر", "عدد الغيابات",
        "وقت الدراسة الأسبوعي", "تقييم الفترة الأولى", "تقييم الفترة الثانية",
        "احتمال الرسوب %", "مستوى الخطر", "تجاوز حد الغياب",
    ])

    for record in StudentRecord.objects.all():
        fail_percent = get_fail_probability(record)
        risk_level, css_class, badge = classify_risk(fail_percent)

        writer.writerow([
            record.student.student_id,
            record.student.name,
            record.course.title,
            record.absences,
            record.studytime,
            record.g1(),
            record.g2(),
            fail_percent,
            risk_level,
            "نعم" if record.absences > ABSENCE_LIMIT else "لا",
        ])

    return response


@login_required
def add_record(request):
    """إدخال بيانات طالب مع الحماية من الكتابة فوق سجل موجود"""

    saved_name = None
    was_updated = False

    if request.method == "POST":
        student = Student.objects.get(id=request.POST["student"])
        course = Course.objects.get(id=request.POST["course"])

        # البحث عن سجل سابق لنفس الطالب في نفس المقرر
        # first تعيد أول نتيجة أو None إن لم توجد نتائج
        existing = StudentRecord.objects.filter(student=student, course=course).first()

        # إن وُجد سجل سابق ولم يؤكد المدرس بعد، نعرض صفحة المقارنة ولا نحفظ شيئاً
        if existing and request.POST.get("confirm") != "yes":
            return render(request, "students/confirm_update.html", {
                "student": student,
                "course": course,
                "existing": existing,
                "new_absences": request.POST["absences"],
                "new_studytime": request.POST["studytime"],
                "new_assignment1": request.POST["assignment1"],
                "new_quiz1": request.POST["quiz1"],
                "new_assignment2": request.POST["assignment2"],
                "new_quiz2": request.POST["quiz2"],
            })

        # نصل هنا إما لأن السجل جديد، وإما لأن المدرس أكد التحديث
        record, created = StudentRecord.objects.update_or_create(
            student=student,
            course=course,
            defaults={
                "absences": request.POST["absences"],
                "studytime": request.POST["studytime"],
                "assignment1": request.POST["assignment1"],
                "quiz1": request.POST["quiz1"],
                "assignment2": request.POST["assignment2"],
                "quiz2": request.POST["quiz2"],
            }
        )

        saved_name = student.name
        was_updated = not created

    # قائمة الأزواج الموجودة مسبقاً بصيغة "رقم الطالب-رقم المقرر"
    # تُرسل إلى المتصفح ليتحقق منها لحظة الاختيار دون إرسال الصفحة
    existing_pairs = []
    for record in StudentRecord.objects.all():
        existing_pairs.append(str(record.student.id) + "-" + str(record.course.id))

    return render(request, "students/add_record.html", {
        "students": Student.objects.all(),
        "courses": Course.objects.all(),
        "saved_name": saved_name,
        "was_updated": was_updated,
        "existing_pairs": existing_pairs,
    })


@login_required
def dashboard(request):
    """لوحة التحليلات: صورة كلية عن حالة الطلاب وأداء النموذج"""

    high_risk = 0
    medium_risk = 0
    stable = 0
    absence_alerts = 0
    students_list = []

    for record in StudentRecord.objects.all():
        fail_percent = get_fail_probability(record)
        risk_level, css_class, badge = classify_risk(fail_percent)

        if fail_percent >= HIGH_RISK_THRESHOLD:
            high_risk += 1
        elif fail_percent >= MEDIUM_RISK_THRESHOLD:
            medium_risk += 1
        else:
            stable += 1

        if record.absences > ABSENCE_LIMIT:
            absence_alerts += 1

        students_list.append({
            "student": record.student.name,
            "course": record.course.title,
            "absences": record.absences,
            "fail_probability": fail_percent,
            "risk_level": risk_level,
            "badge": badge,
        })

    total = len(students_list)

    # نعرض من هم في دائرة الخطر فقط، لأن القائمة قائمة عمل لا قائمة عرض
    at_risk = []
    for item in students_list:
        if item["fail_probability"] >= MEDIUM_RISK_THRESHOLD:
            at_risk.append(item)

    at_risk.sort(key=lambda item: item["fail_probability"], reverse=True)

    # حساب النسب المئوية لأشرطة التوزيع
    # الشرط يمنع القسمة على صفر حين لا توجد بيانات
    if total > 0:
        high_percent = round(high_risk / total * 100, 1)
        medium_percent = round(medium_risk / total * 100, 1)
        stable_percent = round(stable / total * 100, 1)
    else:
        high_percent = 0
        medium_percent = 0
        stable_percent = 0

    # أهمية الميزات، مأخوذة من مخرجات feature_importance.py
    feature_importance = [
        {"name": "تقييم الفترة الثانية", "value": 67.3, "color": "bg-primary"},
        {"name": "تقييم الفترة الأولى", "value": 20.4, "color": "bg-info"},
        {"name": "عدد الغيابات", "value": 7.2, "color": "bg-secondary"},
        {"name": "وقت الدراسة الأسبوعي", "value": 5.1, "color": "bg-secondary"},
    ]

    # مقاييس أداء النموذج، مأخوذة من مخرجات train.py و cross_validation.py
    model_metrics = {
        "name": "الانحدار اللوجستي",
        "accuracy": 90.2,
        "risk_recall": 93.6,
        "baseline": 73.6,
    }

    return render(request, "students/dashboard.html", {
        "total": total,
        "high_risk": high_risk,
        "medium_risk": medium_risk,
        "stable": stable,
        "absence_alerts": absence_alerts,
        "high_percent": high_percent,
        "medium_percent": medium_percent,
        "stable_percent": stable_percent,
        "top_risky": at_risk,
        "feature_importance": feature_importance,
        "model_metrics": model_metrics,
    })


