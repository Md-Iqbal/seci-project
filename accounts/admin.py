from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import AccountApplication, ApplicationLog

# Customize admin site
admin.site.site_header = "সোনালী ব্যাংক পিএলসি - প্রশাসন"
admin.site.site_title = "সোনালী ব্যাংক প্রশাসন"
admin.site.index_title = "প্রশাসনিক ড্যাশবোর্ডে স্বাগতম"

@admin.register(AccountApplication)
class AccountApplicationAdmin(admin.ModelAdmin):
    list_display = [
        'application_number_link', 'full_name_eng', 'nid_number',
        'account_type_display', 'status_badge', 'application_date_formatted',
        'account_number', 'action_buttons'
    ]
    list_filter = ['status', 'account_type', 'application_date', 'gender']
    search_fields = [
        'application_number', 'full_name_eng', 'nid_number',
        'mobile_number', 'account_number', 'email'
    ]
    readonly_fields = [
        'application_number', 'application_date', 'account_number',
        'approved_by', 'approval_date', 'photo_preview', 'signature_preview'
    ]
    
    date_hierarchy = 'application_date'
    
    # fieldsets = (
    #     ('আবেদন তথ্য', {
    #         'fields': ('application_number', 'application_date', 'status'),
    #         'classes': ('wide',)
    #     }),
    #     ('ব্যক্তিগত তথ্য', {
    #         'fields': (
    #             'full_name_eng', 'father_name', 'mother_name',
    #             'date_of_birth', 'gender', 'nid_number'
    #         ),
    #         'classes': ('wide',)
    #     }),
    #     ('যোগাযোগ তথ্য', {
    #         'fields': (
    #             'mobile_number', 'email', 'present_address',
    #             'permanent_address', 'city', 'postal_code'
    #         ),
    #         'classes': ('wide',)
    #     }),
    #     ('হিসাব বিবরণ', {
    #         'fields': ('account_type', 'initial_deposit', 'account_number'),
    #         'classes': ('wide',)
    #     }),
    #     ('নথিপত্র', {
    #         'fields': ('photo_preview', 'photograph', 'signature_preview', 
    #                   'signature', 'nid_copy'),
    #         'classes': ('wide',)
    #     }),
    #     ('নমিনি তথ্য', {
    #         'fields': (
    #             'nominee_name', 'nominee_relation',
    #             'nominee_nid', 'nominee_mobile'
    #         ),
    #         'classes': ('collapse',)
    #     }),
    #     ('অনুমোদন তথ্য', {
    #         'fields': (
    #             'approved_by', 'approval_date', 'rejection_reason'
    #         ),
    #         'classes': ('wide',)
    #     }),
    # )
    
    actions = ['approve_applications', 'reject_applications']
    
    def application_number_link(self, obj):
        url = reverse('admin:accounts_accountapplication_change', args=[obj.pk])
        return format_html('<a href="{}">{}</a>', url, obj.application_number)
    application_number_link.short_description = 'আবেদন নম্বর'
    
    def account_type_display(self, obj):
        type_map = {
            'SAVINGS': 'সঞ্চয়ী',
            'CURRENT': 'চলতি',
            'SND': 'এসএনডি',
            'FC': 'এফসি',
            'RFCD': 'আরএফসিডি',
            'NFCD': 'এনএফসিডি',
            'OTHERS': 'অন্যান্য',
        }
        return type_map.get(obj.account_type, obj.account_type)
    account_type_display.short_description = 'হিসাবের ধরন'
    
    def status_badge(self, obj):
        colors = {
            'PENDING': '#f39c12',
            'APPROVED': '#27ae60',
            'REJECTED': '#c0392b'
        }
        labels = {
            'PENDING': 'অপেক্ষমাণ',
            'APPROVED': 'অনুমোদিত',
            'REJECTED': 'প্রত্যাখ্যাত'
        }
        color = colors.get(obj.status, '#95a5a6')
        label = labels.get(obj.status, obj.status)
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-weight: bold;">{}</span>',
            color, label
        )
    status_badge.short_description = 'অবস্থা'
    
    def application_date_formatted(self, obj):
        bengali_months = [
            'জানুয়ারি', 'ফেব্রুয়ারি', 'মার্চ', 'এপ্রিল', 'মে', 'জুন',
            'জুলাই', 'আগস্ট', 'সেপ্টেম্বর', 'অক্টোবর', 'নভেম্বর', 'ডিসেম্বর'
        ]
        date = obj.application_date
        return f"{date.day} {bengali_months[date.month-1]}, {date.year}"
    application_date_formatted.short_description = 'আবেদনের তারিখ'
    
    def action_buttons(self, obj):
        buttons = []
        
        if obj.status == 'PENDING':
            approve_url = reverse('admin:accounts_accountapplication_change', args=[obj.pk])
            buttons.append(
                f'<a class="button" href="{approve_url}" '
                f'style="background-color: #27ae60; color: white; padding: 5px 10px; '
                f'border-radius: 3px; text-decoration: none;">অনুমোদন</a>'
            )
        
        detail_url = reverse('application_detail', args=[obj.application_number])
        buttons.append(
            f'<a class="button" href="{detail_url}" target="_blank" '
            f'style="background-color: #3498db; color: white; padding: 5px 10px; '
            f'border-radius: 3px; text-decoration: none; margin-left: 5px;">দেখুন</a>'
        )
        
        return format_html(' '.join(buttons))
    action_buttons.short_description = 'কার্যক্রম'
    
    def photo_preview(self, obj):
        if obj.photograph:
            return mark_safe(f'<img src="{obj.photograph.url}" width="150" />')
        return "কোনো ছবি নেই"
    photo_preview.short_description = 'ছবি পূর্বরূপ'
    
    def signature_preview(self, obj):
        if obj.signature:
            return mark_safe(f'<img src="{obj.signature.url}" width="200" />')
        return "কোনো স্বাক্ষর নেই"
    signature_preview.short_description = 'স্বাক্ষর পূর্বরূপ'
    
    def approve_applications(self, request, queryset):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        count = 0
        for application in queryset.filter(status='PENDING'):
            application.approve(request.user)
            count += 1
        
        self.message_user(request, f'{count}টি আবেদন অনুমোদিত হয়েছে।')
    approve_applications.short_description = 'নির্বাচিত আবেদন অনুমোদন করুন'
    
    def reject_applications(self, request, queryset):
        count = 0
        for application in queryset.filter(status='PENDING'):
            application.reject(request.user, 'প্রশাসক দ্বারা প্রত্যাখ্যাত')
            count += 1
        
        self.message_user(request, f'{count}টি আবেদন প্রত্যাখ্যান করা হয়েছে।')
    reject_applications.short_description = 'নির্বাচিত আবেদন প্রত্যাখ্যান করুন'

