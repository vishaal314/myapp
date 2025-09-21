#!/usr/bin/env python3
"""
Comprehensive Production Syntax Fix for DataGuardian Pro
Handles multiple syntax errors systematically
"""

import re
import os
import subprocess
from typing import List, Tuple

def backup_file(filepath: str) -> str:
    """Create a backup of the file"""
    backup_path = f"{filepath}.comprehensive_backup_{os.getpid()}"
    with open(filepath, 'r') as original:
        content = original.read()
    with open(backup_path, 'w') as backup:
        backup.write(content)
    print(f"💾 Created backup: {backup_path}")
    return backup_path

def fix_st_metric_syntax_errors(content: str) -> str:
    """Fix all st.metric syntax errors systematically"""
    print("🔧 Fixing st.metric syntax errors...")
    
    # Split into lines for easier processing
    lines = content.split('\n')
    fixed_lines = []
    fixes_applied = 0
    
    for i, line in enumerate(lines):
        if 'st.metric(' in line:
            original_line = line
            
            # Fix 1: Remove extra closing parentheses at the end
            if line.strip().endswith('))'):
                # Count opening and closing parentheses
                open_count = line.count('(')
                close_count = line.count(')')
                
                if close_count > open_count:
                    # Remove extra closing parentheses
                    excess = close_count - open_count
                    line = line.rstrip(')')
                    line += ')' * open_count
                    print(f"  Line {i+1}: Fixed extra closing parentheses")
                    fixes_applied += 1
            
            # Fix 2: Add missing closing parentheses
            elif 'st.metric(' in line and not line.strip().endswith(')'):
                open_count = line.count('(')
                close_count = line.count(')')
                
                if open_count > close_count:
                    missing = open_count - close_count
                    line = line.rstrip() + ')' * missing
                    print(f"  Line {i+1}: Added {missing} missing closing parentheses")
                    fixes_applied += 1
            
            # Fix 3: Handle malformed st.metric calls
            if 'st.metric(' in line and ',' not in line and not line.strip().endswith(')'):
                # This looks like an incomplete st.metric call
                if line.strip().endswith('st.metric('):
                    line = line.replace('st.metric(', 'st.metric("Metric", "Value")')
                    print(f"  Line {i+1}: Fixed incomplete st.metric call")
                    fixes_applied += 1
        
        fixed_lines.append(line)
    
    print(f"✅ Applied {fixes_applied} st.metric fixes")
    return '\n'.join(fixed_lines)

def fix_indentation_and_structure(content: str) -> str:
    """Fix basic indentation and structure issues"""
    print("🔧 Fixing indentation and structure...")
    
    lines = content.split('\n')
    fixed_lines = []
    fixes_applied = 0
    
    for i, line in enumerate(lines):
        # Fix common indentation issues after with statements
        if i > 0 and lines[i-1].strip().endswith(':') and line.strip() and not line.startswith(' '):
            # Previous line ends with colon, current line should be indented
            if 'with col' in lines[i-1] or 'if ' in lines[i-1] or 'def ' in lines[i-1]:
                line = '    ' + line
                print(f"  Line {i+1}: Fixed indentation after colon")
                fixes_applied += 1
        
        fixed_lines.append(line)
    
    print(f"✅ Applied {fixes_applied} indentation fixes")
    return '\n'.join(fixed_lines)

def validate_python_syntax(filepath: str) -> bool:
    """Validate Python syntax of the file"""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        
        # Try to compile the code
        compile(content, filepath, 'exec')
        return True
    except SyntaxError as e:
        print(f"❌ Syntax error at line {e.lineno}: {e.msg}")
        return False
    except Exception as e:
        print(f"❌ Other error: {e}")
        return False

def main():
    """Main function to fix all syntax errors"""
    print("🚀 DataGuardian Pro - Comprehensive Production Syntax Fix")
    print("=" * 60)
    
    app_path = "/opt/dataguardian/app.py"
    
    if not os.path.exists(app_path):
        print(f"❌ File not found: {app_path}")
        return False
    
    # Create backup
    backup_path = backup_file(app_path)
    
    # Read content
    with open(app_path, 'r') as f:
        content = f.read()
    
    # Apply fixes
    original_content = content
    content = fix_st_metric_syntax_errors(content)
    content = fix_indentation_and_structure(content)
    
    # Write fixed content
    with open(app_path, 'w') as f:
        f.write(content)
    
    # Validate syntax
    print("🔍 Validating Python syntax...")
    if validate_python_syntax(app_path):
        print("✅ Python syntax is valid!")
        return True
    else:
        print("❌ Syntax validation failed, restoring backup")
        with open(backup_path, 'r') as f:
            backup_content = f.read()
        with open(app_path, 'w') as f:
            f.write(backup_content)
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 SUCCESS! All syntax errors fixed!")
        print("📋 Ready to restart DataGuardian service")
    else:
        print("\n❌ Fix failed - manual intervention required")
        exit(1)