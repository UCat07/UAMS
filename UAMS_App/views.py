# UAMS_App/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate
from .models import Profile
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import Notification




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
            else:
                return redirect('login')  # Redirect to login if the user is neither an admin nor a student
    else:
        form = AuthenticationForm()

    return render(request, 'UAMS_App/login.html', {'form': form})

from django.shortcuts import redirect
from django.contrib.auth import logout

def custom_logout(request):
    logout(request)  # Log out the user
    return redirect('login')  # Redirect to the login page (adjust as needed)


from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Profile

@login_required
def student_home(request):
    # Retrieve the profile of the logged-in user
    profile = Profile.objects.get(user=request.user)
    
    # Get the count of unread notifications for the logged-in user
    unread_notifications_count = Notification.objects.filter(recipient=request.user, is_read=False).count()
    
    # Pass the profile, unread notifications count, and user details to the template
    return render(request, 'UAMS_App/student_home.html', {
        'profile': profile,
        'unread_notifications_count': unread_notifications_count
    })

from django.contrib import messages
from .forms import AidApplicationForm

def submit_application(request):
    if request.method == 'POST':
        form = AidApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            print(form.cleaned_data.get('parent_monthly_income'))  # Debugging
            application = form.save(commit=False)
            application.user = request.user
            application.save()
            
            application_id = application.application_id
            messages.success(request, 'Your application has been successfully submitted!')
            return redirect('submit_application_success', application_id=application_id)
        else:
            messages.error(request, 'There was an error with your submission.')
    else:
        form = AidApplicationForm()

    return render(request, 'UAMS_App/submit_application.html', {'form': form})

def submit_application_success(request, application_id):
    return render(request, 'UAMS_App/submit_application_success.html', {'application_id': application_id})

@login_required
def track_application_status(request):
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
    
from .forms import FeedbackForm
from .models import Feedback

def provide_feedback(request):
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

def provide_feedback_success(request, feedback_id):
    feedback = Feedback.objects.get(feedback_id=feedback_id)
    return render(request, 'UAMS_App/provide_feedback_success.html', {'feedback_id': feedback.feedback_id})
    
    
@login_required
def select_notification(request):
    status_filter = request.GET.get('is_read', '')
    
    # Define the notification query
    if status_filter == 'True':
        notification = Notification.objects.filter(is_read=True).order_by('-created_at')
    elif status_filter == 'False':
        notification = Notification.objects.filter(is_read=False).order_by('-created_at')
    else:
        notification = Notification.objects.all().order_by('-created_at')

    # Render the template with filtered notifications
    return render(request, 'UAMS_App/select_notification.html', {'notification': notification})

@login_required
def review_notification(request, notification_id):
    notification = Notification.objects.get(notification_id=notification_id)
    if not notification.is_read:
        notification.is_read = True
        notification.save()
    return render(request, 'UAMS_App/review_notification.html', {'notification': notification})

@login_required
def admin_home(request):
    # Check if the logged-in user is a superuser
    if not request.user.is_superuser:
        return HttpResponseForbidden("You are not authorized to access this page.")
    
    # If the user is an admin, render the admin home page
    return render(request, 'UAMS_App/admin_home.html')


from django.shortcuts import render, get_object_or_404, redirect
from .models import AidApplication

def select_application(request):
    # Get applications with a 'pending' status
    applications = AidApplication.objects.filter(application_status='pending')

    return render(request, 'UAMS_App/select_application.html', {'applications': applications})

def review_application(request, application_id):
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

def review_application_step2(request, application_id):
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
                application.rejection_reason = rejection_reason

            # Save the application
            application.save()

            return redirect('select_application')  # Redirect after form submission

    return render(request, 'UAMS_App/review_application_step2.html', {'application': application})

def select_aid_record(request):
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
    
def review_aid(request, application_id):
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

def review_aid_step2(request, application_id):
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
                application.rejection_reason = rejection_reason

            # Save the application
            application.save()

            return redirect('select_aid_record')  # Redirect after form submission

    return render(request, 'UAMS_App/review_aid_step2.html', {'application': application})

def select_feedback(request):
    feedbacks = Feedback.objects.filter(feedback_status='pending')  # Only get pending feedbacks
    return render(request, 'UAMS_App/select_feedback.html', {'feedbacks': feedbacks})

def response_feedback(request, feedback_id):
    feedback = get_object_or_404(Feedback, feedback_id=feedback_id)

    if request.method == 'POST':
        # Update the feedback response if a response is provided
        feedback.response = request.POST.get('response')
        feedback.feedback_status = 'responded'  # Update status to responded
        feedback.save()
        # Optionally redirect after saving the response, e.g., back to the list or to a success page
        return redirect('select_feedback')  # Replace with your redirect URL
    
    return render(request, 'UAMS_App/response_feedback.html', {'feedback': feedback})