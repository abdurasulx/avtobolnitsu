from django.db import models
from django.contrib.auth.models import User
from .func import make_login, make_password, to_latin


class Reception(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='reception')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    plain_password = models.CharField(max_length=255, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.pk and not self.user:
            username = make_login(f"{self.first_name}{self.last_name}")
            password = f"{self.first_name}{self.last_name}2024!"
            self.user = User.objects.create_user(
                username=username,
                first_name=self.first_name,
                last_name=self.last_name,
                password=password
            )
            self.plain_password = password
        super().save(*args, **kwargs)
class Department(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
    specialty = models.CharField(max_length=150)
    detail = models.TextField(blank=True, null=True)
    img = models.ImageField(upload_to='doctor_images/', blank=True, null=True)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.specialty}"

class Patient(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    birth_date = models.DateField()
    gender = models.CharField(max_length=10, choices=[('M', 'Мужской'), ('F', 'женский')])
    phone = models.CharField(max_length=30)
    address = models.TextField(blank=True)
    user= models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)
    insurance_number = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    plain_password = models.CharField(max_length=255, blank=True, null=True)

    

    def save(self, *args, **kwargs):
        # Faqat yangi obyekt yaratilganda (update emas) va user yo'q bo'lsa
        if not self.pk and not self.user:  # self.pk None bo'lsa - yangi obyekt
            username = make_login(to_latin(f"{self.first_name}{self.last_name}"))
            password = f"{self.first_name}{self.last_name}2024!"
      

            self.user = User.objects.create_user(
                username=username,
                first_name=self.first_name,
                last_name=self.last_name,
                password=password  # make_password o'rniga to'g'ridan-to'g'ri password uzating (create_user hash qiladi)

            )
        
            self.plain_password = password  # Oddiy parolni saqlaymiz
        
        super().save(*args, **kwargs)  # Standart save ni chaqiring

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

from django.utils import timezone

class Visit(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True)
    diagnosis = models.TextField()
    treatment_plan = models.TextField()
    visit_datetime = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=15, choices=[('in_progress', 'В процессе'), ('ended', 'Завершен')], default='in_progress')
    result= models.CharField(max_length=255, choices=[('hospital', 'Стационарное лечение (в палате)'),('home', ' Домашнее лечение'),('none', 'Не подлежит лечению'),('in_progress', 'В процессе')], blank=True, null=True,default='in_progress')

    def __str__(self):
        return f"{self.patient} - {self.visit_datetime}"

class LabTest(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    test_type = models.CharField(max_length=150)
    result = models.TextField()
    result_date = models.DateField()

    def __str__(self):
        return f"{self.patient} - {self.test_type}"

class Medicine(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name

class PatientMedicine(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    medicine = models.ForeignKey(Medicine, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    prescribed_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient} - {self.medicine}"


