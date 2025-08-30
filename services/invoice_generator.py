"""
Invoice Generator for DataGuardian Pro
EU VAT compliant invoice generation with Netherlands specialization
"""

import os
import logging
from datetime import datetime, date
from typing import Dict, Any, Optional
import io
from decimal import Decimal, ROUND_HALF_UP

# ReportLab imports for PDF generation
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.platypus.frames import Frame
from reportlab.platypus.doctemplate import PageTemplate
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER

logger = logging.getLogger(__name__)

class InvoiceGenerator:
    """Professional EU VAT compliant invoice generator"""
    
    def __init__(self):
        # Company information for invoices
        self.company_info = {
            'name': 'DataGuardian Pro B.V.',
            'address_line1': 'Science Park 123',
            'address_line2': '1098 XG Amsterdam',
            'country': 'Netherlands',
            'vat_number': 'NL123456789B01',
            'kvk_number': '12345678',
            'email': 'billing@dataguardian.pro',
            'phone': '+31 20 123 4567',
            'website': 'https://dataguardian.pro',
            'bank_account': 'NL91 ABNA 0417 1643 00',
            'bank_name': 'ABN AMRO Bank N.V.'
        }
        
        # VAT rates by country
        self.vat_rates = {
            'NL': Decimal('0.21'),  # Netherlands 21%
            'DE': Decimal('0.19'),  # Germany 19%
            'FR': Decimal('0.20'),  # France 20%
            'BE': Decimal('0.21'),  # Belgium 21%
            'AT': Decimal('0.20'),  # Austria 20%
            'IT': Decimal('0.22'),  # Italy 22%
            'ES': Decimal('0.21'),  # Spain 21%
            'PT': Decimal('0.23'),  # Portugal 23%
        }
        
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom styles for invoice"""
        # Company header style
        self.styles.add(ParagraphStyle(
            name='CompanyHeader',
            parent=self.styles['Normal'],
            fontSize=16,
            textColor=colors.HexColor('#2e7d32'),
            spaceAfter=6,
            fontName='Helvetica-Bold'
        ))
        
        # Invoice title style
        self.styles.add(ParagraphStyle(
            name='InvoiceTitle',
            parent=self.styles['Normal'],
            fontSize=24,
            textColor=colors.HexColor('#1976d2'),
            spaceAfter=12,
            fontName='Helvetica-Bold',
            alignment=TA_RIGHT
        ))
        
        # Customer info style
        self.styles.add(ParagraphStyle(
            name='CustomerInfo',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=4
        ))
        
        # Line item style
        self.styles.add(ParagraphStyle(
            name='LineItem',
            parent=self.styles['Normal'],
            fontSize=9,
            spaceAfter=2
        ))
        
        # Footer style
        self.styles.add(ParagraphStyle(
            name='Footer',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#666666'),
            alignment=TA_CENTER
        ))
    
    def generate_payment_invoice(self, payment_data: Dict[str, Any]) -> bytes:
        """
        Generate EU VAT compliant invoice for payment
        
        Args:
            payment_data: Payment information including customer and amount details
            
        Returns:
            PDF invoice as bytes
        """
        try:
            # Create invoice data structure
            invoice_data = self._prepare_invoice_data(payment_data)
            
            # Generate PDF
            return self._create_pdf_invoice(invoice_data)
            
        except Exception as e:
            logger.error(f"Failed to generate invoice: {str(e)}")
            raise
    
    def generate_subscription_invoice(self, subscription_data: Dict[str, Any]) -> bytes:
        """Generate invoice for subscription billing"""
        try:
            # Adapt subscription data for invoice generation
            payment_data = {
                'customer_email': subscription_data['customer_email'],
                'customer_name': subscription_data.get('customer_name', ''),
                'customer_address': subscription_data.get('customer_address', ''),
                'amount': subscription_data['amount'],
                'currency': subscription_data.get('currency', 'EUR'),
                'country_code': subscription_data.get('country_code', 'NL'),
                'description': f"Subscription: {subscription_data['plan_name']}",
                'scan_type': f"Subscription - {subscription_data['plan_name']}",
                'payment_method': subscription_data.get('payment_method', 'subscription'),
                'billing_period': subscription_data.get('billing_period', 'Monthly'),
                'subscription_id': subscription_data.get('subscription_id', '')
            }
            
            return self.generate_payment_invoice(payment_data)
            
        except Exception as e:
            logger.error(f"Failed to generate subscription invoice: {str(e)}")
            raise
    
    def _prepare_invoice_data(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare invoice data with VAT calculations"""
        
        # Generate invoice number
        invoice_number = self._generate_invoice_number()
        
        # Get customer information
        customer_info = self._extract_customer_info(payment_data)
        
        # Calculate amounts
        country_code = payment_data.get('country_code', 'NL')
        vat_rate = self.vat_rates.get(country_code, self.vat_rates['NL'])
        
        # Convert amount to Decimal for precise calculations
        total_amount = Decimal(str(payment_data['amount']))
        
        # Calculate subtotal and VAT (amount includes VAT)
        subtotal = total_amount / (1 + vat_rate)
        vat_amount = total_amount - subtotal
        
        # Round to 2 decimal places
        subtotal = subtotal.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        vat_amount = vat_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        # Line items
        line_items = [{
            'description': payment_data.get('description', f"DataGuardian Pro - {payment_data.get('scan_type', 'Service')}"),
            'quantity': 1,
            'unit_price': float(subtotal),
            'total': float(subtotal)
        }]
        
        return {
            'invoice_number': invoice_number,
            'issue_date': date.today(),
            'due_date': date.today(),  # Immediate payment
            'customer': customer_info,
            'line_items': line_items,
            'subtotal': float(subtotal),
            'vat_rate': float(vat_rate * 100),  # Convert to percentage
            'vat_amount': float(vat_amount),
            'total_amount': float(total_amount),
            'currency': payment_data.get('currency', 'EUR').upper(),
            'country_code': country_code,
            'payment_method': payment_data.get('payment_method', 'Card'),
            'payment_status': 'Paid',
            'notes': self._get_invoice_notes(country_code),
            'metadata': {
                'session_id': payment_data.get('session_id', ''),
                'scan_type': payment_data.get('scan_type', ''),
                'payment_method': payment_data.get('payment_method', '')
            }
        }
    
    def _extract_customer_info(self, payment_data: Dict[str, Any]) -> Dict[str, str]:
        """Extract and format customer information"""
        return {
            'email': payment_data['customer_email'],
            'name': payment_data.get('customer_name', ''),
            'company': payment_data.get('customer_company', ''),
            'address': payment_data.get('customer_address', ''),
            'city': payment_data.get('customer_city', ''),
            'postal_code': payment_data.get('customer_postal_code', ''),
            'country': payment_data.get('customer_country', payment_data.get('country_code', 'NL')),
            'vat_number': payment_data.get('customer_vat_number', '')
        }
    
    def _generate_invoice_number(self) -> str:
        """Generate unique invoice number"""
        # Format: DGP-YYYY-MMDD-HHMMSS
        now = datetime.now()
        return f"DGP-{now.strftime('%Y-%m%d-%H%M%S')}"
    
    def _create_pdf_invoice(self, invoice_data: Dict[str, Any]) -> bytes:
        """Create PDF invoice using ReportLab"""
        
        # Create PDF in memory
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=20*mm,
            leftMargin=20*mm,
            topMargin=20*mm,
            bottomMargin=20*mm
        )
        
        # Build story
        story = []
        
        # Header
        story.extend(self._create_header(invoice_data))
        story.append(Spacer(1, 10*mm))
        
        # Customer information
        story.extend(self._create_customer_section(invoice_data))
        story.append(Spacer(1, 8*mm))
        
        # Line items table
        story.extend(self._create_line_items_table(invoice_data))
        story.append(Spacer(1, 8*mm))
        
        # Totals table
        story.extend(self._create_totals_table(invoice_data))
        story.append(Spacer(1, 10*mm))
        
        # Payment info and notes
        story.extend(self._create_payment_info(invoice_data))
        story.append(Spacer(1, 8*mm))
        
        # Footer
        story.extend(self._create_footer())
        
        # Build PDF
        doc.build(story)
        
        # Get PDF bytes
        buffer.seek(0)
        return buffer.getvalue()
    
    def _create_header(self, invoice_data: Dict[str, Any]) -> list:
        """Create invoice header"""
        elements = []
        
        # Company info and invoice title in table
        header_data = [
            [
                Paragraph(f"<b>{self.company_info['name']}</b>", self.styles['CompanyHeader']),
                Paragraph(f"<b>INVOICE</b>", self.styles['InvoiceTitle'])
            ],
            [
                Paragraph(f"{self.company_info['address_line1']}<br/>{self.company_info['address_line2']}<br/>{self.company_info['country']}", self.styles['Normal']),
                Paragraph(f"<b>#{invoice_data['invoice_number']}</b>", self.styles['Normal'])
            ],
            [
                Paragraph(f"VAT: {self.company_info['vat_number']}<br/>KvK: {self.company_info['kvk_number']}", self.styles['Normal']),
                Paragraph(f"Date: {invoice_data['issue_date'].strftime('%B %d, %Y')}<br/>Due: {invoice_data['due_date'].strftime('%B %d, %Y')}", self.styles['Normal'])
            ]
        ]
        
        header_table = Table(header_data, colWidths=[100*mm, 70*mm])
        header_table.setStyle(TableStyle([
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTSIZE', (0, 0), (-1, -1), 10)
        ]))
        
        elements.append(header_table)
        return elements
    
    def _create_customer_section(self, invoice_data: Dict[str, Any]) -> list:
        """Create customer information section"""
        elements = []
        customer = invoice_data['customer']
        
        # Bill to section
        elements.append(Paragraph("<b>Bill To:</b>", self.styles['Normal']))
        
        customer_lines = []
        if customer['name']:
            customer_lines.append(customer['name'])
        if customer['company']:
            customer_lines.append(customer['company'])
        
        customer_lines.append(customer['email'])
        
        if customer['address']:
            customer_lines.append(customer['address'])
        if customer['city'] and customer['postal_code']:
            customer_lines.append(f"{customer['postal_code']} {customer['city']}")
        if customer['country']:
            customer_lines.append(customer['country'])
        if customer['vat_number']:
            customer_lines.append(f"VAT: {customer['vat_number']}")
        
        customer_text = "<br/>".join(customer_lines)
        elements.append(Paragraph(customer_text, self.styles['CustomerInfo']))
        
        return elements
    
    def _create_line_items_table(self, invoice_data: Dict[str, Any]) -> list:
        """Create line items table"""
        elements = []
        
        # Table headers
        headers = ['Description', 'Qty', 'Unit Price', 'Total']
        table_data = [headers]
        
        # Line items
        for item in invoice_data['line_items']:
            table_data.append([
                item['description'],
                str(item['quantity']),
                f"{invoice_data['currency']} {item['unit_price']:.2f}",
                f"{invoice_data['currency']} {item['total']:.2f}"
            ])
        
        # Create table
        line_table = Table(table_data, colWidths=[100*mm, 20*mm, 25*mm, 25*mm])
        line_table.setStyle(TableStyle([
            # Header styling
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f5f5f5')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            # Data styling
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fafafa')])
        ]))
        
        elements.append(line_table)
        return elements
    
    def _create_totals_table(self, invoice_data: Dict[str, Any]) -> list:
        """Create totals summary table"""
        elements = []
        
        currency = invoice_data['currency']
        
        totals_data = [
            ['Subtotal:', f"{currency} {invoice_data['subtotal']:.2f}"],
            [f"VAT ({invoice_data['vat_rate']:.1f}%):", f"{currency} {invoice_data['vat_amount']:.2f}"],
            ['<b>Total:</b>', f"<b>{currency} {invoice_data['total_amount']:.2f}</b>"],
            ['Status:', f"<b>{invoice_data['payment_status']}</b>"]
        ]
        
        totals_table = Table(totals_data, colWidths=[50*mm, 30*mm], hAlign='RIGHT')
        totals_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -2), 'Helvetica'),
            ('FONTNAME', (0, -2), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('LINEBELOW', (0, -2), (-1, -2), 1, colors.black),
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.HexColor('#2e7d32'))
        ]))
        
        elements.append(totals_table)
        return elements
    
    def _create_payment_info(self, invoice_data: Dict[str, Any]) -> list:
        """Create payment information section"""
        elements = []
        
        # Payment details
        payment_info = f"""
        <b>Payment Information:</b><br/>
        Payment Method: {invoice_data['payment_method']}<br/>
        Payment Status: {invoice_data['payment_status']}<br/>
        Transaction Date: {invoice_data['issue_date'].strftime('%B %d, %Y')}<br/>
        """
        
        elements.append(Paragraph(payment_info, self.styles['Normal']))
        
        # Notes
        if invoice_data['notes']:
            elements.append(Spacer(1, 4*mm))
            elements.append(Paragraph("<b>Notes:</b>", self.styles['Normal']))
            elements.append(Paragraph(invoice_data['notes'], self.styles['Normal']))
        
        return elements
    
    def _create_footer(self) -> list:
        """Create invoice footer"""
        elements = []
        
        footer_text = f"""
        {self.company_info['name']} | {self.company_info['email']} | {self.company_info['phone']}<br/>
        VAT Number: {self.company_info['vat_number']} | KvK Number: {self.company_info['kvk_number']}<br/>
        Bank: {self.company_info['bank_name']} | IBAN: {self.company_info['bank_account']}<br/>
        <i>This invoice was generated automatically by DataGuardian Pro billing system.</i>
        """
        
        elements.append(Paragraph(footer_text, self.styles['Footer']))
        return elements
    
    def _get_invoice_notes(self, country_code: str) -> str:
        """Get country-specific invoice notes"""
        notes = {
            'NL': "This invoice complies with Netherlands tax regulations (Wet op de omzetbelasting 1968). EU VAT rules apply for B2B transactions.",
            'DE': "Diese Rechnung entspricht den deutschen Steuervorschriften. EU-Mehrwertsteuerregeln gelten für B2B-Transaktionen.",
            'FR': "Cette facture est conforme à la réglementation fiscale française. Les règles de TVA de l'UE s'appliquent aux transactions B2B.",
            'BE': "Deze factuur voldoet aan de Belgische belastingvoorschriften. EU BTW-regels zijn van toepassing op B2B-transacties."
        }
        
        return notes.get(country_code, "This invoice complies with EU tax regulations. VAT rules apply for B2B transactions.")
    
    def validate_invoice_data(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate invoice data for EU compliance"""
        errors = []
        warnings = []
        
        # Required fields check
        required_fields = ['customer_email', 'amount', 'scan_type']
        for field in required_fields:
            if not invoice_data.get(field):
                errors.append(f"Missing required field: {field}")
        
        # VAT validation for EU countries
        country_code = invoice_data.get('country_code', 'NL')
        if country_code in self.vat_rates:
            customer_vat = invoice_data.get('customer_vat_number', '')
            if not customer_vat:
                warnings.append(f"No VAT number provided for EU customer in {country_code}")
        
        # Amount validation
        try:
            amount = float(invoice_data.get('amount', 0))
            if amount <= 0:
                errors.append("Invoice amount must be greater than 0")
        except (ValueError, TypeError):
            errors.append("Invalid invoice amount format")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }

# Global invoice generator instance
invoice_generator = InvoiceGenerator()