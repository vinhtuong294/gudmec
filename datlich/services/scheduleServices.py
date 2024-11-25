from datetime import date
from django.db.models import Sum
from ..models import *
from ..serializers import *
from .MedicalRecordServices import MedicalRecordService


class ScheduleService:
    def __init__(self):
        self.medical_record_service = MedicalRecordService()

    def create_schedule(self, data):
        """
        Tạo lịch hẹn mới từ dữ liệu cung cấp.
        """
        schedule = Schedule(
            date=data["date"],
            state=data["state"],
            doctor=Doctor.objects.get(id=data["doctor_id"]),
            patient=Patient.objects.get(id=data["patient_id"]),
            shift=Shift.objects.get(id=data["shift_id"]),
        )
        schedule.save()
        self.medical_record_service.create_medical_record(schedule)

    def get_all_schedules(self):
        """
        Lấy danh sách tất cả lịch hẹn.
        """
        schedules = Schedule.objects.all()
        return ScheduleResponseSerializer(schedules, many=True).data

    def get_all_schedule_info(self):
        """
        Lấy thông tin chi tiết của tất cả lịch hẹn.
        """
        schedules = Schedule.objects.all()
        return ScheduleResponseSerializer(schedules, many=True).data

    def get_schedule_info_by_date(self, target_date):
        """
        Lấy thông tin lịch hẹn theo ngày cụ thể.
        """
        schedules = Schedule.objects.filter(date=target_date)
        return ScheduleResponseSerializer(schedules, many=True).data

    def get_schedules_by_date(self, target_date):
        """
        Lấy danh sách lịch hẹn theo ngày cụ thể.
        """
        return Schedule.objects.filter(date=target_date)

    def get_revenue_of_day(self, target_date):
        """
        Tính tổng doanh thu trong một ngày cụ thể.
        """
        schedules = self.get_schedules_by_date(target_date)
        return schedules.aggregate(total=Sum("doctor__service_prices"))["total"] or 0

    def get_schedules_by_month_and_year(self, month, year):
        """
        Lấy danh sách lịch hẹn theo tháng và năm.
        """
        return Schedule.objects.filter(date__month=month, date__year=year)

    def get_revenue_of_month(self, month, year):
        """
        Tính tổng doanh thu trong một tháng cụ thể.
        """
        schedules = self.get_schedules_by_month_and_year(month, year)
        return schedules.aggregate(total=Sum("doctor__service_prices"))["total"] or 0
