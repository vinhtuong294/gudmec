from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
import os




# class UserModelManager(BaseUserManager):
#     def create_user(self, username, password=None, **extra_fields):
#         """Tạo và trả về người dùng với mật khẩu mã hóa"""
#         if not username:
#             raise ValueError('The Username field must be set')
#         user = self.model(username=username, **extra_fields)
#         user.set_password(password)  # Mã hóa mật khẩu trước khi lưu
#         user.save(using=self._db)
#         return user

#     def create_superuser(self, username, password=None, **extra_fields):
#         """Tạo và trả về người dùng superuser"""
#         extra_fields.setdefault('is_staff', True)
#         extra_fields.setdefault('is_superuser', True)
#         return self.create_user(username, password, **extra_fields)


# class UserModel(AbstractBaseUser, PermissionsMixin):
#     username = models.CharField(max_length=150, unique=True)
#     password = models.CharField(max_length=128)
#     enabled = models.BooleanField(default=True)
#     fullname = models.CharField(max_length=255)
#     gender = models.BooleanField()
#     birthday = models.DateField()
#     email = models.EmailField(unique=True)
#     telephone = models.CharField(max_length=15, unique=True)
#     role = models.ForeignKey('Role', on_delete=models.CASCADE, related_name='users')

#     USERNAME_FIELD = 'username'  # Trường dùng làm tên đăng nhập
#     REQUIRED_FIELDS = ['email', 'fullname', 'birthday', 'telephone']

#     objects = UserModelManager()

#     def __str__(self):
#         return self.fullname

# Enum classes
class ERole(models.TextChoices):
    PATIENT = 'PATIENT', _('Patient')
    DOCTOR = 'DOCTOR', _('Doctor')
    ADMIN = 'ADMIN', _('Admin')

class Status(models.TextChoices):
    APPROVED = 'APPROVED', _('Approved')
    PENDING = 'PENDING', _('Pending')
    REJECTED = 'REJECTED', _('Rejected')

class ScheduleState(models.IntegerChoices):
    WAITING = 0, _('Đang chờ')
    DONE = 1, _('Đã hoàn thành')
    MISSED = 2, _('Đã bỏ lỡ')
# Main Models
class Role(models.Model):
    name = models.CharField(max_length=20, choices=ERole.choices)

    def __str__(self):
        return self.get_name_display()

class UserModelManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError('The Username field must be set')
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', Role.objects.get(id=1))
        return self.create_user(username, password, **extra_fields)

class UserModel(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128)
    enabled = models.BooleanField(default=True)
    fullname = models.CharField(max_length=255)
    gender = models.BooleanField()
    birthday = models.DateField()
    email = models.EmailField(unique=True)
    telephone = models.CharField(max_length=15, unique=True)
    role = models.ForeignKey('Role', on_delete=models.CASCADE, related_name='users')

    # Thêm hai trường này
    is_staff = models.BooleanField(default=False)  # Cho phép truy cập admin
    is_superuser = models.BooleanField(default=False)  # Quyền quản trị viên

    USERNAME_FIELD = 'username'  # Trường dùng làm tên đăng nhập
    REQUIRED_FIELDS = ['email', 'fullname', 'birthday', 'telephone','is_staff', 'is_superuser','gender','role' ]

    objects = UserModelManager()

    def __str__(self):
        return self.fullname


    def check_password(self, raw_password):
        # So sánh mật khẩu được mã hóa với mật khẩu nhập vào
        return check_password(raw_password, self.password)

class Department(models.Model): #Khoa
    name_department = models.TextField()
    description_department = models.TextField()
    location = models.TextField()

    def __str__(self):
        return self.name_department

class Doctor(models.Model): #Bác sĩ
    position = models.CharField(max_length=100)
    description = models.TextField()
    room_address = models.CharField(max_length=255)
    service_prices = models.IntegerField()
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='list_doctors')
    user = models.OneToOneField(UserModel, on_delete=models.CASCADE, related_name='doctor')
    avatar = models.TextField(blank=None, null=True)
    average_rate = models.FloatField(default=0)

    def update_average_rate(self):
        rates = self.rates.all()
        self.average_rate = rates.aggregate(models.Avg('rate'))['rate__avg'] or 0
        self.save()

    def __str__(self):
        return self.user.fullname
    
class Rate(models.Model):
    content = models.TextField()
    rate = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='rates')
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='user_rates')
    date = models.DateField(auto_now_add=True, null=True)

class Patient(models.Model): #bệnh nhân
    name = models.CharField(max_length=255)
    user = models.OneToOneField(UserModel, on_delete=models.CASCADE, related_name='patient')
    nhommau = models.CharField(max_length=255, blank=None)
    cannang = models.FloatField(blank=None)
    chieucao = models.FloatField(blank=None)
    benhnen = models.TextField(blank=None)

    def __str__(self):
        return self.name

class Shift(models.Model): #ca khám
    time_start = models.TimeField()
    time_end = models.TimeField()

    def __str__(self):
        return f"{self.time_start} - {self.time_end}"

class Schedule(models.Model): #Lịch hẹn khám
    date = models.DateField()
    state = models.IntegerField(choices=ScheduleState.choices)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='schedules')
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='schedules',blank=None, null=True)
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE, related_name='schedules',blank=None, null=True)
    is_ready = models.BooleanField(default=True)
    

class MedicalRecord(models.Model): #Bệnh án
    schedule = models.OneToOneField(Schedule, on_delete=models.CASCADE, related_name='medical_record')
    diagnosis = models.TextField()
    description = models.TextField(blank=None, null=True)
    medical_results =models.TextField(blank=None, null=True)

    def __str__(self):
        return f"Medical Record for {self.schedule.patient.name} on {self.schedule.date}"

class Article(models.Model):
    title = models.TextField()
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=Status.choices)
    author = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='articles')
    image = models.ImageField(upload_to='articles/images/', null=True, blank=True)  # Trường lưu ảnh

    def image_url(self):
        if self.image:
            return os.path.join(settings.MEDIA_URL, str(self.image))
        return None

