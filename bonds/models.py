from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.models import User

from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from .utils import generate_WEB_application_no, generate_USDB_application_no
from num2words import num2words

# class ApplicationStatus(models.TextChoices):
#     PENDING = 'PENDING', 'Pending'
#     APPROVED = 'APPROVED', 'Approved'
#     REJECTED = 'REJECTED', 'Rejected'
class ApplicationStatus(models.TextChoices):
    PENDING = 'PENDING', 'Pending'
    APPROVED = 'APPROVED', 'Approved'
    REJECTED = 'REJECTED', 'Rejected'
class USD_BondChice(models.TextChoices):
    # Select_One = '*Select*', '*Select any of the Bond*'
    USD_INVESTMENT_BOND = 'US DOLLAR INVESTMENT BOND', 'US DOLLAR INVESTMENT BOND'
    USD_PREMIUM_BOND = 'US DOLLAR PREMIUM BOND', 'US DOLLAR PREMIUM BOND'
class CURRENCY_CHOICE(models.TextChoices):
    USD = 'USD','USD'
    BDT = 'BDT','BDT'

class WageEarnersBond(models.Model):
    application_no = models.CharField(max_length=30, unique=True)
    application_date = models.DateField(auto_now_add=True)
    applicant_name = models.CharField(max_length=250)
    nominee_name = models.CharField(max_length=250, blank=True)
    applicant_address = models.TextField()
    nominee_address = models.TextField(blank=True)
    name_of_paying_office = models.CharField(max_length=250, null=True, blank=True)
    address_of_paying_office = models.CharField(max_length=255, null=True, blank=True)
    currency = models.CharField(
        max_length=10,
        choices=CURRENCY_CHOICE.choices,
        default=CURRENCY_CHOICE.BDT
    )
    mobile_no = models.CharField(max_length=20, null=True, blank=True)
    denomination = models.CharField(
        max_length=20,
        null=True,
        blank=True
    )
    face_value = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    face_value_words = models.CharField(
        max_length=500, null=True, blank=True
    )
    total_no_of_bonds = models.PositiveIntegerField(default=1, null=True, blank=True)
    total_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    FC_account_no = models.CharField(max_length=20,blank=True,null=True)
    FC_account_office = models.CharField(max_length=150,blank=True,null=True)
    service = models.CharField(max_length=150,blank=True,null=True)
    service_address = models.CharField(max_length=250,blank=True,null=True)
    reference_name = models.CharField(max_length=150,blank=True,null=True)
    reference_service = models.CharField(max_length=150,blank=True,null=True)
    reference_service_address = models.CharField(max_length=250,blank=True,null=True)
    # wage_earner_buying_branch = models.CharField(max_length=250,blank=True,null=True)
    passport_no = models.CharField(
        max_length=50,
        blank=True
    )
    place_of_issue= models.CharField(max_length=150, null=True, blank=True)
    date_of_issue = models.DateField(null=True, blank=True)

    status = models.CharField(
        max_length=10,
        choices=ApplicationStatus.choices,
        default=ApplicationStatus.PENDING
    )
    approved_by = models.ForeignKey(
                User,
                on_delete=models.SET_NULL,
                null=True,
                blank=True,
                related_name='approved_WEB_app'
            )
    approval_date = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ['-application_date', '-id']
        indexes = [
            models.Index(fields=['applicant_name']),
            models.Index(fields=['status', 'application_date']),
        ]
    def is_expired(self):
        """Check if application is older than 30 days and still pending"""
        if self.status == ApplicationStatus.PENDING:
            expiry_date = self.application_date + timedelta(days=30)
            return timezone.localdate() > expiry_date
        return False
    def approve(self, user):
        """Approve the application"""
        self.status = ApplicationStatus.APPROVED
        self.approved_by = user
        self.approval_date = timezone.now()
        self.save()
    
    def reject(self, user, reason):
        """Reject the application"""
        self.status = ApplicationStatus.REJECTED
        self.approved_by = user
        self.approval_date = timezone.now()
        self.rejection_reason = reason
        self.save()
    def save(self, *args, **kwargs):
        if not self.application_no:
            last = WageEarnersBond.objects.order_by("-id").first()
            next_id = 1 if not last else last.id + 1
            self.application_no = generate_WEB_application_no(next_id)
        self.face_value_words = num2words(self.face_value, lang="en").upper()
        self.total_amount = self.face_value * self.total_no_of_bonds
        super().save(*args, **kwargs)
    def __str__(self):
        return f"{self.application_no} | {self.applicant_name}"
    
