from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.urls import reverse
from .models import Student, Subject, Marks

# ============================================================
# DJANGO ADMIN SITE BRANDING
# ============================================================
admin.site.site_header = "Student Performance & Analytics System"
admin.site.site_title = "Admin Portal | SPAS"
admin.site.index_title = "Institutional Administration & Control Center"


# ============================================================
# INLINE MARKS EDITOR IN STUDENT VIEW
# ============================================================
class MarksInline(admin.TabularInline):
    model = Marks
    extra = 1
    autocomplete_fields = ["subject"]
    fields = ("subject", "marks")
    classes = ("collapse",)


# ============================================================
# STUDENT ADMIN
# ============================================================
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = (
        "student_id_badge",
        "name_display",
        "department_badge",
        "email",
        "date_of_birth",
        "subjects_count",
        "total_marks_display",
        "average_score_display",
        "performance_badge",
        "quick_actions",
    )

    search_fields = (
        "student_id",
        "name",
        "email",
        "department",
    )

    list_filter = ("department",)
    ordering = ("student_id",)
    inlines = [MarksInline]

    fieldsets = (
        ("Personal Identification", {
            "fields": ("student_id", "name", "email", "date_of_birth")
        }),
        ("Academic Enrollment", {
            "fields": ("department",)
        }),
    )

    @admin.display(description="Student ID", ordering="student_id")
    def student_id_badge(self, obj):
        return format_html(
            '<span class="spas-badge spas-badge-slate" style="font-family: ui-monospace, monospace;">{}</span>',
            obj.student_id,
        )

    @admin.display(description="Full Name", ordering="name")
    def name_display(self, obj):
        return format_html("<strong>{}</strong>", obj.name)

    @admin.display(description="Department", ordering="department")
    def department_badge(self, obj):
        return format_html(
            '<span class="spas-badge spas-badge-blue">{}</span>',
            obj.department,
        )

    @admin.display(description="Subjects")
    def subjects_count(self, obj):
        count = obj.marks_set.count()
        return format_html('<span style="font-weight: 600;">{}</span>', count)

    @admin.display(description="Total Marks")
    def total_marks_display(self, obj):
        marks = obj.marks_set.all()
        if not marks:
            return mark_safe('<span style="color: #94a3b8;">—</span>')
        total = sum(m.marks for m in marks)
        return format_html('<span style="font-weight: 700; color: #1e293b;">{}</span>', total)

    @admin.display(description="Average %")
    def average_score_display(self, obj):
        marks = obj.marks_set.all()
        if not marks:
            return mark_safe('<span style="color: #94a3b8;">N/A</span>')
        total = sum(m.marks for m in marks)
        avg = round(float(total) / len(marks), 2)
        color = "#059669" if avg >= 75 else ("#2563eb" if avg >= 50 else ("#d97706" if avg >= 40 else "#dc2626"))
        return format_html('<span style="font-weight: 800; color: {};">{}%</span>', color, avg)

    @admin.display(description="Academic Standing")
    def performance_badge(self, obj):
        marks = obj.marks_set.all()
        if not marks:
            return mark_safe('<span class="spas-badge spas-badge-slate">No Marks</span>')
        total = sum(m.marks for m in marks)
        avg = round(float(total) / len(marks), 2)

        if avg >= 90:
            return mark_safe('<span class="spas-badge spas-badge-gold">🥇 Outstanding</span>')
        elif avg >= 80:
            return mark_safe('<span class="spas-badge spas-badge-green">⭐ Excellent</span>')
        elif avg >= 70:
            return mark_safe('<span class="spas-badge spas-badge-blue">Very Good</span>')
        elif avg >= 60:
            return mark_safe('<span class="spas-badge spas-badge-cyan">Good</span>')
        elif avg >= 50:
            return mark_safe('<span class="spas-badge spas-badge-amber">Average</span>')
        elif avg >= 40:
            return mark_safe('<span class="spas-badge spas-badge-amber">Pass</span>')
        else:
            return mark_safe('<span class="spas-badge spas-badge-red">Needs Attention</span>')

    @admin.display(description="Actions")
    def quick_actions(self, obj):
        detail_url = reverse("student_detail", kwargs={"student_id": obj.student_id})
        pdf_url = reverse("student_pdf_report", kwargs={"student_id": obj.student_id})
        return format_html(
            '<a href="{}" target="_blank" class="spas-action-link" title="Open Student Analytics Profile">📊 Profile</a> '
            '<a href="{}" target="_blank" class="spas-action-link" style="color: #059669 !important;" title="Download Official PDF Report">📄 PDF</a>',
            detail_url,
            pdf_url,
        )


