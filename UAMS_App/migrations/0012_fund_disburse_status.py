# Generated by Django 5.1.4 on 2025-01-24 08:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('UAMS_App', '0011_notification_related_fund'),
    ]

    operations = [
        migrations.AddField(
            model_name='fund',
            name='disburse_status',
            field=models.CharField(choices=[('pending', 'Pending'), ('disbursed', 'Disbursed')], default='pending', max_length=10),
        ),
    ]
