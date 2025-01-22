# UAMS_App/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate
from .models import Profile
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden


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
    
    # Pass the profile and user details to the template
    return render(request, 'UAMS_App/student_home.html', {'profile': profile})

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