from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
# Create your models here.


class Student(models.Model):
    student_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    date_of_birth = models.DateField()
    department = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Subject(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.code} - {self.name}"


class Marks(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    marks = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[
           MinValueValidator(0),
           MaxValueValidator(100),
],
    )

    class Meta:
        verbose_name_plural = "Marks"


        constraints = [
            models.UniqueConstraint(
                fields=["student", "subject"],
                name="unique_student_subject_marks",
            )
        ]

    def __str__(self):
        return f"{self.student} - {self.subject} - {self.marks}"