import csv
from io import StringIO
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.db.models import Q
from .models import Patient, Doctor, Visit, LabTest, Medicine, PatientMedicine, Department, Reception
from .forms import PatientForm, DoctorForm, VisitForm, LabTestForm, MedicineForm, PatientMedicineForm, SignUpForm , SetPPasswordForm, ReceptionForm, DepartmentForm
from django.contrib.auth.forms import SetPasswordForm
import logging
from django.urls import reverse_lazy , reverse
from django.db import IntegrityError
from django.views.generic import TemplateView
from django.http import HttpResponseRedirect



from django.utils import timezone


logger = logging.getLogger('hospital')

def is_admin(user):
    return user.is_superuser

def is_doctor(user):
    return hasattr(user, 'doctor')

def is_nurse(user):

    return user.groups.filter(name='Nurse').exists()
def is_receptionist(user):
    return hasattr(user, 'reception')

ogger = logging.getLogger(__name__)

def dashboard(request):
    from datetime import timedelta
    doctor = getattr(request.user, 'doctor', None)
    patient = getattr(request.user, 'patient', None)
    receptionist = getattr(request.user, 'reception', None)
    today = timezone.now().date()
    now = timezone.now()


    if doctor:
        recent_week = now - timedelta(days=7)
        recent_visits = (
            Visit.objects.filter(doctor=doctor)
            .select_related('patient')
            .order_by('-visit_datetime')[:5]
        )

        scheduled_appointments = Visit.objects.filter(
            doctor=doctor,
            visit_datetime__date=today
        )

        active_patients_count = (
            Patient.objects.filter(visit__doctor=doctor, visit__status='in_progress')
            .distinct()
            .count()
        )

        context = {
            'doctor': doctor,
            'recent_visits': recent_visits,
            'weekly_visits': Visit.objects.filter(doctor=doctor, visit_datetime__gte=recent_week).count(),
            'scheduled_appointments': scheduled_appointments,
            'todays_visits_count': scheduled_appointments.count(),
            'active_patients_count': active_patients_count,
        }

        return render(request, 'doctors/dashboard.html', context)

    elif patient:

        patient_visits = (
            Visit.objects.filter(patient=patient)
            .select_related('doctor')
            .order_by('-visit_datetime')[:5]
        )

        if not patient_visits.exists():
            message = "На данный момент вы не проходите лечение."
        else:
            message = None
        medicines = PatientMedicine.objects.filter(patient=patient)

        context = {
            'patient': patient,
            'patient_visits': patient_visits,
            'message': message,
            'medicines': medicines,
        }

        return render(request, 'patients/dashboard.html', context)
    elif receptionist:
        visits_today = Visit.objects.filter(visit_datetime__date=today).count()
        total_patients = Patient.objects.count()
        total_doctors = Doctor.objects.count()
        new_patients_today = Patient.objects.filter(created_at__date=today).count()

        context = {
            'visits_today': visits_today,
            'new_patients_today': new_patients_today,
        }

        return render(request, 'reception/dashboard.html', context)
    elif not request.user.is_authenticated:
        return redirect('landing')


    else:
        one_hour_ago = now - timedelta(hours=1)

        daily_visits = Visit.objects.filter(visit_datetime__date=today).count()
        new_patients_today = Patient.objects.filter(created_at__date=today).count()
        total_doctors = Doctor.objects.count()
        total_patients = Patient.objects.count()
        active_doctors = Doctor.objects.filter(user__last_login__gte=one_hour_ago).count()

        recent_visits = (
            Visit.objects.select_related('patient', 'doctor')
            .order_by('-visit_datetime')[:5]
        )


        visits_last_7_days = []
        for i in range(7):
            date = today - timedelta(days=i)
            count = Visit.objects.filter(visit_datetime__date=date).count()
            visits_last_7_days.append({'date': date.strftime('%d-%b'), 'count': count})
        visits_last_7_days.reverse()

        context = {
            'daily_visits': daily_visits,
            'new_patients_today': new_patients_today,
            'total_doctors': total_doctors,
            'total_patients': total_patients,
            'recent_visits': recent_visits,
            'visits_last_7_days': visits_last_7_days,
            'active_doctors': active_doctors,
        }

        logger.info( f"Админ {request.user} получил доступ к панели управления. " f"Ежедневные посещения: {daily_visits}, Новые пациенты: {new_patients_today}" )

        return render(request, 'dashboard.html', context)
