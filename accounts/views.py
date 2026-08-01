from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import HttpResponse
from django.template.loader import get_template
from django.db.models import Q
from django.core.paginator import Paginator
from django.utils import timezone
from itertools import chain
from operator import attrgetter
from .models import AccountApplication, ApplicationLog, ApplicationStatus
from bonds.models import WageEarnersBond, USDBond
from .forms import AccountApplicationForm, ApplicationSearchForm, ApplicationApprovalForm
import logging

logger = logging.getLogger('accounts')

def is_bank_employee(user):
    """Check if user is a bank employee (staff)"""
    return user.is_staff

# Public Views
def home(request):
    """Home page with Bengali content"""
    context = {
        'page_title': 'প্রধান পাতা',
    }
    return render(request, 'accounts/home.html', context)

def apply_account(request):
    """Account application form for public users"""
    if request.method == 'POST':
        form = AccountApplicationForm(request.POST, request.FILES)

        if form.is_valid():
            try:
                application = form.save()
                
                # Log the creation
                ApplicationLog.objects.create(
                    application=application,
                    action='APPLICATION_CREATED',
                    details=f'আবেদন জমা দেওয়া হয়েছে: {application.full_name}'
                )
                
                logger.info(f'New application created: {application.application_number}')
                
                messages.success(
                    request,
                    f'আবেদন সফলভাবে জমা হয়েছে! আপনার আবেদন নম্বর: {application.application_number}। '
                    f'অনুগ্রহ করে এই নম্বরটি সংরক্ষণ করুন।'
                )
                return redirect('application_success', app_number=application.application_number)
            except Exception as e:
                logger.error(f'Error creating application: {str(e)}')
                messages.error(request, 'আবেদন জমা দিতে সমস্যা হয়েছে। অনুগ্রহ করে আবার চেষ্টা করুন।')
    else:
        form = AccountApplicationForm()
    
    context = {
        'form': form,
        'page_title': 'হিসাব খোলার আবেদন'
    }
    return render(request, 'accounts/apply.html', context)

def application_success(request, app_number):
    """Success page after application submission"""
    application = get_object_or_404(AccountApplication, application_number=app_number)
    
    context = {
        'application': application,
        'page_title': 'আবেদন সফল'
    }
    return render(request, 'accounts/success.html', context)

def search_application(request):
    """Search application/account by NID"""
    applications = None
    
    if request.method == 'POST':
        form = ApplicationSearchForm(request.POST)
        if form.is_valid():
            nid = form.cleaned_data['nid_number']
            applications = AccountApplication.objects.filter(
                nid_number=nid
            ).order_by('-application_date')
            
            if not applications.exists():
                messages.info(request, 'এই এনআইডি নম্বর দিয়ে কোনো আবেদন পাওয়া যায়নি।')
            else:
                logger.info(f'NID search: {nid}, Found: {applications.count()} applications')
    else:
        form = ApplicationSearchForm()
    
    context = {
        'form': form,
        'applications': applications,
        'page_title': 'আবেদন খুঁজুন'
    }
    return render(request, 'accounts/search.html', context)

def application_detail_public(request, app_number):
    """Public view of application details"""
    application = get_object_or_404(AccountApplication, application_number=app_number)
    
    # Get Bengali month names
    bengali_months = [
        'জানুয়ারি', 'ফেব্রুয়ারি', 'মার্চ', 'এপ্রিল', 'মে', 'জুন',
        'জুলাই', 'আগস্ট', 'সেপ্টেম্বর', 'অক্টোবর', 'নভেম্বর', 'ডিসেম্বর'
    ]
    
    # Get status in Bengali
    status_bengali = {
        'PENDING': 'অপেক্ষমাণ',
        'APPROVED': 'অনুমোদিত',
        'REJECTED': 'প্রত্যাখ্যাত'
    }
    
    # Get account type in Bengali
    account_type_bengali = {
        'SAVINGS': 'সঞ্চয়ী হিসাব',
        'CURRENT': 'চলতি হিসাব',
        'FD': 'স্থায়ী আমানত'
    }
    
    context = {
        'application': application,
        'page_title': 'আবেদনের বিস্তারিত',
        'bengali_months': bengali_months,
        'status_bengali': status_bengali.get(application.status, application.status),
        'account_type_bengali': account_type_bengali.get(application.account_type, application.account_type)
    }
    return render(request, 'accounts/application_detail.html', context)

# Employee Views
from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from django.contrib import messages

