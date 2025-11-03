from django.contrib import admin
from .models import Department, Doctor, Patient, Visit, LabTest, Medicine, PatientMedicine, Reception
@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    pass

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    pass

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    pass

@admin.register(Visit)
class VisitAdmin(admin.ModelAdmin):
    pass

@admin.register(LabTest)
class LabTestAdmin(admin.ModelAdmin):
    pass

@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    pass

@admin.register(PatientMedicine)
class PatientMedicineAdmin(admin.ModelAdmin):
    pass
@admin.register(Reception)
class ReceptionAdmin(admin.ModelAdmin):
    pass