#!/usr/bin/env python3
"""
Create professional patent drawings for Netherlands patent filing
"""

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib.colors import black, white, gray, lightgrey
from reportlab.platypus.flowables import Flowable
from reportlab.graphics.shapes import Drawing, Rect, String, Line
from reportlab.graphics import renderPDF

class PatentDiagram(Flowable):
    """Professional patent diagram flowable"""
    
    def __init__(self, width, height, diagram_type):
        self.width = width
        self.height = height
        self.diagram_type = diagram_type
        
    def draw(self):
        canvas = self.canv
        
        if self.diagram_type == "system_overview":
            self._draw_system_overview(canvas)
        elif self.diagram_type == "bias_engine":
            self._draw_bias_engine(canvas)
        elif self.diagram_type == "compliance_matrix":
            self._draw_compliance_matrix(canvas)
        elif self.diagram_type == "math_formulas":
            self._draw_math_formulas(canvas)
    
    def _draw_system_overview(self, canvas):
        """Draw Figure 1: System Architecture Overview"""
        # Title
        canvas.setFont("Helvetica-Bold", 12)
        canvas.drawString(50, self.height - 30, "FIGURE 1: AI MODEL SCANNER - SYSTEM ARCHITECTURE")
        
        # Main platform box
        canvas.setStrokeColor(black)
        canvas.setFillColor(lightgrey)
        canvas.rect(100, self.height - 90, 300, 40, fill=1, stroke=1)
        canvas.setFont("Helvetica-Bold", 11)
        canvas.setFillColor(black)
        canvas.drawCentredString(250, self.height - 65, "AI MODEL SCANNER PLATFORM")
        canvas.setFont("Helvetica", 9)
        canvas.drawCentredString(250, self.height - 78, "EU AI Act 2025 Compliance System")
        
        # Three main components
        components = [
            ("INPUT", "Model Files", [".pt", ".h5", ".onnx", ".pkl"]),
            ("PROCESSING", "Analysis Engine", ["Multi-Framework", "Bias Detection", "Compliance"]),
            ("OUTPUT", "Reports", ["Risk Scores", "Penalties", "Certificates"])
        ]
        
        for i, (title, subtitle, items) in enumerate(components):
            x = 50 + i * 150
            y = self.height - 160
            
            # Component box
            canvas.setFillColor(white)
            canvas.rect(x, y, 120, 60, fill=1, stroke=1)
            
            # Title
            canvas.setFont("Helvetica-Bold", 10)
            canvas.drawCentredString(x + 60, y + 45, title)
            canvas.setFont("Helvetica", 9)
            canvas.drawCentredString(x + 60, y + 35, subtitle)
            
            # Items
            canvas.setFont("Helvetica", 8)
            for j, item in enumerate(items):
                canvas.drawCentredString(x + 60, y + 20 - j * 8, item)
        
        # Arrows between components
        canvas.setStrokeColor(black)
        canvas.setLineWidth(2)
        # Arrow 1 -> 2
        canvas.line(170, self.height - 130, 200, self.height - 130)
        canvas.line(195, self.height - 125, 200, self.height - 130)
        canvas.line(195, self.height - 135, 200, self.height - 130)
        
        # Arrow 2 -> 3
        canvas.line(320, self.height - 130, 350, self.height - 130)
        canvas.line(345, self.height - 125, 350, self.height - 130)
        canvas.line(345, self.height - 135, 350, self.height - 130)
        
        # Framework support boxes
        frameworks = ["PyTorch", "TensorFlow", "ONNX", "scikit-learn"]
        canvas.setFont("Helvetica", 8)
        for i, fw in enumerate(frameworks):
            x = 80 + i * 85
            canvas.rect(x, self.height - 250, 70, 20, fill=1, stroke=1)
            canvas.drawCentredString(x + 35, self.height - 235, fw)
    
    def _draw_bias_engine(self, canvas):
        """Draw Figure 2: Bias Detection Engine"""
        canvas.setFont("Helvetica-Bold", 12)
        canvas.drawString(50, self.height - 30, "FIGURE 2: BIAS DETECTION ENGINE")
        
        # Main engine box
        canvas.setFillColor(lightgrey)
        canvas.rect(50, self.height - 80, 400, 35, fill=1, stroke=1)
        canvas.setFont("Helvetica-Bold", 11)
        canvas.setFillColor(black)
        canvas.drawCentredString(250, self.height - 58, "BIAS DETECTION ENGINE")
        canvas.setFont("Helvetica", 9)
        canvas.drawCentredString(250, self.height - 70, "Mathematical Fairness Assessment")
        
        # Four bias algorithms
        algorithms = [
            ("Demographic Parity", "P(Y=1|A=0) ≈ P(Y=1|A=1)", "80% Threshold"),
            ("Equalized Odds", "TPR_A=0 ≈ TPR_A=1", "Fair Outcomes"),
            ("Calibration Score", "P(Y=1|s,A=0) ≈ P(Y=1|s,A=1)", "Prediction Reliability"),
            ("Individual Fairness", "d(f(x1),f(x2)) ≤ L*d(x1,x2)", "Lipschitz Constraint")
        ]
        
        for i, (name, formula, description) in enumerate(algorithms):
            x = 30 + i * 110
            y = self.height - 150
            
            # Algorithm box
            canvas.setFillColor(white)
            canvas.rect(x, y, 100, 70, fill=1, stroke=1)
            
            # Algorithm name
            canvas.setFont("Helvetica-Bold", 8)
            canvas.drawCentredString(x + 50, y + 60, name)
            
            # Formula
            canvas.setFont("Courier", 7)
            canvas.drawCentredString(x + 50, y + 45, formula)
            
            # Description
            canvas.setFont("Helvetica", 7)
            canvas.drawCentredString(x + 50, y + 30, description)
            
            # Compliance indicator
            canvas.setFillColor(lightgrey)
            canvas.rect(x + 10, y + 5, 80, 15, fill=1, stroke=1)
            canvas.setFont("Helvetica", 7)
            canvas.setFillColor(black)
            canvas.drawCentredString(x + 50, y + 10, f"Algorithm {i+1}")
        
        # Output box
        canvas.setFillColor(gray)
        canvas.rect(100, self.height - 250, 300, 25, fill=1, stroke=1)
        canvas.setFont("Helvetica-Bold", 10)
        canvas.setFillColor(white)
        canvas.drawCentredString(250, self.height - 232, "Overall Bias Score (0-100) + Remediation Recommendations")
    
    def _draw_compliance_matrix(self, canvas):
        """Draw Figure 3: EU AI Act Compliance Matrix"""
        canvas.setFont("Helvetica-Bold", 12)
        canvas.drawString(50, self.height - 30, "FIGURE 3: EU AI ACT COMPLIANCE ASSESSMENT MATRIX")
        
        # Three main article categories
        articles = [
            {
                "title": "ARTICLE 5",
                "subtitle": "Prohibited Practices",
                "items": ["Social Scoring", "Manipulation", "Subliminal Tech", "Biometric ID"],
                "penalty": "€35M or 7% Turnover",
                "color": lightgrey
            },
            {
                "title": "ARTICLES 19-24", 
                "subtitle": "High-Risk Systems",
                "items": ["QMS Required", "Tech Documentation", "Record Keeping", "CE Marking"],
                "penalty": "€15M or 3% Turnover",
                "color": white
            },
            {
                "title": "ARTICLES 51-55",
                "subtitle": "General Purpose AI",
                "items": ["Foundation Models", ">1B Parameters", "Compute Thresholds", "Risk Assessment"],
                "penalty": "€15M or 3% Turnover",
                "color": lightgrey
            }
        ]
        
        for i, article in enumerate(articles):
            x = 50 + i * 150
            y = self.height - 100
            
            # Main article header
            canvas.setFillColor(article["color"])
            canvas.rect(x, y, 130, 30, fill=1, stroke=1)
            canvas.setFont("Helvetica-Bold", 9)
            canvas.setFillColor(black)
            canvas.drawCentredString(x + 65, y + 20, article["title"])
            canvas.setFont("Helvetica", 8)
            canvas.drawCentredString(x + 65, y + 8, article["subtitle"])
            
            # Requirements list
            for j, item in enumerate(article["items"]):
                canvas.setFillColor(white)
                canvas.rect(x, y - 30 - j * 18, 130, 16, fill=1, stroke=1)
                canvas.setFont("Helvetica", 7)
                canvas.setFillColor(black)
                canvas.drawCentredString(x + 65, y - 23 - j * 18, item)
            
            # Penalty box
            canvas.setFillColor(gray)
            canvas.rect(x, y - 130, 130, 20, fill=1, stroke=1)
            canvas.setFont("Helvetica-Bold", 8)
            canvas.setFillColor(white)
            canvas.drawCentredString(x + 65, y - 115, article["penalty"])
        
        # Netherlands specialization box
        canvas.setFillColor(lightgrey)
        canvas.rect(50, self.height - 280, 350, 40, fill=1, stroke=1)
        canvas.setFont("Helvetica-Bold", 10)
        canvas.setFillColor(black)
        canvas.drawCentredString(225, self.height - 255, "NETHERLANDS SPECIALIZATION")
        canvas.setFont("Helvetica", 8)
        canvas.drawCentredString(225, self.height - 268, "BSN Detection • UAVG Compliance • Dutch Privacy Authority (AP) Integration")
    
    def _draw_math_formulas(self, canvas):
        """Draw Figure 4: Mathematical Formulas"""
        canvas.setFont("Helvetica-Bold", 12)
        canvas.drawString(50, self.height - 30, "FIGURE 4: MATHEMATICAL FORMULAS AND ALGORITHMS")
        
        formulas = [
            ("Formula 1 - Demographic Parity:", "P(Y=1|A=0) ≈ P(Y=1|A=1)"),
            ("Formula 2 - Equalized Odds:", "TPR_A=0 ≈ TPR_A=1 AND FPR_A=0 ≈ FPR_A=1"),
            ("Formula 3 - Calibration Score:", "P(Y=1|Score=s,A=0) ≈ P(Y=1|Score=s,A=1)"),
            ("Formula 4 - Individual Fairness:", "d(f(x1),f(x2)) ≤ L*d(x1,x2)"),
            ("Formula 5 - BSN Checksum Validation:", "checksum = Σ(digit_i × (9-i)) mod 11"),
            ("Formula 6 - EU AI Act Penalty:", "penalty = MAX(fixed_amount, revenue × percentage)")
        ]
        
        for i, (name, formula) in enumerate(formulas):
            y = self.height - 80 - i * 35
            
            # Formula container
            canvas.setFillColor(white)
            canvas.rect(50, y - 20, 400, 25, fill=1, stroke=1)
            
            # Formula name
            canvas.setFont("Helvetica-Bold", 9)
            canvas.setFillColor(black)
            canvas.drawString(60, y - 5, name)
            
            # Mathematical formula
            canvas.setFont("Courier", 10)
            canvas.drawString(60, y - 15, formula)

