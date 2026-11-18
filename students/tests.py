from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from students.models import Student
import datetime


class AdminAuthTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_user(
            username="testadmin",
            password="adminpassword123",
            is_staff=True,
            is_superuser=True,
        )
        self.normal_user = User.objects.create_user(
            username="normaluser",
            password="userpassword123",
            is_staff=False,
            is_superuser=False,
        )
        self.student = Student.objects.create(
            student_id="STU999",
            name="Test Student",
            email="teststudent@example.com",
            date_of_birth=datetime.date(2002, 5, 10),
            department="CSE",
        )

    def test_home_page_is_public(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "students/home.html")
        self.assertContains(response, "Admin Login")

    def test_admin_login_page_renders(self):
        response = self.client.get(reverse("admin_login"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "students/admin_login.html")
        self.assertContains(response, "Admin Sign In")
        self.assertContains(response, "togglePasswordBtn")
        self.assertContains(response, "Back to Home Page")

    def test_admin_login_invalid_credentials(self):
        response = self.client.post(
            reverse("admin_login"),
            {"username": "testadmin", "password": "wrongpassword"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid username or password")

    def test_admin_login_non_staff_user_denied(self):
        response = self.client.post(
            reverse("admin_login"),
            {"username": "normaluser", "password": "userpassword123"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Access restricted")

    def test_admin_login_success_redirects_to_dashboard(self):
        response = self.client.post(
            reverse("admin_login"),
            {"username": "testadmin", "password": "adminpassword123"},
        )
        self.assertRedirects(response, reverse("dashboard"))

    def test_admin_login_with_next_url(self):
        next_url = reverse("student_add")
        response = self.client.post(
            f"{reverse('admin_login')}?next={next_url}",
            {"username": "testadmin", "password": "adminpassword123"},
        )
        self.assertRedirects(response, next_url)

    def test_admin_logout_redirects_to_home(self):
        self.client.login(username="testadmin", password="adminpassword123")
        response = self.client.get(reverse("admin_logout"))
        self.assertRedirects(response, reverse("home"))

    def test_protected_pages_redirect_unauthenticated_user(self):
        protected_urls = [
            reverse("dashboard"),
            reverse("student_list"),
            reverse("student_add"),
            reverse("student_detail", kwargs={"student_id": self.student.student_id}),
            reverse("student_edit", kwargs={"student_id": self.student.student_id}),
            reverse("student_delete", kwargs={"student_id": self.student.student_id}),
            reverse("student_pdf_report", kwargs={"student_id": self.student.student_id}),
        ]

        for url in protected_urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertRedirects(
                    response,
                    f"{reverse('admin_login')}?next={url}",
                )

    def test_dashboard_displays_admin_username_and_logout(self):
        self.client.login(username="testadmin", password="adminpassword123")
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "testadmin")
        self.assertContains(response, reverse("admin_logout"))

    def test_dashboard_student_ranking_system(self):
        from students.models import Subject, Marks
        math = Subject.objects.create(code="MTH101", name="Mathematics")
        phy = Subject.objects.create(code="PHY101", name="Physics")

        student_b = Student.objects.create(
            student_id="STU888",
            name="Bob High Scorer",
            email="bob@example.com",
            date_of_birth=datetime.date(2002, 1, 1),
            department="CSE",
        )

        Marks.objects.create(student=self.student, subject=math, marks=60)
        Marks.objects.create(student=student_b, subject=math, marks=95)

        self.client.login(username="testadmin", password="adminpassword123")
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)

        self.assertContains(response, "Student Performance Ranking System")
        self.assertContains(response, "Bob High Scorer")
        self.assertContains(response, "🥇 #1")
        self.assertIn("top_rankers", response.context)
        self.assertEqual(response.context["top_rankers"][0]["student"].student_id, "STU888")
        self.assertEqual(response.context["top_rankers"][0]["rank"], 1)

    def test_cannot_access_protected_pages_after_logout(self):
        # 1. Login
        self.client.login(username="testadmin", password="adminpassword123")
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)

        # 2. Logout
        logout_response = self.client.get(reverse("admin_logout"))
        self.assertRedirects(logout_response, reverse("home"))

        # 3. Verify access to dashboard is now blocked and redirects to login
        followup_response = self.client.get(reverse("dashboard"))
        self.assertRedirects(
            followup_response,
            f"{reverse('admin_login')}?next={reverse('dashboard')}",
        )

    def test_all_crud_templates_render_for_admin(self):
        self.client.login(username="testadmin", password="adminpassword123")

        # 1. Student List
        res_list = self.client.get(reverse("student_list"))
        self.assertEqual(res_list.status_code, 200)
        self.assertTemplateUsed(res_list, "students/student_list.html")

        # 2. Student Add Form
        res_add = self.client.get(reverse("student_add"))
        self.assertEqual(res_add.status_code, 200)
        self.assertTemplateUsed(res_add, "students/student_form.html")
        self.assertContains(res_add, "Add Student")

        # 3. Student Detail
        res_detail = self.client.get(
            reverse("student_detail", kwargs={"student_id": self.student.student_id})
        )
        self.assertEqual(res_detail.status_code, 200)
        self.assertTemplateUsed(res_detail, "students/student_detail.html")
        self.assertContains(res_detail, self.student.name)

        # 4. Student Edit Form
        res_edit = self.client.get(
            reverse("student_edit", kwargs={"student_id": self.student.student_id})
        )
        self.assertEqual(res_edit.status_code, 200)
        self.assertTemplateUsed(res_edit, "students/student_form.html")
        self.assertContains(res_edit, "Edit Student")

        # 5. Student Delete Confirmation
        res_del = self.client.get(
            reverse("student_delete", kwargs={"student_id": self.student.student_id})
        )
        self.assertEqual(res_del.status_code, 200)
        self.assertTemplateUsed(res_del, "students/student_confirm_delete.html")
        self.assertContains(res_del, "Delete Student Record")

    def test_django_admin_panel_branding_and_index(self):
        self.client.login(username="testadmin", password="adminpassword123")
        res = self.client.get("/admin/")
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Student Performance & Analytics System")
        self.assertContains(res, "Administrator Control Panel")
        self.assertContains(res, "Analytics Dashboard")

    def test_django_admin_student_changelist(self):
        self.client.login(username="testadmin", password="adminpassword123")
        res = self.client.get("/admin/students/student/")
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, self.student.student_id)
        self.assertContains(res, self.student.name)
        self.assertContains(res, "CSE")

    def test_student_pdf_report_generates_valid_pdf(self):
        self.client.login(username="testadmin", password="adminpassword123")
        url = reverse("student_pdf_report", kwargs={"student_id": self.student.student_id})
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res["Content-Type"], "application/pdf")
        self.assertIn("attachment;", res["Content-Disposition"])
        self.assertIn(f"{self.student.student_id}_Academic_Transcript.pdf", res["Content-Disposition"])
        self.assertTrue(res.content.startswith(b"%PDF-"))
