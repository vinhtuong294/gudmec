from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *
from . import views 
from django.conf import settings
from django.conf.urls.static import static

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
    path('appointment/<int:doctor_id>/', booking_doctor.as_view(), name='appointment'),
    path('edit/', Edit_user.as_view(), name='edit'),
    path('appointment/', Appointment.as_view(), name='appointmentDoctor'),
    path('medical-record/<int:id>/', Medical_record.as_view(), name='medicalrecord'),
    path('news/', News.as_view(), name = 'news'),
    path('posts/', Posts.as_view(), name = 'posts'),
    path('appointmenthistory/', AppointmentHistory.as_view(), name = 'appointmenthistory'),
    path('my-medical-record/', MyMedicalRecord.as_view(), name='mymedicalrecord'),
    path('my-schedule/<int:id>/detail/', MyScheduleDetail.as_view(), name='my-schedule-detail'),
    path('rate/<int:id>/', Rate.as_view(), name='rate'),
    path('my-health/', MyHealth.as_view(), name='myhealth'),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
