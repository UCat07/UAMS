from django.contrib import admin
from .models import Profile
from .models import AidApplication, Feedback, Notification, Fund

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

class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('feedback_id', 'user', 'subject', 'date_submitted', 'feedback_status')
    list_filter = ('feedback_status', 'date_submitted')
    search_fields = ('user__username', 'subject', 'content')
    ordering = ('-date_submitted',)
    readonly_fields = ('feedback_id', 'date_submitted')  # Remove 'date_modified' from readonly_fields

    fieldsets = (
        (None, {
            'fields': ('feedback_id', 'user', 'subject', 'content', 'date_submitted', 'feedback_status')
        }),
        ('Response Information', {
            'fields': ('response',),  # Do not include 'date_modified' in fieldsets
        }),
    )

admin.site.register(Feedback, FeedbackAdmin)

class NotificationAdmin(admin.ModelAdmin):
    list_display = ('notification_id', 'recipient', 'message', 'created_at', 'is_read')
    list_filter = ('is_read', 'created_at')
    search_fields = ('recipient__username', 'message')
    ordering = ('-created_at',)
    readonly_fields = ('notification_id', 'created_at')

    fieldsets = (
        (None, {
            'fields': ('notification_id', 'recipient', 'message', 'created_at', 'is_read')
        }),
        ('Related Information', {
            'fields': ('related_aid_application', 'related_feedback', 'related_fund')
        }),
    )

admin.site.register(Notification, NotificationAdmin)

class FundAdmin(admin.ModelAdmin):
    list_display = ('fund_id', 'aid_application', 'amount', 'duration_years', 'status', 'date_created')
    list_filter = ('status', 'date_created')
    search_fields = ('fund_id', 'aid_application__application_id', 'aid_application__user__username')
    ordering = ('-date_created',)
    readonly_fields = ('fund_id', 'date_created')

    fieldsets = (
        (None, {
            'fields': ('fund_id', 'aid_application', 'amount', 'duration_years', 'status', 'date_created')
        }),
    )

admin.site.register(Fund, FundAdmin)