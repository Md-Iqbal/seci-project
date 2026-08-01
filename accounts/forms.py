from django import forms
from django.core.validators import RegexValidator
from .models import AccountApplication, AccountType

class AccountApplicationForm(forms.ModelForm):
    # Validators
    phone_validator = RegexValidator(
        regex=r'^01[3-9]\d{8}$',
        message="Enter a valid Bangladesh mobile number (e.g., 01712345678)"
    )
    
    nid_validator = RegexValidator(
        regex=r'^\d{10}$|^\d{13}$|^\d{17}$',
        message="Enter a valid NID number (10, 13, or 17 digits)"
    )
    
    # Override fields with custom widgets and validators
    mobile_number = forms.CharField(
        validators=[phone_validator],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '01712345678'
        })
    )
    
    nid_number = forms.CharField(
        validators=[nid_validator],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter 10, 13, or 17 digit NID'
        })
    )
    
    nominee_mobile = forms.CharField(
        validators=[phone_validator],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '01712345678'
        })
    )
    
    nominee_nid = forms.CharField(
        validators=[nid_validator],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter nominee NID'
        })
    )
    
    terms_accepted = forms.BooleanField(
        required=True,
        label="I accept the terms and conditions"
    )
    
    class Meta:
        model = AccountApplication
        exclude = [
            'application_number', 'status', 'approved_by',
            'approval_date', 'rejection_reason', 'account_number'
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'father_name': forms.TextInput(attrs={'class': 'form-control'}),
            'mother_name': forms.TextInput(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'email@example.com'
            }),
            'present_address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'permanent_address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control'}),
            'account_type': forms.Select(attrs={'class': 'form-control'}),
            'initial_deposit': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '500'
            }),
            # 'photograph': forms.FileInput(attrs={
            #     'class': 'form-control',
            #     'accept': 'image/*'
            # }),
            # 'nid_copy': forms.FileInput(attrs={
            #     'class': 'form-control',
            #     'accept': 'image/*,application/pdf'
            # }),
            # 'signature': forms.FileInput(attrs={
            #     'class': 'form-control',
            #     'accept': 'image/*'
            # }),
            'nominee_name': forms.TextInput(attrs={'class': 'form-control'}),
            'nominee_relation': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def clean_initial_deposit(self):
        deposit = self.cleaned_data.get('initial_deposit')
        if deposit < 500:
            raise forms.ValidationError("Minimum initial deposit is 500 BDT")
        return deposit
    
    def clean_nid_number(self):
        nid = self.cleaned_data.get('nid_number')
        # Check if NID already has an approved application
        existing = AccountApplication.objects.filter(
            nid_number=nid,
            status='APPROVED'
        ).exists()
        if existing:
            raise forms.ValidationError(
                "An account with this NID already exists."
            )
        return nid

class ApplicationSearchForm(forms.Form):
    nid_validator = RegexValidator(
        regex=r'^\d{10}$|^\d{13}$|^\d{17}$',
        message="Enter a valid NID number (10, 13, or 17 digits)"
    )
    
    nid_number = forms.CharField(
        validators=[nid_validator],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your NID number'
        }),
        label='National ID Number'
    )

class ApplicationApprovalForm(forms.Form):
    action = forms.ChoiceField(
        choices=[('approve', 'Approve'), ('reject', 'Reject')],
        widget=forms.RadioSelect
    )
    rejection_reason = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Enter reason for rejection (required if rejecting)'
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        action = cleaned_data.get('action')
        reason = cleaned_data.get('rejection_reason')
        
        if action == 'reject' and not reason:
            raise forms.ValidationError(
                "Rejection reason is required when rejecting an application."
            )
        return cleaned_data