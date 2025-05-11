"""
Script to generate a modern, minimal DataGuardian Pro logo as an SVG file.
This is a clean, icon-only logo design with no text.
"""

import os
import cairosvg
from io import BytesIO

# Define a clean, modern SVG logo for DataGuardian Pro - icon only, no text
LOGO_SVG = '''
<svg width="120" height="120" xmlns="http://www.w3.org/2000/svg">
  <!-- Modern Gradients -->
  <defs>
    <linearGradient id="shield-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#1E3A8A;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#3B82F6;stop-opacity:1" />
    </linearGradient>
    <linearGradient id="ring-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#3B82F6;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#93C5FD;stop-opacity:1" />
    </linearGradient>
  </defs>
  
  <!-- Outer ring for modern look -->
  <circle cx="60" cy="60" r="55" fill="none" stroke="url(#ring-gradient)" stroke-width="2" />
  
  <!-- Modern Shield Shape -->
  <path d="M60,15 C75,15 85,20 95,30 L95,60 C95,80 75,95 60,100 C45,95 25,80 25,60 L25,30 C35,20 45,15 60,15 Z" 
        fill="url(#shield-gradient)" />
  
  <!-- Modern check mark -->
  <path d="M45,60 L55,70 L75,48" stroke="white" stroke-width="4" fill="none" 
        stroke-linecap="round" stroke-linejoin="round" />
        
  <!-- Subtle data protection element -->
  <circle cx="60" cy="60" r="32" fill="none" stroke="rgba(255,255,255,0.2)" stroke-width="1" />
  <path d="M60,34 L60,34 C65,34 69,36 73,40 C77,44 78,48 78,52 C78,60 70,69 60,72 C50,69 42,60 42,52 C42,48 43,44 47,40 C51,36 55,34 60,34 Z" 
        fill="none" stroke="rgba(255,255,255,0.4)" stroke-width="1" />
</svg>
'''

def generate_logo_png(output_path='static/dataguardian_logo.png', width=300, height=300):
    """Generate PNG logo from SVG and save to file"""
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Convert SVG to PNG
        png_data = cairosvg.svg2png(bytestring=LOGO_SVG.encode('utf-8'), 
                                   output_width=width, 
                                   output_height=height)
        
        # Save to file
        with open(output_path, 'wb') as f:
            f.write(png_data)
            
        print(f"Logo generated and saved to {output_path}")
        return True
    except Exception as e:
        print(f"Error generating logo: {str(e)}")
        return False

def get_logo_as_bytes():
    """Return the logo as bytes for in-memory usage"""
    try:
        # Convert SVG to PNG - use square dimensions for the modern icon-only logo
        png_data = cairosvg.svg2png(bytestring=LOGO_SVG.encode('utf-8'),
                                   output_width=250,
                                   output_height=250)
        return png_data
    except Exception as e:
        print(f"Error generating logo bytes: {str(e)}")
        return None

def get_logo_stream():
    """Get logo as a BytesIO stream for ReportLab"""
    try:
        png_data = get_logo_as_bytes()
        if png_data:
            return BytesIO(png_data)
        return None
    except Exception as e:
        print(f"Error creating logo stream: {str(e)}")
        return None

if __name__ == "__main__":
    generate_logo_png()
    print("Logo generation complete!")