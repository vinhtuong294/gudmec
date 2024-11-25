from .models import *
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ['id', 'fullname', 'gender', 'birthday', 'telephone', 'role']


class RegisterRequestSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True)
    email = serializers.EmailField()
    telephone = serializers.CharField(max_length=15)
    fullname = serializers.CharField(max_length=255)
    birthday = serializers.DateField()
    gender = serializers.BooleanField()
    role = serializers.ChoiceField(choices=ERole.choices, required=False)


class AuthenticationRequestSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=255)
    password = serializers.CharField()


class AuthenticationResponseSerializer(serializers.Serializer):
    token = serializers.CharField()


class UserResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ['id', 'username', 'fullname', 'email', 'phone', 'gender', 'birthday', 'enabled', 'role']

    role = serializers.StringRelatedField()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['username'] = user.username
        token['email'] = user.email
        if hasattr(user, 'role'):  # Nếu có trường role
            token['role'] = user.role

        return token


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'name', 'description', 'location']


class ShiftSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shift
        fields = '__all__'


class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = ['id', 'user', 'service_prices', 'description', 'department']


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ['id', 'user']


class ScheduleSerializer(serializers.ModelSerializer):
    doctor = DoctorSerializer()
    patient = PatientSerializer()
    shift = ShiftSerializer()

    class Meta:
        model = Schedule
        fields = ['id', 'date', 'state', 'doctor', 'patient', 'shift']


class ShiftResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shift
        fields = ["id", "time_start", "time_end"]


class MedicalRecordResponseSerializer(serializers.ModelSerializer):
    shift = ShiftResponseSerializer(source="schedule.shift")
    patient_name = serializers.CharField(source="schedule.patient.user.fullname")
    date = serializers.DateField(source="schedule.date")
    schedule_id = serializers.IntegerField(source="schedule.id")

    class Meta:
        model = MedicalRecord
        fields = [
            "id",
            "patient_name",
            "date",
            "shift",
            "schedule_id",
            "diagnosis",
        ]


class DoctorInfoResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = "__all__"


class ScheduleResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = ['id', 'date', 'state', 'doctor', 'patient', 'shift']

    doctor = DoctorSerializer()
    patient = PatientSerializer()
    shift = ShiftResponseSerializer()


class BookingModelSerializer(serializers.Serializer):
    day = serializers.DateField()
    list_shift = serializers.ListField(
        child=serializers.PrimaryKeyRelatedField(queryset=Shift.objects.all())
    )


# Article Response
class ArticleResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ['id', 'title', 'content', 'created_at', 'updated_at', 'status', 'author']

    author = serializers.StringRelatedField()


# Department Response
class DepartmentResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'name_department', 'description_department', 'location']


# Doctor Response
class DoctorResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = ['id', 'position', 'description', 'room_address', 'service_prices', 'department', 'user']

    department = DepartmentResponseSerializer()
    user = serializers.StringRelatedField()


# Patient Response
class PatientResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ['id', 'name', 'nhommau', 'cannang', 'chieucao', 'benhnen', 'user']

    user = serializers.StringRelatedField()


# Schedule Response
class ScheduleResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = ['id', 'date', 'state', 'doctor', 'patient', 'shift']

    doctor = DoctorResponseSerializer()
    patient = PatientResponseSerializer()
    shift = ShiftResponseSerializer()


# Medical Record Response
class MedicalRecordResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalRecord
        fields = ['id', 'schedule', 'diagnosis']

    schedule = ScheduleResponseSerializer()


# Register Response
class RegisterResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ['id', 'username', 'fullname', 'email', 'phone', 'gender', 'birthday', 'role']

    role = serializers.StringRelatedField()


# Doctor Details Response
class DoctorDetailsResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = ['id', 'position', 'description', 'room_address', 'service_prices', 'department', 'user']

    department = DepartmentResponseSerializer()
    user = UserResponseSerializer()


# Schedule Details Response
class ScheduleDetailsResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = ['id', 'date', 'state', 'doctor', 'patient', 'shift']

    doctor = DoctorResponseSerializer()
    patient = PatientResponseSerializer()
    shift = ShiftResponseSerializer()


# Medical Record Details Response
class MedicalRecordDetailsResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalRecord
        fields = ['id', 'schedule', 'diagnosis']

    schedule = ScheduleResponseSerializer()


# Article Request
class ArticleRequestSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    content = serializers.CharField()
    user_id = serializers.IntegerField()

    def create_article(self, validated_data):
        user = UserModel.objects.get(id=validated_data['user_id'])
        return Article.objects.create(
            title=validated_data['title'],
            content=validated_data['content'],
            author=user
        )


# Department Request
class DepartmentRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['name_department', 'description_department', 'location']


# Doctor Request
class DoctorRequestSerializer(serializers.Serializer):
    position = serializers.CharField(max_length=100)
    description = serializers.CharField()
    room_address = serializers.CharField(max_length=255)
    service_prices = serializers.IntegerField()
    department_id = serializers.IntegerField()
    user_id = serializers.IntegerField()


# Medical Record Request
class MedicalRecordRequestSerializer(serializers.Serializer):
    schedule_id = serializers.IntegerField()
    diagnosis = serializers.CharField(max_length=255)


# Password Check Request
class PasswordCheckRequestSerializer(serializers.Serializer):
    input_password = serializers.CharField()
    encoded_password = serializers.CharField()


# Patient Update Request
class PatientUpdateRequestSerializer(serializers.Serializer):
    nhommau = serializers.CharField(max_length=255)
    cannang = serializers.FloatField()
    chieucao = serializers.FloatField()
    benhnen = serializers.CharField(max_length=255)


# Register Request
class RegisterRequestSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=255)
    fullname = serializers.CharField(max_length=255)
    gender = serializers.BooleanField()
    birthday = serializers.DateField()
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=20)
    role = serializers.CharField(max_length=20)


# Schedule Request
class ScheduleRequestSerializer(serializers.Serializer):
    date = serializers.DateField()
    state = serializers.IntegerField()
    doctor_id = serializers.IntegerField()
    patient_id = serializers.IntegerField()
    shift_id = serializers.IntegerField()


# UserDTO Request
class UserDTORequestSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=255)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=20)
    fullname = serializers.CharField(max_length=255)
    gender = serializers.BooleanField()
    birthday = serializers.DateField()
    enabled = serializers.BooleanField()
    role = serializers.CharField(max_length=50)

    @staticmethod
    def map_to_user_dto(user):
        return UserDTORequestSerializer(user).data

    @staticmethod
    def map_to_user_model(user_dto):
        return UserModel.objects.create(
            username=user_dto['username'],
            password=user_dto['password'],
            email=user_dto['email'],
            telephone=user_dto['phone'],
            fullname=user_dto['fullname'],
            gender=user_dto['gender'],
            birthday=user_dto['birthday'],
            enabled=user_dto['enabled'],
            role=UserDTORequestSerializer.string_to_role(user_dto['role'])
        )

    @staticmethod
    def string_to_role(str_role):
        from .models import ERole, Role
        if str_role == "ADMIN":
            return Role(name=ERole.ADMIN)
        elif str_role == "DOCTOR":
            return Role(name=ERole.DOCTOR)
        else:
            return Role(name=ERole.PATIENT)