def create_patent_drawings_pdf():
    """Create professional patent drawings PDF"""
    
    doc = SimpleDocTemplate(
        "Professional_Patent_Drawings.pdf",
        pagesize=A4,
        topMargin=0.5*inch,
        bottomMargin=0.5*inch,
        leftMargin=0.5*inch,
        rightMargin=0.5*inch
    )
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'PatentTitle',
        parent=styles['Title'],
        fontSize=16,
        spaceAfter=20,
        alignment=1
    )
    
    story = []
    
    # Title page
    story.append(Paragraph("PATENT DRAWINGS", title_style))
    story.append(Paragraph("System and Method for Automated AI Model Risk Assessment", title_style))
    story.append(Paragraph("and EU AI Act 2025 Compliance Verification", title_style))
    story.append(Spacer(1, 50))
    
    # Patent application info
    info_data = [
        ['Patent Application:', 'Netherlands Patent Office (RVO)'],
        ['Inventor:', 'Vishaal Kumar'],
        ['Filing Date:', 'September 2025'],
        ['Classification:', 'G06N 20/00 (Machine Learning), G06F 21/62 (Data Privacy)'],
        ['Patent Value:', '€10M+ (AI Act Compliance Market)']
    ]
    
    info_table = Table(info_data, colWidths=[1.5*inch, 3*inch])
    info_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    story.append(info_table)
    story.append(PageBreak())
    
    # Figure 1: System Architecture
    story.append(PatentDiagram(500, 300, "system_overview"))
    story.append(PageBreak())
    
    # Figure 2: Bias Detection Engine  
    story.append(PatentDiagram(500, 300, "bias_engine"))
    story.append(PageBreak())
    
    # Figure 3: EU AI Act Compliance Matrix
    story.append(PatentDiagram(500, 320, "compliance_matrix"))
    story.append(PageBreak())
    
    # Figure 4: Mathematical Formulas
    story.append(PatentDiagram(500, 300, "math_formulas"))
    
    # Build PDF
    doc.build(story)
    print("Professional patent drawings created: Professional_Patent_Drawings.pdf")

