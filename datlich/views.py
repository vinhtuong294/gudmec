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
                       exceptions,scheduleServices,doctor_service)
from .services.authenticate_service import AuthenticateService
from .services.department_service import DepartmentService
from .services.scheduleServices import ScheduleService
from .services.userService import UserService
from .services.patient_service import PatientService
from .services.medicalRecordServices import MedicalRecordService
from .services.doctor_service  import DoctorService
from .services.articleService  import ArticleService
from .services.rateService  import RateService
from .services.likeService  import LikeService
from .services.commentService  import CommentService
import json
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.views.decorators.csrf import csrf_exempt
import secrets
import string


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer



class UserViewSet(viewsets.ModelViewSet):

    queryset = UserModel.objects.all()
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        print("Received data: %s", request.data)  # Log dữ liệu nhận được
        return super().create(request, *args, **kwargs)
    # permission_classes = [IsAuthenticated]


def generate_random_password(length=12):
    """Generate a random password."""
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(characters) for _ in range(length))

@csrf_exempt
def reset_password(request):
    if request.method == "POST":
        try:
            # Parse JSON từ body của request
            data = json.loads(request.body)
            email = data.get('email')
            print(email)
            
            if not email:
                print("Debug: Email field is missing from the request body.")  # Debug
                return JsonResponse({"error": "Email field is required."}, status=400)

            print('Debug: Received email:', email)  # Debug

            # Tìm người dùng có email
            user = get_object_or_404(UserModel, email=email)
            print('Debug: Found user:', user.email, "| Current password (hashed):", user.password)  # Debug

            # Tạo mật khẩu mới
            new_password = generate_random_password(12)
            print('Debug: New password to set:', new_password)  # Debug
            

            # Đặt lại mật khẩu
            user.set_password(new_password)
            user.save()
            print('Debug: Password updated successfully for user:', user.email)  # Debug

            # Gửi email thông báo
            send_mail(
                subject="Your Password Has Been Reset",
                message=f"Your new password is: {new_password}",
                from_email="chauchihieu2003@gmail.com",
                recipient_list=[email],
            )
            print('Debug: Email sent successfully to:', email)  # Debug

            return JsonResponse({"message": "New password sent to your email."}, status=200)

        except json.JSONDecodeError:
            print("Debug: Invalid JSON in request body.")  # Debug
            return JsonResponse({"error": "Invalid JSON."}, status=400)

        except UserModel.DoesNotExist:
            print("Debug: No user found with email:", email)  # Debug
            return JsonResponse({"error": "User with this email does not exist."}, status=404)

        except Exception as e:
            print("Debug: Unexpected error occurred:", str(e))  # Debug
            return JsonResponse({"error": "An unexpected error occurred."}, status=500)

    print("Debug: Invalid request method used.")  # Debug
    return JsonResponse({"error": "Invalid request method."}, status=405)

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



# Lấy danh sách bác sĩ trong khoa
class fillter_doctor(APIView):
    permission_classes = [AllowAny]

    def get(self, request, department_id):
        if request.method == "GET":
            search_query = request.GET.get('search_query', None)
            gender = request.GET.get('gender', None)
            session = request.GET.get('session', None)
            shift = request.GET.get('shift', None)

            service = DepartmentService()
            # Lấy danh sách bác sĩ theo department_id
            doctors = service.get_doctors_by_department(department_id)

            # Kiểm tra các điều kiện tìm kiếm
            if search_query or gender or session or shift or search_query =='':
                doctors = service.get_doctors_by_department(department_id, search_query, gender,session,shift)
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

class booking_doctor(APIView):
    permission_classes = [AllowAny]

    def get(self, request, doctor_id):
        if request.method == "GET":
            authenticate_service = AuthenticateService
            token = request.COOKIES.get('authToken')
            user = authenticate_service.get_user_from_token(token)
            date = request.GET.get('date', None)

            scheduleServices = ScheduleService()
            doctorService = DoctorService()
            rateService = RateService()
            shifts = scheduleServices.get_schedules_by_doctor(user.id,doctor_id,date)
            doctor = doctorService.get_one_doctors(doctor_id)
            rates = rateService.get_rate_doctor(doctor_id)
            if date:
                shifts = scheduleServices.get_schedules_by_doctor(user.id,doctor_id,date)
                context = {
                "booking_list": shifts,
                }
                return render(request, "homepage/homeComponent/bookModel.html", context)
            context = {
                "nav": "partials/navLogged.html",
                "view": "homepage/homeComponent/bookAppointment.html",
                "file": "bookAppointment",
                "booking_list": shifts,
                "doctor": doctor,
                "rates": rates,
            }

            return render(request, "homepage/index.html", context)
    def put(self, request, doctor_id):
        if request.method == "PUT":
            authenticate_service = AuthenticateService
            token = request.COOKIES.get('authToken')
            user = authenticate_service.get_user_from_token(token)
            scheduleServices = ScheduleService()
            shift = scheduleServices.booking(user.id,doctor_id)
            return Response({
                    "message": "Booking successfully.",
                }, status=status.HTTP_200_OK)



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


