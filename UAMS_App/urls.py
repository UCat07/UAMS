# UAMS_App/urls.py
from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView


urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.custom_logout, name='logout'),  # Log out and redirect
    
    path('student_home/', views.student_home, name='student_home'),
    path('submit/', views.submit_application, name='submit_application'),
    path('submit_application_success/<str:application_id>/', views.submit_application_success, name='submit_application_success'),
    path('track_application_status/', views.track_application_status, name='track_application_status'),
    
    path('admin_home/', views.admin_home, name='admin_home'),
    path('select_application/', views.select_application, name='select_application'),
    path('review_application/<str:application_id>/', views.review_application, name='review_application'),
    path('review_application_step2/<str:application_id>/', views.review_application_step2, name='review_application_step2'),
]
