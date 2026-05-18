from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import random
import string

class AccountType(models.TextChoices):
    SAVINGS = 'SAVINGS', 'Savings Account'
    CURRENT = 'CURRENT', 'Current Account'
    FIXED_DEPOSIT = 'FD', 'Fixed Deposit Account'

class ApplicationStatus(models.TextChoices):
    PENDING = 'PENDING', 'Pending'
    APPROVED = 'APPROVED', 'Approved'
    REJECTED = 'REJECTED', 'Rejected'

class Gender(models.TextChoices):
    MALE = 'M', 'Male'
    FEMALE = 'F', 'Female'
    OTHER = 'O', 'Other'

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
    application_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=10,
        choices=ApplicationStatus.choices,
        default=ApplicationStatus.PENDING
    )
    
    # Personal Information
    full_name = models.CharField(max_length=200)
    father_name = models.CharField(max_length=200)
    mother_name = models.CharField(max_length=200)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=Gender.choices)
    nid_number = models.CharField(max_length=20, unique=True, db_index=True)
    
    # Contact Information
    mobile_number = models.CharField(max_length=15)
    email = models.EmailField(blank=True, null=True)
    
    # Address
    present_address = models.TextField()
    permanent_address = models.TextField()
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=10)
    
    # Account Details
    account_type = models.CharField(max_length=20, choices=AccountType.choices)
    initial_deposit = models.DecimalField(max_digits=12, decimal_places=2)
    
    # Documents
    photograph = models.ImageField(upload_to='applicant_photos/')
    nid_copy = models.FileField(upload_to='nid_copies/')
    signature = models.ImageField(upload_to='signatures/')
    
    # Nominee Information
    nominee_name = models.CharField(max_length=200)
    nominee_relation = models.CharField(max_length=100)
    nominee_nid = models.CharField(max_length=20)
    nominee_mobile = models.CharField(max_length=15)
    
    # Approval Details
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
        return f"{self.application_number} - {self.full_name}"
    
    def is_expired(self):
        """Check if application is older than 20 days and still pending"""
        if self.status == ApplicationStatus.PENDING:
            expiry_date = self.application_date + timedelta(days=20)
            return timezone.now() > expiry_date
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