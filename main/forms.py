from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Department, Doctor, Patient, Visit, LabTest, Medicine, PatientMedicine, Reception
from django.contrib.auth.password_validation import validate_password

class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['first_name', 'last_name', 'birth_date', 'gender', 'phone', 'address', 'plain_password', 'insurance_number']
        labels = {
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'birth_date': 'Дата рождения',
            'gender': 'Пол',
            'phone': 'Телефон',
            'address': 'Адрес',
            'insurance_number': 'Номер страховки',
            'plain_password': 'Пароль',
        }
        
        widgets = {
            'birth_date': forms.DateInput(
                format='%Y-%m-%d',
                attrs={'type': 'date'}
            ),
            'phone': forms.TextInput(attrs={'placeholder': '+7 (495) 539-55-19'}),
        }

class DoctorForm(forms.ModelForm):
    # User bilan bog'liq maydonlar
    username = forms.CharField(label="Логин", max_length=150)
    first_name = forms.CharField(label="Имя", max_length=150)
    last_name = forms.CharField(label="Фамилия", max_length=150)
    email = forms.EmailField(label="Эл. почта")

    class Meta:
        model = Doctor
        fields = [
            'username', 'first_name', 'last_name', 'email',
            'department', 'specialty', 'detail', 'img'
        ]
        labels = {
            'department': 'Отделение',
            'specialty': 'Специальность',
            'detail': 'Информация о враче',
            'img': 'Фото врача',
        }
        widgets = {
            'specialty': forms.TextInput(attrs={
                'placeholder': 'Кардиология',
                'class': 'form-control'
            }),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'detail': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Опыт работы, достижения и т.д.'
            }),
        }

    def __init__(self, *args, **kwargs):
        """Tahrirlash paytida mavjud user ma'lumotlarini formga to'ldirib qo'yish."""
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            user = self.instance.user
            self.fields['username'].initial = user.username
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['email'].initial = user.email
            self.fields['img'].initial = self.instance.img

    def save(self, commit=True):
        """Yaratish va yangilashni to'g'ri ajratadi."""
        doctor = super().save(commit=False)

        # Agar mavjud doctorni tahrirlayotgan bo'lsak
        if doctor.pk:
            doctor.img = self.cleaned_data['img']
            user = doctor.user
            user.username = self.cleaned_data['username']
            user.first_name = self.cleaned_data['first_name']
            user.last_name = self.cleaned_data['last_name']
            user.email = self.cleaned_data['email']
        
            user.save()
        else:
            # Yangi doctor uchun yangi user yaratish
            if User.objects.filter(username=self.cleaned_data['username']).exists():
                raise forms.ValidationError("❌ Этот логин уже используется.")
            user = User.objects.create_user(
                username=self.cleaned_data['username'],
                first_name=self.cleaned_data['first_name'],
                last_name=self.cleaned_data['last_name'],
                email=self.cleaned_data['email'],
                password='12345'  # ⚠️ vaqtinchalik parol
            )
            doctor.user = user

        if commit:
            doctor.save()
        return doctor

class VisitForm(forms.ModelForm):
    class Meta:
        model = Visit
        fields = ['patient', 'doctor', 'diagnosis', 'status', 'treatment_plan', 'result', 'visit_datetime']
        labels = {
            'patient': 'Пациент',
            'doctor': 'Врач',
            'diagnosis': 'Диагноз',
            'status': 'Статус',
            'treatment_plan': 'План лечения',
            'result': 'Результат',
            'visit_datetime': 'Дата и время посещения',
        }
        widgets = {
            'diagnosis': forms.Textarea(attrs={'rows': 3}),
            'treatment_plan': forms.Textarea(attrs={'rows': 3}),
            'visit_datetime': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        }

class LabTestForm(forms.ModelForm):
    class Meta:
        model = LabTest
        fields = ['patient', 'test_type', 'result', 'result_date']
        labels = {
            'patient': 'Пациент',
            'test_type': 'Тип анализа',
            'result': 'Результат',
            'result_date': 'Дата результата',
        }
        widgets = {
            'result_date': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
            'result': forms.Textarea(attrs={'rows': 3}),
        }

