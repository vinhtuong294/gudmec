from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(UserModel)
admin.site.register(Department)
admin.site.register(Schedule)
admin.site.register(Shift)
admin.site.register(Patient)
admin.site.register(MedicalRecord)
admin.site.register(Article)

