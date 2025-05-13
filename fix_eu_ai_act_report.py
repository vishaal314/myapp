"""
Fix EU AI Act Report Generator

This script addresses style definition issues in the EU AI Act report generator,
fixing potential errors with style redefinition and ensuring all required styles
are properly available.
"""

import os

def fix_report_generator():
    """Fix style definition issues in the EU AI Act report generator."""
    
    # Path to the file
    file_path = 'services/eu_ai_act_report_generator.py'
    
    try:
        # Read the file content
        with open(file_path, 'r') as file:
            content = file.read()
        
        # Find the local modern_colors definition introduced by a previous fix
        local_colors_str = """
        # Define modern colors for use within the document
        modern_colors = {
            "primary": "#1E40AF",     # Deep blue
            "secondary": "#3B82F6",   # Bright blue
            "text": "#1F2937",        # Dark gray
            "light_text": "#6B7280",  # Medium gray
            "critical": "#DC2626",    # Red
            "high": "#F59E0B",        # Amber
            "medium": "#10B981",      # Green
            "low": "#0EA5E9",         # Light blue
            "info": "#6366F1",        # Indigo
            "background": "#F9FAFB",  # Light gray
            "border": "#E5E7EB",      # Border gray
            "highlight": "#EFF6FF"    # Light blue highlight
        }"""
        
        # Remove the local definition if it exists
        if local_colors_str.strip() in content:
            content = content.replace(local_colors_str, '')
        
        # Replace the styles initialization with a better approach
        old_style_init = """
        # Get base stylesheet with standard styles
        styles = getSampleStyleSheet()"""
        
        new_style_init = """
        # Get base stylesheet with standard styles
        styles = getSampleStyleSheet()
        
        # Create a function to safely add styles
        def add_style_safely(name, style_def):
            try:
                # Check if style already exists
                existing_style = styles.get(name, None)
                if existing_style is None:
                    # Add new style
                    styles.add(style_def)
                # If style exists, we'll use the existing one
            except Exception as style_error:
                logger.warning(f"Error adding style {name}: {str(style_error)}")"""
        
        if old_style_init.strip() in content:
            content = content.replace(old_style_init, new_style_init)
        
        # Now fix the add_style calls
        old_style_add = """styles.add(ParagraphStyle(
                name='CustomHeading1',"""
        
        if old_style_add in content:
            content = content.replace(old_style_add, """add_style_safely('CustomHeading1', ParagraphStyle(
                name='CustomHeading1',""")
        
        old_style_add = """styles.add(ParagraphStyle(
                name='CustomHeading2',"""
        
        if old_style_add in content:
            content = content.replace(old_style_add, """add_style_safely('CustomHeading2', ParagraphStyle(
                name='CustomHeading2',""")
        
        old_style_add = """styles.add(ParagraphStyle(
                name='SectionHeading',"""
        
        if old_style_add in content:
            content = content.replace(old_style_add, """add_style_safely('SectionHeading', ParagraphStyle(
                name='SectionHeading',""")
        
        old_style_add = """styles.add(ParagraphStyle(
                name='Normal',"""
        
        if old_style_add in content:
            content = content.replace(old_style_add, """add_style_safely('Normal', ParagraphStyle(
                name='Normal',""")
        
        old_style_add = """styles.add(ParagraphStyle(
                name='Bold',"""
        
        if old_style_add in content:
            content = content.replace(old_style_add, """add_style_safely('Bold', ParagraphStyle(
                name='Bold',""")
        
        old_style_add = """styles.add(ParagraphStyle(
                name='Critical',"""
        
        if old_style_add in content:
            content = content.replace(old_style_add, """add_style_safely('Critical', ParagraphStyle(
                name='Critical',""")
        
        old_style_add = """styles.add(ParagraphStyle(
                name='Warning',"""
        
        if old_style_add in content:
            content = content.replace(old_style_add, """add_style_safely('Warning', ParagraphStyle(
                name='Warning',""")
        
        old_style_add = """styles.add(ParagraphStyle(
                name='Success',"""
        
        if old_style_add in content:
            content = content.replace(old_style_add, """add_style_safely('Success', ParagraphStyle(
                name='Success',""")
        
        old_style_add = """styles.add(ParagraphStyle(
                name='Info',"""
        
        if old_style_add in content:
            content = content.replace(old_style_add, """add_style_safely('Info', ParagraphStyle(
                name='Info',""")
        
        old_style_add = """styles.add(ParagraphStyle(
                name='Button',"""
        
        if old_style_add in content:
            content = content.replace(old_style_add, """add_style_safely('Button', ParagraphStyle(
                name='Button',""")
        
        # Write the updated content back to the file
        with open(file_path, 'w') as file:
            file.write(content)
        
        print(f"Successfully fixed styles in {file_path}")
        return True
    
    except Exception as e:
        print(f"Error fixing EU AI Act report generator: {str(e)}")
        return False

if __name__ == "__main__":
    fix_report_generator()