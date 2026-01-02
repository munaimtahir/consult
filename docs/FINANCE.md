# Finance Module - Implementation Plan

## Overview
Complete Finance module for SIMS (Student Information Management System) with backend, frontend, PDF generation, finance gating, and demo data.

## Entities

### 1. FeeType (Reference Table)
- **code**: Unique identifier (TUITION, EXAM, ADMISSION, LIBRARY, HOSTEL, FINE, MISC)
- **name**: Human-readable name
- **is_active**: Boolean flag

### 2. FeePlan
- **program**: FK to Program (academics app)
- **term**: FK to Term (academics app)
- **fee_type**: FK to FeeType
- **amount**: Decimal
- **is_mandatory**: Boolean
- **frequency**: Choice (one_time, per_term)
- **effective_from**: Date (optional)
- **is_active**: Boolean
- **Constraint**: Unique(program, term, fee_type) when active

### 3. Voucher
- **voucher_no**: Unique, readable identifier
- **student**: FK to Student
- **term**: FK to Term
- **status**: Choice (generated, partially_paid, paid, overdue, cancelled)
- **issue_date**: Date
- **due_date**: Date
- **total_amount**: Decimal (snapshot for printing, also derivable from items)
- **notes**: Text
- **created_by**: FK to User

### 4. VoucherItem
- **voucher**: FK to Voucher
- **fee_type**: FK to FeeType
- **description**: Text
- **amount**: Decimal
- **metadata**: JSON (optional)
- **Rule**: Sum(VoucherItem.amount) = voucher.total_amount

### 5. LedgerEntry (Source of Truth)
- **student**: FK to Student
- **term**: FK to Term
- **entry_type**: Choice (debit, credit)
- **amount**: Decimal (always positive)
- **currency**: Default PKR
- **reference_type**: Choice (voucher, payment, adjustment, waiver, scholarship, reversal)
- **reference_id**: UUID/Integer
- **description**: Text
- **created_by**: FK to User
- **created_at**: DateTime
- **voided_at**: Nullable DateTime
- **void_reason**: Nullable Text
- **Important**: Balance is derived, never stored: balance = sum(debits) - sum(credits)

### 6. Payment
- **receipt_no**: Unique identifier
- **student**: FK to Student
- **term**: FK to Term
- **voucher**: Nullable FK to Voucher
- **amount**: Decimal
- **method**: Choice (cash, bank_transfer, online, scholarship, waiver)
- **reference_no**: Bank reference
- **received_by**: FK to User
- **received_at**: DateTime
- **status**: Choice (received, verified, rejected)
- **Rule**: When verified, creates LedgerEntry CREDIT

### 7. Adjustment
- **student**: FK to Student
- **term**: FK to Term
- **kind**: Choice (waiver, scholarship, adjustment, fine_reversal)
- **amount**: Decimal
- **reason**: Text
- **requested_by**: FK to User
- **approved_by**: Nullable FK to User
- **approved_at**: Nullable DateTime
- **status**: Choice (pending, approved, rejected)
- **Rule**: Only when approved, creates LedgerEntry CREDIT

## Workflows

### Voucher Generation
1. Select program + term
2. Option: Generate for all students OR selected students
3. For each student:
   - Get active FeePlans for program+term
   - Create Voucher with VoucherItems
   - Create LedgerEntry DEBIT for each item
   - Set status based on due_date

### Payment Processing
1. Record payment (student, term, amount, method, voucher optional)
2. Create Payment record (status: received)
3. Verify payment (finance/admin role)
4. On verification:
   - Create LedgerEntry CREDIT
   - Reconcile voucher status (paid/partial/overdue)

### Balance Computation
- Query LedgerEntry for student+term
- Calculate: sum(debits) - sum(credits)
- Return outstanding amount

### Finance Gating
- Check outstanding balance for student+term
- Apply rules:
  - Outstanding > 0 => block transcript generation
  - Exam fee outstanding => block results view
  - Tuition outstanding => block exam eligibility (optional)
- Return flags: can_sit_exam, can_view_results, can_generate_transcript, can_enroll_next_term

## API Endpoints

### Fee Types
- `GET /api/finance/fee-types/` - List (admin/finance)
- `POST /api/finance/fee-types/` - Create (admin)
- `GET /api/finance/fee-types/{id}/` - Retrieve
- `PUT/PATCH /api/finance/fee-types/{id}/` - Update (admin)
- `DELETE /api/finance/fee-types/{id}/` - Delete (admin)

### Fee Plans
- `GET /api/finance/fee-plans/` - List (filters: program, term)
- `POST /api/finance/fee-plans/` - Create (finance/admin)
- `GET /api/finance/fee-plans/{id}/` - Retrieve
- `PUT/PATCH /api/finance/fee-plans/{id}/` - Update (finance/admin)
- `DELETE /api/finance/fee-plans/{id}/` - Delete (finance/admin)

### Vouchers
- `GET /api/finance/vouchers/` - List (filters: status, term, program, student)
- `POST /api/finance/vouchers/generate/` - Bulk generate
- `GET /api/finance/vouchers/{id}/` - Retrieve
- `GET /api/finance/vouchers/{id}/pdf/` - Download PDF
- `POST /api/finance/vouchers/{id}/cancel/` - Cancel (creates reversal)

### Payments
- `GET /api/finance/payments/` - List (filters: student, term, status, method)
- `POST /api/finance/payments/` - Create (finance/admin)
- `GET /api/finance/payments/{id}/` - Retrieve
- `POST /api/finance/payments/{id}/verify/` - Verify (finance/admin)
- `GET /api/finance/payments/{id}/pdf/` - Download receipt PDF

### Ledger
- `GET /api/finance/ledger/` - Read-only list (filters: student, term, entry_type, reference_type)

### Student Summary
- `GET /api/finance/students/{id}/summary/` - Balance, dues, voucher status, gating flags

### Reports
- `GET /api/finance/reports/defaulters/` - List defaulters (filters: program, term)
- `GET /api/finance/reports/collection/` - Collection summary (date range)

## Permissions (RBAC)

- **Finance Role**: Full access except system settings
- **Admin**: Full access
- **Registrar**: Read-only for student summaries
- **Student**: Can view own vouchers, payments, ledger summary, download own PDFs

## Demo Scenario

### Setup
1. Create 2 programs (or use existing)
2. Create 2 terms (Term 1, Term 2)
3. Create 20+ students (or use existing)
4. Create fee plans:
   - Term 1: Tuition 50,000; Exam 5,000; Library 2,000
   - Term 2: Tuition 50,000; Exam 5,000; Library 2,000

### Voucher Generation
- Generate vouchers for 20 students in Term 1
- Status distribution:
  - 10 students: Fully paid
  - 5 students: Partially paid
  - 5 students: Unpaid (defaulters)

### Payments
- Create payments with different methods (cash, bank_transfer, online)
- Verify payments to create ledger credits
- Ensure voucher statuses update correctly

### Gating Demonstration
- For 1 unpaid student:
  - Transcript endpoint denies with clear message
  - Student UI shows gating warning
  - After payment, gating is removed

### Demo Credentials
- admin/admin123
- finance/finance123
- registrar/registrar123
- student/student123

## Implementation Notes

1. **No Deletion**: Use reversals (credit notes/void entries) instead of deleting finance records
2. **Balance Derivation**: Never store balance; always compute from ledger entries
3. **Error Format**: Follow existing repo error response patterns
4. **Audit Logging**: Integrate with existing audit service
5. **PDF Generation**: Use ReportLab (check if already in requirements)
6. **Migrations**: Keep linear and correct, no circular dependencies
