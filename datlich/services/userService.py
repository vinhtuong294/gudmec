from datlich.models import UserModel
from datetime import datetime, timedelta
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError

class UserService:
    def get_all_users(self):
        return UserModel.objects.all()
    def get_one_user(self,id):
        user = UserModel.objects.get(id=id)
        return {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'fullname': user.fullname,
            'phone': user.telephone,
            'birthday': user.birthday,
            'gender': user.gender,
            'password': user.password,
            "image": user.image,
        }
    def update_user(user_id, phone,fullname,gender,birthday, avatar):
        try:
            # Lấy người dùng từ cơ sở dữ liệu
            user = UserModel.objects.get(id=user_id)
            user.fullname = fullname
            user.telephone = phone
            user.gender = gender
            user.birthday = birthday
            if avatar:
                user.image = avatar

            # Lưu các thay đổi vào cơ sở dữ liệu
            user.save()

            return user
        except Exception as e:
            raise ValueError(f"Failed to update user: {str(e)}")
    def change_password(self, user_id, old_password, new_password):
        try:
            print(old_password,new_password)
            # Lấy người dùng từ cơ sở dữ liệu
            user = UserModel.objects.get(id=user_id)
            
            # Kiểm tra mật khẩu cũ
            if not user.check_password(old_password):
                raise ValidationError("Old password is incorrect.")
            
            # Cập nhật mật khẩu mới
            user.password = make_password(new_password)
            user.save()

            return {"message": "Password changed successfully."}
        
        except Exception as e:
            raise ValueError(f"An error occurred while changing the password: {str(e)}")