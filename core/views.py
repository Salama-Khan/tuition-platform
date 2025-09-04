from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from subjects.models import Subject, UserSubject, TeacherSubject
from django.views.decorators.http import require_GET
from bookings.models import LessonBooking
from django.http import HttpResponseForbidden, Http404
from django.contrib.auth.models import Group
from .forms import SignupForm
from .models import Profile
from homework.models import Task, Submission
from django.utils import timezone
from django.contrib import messages

def is_student(user):
    return user.groups.filter(name="student").exists()
    
def ensure_group(name):
    Group.objects.get_or_create(name=name)

def add_to_group(user, name):
    ensure_group(name)
    user.groups.add(Group.objects.get(name=name))

def signup(request):
    if request.user.is_authenticated:
        # route to their dashboard if they hit signup while logged in
        return redirect('teacher_dashboard' if is_teacher(request.user) else 'dashboard')

    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data["email"].lower()
            user.save()

            # Group: teacher with valid invite → teacher; else student
            if form.cleaned_data.get("is_teacher"):
                add_to_group(user, "teacher")
                # you might still want them to set subjects next
                next_url = 'teacher_subjects'
            else:
                add_to_group(user, "student")
                next_url = 'choose_subjects'

            # Profile
            dob = form.cleaned_data.get("dob")
            parent_email = form.cleaned_data.get("parent_email", "")
            under_16 = False
            if dob:
                from datetime import date
                from django.utils import timezone
                today = timezone.localdate()
                under_16 = (today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))) < 16
            Profile.objects.create(user=user, dob=dob, parent_email=parent_email, under_16=under_16)

            login(request, user)
            return redirect(next_url)
    else:
        form = SignupForm()

    return render(request, 'core/signup.html', {'form': form})

def home(request):
    if request.user.is_authenticated:
        # 🚦 already logged in: route by role
        return redirect('teacher_dashboard' if is_teacher(request.user) else 'dashboard')

    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        # 🚦 route by role after login
        return redirect('teacher_dashboard' if is_teacher(user) else 'dashboard')
    return render(request, 'core/home.html', {'form': form})



@login_required
@login_required
def dashboard(request):
    # 🚫 teachers shouldn’t see the student dashboard
    if is_teacher(request.user) or request.user.is_staff:
        return redirect('teacher_dashboard')

    my_subjects = Subject.objects.filter(usersubject__user=request.user)
    my_bookings = LessonBooking.objects.filter(student=request.user)\
        .select_related('teacher','subject').order_by('-created_at')[:20]

    return render(request, 'core/dashboard.html', {
        'my_subjects': my_subjects,
        'my_bookings': my_bookings,
        'is_teacher': False,  # hard-false since teachers are redirected
    })


@login_required
def teacher_dashboard(request):
    if not (is_teacher(request.user) or request.user.is_staff):
        return HttpResponseForbidden("Not allowed")

    pending = LessonBooking.objects.filter(
        teacher=request.user, status='pending'
    ).select_related('student','subject').order_by('start_datetime')

    recent = LessonBooking.objects.filter(
        teacher=request.user
    ).exclude(status='pending').select_related('student','subject').order_by('-created_at')[:20]

    return render(request, 'core/teacher_dashboard.html', {
        'pending': pending,
        'recent': recent,
    })


@login_required
def choose_subjects(request):
    subjects = Subject.objects.all().order_by('name')
    if request.method == 'POST':
        # clear existing
        UserSubject.objects.filter(user=request.user).delete()
        # add selected
        selected = request.POST.getlist('subjects')
        for sid in selected:
            UserSubject.objects.create(user=request.user, subject_id=sid)
        return redirect('dashboard')
    return render(request, 'core/choose_subjects.html', {'subjects': subjects})

@require_GET
def logout_view(request):
    logout(request)
    return redirect('home')

def is_teacher(user):
    return user.groups.filter(name="teacher").exists()

@login_required
def teacher_subjects(request):
    if not (is_teacher(request.user) or request.user.is_staff):
        return HttpResponseForbidden("Not allowed")

    all_subjects = Subject.objects.all().order_by('name')
    if request.method == 'POST':
        TeacherSubject.objects.filter(teacher=request.user).delete()
        for sid in request.POST.getlist('subjects'):
            TeacherSubject.objects.create(teacher=request.user, subject_id=sid)
        return redirect('teacher_dashboard')
    chosen_ids = set(TeacherSubject.objects.filter(teacher=request.user).values_list('subject_id', flat=True))
    return render(request, 'core/teacher_subjects.html', {
        'subjects': all_subjects, 'chosen_ids': chosen_ids
    })

@login_required
def teacher_tasks(request):
    if not (is_teacher(request.user) or request.user.is_staff):
        return HttpResponseForbidden("Not allowed")
    tasks = Task.objects.filter(teacher=request.user).select_related('subject')\
             .order_by('-created_at')
    return render(request, 'core/teacher_tasks.html', {'tasks': tasks})

