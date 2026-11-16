from django.contrib import admin
from .models import Student, Subject, Marks

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = (
        "student_id",
        "name",
        "email",
        "department",
    )

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("code", "name")
    
@admin.register(Marks)
class MarksAdmin(admin.ModelAdmin):
    list_display = (
        "student_id_display",
        "student",
        "subject",
        "marks",
    )

    search_fields = ("student__name", "subject__name")
    list_filter = ("subject",)
    ordering = ("marks",)
    list_per_page = 10

    @admin.display(description="Student ID")
    def student_id_display(self, obj):
        return obj.student.student_id