def custom_login(request):
    """Custom login view with Bengali messages"""
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('dashboard')
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            
            # Log the login
            logger.info(f'User logged in: {username}')
            
            messages.success(request, f'স্বাগতম, {user.get_full_name() or username}!')
            
            # Redirect to dashboard if staff, otherwise home
            if user.is_staff:
                return redirect('dashboard')
            else:
                return redirect('home')
        else:
            messages.error(request, 'ভুল ব্যবহারকারীর নাম অথবা পাসওয়ার্ড।')
    
    return render(request, 'accounts/login.html')


@login_required
def profile(request):
    """User profile page - redirect to appropriate dashboard"""
    if request.user.is_staff:
        return redirect('dashboard')
    else:
        messages.info(request, 'আপনার কোনো প্রোফাইল নেই। হিসাব খুলতে আবেদন করুন।')
        return redirect('apply_account')
    

@login_required
@user_passes_test(is_bank_employee)
def dashboard(request):
    """Employee dashboard with Bengali labels"""
    pending_count = AccountApplication.objects.filter(
        status=ApplicationStatus.PENDING
    ).count()
    
    approved_count = AccountApplication.objects.filter(
        status=ApplicationStatus.APPROVED
    ).count()
    
    rejected_count = AccountApplication.objects.filter(
        status=ApplicationStatus.REJECTED
    ).count()
    
    recent_applications = AccountApplication.objects.all()[:10]
    
    context = {
        'pending_count': pending_count,
        'approved_count': approved_count,
        'rejected_count': rejected_count,
        'recent_applications': recent_applications,
        'page_title': 'ড্যাশবোর্ড'
    }
    
    logger.info(f'Dashboard accessed by: {request.user.username}')
    
    return render(request, 'accounts/dashboard.html', context)

@login_required
@user_passes_test(is_bank_employee)
def application_list(request):
    app_type = request.GET.get("type", "")
    search = request.GET.get("search", "").strip()

    status_labels = {
        "PENDING": "PENDING",
        "APPROVED": "APPROVED",
        "REJECTED": "REJECTED",
    }

    # ---------------- SEARCH ----------------
    if search:

        if app_type == "Account":
            applications = AccountApplication.objects.filter(
                Q(application_number__icontains=search) |
                Q(full_name__icontains=search) |
                Q(nid_number__icontains=search) |
                Q(mobile_number__icontains=search) |
                Q(account_number__icontains=search)
            ).order_by("-application_date")

        elif app_type == "Wage":
            applications = WageEarnersBond.objects.filter(
                Q(application_no__icontains=search) |
                Q(applicant_name__icontains=search) |
                Q(passport_no__icontains=search) |
                Q(mobile_no__icontains=search)
            ).order_by("-application_date")

        elif app_type == "USD":
            applications = USDBond.objects.filter(
                Q(application_no__icontains=search) |
                Q(applicant_name__icontains=search) |
                Q(passport_no__icontains=search) |
                Q(applicant_contact__icontains=search)
            ).order_by("-application_date")

        else:
            applications = []

    # ---------------- NO SEARCH ----------------
    else:

        accounts = list(AccountApplication.objects.all())
        wages = list(WageEarnersBond.objects.all())
        usds = list(USDBond.objects.all())

        for obj in accounts:
            obj.app_type = "Account"

        for obj in wages:
            obj.app_type = "Wage"

        for obj in usds:
            obj.app_type = "USD"

        applications = sorted(
            chain(accounts, wages, usds),
            key=attrgetter("application_date"),
            reverse=True,
        )

    paginator = Paginator(applications, 20)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "page_obj": page_obj,
        "applications": applications,
        "status_filter": app_type,
        "search_query": search,
        "status_labels": status_labels,
        "page_title": "সকল আবেদন",
    }

    return render(request, "accounts/application_list.html", context)

@login_required
@user_passes_test(is_bank_employee)
def application_detail(request, app_number):
    """Detailed view of application for employees"""
    application = get_object_or_404(AccountApplication, application_number=app_number)
    logs = application.logs.all()
    
    # Get Bengali labels
    status_bengali = {
        'PENDING': 'অপেক্ষমাণ',
        'APPROVED': 'অনুমোদিত',
        'REJECTED': 'প্রত্যাখ্যাত'
    }
    
    account_type_bengali = {
        'SAVINGS': 'সঞ্চয়ী',
        'CURRENT': 'চলতি',
        'SND': 'এসএনডি',
        'FC': 'এফসি',
        'RFCD': 'আরএফসিডি',
        'NFCD': 'এনএফসিডি',
        'OTHERS': 'অন্যান্য'
    }
    
    gender_bengali = {
        'M': 'পুরুষ',
        'F': 'মহিলা',
        'O': 'অন্যান্য'
    }
    
    context = {
        'application': application,
        'logs': logs,
        'page_title': 'আবেদনের বিস্তারিত',
        'status_bengali': status_bengali.get(application.status, application.status),
        'account_type_bengali': account_type_bengali.get(application.account_type, application.account_type),
        'gender_bengali': gender_bengali.get(application.gender, application.gender)
    }
    
    logger.info(f'Application {app_number} viewed by: {request.user.username}')
    
    return render(request, 'accounts/application_detail.html', context)

