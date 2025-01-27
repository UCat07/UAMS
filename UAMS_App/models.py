# Models.py for UAMS_App
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError





class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, null=False, default="unknown")
    course = models.CharField(max_length=255, null=False, default="unknown")
    student_id = models.CharField(max_length=255, null=False, unique=True, default="unknown")  # Using username as student_id
    name = models.CharField(max_length=255, null=False, default="unknown")  # Added name field for full name

    def save(self, *args, **kwargs):
        self.student_id = self.user.username  # Set student_id to the username of the User model
        super().save(*args, **kwargs)

    def __str__(self):
        return self.user.username




class AidApplication(models.Model):
    APPLICATION_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    application_id = models.CharField(max_length=10, primary_key=True, editable=False)
    bank_type = models.CharField(max_length=50)
    bank_account_number = models.CharField(max_length=20)
    parents_monthly_income = models.DecimalField(max_digits=10, decimal_places=2)
    support_document = models.FileField(upload_to='support_documents/', blank=True, null=True)
    date_submitted = models.DateTimeField(auto_now_add=True)
    application_status = models.CharField(max_length=10, choices=APPLICATION_STATUS_CHOICES, default='pending')
    rejection_reason = models.TextField(blank=True, null=True, default ='')

    def clean(self):
        # Validate other fields (example for negative income)
        if self.parents_monthly_income < 0:
            raise ValidationError({'parents_monthly_income': 'Income cannot be negative.'})

    def save(self, *args, **kwargs):
        if not self.application_id:
            last_application = AidApplication.objects.order_by('-application_id').first()
            if last_application:
                last_id = int(last_application.application_id[3:])
                new_id = f"AID{last_id + 1:03d}"
            else:
                new_id = "AID001"
            self.application_id = new_id
            
        if self.application_status == 'accepted':
            # Clear the rejection reason if the application is accepted
            self.rejection_reason = ''

        # Save the AidApplication instance first
        super().save(*args, **kwargs)

        if self.application_status == 'rejected':
            # Update the associated fund instead of deleting it
            if hasattr(self, 'fund'):
                self.fund.status = 'cancelled'
                self.fund.save()
        
        if self.application_status == 'accepted':

            if not hasattr(self, 'fund') or self.fund is None:
            # Create the associated Fund if it doesn't exist
                Fund.objects.create(
                    aid_application=self,
                    amount=0
                )

        local_timezone = timezone.get_current_timezone()
        local_date_submitted = self.date_submitted.astimezone(local_timezone)
        formatted_date = local_date_submitted.strftime('%Y-%m-%d %H:%M:%S')

        # Create a notification based on the application status
        if self.application_status == 'pending':
            Notification.objects.create(
                recipient=self.user,
                message=f"Your application {self.application_id} has been submitted successfully at {formatted_date}. Please wait for admin to approve.",
                related_aid_application=self
            )
        elif self.application_status == 'rejected':
            Notification.objects.create(
                recipient=self.user,
                message=f"Your application {self.application_id} has been rejected by admin. Please track application status for further information.",
                related_aid_application=self
            )
        elif self.application_status == 'accepted':
            Notification.objects.create(
                recipient=self.user,
                message=f"Your application {self.application_id} has been accepted by the admin, please wait for further disbursement.",
                related_aid_application=self
            )


    def __str__(self):
        return f"Aid Application {self.application_id} by {self.user.username}"

    def delete(self, *args, **kwargs):
        if self.support_document:
            self.support_document.delete(save=False)
        super().delete(*args, **kwargs)




