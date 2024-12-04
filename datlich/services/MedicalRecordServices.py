from datlich.models import MedicalRecord, Schedule
from datetime import datetime, timedelta

class MedicalRecordService:
    def get_all_record(self):
        return MedicalRecord.objects.all()
    def get_record_patient(self, id):
        # Lấy schedule có id tương ứng
        schedule = Schedule.objects.select_related('patient').get(id=id)
        # Lọc các MedicalRecord theo patient_id của schedule và sắp xếp giảm dần theo id
        records = MedicalRecord.objects.select_related('schedule', 'schedule__patient').filter(
            schedule__patient_id=schedule.patient.id
        ).order_by('-id')
        return [
            {
                "id": record.id,
                "description": record.description,
                "diagnosis": record.diagnosis,
                "medical_results": record.medical_results,
                "date": record.schedule.date,
            }
            for record in records
        ]
    def create_medical_record(schedule_id, data):
    # Lấy đối tượng Schedule, nếu không tìm thấy thì trả về lỗi 404
        schedule = Schedule.objects.get(id=schedule_id)
        # Kiểm tra xem Schedule này đã có MedicalRecord chưa
        if hasattr(schedule, 'medical_record'):
            raise ValueError(f"Schedule with ID {schedule_id} already has an associated medical record.")

        # Tạo bản ghi MedicalRecord mới
        medical_record = MedicalRecord.objects.create(
            schedule=schedule,
            diagnosis=data.get('diagnosis'),
            description=data.get('description'),
            medical_results=data.get('medical_results')
        )
        schedule.state = 1
        schedule.save()
        print(medical_record)
        return medical_record