@login_required
@user_passes_test(is_bank_employee)
def process_application(request, app_number):
    """Approve or reject application"""
    application = get_object_or_404(
        AccountApplication,
        application_number=app_number,
        status=ApplicationStatus.PENDING
    )
    
    if request.method == 'POST':
        form = ApplicationApprovalForm(request.POST)
        if form.is_valid():
            action = form.cleaned_data['action']
            
            try:
                if action == 'approve':
                    application.approve(request.user)
                    
                    ApplicationLog.objects.create(
                        application=application,
                        action='APPLICATION_APPROVED',
                        performed_by=request.user,
                        details=f'হিসাব নম্বর: {application.account_number}'
                    )
                    
                    logger.info(f'Application {app_number} approved by {request.user.username}')
                    
                    messages.success(
                        request,
                        f'আবেদন অনুমোদিত হয়েছে! হিসাব নম্বর: {application.account_number}'
                    )
                else:
                    reason = form.cleaned_data['rejection_reason']
                    application.reject(request.user, reason)
                    
                    ApplicationLog.objects.create(
                        application=application,
                        action='APPLICATION_REJECTED',
                        performed_by=request.user,
                        details=f'কারণ: {reason}'
                    )
                    
                    logger.info(f'Application {app_number} rejected by {request.user.username}')
                    
                    messages.success(request, 'আবেদন প্রত্যাখ্যান করা হয়েছে।')
                
                return redirect('application_detail', app_number=app_number)
                
            except Exception as e:
                logger.error(f'Error processing application {app_number}: {str(e)}')
                messages.error(request, 'আবেদন প্রক্রিয়া করতে সমস্যা হয়েছে।')
    else:
        form = ApplicationApprovalForm()
    
    context = {
        'application': application,
        'form': form,
        'page_title': 'আবেদন প্রক্রিয়া করুন'
    }
    
    return render(request, 'accounts/process_application.html', context)

import pdfkit
import os
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import AccountApplication, ApplicationLog

def is_bank_employee(user):
    return user.is_staff

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required, user_passes_test
from playwright.sync_api import sync_playwright
from datetime import datetime
from django.contrib.staticfiles import finders
from pathlib import Path
import base64
@login_required
@user_passes_test(lambda u: u.is_staff)
def print_application(request, app_number):
    application = get_object_or_404(AccountApplication, application_number=app_number)
    img_path = finders.find('logo/logo.png')


    with open(img_path, "rb") as f:
        logo_base64 = base64.b64encode(f.read()).decode()

    context = {
        'application': application,
        'today': datetime.now().strftime("%d/%m/%Y"),
        'img_path': logo_base64,
        # Add your model fields here for auto-filling
        'account_title_bn': application.account_title_bn if hasattr(application, 'account_title_bn') else '',
        'account_title_en': application.account_title_en if hasattr(application, 'account_title_en') else '',
        'father_name': application.father_name if hasattr(application, 'father_name') else '',
        'mother_name': application.mother_name if hasattr(application, 'mother_name') else '',
        'dob': application.date_of_birth.strftime("%d/%m/%Y") if hasattr(application, 'date_of_birth') and application.date_of_birth else '',
        'nid': application.nid if hasattr(application, 'nid') else '',
        # Add more fields as needed...
    }

    html_string = render_to_string('accounts/print_application.html', context)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        
        # Critical: Wait for fonts and CSS to fully load
        page.set_content(html_string, wait_until="networkidle")
        
        pdf_bytes = page.pdf(
            format="A4",
            # margin={"top": "0px", "bottom": "0px", "left": "0px", "right": "0px"},
            print_background=True,
            scale=0.98,                    # Slight scale adjustment helps with borders
        )
        browser.close()

    response = HttpResponse(pdf_bytes, content_type="application/pdf")
    response["Content-Disposition"] = f'inline; filename="Sonali_Bank_Form_{app_number}.pdf"'
    
    return response