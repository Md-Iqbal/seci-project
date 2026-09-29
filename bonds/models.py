from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.models import User
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from .utils import generate_WEB_application_no, generate_USDB_application_no
from num2words import num2words
from decimal import Decimal
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
class WageEarnersBondBranch_CHOICE(models.TextChoices):
    DHAKA = 'Wage Earners Corp br. Dhaka', 'Wage Earners Corp br. Dhaka'
    DHAKA_CANT = 'Dhaka Cant.Corp br. Dhaka','Dhaka Cant.Corp br. Dhaka'
    CHITTAGONG = 'Wage Earners Corp br. Chattogram', 'Wage Earners Corp br. Chattogram'
    KHULNA = 'Khulna Corp. br. Khulna', 'Khulna Corp. br. Khulna'
    SYLHET = 'Dargagate Corp. br. Sylhet', 'Dargagate Corp. br. Sylhet'

class WageEarnersBond(models.Model):
    application_no = models.CharField(max_length=30, unique=True)
    application_date = models.DateField(auto_now_add=True)
    # applicant info
    applicant_name = models.CharField(max_length=250)
    applicant_name_bn = models.CharField(max_length=250, blank=True, null=True)
    dob = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female')], null=True, blank=True)                                              
    applicant_address = models.TextField(null=True, blank=True)#bd address
    applicant_address_abroad = models.TextField(null=True, blank=True)#foreign addressmobile_no = models.CharField(max_length=20, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    phone_abroad = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(max_length=100, null=True, blank=True)
    service = models.CharField(max_length=150,blank=True,null=True)
    service_address = models.CharField(max_length=250,blank=True,null=True)
    nid_number = models.CharField(max_length=20, null=True, blank=True)
    passport_no = models.CharField(
            max_length=50,
            blank=True
        )
    place_of_issue= models.CharField(max_length=150, null=True, blank=True)
    date_of_issue = models.DateField(null=True, blank=True)
    date_of_expiry = models.DateField(null=True, blank=True)
    visa_type = models.TextField(null=True, blank=True)
    visa_start_date = models.DateField(null=True, blank=True)
    visa_end_date = models.DateField(null=True, blank=True)
    #If returned from abroad permanently
    return_date = models.DateField(null=True, blank=True)
    #nominee info  
    nominee_name = models.CharField(max_length=250, blank=True)    
    nominee_dob = models.DateField(null=True, blank=True) 
    nominee_nid_number = models.CharField(max_length=20, null=True, blank=True)
    nominee_address = models.TextField(blank=True)
    nominee_gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female')], null=True, blank=True)
    #if nominee is minor then we need to store minor nominee info
    is_minor = models.BooleanField(default=False)
    minor_nominee_name = models.CharField(max_length=250, blank=True)
    minor_nominee_address = models.TextField(blank=True)
    identifier_nid = models.CharField(max_length=20, null=True, blank=True)
    identifier_dob = models.DateField(null=True, blank=True)
    identifier_gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female')], null=True, blank=True)
    identifier_name = models.CharField(max_length=250, blank=True)
    identifier_name_bn = models.CharField(max_length=250, blank=True, null=True)
    identifier_pre_address = models.TextField(blank=True)
    identifier_per_address = models.TextField(blank=True)
    identifier_father = models.CharField(max_length=250, blank=True)
    identifier_mother = models.CharField(max_length=250, blank=True)
    relation_with_nominee = models.CharField(max_length=150, blank=True)
    identifier_phone = models.CharField(max_length=20, blank=True, null=True)
    identifier_email = models.EmailField(max_length=100, blank=True, null=True)

    #benificiary info
    beneficiary_name = models.CharField(max_length=250, blank=True)
    benificiary_name_bn = models.CharField(max_length=250, blank=True, null=True)
    beneficiary_father_name = models.CharField(max_length=250, blank=True)
    beneficiary_mother_name = models.CharField(max_length=250, blank=True)
    beneficiary_spouse_name = models.CharField(max_length=250, blank=True)
    benificiary_nid = models.CharField(max_length=20, null=True, blank=True)
    benificiary_dob = models.DateField(null=True, blank=True)
    benificiary_gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female')], null=True, blank=True)
    benificiary_present_address = models.TextField(blank=True)
    benificiary_permanent_address = models.TextField(blank=True)
    benificiary_email = models.EmailField(max_length=100, blank=True, null=True)
    benificiary_phone = models.CharField(max_length=20, blank=True, null=True)
    benificiary_phone_abroad = models.CharField(max_length=20, blank=True, null=True)

    name_of_paying_office = models.CharField(
        max_length=150,
        choices=WageEarnersBondBranch_CHOICE.choices,
        default=WageEarnersBondBranch_CHOICE.DHAKA
    )
    currency = models.CharField(
        max_length=10,
        choices=CURRENCY_CHOICE.choices,
        default=CURRENCY_CHOICE.BDT
    )
    

    denomination = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        validators=[MinValueValidator(0)], 
        null=True, blank=True
    )
    denomication_words = models.CharField(
        max_length=500, null=True, blank=True
    )
    face_value = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        validators=[MinValueValidator(0)], 
        default=25000.00, null=True, blank=True
    )
    face_value_words = models.CharField(
        max_length=500, null=True, blank=True
    )
    Bank_name = models.CharField(max_length=150,blank=True,null=True)
    Bank_account_no = models.CharField(max_length=20,blank=True,null=True)
    Bank_account_branch = models.CharField(max_length=150,blank=True,null=True)
    reference_name = models.CharField(max_length=150,blank=True,null=True)
    reference_service = models.CharField(max_length=150,blank=True,null=True)
    reference_service_address = models.CharField(max_length=250,blank=True,null=True)
    # wage_earner_buying_branch = models.CharField(max_length=250,blank=True,null=True)
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
        self.face_value = Decimal("25000.00")
        self.face_value_words = num2words(self.face_value, lang="en")
        self.denomication_words = num2words(self.denomination, lang="en")
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
    face_value = models.DecimalField(max_digits=18, decimal_places=2, validators=[MinValueValidator(0)], null=True, blank=True)
    denomination = models.DecimalField(max_digits=18, decimal_places=2, validators=[MinValueValidator(0)], null=True, blank=True)
    quantity = models.DecimalField(max_digits=8, decimal_places=2, validators=[MinValueValidator(0)], null=True, blank=True)
    face_value_words = models.CharField(max_length=500, null=True, blank=True)
    applicant_name = models.CharField(max_length=250)
    applicant_name_bn = models.CharField(max_length=250, blank=True, null=True)
    father_name = models.CharField(max_length=250, blank=True, null=True)
    mother_name = models.CharField(max_length=250, blank=True, null=True)
    spouse_name = models.CharField(max_length=250, blank=True, null=True)
    nid_number = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(max_length=100, blank=True, null=True)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female')], null=True, blank=True)                                              
    applicant_address = models.TextField(null=True, blank=True)
    applicant_address_BD = models.TextField(null=True, blank=True)
    mobile_no = models.CharField(max_length=20, null=True, blank=True)
    phone_abroad = models.CharField(max_length=20, null=True, blank=True)
    dob = models.DateField(null=True, blank=True)
    visa_type = models.TextField(null=True, blank=True)
    visa_start_date = models.DateField(null=True, blank=True)
    visa_end_date = models.DateField(null=True, blank=True)

    #nominee info
    nominee_name = models.CharField(max_length=250, blank=True, null=True)
    nominee_address = models.TextField(blank=True)
    nominee_contact = models.CharField(max_length=20, blank=True, null=True)
    nominee_nid_number = models.CharField(max_length=20, null=True, blank=True)
    nominee_dob = models.DateField(null=True, blank=True)
    nominee_gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female')], null=True, blank=True)
    relation_with_nominee = models.CharField(max_length=150, blank=True, null=True)
    
    #if minior
    is_minor = models.BooleanField(default=False)
    minor_nominee_name = models.CharField(max_length=250, blank=True)
    minor_nominee_address = models.TextField(blank=True)
    identifier_nid = models.CharField(max_length=20, null=True, blank=True)
    identifier_dob = models.DateField(null=True, blank=True)
    identifier_gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female')], null=True, blank=True)
    identifier_name = models.CharField(max_length=250, blank=True)
    identifier_name_bn = models.CharField(max_length=250, blank=True, null=True)
    identifier_pre_address = models.TextField(blank=True)
    identifier_per_address = models.TextField(blank=True)
    identifier_father = models.CharField(max_length=250, blank=True)
    identifier_mother = models.CharField(max_length=250, blank=True)
    relation_with_nominee = models.CharField(max_length=150, blank=True)
    identifier_phone = models.CharField(max_length=20, blank=True, null=True)
    identifier_email = models.EmailField(max_length=100, blank=True, null=True)
    
    #benificiary info
    benificiary_name = models.CharField(max_length=250, blank=True, null=True)
    benificiary_name_bn = models.CharField(max_length=250, blank=True, null=True)
    benificiary_present_address = models.TextField(blank=True)
    benificiary_address = models.TextField(blank=True)
    benificiary_father_name = models.CharField(max_length=250, blank=True)
    benificiary_mother_name = models.CharField(max_length=250, blank=True)
    benificiary_spouse_name = models.CharField(max_length=250, blank=True)
    benificiary_email = models.EmailField(max_length=100, blank=True, null=True)
    benificiary_phone_abroad = models.CharField(max_length=20, blank=True, null=True)
    benificiary_phone_bangladesh = models.CharField(max_length=20, blank=True, null=True)
    relation_with_holder = models.CharField(max_length=150, blank=True, null=True)
    passport_no = models.CharField(max_length=50, blank=True, null=True)
    date_of_expiry = models.DateField(null=True, blank=True)
    place_of_issue= models.CharField(max_length=150, null=True, blank=True)
    return_date = models.DateField(null=True, blank=True)
    FC_account_no = models.CharField(max_length=20,blank=True,null=True)
    FC_account_office = models.CharField(max_length=150,blank=True,null=True)
    
    service = models.CharField(max_length=150,blank=True,null=True)
    service_address = models.CharField(max_length=250,blank=True,null=True)
    name_of_paying_office = models.CharField(max_length=250)
    address_of_paying_office = models.CharField(max_length=255, blank=True, null=True)

    # total_no_of_bonds = models.PositiveIntegerField(default=0)
    total_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        validators=[MinValueValidator(0)], null=True, blank=True
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
    

    def save(self, *args, **kwargs):
        if not self.application_no:
            last = USDBond.objects.order_by("-id").first()
            next_id = 1 if not last else last.id + 1
            self.application_no = generate_USDB_application_no(next_id)
        self.face_value_words = num2words(self.face_value, lang="en").upper()
        self.denomination = self.face_value
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
