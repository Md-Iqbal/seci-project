from rest_framework import serializers
from django.contrib.auth.models import User
from .models import AccountApplication, ApplicationLog, ApplicationStatus
import base64
from django.core.files.base import ContentFile

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']

class ApplicationLogSerializer(serializers.ModelSerializer):
    performed_by = UserSerializer(read_only=True)
    
    class Meta:
        model = ApplicationLog
        fields = ['id', 'action', 'performed_by', 'timestamp', 'details']

class AccountApplicationListSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    account_type_display = serializers.CharField(source='get_account_type_display', read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = AccountApplication
        fields = [
            'id', 'application_number', 'application_date', 'status',
            'status_display', 'full_name', 'nid_number', 'mobile_number',
            'account_type', 'account_type_display', 'account_number',
            'initial_deposit', 'is_expired'
        ]

class AccountApplicationDetailSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    account_type_display = serializers.CharField(source='get_account_type_display', read_only=True)
    gender_display = serializers.CharField(source='get_gender_display', read_only=True)
    approved_by = UserSerializer(read_only=True)
    logs = ApplicationLogSerializer(many=True, read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = AccountApplication
        fields = '__all__'
        read_only_fields = [
            'application_number', 'application_date', 'approved_by',
            'approval_date', 'account_number'
        ]

class AccountApplicationCreateSerializer(serializers.ModelSerializer):
    # Add this to return the application number in response
    application_number = serializers.CharField(read_only=True)
    
    class Meta:
        model = AccountApplication
        exclude = [
            'status', 'approved_by',
            'approval_date', 'rejection_reason', 'account_number'
        ]
        read_only_fields = ['application_number']  # Make it read-only
    
    def validate_nid_number(self, value):
        # Check if NID already has an approved application
        existing = AccountApplication.objects.filter(
            nid_number=value,
            status=ApplicationStatus.APPROVED
        ).exists()
        if existing:
            raise serializers.ValidationError(
                "এই এনআইডি নম্বর দিয়ে ইতিমধ্যে একটি হিসাব আছে।"
            )
        return value
    
    def validate_initial_deposit(self, value):
        if value < 500:
            raise serializers.ValidationError(
                "সর্বনিম্ন প্রাথমিক জমা ৫০০ টাকা"
            )
        return value
    
    def validate_photograph(self, value):
        if not value:
            raise serializers.ValidationError("ছবি আপলোড করা আবশ্যক")
        
        # Check file size (max 5MB)
        if value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError("ছবির সাইজ ৫ এমবি এর বেশি হতে পারবে না")
        
        # Check file type
        if not value.content_type.startswith('image/'):
            raise serializers.ValidationError("শুধুমাত্র ছবি ফাইল আপলোড করুন")
        
        return value
    
    def validate_nid_copy(self, value):
        if not value:
            raise serializers.ValidationError("এনআইডি কপি আপলোড করা আবশ্যক")
        
        # Check file size (max 5MB)
        if value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError("ফাইলের সাইজ ৫ এমবি এর বেশি হতে পারবে না")
        
        return value
    
    def validate_signature(self, value):
        if not value:
            raise serializers.ValidationError("স্বাক্ষর আপলোড করা আবশ্যক")
        
        # Check file size (max 2MB)
        if value.size > 2 * 1024 * 1024:
            raise serializers.ValidationError("স্বাক্ষরের সাইজ ২ এমবি এর বেশি হতে পারবে না")
        
        # Check file type
        if not value.content_type.startswith('image/'):
            raise serializers.ValidationError("শুধুমাত্র ছবি ফাইল আপলোড করুন")
        
        return value
    
    def create(self, validated_data):
        application = AccountApplication.objects.create(**validated_data)
        
        # Create log
        ApplicationLog.objects.create(
            application=application,
            action='APPLICATION_CREATED',
            details=f'আবেদন জমা দেওয়া হয়েছে: {application.full_name}'
        )
        
        return application
    
    def to_representation(self, instance):
        """Customize the response to include essential fields"""
        representation = super().to_representation(instance)
        # Ensure application_number is in the response
        representation['application_number'] = instance.application_number
        representation['application_date'] = instance.application_date
        representation['status'] = instance.status
        representation['full_name'] = instance.full_name
        return representation

class ApplicationApprovalSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=['approve', 'reject'])
    rejection_reason = serializers.CharField(required=False, allow_blank=True)
    
    def validate(self, data):
        if data['action'] == 'reject' and not data.get('rejection_reason'):
            raise serializers.ValidationError({
                'rejection_reason': 'Rejection reason is required when rejecting an application.'
            })
        return data

class DashboardStatsSerializer(serializers.Serializer):
    pending_count = serializers.IntegerField()
    approved_count = serializers.IntegerField()
    rejected_count = serializers.IntegerField()
    total_count = serializers.IntegerField()
    recent_applications = AccountApplicationListSerializer(many=True)