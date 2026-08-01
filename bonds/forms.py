from django import forms
from django.core.validators import RegexValidator
from .models import *


class WageEarnersBondForm(forms.ModelForm):

    class Meta:

        model = WageEarnersBond

        exclude = (
            "application_no",
            "status",
            "created_by",
            "created_at",
            "updated_at",
        )

        widgets = {

            "application_date":
                forms.DateInput(attrs={
                    "type": "date"
                }),

            "remarks":
                forms.Textarea(attrs={
                    "rows": 3
                }),

            "applicant_address":
                forms.Textarea(attrs={
                    "rows": 2
                }),

            "name_of_paying_office":
                forms.Textarea(attrs={
                    "rows": 2
                }),

        }
class ApplicationSearchForm(forms.Form):
    
    application_no = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your application number'
        }),
        label='National ID Number'
    )

class USDBondForm(forms.ModelForm):

    class Meta:

        model = USDBond

        exclude = (
            "application_no",
            "status",
            "created_by",
            "created_at",
            "updated_at",
        )

        widgets = {

            "application_date":
                forms.DateInput(attrs={
                    "type": "date"
                }),

            "remarks":
                forms.Textarea(attrs={
                    "rows": 3
                }),

            "applicant_address":
                forms.Textarea(attrs={
                    "rows": 2
                }),

            "name_of_paying_office":
                forms.Textarea(attrs={
                    "rows": 2
                }),

        }