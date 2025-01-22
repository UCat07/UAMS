from django.contrib import admin
from .models import Profile
from .models import AidApplication


admin.site.register(Profile)

class AidApplicationAdmin(admin.ModelAdmin):
    list_display = ('application_id', 'user', 'date_submitted', 'application_status')
    list_filter = ('application_status', 'date_submitted')
    search_fields = ('user__username', 'user__profile__name', 'bank_account_number')
    ordering = ('-date_submitted',)
    readonly_fields = ('application_id', 'date_submitted')

    # Add inline display for fields with longer content
    fieldsets = (
        (None, {
            'fields': (
                'application_id',
                'user',
                'date_submitted',
                'application_status',
            )
        }),
        ('Application Details', {
            'fields': (
                'bank_type',
                'bank_account_number',
                'parents_monthly_income',
                'support_document',
                'rejection_reason',
            )
        }),
    )

admin.site.register(AidApplication, AidApplicationAdmin)
