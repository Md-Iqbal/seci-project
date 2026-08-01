from rest_framework import serializers
from django.contrib.auth.models import User
from .models import AccountApplication, ApplicationLog, ApplicationStatus
from bonds.models import WageEarnersBond, USDBond, ApplicationStatus
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
        fields = '__all__'

class WEBListSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = WageEarnersBond
        fields = '__all__'

class USDBListSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = USDBond
        fields = '__all__'

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
        # Check if NID already has an approved or rejected application
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
    
    
    def create(self, validated_data):
        application = AccountApplication.objects.create(**validated_data)
        
        # Create log
        ApplicationLog.objects.create(
            application=application,
            action='APPLICATION_CREATED',
            details=f'আবেদন জমা দেওয়া হয়েছে: {application.account_title_Eng}'
        )
        
        return application
    
    def to_representation(self, instance):
        """Customize the response to include essential fields"""
        representation = super().to_representation(instance)
        # Ensure application_number is in the response
        representation['application_number'] = instance.application_number
        representation['application_date'] = instance.application_date
        representation['status'] = instance.status
        representation['account_title_Eng'] = instance.account_title_Eng
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
    pending_Acc = serializers.IntegerField()
    pending_WEB = serializers.IntegerField()
    pending_USDB = serializers.IntegerField()
    approved_Acc = serializers.IntegerField()
    approved_WEB = serializers.IntegerField()
    approved_USDB = serializers.IntegerField()
    rejected_Acc = serializers.IntegerField()
    rejected_WEB = serializers.IntegerField()
    rejected_USDB = serializers.IntegerField()
    pending_count = serializers.IntegerField()
    approved_count = serializers.IntegerField()
    rejected_count = serializers.IntegerField()
    total_count = serializers.IntegerField()
    recent_applications = AccountApplicationListSerializer(many=True)
    recent_WEBapplications = WEBListSerializer(many=True)
    recent_USDBapplications = USDBListSerializer(many=True)