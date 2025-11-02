from rest_framework import serializers
from .models import Patients, Insurance, Doctors, bank_infomation


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patients
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class InsuranceSerializer(serializers.ModelSerializer):
    # show patient details when reading, accept patient_id when writing
    patient = PatientSerializer(source='patient_id', read_only=True)
    patient_id = serializers.PrimaryKeyRelatedField(
        queryset=Patients.objects.all(), write_only=True
    )

    class Meta:
        model = Insurance
        # explicit field list gives more control than '__all__'
        fields = ('id', 'patient', 'patient_id', 'insurance_number', 'expixry_date')


class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctors
        fields = '__all__'


class BankInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = bank_infomation
        fields = '__all__'