class MedicineForm(forms.ModelForm):
    class Meta:
        model = Medicine
        fields = ['name', 'description', 'unit_price']
        labels = {
            'name': 'Название',
            'description': 'Описание',
            'unit_price': 'Цена за единицу',
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class PatientMedicineForm(forms.ModelForm):
    class Meta:
        model = PatientMedicine
        fields = ['patient', 'medicine', 'quantity']
        labels = {
            'patient': 'Пациент',
            'medicine': 'Лекарство',
            'quantity': 'Количество',
        }
        widgets = {
            'quantity': forms.NumberInput(attrs={'min': 1}),
        }

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
        labels = {
            'username': 'Имя пользователя',
            'email': 'Email',
            'password1': 'Пароль',
            'password2': 'Подтверждение пароля',
        }

    def save(self, commit=True):
        user = super(SignUpForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user

class SetPasswordForm(forms.Form):
    new_password1 = forms.CharField(
        label="Новый пароль",
        widget=forms.PasswordInput(attrs={'placeholder': 'Введите новый пароль', 'class': 'form-control'})
    )
    new_password2 = forms.CharField(
        label="Подтверждение нового пароля",
        widget=forms.PasswordInput(attrs={'placeholder': 'Подтвердите новый пароль', 'class': 'form-control'})
    )

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("new_password1")
        password2 = cleaned_data.get("new_password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Пароли не совпадают.")

        return cleaned_data

class SetPPasswordForm(forms.Form):
    new_password1 = forms.CharField(
        label="Новый пароль",
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Введите новый пароль',
            'class': 'form-control'
        })
    )
    new_password2 = forms.CharField(
        label="Подтверждение нового пароля",
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Подтвердите новый пароль',
            'class': 'form-control'
        })
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("new_password1")
        password2 = cleaned_data.get("new_password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Пароли не совпадают.")

        # optional: Django parol tekshiruvlarini ishlatish
        validate_password(password1, self.user)

        return cleaned_data

class ReceptionForm(forms.ModelForm):
    first_name = forms.CharField(label='Имя', required=True)
    last_name = forms.CharField(label='Фамилия', required=True)
    username = forms.CharField(label='Логин', required=True)
    # email = forms.EmailField(label='Email', required=True)  # User uchun majburiy
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput, required=True)

    class Meta:
        model = Reception
        fields = []  # Reception'ga qo'shimcha maydon yo'q, user yaratamiz

    def save(self, commit=True):
        # Yangi user yaratish
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            # email=self.cleaned_data['email'],
            password=self.cleaned_data['password'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name']
        )
        # Reception yaratish va user bilan bog'lash
        reception = super().save(commit=False)
        reception.user = user
        if commit:
            reception.save()
        return reception

class ReceptionEditForm(forms.ModelForm):
    first_name = forms.CharField(label='Имя')
    last_name = forms.CharField(label='Фамилия')
    username = forms.CharField(label='Логин')
    password = forms.CharField(label='Новый пароль', required=False, widget=forms.PasswordInput)

    class Meta:
        model = Reception
        fields = []  # Reception modelida qo'shimcha maydon yo'q

    def save(self, commit=True):
        reception = super().save(commit=False)
        user = reception.user
        user.username = self.cleaned_data['username']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']

        if self.cleaned_data['password']:
            user.set_password(self.cleaned_data['password'])

        if commit:
            user.save()
            reception.save()
        return reception

class DepartmentForm(forms.ModelForm):
    
    class Meta:
  
        model = Department

        fields = ['name', 'description']
        labels = {
            'name': 'Название отдела',
            'description': 'Описание',     
        }
     
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Название отдела'  
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control', 
                'placeholder': 'Описание' 
            }),
        }

# New form for patient appointment booking
class AppointmentForm(forms.ModelForm):
    booking_for_self = forms.BooleanField(
        required=False, 
        initial=True,
        label='Записываю себя',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    # Fields for booking another patient
    other_first_name = forms.CharField(
        required=False, 
        max_length=100,
        label='Имя пациента',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    other_last_name = forms.CharField(
        required=False, 
        max_length=100,
        label='Фамилия пациента',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    other_phone = forms.CharField(
        required=False, 
        max_length=30,
        label='Телефон пациента',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+7 (495) 539-55-19'})
    )
    other_birth_date = forms.DateField(
        required=False,
        label='Дата рождения пациента',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    other_gender = forms.ChoiceField(
        required=False,
        choices=[('M', 'Мужской'), ('F', 'Женский')],
        label='Пол пациента',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = Visit
        fields = ['doctor', 'visit_datetime']
        labels = {
            'doctor': 'Врач',
            'visit_datetime': 'Дата и время приёма',
        }
        widgets = {
            'doctor': forms.Select(attrs={'class': 'form-control'}),
            'visit_datetime': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        booking_for_self = cleaned_data.get('booking_for_self')
        
        if not booking_for_self:
            # Validate other patient fields
            if not cleaned_data.get('other_first_name'):
                raise forms.ValidationError('Имя пациента обязательно')
            if not cleaned_data.get('other_last_name'):
                raise forms.ValidationError('Фамилия пациента обязательна')
            if not cleaned_data.get('other_phone'):
                raise forms.ValidationError('Телефон пациента обязателен')
            if not cleaned_data.get('other_birth_date'):
                raise forms.ValidationError('Дата рождения пациента обязательна')
        
        return cleaned_data