@login_required
def teacher_task_new(request):
    if not (is_teacher(request.user) or request.user.is_staff):
        return HttpResponseForbidden("Not allowed")
    subjects = Subject.objects.filter(teachersubject__teacher=request.user).distinct().order_by('name')
    if request.method == 'POST':
        s_id = request.POST.get('subject_id')
        title = request.POST.get('title')
        desc = request.POST.get('description', '')
        due = request.POST.get('due_dt') or None
        t = Task(teacher=request.user, subject_id=s_id, title=title, description=desc, due_dt=due)
        t.save()  # runs validation (teacher teaches subject)
        return redirect('teacher_tasks')
    return render(request, 'core/teacher_task_new.html', {'subjects': subjects})

@login_required
def student_tasks(request):
    if not is_student(request.user):
        return HttpResponseForbidden("Not allowed")

    my_subject_ids = UserSubject.objects.filter(user=request.user).values_list('subject_id', flat=True)
    tasks = (Task.objects
             .filter(subject_id__in=my_subject_ids)
             .select_related('subject', 'teacher')
             .order_by('-created_at'))

    # latest submission per task (dict) AND a set of submitted task ids
    task_ids = [t.id for t in tasks]
    latest_by_task = {}
    submitted_task_ids = set()
    for s in Submission.objects.filter(student=request.user, task_id__in=task_ids).order_by('-submitted_at'):
        if s.task_id not in latest_by_task:
            latest_by_task[s.task_id] = {
                "id": s.id,
                "submitted_at": s.submitted_at,
                "feedback_text": s.feedback_text,
                "feedback_at": s.feedback_at,
                "locked": s.locked,
                "file_url": s.file.url if s.file else "",
            }
        submitted_task_ids.add(s.task_id)

    return render(request, 'core/student_tasks.html', {
        'tasks': tasks,
        'latest_by_task': latest_by_task,
        'submitted_task_ids': submitted_task_ids,   # 👈 use this in template
    })


@login_required
def student_submit(request, task_id):
    if not is_student(request.user):
        return HttpResponseForbidden("Not allowed")

    task = get_object_or_404(Task.objects.select_related('subject'), id=task_id)

    # only if student has this subject
    if not UserSubject.objects.filter(user=request.user, subject=task.subject).exists():
        return HttpResponseForbidden("This task is not for your subjects.")

    # latest submission (if any)
    latest = (Submission.objects
              .filter(student=request.user, task=task)
              .order_by('-submitted_at')
              .first())

    # 🚫 block if locked
    if latest and latest.locked:
        return render(request, 'core/student_submit.html', {
            'task': task,
            'locked': True,
            'latest': latest,
            'error': "This submission is locked by your teacher. You can no longer resubmit.",
        })

    if request.method == 'POST':
        f = request.FILES.get('file')
        if not f:
            return render(request, 'core/student_submit.html', {'task': task, 'error': 'Please choose a file.'})
        Submission.objects.create(task=task, student=request.user, file=f)
        return redirect('student_tasks')

    return render(request, 'core/student_submit.html', {'task': task, 'latest': latest, 'locked': False})

@login_required
def teacher_submissions(request):
    if not (is_teacher(request.user) or request.user.is_staff):
        return HttpResponseForbidden("Not allowed")

    subs = (Submission.objects
            .filter(task__teacher=request.user)
            .select_related('task', 'student', 'task__subject')
            .order_by('-submitted_at'))
    return render(request, 'core/teacher_submissions.html', {'subs': subs})

@login_required
def teacher_task_submissions(request, task_id):
    if not (is_teacher(request.user) or request.user.is_staff):
        return HttpResponseForbidden("Not allowed")

    task = get_object_or_404(Task.objects.select_related('subject'), id=task_id, teacher=request.user)
    subs = (Submission.objects
            .filter(task=task)
            .select_related('student')
            .order_by('-submitted_at'))
    return render(request, 'core/teacher_task_submissions.html', {'task': task, 'subs': subs})

@login_required
def teacher_submission_detail(request, submission_id):
    if not (is_teacher(request.user) or request.user.is_staff):
        return HttpResponseForbidden("Not allowed")

    sub = get_object_or_404(
        Submission.objects.select_related('task', 'student', 'task__subject'),
        id=submission_id
    )
    # ownership check: only the task's teacher can view/edit
    if sub.task.teacher_id != request.user.id and not request.user.is_staff:
        return HttpResponseForbidden("Not allowed")

    if request.method == 'POST':
        feedback = request.POST.get('feedback_text', '').strip()
        lock = bool(request.POST.get('lock'))
        sub.feedback_text = feedback
        sub.locked = lock
        from django.utils import timezone
        sub.feedback_at = timezone.now() if feedback else None
        sub.save()
        return redirect('teacher_submissions')

    return render(request, 'core/teacher_submission_detail.html', {'sub': sub})
