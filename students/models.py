from django.db import models
from django.contrib.auth.models import User


class Student(models.Model):
    """جدول الطلاب"""
    name = models.CharField("اسم الطالب", max_length=200)
    student_id = models.CharField("الرقم التعريفي", max_length=50, unique=True)

    class Meta:
        verbose_name = "طالب"
        verbose_name_plural = "الطلاب"

    def __str__(self):
        return self.name


class Course(models.Model):
    """جدول المقررات"""
    title = models.CharField("اسم المقرر", max_length=200)
    code = models.CharField("رمز المقرر", max_length=50, unique=True)
    
    # المعلم المسؤول عن المقرر.. و صلاحية الوصول الى سجلاته
    teacher = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name="المعلم المسؤول",
    )

    class Meta:
        verbose_name = "مقرر"
        verbose_name_plural = "المقررات"

    def __str__(self):
        return self.title


class StudentRecord(models.Model):
    """سجل الطالب: درجات التقييم المستمر والحضور"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name="الطالب")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name="المقرر")

    absences = models.IntegerField("عدد الغيابات")
    studytime = models.IntegerField("وقت الدراسة الأسبوعي (1-4)")

    # الفترة الأولى
    assignment1 = models.FloatField("درجة الوظيفة الأولى (0-20)")
    quiz1 = models.FloatField("درجة الاختبار الأول (0-20)")

    # الفترة الثانية
    assignment2 = models.FloatField("درجة الوظيفة الثانية (0-20)")
    quiz2 = models.FloatField("درجة الاختبار الثاني (0-20)")

    class Meta:
        # لا يجوز وجود أكثر من سجل واحد لنفس الطالب في نفس المقرر
        unique_together = ("student", "course")
        verbose_name = "سجل أداء"
        verbose_name_plural = "سجلات الأداء"

    def g1(self):
        """متوسط الفترة الأولى"""
        return (self.assignment1 + self.quiz1) / 2

    def g2(self):
        """متوسط الفترة الثانية"""
        return (self.assignment2 + self.quiz2) / 2

    def __str__(self):
        return f"{self.student.name} - {self.course.title}"