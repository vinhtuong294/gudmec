from apscheduler.schedulers.background import BackgroundScheduler
from datetime import date, datetime,timedelta
from datlich.models import Doctor, Shift, Schedule
from django.core.mail import send_mail

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
    
def notify_schedules():
    today = datetime.now().date()

    # Lấy danh sách lịch hẹn cần thông báo
    schedules = Schedule.objects.select_related(
        'patient', 'patient__user', 'doctor', 'doctor__user', 'shift'
    ).filter(
        date=today,
        is_ready=False,  # Chưa sẵn sàng
        shift__time_start__gt=(datetime.now() - timedelta(hours=3)).time(),  # Sớm hơn 3 giờ
        notified=False,
    ).exclude(
        patient__isnull=True  # Bệnh nhân không được null
    )

    # Gửi email cho từng lịch hẹn
    for schedule in schedules:
        user_email = schedule.patient.user.email
        doctor_name = schedule.doctor.user.fullname
        schedule_date = schedule.date.strftime('%d-%m-%Y')
        schedule_time = schedule.shift.time_start.strftime('%H:%M')
        send_mail(
            subject="Bạn có lịch đặt khám hôm nay!",
            message=f"Bạn có cuộc hẹn với Bác sĩ {doctor_name} vào ngày {schedule_date} lúc {schedule_time}. Mọi thắc mắc vui lòng liên hệ hotline: 0397521031",
            from_email="tuong7749@gmail.com",
            recipient_list=[user_email],
        )
        schedule.notified = True
        schedule.save()
    print("Notify schedules executed successfully.")

# Chức năng 2: Cập nhật is_ready cho các schedule quá hạn
def update_schedule_ready_status():
    now = datetime.now()
    today = date.today()
    
    schedules = Schedule.objects.select_related('patient').all()
    overdue_schedules = schedules.filter(
        date__lte=today,
        shift__time_start__lt=now.time()
    )
    for schedule in overdue_schedules:
        if schedule.patient and schedule.state != 1:
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
    
    scheduler.add_job(notify_schedules, 'interval', minutes=5)
    
    scheduler.add_job(auto_delete_schedule, 'cron', hour=0, minute=0)
    
    scheduler.start()
    print("Scheduler started: Tasks are running.")
