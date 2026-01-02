# Finance Module - Demo Script

## Prerequisites

1. Backend running on `http://localhost:8000`
2. Frontend running on `http://localhost:3000`
3. Database migrations applied
4. Demo data seeded

## Setup Commands

```bash
# Backend setup
cd backend
python manage.py makemigrations academics students finance
python manage.py migrate
python manage.py seed_finance --students 20

# Frontend setup (if needed)
cd ../frontend
npm install
npm run dev
```

## Demo Credentials

| Role | Email | Password |
|------|-------|----------|
| Finance/Admin | finance@pmc.edu.pk | finance123 |
| Admin | admin@pmc.edu.pk | adminpassword123 |
| Student | student1@test.com | (created by seed) |

## Demo Walkthrough

### Part 1: Finance Dashboard (5 minutes)

1. **Login as Finance User**
   - Navigate to `http://localhost:3000/login`
   - Login: `finance@pmc.edu.pk` / `finance123`
   - Click "Finance" in top navigation

2. **View Dashboard**
   - See KPIs: Total Outstanding, Total Collected, Defaulters Count
   - Review recent defaulters table
   - Note the quick action buttons

### Part 2: Vouchers Management (5 minutes)

1. **View Vouchers**
   - Click "Vouchers" or navigate to `/finance/vouchers`
   - See list of all vouchers
   - Use filters: Status (paid, overdue, etc.), Term

2. **Download Voucher PDF**
   - Click "PDF" button on any voucher
   - PDF downloads with student details, line items, payment summary

3. **View Voucher Details**
   - Click "View" on a voucher
   - See full voucher information

### Part 3: Payments Management (5 minutes)

1. **View Payments**
   - Navigate to `/finance/payments`
   - See list of all payments
   - Filter by status (verified, received) and method (cash, bank_transfer)

2. **Download Receipt PDF**
   - Click "Receipt" button on any payment
   - PDF downloads with payment details

### Part 4: Student Finance View (5 minutes)

1. **View Student Summary**
   - Navigate to `/finance/students/1/summary` (replace 1 with actual student ID from seed)
   - See balance breakdown:
     - Total Debits
     - Total Credits
     - Outstanding Amount
   - View voucher statistics (paid, pending, overdue)
   - See recent vouchers and payments

2. **Finance Gating Demonstration**
   - For a student with outstanding dues, you'll see:
     - Red warning box with blocking reasons
     - Example: "⚠️ Finance Restrictions - Outstanding dues: 50000.00 PKR"
   - This indicates the student cannot:
     - Generate transcript (if policy active)
     - View results (if exam fee due)

### Part 5: Backend API Testing (Optional - 10 minutes)

1. **Generate Vouchers via API**
```bash
curl -X POST http://localhost:8000/api/v1/finance/vouchers/generate/ \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "program_id": 1,
    "term_id": 1,
    "due_date": "2024-12-31"
  }'
```

2. **Record Payment via API**
```bash
curl -X POST http://localhost:8000/api/v1/finance/payments/ \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "student": 1,
    "term": 1,
    "amount": "50000.00",
    "method": "cash",
    "voucher": 1
  }'
```

3. **Get Defaulters Report**
```bash
curl http://localhost:8000/api/v1/finance/reports/defaulters/?term_id=1 \
  -H "Authorization: Bearer <your_token>"
```

4. **Get Student Finance Summary**
```bash
curl http://localhost:8000/api/v1/finance/students/1/summary/ \
  -H "Authorization: Bearer <your_token>"
```

## Expected Outcomes

### After Seeding
- 2 Programs (MBBS, BDS)
- 2 Terms (T1-2024, T2-2024)
- 20 Students
- Fee Plans for each program+term combination
- Vouchers generated for students
- Payments created (10 fully paid, 5 partially paid, 5 unpaid/defaulters)

### Finance Dashboard Should Show
- Total Outstanding: Sum of all unpaid vouchers
- Total Collected: Sum of all verified payments
- Defaulters: Count of students with outstanding dues
- Recent defaulters table with details

### Student Summary Should Show
- Balance breakdown (debits, credits, outstanding)
- Voucher statistics
- Recent transactions
- Finance gating warnings (if applicable)

## Troubleshooting

### Issue: No data showing
- **Solution**: Run `python manage.py seed_finance --students 20`

### Issue: 404 on finance routes
- **Solution**: Ensure frontend routes are added in `App.jsx`

### Issue: PDF download fails
- **Solution**: Check backend logs, ensure ReportLab is installed

### Issue: Permission denied
- **Solution**: Login as finance@pmc.edu.pk or admin@pmc.edu.pk

## Next Steps

1. **Integrate with Transcript App**: Add finance gating check in transcript generation endpoint
2. **Integrate with Results App**: Add finance gating check in results view endpoint
3. **Add Voucher Generation UI**: Create form for bulk voucher generation
4. **Add Payment Recording UI**: Create form for recording payments
5. **Add Fee Plan Management UI**: Create CRUD interface for fee plans
