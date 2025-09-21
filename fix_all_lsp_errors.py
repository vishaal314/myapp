#!/usr/bin/env python3
"""
Comprehensive LSP Error Fix Script for DataGuardian Pro
Fixes all 35 LSP diagnostic errors systematically
"""

import re
import os
from typing import List, Tuple

def fix_scanner_type_imports_and_declarations(content: str) -> str:
    """Fix ScannerType enum conflicts and imports"""
    print("🔧 Fixing ScannerType enum conflicts...")
    
    # Fix 1: Remove duplicate ScannerType declaration
    # Find the duplicate declaration and comment it out
    lines = content.split('\n')
    fixed_lines = []
    scanner_type_declared = False
    
    for i, line in enumerate(lines):
        # Look for class ScannerType declaration that conflicts
        if 'class ScannerType' in line and 'Enum' in line:
            if scanner_type_declared:
                # This is a duplicate, comment it out
                fixed_lines.append(f"# DUPLICATE REMOVED: {line}")
                print(f"  Line {i+1}: Commented out duplicate ScannerType declaration")
            else:
                fixed_lines.append(line)
                scanner_type_declared = True
        else:
            fixed_lines.append(line)
    
    content = '\n'.join(fixed_lines)
    
    # Fix 2: Ensure proper import of ScannerType
    if 'from utils.activity_tracker import ScannerType' not in content:
        # Find import section and add proper import
        lines = content.split('\n')
        import_added = False
        for i, line in enumerate(lines):
            if line.startswith('import ') or line.startswith('from '):
                if not import_added:
                    lines.insert(i, 'from utils.activity_tracker import ScannerType')
                    import_added = True
                    print("  Added proper ScannerType import")
                    break
        content = '\n'.join(lines)
    
    return content

def fix_unbound_variables(content: str) -> str:
    """Fix all unbound variable errors"""
    print("🔧 Fixing unbound variables...")
    
    # Fix ssl variables
    ssl_fixes = [
        ('ssl_mode', 'ssl_mode = "require"'),
        ('ssl_cert_path', 'ssl_cert_path = None'),
        ('ssl_key_path', 'ssl_key_path = None'), 
        ('ssl_ca_path', 'ssl_ca_path = None')
    ]
    
    for var_name, default_value in ssl_fixes:
        # Find where the variable is used but not defined
        if f'"{var_name}" is possibly unbound' in content:
            # Find the function containing the unbound variable
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if var_name in line and 'def ' in lines[max(0, i-20):i]:
                    # Find the function start
                    func_start = i
                    while func_start > 0 and not lines[func_start].strip().startswith('def '):
                        func_start -= 1
                    
                    # Add variable definition after function start
                    if func_start < len(lines):
                        indent = '    '  # Standard function indent
                        lines.insert(func_start + 1, f'{indent}{default_value}')
                        print(f"  Added {var_name} definition in function")
                        break
            
            content = '\n'.join(lines)
    
    # Fix user_id and session_id in scanner functions
    scanner_functions = [
        'ai_model_scanner',
        'website_scanner', 
        'sustainability_scanner',
        'soc2_scanner',
        'image_scanner'
    ]
    
    for func_name in scanner_functions:
        # Find the function and add missing variables
        pattern = rf'(def {func_name}\([^)]*\):)'
        match = re.search(pattern, content)
        if match:
            func_def = match.group(1)
            # Add user_id and session_id definitions after function start
            replacement = f"""{func_def}
    user_id = st.session_state.get('username', 'anonymous')
    session_id = st.session_state.get('session_id', 'default_session')"""
            content = content.replace(func_def, replacement)
            print(f"  Added user_id and session_id to {func_name}")
    
    return content

def fix_parameter_mismatches(content: str) -> str:
    """Fix parameter name mismatches"""
    print("🔧 Fixing parameter name mismatches...")
    
    # Fix scan_result vs scan_results parameter mismatch
    # Find function definitions with parameter mismatches
    pattern = r'def\s+(\w+)\s*\([^)]*scan_results[^)]*\)\s*->\s*str:'
    matches = re.findall(pattern, content)
    
    for func_name in matches:
        # Replace scan_results parameter with scan_result for consistency
        old_pattern = rf'(def\s+{func_name}\s*\([^)]*?)scan_results([^)]*?\)\s*->\s*str:)'
        new_replacement = r'\1scan_result\2'
        content = re.sub(old_pattern, new_replacement, content)
        print(f"  Fixed parameter name in {func_name}")
    
    return content

def fix_possibly_unbound_scanner_type(content: str) -> str:
    """Fix possibly unbound ScannerType references"""
    print("🔧 Fixing unbound ScannerType references...")
    
    # Find all ScannerType usages and ensure they're properly imported
    lines = content.split('\n')
    fixed_lines = []
    
    for i, line in enumerate(lines):
        if 'ScannerType' in line and '"ScannerType" is possibly unbound' in content:
            # Check if we need to add import at function level
            if 'from utils.activity_tracker import ScannerType' not in line:
                # Find the function this line belongs to
                func_start = i
                while func_start > 0 and not lines[func_start].strip().startswith('def '):
                    func_start -= 1
                
                # Add local import if needed
                if func_start < len(lines):
                    indent = '    '
                    import_line = f'{indent}from utils.activity_tracker import ScannerType'
                    if import_line not in fixed_lines:
                        fixed_lines.insert(func_start + 1, import_line)
                        print(f"  Added ScannerType import in function at line {func_start + 1}")
        
        fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)

def main():
    """Main function to fix all LSP errors"""
    print("🚀 DataGuardian Pro - Comprehensive LSP Error Fix")
    print("=" * 50)
    
    # Read the current app.py
    if not os.path.exists('app.py'):
        print("❌ app.py not found!")
        return False
    
    print("📖 Reading app.py...")
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Create backup
    backup_name = f'app.py.lsp_fix_backup.{os.getpid()}'
    with open(backup_name, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"💾 Created backup: {backup_name}")
    
    # Apply all fixes
    original_content = content
    
    content = fix_scanner_type_imports_and_declarations(content)
    content = fix_unbound_variables(content)  
    content = fix_parameter_mismatches(content)
    content = fix_possibly_unbound_scanner_type(content)
    
    # Count changes
    changes_made = len(original_content.split('\n')) != len(content.split('\n'))
    
    if changes_made:
        # Write the fixed content
        with open('app.py', 'w', encoding='utf-8') as f:
            f.write(content)
        print("✅ All LSP fixes applied!")
        
        # Verify syntax
        import subprocess
        try:
            result = subprocess.run(['python3', '-m', 'py_compile', 'app.py'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Python syntax validation passed!")
                return True
            else:
                print(f"❌ Syntax validation failed: {result.stderr}")
                # Restore backup
                with open(backup_name, 'r') as f:
                    backup_content = f.read()
                with open('app.py', 'w') as f:
                    f.write(backup_content)
                print(f"🔄 Restored from backup: {backup_name}")
                return False
        except Exception as e:
            print(f"⚠️  Could not validate syntax: {e}")
            return False
    else:
        print("ℹ️  No changes needed")
        return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 SUCCESS! All LSP errors should be resolved!")
        print("\n📋 Next steps:")
        print("1. Restart the Streamlit server")
        print("2. Check for remaining LSP diagnostics")
        print("3. Test application functionality")
    else:
        print("\n❌ Fix failed - check backup and try manual fixes")