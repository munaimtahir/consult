"""
Views for Finance app.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.db.models import Q, Count, Sum
from django.http import HttpResponse
from django.utils import timezone
from datetime import timedelta

from .models import (
    FeeType, FeePlan, Voucher, VoucherItem, LedgerEntry,
    Payment, Adjustment, FinancePolicy
)
from .serializers import (
    FeeTypeSerializer, FeePlanSerializer, VoucherSerializer, VoucherItemSerializer,
    VoucherCreateSerializer, LedgerEntrySerializer, PaymentSerializer,
    PaymentCreateSerializer, AdjustmentSerializer, FinancePolicySerializer,
    StudentFinanceSummarySerializer
)
from .services import FinanceService
from .permissions import IsFinanceUser, IsFinanceUserOrReadOnly, IsStudentOwner
from .pdf_generator import generate_voucher_pdf, generate_receipt_pdf
from apps.students.models import Student
from apps.academics.models import Program, Term


class FeeTypeViewSet(viewsets.ModelViewSet):
    """ViewSet for FeeType."""
    
    queryset = FeeType.objects.all()
    serializer_class = FeeTypeSerializer
    permission_classes = [IsAuthenticated, IsFinanceUserOrReadOnly]
    filterset_fields = ['is_active']
    search_fields = ['code', 'name']
    ordering = ['code']


class FeePlanViewSet(viewsets.ModelViewSet):
    """ViewSet for FeePlan."""
    
    queryset = FeePlan.objects.select_related('program', 'term', 'fee_type').all()
    serializer_class = FeePlanSerializer
    permission_classes = [IsAuthenticated, IsFinanceUserOrReadOnly]
    filterset_fields = ['program', 'term', 'fee_type', 'is_active', 'is_mandatory']
    search_fields = ['program__code', 'program__name', 'term__code', 'fee_type__code']
    ordering = ['program__code', 'term__code']


class VoucherViewSet(viewsets.ModelViewSet):
    """ViewSet for Voucher."""
    
    queryset = Voucher.objects.select_related(
        'student', 'term', 'created_by'
    ).prefetch_related('items__fee_type').all()
    serializer_class = VoucherSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['status', 'term', 'student']
    search_fields = ['voucher_no', 'student__student_id', 'student__full_name']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter queryset based on user role."""
        queryset = super().get_queryset()
        user = self.request.user
        
        # Students can only see their own vouchers
        if user.role not in ['ADMIN', 'SUPER_ADMIN'] and not user.is_superuser:
            try:
                student = Student.objects.get(email=user.email)
                queryset = queryset.filter(student=student)
            except Student.DoesNotExist:
                # If not a student, return empty queryset
                queryset = queryset.none()
        
        # Filter by program if provided
        program_id = self.request.query_params.get('program')
        if program_id:
            queryset = queryset.filter(student__program_id=program_id)
        
        return queryset
    
    @action(detail=False, methods=['post'], url_path='generate')
    def generate(self, request):
        """Bulk generate vouchers."""
        if not IsFinanceUser().has_permission(request, self):
            return Response(
                {'error': 'You do not have permission to generate vouchers'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = VoucherCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        program_id = data['program_id']
        term_id = data['term_id']
        due_date = data['due_date']
        student_ids = data.get('student_ids', [])
        selected_fee_types = data.get('selected_fee_types', [])
        
        try:
            program = Program.objects.get(id=program_id)
            term = Term.objects.get(id=term_id)
        except (Program.DoesNotExist, Term.DoesNotExist):
            return Response(
                {'error': 'Program or Term not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get students
        if student_ids:
            students = Student.objects.filter(
                id__in=student_ids,
                program=program,
                is_active=True
            )
        else:
            students = Student.objects.filter(
                program=program,
                is_active=True
            )
        
        if not students.exists():
            return Response(
                {'error': 'No students found for the specified criteria'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        results = {
            'created': [],
            'skipped': [],
            'errors': []
        }
        
        for student in students:
            try:
                voucher = FinanceService.create_voucher_from_feeplan(
                    student=student,
                    term=term,
                    created_by=request.user,
                    due_date=due_date,
                    selected_fee_types=selected_fee_types
                )
                results['created'].append({
                    'student_id': student.id,
                    'student_name': student.full_name,
                    'voucher_no': voucher.voucher_no,
                    'amount': str(voucher.total_amount)
                })
            except ValueError as e:
                results['skipped'].append({
                    'student_id': student.id,
                    'student_name': student.full_name,
                    'reason': str(e)
                })
            except Exception as e:
                results['errors'].append({
                    'student_id': student.id,
                    'student_name': student.full_name,
                    'error': str(e)
                })
        
        return Response(results, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['get'], url_path='pdf')
    def pdf(self, request, pk=None):
        """Generate and return voucher PDF."""
        voucher = self.get_object()
        
        # Check permissions
        if not IsFinanceUser().has_permission(request, self):
            # Check if student owns this voucher
            try:
                student = Student.objects.get(email=request.user.email)
                if voucher.student != student:
                    return Response(
                        {'error': 'You do not have permission to view this voucher'},
                        status=status.HTTP_403_FORBIDDEN
                    )
            except Student.DoesNotExist:
                return Response(
                    {'error': 'You do not have permission to view this voucher'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        try:
            pdf_buffer = generate_voucher_pdf(voucher)
            response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="voucher_{voucher.voucher_no}.pdf"'
            return response
        except Exception as e:
            return Response(
                {'error': f'Failed to generate PDF: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel(self, request, pk=None):
        """Cancel a voucher."""
        if not IsFinanceUser().has_permission(request, self):
            return Response(
                {'error': 'You do not have permission to cancel vouchers'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        voucher = self.get_object()
        reason = request.data.get('reason', 'Cancelled by user')
        
        try:
            cancelled_voucher = FinanceService.cancel_voucher(
                voucher.id,
                request.user,
                reason
            )
            serializer = self.get_serializer(cancelled_voucher)
            return Response(serializer.data)
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class PaymentViewSet(viewsets.ModelViewSet):
    """ViewSet for Payment."""
    
    queryset = Payment.objects.select_related(
        'student', 'term', 'voucher', 'received_by', 'verified_by'
    ).all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['status', 'method', 'term', 'student']
    search_fields = ['receipt_no', 'student__student_id', 'student__full_name', 'reference_no']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return PaymentCreateSerializer
        return PaymentSerializer
    
    def get_queryset(self):
        """Filter queryset based on user role."""
        queryset = super().get_queryset()
        user = self.request.user
        
        # Students can only see their own payments
        if user.role not in ['ADMIN', 'SUPER_ADMIN'] and not user.is_superuser:
            try:
                student = Student.objects.get(email=user.email)
                queryset = queryset.filter(student=student)
            except Student.DoesNotExist:
                queryset = queryset.none()
        
        return queryset
    
    def create(self, request, *args, **kwargs):
        """Create a payment."""
        if not IsFinanceUser().has_permission(request, self):
            return Response(
                {'error': 'You do not have permission to create payments'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        try:
            payment = FinanceService.post_payment(
                student=data['student'],
                term=data['term'],
                amount=data['amount'],
                method=data['method'],
                received_by=request.user,
                voucher=data.get('voucher'),
                reference_no=data.get('reference_no')
            )
            return Response(
                PaymentSerializer(payment).data,
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'], url_path='verify')
    def verify(self, request, pk=None):
        """Verify a payment."""
        if not IsFinanceUser().has_permission(request, self):
            return Response(
                {'error': 'You do not have permission to verify payments'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        payment = self.get_object()
        
        try:
            verified_payment = FinanceService.verify_payment(payment.id, request.user)
            serializer = self.get_serializer(verified_payment)
            return Response(serializer.data)
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['get'], url_path='pdf')
    def pdf(self, request, pk=None):
        """Generate and return receipt PDF."""
        payment = self.get_object()
        
        # Check permissions
        if not IsFinanceUser().has_permission(request, self):
            try:
                student = Student.objects.get(email=request.user.email)
                if payment.student != student:
                    return Response(
                        {'error': 'You do not have permission to view this receipt'},
                        status=status.HTTP_403_FORBIDDEN
                    )
            except Student.DoesNotExist:
                return Response(
                    {'error': 'You do not have permission to view this receipt'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        try:
            pdf_buffer = generate_receipt_pdf(payment)
            response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="receipt_{payment.receipt_no}.pdf"'
            return response
        except Exception as e:
            return Response(
                {'error': f'Failed to generate PDF: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class LedgerEntryViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only ViewSet for LedgerEntry."""
    
    queryset = LedgerEntry.objects.select_related(
        'student', 'term', 'created_by'
    ).all()
    serializer_class = LedgerEntrySerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['entry_type', 'reference_type', 'student', 'term']
    search_fields = ['student__student_id', 'student__full_name', 'reference_id', 'description']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter queryset based on user role."""
        queryset = super().get_queryset()
        user = self.request.user
        
        # Students can only see their own ledger entries
        if user.role not in ['ADMIN', 'SUPER_ADMIN'] and not user.is_superuser:
            try:
                student = Student.objects.get(email=user.email)
                queryset = queryset.filter(student=student)
            except Student.DoesNotExist:
                queryset = queryset.none()
        
        return queryset


class AdjustmentViewSet(viewsets.ModelViewSet):
    """ViewSet for Adjustment."""
    
    queryset = Adjustment.objects.select_related(
        'student', 'term', 'requested_by', 'approved_by'
    ).all()
    serializer_class = AdjustmentSerializer
    permission_classes = [IsAuthenticated, IsFinanceUserOrReadOnly]
    filterset_fields = ['status', 'kind', 'term', 'student']
    search_fields = ['student__student_id', 'student__full_name', 'reason']
    ordering = ['-created_at']
    
    @action(detail=True, methods=['post'], url_path='approve')
    def approve(self, request, pk=None):
        """Approve an adjustment."""
        if not IsFinanceUser().has_permission(request, self):
            return Response(
                {'error': 'You do not have permission to approve adjustments'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        adjustment = self.get_object()
        
        try:
            approved_adjustment = FinanceService.approve_adjustment(adjustment.id, request.user)
            serializer = self.get_serializer(approved_adjustment)
            return Response(serializer.data)
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class FinancePolicyViewSet(viewsets.ModelViewSet):
    """ViewSet for FinancePolicy."""
    
    queryset = FinancePolicy.objects.select_related('fee_type_scope').all()
    serializer_class = FinancePolicySerializer
    permission_classes = [IsAuthenticated, IsFinanceUser]
    filterset_fields = ['is_active', 'rule_key']
    ordering = ['rule_key']


class StudentFinanceSummaryView(APIView):
    """View for student finance summary."""
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request, student_id=None):
        """Get finance summary for a student."""
        try:
            student = Student.objects.get(id=student_id)
        except Student.DoesNotExist:
            return Response(
                {'error': 'Student not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check permissions
        user = request.user
        if user.role not in ['ADMIN', 'SUPER_ADMIN'] and not user.is_superuser:
            try:
                student_user = Student.objects.get(email=user.email)
                if student != student_user:
                    return Response(
                        {'error': 'You can only view your own finance summary'},
                        status=status.HTTP_403_FORBIDDEN
                    )
            except Student.DoesNotExist:
                return Response(
                    {'error': 'You do not have permission to view this summary'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        term_id = request.query_params.get('term_id')
        term = None
        if term_id:
            try:
                term = Term.objects.get(id=term_id)
            except Term.DoesNotExist:
                pass
        
        # Compute balance
        balance_info = FinanceService.compute_student_balance(student, term)
        
        # Get voucher counts
        vouchers_qs = Voucher.objects.filter(student=student)
        if term:
            vouchers_qs = vouchers_qs.filter(term=term)
        
        vouchers_count = vouchers_qs.count()
        vouchers_paid = vouchers_qs.filter(status='paid').count()
        vouchers_pending = vouchers_qs.filter(status__in=['generated', 'partially_paid']).count()
        vouchers_overdue = vouchers_qs.filter(status='overdue').count()
        
        # Get gating flags
        gating_flags = FinanceService.finance_gate_checks(student, term)
        
        # Get recent payments and vouchers
        recent_payments = Payment.objects.filter(student=student).order_by('-created_at')[:5]
        recent_vouchers = Voucher.objects.filter(student=student).order_by('-created_at')[:5]
        
        data = {
            'student_id': student.student_id,
            'student_name': student.full_name,
            'term_id': term.id if term else None,
            'term_name': term.name if term else None,
            'total_debits': balance_info['total_debits'],
            'total_credits': balance_info['total_credits'],
            'outstanding': balance_info['outstanding'],
            'vouchers_count': vouchers_count,
            'vouchers_paid': vouchers_paid,
            'vouchers_pending': vouchers_pending,
            'vouchers_overdue': vouchers_overdue,
            'gating_flags': gating_flags,
            'recent_payments': PaymentSerializer(recent_payments, many=True).data,
            'recent_vouchers': VoucherSerializer(recent_vouchers, many=True).data,
        }
        
        serializer = StudentFinanceSummarySerializer(data=data)
        serializer.is_valid()
        return Response(serializer.validated_data)


class FinanceReportsView(APIView):
    """View for finance reports."""
    
    permission_classes = [IsAuthenticated, IsFinanceUser]
    
    def get(self, request, report_type=None):
        """Get list of defaulters."""
        program_id = request.query_params.get('program_id')
        term_id = request.query_params.get('term_id')
        
        # Get students with outstanding vouchers
        vouchers_qs = Voucher.objects.filter(
            status__in=['generated', 'partially_paid', 'overdue']
        ).select_related('student', 'term', 'student__program')
        
        if program_id:
            vouchers_qs = vouchers_qs.filter(student__program_id=program_id)
        if term_id:
            vouchers_qs = vouchers_qs.filter(term_id=term_id)
        
        # Group by student and calculate totals
        defaulters = {}
        for voucher in vouchers_qs:
            student_id = voucher.student.id
            if student_id not in defaulters:
                defaulters[student_id] = {
                    'student_id': voucher.student.student_id,
                    'student_name': voucher.student.full_name,
                    'program': voucher.student.program.code if voucher.student.program else None,
                    'term': voucher.term.code,
                    'total_outstanding': Decimal('0.00'),
                    'vouchers': []
                }
            
            outstanding = voucher.get_outstanding_amount()
            defaulters[student_id]['total_outstanding'] += outstanding
            defaulters[student_id]['vouchers'].append({
                'voucher_no': voucher.voucher_no,
                'amount': str(voucher.total_amount),
                'outstanding': str(outstanding),
                'due_date': voucher.due_date.isoformat(),
                'status': voucher.status
            })
        
        return Response(list(defaulters.values()))


class FinanceCollectionReportView(APIView):
    """View for collection report."""
    
    permission_classes = [IsAuthenticated, IsFinanceUser]
    
    def get(self, request):
        """Get collection summary."""
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        term_id = request.query_params.get('term_id')
        
        payments_qs = Payment.objects.filter(status='verified')
        
        if start_date:
            payments_qs = payments_qs.filter(received_at__date__gte=start_date)
        if end_date:
            payments_qs = payments_qs.filter(received_at__date__lte=end_date)
        if term_id:
            payments_qs = payments_qs.filter(term_id=term_id)
        
        # Aggregate by method
        collection_by_method = payments_qs.values('method').annotate(
            total=Sum('amount'),
            count=Count('id')
        )
        
        total_collection = payments_qs.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        total_count = payments_qs.count()
        
        return Response({
            'total_collection': str(total_collection),
            'total_count': total_count,
            'by_method': list(collection_by_method),
            'date_range': {
                'start_date': start_date,
                'end_date': end_date
            }
        })
