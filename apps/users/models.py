from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

# Create your models here.

class Patients(models.Model):
    national_id = models.CharField(max_length=12, unique=True)
    full_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10, choices=[('Nam', 'Nam'), ('Nữ', 'Nữ')])
    phone = PhoneNumberField(region="VN")
    ward = models.CharField(max_length=50)
    district = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    occupation = models.CharField(max_length=100)
    ethnicity = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.national_id
    
class Insurance(models.Model):
    patient_id = models.ForeignKey(Patients, on_delete=models.CASCADE)
    insurance_number = models.CharField(max_length=30, unique=True)
    expixry_date = models.DateField()

    def __str__(self):
       return self.patient_id

class Doctors(models.Model):
    doctor_id = models.CharField(max_length=20, unique=True)
    full_name = models.CharField(max_length=100)
    specialization = models.CharField(max_length=100)
    phone = PhoneNumberField(region="VN")
    email = models.EmailField()
    user_id = models.CharField(max_length=20)

    def __str__(self):
        return self.doctor_id

class bank_infomation(models.Model):
    bank_id = models.CharField(max_length=20, unique=True)
    bank_name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=30)
    def __str__(self):
        return self.bank_id
