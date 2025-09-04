from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    dob = models.DateField(null=True, blank=True)
    parent_email = models.EmailField(blank=True)
    under_16 = models.BooleanField(default=False)

    def __str__(self):
        return f"Profile({self.user.username})"
