from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('choose-subjects/', views.choose_subjects, name='choose_subjects'),
    path('logout/', views.logout_view, name='logout'), 
    path('teacher/dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('signup/', views.signup, name='signup'),
    path('teacher/subjects/', views.teacher_subjects, name='teacher_subjects'),
    path('teacher/tasks/', views.teacher_tasks, name='teacher_tasks'),
    path('teacher/tasks/new/', views.teacher_task_new, name='teacher_task_new'),
    path('student/tasks/', views.student_tasks, name='student_tasks'),
    path('student/tasks/<int:task_id>/submit/', views.student_submit, name='student_submit'),
    path('teacher/submissions/', views.teacher_submissions, name='teacher_submissions'),
    path('teacher/submissions/<int:submission_id>/', views.teacher_submission_detail, name='teacher_submission_detail'),
    path('teacher/tasks/<int:task_id>/submissions/', views.teacher_task_submissions, name='teacher_task_submissions'),



]
