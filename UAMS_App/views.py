from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import Notification
from django.contrib.auth import logout
from .models import Profile, Fund
from django.contrib import messages
from .forms import AidApplicationForm
from .forms import FeedbackForm
from .models import Feedback
from django.shortcuts import render, get_object_or_404, redirect
from .models import AidApplication
from .forms import DisburseFundForm
from .forms import EnsureDisburseFundForm
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML  # Install WeasyPrint for PDF generation
from .models import NotificationPreference
from .forms import NotificationPreferenceForm



def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            # Check if the user is a superuser (admin)
            if user.is_superuser:
                return redirect('admin_home')  # Redirect to the admin home page
            # Check if the user is in the "Student" group
            elif user.groups.filter(name='Student').exists():
                return redirect('student_home')  # Redirect to the student home page
            elif user.groups.filter(name='Financial Officer').exists():
                return redirect('officer_home')  # Redirect to the student home page
            else:
                return redirect('login')  # Redirect to login if the user is neither an admin nor a student
    else:
        form = AuthenticationForm()

    return render(request, 'UAMS_App/login.html', {'form': form})



def custom_logout(request):
    logout(request)  # Log out the user
    return redirect('login')  # Redirect to the login page (adjust as needed)




@login_required
def student_home(request):
    if not request.user.groups.filter(name="Student").exists():
        return HttpResponseForbidden("You are not authorized to access this page.")
    
    # Retrieve the profile of the logged-in user
    profile = Profile.objects.get(user=request.user)
    
    # Get the count of unread notifications for the logged-in user
    unread_notifications_count = Notification.objects.filter(recipient=request.user, is_read=False).count()
    
    # Pass the profile, unread notifications count, and user details to the template
    return render(request, 'UAMS_App/student_home.html', {
        'profile': profile,
        'unread_notifications_count': unread_notifications_count
    })


@login_required
def submit_application(request):
    if not request.user.groups.filter(name="Student").exists():
        return HttpResponseForbidden("You are not authorized to access this page.")
    
    if request.method == 'POST':
        form = AidApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            print(form.cleaned_data.get('parent_monthly_income'))  # Debugging
            application = form.save(commit=False)
            application.user = request.user
            application.save()
            
            application_id = application.application_id
            return redirect('submit_application_success', application_id=application_id)
        else:
            messages.error(request, 'There was an error with your submission.')
    else:
        form = AidApplicationForm()

    return render(request, 'UAMS_App/submit_application.html', {'form': form})

@login_required
def submit_application_success(request, application_id):
    return render(request, 'UAMS_App/submit_application_success.html', {'application_id': application_id})

@login_required
def track_application_status(request):
    if not request.user.groups.filter(name="Student").exists():
        return HttpResponseForbidden("You are not authorized to access this page.")
    
    application = None
    query = False

    if 'application_id' in request.GET:
        query = True
        application_id = request.GET.get('application_id', '').strip()
        try:
            application = AidApplication.objects.get(
                application_id=application_id,
                user=request.user
            )
        except AidApplication.DoesNotExist:
            application = None

    return render(request, 'UAMS_App/track_application_status.html', {
        'application': application,
        'query': query
    })
    

@login_required
def provide_feedback(request):
    if not request.user.groups.filter(name="Student").exists():
        return HttpResponseForbidden("You are not authorized to access this page.")
    
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.user = request.user  # Associate the feedback with the logged-in user
            feedback.save()
            return redirect('provide_feedback_success', feedback_id=feedback.feedback_id)
    else:
        form = FeedbackForm()

    return render(request, 'UAMS_App/provide_feedback.html', {'form': form})

@login_required
def provide_feedback_success(request, feedback_id):
    if not request.user.groups.filter(name="Student").exists():
        return HttpResponseForbidden("You are not authorized to access this page.")
    
    feedback = Feedback.objects.get(feedback_id=feedback_id)
    return render(request, 'UAMS_App/provide_feedback_success.html', {'feedback_id': feedback.feedback_id})
    
    