def create_system_flowchart_pdf():
    """Create detailed system flowchart"""
    
    doc = SimpleDocTemplate(
        "System_Architecture_Flowchart.pdf",
        pagesize=A4,
        topMargin=0.5*inch,
        bottomMargin=0.5*inch,
        leftMargin=0.5*inch,
        rightMargin=0.5*inch
    )
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title', parent=styles['Title'], fontSize=14, alignment=1)
    
    # Flowchart data
    flow_data = [
        ['MODEL INPUT', '→', 'FRAMEWORK DETECTION', '→', 'PARAMETER ANALYSIS'],
        ['PyTorch (.pt, .pth)', '', 'Automatic Detection', '', 'Count: <1M = Low Risk'],
        ['TensorFlow (.h5, .pb)', '', 'File Extension + Header', '', 'Count: 1M-100M = Medium'],
        ['ONNX (.onnx)', '', 'Magic Number Check', '', 'Count: 100M-1B = High'],
        ['scikit-learn (.pkl)', '', 'Object Inspection', '', 'Count: >1B = Very High'],
        ['', '', '', '', ''],
        ['↓', '', '↓', '', '↓'],
        ['', '', '', '', ''],
        ['BIAS DETECTION', '→', 'EU AI ACT COMPLIANCE', '→', 'NETHERLANDS COMPLIANCE'],
        ['Demographic Parity', '', 'Article 5: Prohibited', '', 'BSN Pattern Detection'],
        ['Equalized Odds', '', 'Articles 19-24: High-Risk', '', 'UAVG Validation'],
        ['Calibration Score', '', 'Articles 51-55: GPAI', '', 'AP Authority Check'],
        ['Individual Fairness', '', 'Penalty Calculation', '', 'Regional Multipliers'],
        ['', '', '', '', ''],
        ['↓', '', '↓', '', '↓'],
        ['', '', '', '', ''],
        ['RISK ASSESSMENT', '→', 'REPORT GENERATION', '→', 'COMPLIANCE CERTIFICATE'],
        ['Overall Score: 0-100', '', 'PDF/HTML Output', '', 'Digital Verification'],
        ['Risk Classification', '', 'Technical Documentation', '', 'Legal Framework'],
        ['Penalty Estimation', '', 'Remediation Guide', '', 'AP Authority Stamp']
    ]
    
    flow_table = Table(flow_data, colWidths=[1.6*inch, 0.2*inch, 1.6*inch, 0.2*inch, 1.6*inch])
    
    flow_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('FONTNAME', (0, 0), (4, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 8), (4, 8), 'Helvetica-Bold'),
        ('FONTNAME', (0, 16), (4, 16), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, black),
        ('BACKGROUND', (0, 0), (4, 0), lightgrey),
        ('BACKGROUND', (0, 8), (4, 8), lightgrey),
        ('BACKGROUND', (0, 16), (4, 16), lightgrey),
    ]))
    
    story = [
        Paragraph("SYSTEM ARCHITECTURE AND PROCESSING FLOWCHART", title_style),
        Spacer(1, 20),
        flow_table
    ]
    
    doc.build(story)
    print("System flowchart created: System_Architecture_Flowchart.pdf")

