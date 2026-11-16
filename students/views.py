from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.core.paginator import Paginator

from .models import Student, Subject, Marks
from django.shortcuts import redirect
from .forms import StudentForm
from django.http import HttpResponse

from reportlab.pdfgen import canvas

from reportlab.lib.pagesizes import A4

from reportlab.lib import colors


# ============================================================
# STUDENT LIST
# ============================================================

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
# INDIVIDUAL STUDENT PDF REPORT
# ============================================================

# ============================================================
# INDIVIDUAL STUDENT PDF REPORT
# ============================================================

def student_pdf_report(request, student_id):

    # GET STUDENT
    student = get_object_or_404(
        Student,
        student_id=student_id
    )

    # GET STUDENT MARKS
    marks = Marks.objects.filter(
        student=student
    ).select_related("subject")

    # CALCULATE TOTAL MARKS
    total_marks = sum(mark.marks for mark in marks)

    # CALCULATE AVERAGE
    average_marks = round(
        total_marks / len(marks), 2
    ) if marks else 0

    percentage = average_marks

    # CALCULATE CGPA
    cgpa = round(percentage / 10, 2)

    # RESULT STATUS
    if not marks:
        result_status = "NO RESULT"

    elif all(mark.marks >= 40 for mark in marks):
        result_status = "PASS"

    else:
        result_status = "FAIL"

    # GRADE AND PERFORMANCE
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

    # CREATE PDF RESPONSE
    response = HttpResponse(
        content_type="application/pdf"
    )

    response["Content-Disposition"] = (
        f'attachment; filename="{student.student_id}_Report.pdf"'
    )

    # CREATE PDF CANVAS
    pdf = canvas.Canvas(response, pagesize=A4)

    width, height = A4

    # ========================================================
    # HELPER FUNCTION: WRAP LONG SUBJECT NAMES
    # ========================================================

    def wrap_text(text, max_width, font_name, font_size):

        words = str(text).split()

        lines = []
        current_line = ""

        for word in words:

            test_line = (
                current_line + " " + word
            ).strip()

            if pdf.stringWidth(
                test_line,
                font_name,
                font_size
            ) <= max_width:

                current_line = test_line

            else:

                if current_line:
                    lines.append(current_line)

                current_line = word

        if current_line:
            lines.append(current_line)

        return lines

    # ========================================================
    # HELPER FUNCTION: DRAW SUBJECT TABLE HEADER
    # ========================================================

    def draw_table_header(y_position):

        pdf.setFillColor(colors.lightblue)

        pdf.rect(
            40,
            y_position - 5,
            width - 80,
            25,
            fill=1,
            stroke=0
        )

        pdf.setFillColor(colors.black)

        pdf.setFont("Helvetica-Bold", 10)

        pdf.drawString(
            50,
            y_position + 3,
            "Subject"
        )

        pdf.drawString(
            350,
            y_position + 3,
            "Marks"
        )

    # ========================================================
    # REPORT HEADER
    # ========================================================

    pdf.setFillColor(colors.darkblue)

    pdf.setFont("Helvetica-Bold", 20)

    pdf.drawCentredString(
        width / 2,
        height - 50,
        "STUDENT PERFORMANCE REPORT"
    )

    pdf.setStrokeColor(colors.darkblue)

    pdf.line(
        40,
        height - 65,
        width - 40,
        height - 65
    )

    # ========================================================
    # STUDENT DETAILS
    # ========================================================

    y = height - 110

    pdf.setFillColor(colors.black)

    pdf.setFont("Helvetica-Bold", 14)

    pdf.drawString(
        40,
        y,
        "Student Information"
    )

    y -= 30

    pdf.setFont("Helvetica", 11)

    details = [

        f"Student ID: {student.student_id}",

        f"Student Name: {student.name}",

        f"Email: {student.email}",

        f"Department: {student.department}",

    ]

    for detail in details:

        pdf.drawString(
            50,
            y,
            detail
        )

        y -= 22

    # ========================================================
    # SUBJECT-WISE MARKS
    # ========================================================

    y -= 20

    pdf.setFont("Helvetica-Bold", 14)

    pdf.drawString(
        40,
        y,
        "Subject-wise Marks"
    )

    y -= 30

    draw_table_header(y)

    y -= 30

    pdf.setFont("Helvetica", 10)

    # DISPLAY SUBJECTS WITH AUTOMATIC TEXT WRAPPING

    for mark in marks:

        subject_name = str(mark.subject)

        subject_lines = wrap_text(
            subject_name,
            280,
            "Helvetica",
            10
        )

        # CALCULATE ROW HEIGHT
        row_height = max(
            22,
            len(subject_lines) * 14 + 8
        )

        # CHECK PAGE SPACE
        if y - row_height < 70:

            pdf.showPage()

            y = height - 60

            draw_table_header(y)

            y -= 30

            pdf.setFont("Helvetica", 10)

        # DRAW SUBJECT NAME
        for index, line in enumerate(subject_lines):

            pdf.drawString(
                50,
                y - (index * 14),
                line
            )

        # DRAW MARKS
        pdf.drawString(
            350,
            y,
            str(mark.marks)
        )

        y -= row_height

    # ========================================================
    # PERFORMANCE SUMMARY
    # ========================================================

    y -= 20

    if y < 200:

        pdf.showPage()

        y = height - 70

    pdf.setFont("Helvetica-Bold", 14)

    pdf.drawString(
        40,
        y,
        "Performance Summary"
    )

    y -= 30

    pdf.setFont("Helvetica", 11)

    summary = [

        f"Total Marks: {total_marks}",

        f"Average Marks: {average_marks}",

        f"Percentage: {percentage}%",

        f"CGPA: {cgpa}",

        f"Grade: {grade}",

        f"Performance: {performance_status}",

        f"Result Status: {result_status}",

    ]

    for item in summary:

        pdf.drawString(
            50,
            y,
            item
        )

        y -= 22

    # ========================================================
    # FOOTER
    # ========================================================

    pdf.setFont("Helvetica-Oblique", 9)

    pdf.drawCentredString(
        width / 2,
        30,
        "Generated by Student Performance & Analytics System"
    )

    # SAVE PDF
    pdf.save()

    return response

