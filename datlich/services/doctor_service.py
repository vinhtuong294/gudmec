from datlich.models import Doctor
from datetime import datetime, timedelta

class DoctorService:
    def get_all_departments(self):
        return Doctor.objects.all()
    def get_one_doctors(self,id):
        doctor = Doctor.objects.select_related('department','user').get(id=id)
        
        return {
            "id": doctor.id,
            "name": doctor.user.fullname,
            "position": doctor.position,
            "description": doctor.description,
            "room_address": doctor.room_address,
            "service_prices": doctor.service_prices,
            "department": doctor.department.name_department,
            "avatar":doctor.avatar,
            "average_rating":doctor.average_rate
        }