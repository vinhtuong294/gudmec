from apscheduler.schedulers.background import BackgroundScheduler
from datetime import date, datetime,timedelta
from datlich.models import Doctor, Shift, Schedule

# Chức năng 1: Tạo lịch khám hàng ngày
def generate_daily_schedules():
    doctors = Doctor.objects.all()
    shifts = Shift.objects.all()
    today = date.today() + timedelta(days=7)
    
    for doctor in doctors:
        for shift in shifts:
            Schedule.objects.get_or_create(
                date=today,
                doctor=doctor,
                shift=shift,
                defaults={
                    'state': 0,  # Giá trị mặc định
                    'patient': None,  # Chưa có bệnh nhân
                    'is_ready': True
                }
            )
    print("Schedules created for date:", today)

# Chức năng 2: Cập nhật is_ready cho các schedule quá hạn
def update_schedule_ready_status():
    now = datetime.now()
    today = date.today()
    
    schedules = Schedule.objects.select_related('patient').all()
    overdue_schedules = schedules.filter(
        date__lte=today,
        shift__time_start__lt=now.time(),
        is_ready=True
    )
    for schedule in overdue_schedules:
        if schedule.patient:
            schedule.state = 2
            schedule.save()
        else:
            schedule.save()
    overdue_schedules.update(is_ready=False)
    print(f"Updated {overdue_schedules.count()} overdue schedules to is_ready=False at {now}")


def auto_delete_schedule():
    today = date.today()
    schedules = Schedule.objects.select_related('patient').all()
    schedules = schedules.filter(date__lt=today - timedelta(days=2))
    for schedule in schedules:
        if schedule.patient:
            schedule.save()
        else:
            schedule.delete()
    print("Schedules auto delete successfully")

# Hàm khởi chạy Scheduler
def start_scheduler():
    scheduler = BackgroundScheduler()
    
    # Lịch trình chạy: Tạo schedule mới lúc 0h mỗi ngày
    scheduler.add_job(generate_daily_schedules, 'cron', hour=0, minute=0)
    
    # Lịch trình chạy: Cập nhật trạng thái schedule mỗi 1 phút
    scheduler.add_job(update_schedule_ready_status, 'interval', minutes=5)
    
    scheduler.add_job(auto_delete_schedule, 'interval', minutes=1)
    
    scheduler.start()
    print("Scheduler started: Tasks are running.")
