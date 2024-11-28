from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from ..repositories.patient_repository import PatientRepository
from ..repositories.user_repository import UserRepository
from ..serializers import *


class PatientService:
    def __init__(self):
        self.patient_repository = PatientRepository()
        self.user_repository = UserRepository()

    def create_new_patient(user):
    # Khởi tạo một đối tượng Patient mới cho người dùng
        Patient.objects.create(
            name=user.fullname,
            user=user,
            nhommau='O',  # Giá trị mặc định hoặc tùy chỉnh dựa trên yêu cầu của ứng dụng
            cannang=0.0,  # Giá trị mặc định hoặc tùy chỉnh
            chieucao=0.0,  # Giá trị mặc định hoặc tùy chỉnh
            benhnen='N/A'  # Giá trị mặc định hoặc tùy chỉnh
        )

    def get_all_patients(self):
        """
        Lấy tất cả bệnh nhân và trả về dưới dạng response.
        """
        patients = self.patient_repository.find_all()
        return [PatientResponseSerializer.map_to_response(patient) for patient in patients]

    @transaction.atomic
    def update_patient_info(self, user_id, nhommau, cannang, chieucao, benhnen):
        """
        Cập nhật thông tin bệnh nhân.
        """
        try:
            # Tìm user tương ứng
            user = self.user_repository.find_by_id(user_id)

            # Lấy bệnh nhân liên kết với user
            patient = user.patient
            if not patient:
                raise RuntimeError("Patient not found")

            # Cập nhật thông tin bệnh nhân
            patient.nhommau = nhommau
            patient.cannang = cannang
            patient.chieucao = chieucao
            patient.benhnen = benhnen

            patient.save()
        except ObjectDoesNotExist:
            raise RuntimeError("User not found")

    def get_patient_by_user_id(self, user_id):
        """
        Lấy bệnh nhân theo user_id.
        """
        try:
            patient = self.patient_repository.find_by_user_id(user_id)
            return patient
        except ObjectDoesNotExist:
            raise RuntimeError("Patient not found")