@login_required
def select_notification(request):
    if not request.user.groups.filter(name="Student").exists():
        return HttpResponseForbidden("You are not authorized to access this page.")
    
    status_filter = request.GET.get('is_read', '')

    # Filter notifications based on the logged-in user (using 'recipient' instead of 'user')
    notifications = Notification.objects.filter(recipient=request.user)

    # Filter notifications based on the status_filter
    if status_filter == 'True':
        notifications = notifications.filter(is_read=True).order_by('-created_at')
    elif status_filter == 'False':
        notifications = notifications.filter(is_read=False).order_by('-created_at')
    else:
        notifications = notifications.order_by('-created_at')

    # Render the template with the current filter and filtered notifications
    return render(request, 'UAMS_App/select_notification.html', {
        'notification': notifications,
        'status_filter': status_filter
    })



@login_required
def review_notification(request, notification_id):
    if not request.user.groups.filter(name="Student").exists():
        return HttpResponseForbidden("You are not authorized to access this page.")
    
    # Retrieve the notification by ID
    notification = Notification.objects.get(notification_id=notification_id)

    # Mark the notification as read if it isn't already
    if not notification.is_read:
        notification.is_read = True
        notification.save()

    # Retrieve the filter parameter from the query string
    filter_param = request.GET.get('is_read', '')

    # Pass the filter parameter to the template
    return render(request, 'UAMS_App/review_notification.html', {
        'notification': notification,
        'filter_param': filter_param
    })



@login_required
def admin_home(request):
    # Check if the logged-in user is a superuser
    if not request.user.is_superuser:
        return HttpResponseForbidden("You are not authorized to access this page.")
    
    # If the user is an admin, render the admin home page
    return render(request, 'UAMS_App/admin_home.html')



