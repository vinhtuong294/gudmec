from ..models import Doctor

class DoctorRepository:
    @staticmethod
    def find_all():
        return Doctor.objects.all()

    @staticmethod
    def find_by_id(doctor_id):
        return Doctor.objects.filter(id=doctor_id).first()

    @staticmethod
    def find_all_info():
        return Doctor.objects.select_related("user", "department").values(
            "id",
            "position",
            "description",
            "room_address",
            "service_prices",
            "department__name",
            "user__first_name",
            "user__last_name",
            "user__date_joined",
        )
