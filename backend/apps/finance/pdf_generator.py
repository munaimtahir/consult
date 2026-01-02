"""
PDF generation for vouchers and receipts using ReportLab.
"""

from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from django.utils import timezone


def generate_voucher_pdf(voucher):
    """Generate PDF for a voucher."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=0.5*inch, leftMargin=0.5*inch)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    # Title
    elements.append(Paragraph("FEE VOUCHER", title_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Voucher details
    voucher_data = [
        ['Voucher No:', voucher.voucher_no],
        ['Issue Date:', voucher.issue_date.strftime('%d-%m-%Y')],
        ['Due Date:', voucher.due_date.strftime('%d-%m-%Y')],
        ['Status:', voucher.get_status_display()],
    ]
    
    voucher_table = Table(voucher_data, colWidths=[2*inch, 4*inch])
    voucher_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(voucher_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Student details
    student_data = [
        ['Student ID:', voucher.student.student_id],
        ['Student Name:', voucher.student.full_name],
        ['Program:', voucher.student.program.code if voucher.student.program else 'N/A'],
        ['Term:', voucher.term.code],
    ]
    
    student_table = Table(student_data, colWidths=[2*inch, 4*inch])
    student_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8e8e8')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(student_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Fee items
    items_data = [['S.No', 'Fee Type', 'Description', 'Amount (PKR)']]
    
    for idx, item in enumerate(voucher.items.all(), 1):
        items_data.append([
            str(idx),
            item.fee_type.code,
            item.description[:50],  # Truncate long descriptions
            f"{item.amount:,.2f}"
        ])
    
    # Add total row
    items_data.append([
        '',
        '',
        '<b>TOTAL</b>',
        f"<b>{voucher.total_amount:,.2f}</b>"
    ])
    
    items_table = Table(items_data, colWidths=[0.5*inch, 1.5*inch, 3*inch, 1.5*inch])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -2), colors.white),
        ('TEXTCOLOR', (0, 1), (-1, -2), colors.black),
        ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -2), 10),
        ('ALIGN', (3, 1), (3, -2), 'RIGHT'),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#ecf0f1')),
        ('TEXTCOLOR', (0, -1), (-1, -1), colors.black),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, -1), (-1, -1), 11),
        ('BOTTOMPADDING', (0, -1), (-1, -1), 12),
        ('TOPPADDING', (0, -1), (-1, -1), 12),
        ('ALIGN', (3, -1), (3, -1), 'RIGHT'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(items_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Payment summary
    paid_amount = voucher.get_paid_amount()
    outstanding = voucher.get_outstanding_amount()
    
    payment_data = [
        ['Total Amount:', f"{voucher.total_amount:,.2f} PKR"],
        ['Paid Amount:', f"{paid_amount:,.2f} PKR"],
        ['Outstanding:', f"<b>{outstanding:,.2f} PKR</b>"],
    ]
    
    payment_table = Table(payment_data, colWidths=[2*inch, 4*inch])
    payment_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#d5dbdb')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('FONTNAME', (1, -1), (1, -1), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(payment_table)
    
    # Notes
    if voucher.notes:
        elements.append(Spacer(1, 0.2*inch))
        elements.append(Paragraph(f"<b>Notes:</b> {voucher.notes}", styles['Normal']))
    
    # Footer
    elements.append(Spacer(1, 0.3*inch))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.grey,
        alignment=TA_CENTER
    )
    elements.append(Paragraph(
        f"Generated on {timezone.now().strftime('%d-%m-%Y %H:%M:%S')}",
        footer_style
    ))
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer


def generate_receipt_pdf(payment):
    """Generate PDF for a payment receipt."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=0.5*inch, leftMargin=0.5*inch)
    
    elements = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    # Title
    elements.append(Paragraph("PAYMENT RECEIPT", title_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Receipt details
    receipt_data = [
        ['Receipt No:', payment.receipt_no],
        ['Date:', payment.received_at.strftime('%d-%m-%Y %H:%M:%S')],
        ['Status:', payment.get_status_display()],
    ]
    
    receipt_table = Table(receipt_data, colWidths=[2*inch, 4*inch])
    receipt_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(receipt_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Student details
    student_data = [
        ['Student ID:', payment.student.student_id],
        ['Student Name:', payment.student.full_name],
        ['Program:', payment.student.program.code if payment.student.program else 'N/A'],
        ['Term:', payment.term.code],
    ]
    
    student_table = Table(student_data, colWidths=[2*inch, 4*inch])
    student_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8e8e8')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(student_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Payment details
    payment_details = [
        ['Amount Received:', f"<b>{payment.amount:,.2f} PKR</b>"],
        ['Payment Method:', payment.get_method_display()],
    ]
    
    if payment.voucher:
        payment_details.append(['Voucher No:', payment.voucher.voucher_no])
    
    if payment.reference_no:
        payment_details.append(['Reference No:', payment.reference_no])
    
    if payment.verified_by:
        payment_details.append(['Verified By:', payment.verified_by.get_full_name()])
        payment_details.append(['Verified At:', payment.verified_at.strftime('%d-%m-%Y %H:%M:%S') if payment.verified_at else 'N/A'])
    
    payment_table = Table(payment_details, colWidths=[2*inch, 4*inch])
    payment_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), colors.HexColor('#2c3e50')),
        ('TEXTCOLOR', (0, 0), (0, 0), colors.whitesmoke),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('FONTNAME', (1, 0), (1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(payment_table)
    
    # Notes
    if payment.notes:
        elements.append(Spacer(1, 0.2*inch))
        elements.append(Paragraph(f"<b>Notes:</b> {payment.notes}", styles['Normal']))
    
    # Footer
    elements.append(Spacer(1, 0.3*inch))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.grey,
        alignment=TA_CENTER
    )
    elements.append(Paragraph(
        f"Generated on {timezone.now().strftime('%d-%m-%Y %H:%M:%S')}",
        footer_style
    ))
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer
