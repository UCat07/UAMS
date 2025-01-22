from django.db import models
from django.contrib.auth.models import User

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
    application_id = models.AutoField(primary_key=True)
    bank_type = models.CharField(max_length=50)
    bank_account_number = models.CharField(max_length=20)
    parents_monthly_income = models.DecimalField(max_digits=10, decimal_places=2)
    support_document = models.FileField(upload_to='support_documents/', blank=True, null=True)
    date_submitted = models.DateTimeField(auto_now_add=True)
    application_status = models.CharField(max_length=10, choices=APPLICATION_STATUS_CHOICES, default='pending')
    rejection_reason = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Aid Application {self.application_id} by {self.user.username}"