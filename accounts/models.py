from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import random
import string
from django.core.validators import MaxValueValidator, MinValueValidator

class AccountType(models.TextChoices):
    SAVINGS = 'SAVINGS', 'সঞ্চয়ী'
    CURRENT = 'CURRENT', 'চলতি'
    SND = 'SND', 'এসএনডি'
    FC = 'FC', 'এফসি'
    RFCD = 'RFCD', 'আরএফসিডি'
    NFCD = 'NFCD', 'এনএফসিডি'
    OTHERS = 'OTHERS', 'অন্যান্য'

class CurrencyType(models.TextChoices):
    BDT = 'BDT', 'টাকা'
    EURO = 'EURO', 'ইউরো'
    POUND = 'POUND', 'পাউন্ড'
    USD = 'USD', 'ডলার'
    OTHERS = 'OTHERS', 'অন্যান্য'

class AccountProcedureType(models.TextChoices):
    SINGLE = 'SINGLE', 'এককভাবে'
    COMBINED = 'COMBINED', 'যৌথভাবে'
    ANY_ONE = 'ANY_ONE', 'যে কোনো একজন'
    ANY_ONE_or_LIVING = 'ANY_ONE_or_LIVING', 'যে কোনো একজন অথবা জীবিতজন'
    OTHERS = 'OTHERS', 'অন্যান্য'


class ApplicationStatus(models.TextChoices):
    PENDING = 'PENDING', 'Pending'
    APPROVED = 'APPROVED', 'Approved'
    REJECTED = 'REJECTED', 'Rejected'

class Gender(models.TextChoices):
    MALE = 'M', 'Male'
    FEMALE = 'F', 'Female'
    OTHER = 'O', 'Other'
class ResidentStatus(models.TextChoices):
    RESIDENT = 'RESIDENT', 'রেসিডেন্ট'
    NON_RESIDENT = 'NON_RESIDENT', 'নন-রেসিডেন্ট'

def generate_application_number():
    """Generate unique application number"""
    timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
    random_str = ''.join(random.choices(string.digits, k=4))
    return f'APP{timestamp}{random_str}'

def generate_account_number():
    """Generate unique account number"""
    timestamp = timezone.now().strftime('%Y%m%d')
    random_str = ''.join(random.choices(string.digits, k=8))
    return f'{timestamp}{random_str}'

