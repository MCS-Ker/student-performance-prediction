from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, Http404
from django.contrib.auth.decorators import login_required
import joblib
import os
import csv
from .models import Student, Course, StudentRecord
 
 
# تحميل النموذج مرة واحدة عند تشغيل السيرفر
MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "model.pkl")
model = joblib.load(MODEL_PATH)
 
HIGH_RISK_THRESHOLD = 60
MEDIUM_RISK_THRESHOLD = 40
ABSENCE_LIMIT = 12
DECLINE_LIMIT = 1
 
 
def get_fail_probability(record):
    features = [[record.absences, record.studytime, record.g1(), record.g2()]]
    return round(model.predict_proba(features)[0][0] * 100, 1)
 
 
def classify_risk(fail_percent):
    if fail_percent >= HIGH_RISK_THRESHOLD:
        return "خطر مرتفع", "table-danger", "bg-danger"
    elif fail_percent >= MEDIUM_RISK_THRESHOLD:
        return "خطر متوسط", "table-warning", "bg-warning text-dark"
    else:
        return "وضع مستقر", "", "bg-success"
 
 
# تنبيه الغياب منفصل عن النموذج
def is_absence_alert(record):
    return record.absences >= ABSENCE_LIMIT
 
 
# الادمن يرى كل المقررات والمعلم يرى مقرراته فقط
def visible_courses(user):
    if user.is_superuser:
        return Course.objects.all()
    return Course.objects.filter(teacher=user)
 
 
def visible_records(user):
    if user.is_superuser:
        return StudentRecord.objects.all()
    return StudentRecord.objects.filter(course__teacher=user)
 
 
@login_required
def predict_all(request):
    results = []
 
    for record in visible_records(request.user):
        fail_percent = get_fail_probability(record)
        risk_level, css_class, badge = classify_risk(fail_percent)
 
        results.append({
            "student": record.student.name,
            "course": record.course.title,
            "absences": record.absences,
            "absences_alert": is_absence_alert(record),
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
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="predictions.csv"'
 
    # بدون هذا السطر يظهر العربي مشوه بالاكسل
    response.write("﻿")
 
    writer = csv.writer(response)
 
    writer.writerow([
        "الرقم الجامعي", "الطالب", "المقرر", "عدد الغيابات",
        "وقت الدراسة الأسبوعي", "تقييم الفترة الأولى", "تقييم الفترة الثانية",
        "احتمال الرسوب %", "مستوى الخطر", "بلغ حد الغياب",
    ])
 
    for record in visible_records(request.user):
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
            "نعم" if is_absence_alert(record) else "لا",
        ])
 
    return response
 
 
@login_required
def add_record(request):
    saved_name = None
    was_updated = False
 
    if request.method == "POST":
        student = get_object_or_404(Student, id=request.POST["student"])
        course = get_object_or_404(Course, id=request.POST["course"])
 
        # المعلم لا يستطيع الحفظ في مقرر ليس له
        if not request.user.is_superuser and course.teacher != request.user:
            raise Http404("المقرر غير متاح")
 
        existing = StudentRecord.objects.filter(student=student, course=course).first()
 
        # اذا في سجل سابق ولم يؤكد المعلم، نعرض صفحة المقارنة بدون حفظ
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
 
    # للتحقق من التكرار بالجافاسكربت قبل الارسال
    existing_pairs = []
    for record in visible_records(request.user):
        existing_pairs.append(str(record.student.id) + "-" + str(record.course.id))
 
    return render(request, "students/add_record.html", {
        "students": Student.objects.all(),
        "courses": visible_courses(request.user),
        "saved_name": saved_name,
        "was_updated": was_updated,
        "existing_pairs": existing_pairs,
    })
 
 
@login_required
def dashboard(request):
    high_risk = 0
    medium_risk = 0
    stable = 0
    absence_alerts = 0
    students_list = []
    courses = {}
    declines = []
 
    for record in visible_records(request.user):
        fail_percent = get_fail_probability(record)
        risk_level, css_class, badge = classify_risk(fail_percent)
 
        if fail_percent >= HIGH_RISK_THRESHOLD:
            high_risk += 1
        elif fail_percent >= MEDIUM_RISK_THRESHOLD:
            medium_risk += 1
        else:
            stable += 1
 
        if is_absence_alert(record):
            absence_alerts += 1
 
        students_list.append({
            "student": record.student.name,
            "course": record.course.title,
            "absences": record.absences,
            "fail_probability": fail_percent,
            "risk_level": risk_level,
            "badge": badge,
        })
 
        # مقارنة المقررات: نجمع ارقام كل مقرر لوحده
        title = record.course.title
        if title not in courses:
            courses[title] = {"course": title, "total": 0, "at_risk": 0, "absence": 0}
        courses[title]["total"] += 1
        if fail_percent >= MEDIUM_RISK_THRESHOLD:
            courses[title]["at_risk"] += 1
        if is_absence_alert(record):
            courses[title]["absence"] += 1
 
        # تراجع تقييم الفترة الثانية عن الاولى بعلامة او اكثر
        drop = record.g1() - record.g2()
        if drop >= DECLINE_LIMIT:
            declines.append({
                "student": record.student.name,
                "course": title,
                "g1": record.g1(),
                "g2": record.g2(),
                "drop": drop,
                "absences": record.absences,
                "risk_level": risk_level,
                "badge": badge,
            })
 
    total = len(students_list)
 
    # نسبة المعرضين للخطر في كل مقرر، والمقرر الاسوأ اولا
    course_stats = list(courses.values())
    for c in course_stats:
        c["percent"] = round(c["at_risk"] / c["total"] * 100)
    course_stats.sort(key=lambda c: c["percent"], reverse=True)
 
    declines.sort(key=lambda item: item["drop"], reverse=True)
 
    # نعرض فقط الطلاب اللي بخطر
    at_risk = []
    for item in students_list:
        if item["fail_probability"] >= MEDIUM_RISK_THRESHOLD:
            at_risk.append(item)
 
    at_risk.sort(key=lambda item: item["fail_probability"], reverse=True)
 
    # الشرط لتجنب القسمة على صفر
    if total > 0:
        high_percent = round(high_risk / total * 100, 1)
        medium_percent = round(medium_risk / total * 100, 1)
        stable_percent = round(stable / total * 100, 1)
    else:
        high_percent = 0
        medium_percent = 0
        stable_percent = 0
 
    # الارقام من نتائج feature_importance.py
    feature_importance = [
        {"name": "تقييم الفترة الثانية", "value": 67.3, "color": "bg-primary"},
        {"name": "تقييم الفترة الأولى", "value": 20.4, "color": "bg-info"},
        {"name": "عدد الغيابات", "value": 7.2, "color": "bg-secondary"},
        {"name": "وقت الدراسة الأسبوعي", "value": 5.1, "color": "bg-secondary"},
    ]
 
    # من نتائج train.py و cross_validation.py
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
        "course_stats": course_stats,
        "show_comparison": len(course_stats) > 1,
        "declines": declines,
    })
 
 
# المدير يبدأ من لوحة الادارة والمعلم من صفحة الادخال
@login_required
def after_login(request):
    if request.user.is_superuser:
        return redirect("admin:index")
    return redirect("add_record")