from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    
    path("students/", views.student_list, name="student_list"),
    path("students/add/", views.student_add, name="student_add"),
    path( "students/<str:student_id>/edit/", views.student_edit, name="student_edit"),
    path("students/<str:student_id>/delete/",views.student_delete,name="student_delete"),
    
    path("students/<str:student_id>/", views.student_detail, name="student_detail"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path(
    "students/<str:student_id>/pdf/",views.student_pdf_report,name="student_pdf_report"),
]