from django.contrib import admin
from .models import Task, Submission

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("title", "subject", "teacher", "due_dt", "created_at")
    list_filter = ("subject", "teacher")

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ("task", "student", "submitted_at", "locked")
    list_filter = ("locked", "task__subject")
