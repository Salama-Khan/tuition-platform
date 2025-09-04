from django.urls import path
from . import views
from . import bookings as booking_views

urlpatterns = [
    path('me/', views.me, name='api_me'),
    path('subjects/', views.subjects, name='api_subjects'),
    path('my-subjects/', views.my_subjects, name='api_my_subjects'),

    path('bookings/request/', booking_views.request_booking, name='api_request_booking'),
    path('bookings/mine/', booking_views.my_bookings, name='api_my_bookings'),
    path('bookings/<int:booking_id>/approve/', booking_views.approve_booking, name='api_approve_booking'),
    path('bookings/<int:booking_id>/reject/', booking_views.reject_booking, name='api_reject_booking'),
]
