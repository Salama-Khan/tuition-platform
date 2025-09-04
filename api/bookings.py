# api/bookings.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from datetime import datetime, timedelta
from django.contrib.auth.models import Group
from bookings.models import LessonBooking, TeacherAvailability
from rest_framework import status

def is_teacher(user):
    return user.groups.filter(name="teacher").exists()

def is_admin(user):
    # using Django staff as "admin" here; you can switch to a group if you prefer
    return user.is_staff

def booking_to_dict(b: LessonBooking):
    return {
        "id": b.id,
        "student": b.student.username,
        "teacher": b.teacher.username,
        "subject": b.subject.name,
        "start": b.start_datetime,
        "end": b.end_datetime,
        "status": b.status,
        "created_at": b.created_at,
    }

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def request_booking(request):
    """Student requests a booking with a teacher availability"""
    user = request.user
    availability_id = request.data.get('availability_id')
    duration = int(request.data.get('duration', 1))  # hours

    try:
        availability = TeacherAvailability.objects.get(id=availability_id)
    except TeacherAvailability.DoesNotExist:
        return Response({"error": "Availability not found"}, status=404)

    # next occurrence of that weekday
    today = timezone.now().date()
    days_ahead = (availability.weekday - today.weekday()) % 7
    start_date = today + timedelta(days=days_ahead)
    start_dt = timezone.make_aware(datetime.combine(start_date, availability.start_time))
    end_dt = start_dt + timedelta(hours=duration)

    # 24h rule
    if start_dt < timezone.now() + timedelta(hours=24):
        return Response({"error": "Must book at least 24h in advance"}, status=400)

    booking = LessonBooking.objects.create(
        student=user,
        teacher=availability.teacher,
        subject=availability.subject,
        start_datetime=start_dt,
        end_datetime=end_dt,
        status='pending',
    )
    return Response(booking_to_dict(booking), status=201)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_bookings(request):
    """List bookings for the current user (student sees theirs; teacher sees theirs)"""
    user = request.user
    if is_teacher(user) or is_admin(user):
        qs = LessonBooking.objects.filter(teacher=user).order_by('-created_at')
    else:
        qs = LessonBooking.objects.filter(student=user).order_by('-created_at')
    return Response([booking_to_dict(b) for b in qs])

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def approve_booking(request, booking_id: int):
    """Teacher (owner) or admin can approve a pending booking"""
    user = request.user
    try:
        booking = LessonBooking.objects.get(id=booking_id)
    except LessonBooking.DoesNotExist:
        return Response({"error": "Booking not found"}, status=404)

    if not (is_admin(user) or (is_teacher(user) and booking.teacher_id == user.id)):
        return Response({"error": "Not allowed"}, status=403)

    if booking.status != 'pending':
        return Response({"error": "Only pending bookings can be approved"}, status=400)

    booking.status = 'approved'
    booking.save()
    return Response(booking_to_dict(booking))

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reject_booking(request, booking_id: int):
    """Teacher (owner) or admin can reject a pending booking"""
    user = request.user
    try:
        booking = LessonBooking.objects.get(id=booking_id)
    except LessonBooking.DoesNotExist:
        return Response({"error": "Booking not found"}, status=404)

    if not (is_admin(user) or (is_teacher(user) and booking.teacher_id == user.id)):
        return Response({"error": "Not allowed"}, status=403)

    if booking.status != 'pending':
        return Response({"error": "Only pending bookings can be rejected"}, status=400)

    booking.status = 'rejected'
    booking.save()
    return Response(booking_to_dict(booking))
