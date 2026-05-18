from rest_framework import viewsets, status, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from .models import AccountApplication, ApplicationLog, ApplicationStatus
from .serializers import (
    AccountApplicationListSerializer,
    AccountApplicationDetailSerializer,
    AccountApplicationCreateSerializer,
    ApplicationApprovalSerializer,
    ApplicationLogSerializer,
    DashboardStatsSerializer
)
import logging

logger = logging.getLogger('accounts')

class IsStaffUser(IsAuthenticated):
    """Permission class for staff users only"""
    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.is_staff

class AccountApplicationViewSet(viewsets.ModelViewSet):
    queryset = AccountApplication.objects.all()
    parser_classes = [MultiPartParser, FormParser, JSONParser]  # Important!
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'account_type']
    search_fields = ['application_number', 'full_name', 'nid_number', 'mobile_number', 'account_number']
    ordering_fields = ['application_date', 'approval_date']
    ordering = ['-application_date']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return AccountApplicationCreateSerializer
        elif self.action == 'list':
            return AccountApplicationListSerializer
        return AccountApplicationDetailSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'search_by_nid']:
            return [AllowAny()]
        return [IsStaffUser()]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by status from query params
        status_param = self.request.query_params.get('status', None)
        if status_param:
            queryset = queryset.filter(status=status_param)
        
        # Search functionality
        search_param = self.request.query_params.get('search', None)
        if search_param:
            queryset = queryset.filter(
                Q(application_number__icontains=search_param) |
                Q(full_name__icontains=search_param) |
                Q(nid_number__icontains=search_param) |
                Q(mobile_number__icontains=search_param) |
                Q(account_number__icontains=search_param)
            )
        
        return queryset
    
    def create(self, request, *args, **kwargs):
        logger.info(f"Application creation attempt. Files: {request.FILES.keys()}")
        logger.info(f"Data: {request.data.keys()}")
        
        serializer = self.get_serializer(data=request.data)
        
        if not serializer.is_valid():
            logger.error(f"Validation errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Save the application
        application = serializer.save()
        
        logger.info(f"Application created: {application.application_number}")
        
        # Return response with application number
        response_data = {
            'application_number': application.application_number,
            'full_name': application.full_name,
            'application_date': application.application_date,
            'status': application.status,
            'message': 'আবেদন সফলভাবে জমা হয়েছে!'
        }
        
        headers = self.get_success_headers(serializer.data)
        return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)
    

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def search_by_nid(self, request):
        """Search applications by NID number"""
        nid_number = request.data.get('nid_number')
        
        if not nid_number:
            return Response(
                {'error': 'এনআইডি নম্বর প্রয়োজন'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        applications = AccountApplication.objects.filter(
            nid_number=nid_number
        ).order_by('-application_date')
        
        serializer = AccountApplicationListSerializer(applications, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsStaffUser])
    def process(self, request, pk=None):
        """Approve or reject application"""
        application = self.get_object()
        
        if application.status != ApplicationStatus.PENDING:
            return Response(
                {'error': 'শুধুমাত্র অপেক্ষমাণ আবেদন প্রক্রিয়া করা যাবে'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = ApplicationApprovalSerializer(data=request.data)
        if serializer.is_valid():
            action_type = serializer.validated_data['action']
            
            if action_type == 'approve':
                application.approve(request.user)
                
                ApplicationLog.objects.create(
                    application=application,
                    action='APPLICATION_APPROVED',
                    performed_by=request.user,
                    details=f'হিসাব নম্বর: {application.account_number}'
                )
                
                message = f'আবেদন অনুমোদিত হয়েছে! হিসাব নম্বর: {application.account_number}'
            else:
                reason = serializer.validated_data['rejection_reason']
                application.reject(request.user, reason)
                
                ApplicationLog.objects.create(
                    application=application,
                    action='APPLICATION_REJECTED',
                    performed_by=request.user,
                    details=f'কারণ: {reason}'
                )
                
                message = 'আবেদন প্রত্যাখ্যান করা হয়েছে।'
            
            return Response({
                'message': message,
                'application': AccountApplicationDetailSerializer(application).data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'], permission_classes=[IsStaffUser])
    def logs(self, request, pk=None):
        """Get application logs"""
        application = self.get_object()
        logs = application.logs.all()
        serializer = ApplicationLogSerializer(logs, many=True)
        return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsStaffUser])
def dashboard_stats(request):
    """Get dashboard statistics"""
    pending_count = AccountApplication.objects.filter(
        status=ApplicationStatus.PENDING
    ).count()
    
    approved_count = AccountApplication.objects.filter(
        status=ApplicationStatus.APPROVED
    ).count()
    
    rejected_count = AccountApplication.objects.filter(
        status=ApplicationStatus.REJECTED
    ).count()
    
    total_count = AccountApplication.objects.count()
    
    recent_applications = AccountApplication.objects.all()[:10]
    
    data = {
        'pending_count': pending_count,
        'approved_count': approved_count,
        'rejected_count': rejected_count,
        'total_count': total_count,
        'recent_applications': recent_applications
    }
    
    serializer = DashboardStatsSerializer(data)
    return Response(serializer.data)