def redashboard(request):
    return redirect('dashboard')

class PatientListView(LoginRequiredMixin, ListView):
    model = Patient
    template_name = 'patients/list.html'
    context_object_name = 'patients'

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_superuser and hasattr(self.request.user, 'doctor'):
            # Shifokor faqat o'z bemorlarini ko'radi
            qs = qs.filter(visit__doctor=self.request.user.doctor)
        return qs.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['export_url'] = '/patients/export/'
        return context

@login_required
def patient_detail(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    # Permission check
    if not request.user.is_superuser and hasattr(request.user, 'doctor'):
        if not Visit.objects.filter(patient=patient, doctor=request.user.doctor).exists():
            messages.error(request, "У вас нет разрешения (доступа).")
            return redirect('patient_list')
    visits = Visit.objects.filter(patient=patient)
    tests = LabTest.objects.filter(patient=patient)
    meds = PatientMedicine.objects.filter(patient=patient)
    context = {'patient': patient, 'visits': visits, 'tests': tests, 'meds': meds}
    logger.info(f"Пользователь {request.user} просмотрел пациента {patient.id}")
    return render(request, 'patients/detail.html', context)

class PatientCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Patient
    form_class = PatientForm
    template_name = 'patients/add.html'
    success_url = '/patients/'

    def test_func(self):
        return self.request.user.is_superuser or is_nurse(self.request.user)

    def form_valid(self, form):
        logger.info(f"Пользователь {self.request.user} создал пациента {form.instance.first_name}")
        return super().form_valid(form)

class PatientUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Patient
    form_class = PatientForm
    template_name = 'patients/edit.html'
    success_url = '/patients/'

    def test_func(self):
        return self.request.user.is_superuser or is_nurse(self.request.user)

    def form_valid(self, form):
        logger.info(f"Пользователь {self.request.user} обновил пациента {form.instance.id}")
        return super().form_valid(form)

class PatientDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Patient
    success_url = '/patients/'

    def test_func(self):
        return self.request.user.is_superuser

    def delete(self, request, *args, **kwargs):
        logger.info(f"User {request.user} deleted patient {kwargs['pk']}")
        return super().delete(request, *args, **kwargs)

@login_required
def export_patients_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="patients.csv"'
    writer = csv.writer(response)
    writer.writerow(['ID', 'Имя', 'Фамилия', 'Дата рождения', 'Пол', 'Телефон'])
    for patient in Patient.objects.all():
        writer.writerow([patient.id, patient.first_name, patient.last_name, patient.birth_date, patient.gender, patient.phone])
    logger.info(f"Пользователь {request.user} экспортировал CSV-файл пациентов")
    return response

# Doctors
class DoctorListView(LoginRequiredMixin, ListView):
    model = Doctor
    template_name = 'doctors/list.html'
    context_object_name = 'doctors'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['export_url'] = '/doctors/export/'
        return context

class DoctorCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Doctor
    form_class = DoctorForm
    template_name = 'doctors/add.html'
    success_url = reverse_lazy('doctor_list')

    def test_func(self):
        return self.request.user.is_superuser

    def form_valid(self, form):
        try:
            doctor = form.save(commit=True)
            messages.success(
                self.request,
                f"Доктор {doctor.user.get_full_name()} успешно добавлен ✅"
            )
            return super().form_valid(form)
        except IntegrityError:
            messages.error(
                self.request,
                f"Пользователь с логином «{form.cleaned_data.get('username')}» уже существует. "
                "Пожалуйста, выберите другой логин."
            )
            return self.form_invalid(form)
        except Exception as e:
            messages.error(
                self.request,
                f"Произошла ошибка при создании врача: {str(e)}"
            )
            return self.form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Ошибка при заполнении формы. Проверьте данные и попробуйте снова.")
        return super().form_invalid(form)

class DoctorUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Doctor
    form_class = DoctorForm
    template_name = 'doctors/edit.html'
    success_url = '/doctors/'

    def test_func(self):
        return self.request.user.is_superuser

    def form_valid(self, form):
        logger.info(f"User {self.request.user} updated doctor {form.instance.id}")
        return super().form_valid(form)

class DoctorDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Doctor
    success_url = '/doctors/'

    def test_func(self):
        return self.request.user.is_superuser

    def delete(self, request, *args, **kwargs):
        logger.info(f"User {request.user} deleted doctor {kwargs['pk']}")
        return super().delete(request, *args, **kwargs)
class DoctorProfileView(LoginRequiredMixin, DetailView):
    model = Doctor
    template_name = 'doctors/profile.html'
    context_object_name = 'doctor'

    def get_object(self, queryset=None):
        # Foydalanuvchining o'ziga tegishli Doctor obyektini qaytaradi
        return get_object_or_404(Doctor, user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Parol formasi (faqat admin emas, oddiy foydalanuvchi uchun ham)
        context['password_form'] = SetPasswordForm(user=self.request.user)
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        # Foydalanuvchi "parolni o‘zgartirish" formasini yuborganmi, tekshiramiz
        new_password1 = request.POST.get('new_password1', '').strip()
        new_password2 = request.POST.get('new_password2', '').strip()

        # Agar ikkala parol ham bo‘sh bo‘lsa, hech narsa o‘zgartirmay qaytamiz
        if not new_password1 and not new_password2:
            messages.info(request, "Изменения не были внесены.")
            return redirect('doctor_profile')

        # Parol formasi bilan tekshiruv
        form = SetPasswordForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Пароль успешно изменён.")
            return redirect('doctor_profile')
        else:
            # Xatolik bo‘lsa, sahifani xatolik bilan qaytaradi
            context = self.get_context_data()
            context['password_form'] = form
            return self.render_to_response(context)@login_required
def export_doctors_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="doctors.csv"'
    writer = csv.writer(response)
    writer.writerow(['ID', 'Пользователь', 'Отделение (Раздел)', 'Специальность'])
    for doctor in Doctor.objects.all():
        writer.writerow([doctor.id, doctor.user.username, doctor.department.name if doctor.department else '', doctor.specialty])
    return response

# Visits
class VisitListView(LoginRequiredMixin, ListView):
    model = Visit
    template_name = 'visits/list.html'
    context_object_name = 'visits'

    def get_queryset(self):
        qs = super().get_queryset()
        if is_doctor(self.request.user):
            qs = qs.filter(doctor=self.request.user.doctor)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['export_url'] = '/visits/export/'
        return context

class VisitCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Visit
    form_class = VisitForm
    template_name = 'visits/add.html'
    success_url = '/visits/'

    def test_func(self):
        return self.request.user.is_superuser or is_doctor(self.request.user) or is_nurse(self.request.user)

    def form_valid(self, form):
        logger.info(f"Пользователь {self.request.user} создал посещение для пациента {form.instance.patient.id}")
        return super().form_valid(form)

class VisitUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Visit
    form_class = VisitForm
    template_name = 'visits/edit.html'
    success_url = '/visits/'

    def test_func(self):
        obj = self.get_object()
        return (
            self.request.user.is_superuser
            or (is_doctor(self.request.user) and obj.doctor == self.request.user.doctor)
            or is_nurse(self.request.user)
        )

    def get_template_names(self):
        if self.request.user.is_superuser or is_nurse(self.request.user):
            return ['visits/edit.html']
        elif is_doctor(self.request.user):
            return ['doctors/dedit.html']
        return super().get_template_names()

    def form_valid(self, form):
        # Avval ma'lumotni saqlaymiz
        self.object = form.save()
        logger.info(f"Пользователь {self.request.user} обновил посещение {self.object.id}")

        user = self.request.user
        # So‘ng rolga qarab redirect qilamiz
        if user.is_superuser:
            return redirect(reverse('dashboard'))  # admin dashboard
        elif is_doctor(user):
            return redirect(reverse('dashboard'))  # doctor sahifasi
        else:
            return super().form_valid(form)


class VisitDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Visit
    success_url = '/visits/'

    def test_func(self):
        obj = self.get_object()
        return (self.request.user.is_superuser or 
                (is_doctor(self.request.user) and obj.doctor == self.request.user.doctor))

    def delete(self, request, *args, **kwargs):
        logger.info(f"Пользователь {request.user} удалил посещение {kwargs['pk']}")
        return super().delete(request, *args, **kwargs)

@login_required
def export_visits_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="visits.csv"'
    writer = csv.writer(response)
    writer.writerow(['ID', 'Пациент', 'Врач', 'Диагноз', 'Дата'])
    for visit in Visit.objects.all():
        writer.writerow([visit.id, str(visit.patient), str(visit.doctor) if visit.doctor else '', visit.diagnosis[:50], visit.visit_datetime])
    return response

# LabTests
class LabTestListView(LoginRequiredMixin, ListView):
    model = LabTest
    template_name = 'labtests/list.html'
    context_object_name = 'labtests'

    def get_queryset(self):
        qs = super().get_queryset()
        if is_doctor(self.request.user):
            qs = qs.filter(patient__visit__doctor=self.request.user.doctor)
        return qs.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['export_url'] = '/labtests/export/'
        return context

class LabTestCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = LabTest
    form_class = LabTestForm
    template_name = 'labtests/add.html'
    success_url = '/labtests/'

    def test_func(self):
        return self.request.user.is_superuser or is_nurse(self.request.user)

    def form_valid(self, form):
        logger.info(f"Пользователь {self.request.user} создал лабораторный анализ для пациента {form.instance.patient.id}")
        return super().form_valid(form)

class LabTestUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = LabTest
    form_class = LabTestForm
    template_name = 'labtests/edit.html'
    success_url = '/labtests/'

    def test_func(self):
        obj = self.get_object()
        return (self.request.user.is_superuser or 
                (is_doctor(self.request.user) and obj.patient.visit_set.filter(doctor=self.request.user.doctor).exists()) or 
                is_nurse(self.request.user))

    def form_valid(self, form):
        logger.info(f"Пользователь {self.request.user} обновил лабораторный анализ {form.instance.id}")
        return super().form_valid(form)

class LabTestDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = LabTest
    success_url = '/labtests/'

    def test_func(self):
        obj = self.get_object()
        return (self.request.user.is_superuser or 
                (is_doctor(self.request.user) and obj.patient.visit_set.filter(doctor=self.request.user.doctor).exists()))

    def delete(self, request, *args, **kwargs):
        logger.info(f"Пользователь {request.user} удалил лабораторный анализ {kwargs['pk']}")
        return super().delete(request, *args, **kwargs)

@login_required
def export_labtests_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="labtests.csv"'
    writer = csv.writer(response)
    writer.writerow(['ID', 'Пациент', 'Тип (Вид)', 'Результат', 'Дата'])
    for test in LabTest.objects.all():
        writer.writerow([test.id, str(test.patient), test.test_type, test.result[:50], test.result_date])
    return response

# Medicines
class MedicineListView(LoginRequiredMixin, ListView):
    model = Medicine
    template_name = 'medicines/list.html'
    context_object_name = 'medicines'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['export_url'] = '/medicines/export/'
        return context

class MedicineCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Medicine
    form_class = MedicineForm
    template_name = 'medicines/add.html'
    success_url = '/medicines/'

    def test_func(self):
        return self.request.user.is_superuser or is_doctor(self.request.user)

    def form_valid(self, form):
        logger.info(f"Пользователь {self.request.user} создал лекарство {form.instance.name}")
        return super().form_valid(form)

class MedicineUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Medicine
    form_class = MedicineForm
    template_name = 'medicines/edit.html'
    success_url = '/medicines/'

    def test_func(self):
        return self.request.user.is_superuser or is_doctor(self.request.user)

    def form_valid(self, form):
        logger.info(f"Пользователь {self.request.user} обновил лекарство {form.instance.id}")
        return super().form_valid(form)

class MedicineDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Medicine
    success_url = '/medicines/'

    def test_func(self):
        return self.request.user.is_superuser

    def delete(self, request, *args, **kwargs):
        logger.info(f"Пользователь {request.user} удалил лекарство {kwargs['pk']}")
        return super().delete(request, *args, **kwargs)

@login_required
def export_medicines_csv(request):    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="medicines.csv"'
    writer = csv.writer(response)
    writer.writerow(['ID', 'Название (Имя)', 'Описание', 'Цена'])
    for med in Medicine.objects.all():
        writer.writerow([med.id, med.name, med.description[:50], med.unit_price])
    return response

# PatientMedicine
class PatientMedicineListView(LoginRequiredMixin, ListView):
    model = PatientMedicine
    template_name = 'patientmedicines/list.html'  # Alohida template
    context_object_name = 'patient_medicines'

    def get_queryset(self):
        qs = super().get_queryset()
        if is_doctor(self.request.user):
            qs = qs.filter(patient__visit__doctor=self.request.user.doctor)
        return qs.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['export_url'] = '/patientmedicines/export/'
        return context

class PatientMedicineCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = PatientMedicine
    form_class = PatientMedicineForm
    template_name = 'patientmedicines/add.html'
    success_url = '/patientmedicines/'

    def test_func(self):
        return self.request.user.is_superuser or is_doctor(self.request.user)

    def form_valid(self, form):
        logger.info(f"Пользователь {self.request.user} назначил лекарство {form.instance.medicine.name} пациенту {form.instance.patient.id}")
        return super().form_valid(form)

class PatientMedicineUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = PatientMedicine
    form_class = PatientMedicineForm
    template_name = 'patientmedicines/edit.html'
    success_url = '/patientmedicines/'

    def test_func(self):
        obj = self.get_object()
        return (self.request.user.is_superuser or 
                (is_doctor(self.request.user) and obj.patient.visit_set.filter(doctor=self.request.user.doctor).exists()))

    def form_valid(self, form):
        logger.info(f"Пользователь {self.request.user} обновил назначение лекарства пациенту {form.instance.id}")
        return super().form_valid(form)

class PatientMedicineDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = PatientMedicine
    success_url = '/patientmedicines/'

    def test_func(self):
        obj = self.get_object()
        return (self.request.user.is_superuser or 
                (is_doctor(self.request.user) and obj.patient.visit_set.filter(doctor=self.request.user.doctor).exists()))

    def delete(self, request, *args, **kwargs):
        logger.info(f"Пользователь {request.user} удалил назначение лекарства пациенту {kwargs['pk']}")
        return super().delete(request, *args, **kwargs)

@login_required
def export_patientmedicines_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="patient_medicines.csv"'
    writer = csv.writer(response)
    writer.writerow(['ID', 'Пациент', 'Лекарство (Препарат)', 'Количество (Доза)', 'Дата'])
    for pm in PatientMedicine.objects.all():
        writer.writerow([pm.id, str(pm.patient), str(pm.medicine), pm.quantity, pm.prescribed_date])
    return response

# Auth
def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Group qo'shish uchun admin paneldan
            username = form.cleaned_data.get('username')
            messages.success(request, f'Пользователь {username} успешно создан. Войдите, пожалуйста.')
            logger.info(f"Новый пользователь {username} зарегистрировался")
            return redirect('login')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})
