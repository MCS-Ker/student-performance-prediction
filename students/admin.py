from django.contrib import admin
from .models import Student, Course, StudentRecord, Prediction


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("student_id", "name")
    search_fields = ("name", "student_id")


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("code", "title")


@admin.register(StudentRecord)
class StudentRecordAdmin(admin.ModelAdmin):
    list_display = ("student", "course", "absences", "studytime",
                    "assignment1", "quiz1", "assignment2", "quiz2")


@admin.register(Prediction)
class PredictionAdmin(admin.ModelAdmin):
    list_display = ("student", "course", "fail_probability",
                    "predicted_result", "created_at")