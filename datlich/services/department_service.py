from datlich.models import Department

class DepartmentService:
    def get_all_departments(self):
        return Department.objects.all()

    def get_department_by_id(self, department_id):
        try:
            return Department.objects.get(id=department_id)
        except Department.DoesNotExist:
            return None
    def get_doctors_by_department(self, department_id, search_query=None, gender=None):
        try:
            department = Department.objects.get(id=department_id)

            doctors = department.list_doctors.select_related('user', 'department').all()

            # print(str(gender), "asdasd")
            # print(str(doctors.first().user.gender).lower(), "dtb")
            # print(str(doctors.first().user.gender).lower() == str(gender))

            if search_query:
                doctors = doctors.filter(user__fullname__icontains=search_query)

        # Filter by gender if provided
            if gender:
                gender = 1 if gender == "true" else 0
                
                print(gender, 'req')
                print(doctors.first().user.gender, 'db')

                print(gender == doctors.first().user.gender)
                doctors = doctors.filter(user__gender__iexact=gender)

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