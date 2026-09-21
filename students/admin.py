from django.contrib import admin
from .models import Student, Course, StudentRecord


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("student_id", "name")
    search_fields = ("name", "student_id")


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("code", "title", "teacher")


@admin.register(StudentRecord)
class StudentRecordAdmin(admin.ModelAdmin):
    list_display = ("student", "course", "absences", "studytime",
                    "assignment1", "quiz1", "assignment2", "quiz2")