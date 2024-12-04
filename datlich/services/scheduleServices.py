from datetime import date, datetime
from django.db.models import Sum
from ..models import *
from ..serializers import *


class ScheduleService:

    def get_one_schedule(self, id):
        return Schedule.objects.get(id=id)

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

    def get_schedules_by_doctor(self,user_id, doctor_id, target_date):
        schedules = Schedule.objects.select_related('shift','patient__user').all()
        schedules =  schedules.filter(doctor_id=doctor_id)
        if target_date:
            schedules= schedules.filter(date=target_date)
        else:
            today = datetime.today().date()
            schedules = schedules.filter(date=today)
        return [{
            "id": schedule.id,
            "date": schedule.date,
            "time_start": schedule.shift.time_start,
            "time_end": schedule.shift.time_end,
            "is_ready": schedule.is_ready,
            "is_my_schedule": schedule.patient.user.id == user_id if schedule.patient else False
        }for schedule in schedules
        ] 
    def get_doctor_schedules(self,user_id, target_date):
        schedules = Schedule.objects.select_related('shift', 'patient__user').all()
        doctor_id = Doctor.objects.get(user_id=user_id).id
        print(target_date)
        # Lọc schedules theo điều kiện và sắp xếp
        schedules = schedules.filter(
            doctor_id=doctor_id,
            patient__isnull=False  # Điều kiện patient không phải Null
        ).order_by('-id')
        if target_date:
            schedules= schedules.filter(date=target_date)
        print(schedules)
        return [{
            "id": schedule.id,
            "date": schedule.date,
            "time_start": schedule.shift.time_start,
            "time_end": schedule.shift.time_end,
            "is_ready": schedule.is_ready,
            "state": schedule.state,
            "patient_name": schedule.patient.user.fullname,
        }for schedule in schedules
        ]     
    
    def booking(self,user_id, id):
        schedule = Schedule.objects.select_related('patient').get(id=id)
        patient =  Patient.objects.get(user_id =user_id )

        if schedule.patient:
            schedule.is_ready = True
            schedule.patient = None
            schedule.save()
        else:
            schedule.is_ready = False
            schedule.patient = patient
            schedule.save()

        return schedule

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