# ============================================================
# SUBJECT ADMIN
# ============================================================
@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = (
        "code_badge",
        "name",
        "enrolled_students_count",
        "average_score_display",
        "pass_rate_display",
    )

    search_fields = ("code", "name")
    ordering = ("code",)

    @admin.display(description="Subject Code", ordering="code")
    def code_badge(self, obj):
        return format_html(
            '<span class="spas-badge spas-badge-blue" style="font-family: ui-monospace, monospace;">{}</span>',
            obj.code,
        )

    @admin.display(description="Students Enrolled")
    def enrolled_students_count(self, obj):
        count = obj.marks_set.count()
        return format_html('<span style="font-weight: 700;">{} students</span>', count)

    @admin.display(description="Subject Average")
    def average_score_display(self, obj):
        marks = obj.marks_set.all()
        if not marks:
            return mark_safe('<span style="color: #94a3b8;">No Records</span>')
        avg = round(sum(m.marks for m in marks) / len(marks), 2)
        return format_html('<span style="font-weight: 700; color: #1e293b;">{} / 100</span>', avg)

    @admin.display(description="Pass Rate")
    def pass_rate_display(self, obj):
        marks = obj.marks_set.all()
        if not marks:
            return mark_safe('<span style="color: #94a3b8;">—</span>')
        passed = sum(1 for m in marks if m.marks >= 40)
        rate = round((passed / len(marks)) * 100, 1)
        badge_cls = "spas-badge-green" if rate >= 75 else ("spas-badge-amber" if rate >= 50 else "spas-badge-red")
        return format_html('<span class="spas-badge {}">{}%</span>', badge_cls, rate)


# ============================================================
# MARKS ADMIN
# ============================================================
@admin.register(Marks)
class MarksAdmin(admin.ModelAdmin):
    list_display = (
        "student_id_display",
        "student_name_display",
        "subject_badge",
        "marks",
        "progress_bar",
        "result_badge",
    )

    list_editable = ("marks",)
    search_fields = (
        "student__student_id",
        "student__name",
        "subject__code",
        "subject__name",
    )
    list_filter = ("subject", "student__department")
    ordering = ("student__student_id", "subject__code")
    list_per_page = 20
    autocomplete_fields = ["student", "subject"]

    @admin.display(description="Student ID", ordering="student__student_id")
    def student_id_display(self, obj):
        return format_html(
            '<span class="spas-badge spas-badge-slate" style="font-family: ui-monospace, monospace;">{}</span>',
            obj.student.student_id,
        )

    @admin.display(description="Student Name", ordering="student__name")
    def student_name_display(self, obj):
        return format_html("<strong>{}</strong>", obj.student.name)

    @admin.display(description="Subject", ordering="subject__code")
    def subject_badge(self, obj):
        return format_html(
            '<span class="spas-badge spas-badge-blue">{}</span> {}',
            obj.subject.code,
            obj.subject.name,
        )

    @admin.display(description="Score Progress")
    def progress_bar(self, obj):
        marks_val = float(obj.marks)
        bar_color = "#10b981" if marks_val >= 75 else ("#3b82f6" if marks_val >= 50 else ("#f59e0b" if marks_val >= 40 else "#ef4444"))
        return format_html(
            '<div style="display: flex; align-items: center; gap: 8px; width: 140px;">'
            '<div style="flex-grow: 1; height: 6px; background: #e2e8f0; border-radius: 9999px; overflow: hidden;">'
            '<div style="width: {}%; height: 100%; background: {}; border-radius: 9999px;"></div>'
            '</div>'
            '<span style="font-size: 11px; font-weight: 700; color: #64748b;">{}%</span>'
            '</div>',
            marks_val,
            bar_color,
            marks_val,
        )

    @admin.display(description="Result", ordering="marks")
    def result_badge(self, obj):
        if obj.marks >= 40:
            return mark_safe('<span class="spas-badge spas-badge-green">✓ PASS</span>')
        return mark_safe('<span class="spas-badge spas-badge-red">✗ FAIL</span>')
