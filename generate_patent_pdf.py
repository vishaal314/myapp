#!/usr/bin/env python3
"""
Generate PDF patent application from HTML
"""

import os
from pathlib import Path

def generate_pdf_from_html():
    """Generate PDF using available libraries"""
    
    html_file = "patent_application_predictive_compliance.html"
    pdf_file = "DataGuardian_Pro_Patent_Application_2_Predictive_Compliance_Engine.pdf"
    
    if not os.path.exists(html_file):
        print(f"Error: {html_file} not found")
        return False
    
    # Try weasyprint first
    try:
        from weasyprint import HTML, CSS
        print("Using WeasyPrint to generate PDF...")
        
        # Custom CSS for better PDF formatting
        css = CSS(string='''
            @page {
                size: A4;
                margin: 2cm;
                @top-center {
                    content: "DataGuardian Pro - Patent Application";
                    font-size: 10pt;
                    color: #666;
                }
                @bottom-center {
                    content: "Page " counter(page);
                    font-size: 10pt;
                    color: #666;
                }
            }
            body {
                font-size: 11pt;
                line-height: 1.4;
            }
            .header h1 {
                font-size: 18pt;
                text-align: center;
            }
            .header h2 {
                font-size: 14pt;
                text-align: center;
            }
            .section h2 {
                font-size: 14pt;
                page-break-before: avoid;
            }
            table {
                font-size: 10pt;
            }
            .code-snippet {
                font-size: 9pt;
            }
            .diagram pre {
                font-size: 8pt;
            }
        ''')
        
        HTML(filename=html_file).write_pdf(pdf_file, stylesheets=[css])
        print(f"✅ PDF successfully generated: {pdf_file}")
        return True
        
    except ImportError:
        print("WeasyPrint not available, trying alternative methods...")
    except Exception as e:
        print(f"WeasyPrint failed: {e}")
    
    # Try using reportlab as fallback
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from bs4 import BeautifulSoup
        
        print("Using ReportLab to generate PDF...")
        
        # Parse HTML content
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Create PDF document
        doc = SimpleDocTemplate(pdf_file, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Add title
        title_text = soup.find('h1').get_text() if soup.find('h1') else "Patent Application"
        story.append(Paragraph(title_text, styles['Title']))
        story.append(Spacer(1, 20))
        
        # Add subtitle  
        subtitle_text = soup.find('h2').get_text() if soup.find('h2') else ""
        story.append(Paragraph(subtitle_text, styles['Heading1']))
        story.append(Spacer(1, 20))
        
        # Add sections
        for section in soup.find_all('div', class_='section'):
            section_title = section.find('h2')
            if section_title:
                story.append(Paragraph(section_title.get_text(), styles['Heading2']))
                story.append(Spacer(1, 12))
            
            # Add paragraphs
            for p in section.find_all('p'):
                story.append(Paragraph(p.get_text(), styles['Normal']))
                story.append(Spacer(1, 6))
        
        doc.build(story)
        print(f"✅ PDF successfully generated: {pdf_file}")
        return True
        
    except ImportError:
        print("ReportLab not available")
    except Exception as e:
        print(f"ReportLab failed: {e}")
    
    return False

if __name__ == "__main__":
    success = generate_pdf_from_html()
    if success:
        print("\n🎉 Patent application PDF generated successfully!")
        print("📄 File: DataGuardian_Pro_Patent_Application_2_Predictive_Compliance_Engine.pdf")
    else:
        print("\n❌ Failed to generate PDF. HTML file is available for manual conversion.")