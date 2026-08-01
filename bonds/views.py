from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.template.loader import render_to_string
from playwright.sync_api import sync_playwright
from datetime import datetime
from .models import *
from .forms import *
from accounts.forms import ApplicationApprovalForm
import logging

logger = logging.getLogger('bonds')

def is_bank_employee(user):
    """Check if user is a bank employee (staff)"""
    return user.is_staff
class WageEarnersBondCreateView(CreateView):

    model = WageEarnersBond

    form_class = WageEarnersBondForm

    template_name = "bonds/apply.html"

    success_url = reverse_lazy("bond-list")

    def form_valid(self, form):

        return super().form_valid(form)

def application_success(request, application_no):
    """Success page after application submission"""
    # application = get_object_or_404(WageEarnersBond, application_no=application_no)
    application = WageEarnersBond.objects.filter(
        application_no=application_no
    ).first()

    if application is None:
        application = get_object_or_404(
            USDBond,
            application_no=application_no
        )
    
    context = {
        'application': application,
        'page_title': 'আবেদন সফল'
    }
    return render(request, 'bonds/success.html', context)
def search_application(request):
    """Search application/account by application_no"""
    applications = None
    
    if request.method == 'POST':
        form = ApplicationSearchForm(request.POST)
        if form.is_valid():
            application_no = form.cleaned_data['application_no']
            applications = WageEarnersBond.objects.filter(
                application_no=application_no
            ).order_by('-application_date')
            
            if not applications.exists():
                messages.info(request, 'এই এনআইডি নম্বর দিয়ে কোনো আবেদন পাওয়া যায়নি।')
            else:
                logger.info(f'Application no search: {application_no}, Found: {applications.count()} bonds')
    else:
        form = ApplicationSearchForm()
    
    context = {
        'form': form,
        'applications': applications,
        'page_title': 'Find application'
    }
    return render(request, 'bonds/search.html', context)

def bond_detail_public(request, application_no):
    """Public view of application details"""
    bond = WageEarnersBond.objects.filter(
            application_no=application_no
        ).first()

    if bond is None:
        bond = get_object_or_404(
            USDBond,
            application_no=application_no
        )
        
    
    # Get status in Bengali
    status_bengali = {
        'PENDING': 'PENDING',
        'APPROVED': 'APPROVED',
        'REJECTED': 'REJECTED'
    }
    
    context = {
        'bond': bond,
        'page_title': 'Application Details',
        'status_bengali': status_bengali.get(bond.status, bond.status),
    }
    return render(request, 'bonds/bond_detail.html', context)

#usd investment/premium bond
class USDBondCreateView(CreateView):

    model = USDBond

    form_class = USDBondForm

    template_name = "bonds/USD bond apply.html"

    success_url = reverse_lazy("bond-list")

    def form_valid(self, form):

        return super().form_valid(form)

@login_required
@user_passes_test(is_bank_employee)
def process_applicationBond(request, application_no):
    """Approve or reject application"""
    application = USDBond.objects.filter(application_no=application_no).first()

    if application:
        is_usd = True
    else:
        application = get_object_or_404(
            WageEarnersBond,
            application_no=application_no
        )
        is_usd = False
    
    if request.method == 'POST':
        form = ApplicationApprovalForm(request.POST)
        if form.is_valid():
            action = form.cleaned_data['action']
            
            try:
                if action == 'approve':
                    application.approve(request.user)
                    
                    if is_usd:
                        USDBondApprovalLog.objects.create(
                            application=application,
                            action="APPLICATION_APPROVED",
                            performed_by=request.user,
                            details=f"Application No: {application.application_no}"
                        )
                    else:
                        BondApprovalLog.objects.create(
                            application=application,
                            action="APPLICATION_APPROVED",
                            performed_by=request.user,
                            details=f"Application No: {application.application_no}"
                        )
                    
                    logger.info(f'Application {application_no} approved by {request.user.username}')
                    
                    messages.success(
                        request,
                        f'Application Approved! Application No: {application.application_no}'
                    )
                else:
                    reason = form.cleaned_data['rejection_reason']
                    application.reject(request.user, reason)
                    
                    if is_usd:
                        USDBondApprovalLog.objects.create(
                            application=application,
                            action="APPLICATION_REJECTED",
                            performed_by=request.user,
                            details=f"Reason: {reason}"
                        )
                    else:
                        BondApprovalLog.objects.create(
                            application=application,
                            action="APPLICATION_REJECTED",
                            performed_by=request.user,
                        )
                    
                    logger.info(f'Application {application_no} rejected by {request.user.username}')
                    
                    messages.success(request, 'Application Rejected')
                
                if is_usd:
                    return redirect(
                        "application_detail_public",
                        application_no=application.application_no
                    )
                else:
                    return redirect(
                        "application_detail",
                        application_no=application.application_no
                    )
                
            except Exception as e:
                logger.error(f'Error processing application {application_no}: {str(e)}')
                messages.error(request, 'Error in processing application.')
    else:
        form = ApplicationApprovalForm()
    
    context = {
        'application': application,
        'form': form,
        'page_title': 'Process Application'
    }
    
    return render(request, 'bonds/process_applicationBond.html', context)

@login_required
@user_passes_test(lambda u: u.is_staff)
def print_application(request, application_no):
    bond_type = request.GET.get("type")
    app = USDBond.objects.filter(
        application_no=application_no
    ).first()
    if app:
        template = "bonds/print_application.html"
    else:
        app = get_object_or_404(
            WageEarnersBond,
            application_no=application_no
        )
        template = "bonds/print_application WEB.html"
    
    context = {
        'application': app,
        'today': datetime.now().strftime("%d/%m/%Y")
    }

    html_string = render_to_string(template, context)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        
        # Critical: Wait for fonts and CSS to fully load
        page.set_content(html_string, wait_until="networkidle")
        
        pdf_bytes = page.pdf(
            format="A4",
            print_background=True,
            margin={
                "top":"0",
                "bottom":"0",
                "left":"0",
                "right":"0"
            }
        )
        browser.close()

    response = HttpResponse(pdf_bytes, content_type="application/pdf")
    response["Content-Disposition"] = f'inline; filename="Sonali_Bank_Form_{application_no}.pdf"'
    
    return response