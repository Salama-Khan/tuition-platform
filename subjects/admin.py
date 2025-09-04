from django.contrib import admin
from .models import Subject, UserSubject, TeacherSubject

admin.site.register(Subject)
admin.site.register(UserSubject)
admin.site.register(TeacherSubject)
