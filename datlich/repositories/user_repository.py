from django.db import models
from ..models import UserModel

class UserManager(models.Manager):
    def find_by_user_name(self, user_name):
        """Tìm user theo user_name và tham chiếu tới role"""
        return self.filter(user_name=user_name).select_related('role').first()

    def find_by_user_name_containing(self, user_name):
        """Tìm danh sách users có user_name chứa chuỗi"""
        return self.filter(user_name__icontains=user_name)

    def find_by_email_containing(self, email):
        """Tìm danh sách users có email chứa chuỗi"""
        return self.filter(email__icontains=email)

    def find_by_telephone_containing(self, phone):
        """Tìm danh sách users có phone chứa chuỗi"""
        return self.filter(telephone__icontains=phone)

    def find_by_fullname_containing(self, full_name):
        """Tìm danh sách users có fullname chứa chuỗi"""
        return self.filter(fullname__icontains=full_name)

    def delete_by_id(self, user_id):
        """Xóa user theo id"""
        self.filter(id=user_id).delete()


class UserRepository(UserModel):
    # Sử dụng manager tùy chỉnh
    objects = UserManager()

    class Meta:
        proxy = True  # Sử dụng proxy model, không tạo bảng riêng
