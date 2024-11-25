from django.db import models
from ..models import Department

class DepartmentRepository(models.Manager):
    def find_by_id(self, department_id):
        """Tìm department theo id"""
        return self.filter(id=department_id).first()

    def find_all(self):
        """Lấy tất cả các department"""
        return self.all()

# Department Model có thể sử dụng repository này
class Department(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=255)

    objects = DepartmentRepository()  # Sử dụng custom repository

    def __str__(self):
        return self.name