class Edit_user(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        if request.method == "GET":
            authenticate_service = AuthenticateService
            department_service = DepartmentService
            userService = UserService()
            token = request.COOKIES.get('authToken')
            user = authenticate_service.get_user_from_token(token)
            userInfo = userService.get_one_user(user.id)
            print(userInfo)
            if user.role_id==3 :
                context = {
                    "nav": "partials/navLogged.html",
                    "navState": "navLogged",
                    "view": "homepage/homeComponent/edit.html",
                    "file": "edit",
                    "listDepartmentResponse": department_service.get_all_departments(self),
                    "user": userInfo,
                }

                return render(request, "homepage/index.html", context)
    def post(self, request):
        authenticate_service = AuthenticateService
        userService = UserService
        token = request.COOKIES.get('authToken')
        user = authenticate_service.get_user_from_token(token)
        if user.role_id==3 :
            phone = request.POST.get('phone')
            fullname = request.POST.get('fullname')
            gender = request.POST.get('gender')
            birthday = request.POST.get('birthday')
            avatar = request.FILES.get('avatar')
            updated_user = userService.update_user(user.id,phone,fullname,gender,birthday,avatar)
            return Response({
                "message": "User updated successfully.",
                "user": {
                    "id": updated_user.id,
                    "fullname": updated_user.fullname,
                    "telephone": updated_user.telephone,
                    "gender": updated_user.gender,
                    "birthday": updated_user.birthday
                }
            }, status=status.HTTP_200_OK)
    def put(self, request):
        authenticate_service = AuthenticateService
        userService = UserService()
        token = request.COOKIES.get('authToken')
        user = authenticate_service.get_user_from_token(token)
        if user.role_id==3 :
            old_password = request.data.get('inputPassword')
            new_password = request.data.get('newPassword')
            userService.change_password(user.id,old_password,new_password)
            return Response({
                "message": "change password successfully."
            }, status=status.HTTP_200_OK)


class Appointment(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        if request.method == "GET":
            authenticate_service = AuthenticateService
            schedule_service = ScheduleService()
            token = request.COOKIES.get('authToken')
            user = authenticate_service.get_user_from_token(token)
            date = request.GET.get('date', None)
            shifts = schedule_service.get_doctor_schedules(user.id,date )
            if user.role_id==2 :
                context = {
                    "nav": "partials/navDoctorLogged.html",
                    "view": "homepage/homeComponent/appointmentDoctor.html",
                    "file": "appointmentDoctor",
                    "bookings":shifts
                }

                return render(request, "homepage/index.html", context)
            
            
class Medical_record(APIView):
    permission_classes = [AllowAny]

    def get(self, request, id):
        if request.method == "GET":
            authenticate_service = AuthenticateService
            medicalRecordService= MedicalRecordService()
            patientService = PatientService()
            schedule_service = ScheduleService()
            token = request.COOKIES.get('authToken')
            user = authenticate_service.get_user_from_token(token)
            records = medicalRecordService.get_record_patient_schedule(id)
            patient = patientService.get_patient_schedule_id(id)
            if user.role_id==2 :
                context = {
                    "nav": "partials/navDoctorLogged.html",
                    "view": "homepage/homeComponent/medicalrecord.html",
                    "file": "medicalrecord",
                    "medical_records": records,
                    "patient":patient,
                    "state": schedule_service.get_one_schedule(id).state,
                    "schedule_id":id,
                }

                return render(request, "homepage/index.html", context)
    def post(self, request,id):
        if request.method == "POST":
            data = request.data
            authenticate_service = AuthenticateService
            medicalRecordService= MedicalRecordService
            token = request.COOKIES.get('authToken')
            user = authenticate_service.get_user_from_token(token)
            if user.role_id==2 :
                medicalRecordService.create_medical_record(id,data)
                return Response({
                    "message": "Thêm bệnh án thành công"
                }, status=status.HTTP_200_OK)
                


class News(APIView):    
    permission_classes = [AllowAny]
    def get(self, request):
        authenticate_service = AuthenticateService
        token = request.COOKIES.get('authToken')
        user = authenticate_service.get_user_from_token(token)
        if user.role_id==2 :
            context = {
                "nav": "partials/navDoctorLogged.html",
                "view": "homepage/homeComponent/news.html",
                "file": "news",
            }

            return render(request, "homepage/index.html", context)
    def post(self, request):
        authenticate_service = AuthenticateService
        token = request.COOKIES.get('authToken')
        user = authenticate_service.get_user_from_token(token)
        if user.role_id==2 :
            title = request.POST.get('title')
            content = request.POST.get('content')
            image = request.FILES.get('image')
            data = {
                "title": title,
                "content": content,
                "image": image
            }
            articleService =ArticleService()
            articleService.create_article(data,user.id)
            return Response("create article successfully")
                    
class Posts(APIView):    
    permission_classes = [AllowAny]
    def get(self, request):
        authenticate_service = AuthenticateService
        token = request.COOKIES.get('authToken')
        user = authenticate_service.get_user_from_token(token)
        articleService =ArticleService()
        posts = articleService.get_alls(user.id)
        department_service = DepartmentService
        context = {
            "view": "homepage/homeComponent/posts.html",
            "file": "posts",
            "articles":posts,
            "listDepartmentResponse": department_service.get_all_departments(self),
        }
        if user.role_id==2 :
            context["nav"] = {"partials/navDoctorLogged.html"}
        if user.role_id==3 :
            context["nav"] = {"partials/navLogged.html"}

        return render(request, "homepage/homeComponent/posts.html", context)
    
class AppointmentHistory(APIView):    
    permission_classes = [AllowAny]
    def get(self, request):
        authenticate_service = AuthenticateService
        schedule_service = ScheduleService()
        token = request.COOKIES.get('authToken')
        user = authenticate_service.get_user_from_token(token)
        schedule = schedule_service.get_schedules_by_user(user.id)
        context = {
            "view": "homepage/homeComponent/appointmenthistory.html",
            "file": "appointmenthistory",
            "appointments": schedule,
        }
        if user.role_id==3 :
            context["nav"] = {"partials/navLogged.html"}

        return render(request, "homepage/index.html", context)

class MyMedicalRecord(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        authenticate_service = AuthenticateService
        medicalRecordService= MedicalRecordService()
        patientService = PatientService()
        token = request.COOKIES.get('authToken')
        departmentService = DepartmentService
        listDepartment = departmentService.get_all_departments_doctors(self)
        user = authenticate_service.get_user_from_token(token)
        patient = patientService.get_patient_by_user_id(user.id)
        records = medicalRecordService.get_record_patient(patient["id"])
        if user.role_id==3 :
            context = {
                "nav": "partials/navLogged.html",
                "view": "homepage/homeComponent/medicalrecord.html",
                "file": "medicalrecord",
                "listDepartmentResponse":listDepartment,
                "medical_records": records,
                "patient":patient,
                "role":user.role_id,
            }

            return render(request, "homepage/index.html", context)

class MyScheduleDetail(APIView):    
    permission_classes = [AllowAny]
    def get(self, request, id):
        authenticate_service = AuthenticateService
        schedule_service = ScheduleService()
        medicalRecordService= MedicalRecordService()
        token = request.COOKIES.get('authToken')
        user = authenticate_service.get_user_from_token(token)
        if user.role_id == 3:
            rateService= RateService()
            schedule = schedule_service.get_one_with_all(id)
            record = medicalRecordService.get_record_schedule(id)
            rate = rateService.get_my_rate_doctor(user.id,schedule.doctor.id)      
            context = {
                "nav": "partials/navLogged.html",
                "view": "homepage/homeComponent/myScheduleDetail.html",
                "file": "myScheduleDetail",
                "appointment": schedule,
                "record": record,
                "rate": rate,
            }

            return render(request, "homepage/index.html", context)
class Rate(APIView):    
    permission_classes = [AllowAny]
    def post(self, request, id):
        authenticate_service = AuthenticateService
        token = request.COOKIES.get('authToken')
        user = authenticate_service.get_user_from_token(token)
        if user.role_id == 3:
            rateService= RateService()
            rate = request.data.get('rate')
            content = request.data.get('content')
            data = {
                "rate": rate,
                "content": content,
            }
            print(data)
            rateService.create_update_rate(user.id,id,data)
            return Response('Rate successfully')
        
class MyHealth(APIView):    
    permission_classes = [AllowAny]
    def get(self, request):
        authenticate_service = AuthenticateService
        patientService = PatientService()
        departmentService = DepartmentService
        listDepartment = departmentService.get_all_departments_doctors(self)
        token = request.COOKIES.get('authToken')
        user = authenticate_service.get_user_from_token(token)
        patient = patientService.get_patient_by_user_id(user.id)
        if user.role_id==3 :
            context = {
                "nav": "partials/navLogged.html",
                "view": "homepage/homeComponent/medicalInfo.html",
                "file": "medicalInfo",
                "listDepartmentResponse":listDepartment,
                "patient":patient,
            }

            return render(request, "homepage/index.html", context)
    def put(self, request):
        data = request.data
        print(data)
        authenticate_service = AuthenticateService
        pantientService =  PatientService()
        token = request.COOKIES.get('authToken')
        user = authenticate_service.get_user_from_token(token)
        if user.role_id==3 :
            pantientService.update_patient_info(user.id, data)
            return Response({
                "message": "Cập nhật thành công"
            }, status=status.HTTP_200_OK)
            
            
class DoiNguBacSi(APIView):    
    permission_classes = [AllowAny]
    def get(self, request):
        authenticate_service = AuthenticateService
        token = request.COOKIES.get('authToken')
        user = authenticate_service.get_user_from_token(token)
        departmentService = DepartmentService
        listDepartment = departmentService.get_all_departments_doctors(self)

        if user.role_id==3 :
            context = {
                "nav": "partials/navLogged.html",
                "view": "homepage/homeComponent/DoiNguBacSi.html",
                "file": "DoiNguBacSi",
                "listDepartmentResponse":listDepartment,
            }

            return render(request, "homepage/index.html", context)

class Comment(APIView):    
    permission_classes = [AllowAny]
    def post(self, request, id):
        authenticate_service = AuthenticateService
        token = request.COOKIES.get('authToken')
        user = authenticate_service.get_user_from_token(token)
        if user.role_id==3 :
            content = request.data.get('content')
            likeService= CommentService()
            likeService.create_comment(id, user.id, content)
            return Response('comment successfully')
        
class Like(APIView):    
    permission_classes = [AllowAny]
    def post(self, request, id):
        authenticate_service = AuthenticateService
        token = request.COOKIES.get('authToken')
        user = authenticate_service.get_user_from_token(token)
        if user.role_id==3 :
            likeService= LikeService()
            likeService.create_like(id, user.id)
            return Response('like successfully')
    def delete(self, request, id):
        authenticate_service = AuthenticateService
        token = request.COOKIES.get('authToken')
        user = authenticate_service.get_user_from_token(token)
        if user.role_id==3 :
            likeService= LikeService()
            likeService.delete_like(id, user.id)
            return Response('unlike successfully')
        
class gudmec(APIView):   
    permission_classes = [AllowAny]      
    def get (self,request):
            departmentService = DepartmentService
            listDepartment = departmentService.get_all_departments_doctors(self)   
            context = {
                "nav": "partials/navLogged.html",
                "view": "homepage/homeComponent/gioithieu.html",
                "file": "gioithieu",
                "listDepartmentResponse":listDepartment,
            }

            return render(request, "homepage/index.html", context)
        
class chuyenkhoa(APIView):   
    permission_classes = [AllowAny]      
    def get (self,request):
            departmentService = DepartmentService
            listDepartment = departmentService.get_all_departments_doctors(self)   
            context = {
                "nav": "partials/navLogged.html",
                "view": "homepage/homeComponent/chuyenkhoa.html",
                "file": "chuyenkhoa",
                "listDepartmentResponse":listDepartment,
            }

            return render(request, "homepage/index.html", context)


class dichvu(APIView):   
    permission_classes = [AllowAny]      
    def get (self,request):
            departmentService = DepartmentService
            listDepartment = departmentService.get_all_departments_doctors(self)   
            context = {
                "nav": "partials/navLogged.html",
                "view": "homepage/homeComponent/dichvu.html",
                "file": "dichvu",
                "listDepartmentResponse":listDepartment,
            }

            return render(request, "homepage/index.html", context)
        
class thanhtuu(APIView):   
    permission_classes = [AllowAny]      
    def get (self,request):
            departmentService = DepartmentService
            listDepartment = departmentService.get_all_departments_doctors(self)   
            context = {
                "nav": "partials/navLogged.html",
                "view": "homepage/homeComponent/thanhtuu.html",
                "file": "thanhtuu",
                "listDepartmentResponse":listDepartment,
            }

            return render(request, "homepage/index.html", context)
        
class thongtinchokhach(APIView):   
    permission_classes = [AllowAny]      
    def get (self,request):
            departmentService = DepartmentService
            listDepartment = departmentService.get_all_departments_doctors(self)   
            context = {
                "nav": "partials/navLogged.html",
                "view": "homepage/homeComponent/thongtinchokhach.html",
                "file": "thongtinchokhach",
                "listDepartmentResponse":listDepartment,
            }

            return render(request, "homepage/index.html", context)
        
        
class thutucxuatnhapvien(APIView):   
    permission_classes = [AllowAny]      
    def get (self,request):
            departmentService = DepartmentService
            listDepartment = departmentService.get_all_departments_doctors(self)   
            context = {
                "nav": "partials/navLogged.html",
                "view": "homepage/homeComponent/thutucxuatnhapvien.html",
                "file": "thutucxuatnhapvien",
                "listDepartmentResponse":listDepartment,
            }

            return render(request, "homepage/index.html", context)
        
class mucdohailong(APIView):   
    permission_classes = [AllowAny]      
    def get (self,request):
            departmentService = DepartmentService
            listDepartment = departmentService.get_all_departments_doctors(self)   
            context = {
                "nav": "partials/navLogged.html",
                "view": "homepage/homeComponent/mucdohailong.html",
                "file": "mucdohailong",
                "listDepartmentResponse":listDepartment,
            }

            return render(request, "homepage/index.html", context)
        
        
class huongdantracuu(APIView):   
    permission_classes = [AllowAny]      
    def get (self,request):
            departmentService = DepartmentService
            listDepartment = departmentService.get_all_departments_doctors(self)   
            context = {
                "nav": "partials/navLogged.html",
                "view": "homepage/homeComponent/huongdantracuu.html",
                "file": "huongdantracuu",
                "listDepartmentResponse":listDepartment,
            }

            return render(request, "homepage/index.html", context)
        
class dieutringoaitru(APIView):   
    permission_classes = [AllowAny]      
    def get (self,request):
            departmentService = DepartmentService
            listDepartment = departmentService.get_all_departments_doctors(self)   
            context = {
                "nav": "partials/navLogged.html",
                "view": "homepage/homeComponent/dieutringoaitru.html",
                "file": "dieutringoaitru",
                "listDepartmentResponse":listDepartment,
            }

            return render(request, "homepage/index.html", context)
        
class thanhtoanbaohiem(APIView):   
    permission_classes = [AllowAny]      
    def get (self,request):
            departmentService = DepartmentService
            listDepartment = departmentService.get_all_departments_doctors(self)   
            context = {
                "nav": "partials/navLogged.html",
                "view": "homepage/homeComponent/thanhtoanbaohiem.html",
                "file": "thanhtoanbaohiem",
                "listDepartmentResponse":listDepartment,
            }

            return render(request, "homepage/index.html", context)
        
class banggia(APIView):   
    permission_classes = [AllowAny]      
    def get (self,request):
            departmentService = DepartmentService
            listDepartment = departmentService.get_all_departments_doctors(self)   
            context = {
                "nav": "partials/navLogged.html",
                "view": "homepage/homeComponent/banggia.html",
                "file": "banggia",
                "listDepartmentResponse":listDepartment,
            }

            return render(request, "homepage/index.html", context)
        
class noitru(APIView):   
    permission_classes = [AllowAny]      
    def get (self,request):
            departmentService = DepartmentService
            listDepartment = departmentService.get_all_departments_doctors(self)   
            context = {
                "nav": "partials/navLogged.html",
                "view": "homepage/homeComponent/noitru.html",
                "file": "noitru",
                "listDepartmentResponse":listDepartment,
            }

            return render(request, "homepage/index.html", context)
        
class huongdankham(APIView):   
    permission_classes = [AllowAny]      
    def get (self,request):
            departmentService = DepartmentService
            listDepartment = departmentService.get_all_departments_doctors(self)   
            context = {
                "nav": "partials/navLogged.html",
                "view": "homepage/homeComponent/huongdankham.html",
                "file": "huongdankham",
                "listDepartmentResponse":listDepartment,
            }

            return render(request, "homepage/index.html", context)