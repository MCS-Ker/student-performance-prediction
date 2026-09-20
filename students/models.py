from django.db import models


class Student(models.Model):
    """جدول الطلاب"""
    name = models.CharField(max_length=200)
    student_id = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Course(models.Model):
    """جدول المقررات"""
    title = models.CharField(max_length=200)
    code = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.title


class StudentRecord(models.Model):
    """سجل الطالب: درجات التقييم المستمر والحضور"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

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


class Prediction(models.Model):
    """جدول التنبؤات"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    fail_probability = models.FloatField("احتمال الرسوب")
    predicted_result = models.CharField(max_length=20)
    actual_result = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.name} - {self.predicted_result}"