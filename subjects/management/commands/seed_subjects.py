from django.core.management.base import BaseCommand
from subjects.models import Subject

SUBJECTS = [
    ("GCSE-MATH", "GCSE Maths"),
    ("GCSE-BIO", "GCSE Biology"),
    ("GCSE-CHEM", "GCSE Chemistry"),
    ("GCSE-PHY", "GCSE Physics"),
    ("GCSE-CS", "GCSE Computer Science"),
    ("AL-MATH", "A-Level Maths"),
    ("AL-PHY", "A-Level Physics"),
    ("AL-CS", "A-Level Computer Science"),
]

class Command(BaseCommand):
    help = "Seed default subjects"

    def handle(self, *args, **kwargs):
        created = 0
        for code, name in SUBJECTS:
            obj, was_created = Subject.objects.get_or_create(code=code, defaults={'name': name})
            created += 1 if was_created else 0
        self.stdout.write(self.style.SUCCESS(f"Seeded subjects. New: {created}"))
