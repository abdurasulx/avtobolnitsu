from django.urls import path
from . import views
from . import patient_views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('dashboard/',views.redashboard,name='dashboard2'),
    
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('accounts/logout/', views.logout, name='logout'),
    path('signup/', views.signup, name='signup'),

    # Patients
    path('patients/', views.PatientListView.as_view(), name='patient_list'),
    path('patients/<int:pk>/', views.patient_detail, name='patient_detail'),
    path('patients/add/', views.PatientCreateView.as_view(), name='patient_add'),
    path('patients/<int:pk>/edit/', views.PatientUpdateView.as_view(), name='patient_edit'),
    path('patients/<int:pk>/delete/', views.PatientDeleteView.as_view(), name='patient_delete'),
    path('patients/export/', views.export_patients_csv, name='patient_export'),
    path('patients/profile/', views.ProfileView.as_view(), name='patient_profile'),
    

    # Doctors
    path('doctors/', views.DoctorListView.as_view(), name='doctor_list'),
    path('doctors/add/', views.DoctorCreateView.as_view(), name='doctor_add'),
    path('doctors/<int:pk>/edit/', views.DoctorUpdateView.as_view(), name='doctor_edit'),
    path('doctors/<int:pk>/delete/', views.DoctorDeleteView.as_view(), name='doctor_delete'),
    path('doctors/export/', views.export_doctors_csv, name='doctor_export'),
    path('doctors/profile/', views.DoctorProfileView.as_view(), name='doctor_profile'),
    path('doctors/prescribe/', views.PrescribeMedicineView.as_view(), name='prescribe_medicine'),


    # Visits
    path('visits/', views.VisitListView.as_view(), name='visit_list'),
    path('visits/add/', views.VisitCreateView.as_view(), name='visit_add'),
    path('visits/<int:pk>/edit/', views.VisitUpdateView.as_view(), name='visit_edit'),
    path('visits/<int:pk>/delete/', views.VisitDeleteView.as_view(), name='visit_delete'),
    path('visits/export/', views.export_visits_csv, name='visit_export'),
    path('pvisits/', views.PatientVisitsView.as_view(), name='patient_visit_list'),
    path('api/visits/latest/', views.latest_visits_api, name='latest_visits_api'),

    # LabTests
    path('labtests/', views.LabTestListView.as_view(), name='labtest_list'),
    path('labtests/add/', views.LabTestCreateView.as_view(), name='labtest_add'),
    path('labtests/<int:pk>/edit/', views.LabTestUpdateView.as_view(), name='labtest_edit'),
    path('labtests/<int:pk>/delete/', views.LabTestDeleteView.as_view(), name='labtest_delete'),
    path('labtests/export/', views.export_labtests_csv, name='labtest_export'),

    # Medicines
    path('medicines/', views.MedicineListView.as_view(), name='medicine_list'),
    path('medicines/add/', views.MedicineCreateView.as_view(), name='medicine_add'),
    path('medicines/<int:pk>/edit/', views.MedicineUpdateView.as_view(), name='medicine_edit'),
    path('medicines/<int:pk>/delete/', views.MedicineDeleteView.as_view(), name='medicine_delete'),
    path('medicines/export/', views.export_medicines_csv, name='medicine_export'),

    # PatientMedicines
    path('patientmedicines/', views.PatientMedicineListView.as_view(), name='patientmedicine_list'),
    path('patientmedicines/add/', views.PatientMedicineCreateView.as_view(), name='patientmedicine_add'),
    path('patientmedicines/<int:pk>/edit/', views.PatientMedicineUpdateView.as_view(), name='patientmedicine_edit'),
    path('patientmedicines/<int:pk>/delete/', views.PatientMedicineDeleteView.as_view(), name='patientmedicine_delete'),
    path('patientmedicines/export/', views.export_patientmedicines_csv, name='patientmedicine_export'),

    # landing
    path('landing/', views.landing, name='landing'),
    path('create_visit/',views.create_visit,name='create_visit'),
    # Reception URLs
    path('reception/patients/', views.reception_patients, name='reception_patients'),
    path('reception/patients/<int:pk>/', views.reception_patient_detail, name='reception_patient_detail'),
    path('reception/patients/<int:pk>/edit/', views.edit_patient, name='edit_reception_patient'),
    path('reception/visits/', views.reception_visits, name='reception_visits'),
    path('reception/visits/<int:pk>/edit/', views.edit_visit, name='edit_reception_visit'),
    path('reception/add_patient/', views.add_patient, name='add_patient'),
    path('reception/profile/', views.reception_profile, name='reception_profile'),
    path('reception/profile/change-password/', views.reception_change_password, name='reception_change_password'),

    # reception for admin
    path('receptions/', views.reception_list, name='reception_list'),
    path('receptions/add/', views.add_reception, name='add_reception'),
    path('receptions/<int:pk>/edit/', views.edit_reception, name='reception_edit'),
    path('receptions/<int:pk>/delete/', views.delete_reception, name='delete_reception'),

    #Department
    path('department/add',views.department_create,name='add_department'),
    path('department/<int:pk>/edit/',views.derpartment_edit,name='edit_department'),
    path('department/<int:pk>/delete/',views.department_delete,name='delete_department'),
    path('api/department/add/',views.department_add,name='add_department_api'),
    
    # Patient menu enhancements - import from patient_views
    path('patients/prescriptions/', patient_views.patient_prescriptions, name='patient_prescriptions'),
    path('patients/labtests/', patient_views.patient_labtests, name='patient_labtests'),
    path('patients/book-appointment/', patient_views.patient_book_appointment, name='patient_book_appointment'),

]