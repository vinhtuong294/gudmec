from datetime import datetime, timedelta
from django.db import transaction
from django.shortcuts import get_object_or_404
from ..models import *
from ..repositories import doctor_repository, shift_repository
from ..serializers import (
    DoctorInfoResponseSerializer,
    DoctorResponseSerializer,
    ScheduleResponseSerializer,
    BookingModelSerializer,
)
from .exceptions import NotFoundException


class DoctorService:
    def __init__(self, doctor_repo: doctor_repository, shift_repo: shift_repository):
        self.doctor_repo = doctor_repo
        self.shift_repo = shift_repo

    def get_all_doctors(self):
        """Fetch all doctors with detailed information."""
        doctors = self.doctor_repo.get_all()
        return DoctorInfoResponseSerializer(doctors, many=True).data

    def create_new_doctor(self, user_model):
        """Create a new doctor."""
        doctor = Doctor(user=user_model)
        doctor.save()
        return DoctorResponseSerializer(doctor).data  # Return serialized data after creation

    def update_info(self, doctor_request):
        """Update doctor information."""
        doctor = get_object_or_404(Doctor, pk=doctor_request.get("id"))
        doctor.description = doctor_request.get("description")
        doctor.position = doctor_request.get("position")
        doctor.room_address = doctor_request.get("room_address")
        doctor.service_prices = doctor_request.get("service_prices")
        doctor.department = get_object_or_404(
            Department, pk=doctor_request.get("department_id")
        )
        doctor.save()
        return DoctorResponseSerializer(doctor).data  # Return the updated doctor's data

    def get_schedule_responses(self, doctor_id):
        """Fetch schedules of a specific doctor."""
        doctor = self.doctor_repo.get_by_id(doctor_id)
        if not doctor:
            raise NotFoundException(f"Doctor with ID {doctor_id} not found.")
        schedules = doctor.schedule_set.all()
        return ScheduleResponseSerializer(schedules, many=True).data  # Return schedules serialized

    def get_doctor_response(self, doctor_id):
        """Fetch a single doctor's details."""
        doctor = self.doctor_repo.get_by_id(doctor_id)
        if not doctor:
            raise NotFoundException(f"Doctor with ID {doctor_id} not found.")
        return DoctorResponseSerializer(doctor).data  # Return serialized doctor's data

    def get_booking_models(self, doctor_id):
        """Generate booking models for a doctor's next 30 days."""
        doctor = self.doctor_repo.get_by_id(doctor_id)
        if not doctor:
            raise NotFoundException(f"Doctor with ID {doctor_id} not found.")

        shifts = self.shift_repo.get_all()  # Get all available shifts
        bookings = []
        for day_offset in range(30):
            day = datetime.now().date() + timedelta(days=day_offset)
            booking_model = {"day": day, "list_shift": []}

            # Exclude weekends
            if day.weekday() >= 5:  # If it's Saturday or Sunday, skip
                bookings.append(booking_model)
                continue

            # Get shifts of the doctor for the specific day
            schedule_shifts = doctor.schedule_set.filter(date=day).values_list(
                "shift_id", flat=True
            )
            available_shifts = [
                shift
                for shift in shifts
                if shift.id not in schedule_shifts
                and (
                    day != datetime.now().date()
                    or shift.time_start > (datetime.now() + timedelta(minutes=20)).time()
                )
            ]

            booking_model["list_shift"] = available_shifts  # Add available shifts for the day
            bookings.append(booking_model)

        return BookingModelSerializer(bookings, many=True).data  # Return serialized booking models