@login_required
def latest_visits_api(request):

    visits = (
        Visit.objects.select_related('patient', 'doctor')
        .order_by('-visit_datetime')[:5]
    )

    data = []
    for v in visits:
        data.append({
            'id': v.id,
            'patient': str(v.patient),
            'doctor': str(v.doctor),
            'datetime': v.visit_datetime.strftime("%d.%m.%Y %H:%M"),
            'status': v.status,
        })

    return JsonResponse({'visits': data})

@login_required
def logout(request):
    from django.contrib.auth import logout as auth_logout
    auth_logout(request)
    messages.info(request, "Вы вышли из системы.")
    return redirect('login')

class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'patients/profile.html'

    def get(self, request, *args, **kwargs):
        try:
            patient = Patient.objects.get(user=request.user)
        except Patient.DoesNotExist:
            messages.error(request, "Профиль пациента не найден.")
            return redirect('home')

        form = SetPasswordForm(user=request.user)
        return render(request, self.template_name, {'patient': patient, 'form': form})

    def post(self, request, *args, **kwargs):
        patient = Patient.objects.get(user=request.user)
        form = SetPPasswordForm(user=request.user, data=request.POST)

        if form.is_valid():
            new_password = form.cleaned_data['new_password1']
            user = request.user
            user.set_password(new_password)
            user.save()

            messages.success(request, "Пароль успешно изменён. Войдите снова.")
            return redirect('login')
        else:
            messages.error(request, "Ошибка при изменении пароля.")
        
        return render(request, self.template_name, {'patient': patient, 'form': form})
