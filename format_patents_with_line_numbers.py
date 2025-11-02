#!/usr/bin/env python3
"""
Add line numbering to patent files matching RVO.nl format.
Line numbers every 5 lines for Description, Conclusions, and Drawings sections.
No line numbers for Extract section.
"""

import os
import re

def clean_markdown(content):
    """Remove all markdown formatting."""
    # Remove markdown headers
    content = re.sub(r'^#+\s*', '', content, flags=re.MULTILINE)
    
    # Remove bold/italic
    content = content.replace('**', '')
    content = content.replace('*', '')
    
    # Remove code blocks
    content = re.sub(r'```python\n', '', content)
    content = re.sub(r'```\n', '', content)
    content = re.sub(r'```', '', content)
    
    # Remove horizontal rules
    content = re.sub(r'^---+\n', '', content, flags=re.MULTILINE)
    
    # Clean up extra blank lines (max 2 consecutive)
    content = re.sub(r'\n{3,}', '\n\n', content)
    
    return content

def add_line_numbers(content):
    """Add line numbers every 5 lines to content."""
    lines = content.split('\n')
    formatted_lines = []
    line_counter = 5
    
    for i, line in enumerate(lines, 1):
        # Add line number every 5 lines
        if i % 5 == 0:
            formatted_lines.append(f"{line_counter:>3}  {line}")
            line_counter += 5
        else:
            # Add 5 spaces padding for non-numbered lines
            formatted_lines.append(f"     {line}")
    
    return '\n'.join(formatted_lines)

def create_complete_patent(patent_number, patent_name):
    """Create complete patent .txt file with proper formatting."""
    base_path = f"patents/{patent_number:02d}_{patent_name.replace(' ', '_')}"
    output_path = f"patents/Patent_{patent_number:02d}_{patent_name.replace(' ', '_')}_FORMATTED.txt"
    
    sections = [
        ('01_Description_Beschrijving.md', True),
        ('02_Conclusions_Conclusies.md', True),
        ('03_Drawings_Tekeningen.md', True),
        ('04_Extract_Uittreksel.md', False)  # No line numbers for extract
    ]
    
    complete_content = []
    
    for section_file, add_numbers in sections:
        section_path = os.path.join(base_path, section_file)
        if os.path.exists(section_path):
            with open(section_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Clean up all markdown formatting
            content = clean_markdown(content)
            content = content.strip()
            
            if add_numbers:
                # Add line numbers
                formatted_content = add_line_numbers(content)
            else:
                formatted_content = content
            
            complete_content.append(formatted_content)
            complete_content.append('\n\n')
            complete_content.append('=' * 79)
            complete_content.append('\n\n')
    
    # Write complete formatted file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(''.join(complete_content))
    
    # Get file stats
    with open(output_path, 'r', encoding='utf-8') as f:
        line_count = len(f.readlines())
    
    file_size = os.path.getsize(output_path)
    
    print(f"✓ Created {output_path} ({line_count} lines, {file_size//1024}KB)")

# Create all 6 formatted patents
patents = [
    (1, "Predictive_Compliance_Engine"),
    (2, "Intelligent_Database_Scanner"),
    (3, "Cloud_Sustainability_Scanner"),
    (4, "DPIA_Scanner"),
    (5, "Enterprise_Connector_Platform"),
    (6, "Vendor_Risk_Management")
]

print("Formatting all 6 patents with proper line numbering...\n")

for patent_num, patent_name in patents:
    create_complete_patent(patent_num, patent_name)

print("\n✅ All 6 patents formatted with proper line numbering matching RVO.nl format!")
