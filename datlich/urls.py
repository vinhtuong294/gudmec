from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *
from . import views 

router = DefaultRouter()
router.register(r'users', UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('login/', LoginView.as_view(), name="login"),
    path('register/', RegisterView.as_view(), name="register"),
    path('password-reset/',views.password_reset, name="password_reset"),
    path('homepage/', home_page.as_view(), name='homepage'),
    path('api/logout/', LogoutView.as_view(), name='logout'),
    path('search/', search_result, name='search_result'),
    path('api/doctors-in-department/<int:department_id>/', views.fillter_doctor.as_view()),
    # path('appointment/<int:doctor_id>/', bookAppointment, name='appointment'),
    # path('departments/', DepartmentView.as_view()),
    # path('departments/<int:department_id>/', DepartmentView.as_view()),
    # path('medicalRecordInforPageComponent/', medicalRecordInforPageComponent, name='medicalRecordInforPageComponent'),
    # path('quytrinhkham/', prosess_page, name='prosess_page'),
    # path('price/', price_of_gudmec, name='price_of_gudmec'),
    # path('<int:department_id>/', views.get_department, name='get_department'),
    # path('doctors/<int:department_id>/', views.get_list_doctor_of_department, name='get_list_doctor_of_department'),
    # path('doctor/<int:doctor_id>/', views.get_detail_doctor, name='get_detail_doctor'),
    # path('doctors/today/<int:department_id>/', views.get_list_doctor_of_department_today, name='list_doctor_today'),
    # path('doctors/tomorrow/<int:department_id>/', views.get_list_doctor_of_department_tomorrow,
    #      name='list_doctor_tomorrow'),
    # path('doctors/nextsevenday/<int:department_id>/', views.get_list_doctor_of_department_next_seven_days,
    #      name='list_doctor_next_seven_days'),
    # path('doctors/byName/<int:department_id>/', views.get_list_doctor_of_department_by_name,
    #      name='list_doctor_by_name'),
    # path('doctor/schedules/<int:doctor_id>/', views.get_list_schedule_of_doctor, name='get_list_schedule_of_doctor'),
    # path('schedules/', ScheduleView.as_view(), name='schedule-list-create'),
    # path('revenue/<str:date>/', RevenueView.as_view(), name='daily-revenue'),
    # path('shifts/', ShiftListView.as_view(), name='shift-list'),
    # path('shifts/<int:id>/', ShiftDetailView.as_view(), name='shift-detail'),
]

