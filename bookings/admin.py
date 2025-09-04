from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import TeacherAvailability, LessonBooking

User = get_user_model()

@admin.register(TeacherAvailability)
class TeacherAvailabilityAdmin(admin.ModelAdmin):
    list_display = ("teacher", "subject", "weekday", "start_time", "end_time")

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "teacher":
            kwargs["queryset"] = User.objects.filter(groups__name="teacher")
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(LessonBooking)
class LessonBookingAdmin(admin.ModelAdmin):
    list_display = ("student", "teacher", "subject", "start_datetime", "end_datetime", "status", "created_at")
    list_filter = ("status", "subject", "teacher")
    search_fields = ("student__username", "teacher__username")

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "teacher":
            kwargs["queryset"] = User.objects.filter(groups__name="teacher")
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
