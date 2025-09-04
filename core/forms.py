from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date
from django.conf import settings

User = get_user_model()

def calc_age(d: date) -> int:
    today = timezone.localdate()
    return today.year - d.year - ((today.month, today.day) < (d.month, d.day))

class SignupForm(UserCreationForm):
    email = forms.EmailField(required=True)
    dob = forms.DateField(required=False, help_text="YYYY-MM-DD")
    parent_email = forms.EmailField(required=False, help_text="Required if under 16")
    agree = forms.BooleanField(required=True, label="I agree to the Terms & Privacy")
    # teacher self-signup
    is_teacher = forms.BooleanField(required=False, label="I'm a teacher")
    invite_code = forms.CharField(required=False, help_text="Invite code (teachers only)")

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2", "dob", "parent_email", "is_teacher", "invite_code", "agree")

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("An account with this email already exists.")
        return email

    def clean(self):
        cleaned = super().clean()
        dob = cleaned.get("dob")
        parent_email = cleaned.get("parent_email", "")
        is_teacher = cleaned.get("is_teacher") or False
        invite_code = (cleaned.get("invite_code") or "").strip()

        # Under-16 rule
        if dob:
            age = calc_age(dob)
            if age < 16 and not parent_email:
                self.add_error("parent_email", "Parent/Guardian email is required if under 16.")

        # Teacher invite code
        if is_teacher:
            expected = getattr(settings, "TEACHER_INVITE_CODE", "")
            if not expected:
                self.add_error("invite_code", "Teacher signup is not enabled (missing invite code).")
            elif invite_code != expected:
                self.add_error("invite_code", "Invalid invite code.")

        return cleaned
