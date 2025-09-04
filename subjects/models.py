from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Subject(models.Model):
    code = models.CharField(max_length=20, unique=True)   # e.g. "GCSE-BIO"
    name = models.CharField(max_length=100)               # e.g. "GCSE Biology"

    def __str__(self):
        return f"{self.name} ({self.code})"

class UserSubject(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'subject')


class TeacherSubject(models.Model):
    teacher = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='teacher_subjects'
    )
    subject = models.ForeignKey('Subject', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('teacher', 'subject')

    def __str__(self):
        return f"{self.teacher.username} → {self.subject.name}"