@admin.register(ApplicationLog)
class ApplicationLogAdmin(admin.ModelAdmin):
    list_display = ['application_link', 'action_display', 'performed_by', 'timestamp_formatted']
    list_filter = ['action', 'timestamp']
    search_fields = ['application__application_number', 'details']
    readonly_fields = ['application', 'action', 'performed_by', 'timestamp', 'details']
    date_hierarchy = 'timestamp'
    
    def application_link(self, obj):
        url = reverse('application_detail', args=[obj.application.application_number])
        return format_html('<a href="{}" target="_blank">{}</a>', 
                          url, obj.application.application_number)
    application_link.short_description = 'আবেদন নম্বর'
    
    def action_display(self, obj):
        action_map = {
            'APPLICATION_CREATED': '✅ আবেদন তৈরি',
            'APPLICATION_APPROVED': '✔️ অনুমোদিত',
            'APPLICATION_REJECTED': '❌ প্রত্যাখ্যাত',
            'APPLICATION_PRINTED': '🖨️ প্রিন্ট',
            'APPLICATION_AUTO_DELETED': '🗑️ স্বয়ংক্রিয় মুছে ফেলা'
        }
        return action_map.get(obj.action, obj.action)
    action_display.short_description = 'কার্যক্রম'
    
    def timestamp_formatted(self, obj):
        bengali_months = [
            'জানুয়ারি', 'ফেব্রুয়ারি', 'মার্চ', 'এপ্রিল', 'মে', 'জুন',
            'জুলাই', 'আগস্ট', 'সেপ্টেম্বর', 'অক্টোবর', 'নভেম্বর', 'ডিসেম্বর'
        ]
        date = obj.timestamp
        return f"{date.day} {bengali_months[date.month-1]}, {date.year} {date.strftime('%H:%M')}"
    timestamp_formatted.short_description = 'সময়'