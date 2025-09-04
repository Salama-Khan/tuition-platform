from django.db import models
from django.contrib.auth import get_user_model
from subjects.models import Subject, TeacherSubject
from django.core.exceptions import ValidationError

User = get_user_model()

class TeacherAvailability(models.Model):
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='availabilities')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    weekday = models.IntegerField(choices=[(i, day) for i, day in enumerate(
        ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
    )])
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.teacher.username} - {self.subject.name} on {self.get_weekday_display()} {self.start_time}-{self.end_time}"
    def clean(self):
        # Only allow users in the "teacher" group
        if self.teacher and not self.teacher.groups.filter(name="teacher").exists():
            raise ValidationError({"teacher": "Selected user is not in the 'teacher' group."})
        if self.end_time and self.start_time and self.end_time <= self.start_time:
            raise ValidationError({"end_time": "End time must be after start time."})
        if self.teacher_id and self.subject_id:
            if not TeacherSubject.objects.filter(teacher_id=self.teacher_id, subject_id=self.subject_id).exists():
                raise ValidationError({"subject": "This teacher has not selected this subject."})

    def save(self, *args, **kwargs):
        self.full_clean()  # ensures clean() runs in admin/shell
        return super().save(*args, **kwargs)

class LessonBooking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]

    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='teaching_bookings')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.subject.name} with {self.teacher.username} ({self.status})"
    def clean(self):
        errors = {}
        # teacher must be in 'teacher' group
        if self.teacher and not self.teacher.groups.filter(name="teacher").exists():
            errors["teacher"] = "Selected user is not in the 'teacher' group."
        # basic datetime sanity
        if self.end_datetime and self.start_datetime and self.end_datetime <= self.start_datetime:
            errors["end_datetime"] = "End time must be after start time."
        if errors:
            raise ValidationError(errors)
        if self.teacher_id and self.subject_id:
            if not TeacherSubject.objects.filter(teacher_id=self.teacher_id, subject_id=self.subject_id).exists():
                errors["subject"] = "Teacher does not teach this subject."
        if errors:
            raise ValidationError(errors)
    # ✅ and this:
    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
