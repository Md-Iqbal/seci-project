from rest_framework import viewsets, status, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.exceptions import ValidationError
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from .models import AccountApplication, ApplicationLog, ApplicationStatus
from bonds.models import WageEarnersBond,USDBond, ApplicationStatus as BondStatus
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
    search_fields = ['application_number', 'full_name_bng', 'nid_number', 'pre_phone', 'full_name_eng', 'per_phone']
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
        print("QUERY PARAMS:", self.request.query_params)
        print("TYPE:", self.request.query_params.get("type"))
        queryset = super().get_queryset()
        print(self.request)
        # Filter by status from query params
        app_type = self.request.query_params.get("type")
        print(app_type)
        if app_type:
            if app_type == "Wage":
                return WageEarnersBond.objects.all()

            elif app_type == "USD":
                return USDBond.objects.all()

            return AccountApplication.objects.all()
        
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
        print("Api request received for creating application")
        try:
            print("=" * 80)
            print("REQUEST DATA:", request.data)
            

            serializer = self.get_serializer(data=request.data)

            print("Serializer created")

            serializer.is_valid(raise_exception=True)

            print("Serializer valid")

            application = serializer.save()

            print("Application saved:", application.application_number)

            return Response({
                "application_number": application.application_number,
                "message": "Success"
            }, status=201)
        
        except ValidationError as e:
            return Response(e.detail, status=400)
        except Exception:
            logger.exception("Application creation failed")
            return Response(
                {"error": "Internal Server Error"},
                status=500
            )
    

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
    pending_Acc = AccountApplication.objects.filter(
        status=ApplicationStatus.PENDING
    ).count()
    pending_WEB = WageEarnersBond.objects.filter(
        status=BondStatus.PENDING
    ).count()
    pending_USDB = USDBond.objects.filter(
        status=BondStatus.PENDING
    ).count()
    pending_count=pending_Acc+pending_WEB+pending_USDB

    approved_Acc = AccountApplication.objects.filter(
        status=ApplicationStatus.APPROVED
    ).count()
    approved_WEB = WageEarnersBond.objects.filter(
        status=BondStatus.APPROVED
    ).count()
    approved_USDB = USDBond.objects.filter(
        status=BondStatus.APPROVED
    ).count()
    approved_count=approved_Acc+approved_WEB+approved_USDB

    rejected_Acc = AccountApplication.objects.filter(
        status=ApplicationStatus.REJECTED
    ).count()
    rejected_WEB = WageEarnersBond.objects.filter(
        status=BondStatus.REJECTED
    ).count()
    rejected_USDB = USDBond.objects.filter(
        status=BondStatus.REJECTED
    ).count()
    rejected_count=rejected_Acc+rejected_WEB+rejected_USDB

    
    total_app = AccountApplication.objects.count()
    total_WEB = WageEarnersBond.objects.count()
    total_USDB = USDBond.objects.count()
    total_count = total_app + total_WEB + total_USDB
    
    recent_applications = AccountApplication.objects.all()[:7]
    recent_web = WageEarnersBond.objects.all()[:7]
    recent_usdb = USDBond.objects.all()[:7]
    
    data = {
        'pending_Acc': pending_Acc,
        'pending_WEB': pending_WEB,
        'pending_USDB': pending_USDB,
        'approved_Acc': approved_Acc,
        'approved_WEB': approved_WEB,
        'approved_USDB': approved_USDB,
        'rejected_Acc': rejected_Acc,
        'rejected_WEB': rejected_WEB,
        'rejected_USDB': rejected_USDB,
        'pending_count': pending_count,
        'approved_count': approved_count,
        'rejected_count': rejected_count,
        'total_count': total_count,
        'recent_applications': recent_applications,
        'recent_WEBapplications': recent_web,
        'recent_USDBapplications': recent_usdb
    }
    print("data")
    print(data)
    serializer = DashboardStatsSerializer(data)
    print("serializer data")
    print(serializer.data)
    return Response(serializer.data)