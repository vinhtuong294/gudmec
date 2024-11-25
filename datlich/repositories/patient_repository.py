from django.db import models
from ..models import *

class PatientManager(models.Manager):
    def find_by_user_id(self, user_id):
        """Truy vấn bệnh nhân qua user_id"""
        return self.filter(user_id=user_id)

    def find_by_id(self, patient_id):
        """Truy vấn bệnh nhân qua ID"""
        return self.filter(id=patient_id).first()

class PatientRepository(Patient):
    # Sử dụng manager tuỳ chỉnh
    objects = PatientManager()

    class Meta:
        proxy = True  # Đây chỉ là proxy cho model Patient, không cần tạo bảng riêng