class BondApprovalLog(models.Model):

    application = models.ForeignKey(
        WageEarnersBond,
        on_delete=models.CASCADE
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
        return f"{self.application.application_no} - {self.action}"



class USDBond(models.Model):
    application_no = models.CharField(max_length=30, unique=True)
    application_date = models.DateField(auto_now_add=True)
    # bond_type = models.CharField(max_length=150, null=True, blank=True)
    bond_type = models.CharField(
            max_length=70, 
            choices=USD_BondChice.choices,
            null=True, blank=True
        )
    face_value = models.DecimalField(max_digits=18, decimal_places=2, validators=[MinValueValidator(0)])
    quantity = models.DecimalField(max_digits=8, decimal_places=2, validators=[MinValueValidator(0)])
    face_value_words = models.CharField(max_length=500, null=True, blank=True)
    applicant_name = models.CharField(max_length=250)
    nominee_name = models.CharField(max_length=250, blank=True, null=True)
    applicant_address = models.TextField(null=True, blank=True)
    applicant_address_BD = models.TextField(null=True, blank=True)
    nominee_address = models.TextField(blank=True)
    applicant_contact = models.CharField(max_length=20, blank=True, null=True)
    nominee_contact = models.CharField(max_length=20, blank=True, null=True)
    dob = models.DateField(null=True, blank=True)
    relation_with_nominee = models.CharField(max_length=150, blank=True, null=True)
    passport_no = models.CharField(max_length=50, blank=True, null=True)
    place_of_issue= models.CharField(max_length=150, null=True, blank=True)
    FC_account_no = models.CharField(max_length=20,blank=True,null=True)
    FC_account_office = models.CharField(max_length=150,blank=True,null=True)
    
    service = models.CharField(max_length=150,blank=True,null=True)
    service_address = models.CharField(max_length=250,blank=True,null=True)
    name_of_paying_office = models.CharField(max_length=250)
    address_of_paying_office = models.CharField(max_length=255, blank=True, null=True)
    denomination = models.CharField(max_length=20, null=True, blank=True)

    # total_no_of_bonds = models.PositiveIntegerField(default=0)
    total_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    
    status = models.CharField(
        max_length=10,
        choices=ApplicationStatus.choices,
        default=ApplicationStatus.PENDING
    )
    approved_by = models.ForeignKey(
            User,
            on_delete=models.SET_NULL,
            null=True,
            blank=True,
            related_name='approved_USDB_app'
        )
    approval_date = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ['-application_date', '-id']
        indexes = [
            models.Index(fields=['applicant_name']),
            models.Index(fields=['status', 'application_date']),
        ]
    def is_expired(self):
        """Check if application is older than 30 days and still pending"""
        if self.status == ApplicationStatus.PENDING:
            expiry_date = self.application_date + timedelta(days=30)
            return timezone.localdate() > expiry_date
        return False
    def approve(self, user):
        """Approve the application"""
        self.status = ApplicationStatus.APPROVED
        self.approved_by = user
        self.approval_date = timezone.now()
        self.save()
    
    def reject(self, user, reason):
        """Reject the application"""
        self.status = ApplicationStatus.REJECTED
        self.approved_by = user
        self.approval_date = timezone.now()
        self.rejection_reason = reason
        self.save()
    


    def calculate_total_amount(self):
        return self.face_value*self.quantity
    

    def save(self, *args, **kwargs):
        if not self.application_no:
            last = USDBond.objects.order_by("-id").first()
            next_id = 1 if not last else last.id + 1
            self.application_no = generate_USDB_application_no(next_id)
        self.face_value_words = num2words(self.face_value, lang="en").upper()
        amount = self.calculate_total_amount()
        self.total_amount = amount
        super().save(*args, **kwargs)
    def __str__(self):
        return f"{self.application_no} | {self.applicant_name}"

class USDBondApprovalLog(models.Model):

    application = models.ForeignKey(
        USDBond,
        on_delete=models.CASCADE
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
        return f"{self.application.application_no} - {self.action}"