class AccountApplication(models.Model):
    # Application Details
    application_number = models.CharField(max_length=30, unique=True, editable=False)
    application_date = models.DateField(auto_now_add=True)
    status = models.CharField(
        max_length=10,
        choices=ApplicationStatus.choices,
        default=ApplicationStatus.PENDING
    )
    #account_information
    account_title_Bng = models.CharField(max_length=255)
    account_title_Eng = models.CharField(max_length=255)
    account_type = models.CharField(max_length=20, choices=AccountType.choices)
    currency_type = models.CharField(max_length=20, choices=CurrencyType.choices)
    account_procedure_type = models.CharField(max_length=20, choices=AccountProcedureType.choices)
    initial_deposit = models.DecimalField(max_digits=12, decimal_places=2)
    initial_deposit_in_number = models.CharField(max_length=255, null=True, blank=True)
    # Personal Information
    full_name_bng = models.CharField(max_length=200)
    full_name_eng = models.CharField(max_length=200)
    date_of_birth = models.DateField()
    father_name = models.CharField(max_length=200)
    mother_name = models.CharField(max_length=200)
    spouse_name = models.CharField(max_length=200, null=True, blank=True)
    nationality = models.CharField(max_length=50)
    gender = models.CharField(max_length=1, choices=Gender.choices)
    resident_status = models.CharField(max_length=30, choices=ResidentStatus.choices)
    service = models.CharField(max_length=60)
    monthly_income = models.DecimalField(max_digits=15, decimal_places=2)
    income_source = models.CharField(max_length=200)
    TIN = models.CharField(
        max_length=12,
        null=True,
        blank=True
    )

    # present Address
    pre_vill = models.CharField(max_length=200, null=True, blank=True)
    pre_post_office = models.CharField(max_length=50, null=True, blank=True)
    pre_ps = models.CharField(max_length=100, null=True, blank=True)
    pre_district = models.CharField(max_length=100, null=True, blank=True)
    pre_phone = models.CharField(max_length=20, null=True, blank=True)
    pre_email = models.EmailField(max_length=80, null=True, blank=True)
    # permanent Address
    per_vill = models.CharField(max_length=200, null=True, blank=True)
    per_post_office = models.CharField(max_length=50, null=True, blank=True)
    per_ps = models.CharField(max_length=100, null=True, blank=True)
    per_district = models.CharField(max_length=100, null=True, blank=True)
    per_phone = models.CharField(max_length=20, null=True, blank=True)
    per_email = models.EmailField(max_length=80, null=True, blank=True)
    
    #identification papers

    nid_number = models.CharField(max_length=20, null=True, blank=True)
    # pp_number = models.CharField(max_length=20, null=True, blank=True)
    # bc_number = models.CharField(max_length=20, null=True, blank=True)
    other_doc_name = models.CharField(max_length=200, null=True, blank=True)
    other_number = models.CharField(max_length=20, null=True, blank=True)
    reference_person_name = models.CharField(max_length=200, null=True, blank=True)
    reference_doc_name = models.CharField(max_length=200, null=True, blank=True)
    reference_number = models.CharField(max_length=20, null=True, blank=True)
    
    # Nominee Information
    nominee_name1 = models.CharField(max_length=200, null=True, blank=True)
    nominee_DOB1 = models.DateField(null=True, blank=True)
    nominee_address1 = models.TextField(null=True, blank=True)
    nominee_relation1 = models.CharField(max_length=100, null=True, blank=True)
    nominee_nid1 = models.CharField(max_length=20, null=True, blank=True)
    nominee_percentage1 = models.CharField(max_length=15, null=True, blank=True)
    nominee_other_doc_name1 = models.CharField(max_length=200, null=True, blank=True)
    nominee_other_number1 = models.CharField(max_length=20, null=True, blank=True)
    
    nominee_name2 = models.CharField(max_length=200, null=True, blank=True)
    nominee_DOB2 = models.DateField(null=True, blank=True)
    nominee_address2 = models.TextField(null=True, blank=True)
    nominee_relation2 = models.CharField(max_length=100, null=True, blank=True)
    nominee_nid2 = models.CharField(max_length=20, null=True, blank=True)
    nominee_percentage2 = models.CharField(max_length=15, null=True, blank=True)
    nominee_other_doc_name2 = models.CharField(max_length=200, null=True, blank=True)
    nominee_other_number2 = models.CharField(max_length=20, null=True, blank=True)
    #under age nominee
    nominee_name3 = models.CharField(max_length=200, null=True, blank=True)
    nominee_present_address3 = models.TextField(null=True, blank=True)
    nominee_permanent_address3 = models.TextField(null=True, blank=True)
    nominee_other_doc_name3 = models.CharField(max_length=200, null=True, blank=True)
    nominee_other_number3 = models.CharField(max_length=20, null=True, blank=True)
    nominee_relation3 = models.CharField(max_length=100, null=True, blank=True)
    nominee_phone3 = models.CharField(max_length=20, null=True, blank=True)

    #other service
    # debit_card checkbox choice
    debit_card = models.BooleanField(default=False)
    debit_card_delivery_branch = models.CharField(max_length=200, null=True, blank=True)
    
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_applications'
    )
    approval_date = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True, null=True)
    
    # Account Number (generated after approval)
    account_number = models.CharField(max_length=20, unique=True, null=True, blank=True)
    
    class Meta:
        ordering = ['-application_date']
        indexes = [
            models.Index(fields=['nid_number']),
            models.Index(fields=['application_number']),
            models.Index(fields=['account_number']),
            models.Index(fields=['status', 'application_date']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.application_number:
            self.application_number = generate_application_number()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.application_number} - {self.account_title_Eng}"
    
    def is_expired(self):
        """Check if application is older than 20 days and still pending"""
        if self.status == ApplicationStatus.PENDING:
            expiry_date = self.application_date + timedelta(days=30)
            return timezone.localdate() > expiry_date
        return False
    
    def approve(self, user):
        """Approve the application"""
        self.status = ApplicationStatus.APPROVED
        self.approved_by = user
        self.approval_date = timezone.now()
        self.account_number = generate_account_number()
        self.save()
    
    def reject(self, user, reason):
        """Reject the application"""
        self.status = ApplicationStatus.REJECTED
        self.approved_by = user
        self.approval_date = timezone.now()
        self.rejection_reason = reason
        self.save()

class ApplicationLog(models.Model):
    """Track all actions on applications"""
    application = models.ForeignKey(
        AccountApplication,
        on_delete=models.CASCADE,
        related_name='logs'
    )
    action = models.CharField(max_length=50)
    performed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.application.application_number} - {self.action}"