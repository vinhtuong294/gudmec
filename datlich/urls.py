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
    path('doi-ngu-bac-si/', DoiNguBacSi.as_view(), name='doi-ngu-bac-si'),
    path('comment/<int:id>/', Comment.as_view(), name='comment'),
    path('like/<int:id>/', Like.as_view(), name='like'),
    path('gudmec/', gudmec.as_view(), name='gudmec'),
    path('chuyenkhoa/', chuyenkhoa.as_view(), name='chuyenkhoa'),
    path('reset-password/', reset_password, name='reset_password'),
    path('dichvu/',dichvu.as_view(),name="dichvu"),
    path('homepage/thanhtuu/',thanhtuu.as_view(),name="thanhtuu"),
    path('thongtinchokhach/',thongtinchokhach.as_view(),name="thongtinchokhach"),
    path('thutucxuatnhapvien',thutucxuatnhapvien.as_view(),name="thutucxuatnhapvien"),
    path('mucdohailong/',mucdohailong.as_view(),name="mucdohailong"),
    path('huongdantracuu',huongdantracuu.as_view(),name="huongdantracuu"),
    path('dieutringoaitru/',dieutringoaitru.as_view(),name="dieutringoaitru"),
    path('thanhtoanbaohiem/',thanhtoanbaohiem.as_view(),name="thanhtoanbaohiem"),
    path('banggia/',banggia.as_view(),name="banggia"),
    path('noitru/',noitru.as_view(),name="noitru"),
    path('huongdankham/',huongdankham.as_view(),name="huongdankham"),
    path('editdoctor/', Edit_doctor.as_view(), name='editdoctor'),
    path('doingubacsiDocotr',DoiNguBacSidoctor.as_view(), name = 'doingubacsiDocotr'),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
