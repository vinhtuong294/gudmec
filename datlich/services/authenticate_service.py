from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.conf import settings
import jwt

User = get_user_model()
SECRET_KEY = settings.SECRET_KEY
class AuthenticateService:

    def get_user_from_token(token):
        try:
            # Giải mã token, kiểm tra tính hợp lệ
            decoded_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

            # Lấy thông tin người dùng từ token (giả định token chứa user_id)
            user_id = decoded_token.get("user_id")

            # Truy vấn đối tượng người dùng từ cơ sở dữ liệu
            user = User.objects.get(id=user_id)

            return user  # Trả về đối tượng người dùng nếu token hợp lệ

        except jwt.ExpiredSignatureError:
            # Token hết hạn
            print("Token has expired")
            return None
        except jwt.InvalidTokenError:
            # Token không hợp lệ
            print("Invalid token")
            return None
        except User.DoesNotExist:
            # Người dùng không tồn tại
            print("User does not exist")
            return None

    def get_user_role(self, user):
        if user.groups.filter(name='DOCTOR').exists():
            return 'DOCTOR'
        elif user.groups.filter(name='PATIENT').exists():
            return 'PATIENT'
        elif user.is_superuser:
            return 'ADMIN'
        return 'USER'
