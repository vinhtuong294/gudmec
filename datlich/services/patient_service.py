from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from ..serializers import *
from datlich.models import Patient

class PatientService:

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

        patients = Patient.objects.all()
        return patients

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
        try:
            patient = Patient.objects.select_related('user').get(user_id=user_id)
            return {
                "id": patient.id,
                "name": patient.user.fullname,
                "nhommau": patient.nhommau,
                "cannang": patient.cannang,
                "chieucao": patient.chieucao,
                "benhnen": patient.benhnen,
                "birthday": patient.user.birthday,
                "gender": patient.user.gender,
            }
        except ObjectDoesNotExist:
            raise RuntimeError("Patient not found")

    def get_patient_schedule_id(self, id):
        # Lấy schedule có id tương ứng
        schedule = Schedule.objects.select_related('patient', 'patient__user').get(id=id)
        # Lọc các MedicalRecord theo patient_id của schedule và sắp xếp giảm dần theo id
        return {
            "id": schedule.patient.id,
            "name": schedule.patient.user.fullname,
            "birthday": schedule.patient.user.birthday,
            "gender": schedule.patient.user.gender,
        }
