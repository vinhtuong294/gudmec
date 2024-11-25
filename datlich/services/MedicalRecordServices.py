from datetime import date as current_date
from django.db.models import Q
from ..models import MedicalRecord, Schedule
from ..serializers import *
from .exceptions import NotFoundException


class MedicalRecordService:
    def create_medical_record(self, schedule):
        """
        Tạo hồ sơ y tế dựa trên lịch hẹn.
        """
        medical_record = MedicalRecord(schedule=schedule)
        medical_record.save()

    def handle_filter_medical_record(self, doctor_id, date="", patient_name="", today=False):
        """
        Lọc hồ sơ y tế dựa trên các tham số đầu vào.
        """
        query = Q(schedule__doctor_id=doctor_id)

        if today:
            query &= Q(schedule__date=current_date.today())

        if date:
            query &= Q(schedule__date=date)

        if patient_name:
            query &= Q(schedule__patient__user__fullname__icontains=patient_name)

        return MedicalRecord.objects.filter(query)

    def map_data_medical_record_response(self, medical_records):
        """
        Chuyển đổi danh sách MedicalRecord thành định dạng response.
        """
        return MedicalRecordResponseSerializer(medical_records, many=True).data

    def update_medical_record(self, data):
        """
        Cập nhật hồ sơ y tế.
        """
        try:
            medical_record = MedicalRecord.objects.get(id=data["id"])
        except MedicalRecord.DoesNotExist:
            raise NotFoundException("MedicalRecord not found")

        medical_record.diagnosis = data["diagnosis"]
        medical_record.save()
