"""
Script to generate a modern, professional DataGuardian Pro logo as an SVG file.
"""

import os
import cairosvg
from io import BytesIO

# Define a clean, modern SVG logo for DataGuardian Pro
LOGO_SVG = '''
<svg width="200" height="60" xmlns="http://www.w3.org/2000/svg">
  <!-- Shield Background -->
  <defs>
    <linearGradient id="shield-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#2C5282;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#4299E1;stop-opacity:1" />
    </linearGradient>
  </defs>
  
  <!-- Shield Shape -->
  <path d="M30,5 L30,5 C40,5 48,8 55,15 L55,30 C55,42 44,50 30,55 C16,50 5,42 5,30 L5,15 C12,8 20,5 30,5 Z" 
        fill="url(#shield-gradient)" stroke="#1A365D" stroke-width="1.5"/>
  
  <!-- Check Mark -->
  <path d="M20,30 L27,37 L40,22" stroke="white" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
  
  <!-- Text DataGuardian Pro -->
  <text x="70" y="27" font-family="Arial, sans-serif" font-size="16" font-weight="bold" fill="#2C5282">DataGuardian</text>
  <text x="70" y="45" font-family="Arial, sans-serif" font-size="14" fill="#4A5568">Pro</text>
  
  <!-- Data Protection Icon -->
  <circle cx="175" cy="20" r="8" fill="#4299E1" opacity="0.8"/>
  <path d="M170,20 L175,25 L180,20" stroke="white" stroke-width="1.5" fill="none"/>
</svg>
'''

def generate_logo_png(output_path='static/dataguardian_logo.png', width=500, height=150):
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
        # Convert SVG to PNG
        png_data = cairosvg.svg2png(bytestring=LOGO_SVG.encode('utf-8'),
                                   output_width=400,
                                   output_height=120)
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