def create_technical_specs_pdf():
    """Create technical specifications document"""
    
    doc = SimpleDocTemplate(
        "Technical_Specifications.pdf",
        pagesize=A4,
        topMargin=0.5*inch,
        bottomMargin=0.5*inch,
        leftMargin=0.5*inch,
        rightMargin=0.5*inch
    )
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title', parent=styles['Title'], fontSize=14, alignment=1)
    
    # Technical specifications
    tech_data = [
        ['COMPONENT', 'SPECIFICATION', 'PERFORMANCE'],
        ['Multi-Framework Support', 'PyTorch, TensorFlow, ONNX, scikit-learn', '100% Coverage'],
        ['Bias Detection Algorithms', '4 Mathematical Fairness Metrics', '95%+ Accuracy'],
        ['EU AI Act Articles', 'Articles 5, 19-24, 51-55, 61-68', '100% Compliance'],
        ['Processing Speed (Standard)', 'Models <1GB: <30 seconds', '95% Efficiency'],
        ['Processing Speed (LLMs)', 'Models >1GB: <5 minutes', '90% Efficiency'],
        ['False Positive Rate', 'Prohibited Practice Detection', '<3% Error Rate'],
        ['Maximum Penalty Detection', '€35M or 7% Global Turnover', '100% Accuracy'],
        ['BSN Detection (Netherlands)', '9-digit Pattern + Checksum', '99% Accuracy'],
        ['File Format Support', '.pt, .pth, .h5, .pb, .onnx, .pkl, .joblib', '100% Support'],
        ['Concurrent Processing', '10+ Models Simultaneously', '90% Resource Efficiency'],
        ['Model Size Limit', 'Up to 10GB (Large Language Models)', '100% Coverage'],
        ['Memory Usage', 'Dynamic Allocation: 512MB-8GB', '95% Optimization'],
        ['Database Storage', 'PostgreSQL with Connection Pooling', '99% Reliability'],
        ['Caching System', 'Redis Multi-level Cache', '90% Hit Rate'],
        ['Security Features', 'Encrypted Storage + Auto-cleanup', '100% Secure']
    ]
    
    tech_table = Table(tech_data, colWidths=[2*inch, 2.5*inch, 1.5*inch])
    
    tech_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 1, black),
        ('BACKGROUND', (0, 0), (-1, 0), lightgrey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, lightgrey])
    ]))
    
    story = [
        Paragraph("TECHNICAL SPECIFICATIONS AND PERFORMANCE METRICS", title_style),
        Spacer(1, 20),
        tech_table
    ]
    
    doc.build(story)
    print("Technical specifications created: Technical_Specifications.pdf")

if __name__ == "__main__":
    print("Creating professional patent drawings...")
    create_patent_drawings_pdf()
    create_system_flowchart_pdf()
    create_technical_specs_pdf()
    print("\n✅ All professional patent documents created successfully!")
    print("\nCreated files:")
    print("  📋 Professional_Patent_Drawings.pdf - Main patent diagrams")
    print("  🔄 System_Architecture_Flowchart.pdf - Detailed system flow")
    print("  📊 Technical_Specifications.pdf - Performance specifications")