from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.hashers import make_password
from .models import *
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from .services import patient_service, doctor_service  # Giả định có các service tương tự
from .repositories import role_repository, user_repository  # Giả định có các repository tương tự
from .serializers import *
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer
from .services import (department_service, patient_service, patient_service,
                       exceptions, MedicalRecordServices,scheduleServices,doctor_service)
from .services.authenticate_service import AuthenticateService
from .services.department_service import DepartmentService
from .services.MedicalRecordServices import MedicalRecordService
from .services.scheduleServices import ScheduleService
from .services.doctor_service  import DoctorService
import json

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class UserViewSet(viewsets.ModelViewSet):

    queryset = UserModel.objects.all()
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        print("Received data: %s", request.data)  # Log dữ liệu nhận được
        return super().create(request, *args, **kwargs)
    # permission_classes = [IsAuthenticated]


def password_reset(request):
    return render(request, 'password_reset/password_reset.html')

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return render(request, 'register/register.html')

    def post(self, request):
        serializer = RegisterRequestSerializer(data=request.data)
        print(serializer)
        serializer.is_valid(raise_exception=True)

        # Lấy dữ liệu từ serializer
        role_name = serializer.validated_data.get("role")

        print(role_name)

        # Kiểm tra vai trò và gán giá trị tương ứng
        try:
            if role_name is None:
                role = Role.objects.get(name=ERole.PATIENT)
            else:
                role = Role.objects.get(name=role_name)
        except Role.DoesNotExist:
            return Response({"error": "Role not found."}, status=status.HTTP_400_BAD_REQUEST)

        # Tạo người dùng mới
        user = UserModel.objects.create(
            username=serializer.validated_data['username'],
            password=make_password(serializer.validated_data['password']),
            email=serializer.validated_data['email'],
            telephone=serializer.validated_data['telephone'],
            fullname=serializer.validated_data['fullname'],
            birthday=serializer.validated_data['birthday'],
            gender=serializer.validated_data['gender'],
            enabled=True,
            role=role,
        )

        # Lưu người dùng và xử lý tạo đối tượng phụ thuộc vai trò
        user_repository.UserRepository.save(user)

        if role.name == ERole.PATIENT:
            patient_service.PatientService.create_new_patient(user)
        elif role.name == ERole.DOCTOR:
            doctor_service.DoctorService.create_new_doctor(user)

        # Trả về thông tin xác thực hoặc dữ liệu người dùng
        return Response({
            "username": user.username,
            "role": role.name,
            "message": "User registered successfully."
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return render(request, 'login/login.html')

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        try:
            # Lấy người dùng từ cơ sở dữ liệu
            user = UserModel.objects.get(username=username)
        except UserModel.DoesNotExist:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

        # Xác thực mật khẩu
        if user.check_password(password):
            # Sử dụng CustomTokenObtainPairSerializer để tạo token có payload tùy chỉnh
            refresh = RefreshToken.for_user(user)
            # Sử dụng `access_token` từ refresh token có thông tin tùy chỉnh
            access_token = refresh.access_token

            # Thêm thông tin tùy chỉnh vào access token (nếu cần thiết)
            access_token['username'] = user.username
            access_token['email'] = user.email
            if hasattr(user, 'role'):
                access_token['role'] = user.role_id

            # Trả về token cho client
            return Response({
                'access': str(access_token),
                'refresh': str(refresh),
            }, status=status.HTTP_200_OK)

        # Trả về thông báo lỗi nếu thông tin đăng nhập không chính xác
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)



# def home_logged(request):
#     return render(request, 'homepage/homeComponent/homepage.html')


# def admin_homepage(request):
#     return render(request, 'homepage/homeComponent/homepage.html')

class home_page(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        # Authenticate user from Bearer token
        authenticate_service = AuthenticateService
        department_service = DepartmentService

        token = request.COOKIES.get('authToken')

        print(token)

        user = authenticate_service.get_user_from_token(token)

        # Set the default view and file for rendering
        context = {
            "view": "homepage/homeComponent/homepage.html",
            "file": "homepage",
            "listDepartmentResponse": department_service.get_all_departments(self),
        }

        # Check if user is authenticated and their role
        if user is None or str(user.role) == "Admin":
            context["nav"] = "partials/nav.html"
            context["navState"] = "nav"
        else:
            # Different nav based on user role
            if str(user.role) == "Doctor":
                context["nav"] = "partials/navDoctorLogged.html"
                context["navState"] = "navDoctorLogged"
            elif str(user.role) == "Patient":
                context["nav"] = "partials/navLogged.html"
                context["navState"] = "navLogged"
            context["user"] = user

        print(context)

        return render(request, "homepage/index.html", context)


class LogoutView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        # Xóa cookie chứa token
        response = JsonResponse({'message': 'Successfully logged out.'})
        response.delete_cookie('authToken')  # Xóa cookie authToken
        return response


def search_result(request):
    return render(request, 'homepage/homeComponent/search_result.html')

# def bookAppointment(request, doctor_id):
#     doctor = get_object_or_404(Doctor, id=doctor_id)  # Lấy thông tin bác sĩ
#     booking_list = Schedule.objects.filter(Doctor=doctor)  # Lấy danh sách lịch trống
#     return render(request, 'homepage/homeComponent/bookAppointment.html', {
#         'doctor': doctor,
#         'booking_list': booking_list,
#         'user': request.user,
#     })



def medicalRecordInforPageComponent(request):
    # Lấy danh sách hồ sơ bệnh án từ cơ sở dữ liệu
    list_medical_records = MedicalRecord.objects.all()

    # Truyền dữ liệu vào template
    context = {
        'list_medical_records': list_medical_records}
    return render(request, 'homepage/homeComponent/medicalRecordInforPageComponent.html', context)

def prosess_page(request):
    process_steps = [
        {'title': 'Đăng ký khám, xuất trình giấy tờ tùy thân và BHYT tại quầy Lễ tân',
         'description': 'Khách hàng xuất trình giấy tờ tùy thân và thẻ BHYT tại quầy lễ tân. Nhân viên bộ phận Lễ tân đối chiếu thông tin thẻ BHYT và giấy tờ tùy thân, tiến hành đăng ký lịch khám với bác sĩ theo yêu cầu của khách hàng.'},
        {'title': 'Thực hiện kiểm tra sinh hiệu tại quầy Điều dưỡng ở phòng khám',
         'description': 'Khách hàng theo số thứ tự khám bệnh đã lấy từ quầy Lễ tân đến quầy Điều dưỡng phòng khám để được kiểm tra sinh hiệu.'},
        {'title': 'Gặp bác sĩ khám và chẩn đoán',
         'description': 'Các bác sĩ, chuyên gia đầu ngành trực tiếp thăm khám và đánh giá tình trạng; chẩn đoán, tư vấn và yêu cầu các chỉ định lâm sàng (xét nghiệm, X-quang, siêu âm…).'},
        # Thêm các bước tiếp theo...
        {'title': 'Thanh toán phí cận lâm sàng tại quầy Thu ngân',
         'description': 'Khách hàng tiến hành thanh toán các khoản phí cận lâm sàng.'},
        {'title':'Thực hiện các xét nghiệm cận lâm sàng theo chỉ định của bác sĩ',
         'description':'Dựa trên chỉ định của bác sĩ mà khách hàng lần lượt tiến hành các xét nghiệm cận lâm sàng như siêu âm, xét nghiệm máu, chụp X-quang, MRI, CT scanner…'},
        {'title':'Gặp bác sĩ đọc kết quả và tư vấn phương pháp điều trị',
         'description':'Sau khi có đầy đủ kết quả kiểm tra cận lâm sàng cần thiết, khách hàng gặp bác sĩ để được tư vấn'
                       ' tình trạng, phương pháp điều trị, cho toa thuốc, chỉ định nhập viện, chuyển viện hoặc hướng điều trị phù hợp và tốt'
                       ' nhất cho từng khách hàng.'
                        ' Khách hàng còn được tư vấn chế độ dinh dưỡng, tập luyện, các biện pháp phòng ngừa bệnh tật hiệu quả.'},
        {'title':'Mua thuốc và thanh toán tại Nhà thuốc bệnh viện',
         'description':'Đối với khách hàng không có BHYT: Khách hàng tiến hành mua thuốc và nghe hướng dẫn cách sử dụng thuốc.'
        ' Đối với khách hàng có BHYT: Bộ phận Chăm sóc khách hàng, nhân viên Quầy Thu ngân giải đáp các thắc mắc của khách hàng về chính sách, quyền lợi tham gia BHYT đối với các khách hàng có BHYT. Khách hàng được hướng dẫn thủ tục ra viện (nếu nhập viện), được thông báo khoản chi phí cuối cùng phải thanh toán sau trừ thẻ BHYT. Khách hàng nhận lại thẻ BHYT cùng các giấy tờ tùy nhân.'
                        ' Khách hàng nhận thuốc và được hướng dẫn, giải thích về liều lượng thuốc dùng theo chỉ định của bác sĩ.'}
    ]
    return render(request,'homepage/homeComponent/medical_examination_process_page.html',{'process_steps': process_steps})

def price_of_gudmec(request):
    return render(request, 'homepage/homeComponent/priceOfGudmec.html')


# def get_department(request, department_id):
#     department = get_object_or_404(Department, pk=department_id)
#     return JsonResponse({
#         "id": department.id,
#         "name": department.name_department,
#         "description": department.description_department,
#         "location": department.location,
#     })


# Lấy danh sách bác sĩ trong khoa
class fillter_doctor(APIView):
    permission_classes = [AllowAny]

    def get(self, request, department_id):
        if request.method == "GET":
            search_query = request.GET.get('search_query', None)
            gender = request.GET.get('gender', None)

            service = DepartmentService()
            # Lấy danh sách bác sĩ theo department_id
            doctors = service.get_doctors_by_department(department_id)

            # Kiểm tra các điều kiện tìm kiếm
            if search_query or gender:
                doctors = service.get_doctors_by_department(department_id, search_query, gender)

                context = {
                    "listDoctorOfDepartment": doctors
                }
                return render(request, "homepage/homeComponent/fillterListDoctor.html", context)
            
            # Nếu không có điều kiện tìm kiếm, trả về danh sách bác sĩ mặc định
            context = {
                "nav": "partials/navLogged.html",
                "view": "homepage/homeComponent/fillterDoctorPage.html",
                "file": "fillterDoctorPage",
                "listDepartmentResponse": service.get_all_departments(),
                "listDoctorOfDepartment": doctors,
                "departmentId": department_id
            }

            return render(request, "homepage/index.html", context)


# Lấy thông tin chi tiết của bác sĩ
def get_detail_doctor(request, doctor_id):
    user = request.user if request.user.is_authenticated else None
    bookings = doctor_service.get_list_booking_models_of_doctor(doctor_id)
    doctor = doctor_service.get_doctor_by_id(doctor_id)
    departments = department_service.get_all_departments()

    context = {
        "view": "listdoctor/bookAppointment",
        "file": "bookAppointment",
        "nav": "partials/navLogged",
        "navState": "navLogged",
        "doctor": doctor,
        "listDepartmentRespones": departments,
        "ListbookingAvailable": bookings,
        "scheduleRequest": {},  # Form trống để hiển thị
    }

    if user:
        context["user"] = user

    return render(request, "homePage/index.html", context)


# Lọc bác sĩ trong ngày hôm nay
def get_list_doctor_of_department_today(request, department_id):
    doctor_name = request.GET.get("q", "")
    gender = request.GET.get("gender", None)
    shift = request.GET.get("shift", "")

    doctors_today = department_service.list_doctor_today(department_id)
    doctors_filtered = department_service.filter_doctors(doctors_today, doctor_name, gender, shift, "today")

    context = {"listDoctorOfDepartment": doctors_filtered}
    return render(request, "listDoctor/listDoctorComponent.html", context)

#
# Lọc bác sĩ ngày mai
def get_list_doctor_of_department_tomorrow(request, department_id):
    doctor_name = request.GET.get("q", "")
    gender = request.GET.get("gender", None)
    shift = request.GET.get("shift", "")

    doctors_tomorrow = department_service.list_doctor_tomorrow(department_id)
    doctors_filtered = department_service.filter_doctors(doctors_tomorrow, doctor_name, gender, shift, "tomorrow")

    context = {"listDoctorOfDepartment": doctors_filtered}
    return render(request, "listDoctor/listDoctorComponent.html", context)


# Lọc bác sĩ trong 7 ngày tiếp theo
def get_list_doctor_of_department_next_seven_days(request, department_id):
    doctor_name = request.GET.get("q", "")
    gender = request.GET.get("gender", None)
    shift = request.GET.get("shift", "")

    doctors_next_seven_days = department_service.list_doctor_next_seven_days(department_id)
    doctors_filtered = department_service.filter_doctors(doctors_next_seven_days, doctor_name, gender, shift, "nextseven")

    context = {"listDoctorOfDepartment": doctors_filtered}
    return render(request, "listDoctor/listDoctorComponent.html", context)


# Lọc bác sĩ theo tên
def get_list_doctor_of_department_by_name(request, department_id):
    doctor_name = request.GET.get("q", "")
    gender = request.GET.get("gender", None)
    shift = request.GET.get("shift", "")

    doctors = department_service.get_list_doctor(department_id, include_all=True)
    doctors_filtered = department_service.filter_doctors(doctors, doctor_name, gender, shift, "none")

    context = {"listDoctorOfDepartment": doctors_filtered}
    return render(request, "listDoctor/listDoctorComponent.html", context)


# Lấy danh sách lịch khám của bác sĩ
def get_list_schedule_of_doctor(request, doctor_id):
    schedules = doctor_service.get_list_schedules_of_doctor(doctor_id)
    return JsonResponse(schedules, safe=False)

class DepartmentView(APIView):
    def get(self, request, department_id=None):
        if department_id:
            department = DepartmentService.get_department_by_id(department_id)
            if department:
                return Response(department, status=status.HTTP_200_OK)
            return Response({"error": "Department not found"}, status=status.HTTP_404_NOT_FOUND)

        departments = DepartmentService.get_all_departments()
        return Response(departments, status=status.HTTP_200_OK)

    def post(self, request):
        department = DepartmentService.create_department(request.data)
        return Response(department, status=status.HTTP_201_CREATED)



