from datlich.models import Rate, Doctor, UserModel
from datetime import datetime, timedelta

class RateService:
    def get_all_rate(self):
        return Rate.objects.all()
    def get_rate_doctor(self, doctor_id):
        rate =  Rate.objects.all()
        rate = rate.filter(doctor_id=doctor_id).order_by('-id')
        return rate

    
    def create_rate(self,user_id, doctor_id,data ):
        user = UserModel.objects.get(id = user_id)
        doctor = Doctor.objects.get(id = doctor_id)
        print(data["content"])
        article = Rate.objects.create(
                content=data["content"],
                rate=data["rate"],
                user=user,
                doctor=doctor
            )
        return article