class Feedback(models.Model):
    FEEDBACK_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('responded', 'Responded'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    feedback_id = models.CharField(max_length=10, primary_key=True, editable=False)
    subject = models.CharField(max_length=255)
    content = models.TextField()
    date_submitted = models.DateTimeField(auto_now_add=True)
    response = models.TextField(blank=True, null=True, default='')
    feedback_status = models.CharField(max_length=10, choices=FEEDBACK_STATUS_CHOICES, default='pending')

    def save(self, *args, **kwargs):
        if self.response:
            self.feedback_status = 'responded'

        if not self.feedback_id:
            last_feedback = Feedback.objects.order_by('-feedback_id').first()
            if last_feedback:
                last_id = int(last_feedback.feedback_id[3:])
                new_id = f"FED{last_id + 1:03d}"
            else:
                new_id = "FED001"
            self.feedback_id = new_id

        super().save(*args, **kwargs)
        
        local_timezone = timezone.get_current_timezone()
        local_date_submitted = self.date_submitted.astimezone(local_timezone)
        formatted_date = local_date_submitted.strftime('%Y-%m-%d %H:%M:%S')

        # Create a notification based on the feedback status
        if self.feedback_status == 'pending':
            Notification.objects.create(
                recipient=self.user,
                message=f"Your feedback {self.feedback_id} has been submitted successfully at {formatted_date}. Please wait for admin to response.",
                related_feedback=self
            )
        elif self.feedback_status == 'responded':
            Notification.objects.create(
                recipient=self.user,
                message=f"Your feedback {self.feedback_id} has been responded to: \n{self.response}",
                related_feedback=self
            )

    def __str__(self):
        return f"Feedback {self.feedback_id} by {self.user.username}"

    class Meta:
        ordering = ['date_submitted']




class Fund(models.Model):
    FUND_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('disbursed', 'Disbursed'),
        ('cancelled', 'Cancelled'),
        ('finished', 'Finished'),
    ]

    fund_id = models.CharField(max_length=10, primary_key=True, editable=False)
    date_created = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    duration_years = models.PositiveIntegerField(default=0)  # Added duration field
    aid_application = models.OneToOneField(
        AidApplication, on_delete=models.CASCADE, related_name='fund'
    )
    status = models.CharField(max_length=10, choices=FUND_STATUS_CHOICES, default='pending')

    def clean(self):
        # Ensure the amount and duration are not negative
        if self.amount < 0:
            raise ValidationError({'amount': 'Amount cannot be negative.'})
        if self.duration_years < 0:
            raise ValidationError({'duration_years': 'Duration cannot be negative.'})

        # Check that the related aid application is not rejected
        if self.aid_application.application_status == 'rejected':
            raise ValidationError('Cannot create a fund for a rejected application.')

    def save(self, *args, **kwargs):
        # Automatically generate a unique fund_id
        if not self.fund_id:
            last_fund = Fund.objects.order_by('-fund_id').first()
            if last_fund:
                last_id = int(last_fund.fund_id[3:])
                new_id = f"FND{last_id + 1:03d}"
            else:
                new_id = "FND001"
            self.fund_id = new_id

        # Handle fund cancellation when application is rejected
        if self.aid_application.application_status == 'rejected':
            self.status = 'cancelled'

        super().save(*args, **kwargs)

        # Create a notification based on the fund status
        if self.status == 'disbursed':
            Notification.objects.create(
                recipient=self.aid_application.user,
                message=f"Your application {self.aid_application.application_id} has been disbursed of fund {self.fund_id} with an amount of RM {self.amount} during years of {self.duration_years}.",
                related_aid_application=self.aid_application
            )
        elif self.status == 'cancelled':
            Notification.objects.create(
                recipient=self.aid_application.user,
                message=f"Your application {self.aid_application.application_id} was rejected, and the fund {self.fund_id} has been cancelled.",
                related_aid_application=self.aid_application
            )
        elif self.status == 'finished':
            Notification.objects.create(
                recipient=self.aid_application.user,
                message=f"Your fund {self.fund_id} has been marked as finished. Thank you for participating in the aid program.",
                related_aid_application=self.aid_application
            )

    def __str__(self):
        return f"Fund {self.fund_id} for Application {self.aid_application.application_id}"




class Notification(models.Model):
    notification_id = models.CharField(max_length=10, primary_key=True, editable=False)
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    related_aid_application = models.ForeignKey(
        AidApplication, on_delete=models.SET_NULL, blank=True, null=True
    )
    related_feedback = models.ForeignKey(
        Feedback, on_delete=models.SET_NULL, blank=True, null=True
    )
    related_fund = models.ForeignKey(
        Fund, on_delete=models.SET_NULL, blank=True, null=True
    )
    is_read = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.notification_id:
            last_notification = Notification.objects.order_by('-notification_id').first()
            if last_notification:
                last_id = int(last_notification.notification_id[3:])
                new_id = f"NOF{last_id + 1:03d}"
            else:
                new_id = "NOF001"
            self.notification_id = new_id

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Notification {self.notification_id} for {self.recipient.username}"
