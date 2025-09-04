from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from subjects.models import Subject, UserSubject, TeacherSubject

User = get_user_model()

class Task(models.Model):
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    release_dt = models.DateTimeField(null=True, blank=True)
    due_dt = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        # only teachers; teacher must teach this subject
        if self.teacher and not self.teacher.groups.filter(name='teacher').exists():
            raise ValidationError({'teacher': 'Only teachers can create tasks.'})
        if self.teacher_id and self.subject_id:
            if not TeacherSubject.objects.filter(teacher_id=self.teacher_id, subject_id=self.subject_id).exists():
                raise ValidationError({'subject': 'You have not selected this subject.'})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.subject.name})"

class Submission(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submissions')
    file = models.FileField(upload_to='submissions/')
    submitted_at = models.DateTimeField(auto_now_add=True)

    # feedback (simple MVP)
    feedback_text = models.TextField(blank=True)
    feedback_at = models.DateTimeField(null=True, blank=True)
    locked = models.BooleanField(default=False)

    def clean(self):
        errors = {}
        # student must be a student and must have selected the subject
        if self.student and self.student.groups.filter(name='teacher').exists():
            errors['student'] = 'Only students can submit.'
        if self.task_id and self.student_id:
            if not UserSubject.objects.filter(user_id=self.student_id, subject_id=self.task.subject_id).exists():
                errors['file'] = 'You have not selected this task’s subject.'
        # cannot lock without feedback
        if self.locked and not self.feedback_text:
            errors['feedback_text'] = 'Cannot lock without feedback.'
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student.username} → {self.task.title}"
