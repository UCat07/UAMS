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
    
    
from .models import Feedback

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['subject', 'content']  # These are the fields to be filled in by the user

    # Customizing the form's label for readability
    subject = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'form-control'}), label="Subject of your feedback")
    content = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}), label="Your Feedback")

from .models import Fund

class DisburseFundForm(forms.ModelForm):
    class Meta:
        model = Fund
        fields = ['amount', 'duration_years']

    amount = forms.DecimalField(min_value=1, required=True)
    duration_years = forms.IntegerField(min_value=1, required=True)
    
class EnsureDisburseFundForm(forms.ModelForm):
    class Meta:
        model = Fund
        fields = ['status', 'amount', 'duration_years']

    status = forms.ChoiceField(choices=Fund.FUND_STATUS_CHOICES, required=True)
    amount = forms.DecimalField(min_value=1, required=True)
    duration_years = forms.IntegerField(min_value=1, required=True)
    
    
from .models import NotificationPreference

class NotificationPreferenceForm(forms.ModelForm):
    class Meta:
        model = NotificationPreference
        fields = ['preference']