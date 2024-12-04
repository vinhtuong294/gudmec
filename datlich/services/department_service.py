from datlich.models import Department
from datetime import datetime, timedelta

class DepartmentService:
    def get_all_departments(self):
        return Department.objects.all()

    def get_department_by_id(self, department_id):
        try:
            return Department.objects.get(id=department_id)
        except Department.DoesNotExist:
            return None
    def get_doctors_by_department(self, department_id, search_query=None, gender=None, session=None, shift=None):
        try:
            department = Department.objects.get(id=department_id)

            doctors = department.list_doctors.select_related('user', 'department').all()
            
            doctors = doctors.filter(schedules__is_ready=True ).distinct()

            if search_query:
                doctors = doctors.filter(user__fullname__icontains=search_query)

        # Filter by gender if provided
            if gender:
                gender = 0 if gender == "true" else 1
                
                doctors = doctors.filter(user__gender__iexact=gender)
            if shift == 'today':
                today = datetime.today().date()
                doctors = doctors.filter(
                    schedules__date = today
                ).distinct()
                print(doctors)
            if shift == 'tomorrow':
                tomorrow = datetime.today().date() + timedelta(days=1)
                doctors = doctors.filter(
                    schedules__date = tomorrow
                ).distinct()
            if shift == 'nextsevenday':
                nextsevenday = datetime.today().date() + timedelta(days=7)
                doctors = doctors.filter(
                    schedules__date__lte = nextsevenday
                ).distinct()
            if session == 'morning':
                doctors = doctors.filter(
                schedules__shift__id__in=[1,2,3,4,5,6,7,8]
                ).distinct()    
            if session == 'afternoon':
                doctors = doctors.filter(
                schedules__shift__id__in=[9,10,11,12,13,14,15,16]
                ).distinct()  
            return [
                {
                    "id": doctor.id,
                    "position": doctor.position,
                    "description": doctor.description,
                    "room_address": doctor.room_address,
                    "service_prices": doctor.service_prices,
                    "department": {
                        "id": doctor.department.id,
                        "name": doctor.department.name_department
                    },
                    "user": {
                        "id": doctor.user.id,
                        "fullname": doctor.user.fullname,
                        "email": doctor.user.email,
                        "telephone": doctor.user.telephone,
                        "gender": doctor.user.gender,
                    }
                }
                for doctor in doctors
            ]
        except Department.DoesNotExist:
            return []