# ============================================================
# DASHBOARD
# ============================================================

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
    # STUDENTS + SEARCH
    # ========================================================

    students = Student.objects.all()

    if search_query:

        students = students.filter(
            Q(name__icontains=search_query) |
            Q(student_id__icontains=search_query)
        )


    # ========================================================
    # STUDENT-WISE PERFORMANCE
    # ========================================================

    student_results = []

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
    # BUILD STUDENT RESULTS
    # ========================================================

    for student in students:

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


        

        # ====================================================
        # ADD STUDENT RESULT
        # ====================================================

        student_results.append({

            "student": student,

            "total_marks": student_total_marks,

            "average_marks": student_average_marks,

            "percentage": student_percentage,

            "cgpa": student_cgpa,

            "grade": student_grade,

            "performance_status": student_performance,

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

            performance_distribution[
                "needs_improvement"
            ] += 1


    # ========================================================
    # PAGINATION
    # IMPORTANT: THIS MUST BE AFTER THE LOOP
    # ========================================================

    paginator = Paginator(
        student_results,
        5
    )

    page_number = request.GET.get(
        "page"
    )

    student_results = paginator.get_page(
        page_number
    )

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

            "performance_distribution":
                performance_distribution,

            "subject_results": subject_results,

            "search_query": search_query,
            
        }
    )


# ==========================================
# ADD STUDENT
# ==========================================

def student_add(request):

    if request.method == "POST":
        form = StudentForm(request.POST)

        if form.is_valid():
            form.save()
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

def student_delete(request, student_id):

    student = get_object_or_404(
        Student,
        student_id=student_id
    )

    if request.method == "POST":
        student.delete()
        return redirect("student_list")

    return render(
        request,
        "students/student_confirm_delete.html",
        {
            "student": student,
        },
    )

def home(request):
    return render(request, "students/home.html")