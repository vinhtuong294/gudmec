from datlich.models import Rate, Doctor, UserModel
from datetime import datetime, timedelta

class RateService:
    def get_all_rate(self):
        return Rate.objects.all()
    def get_rate_doctor(self, doctor_id):
        rate =  Rate.objects.all()
        rate = rate.filter(doctor_id=doctor_id).order_by('-id')
        return rate
    def get_my_rate_doctor(self,user_id, doctor_id):
        rate = Rate.objects.select_related('user').get(doctor_id=doctor_id, user_id=user_id)
        return rate

 #Tạo và chỉnh sửa đánh giá   
    def create_update_rate(self,user_id, doctor_id,data ):
        rate = Rate.objects.get(doctor_id=doctor_id, user_id=user_id)
        if rate:
            rate.rate = data["rate"]
            rate.content = data["content"]
            rate.save()
        else :
            user = UserModel.objects.get(id = user_id)
            doctor = Doctor.objects.get(id = doctor_id)
            print(data["content"])
            rate = Rate.objects.create(
                    content=data["content"],
                    rate=data["rate"],
                    user=user,
                    doctor=doctor
                )
            return rate