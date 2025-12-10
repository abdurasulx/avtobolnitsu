from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Patient, Doctor, Visit, LabTest, PatientMedicine
from .forms import AppointmentForm

@login_required
def patient_prescriptions(request):
    """View for patient to see their prescriptions/medicines"""
    patient = getattr(request.user, 'patient', None)
    if not patient:
        messages.error(request, "Профиль пациента не найден.")
        return redirect('dashboard')
    
    prescriptions = PatientMedicine.objects.filter(patient=patient).select_related('medicine').order_by('-prescribed_date')
    return render(request, 'patients/prescriptions.html', {'prescriptions': prescriptions})

@login_required
def patient_labtests(request):
    """View for patient to see their lab tests"""
    patient = getattr(request.user, 'patient', None)
    if not patient:
        messages.error(request, "Профиль пациента не найден.")
        return redirect('dashboard')
    
    labtests = LabTest.objects.filter(patient=patient).order_by('-result_date')
    return render(request, 'patients/labtests.html', {'labtests': labtests})

@login_required
def patient_book_appointment(request):
    """View for patient to book an appointment for self or another patient"""
    
    current_patient = getattr(request.user, 'patient', None)
    if not current_patient:
        messages.error(request, "Профиль пациента не найден.")
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            booking_for_self = form.cleaned_data.get('booking_for_self', True)
            
            if booking_for_self:
                patient = current_patient
            else:
              
                patient, created = Patient.objects.get_or_create(
                    first_name=form.cleaned_data['other_first_name'],
                    last_name=form.cleaned_data['other_last_name'],
                    phone=form.cleaned_data['other_phone'],
                    defaults={
                        'birth_date': form.cleaned_data['other_birth_date'],
                        'gender': form.cleaned_data['other_gender'],
                     
                    }
                )
            
            visit = form.save(commit=False)
            visit.patient = patient
            visit.diagnosis = '' 
            visit.treatment_plan = '' 
            visit.save()
            
            messages.success(request, "Запись успешно создана!")
            return redirect('dashboard')
    else:
        form = AppointmentForm()
    
    doctors = Doctor.objects.all()
    return render(request, 'patients/book_appointment.html', {
        'form': form,
        'doctors': doctors,
        'current_patient': current_patient
    })
