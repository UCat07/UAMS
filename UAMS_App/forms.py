from django import forms
from .models import AidApplication

class AidApplicationForm(forms.ModelForm):
    class Meta:
        model = AidApplication
        fields = ['bank_type', 'bank_account_number', 'parents_monthly_income', 'support_document']

    def clean_parents_monthly_income(self):
        income = self.cleaned_data.get('parents_monthly_income')
        if income is not None and income < 0:
            raise forms.ValidationError("Parent's monthly income cannot be negative.")
        return income