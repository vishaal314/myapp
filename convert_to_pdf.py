#!/usr/bin/env python3
"""
Convert patent documents from Markdown to PDF format
"""

import os
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import black, blue
import re

def markdown_to_pdf(markdown_content, output_filename, title):
    """Convert markdown content to PDF"""
    
    # Create PDF document
    doc = SimpleDocTemplate(
        output_filename,
        pagesize=A4,
        topMargin=1*inch,
        bottomMargin=1*inch,
        leftMargin=1*inch,
        rightMargin=1*inch
    )
    
    # Get styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=18,
        spaceAfter=30,
        textColor=black,
        alignment=1  # Center alignment
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading1'],
        fontSize=14,
        spaceAfter=12,
        spaceBefore=20,
        textColor=black
    )
    
    subheading_style = ParagraphStyle(
        'CustomSubHeading',
        parent=styles['Heading2'],
        fontSize=12,
        spaceAfter=10,
        spaceBefore=15,
        textColor=black
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=6,
        leading=12
    )
    
    code_style = ParagraphStyle(
        'CustomCode',
        parent=styles['Code'],
        fontSize=9,
        spaceAfter=6,
        leading=11,
        fontName='Courier'
    )
    
    # Story (content) list
    story = []
    
    # Add title
    story.append(Paragraph(title, title_style))
    story.append(Spacer(1, 20))
    
    # Process markdown content
    lines = markdown_content.split('\n')
    
    for line in lines:
        line = line.strip()
        
        if not line:
            story.append(Spacer(1, 6))
            continue
            
        # Process headers
        if line.startswith('### '):
            text = line[4:].strip()
            story.append(Paragraph(text, subheading_style))
        elif line.startswith('## '):
            text = line[3:].strip()
            story.append(Paragraph(text, heading_style))
        elif line.startswith('# '):
            text = line[2:].strip()
            story.append(Paragraph(text, heading_style))
            
        # Process code blocks
        elif line.startswith('```'):
            continue  # Skip code block markers
        elif line.startswith('    ') or line.startswith('\t'):
            # Indented code
            text = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            story.append(Paragraph(text, code_style))
            
        # Process lists
        elif line.startswith('- ') or line.startswith('* '):
            text = '• ' + line[2:].strip()
            story.append(Paragraph(text, normal_style))
        elif re.match(r'^\d+\. ', line):
            text = line
            story.append(Paragraph(text, normal_style))
            
        # Process bold/italic text and normal paragraphs
        else:
            if line:
                # Clean up markdown formatting
                text = line
                text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)  # Bold
                text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)      # Italic
                text = re.sub(r'`(.*?)`', r'<font name="Courier">\1</font>', text)  # Code
                
                # Handle special characters
                text = text.replace('€', 'EUR ')
                text = text.replace('≈', '~')
                text = text.replace('→', '->')
                
                story.append(Paragraph(text, normal_style))
    
    # Build PDF
    doc.build(story)
    print(f"PDF created: {output_filename}")

def convert_all_patents():
    """Convert all patent documents to PDF"""
    
    documents = [
        {
            'file': 'PATENT_DESCRIPTION.md',
            'output': 'Patent_Description.pdf',
            'title': 'AI Model Scanner - Patent Description'
        },
        {
            'file': 'PATENT_CONCLUSIONS.md',
            'output': 'Patent_Conclusions.pdf',
            'title': 'AI Model Scanner - Patent Conclusions (Conclusies)'
        },
        {
            'file': 'PATENT_DRAWINGS.md',
            'output': 'Patent_Drawings.pdf',
            'title': 'AI Model Scanner - Patent Drawings & Formulas'
        },
        {
            'file': 'PATENT_EXTRACT.md',
            'output': 'Patent_Extract.pdf',
            'title': 'AI Model Scanner - Patent Extract Summary'
        }
    ]
    
    for doc in documents:
        try:
            # Read markdown content
            with open(doc['file'], 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Convert to PDF
            markdown_to_pdf(content, doc['output'], doc['title'])
            
        except FileNotFoundError:
            print(f"Warning: {doc['file']} not found, skipping...")
        except Exception as e:
            print(f"Error converting {doc['file']}: {str(e)}")
    
    print("\nPDF conversion completed!")
    print("Created files:")
    for doc in documents:
        if os.path.exists(doc['output']):
            print(f"  - {doc['output']}")

if __name__ == "__main__":
    convert_all_patents()