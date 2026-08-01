from rest_framework import viewsets, status, filters
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.exceptions import ValidationError
# from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny

from .models import *
from .serializers import *
from accounts.api_views import IsStaffUser
from accounts.serializers import ApplicationApprovalSerializer

class WageEarnersBondViewSet(viewsets.ModelViewSet):
    permission_classes = [IsStaffUser]
    queryset = WageEarnersBond.objects.all()
    parser_classes = [MultiPartParser, FormParser, JSONParser]  # Important!
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status']
    search_fields = ['application_no', 'applicant_name']
    ordering_fields = ['application_date', 'approval_date']
    ordering = ['-application_date']
    lookup_field = "application_no"
    lookup_url_kwarg = "application_no"

    def get_serializer_class(self):
        # if self.action == 'create':
        return WageEarnersBondListSerializer
    def get_permissions(self):
        if self.action == "create":
            return [AllowAny()]
        return super().get_permissions()
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
                Q(application_no__icontains=search_param) |
                Q(applicant_name__icontains=search_param) |
                Q(applicant_name_bn__icontains=search_param) |
                Q(nid_number__icontains=search_param) |
                Q(mobile_no__icontains=search_param)
            )
        
        return queryset
    

    def create(self, request, *args, **kwargs):
        try:
            serializer=self.get_serializer(data=request.data)
            # data = request.data.copy()

            # serializer = WageEarnersBondListSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            bond = serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "Application submitted successfully.",
                    "application_no": bond.application_no,
                    "id": bond.id
                },
                status=status.HTTP_201_CREATED
            )
        except ValidationError as e:
            return Response(e.detail, status=400)
        except Exception as e:
            import traceback
            traceback.print_exc()

            return Response({
                "error": str(e)
            }, status=500)
        
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def search_by_application_no(self, request):
        """Search applications by NID number"""
        application_no = request.data.get('application_no')
        
        if not application_no:
            return Response(
                {'error': 'Need application number.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        applications = WageEarnersBond.objects.filter(
            application_no=application_no
        ).order_by('-application_date')
        if applications is None:
            applications = USDBond.objects.filter(
                application_no=application_no
            ).order_by('-application_date')
            serializer = USDBondListSerializer(applications, many=True)
            return Response(serializer.data)
        
        serializer = WageEarnersBondListSerializer(applications, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsStaffUser])
    def process(self, request, application_no=None):
        """Approve or reject application"""
        application = self.get_object()
        
        if application.status != ApplicationStatus.PENDING:
            return Response(
                {'error': 'Only pending application can be processed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = ApplicationApprovalSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            action_type = serializer.validated_data['action']
            
            if action_type == 'approve':
                application.approve(request.user)
                
                BondApprovalLog.objects.create(
                    application=application,
                    action='APPLICATION_APPROVED',
                    performed_by=request.user,
                    details=f'Application No: {application.application_no}'
                )
                
                message = f'Application Approved! Application No: {application.application_no}'
            else:
                reason = serializer.validated_data['rejection_reason']
                application.reject(request.user, reason)
                
                BondApprovalLog.objects.create(
                    application=application,
                    action='APPLICATION_REJECTED',
                    performed_by=request.user,
                    details=f'Reason: {reason}'
                )
                
                message = 'Application Rejected'
            
            return Response({
                'message': message,
                'application': WageEarnersBondDetailSerializer(application).data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class USDBondViewSet(viewsets.ModelViewSet):
    permission_classes = [IsStaffUser]
    queryset = USDBond.objects.all()
    parser_classes = [MultiPartParser, FormParser, JSONParser]  # Important!
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status']
    search_fields = ['application_no', 'applicant_name']
    ordering_fields = ['application_date', 'approval_date']
    ordering = ['-application_date']
    lookup_field = "application_no"
    lookup_url_kwarg = "application_no"

    def get_serializer_class(self):
        # if self.action == 'create':
        return USDBondListSerializer
    def get_permissions(self):
        if self.action == "create":
            return [AllowAny()]
        return super().get_permissions()
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
                Q(application_no__icontains=search_param) |
                Q(applicant_name__icontains=search_param)
            )
        
        return queryset
    

    def create(self, request, *args, **kwargs):
        try:
            serializer=self.get_serializer(data=request.data)
            # data = request.data.copy()

            # serializer = WageEarnersBondListSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            bond = serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "Application submitted successfully.",
                    "application_no": bond.application_no,
                    "id": bond.id
                },
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            import traceback
            traceback.print_exc()

            return Response({
                "error": str(e)
            }, status=500)
        
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def search_by_application_no(self, request):
        application_no = request.data.get('application_no')
        
        if not application_no:
            return Response(
                {'error': 'Need application number.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        applications = USDBond.objects.filter(
            application_no=application_no
        ).order_by('-application_date')
        
        serializer = USDBondListSerializer(applications, many=True)
        return Response(serializer.data)
    @action(detail=True, methods=['post'], permission_classes=[IsStaffUser])
    def process(self, request, application_no=None):
        """Approve or reject application"""
        application = self.get_object()
        
        if application.status != ApplicationStatus.PENDING:
            return Response(
                {'error': 'Only pending application can be processed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = ApplicationApprovalSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            action_type = serializer.validated_data['action']
            
            if action_type == 'approve':
                application.approve(request.user)
                
                USDBondApprovalLog.objects.create(
                    application=application,
                    action='APPLICATION_APPROVED',
                    performed_by=request.user,
                    details=f'Application No: {application.application_no}'
                )
                
                message = f'Application Approved! Application No: {application.application_no}'
            else:
                reason = serializer.validated_data['rejection_reason']
                application.reject(request.user, reason)
                
                USDBondApprovalLog.objects.create(
                    application=application,
                    action='APPLICATION_REJECTED',
                    performed_by=request.user,
                    details=f'Reason: {reason}'
                )
                
                message = 'Application Rejected'
            
            return Response({
                'message': message,
                'application': USDBondBondDetailSerializer(application).data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)