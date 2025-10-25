#!/usr/bin/env python3
"""
PDF Generator for Corrected Patent Conclusions (English Version)
Converts patent_documents/CORRECTED_Patent_Conclusions_ENGLISH.txt to PDF
"""

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm

def create_patent_conclusions_english_pdf():
    """Generate PDF from corrected English patent conclusions text file"""
    
    # Read the corrected text file
    input_file = 'patent_documents/CORRECTED_Patent_Conclusions_ENGLISH.txt'
    output_file = 'patent_documents/04_Patent_Conclusions_Claims_CORRECTED_ENGLISH.pdf'
    
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Create PDF
    c = canvas.Canvas(output_file, pagesize=A4)
    width, height = A4
    
    # Set margins (25mm on all sides)
    margin_left = 25 * mm
    margin_right = 25 * mm
    margin_top = 20 * mm
    margin_bottom = 20 * mm
    
    # Current position
    y_position = height - margin_top
    
    # Font settings
    font_size = 10
    line_height = 12
    
    # Process content line by line
    lines = content.split('\n')
    
    for line in lines:
        # Check if we need a new page
        if y_position < margin_bottom + line_height:
            c.showPage()
            y_position = height - margin_top
        
        # Handle separator lines
        if '=' * 50 in line:
            # Draw horizontal separator
            c.setLineWidth(0.5)
            c.line(margin_left, y_position - 3, width - margin_right, y_position - 3)
            y_position -= line_height
            continue
        
        # Set font based on content
        if any(keyword in line for keyword in ['CONCLUSIONS', 'CLAIMS', 'PAGE', 'END OF']):
            c.setFont("Courier-Bold", font_size)
        elif line.strip().startswith('Claim'):
            c.setFont("Courier-Bold", font_size)
        else:
            c.setFont("Courier", font_size)
        
        # Draw text line
        c.drawString(margin_left, y_position, line.rstrip())
        y_position -= line_height
    
    # Save PDF
    c.save()
    print(f"✅ English PDF generated successfully!")
    print(f"📄 Input:  {input_file}")
    print(f"📄 Output: {output_file}")
    return output_file

if __name__ == '__main__':
    try:
        pdf_file = create_patent_conclusions_english_pdf()
        print(f"\n🎉 Ready for RVO.nl submission!")
        print(f"📅 Deadline: December 29, 2025")
        print(f"📋 Application: 1045290")
        print(f"💰 Patent Value: €1.9M (NL2025003)")
    except Exception as e:
        print(f"❌ Error generating PDF: {e}")
        import traceback
        traceback.print_exc()
