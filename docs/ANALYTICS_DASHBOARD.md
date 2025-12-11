# Hospital Consult System - Analytics Dashboard

## Overview
The Analytics Dashboard provides real-time insights into consult performance for Department Heads and Administrators. It enables data-driven decision-making and helps identify bottlenecks in the consult workflow.

## Dashboard Access
- **Head of Department (HOD)**: Views metrics for their own department only.
- **Administrator**: Views system-wide metrics across all departments.

## Key Metrics

### 1. Consult Volume
- **Total Consults**: Count of all consults (Generated vs Received).
- **By Urgency**: Breakdown by Emergency, Urgent, and Routine.
- **Trend Over Time**: Line chart showing daily/weekly/monthly volume.

### 2. Response Time Analytics
- **Average Response Time**: Mean time from creation to first response.
- **SLA Compliance Rate**: Percentage of consults completed within the target time.
- **Overdue Consults**: List of active consults that have breached SLA.

### 3. Status Distribution
- **Pie Chart**: Current consults by status (Pending, Assigned, In Progress, Completed, Escalated).
- **Completion Rate**: Percentage of consults marked as completed.

### 4. Department Performance (Admin View)
- **Comparison Table**: All departments ranked by:
    - Average response time.
    - SLA compliance rate.
    - Total consults handled.

### 5. Follow-up Pool
- **Active Follow-ups**: Count of consults in regular and conditional follow-up.
- **Follow-up Completion**: Percentage of follow-ups that were successfully closed.

## Real-time Updates
- Dashboard metrics update automatically as consult statuses change.
- Visual indicators (e.g., red alerts for overdue consults).

## Export & Reporting
- **Export to CSV**: Download raw data for external analysis.
- **PDF Reports**: Generate monthly performance reports for management review.
