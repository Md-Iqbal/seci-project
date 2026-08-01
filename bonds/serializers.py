from rest_framework import serializers
from django.contrib.auth.models import User

from accounts.models import AccountApplication
from .models import WageEarnersBond, USDBond
import base64
from django.core.files.base import ContentFile

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']

class BondApprovalLogSerializer(serializers.ModelSerializer):
    performed_by = UserSerializer(read_only=True)
class WageEarnersBondListSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    
    class Meta:
        model = WageEarnersBond
        fields = '__all__'

        read_only_fields = (
            "application_no",
            "application_date",
            "total_amount",
            "status",
            "approved_by",
            "approval_date",
            "created_at",
            "updated_at"
        )

class USDBondListSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    
    class Meta:
        model = USDBond
        fields = '__all__'

        read_only_fields = (
            "application_no",
            "application_date",
            "status",
            "approved_by",
            "approval_date",
            "created_at",
            "updated_at",
        )
class WageEarnersBondDetailSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    account_type_display = serializers.CharField(source='get_account_type_display', read_only=True)
    gender_display = serializers.CharField(source='get_gender_display', read_only=True)
    approved_by = UserSerializer(read_only=True)
    logs = BondApprovalLogSerializer(many=True, read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = WageEarnersBond
        fields = '__all__'
        read_only_fields = [
            'application_no', 'application_date', 'approved_by',
            'approval_date'
        ]
class USDBondBondDetailSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    account_type_display = serializers.CharField(source='get_account_type_display', read_only=True)
    gender_display = serializers.CharField(source='get_gender_display', read_only=True)
    approved_by = UserSerializer(read_only=True)
    logs = BondApprovalLogSerializer(many=True, read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = USDBond
        fields = '__all__'
        read_only_fields = [
            'application_no', 'application_date', 'approved_by',
            'approval_date'
        ]