class PatientVisitsView(LoginRequiredMixin, ListView):
    model = Visit
    template_name = 'patients/visits.html'
    context_object_name = 'visits'

    def get_queryset(self):
    
        patient = getattr(self.request.user, 'patient', None)
        if not patient:
            return Visit.objects.none()
        return (
            Visit.objects.filter(patient=patient)
            .select_related('doctor__user')
            .order_by('-visit_datetime')
        )
class DoctorTestMixin(UserPassesTestMixin):

    def test_func(self):
        return self.request.user.is_authenticated and is_doctor(self.request.user)
    
class PrescribeMedicineView(LoginRequiredMixin, DoctorTestMixin, ListView):
    
    model = PatientMedicine
    template_name = 'doctors/pedmet.html'
    context_object_name = 'prescriptions'
    paginate_by = 10

    def get_queryset(self):
        return PatientMedicine.objects.select_related('patient', 'medicine').all().order_by('-prescribed_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PatientMedicineForm()
 
        context['all_patients'] = Patient.objects.all()
        context['all_medicines'] = Medicine.objects.all()
        return context

    def post(self, request, *args, **kwargs):
        action = request.POST.get('action')  
        
        if action == 'delete':
            prescription_id = request.POST.get('prescription_id')
            prescription = get_object_or_404(PatientMedicine, id=prescription_id)
            if hasattr(request.user, 'doctor'): 
                prescription.delete()
                messages.success(request, 'Назначение удалено!')
            else:
                messages.error(request, 'У вас нет прав на удаление.')
            return HttpResponseRedirect(request.path)  
        
        elif action == 'update':
            prescription_id = request.POST.get('prescription_id')
            prescription = get_object_or_404(PatientMedicine, id=prescription_id)
            patient_id = request.POST.get('patient')
            medicine_id = request.POST.get('medicine')
            quantity = request.POST.get('quantity')
            
            try:
                prescription.patient_id = patient_id
                prescription.medicine_id = medicine_id
                prescription.quantity = int(quantity)
                prescription.save()
                messages.success(request, 'Назначение обновлено!')
                return HttpResponseRedirect(request.path)
            except ValueError:
                messages.error(request, 'Ошибка при обновлении: неверные данные.')
            except Exception as e:
                messages.error(request, f'Ошибка при обновлении: {str(e)}')
            
           
            context = self.get_context_data()
            return self.render_to_response(context)
        
        else:  
            form = PatientMedicineForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Лекарство успешно назначено!')
                return HttpResponseRedirect(request.path)
            else:
                context = self.get_context_data()
                context['form'] = form
                return self.render_to_response(context)
            

def landing(request):
    today = timezone.now().date()
    visits = Visit.objects.filter(visit_datetime__date=today)
    doctors = Doctor.objects.all()
    return render(request, 'landing.html', {'doctors': doctors, 'visits': visits})

def create_visit(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone = request.POST.get('phone')
        doctor_id = request.POST.get('doctor')

        patient, _ = Patient.objects.get_or_create(
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            defaults={'birth_date': '2000-01-01', 'gender': 'M'}
        )

        Visit.objects.create(
            patient=patient,
            doctor_id=doctor_id,
            diagnosis='',
            treatment_plan=''
        )
        return redirect('landing')

    return redirect('landing')
def reception_patients(request):

    patients = Patient.objects.all().order_by('-created_at')
    form = PatientForm()

    if request.method == 'POST':
        form = PatientForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('reception_patients')

    return render(request, 'reception/patient.html', {'patients': patients, 'form': form})



def add_patient(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        birth_date = request.POST.get('birth_date')
        gender = request.POST.get('gender')
        phone = request.POST.get('phone')
        address = request.POST.get('address')

        if first_name and last_name:
            Patient.objects.create(
                first_name=first_name,
                last_name=last_name,
                birth_date=birth_date,
                gender=gender,
                phone=phone,
                address=address
            )
            messages.success(request, "✅ Успешно добавлен пациент.")
            return redirect('reception_patients')
        else:
            messages.error(request, "⚠️ Имя и фамилия обязательны для заполнения!")

    return render(request, 'reception/add_patient.html')



def edit_patient(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    if request.method == 'POST':
        patient.first_name = request.POST.get('first_name')
        patient.last_name = request.POST.get('last_name')
        patient.birth_date = request.POST.get('birth_date')
        patient.gender = request.POST.get('gender')
        patient.phone = request.POST.get('phone')
        patient.address = request.POST.get('address')
        patient.save()
        messages.success(request, "📝 Информация о пациенте обновлена.")

        return redirect('reception_patients')
    return render(request, 'reception/edit_patient.html', {'patient': patient})





def reception_visits(request):
    visits = Visit.objects.select_related('patient', 'doctor').order_by('-visit_datetime')
    return render(request, 'reception/visit.html', {'visits': visits})


def add_visit(request):
    patients = Patient.objects.all()
    doctors = Doctor.objects.all()

    if request.method == 'POST':
        patient_id = request.POST.get('patient')
        doctor_id = request.POST.get('doctor')
        diagnosis = request.POST.get('diagnosis')
        treatment_plan = request.POST.get('treatment_plan')
        result = request.POST.get('result')
        status = request.POST.get('status')

        if patient_id and doctor_id:
            Visit.objects.create(
                patient_id=patient_id,
                doctor_id=doctor_id,
                diagnosis=diagnosis,
                treatment_plan=treatment_plan,
                result=result,
                status=status
            )
            messages.success(request, "✅ Регистрация успешно добавлена.")
            return redirect('reception_visits')
        else:
            messages.error(request, "⚠️ Выберите пациента и врача!")

    context = {
        'patients': patients,
        'doctors': doctors,
    }
    return render(request, 'reception/add_visit.html', context)


def edit_visit(request, pk):
    visit = get_object_or_404(Visit, pk=pk)
    patients = Patient.objects.all()
    doctors = Doctor.objects.all()

    if request.method == 'POST':
        visit.patient_id = request.POST.get('patient')
        visit.doctor_id = request.POST.get('doctor')
        visit.diagnosis = request.POST.get('diagnosis')
        visit.treatment_plan = request.POST.get('treatment_plan')
        visit.result = request.POST.get('result')
        visit.status = request.POST.get('status')
        visit.save()
        messages.success(request, "🩺 Информация о пациенте обновлена.")
        return redirect('reception_visits')

    context = {
        'visit': visit,
        'patients': patients,
        'doctors': doctors,
    }
    return render(request, 'reception/edit_visit.html', context)


def reception_patient_detail(request, pk):

    patient = get_object_or_404(Patient, pk=pk)

    visits = Visit.objects.filter(patient=patient).order_by('-visit_datetime')
    
    return render(request, 'reception/patient_detail.html', {
        'patient': patient,
        'visits': visits,
    })

@login_required
def reception_profile(request):
    return render(request, 'reception/profile.html')

@login_required
def reception_change_password(request):
    from django.contrib.auth import update_session_auth_hash
    if request.method == 'POST':
        old_pass = request.POST.get('old_password')
        new1 = request.POST.get('new_password1')
        new2 = request.POST.get('new_password2')

        if not request.user.check_password(old_pass):
            messages.error(request, "Ошибка в текущем пароле!")
            return redirect('reception_profile')

        if new1 != new2:
            messages.error(request, "Новые пароли не совпадают!")
            return redirect('reception_profile')

        request.user.set_password(new1)
        request.user.save()
        update_session_auth_hash(request, request.user)
        messages.success(request, "Пароль успешно изменен ✅")
        return redirect('reception_profile')
    
def reception_list(request):
    receptions = Reception.objects.select_related('user').all()

    return render(request, 'reception/list.html', {'receptions': receptions})





def add_reception(request):
    from django.core.exceptions import ValidationError
    from django.contrib.auth.models import User 
    if request.method == 'POST':

   
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        email = request.POST.get('email', '').strip()  
  

        errors = []
        if not first_name:
            errors.append("Имя обязательно для заполнения!")
        if not last_name:
            errors.append("Фамилия обязательно для заполнения!")
        if not username:
            errors.append("Логин обязательно для заполнения!")
        if not password:
            errors.append("Пароль обязательно для заполнения!")

        if errors:
            context = {
                'errors': errors,
                'first_name': first_name,
                'last_name': last_name,
                'username': username,
                'email': email,
                'password': ''  
            }
            return render(request, 'reception/add.html', context)
        
        try:
     
            user = User.objects.create_user(
                username=username,
                email=email or '',  
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            
          
            reception = Reception.objects.create(
                user=user,
                first_name=first_name,  
                last_name=last_name,   
                plain_password=password  
            )
            
            
            messages.success(request, f'Вы написали! Логин: {username} Пароль: {password}')
            return redirect('reception_list')
            
        except ValidationError as e:
           
            errors.append(f"Ошибка при сохранении: {str(e)}")
            return render(request, 'reception/add.html', {
                'errors': errors,
                'first_name': first_name,
                'last_name': last_name,
                'username': username,
                'email': email,
                'password': ''
            })
        except Exception as e:
          # Например, username уже существует
            errors.append(f"Неправильная ошибка: {str(e)}")
            return render(request, 'reception/add.html', {
                'errors': errors,
                'first_name': first_name,
                'last_name': last_name,
                'username': username,
                'email': email,
                'password': ''
            })
    
    return render(request, 'reception/add.html')

def delete_reception(request, pk):
    reception = get_object_or_404(Reception, pk=pk)
    user = reception.user
    reception.delete()
    user.delete()
    messages.success(request, "Реконструкция приема удалена!")
    return redirect('reception_list')


def edit_reception(request, pk):
    from .forms import ReceptionEditForm
    reception = get_object_or_404(Reception, pk=pk)
    user = reception.user

    if request.method == 'POST':
        form = ReceptionEditForm(request.POST, instance=reception)
        if form.is_valid():
            form.save()
            messages.success(request, 'Данные оператора успешно обновлены!')
            return redirect('reception_list')
    else:
        form = ReceptionEditForm(instance=reception, initial={
            'first_name': user.first_name,
            'last_name': user.last_name,
            'username': user.username,
        })

    return render(request, 'reception/edit.html', {'form': form, 'reception': reception})


from django.template.loader import render_to_string

def department_list(request):
    departments = Department.objects.all()
    return render(request, 'department/department_list.html', {'departments': departments})

def save_department_form(request, form, template_name):
    data = {}
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            data['form_is_valid'] = True
            departments = Department.objects.all()
            data['html_department_list'] = render_to_string('department/includes/partial_department_list.html', {
                'departments': departments
            })
        else:
            data['form_is_valid'] = False
    context = {'form': form}
    data['html_form'] = render_to_string(template_name, context, request=request)
    return JsonResponse(data)

def department_create(request):
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
    else:
        form = DepartmentForm()
    return render(request,'department/add.html',{'form':form})
def department_add(request):
    if request.method=="POST":
        form=DepartmentForm(request.POST)
        if form.is_valid:
            form.save()
    return redirect('doctor_add')

def department_update(request, pk):
    department = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=department)
    else:
        form = DepartmentForm(instance=department)
    return save_department_form(request, form, 'department/includes/partial_department_update.html')

def department_delete(request, pk):
    department = get_object_or_404(Department, pk=pk)
    data = {}
    if request.method == 'POST':
        department.delete()
        data['form_is_valid'] = True
        departments = Department.objects.all()
        data['html_department_list'] = render_to_string('department/includes/partial_department_list.html', {
            'departments': departments
        })
    else:
        context = {'department': department}
        data['html_form'] = render_to_string('department/includes/partial_department_delete.html', context, request=request)
    return JsonResponse(data)