@login_required
def select_application(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden("You are not authorized to access this page.")
    
    # Get applications with a 'pending' status
    applications = AidApplication.objects.filter(application_status='pending')

    return render(request, 'UAMS_App/select_application.html', {'applications': applications})

@login_required
def review_application(request, application_id):
    if not request.user.is_superuser:
        return HttpResponseForbidden("You are not authorized to access this page.")
    
    # Get the specific application by ID
    application = get_object_or_404(AidApplication, application_id=application_id)

    if request.method == 'POST':
        # Update the application status
        status = request.POST.get('application_status')
        application.application_status = status
        application.save()

        # Redirect to the step 2 page to handle rejection reason if needed
        return redirect('review_application_step2', application_id=application_id)

    return render(request, 'UAMS_App/review_application.html', {'application': application})

@login_required
def review_application_step2(request, application_id):
    if not request.user.is_superuser:
        return HttpResponseForbidden("You are not authorized to access this page.")
    
    # Get the specific application by ID
    application = get_object_or_404(AidApplication, application_id=application_id)

    if request.method == 'POST':
        # Get the application status from the form data
        status = request.POST.get('application_status')

        # Check if the status is provided
        if status:
            # Update the application status
            application.application_status = status
            rejection_reason = request.POST.get('rejection_reason', '')

            # If the status is 'rejected', save the rejection reason
            if status == 'rejected':
                if not rejection_reason.strip():
                    messages.error(request, "Rejection reason is required when rejecting an application.")
                    return render(request, 'UAMS_App/review_application_step2.html', {'application': application})
                
                application.rejection_reason = rejection_reason

            # Save the application
            application.save()

            return redirect('select_application')  # Redirect after form submission

    return render(request, 'UAMS_App/review_application_step2.html', {'application': application})

@login_required
def select_aid_record(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden("You are not authorized to access this page.")
    
    # Get the filter status from GET parameters
    status_filter = request.GET.get('status', '')

    if status_filter:
        # Filter by the selected status (either 'accepted' or 'rejected')
        aid_applications = AidApplication.objects.filter(application_status=status_filter)
    else:
        # If no filter is selected, show all accepted or rejected applications
        aid_applications = AidApplication.objects.filter(application_status__in=['accepted', 'rejected'])

    return render(request, 'UAMS_App/select_aid_record.html', {
        'aid_applications': aid_applications
    })

@login_required    
def review_aid(request, application_id):
    if not request.user.is_superuser:
        return HttpResponseForbidden("You are not authorized to access this page.")
    
    # Get the specific application by ID
    application = get_object_or_404(AidApplication, application_id=application_id)

    if request.method == 'POST':
        # Update the application status
        status = request.POST.get('application_status')
        application.application_status = status
        application.save()

        # Redirect to the step 2 page to handle rejection reason if needed
        return redirect('review_aid_step2', application_id=application_id)

    return render(request, 'UAMS_App/review_aid.html', {'application': application})

@login_required
def review_aid_step2(request, application_id):
    if not request.user.is_superuser:
        return HttpResponseForbidden("You are not authorized to access this page.")
    
    # Get the specific application by ID
    application = get_object_or_404(AidApplication, application_id=application_id)

    if request.method == 'POST':
        # Get the application status from the form data
        status = request.POST.get('application_status')
        rejection_reason = request.POST.get('rejection_reason', '')

        # Check if the status is provided
        if status:
            if status == 'rejected' and not rejection_reason.strip():
                messages.error(request, "Rejection reason is required when rejecting an application.")
                return render(request, 'UAMS_App/review_aid_step2.html', {'application': application})

        # Check for no changes in data
            if status == application.application_status:
                if status == 'accepted':
                    messages.error(request, "The application status is already set to 'Accepted'. No changes were made.")
                    return render(request, 'UAMS_App/review_aid_step2.html', {'application': application})
                
                elif status == 'rejected' and rejection_reason == application.rejection_reason:
                    messages.error(
                        request,
                        "The application is already 'Rejected' with the same rejection reason. No changes were made."
                    )
                    return render(request, 'UAMS_App/review_aid_step2.html', {'application': application})
            
            # Update the application status
            application.application_status = status

            # If the status is 'rejected', save the rejection reason
            if status == 'rejected':
                application.rejection_reason = rejection_reason
            elif status == 'accepted':
                application.rejection_reason = ''

            # Save the application
            application.save()

            return redirect('select_aid_record')  # Redirect after form submission

    return render(request, 'UAMS_App/review_aid_step2.html', {'application': application})

@login_required
def select_feedback(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden("You are not authorized to access this page.")
    
    feedbacks = Feedback.objects.filter(feedback_status='pending')  # Only get pending feedbacks
    return render(request, 'UAMS_App/select_feedback.html', {'feedbacks': feedbacks})

@login_required
def response_feedback(request, feedback_id):
    if not request.user.is_superuser:
        return HttpResponseForbidden("You are not authorized to access this page.")
    
    feedback = get_object_or_404(Feedback, feedback_id=feedback_id)

    if request.method == 'POST':
        # Update the feedback response if a response is provided
        feedback.response = request.POST.get('response')
        feedback.feedback_status = 'responded'  # Update status to responded
        feedback.save()
        # Optionally redirect after saving the response, e.g., back to the list or to a success page
        return redirect('select_feedback')  # Replace with your redirect URL
    
    return render(request, 'UAMS_App/response_feedback.html', {'feedback': feedback})





@login_required
def officer_home(request):
    # Check if the logged-in user is in the "Financial Officer" group
    if not request.user.groups.filter(name="Financial Officer").exists():
        return HttpResponseForbidden("You are not authorized to access this page.")
    
    # If the user is a Financial Officer, render the officer home page
    return render(request, 'UAMS_App/officer_home.html')

@login_required
def select_fund(request):
    if not request.user.groups.filter(name="Financial Officer").exists():
        return HttpResponseForbidden("You are not authorized to access this page.")
    
    # Query funds with 'pending' status
    pending_funds = Fund.objects.filter(status='pending')

    if request.method == 'POST':
        selected_fund_id = request.POST.get('fund')
        selected_fund = Fund.objects.get(fund_id=selected_fund_id)
        # Process the selected fund (e.g., mark it as 'disbursed', etc.)

    return render(request, 'UAMS_App/select_fund.html', {'funds': pending_funds})

@login_required
def disburse_fund(request, fund_id):
    if not request.user.groups.filter(name="Financial Officer").exists():
        return HttpResponseForbidden("You are not authorized to access this page.")
    
    # Fetch the fund object
    fund = get_object_or_404(Fund, pk=fund_id)

    # Process the form submission
    if request.method == 'POST':
        form = DisburseFundForm(request.POST, instance=fund)
        if form.is_valid():
            fund.status = 'disbursed'
            fund.save()  # Save the disbursement details
            # Redirect to a success page or the same page
            return redirect('select_fund')
    else:
        form = DisburseFundForm(instance=fund)

    return render(request, 'UAMS_App/disburse_fund.html', {'form': form, 'fund': fund})


@login_required
def select_ensure_fund(request):
    if not request.user.groups.filter(name="Financial Officer").exists():
        return HttpResponseForbidden("You are not authorized to access this page.")
    
    # Get all funds (initially, no filter applied)
    status_filter = request.GET.get('status', '')

    if status_filter:
        # Filter by the selected status (either 'accepted' or 'rejected')
        funds = Fund.objects.filter(status=status_filter)
    else:
        # If no filter is selected, show all accepted or rejected applications
        funds = Fund.objects.filter(status__in=['disbursed', 'cancelled', 'finished'])

    return render(request, 'UAMS_App/select_ensure_fund.html', {
        'funds': funds,
    })

@login_required
def ensure_disburse_fund(request, fund_id):
    if not request.user.groups.filter(name="Financial Officer").exists():
        return HttpResponseForbidden("You are not authorized to access this page.")
    
    fund = get_object_or_404(Fund, pk=fund_id)

    if request.method == 'POST':
        form = EnsureDisburseFundForm(request.POST, instance=fund)
        if form.is_valid():
            form.save()
            return redirect('select_ensure_fund')
        else:
            messages.error(request, "Aid application is not accepted by admin yet.")
    else:
        form = EnsureDisburseFundForm(instance=fund)

    return render(request, 'UAMS_App/ensure_disburse_fund.html', {'form': form, 'fund': fund})

@login_required
def select_report(request):
    if not request.user.groups.filter(name="Financial Officer").exists():
        return HttpResponseForbidden("You are not authorized to access this page.")
    
    # Query funds with 'pending' status
    pending_funds = Fund.objects.filter(status='finished')

    if request.method == 'POST':
        selected_fund_id = request.POST.get('fund')
        selected_fund = Fund.objects.get(fund_id=selected_fund_id)
        # Process the selected fund (e.g., mark it as 'disbursed', etc.)

    return render(request, 'UAMS_App/select_report.html', {'funds': pending_funds})



@login_required
def generate_report(request, fund_id):
    if not request.user.groups.filter(name="Financial Officer").exists():
        return HttpResponseForbidden("You are not authorized to access this page.")
    
    fund = get_object_or_404(Fund, fund_id=fund_id)
    return render(request, 'UAMS_App/generate_report.html', {'fund': fund})

@login_required
def download_report(request, fund_id):
    if not request.user.groups.filter(name="Financial Officer").exists():
        return HttpResponseForbidden("You are not authorized to access this page.")
    
    fund = get_object_or_404(Fund, fund_id=fund_id)
    
    # Render the HTML for the PDF with the pdf_rendered context
    html_string = render_to_string('UAMS_App/generate_report.html', {
        'fund': fund,
        'pdf_rendered': True  # Indicate PDF rendering
    })
    
    # Create PDF from the HTML with the passed context
    html = HTML(string=html_string)
    pdf = html.write_pdf()
    
    # Generate the response for PDF download
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Fund_Report_{fund_id}.pdf"'
    return response


@login_required
def manage_notification(request):
    if not request.user.groups.filter(name="Financial Officer").exists():
        return HttpResponseForbidden("You are not authorized to access this page.")
    
    # Get the system's current notification preference
    notification_preference = NotificationPreference.objects.first()

    if request.method == 'POST':
        # Create or update the preference based on the form submission
        form = NotificationPreferenceForm(request.POST, instance=notification_preference)
        
        if form.is_valid():
            form.save()  # Save the new notification preference
            preference = form.cleaned_data['preference']  # Get the selected preference
            messages.success(request, f'Your notification preference has been updated to: {preference}.')  # Success message
            return redirect('manage_notification')  # Redirect after saving
    else:
        # Initialize the form with the current notification preference
        form = NotificationPreferenceForm(instance=notification_preference)
    
    return render(request, 'UAMS_App/manage_notification.html', {'form': form})