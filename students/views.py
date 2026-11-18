from functools import wraps
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse

from .models import Student, Subject, Marks
from .forms import StudentForm, AdminLoginForm

import hashlib
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.platypus import Table, TableStyle


# ============================================================
# ADMIN AUTHENTICATION DECORATOR
# ============================================================

def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(
                request,
                "Please log in as an administrator to perform this action."
            )
            return redirect(f"{reverse('admin_login')}?next={request.path}")

        if not (request.user.is_staff or request.user.is_superuser):
            messages.error(
                request,
                "Access denied: Administrator privileges required."
            )
            return redirect("home")

        return view_func(request, *args, **kwargs)

    return _wrapped_view



# ============================================================
# STUDENT LIST
# ============================================================

@login_required
def student_list(request):

    search_query = request.GET.get("search", "").strip()

    students = Student.objects.all()

    if search_query:
        students = students.filter(
            Q(student_id__icontains=search_query) |
            Q(name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(department__icontains=search_query)
        )

    total_students = students.count()

    students_with_marks = students.filter(marks__isnull=False).distinct().count()

    students_without_marks = total_students - students_with_marks
    
    marks = Marks.objects.select_related("student", "subject").all()

    # ========================================================
    # OVERALL PERFORMANCE SUMMARY
    # ========================================================

    total_marks = sum(mark.marks for mark in marks)

    average_marks = round(
        total_marks / len(marks), 2
    ) if marks else 0

    percentage = average_marks

    cgpa = round(percentage / 10, 2)

    if average_marks >= 90:
        grade = "O"
        performance_status = "Outstanding"

    elif average_marks >= 80:
        grade = "E"
        performance_status = "Excellent"

    elif average_marks >= 70:
        grade = "A"
        performance_status = "Very Good"

    elif average_marks >= 60:
        grade = "B"
        performance_status = "Good"

    elif average_marks >= 50:
        grade = "C"
        performance_status = "Average"

    elif average_marks >= 40:
        grade = "D"
        performance_status = "Pass"

    else:
        grade = "F"
        performance_status = "Needs Improvement"


    # ========================================================
    # INDIVIDUAL STUDENT PERFORMANCE
    # ========================================================

    student_results = []

    for student in students:

        student_marks = marks.filter(student=student)

        if not student_marks:
            student_result_status = "NO RESULT"

        elif all(mark.marks >= 40 for mark in student_marks):
            student_result_status = "PASS"

        else:
            student_result_status = "FAIL"


        student_total_marks = sum(
            mark.marks for mark in student_marks
        )

        student_average_marks = round(
            student_total_marks / len(student_marks), 2
        ) if student_marks else 0

        student_percentage = student_average_marks

        student_cgpa = round(
            student_percentage / 10, 2
        )


        if student_average_marks >= 90:
            student_grade = "O"
            student_performance = "Outstanding"

        elif student_average_marks >= 80:
            student_grade = "E"
            student_performance = "Excellent"

        elif student_average_marks >= 70:
            student_grade = "A"
            student_performance = "Very Good"

        elif student_average_marks >= 60:
            student_grade = "B"
            student_performance = "Good"

        elif student_average_marks >= 50:
            student_grade = "C"
            student_performance = "Average"

        elif student_average_marks >= 40:
            student_grade = "D"
            student_performance = "Pass"

        else:
            student_grade = "F"
            student_performance = "Needs Improvement"


        student_results.append({
            "student": student,
            "total_marks": student_total_marks,
            "average_marks": student_average_marks,
            "percentage": student_percentage,
            "cgpa": student_cgpa,
            "grade": student_grade,
            "performance_status": student_performance,
            "result_status": student_result_status,
        })

        
        



        
    # ========================================================
    # PAGINATION
    # ========================================================

    paginator = Paginator(student_results, 10)

    page_number = request.GET.get("page")

    page_obj = paginator.get_page(page_number)
    # ========================================================
    # SEND DATA TO TEMPLATE
    # ========================================================

    return render(
        request,
        "students/student_list.html",
        {
            "students": students,
            "total_students": total_students,
            "students_with_marks": students_with_marks,
            "students_without_marks": students_without_marks,
            "marks": marks,

            "average_marks": average_marks,
            "percentage": percentage,
            "cgpa": cgpa,
            "grade": grade,
            "performance_status": performance_status,

            
            "page_obj": page_obj,
            "student_results": page_obj,
            "search_query": search_query,


        }
    )


# ============================================================
# STUDENT DETAIL
# ============================================================

@login_required
def student_detail(request, student_id):

    student = get_object_or_404(
        Student,
        student_id=student_id
    )

    marks = Marks.objects.filter(
        student=student
    ).select_related("subject")


    if not marks:
        result_status = "NO RESULT"

    elif all(mark.marks >= 40 for mark in marks):
        result_status = "PASS"

    else:
        result_status = "FAIL"


    total_marks = sum(
        mark.marks for mark in marks
    )

    average_marks = round(
        total_marks / len(marks), 2
    ) if marks else 0

    percentage = average_marks

    cgpa = round(
        percentage / 10, 2
    )


    if average_marks >= 90:
        grade = "O"
        performance_status = "Outstanding"

    elif average_marks >= 80:
        grade = "E"
        performance_status = "Excellent"

    elif average_marks >= 70:
        grade = "A"
        performance_status = "Very Good"

    elif average_marks >= 60:
        grade = "B"
        performance_status = "Good"

    elif average_marks >= 50:
        grade = "C"
        performance_status = "Average"

    elif average_marks >= 40:
        grade = "D"
        performance_status = "Pass"

    else:
        grade = "F"
        performance_status = "Needs Improvement"


    return render(
        request,
        "students/student_detail.html",
        {
            "student": student,
            "marks": marks,
            "total_marks": total_marks,
            "average_marks": average_marks,
            "percentage": percentage,
            "cgpa": cgpa,
            "grade": grade,
            "performance_status": performance_status,
            "result_status": result_status,
        }
    )

# ============================================================
# INDIVIDUAL STUDENT PDF REPORT (OFFICIAL ACADEMIC TRANSCRIPT)
# ============================================================

@login_required
def student_pdf_report(request, student_id):
    student = get_object_or_404(Student, student_id=student_id)
    marks = Marks.objects.filter(student=student).select_related("subject").order_by("subject__code")

    # Aggregate performance calculations
    total_marks = sum(float(mark.marks) for mark in marks)
    count = len(marks)
    average_marks = round(total_marks / count, 2) if count else 0
    percentage = average_marks
    cgpa = round(percentage / 10.0, 2)
    max_total = count * 100

    if not marks:
        result_status = "NO RESULT"
    elif all(float(mark.marks) >= 40 for mark in marks):
        result_status = "PASS"
    else:
        result_status = "FAIL"

    if average_marks >= 90:
        grade = "O"
        performance_status = "Outstanding"
    elif average_marks >= 80:
        grade = "E"
        performance_status = "Excellent"
    elif average_marks >= 70:
        grade = "A"
        performance_status = "Very Good"
    elif average_marks >= 60:
        grade = "B"
        performance_status = "Good"
    elif average_marks >= 50:
        grade = "C"
        performance_status = "Average"
    elif average_marks >= 40:
        grade = "D"
        performance_status = "Pass"
    else:
        grade = "F"
        performance_status = "Needs Improvement"

    # Setup PDF response
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{student.student_id}_Academic_Transcript.pdf"'

    pdf = canvas.Canvas(response, pagesize=A4)
    width, height = A4
    margin_x = 36
    content_w = width - (2 * margin_x)

    def draw_decorations(page_num, total_pages=1):
        # Outer double border
        pdf.setStrokeColor(HexColor('#0f172a'))
        pdf.setLineWidth(1.5)
        pdf.rect(20, 20, width - 40, height - 40)

        pdf.setStrokeColor(HexColor('#94a3b8'))
        pdf.setLineWidth(0.6)
        pdf.rect(24, 24, width - 48, height - 48)

        # Footer
        pdf.setFont("Helvetica", 7.5)
        pdf.setFillColor(HexColor('#64748b'))
        pdf.drawString(margin_x, 32, "Student Performance & Analytics System  •  Official Institutional Academic Transcript")
        pdf.drawRightString(width - margin_x, 32, f"Page {page_num} of {total_pages}")

    # DRAW PAGE 1 DECORATIONS
    draw_decorations(1, 1)

    # 1. TOP HEADER BANNER
    banner_y = height - 122
    banner_h = 86
    pdf.setFillColor(HexColor('#0f172a'))
    pdf.rect(margin_x, banner_y, content_w, banner_h, fill=1, stroke=0)

    # Accent lines
    pdf.setFillColor(HexColor('#2563eb'))
    pdf.rect(margin_x, banner_y - 3, content_w, 3, fill=1, stroke=0)
    pdf.setFillColor(HexColor('#f59e0b'))
    pdf.rect(margin_x, banner_y - 5, content_w, 2, fill=1, stroke=0)

    # Masthead text
    pdf.setFillColor(colors.white)
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawCentredString(width / 2, banner_y + 60, "STUDENT PERFORMANCE & ANALYTICS SYSTEM")

    pdf.setFillColor(HexColor('#93c5fd'))
    pdf.setFont("Helvetica-Bold", 8.5)
    pdf.drawCentredString(width / 2, banner_y + 44, "OFFICE OF ACADEMIC EVALUATION & CONTROLLER OF EXAMINATIONS")

    pdf.setFillColor(HexColor('#fde047'))
    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawCentredString(width / 2, banner_y + 24, "OFFICIAL ACADEMIC TRANSCRIPT & PERFORMANCE REPORT")

    pdf.setFillColor(HexColor('#cbd5e1'))
    pdf.setFont("Helvetica", 7.5)
    pdf.drawCentredString(width / 2, banner_y + 9, f"Academic Session: 2025–2026   |   Issued Under Institutional Authority   |   Document ID: SPAS/TR/{student.student_id}")

    # 2. STUDENT PROFILE CARD
    card_y = banner_y - 94
    card_h = 76
    pdf.setFillColor(HexColor('#f8fafc'))
    pdf.setStrokeColor(HexColor('#cbd5e1'))
    pdf.setLineWidth(0.8)
    pdf.roundRect(margin_x, card_y, content_w, card_h, 6, fill=1, stroke=1)

    # Card Title
    pdf.setFillColor(HexColor('#1e293b'))
    pdf.setFont("Helvetica-Bold", 9)
    pdf.drawString(margin_x + 14, card_y + card_h - 17, "STUDENT PROFILE & ENROLLMENT PARTICULARS")

    pdf.setStrokeColor(HexColor('#e2e8f0'))
    pdf.setLineWidth(0.5)
    pdf.line(margin_x + 14, card_y + card_h - 22, margin_x + content_w - 14, card_y + card_h - 22)

    # Row coordinates
    col1_x = margin_x + 14
    r1_y = card_y + card_h - 37
    r2_y = card_y + card_h - 51
    r3_y = card_y + card_h - 65

    pdf.setFont("Helvetica-Bold", 8.5)
    pdf.setFillColor(HexColor('#475569'))
    pdf.drawString(col1_x, r1_y, "Student ID:")
    pdf.drawString(col1_x, r2_y, "Student Name:")
    pdf.drawString(col1_x, r3_y, "Email Address:")

    pdf.setFont("Helvetica-Bold", 8.5)
    pdf.setFillColor(HexColor('#0f172a'))
    pdf.drawString(col1_x + 80, r1_y, str(student.student_id))
    pdf.drawString(col1_x + 80, r2_y, str(student.name).upper())
    pdf.setFont("Helvetica", 8.5)
    pdf.setFillColor(HexColor('#334155'))
    pdf.drawString(col1_x + 80, r3_y, str(student.email))

    col2_x = margin_x + 280
    pdf.setFont("Helvetica-Bold", 8.5)
    pdf.setFillColor(HexColor('#475569'))
    pdf.drawString(col2_x, r1_y, "Department:")
    pdf.drawString(col2_x, r2_y, "Date of Birth:")
    pdf.drawString(col2_x, r3_y, "Issue Date:")

    pdf.setFont("Helvetica-Bold", 8.5)
    pdf.setFillColor(HexColor('#1d4ed8'))
    pdf.drawString(col2_x + 75, r1_y, str(student.department))
    pdf.setFont("Helvetica", 8.5)
    pdf.setFillColor(HexColor('#334155'))
    pdf.drawString(col2_x + 75, r2_y, str(student.date_of_birth))
    pdf.drawString(col2_x + 75, r3_y, datetime.now().strftime("%d-%b-%Y %I:%M %p"))

    # 3. SECTION HEADER: COURSE EVALUATION
    sect_y = card_y - 24
    pdf.setFont("Helvetica-Bold", 10.5)
    pdf.setFillColor(HexColor('#0f172a'))
    pdf.drawString(margin_x, sect_y, "COURSE EVALUATION & SUBJECT-WISE PERFORMANCE")

    pdf.setFont("Helvetica", 8)
    pdf.setFillColor(HexColor('#64748b'))
    pdf.drawRightString(margin_x + content_w, sect_y, "Evaluation Standard: Maximum 100 Marks / Subject")

    # 4. SUBJECT-WISE TABLE
    table_data = [
        ["Sl.", "Course Code", "Subject Course Title", "Max Marks", "Marks Scored", "Grade", "Status"]
    ]

    for idx, m in enumerate(marks, start=1):
        val = float(m.marks)
        if val >= 90:
            s_grade = "O"
        elif val >= 80:
            s_grade = "E"
        elif val >= 70:
            s_grade = "A"
        elif val >= 60:
            s_grade = "B"
        elif val >= 50:
            s_grade = "C"
        elif val >= 40:
            s_grade = "D"
        else:
            s_grade = "F"

        status_text = "PASS" if val >= 40 else "FAIL"

        table_data.append([
            str(idx),
            str(m.subject.code),
            str(m.subject.name),
            "100",
            f"{val:.2f}",
            s_grade,
            status_text,
        ])

    table_data.append([
        "TOTAL",
        "",
        f"Cumulative Aggregate ({len(marks)} Course{'s' if len(marks)>1 else ''})",
        str(max_total),
        f"{total_marks:.2f}",
        grade,
        result_status,
    ])

    col_widths = [26, 68, 205, 56, 64, 46, 58]

    t = Table(table_data, colWidths=col_widths)
    t_style = [
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1e3a8a')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8.5),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('TOPPADDING', (0, 0), (-1, 0), 6),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (2, 0), (2, -1), 'LEFT'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8.5),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 4.5),
        ('TOPPADDING', (0, 1), (-1, -1), 4.5),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#cbd5e1')),
    ]

    for r in range(1, len(table_data) - 1):
        bg = HexColor('#ffffff') if r % 2 == 1 else HexColor('#f8fafc')
        t_style.append(('BACKGROUND', (0, r), (-1, r), bg))

    last_row_idx = len(table_data) - 1
    t_style.extend([
        ('BACKGROUND', (0, last_row_idx), (-1, last_row_idx), HexColor('#eff6ff')),
        ('FONTNAME', (0, last_row_idx), (-1, last_row_idx), 'Helvetica-Bold'),
        ('TEXTCOLOR', (0, last_row_idx), (-1, last_row_idx), HexColor('#0f172a')),
        ('TOPPADDING', (0, last_row_idx), (-1, last_row_idx), 6),
        ('BOTTOMPADDING', (0, last_row_idx), (-1, last_row_idx), 6),
    ])

    t.setStyle(TableStyle(t_style))
    tw, th = t.wrapOn(pdf, content_w, height)
    table_y = sect_y - 12 - th
    t.drawOn(pdf, margin_x, table_y)

    # 5. PERFORMANCE SUMMARY & SCALE SECTION (2 COLUMNS)
    summary_sect_y = table_y - 18
    box_h = 104
    box_w1 = 265
    box_w2 = content_w - box_w1 - 14
    box1_x = margin_x
    box2_x = margin_x + box_w1 + 14
    box_y = summary_sect_y - box_h

    # BOX 1: SUMMARY METRICS & RESULT STAMP
    pdf.setFillColor(HexColor('#ffffff'))
    pdf.setStrokeColor(HexColor('#cbd5e1'))
    pdf.setLineWidth(0.8)
    pdf.roundRect(box1_x, box_y, box_w1, box_h, 6, fill=1, stroke=1)

    # Header Strip
    pdf.setFillColor(HexColor('#f1f5f9'))
    pdf.roundRect(box1_x, box_y + box_h - 22, box_w1, 22, 6, fill=1, stroke=0)
    pdf.rect(box1_x, box_y + box_h - 22, box_w1, 10, fill=1, stroke=0)
    pdf.setFillColor(HexColor('#0f172a'))
    pdf.setFont("Helvetica-Bold", 8.5)
    pdf.drawString(box1_x + 12, box_y + box_h - 15, "ACADEMIC PERFORMANCE SUMMARY")

    # Metrics
    b1_y1 = box_y + box_h - 36
    b1_y2 = box_y + box_h - 50
    b1_y3 = box_y + box_h - 64
    b1_y4 = box_y + box_h - 78
    b1_y5 = box_y + box_h - 92

    pdf.setFont("Helvetica", 8)
    pdf.setFillColor(HexColor('#475569'))
    pdf.drawString(box1_x + 12, b1_y1, "Total Marks Secured:")
    pdf.drawString(box1_x + 12, b1_y2, "Percentage Aggregate:")
    pdf.drawString(box1_x + 12, b1_y3, "Cumulative GPA (CGPA):")
    pdf.drawString(box1_x + 12, b1_y4, "Overall Letter Grade:")
    pdf.drawString(box1_x + 12, b1_y5, "Final Result Status:")

    pdf.setFont("Helvetica-Bold", 8.5)
    pdf.setFillColor(HexColor('#0f172a'))
    pdf.drawString(box1_x + 135, b1_y1, f"{total_marks:.2f} / {max_total}")
    pdf.drawString(box1_x + 135, b1_y2, f"{percentage:.2f}%")
    pdf.drawString(box1_x + 135, b1_y3, f"{cgpa:.2f} / 10.0")
    pdf.drawString(box1_x + 135, b1_y4, f"Grade {grade} ({performance_status})")

    res_color = '#059669' if result_status == 'PASS' else '#dc2626'
    pdf.setFillColor(HexColor(res_color))
    pdf.drawString(box1_x + 135, b1_y5, str(result_status))

    # BOX 2: GRADING SCALE KEY
    pdf.setFillColor(HexColor('#ffffff'))
    pdf.setStrokeColor(HexColor('#cbd5e1'))
    pdf.setLineWidth(0.8)
    pdf.roundRect(box2_x, box_y, box_w2, box_h, 6, fill=1, stroke=1)

    pdf.setFillColor(HexColor('#f1f5f9'))
    pdf.roundRect(box2_x, box_y + box_h - 22, box_w2, 22, 6, fill=1, stroke=0)
    pdf.rect(box2_x, box_y + box_h - 22, box_w2, 10, fill=1, stroke=0)
    pdf.setFillColor(HexColor('#0f172a'))
    pdf.setFont("Helvetica-Bold", 8.5)
    pdf.drawString(box2_x + 12, box_y + box_h - 15, "INSTITUTIONAL GRADING SCALE")

    scales = [
        ("90% - 100%", "Grade O (Outstanding)", "#15803d"),
        ("80% - 89%", "Grade E (Excellent)", "#059669"),
        ("70% - 79%", "Grade A (Very Good)", "#2563eb"),
        ("60% - 69%", "Grade B (Good)", "#0284c7"),
        ("50% - 59%", "Grade C (Average)", "#d97706"),
        ("40% - 49%", "Grade D (Pass)", "#ea580c"),
        ("Below 40%", "Grade F (Fail)", "#dc2626"),
    ]

    scale_y = box_y + box_h - 33
    pdf.setFont("Helvetica", 7.2)
    for rng, desc, col in scales:
        pdf.setFillColor(HexColor('#475569'))
        pdf.drawString(box2_x + 12, scale_y, rng)
        pdf.setFillColor(HexColor(col))
        pdf.drawString(box2_x + 75, scale_y, f"• {desc}")
        scale_y -= 9.5

    # 6. DIGITAL SEAL & SIGNATURE BLOCK
    sign_y = box_y - 18
    sign_box_h = 58
    sign_top = sign_y - sign_box_h

    # Seal Box on Left
    seal_w = 265
    pdf.setFillColor(HexColor('#f8fafc'))
    pdf.setStrokeColor(HexColor('#e2e8f0'))
    pdf.setLineWidth(0.8)
    pdf.roundRect(margin_x, sign_top, seal_w, sign_box_h, 5, fill=1, stroke=1)

    verif_hash = hashlib.sha256(f"{student.student_id}:{total_marks}:{student.date_of_birth}".encode()).hexdigest()[:16].upper()

    pdf.setFillColor(HexColor('#0f172a'))
    pdf.setFont("Helvetica-Bold", 8)
    pdf.drawString(margin_x + 10, sign_top + sign_box_h - 13, "DIGITAL VERIFICATION & AUTHENTICITY")
    pdf.setFont("Helvetica", 7)
    pdf.setFillColor(HexColor('#64748b'))
    pdf.drawString(margin_x + 10, sign_top + sign_box_h - 25, "This transcript is digitally generated from certified examination database records.")
    pdf.drawString(margin_x + 10, sign_top + sign_box_h - 36, f"Document Security Hash: SPAS-{verif_hash}")
    pdf.setFont("Helvetica-Bold", 7)
    pdf.setFillColor(HexColor('#059669'))
    pdf.drawString(margin_x + 10, sign_top + sign_box_h - 48, "✓ Authenticated by Controller of Examinations")

    # Formal Signature line on Right
    sig_w = 200
    sig_x = width - margin_x - sig_w
    pdf.setStrokeColor(HexColor('#475569'))
    pdf.setLineWidth(0.8)
    pdf.line(sig_x, sign_top + 18, sig_x + sig_w, sign_top + 18)

    pdf.setFont("Helvetica-Bold", 8.5)
    pdf.setFillColor(HexColor('#0f172a'))
    pdf.drawCentredString(sig_x + (sig_w / 2), sign_top + 7, "Controller of Examinations")

    pdf.setFont("Helvetica", 7.5)
    pdf.setFillColor(HexColor('#64748b'))
    pdf.drawCentredString(sig_x + (sig_w / 2), sign_top - 3, "Board of Academic Evaluation & Records")

    # Save and return
    pdf.save()
    return response

# ============================================================
# DASHBOARD
# ============================================================

@login_required
def dashboard(request):

    # ========================================================
    # SEARCH
    # ========================================================

    search_query = request.GET.get(
        "search",
        ""
    ).strip()


    # ========================================================
    # SYSTEM STATISTICS
    # ========================================================

    total_students = Student.objects.count()

    total_subjects = Subject.objects.count()

    total_marks_records = Marks.objects.count()


    # ========================================================
    # ALL MARKS
    # ========================================================

    marks = Marks.objects.all()


    # ========================================================
    # OVERALL PERFORMANCE
    # ========================================================

    total_marks = sum(
        mark.marks for mark in marks
    )

    average_marks = round(
        total_marks / len(marks), 2
    ) if marks else 0

    percentage = average_marks

    cgpa = round(
        percentage / 10,
        2
    )


    if average_marks >= 90:
        grade = "O"
        performance_status = "Outstanding"

    elif average_marks >= 80:
        grade = "E"
        performance_status = "Excellent"

    elif average_marks >= 70:
        grade = "A"
        performance_status = "Very Good"

    elif average_marks >= 60:
        grade = "B"
        performance_status = "Good"

    elif average_marks >= 50:
        grade = "C"
        performance_status = "Average"

    elif average_marks >= 40:
        grade = "D"
        performance_status = "Pass"

    else:
        grade = "F"
        performance_status = "Needs Improvement"


    # ========================================================
    # STUDENT-WISE PERFORMANCE & RANKING SYSTEM
    # ========================================================

    all_students = Student.objects.all()
    all_student_results = []

    # ========================================================
    # PASS / FAIL STATISTICS
    # ========================================================

    passed_students = 0
    failed_students = 0
    no_result_students = 0

    # ========================================================
    # PERFORMANCE DISTRIBUTION
    # ========================================================

    performance_distribution = {
        "outstanding": 0,
        "excellent": 0,
        "very_good": 0,
        "good": 0,
        "average": 0,
        "pass": 0,
        "needs_improvement": 0,
    }

    # ========================================================
    # BUILD ALL STUDENT PERFORMANCE METRICS
    # ========================================================

    for student in all_students:

        student_marks = marks.filter(
            student=student
        )

        # PASS / FAIL / NO RESULT STATUS
        if not student_marks:
            student_result_status = "NO RESULT"
            no_result_students += 1

        elif all(mark.marks >= 40 for mark in student_marks):
            student_result_status = "PASS"
            passed_students += 1

        else:
            student_result_status = "FAIL"
            failed_students += 1

        student_total_marks = sum(
            mark.marks for mark in student_marks
        )

        student_average_marks = round(
            student_total_marks / len(student_marks),
            2
        ) if student_marks else 0

        student_percentage = student_average_marks

        student_cgpa = round(
            student_percentage / 10,
            2
        )

        # ====================================================
        # GRADE + PERFORMANCE
        # ====================================================

        if student_average_marks >= 90:
            student_grade = "O"
            student_performance = "Outstanding"

        elif student_average_marks >= 80:
            student_grade = "E"
            student_performance = "Excellent"

        elif student_average_marks >= 70:
            student_grade = "A"
            student_performance = "Very Good"

        elif student_average_marks >= 60:
            student_grade = "B"
            student_performance = "Good"

        elif student_average_marks >= 50:
            student_grade = "C"
            student_performance = "Average"

        elif student_average_marks >= 40:
            student_grade = "D"
            student_performance = "Pass"

        else:
            student_grade = "F"
            student_performance = "Needs Improvement"

        all_student_results.append({
            "student": student,
            "has_marks": bool(student_marks),
            "total_marks": student_total_marks,
            "average_marks": student_average_marks,
            "percentage": student_percentage,
            "cgpa": student_cgpa,
            "grade": student_grade,
            "performance_status": student_performance,
            "result_status": student_result_status,
        })

        # ====================================================
        # UPDATE PERFORMANCE DISTRIBUTION
        # ====================================================

        if student_performance == "Outstanding":
            performance_distribution["outstanding"] += 1

        elif student_performance == "Excellent":
            performance_distribution["excellent"] += 1

        elif student_performance == "Very Good":
            performance_distribution["very_good"] += 1

        elif student_performance == "Good":
            performance_distribution["good"] += 1

        elif student_performance == "Average":
            performance_distribution["average"] += 1

        elif student_performance == "Pass":
            performance_distribution["pass"] += 1

        elif student_performance == "Needs Improvement":
            performance_distribution["needs_improvement"] += 1

    # ========================================================
    # SORT AND ASSIGN ACADEMIC RANKS
    # Ranked by percentage desc, then total marks desc
    # Students with no marks appear at the bottom as unranked
    # ========================================================

    all_student_results.sort(
        key=lambda x: (
            1 if x["has_marks"] else 0,
            x["percentage"],
            x["total_marks"]
        ),
        reverse=True
    )

    current_rank = 0
    top_rankers = []

    for res in all_student_results:
        if res["has_marks"]:
            current_rank += 1
            res["rank"] = current_rank
            res["rank_display"] = f"#{current_rank}"

            if current_rank == 1:
                res["medal"] = "🥇"
                res["rank_label"] = "1st Place (Gold)"
                res["rank_class"] = "rank-gold"
            elif current_rank == 2:
                res["medal"] = "🥈"
                res["rank_label"] = "2nd Place (Silver)"
                res["rank_class"] = "rank-silver"
            elif current_rank == 3:
                res["medal"] = "🥉"
                res["rank_label"] = "3rd Place (Bronze)"
                res["rank_class"] = "rank-bronze"
            else:
                res["medal"] = ""
                res["rank_label"] = f"Rank #{current_rank}"
                res["rank_class"] = "rank-standard"

            if len(top_rankers) < 3:
                top_rankers.append(res)
        else:
            res["rank"] = None
            res["rank_display"] = "-"
            res["medal"] = ""
            res["rank_label"] = "Unranked"
            res["rank_class"] = "rank-none"

    # ========================================================
    # FILTER BY SEARCH QUERY (IF PROVIDED)
    # Global academic ranks are preserved!
    # ========================================================

    filtered_student_results = all_student_results
    if search_query:
        query = search_query.lower()
        filtered_student_results = [
            r for r in all_student_results
            if query in r["student"].name.lower()
            or query in r["student"].student_id.lower()
            or query in r["student"].department.lower()
        ]

    # ========================================================
    # PAGINATION FOR RANKING TABLE
    # ========================================================

    paginator = Paginator(
        filtered_student_results,
        5
    )

    page_number = request.GET.get(
        "page"
    )

    student_results = paginator.get_page(
        page_number
    )

    # Top ranked students for leaderboard chart
    chart_students = [r for r in all_student_results if r["has_marks"]][:10]

        # ========================================================
    # SUBJECT-WISE PERFORMANCE
    # ========================================================

    subject_results = []

    subjects = Subject.objects.all()

    for subject in subjects:

        subject_marks = marks.filter(
            subject=subject
        )

        subject_total_marks = sum(
            mark.marks for mark in subject_marks
        )

        subject_average_marks = round(
            subject_total_marks / len(subject_marks),
            2
        ) if subject_marks else 0

        subject_percentage = subject_average_marks

        highest_marks = max(
            (mark.marks for mark in subject_marks),
            default=0
        )

        lowest_marks = min(
            (mark.marks for mark in subject_marks),
            default=0
        )

        subject_passed = sum(
            1 for mark in subject_marks
            if mark.marks >= 40
        )

        subject_failed = sum(
            1 for mark in subject_marks
            if mark.marks < 40
        )

        subject_results.append({

            "subject": subject,

            "total_marks": subject_total_marks,

            "records": len(subject_marks),

            "average_marks": subject_average_marks,

            "percentage": subject_percentage,

            "highest_marks": highest_marks,

            "lowest_marks": lowest_marks,

            "passed": subject_passed,

            "failed": subject_failed,

        })


    # ========================================================
    # SEND DATA TO DASHBOARD
    # ========================================================

    return render(
        request,
        "students/dashboard.html",
        {
            "total_students": total_students,

            

            "total_subjects": total_subjects,

            "total_marks_records": total_marks_records,

            "total_marks": total_marks,

            "average_marks": average_marks,
            "passed_students": passed_students,
            
             "no_result_students": no_result_students,
                        
            "failed_students": failed_students,

            "percentage": percentage,

            "cgpa": cgpa,

            "grade": grade,

            "performance_status": performance_status,

            "student_results": student_results,

            "top_rankers": top_rankers,

            "top_ranker": top_rankers[0] if top_rankers else None,

            "chart_students": chart_students,

            "performance_distribution":
                performance_distribution,

            "subject_results": subject_results,

            "search_query": search_query,
            
        }
    )


# ==========================================
# ADD STUDENT
# ==========================================

@admin_required
def student_add(request):

    if request.method == "POST":
        form = StudentForm(request.POST)

        if form.is_valid():
            student = form.save()
            messages.success(request, f"Student '{student.name}' added successfully.")
            return redirect("student_list")

    else:
        form = StudentForm()

    return render(
        request,
        "students/student_form.html",
        {
            "form": form,
            "title": "Add Student",
        },
    )


# ==========================================
# EDIT STUDENT
# ==========================================

@admin_required
def student_edit(request, student_id):

    student = get_object_or_404(
        Student,
        student_id=student_id
    )

    if request.method == "POST":
        form = StudentForm(
            request.POST,
            instance=student
        )

        if form.is_valid():
            form.save()
            messages.success(request, f"Student '{student.name}' updated successfully.")
            return redirect(
                "student_detail",
                student_id=student.student_id
            )

    else:
        form = StudentForm(instance=student)

    return render(
        request,
        "students/student_form.html",
        {
            "form": form,
            "title": "Edit Student",
        },
    )

# ==========================================
# DELETE STUDENT
# ==========================================

@admin_required
def student_delete(request, student_id):

    student = get_object_or_404(
        Student,
        student_id=student_id
    )

    if request.method == "POST":
        student_name = student.name
        student.delete()
        messages.success(request, f"Student '{student_name}' deleted successfully.")
        return redirect("student_list")

    return render(
        request,
        "students/student_confirm_delete.html",
        {
            "student": student,
        },
    )


# ==========================================
# ADMIN AUTHENTICATION
# ==========================================

def admin_login(request):
    if request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser):
        return redirect("dashboard")

    next_url = request.GET.get("next") or request.POST.get("next") or "dashboard"
    if next_url in [reverse("admin_login"), reverse("admin_logout")]:
        next_url = "dashboard"

    if request.method == "POST":
        form = AdminLoginForm(request, data=request.POST)

        if form.is_valid():
            user = form.get_user()
            if user.is_staff or user.is_superuser:
                login(request, user)
                messages.success(request, f"Welcome back, {user.username}! Admin access granted.")
                return redirect(next_url)
            else:
                messages.error(
                    request,
                    "Access restricted: Only staff and administrators may log in."
                )
        else:
            messages.error(request, "Invalid username or password. Please try again.")

    else:
        form = AdminLoginForm(request)

    return render(
        request,
        "students/admin_login.html",
        {
            "form": form,
            "next": next_url,
        },
    )


def admin_logout(request):
    if request.user.is_authenticated:
        logout(request)
        messages.info(request, "You have been logged out successfully.")
    return redirect("home")


# ==========================================
# HOME PAGE
# ==========================================

def home(request):
    return render(request, "students/home.html")