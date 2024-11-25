from django.db import models
from ..models import Schedule

class ScheduleRepository(models.Manager):
    def find_all_by_date(self, date):
        """Tìm tất cả các lịch trình theo ngày"""
        return self.filter(date=date)

    def find_all_by_month_and_year(self, month, year):
        """Tìm tất cả các lịch trình theo tháng và năm"""
        return self.filter(date__month=month, date__year=year)

    def find_all(self):
        """Lấy tất cả các lịch trình"""
        return self.all()

# Schedule Model sử dụng repository này
class Schedule(models.Model):
    date = models.DateField()
    # Các trường khác như doctor, patient, shift, etc.

    objects = ScheduleRepository()  # Sử dụng custom repository

    def __str__(self):
        return f"Schedule for {self.date}"
