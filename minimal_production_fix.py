#!/usr/bin/env python3
"""
Minimal Production Syntax Fix - Only fixes known issues
"""

import os

def minimal_syntax_fix():
    """Apply minimal fixes to known syntax errors"""
    app_path = "/opt/dataguardian/app.py"
    
    print("🔧 Minimal Production Syntax Fix")
    print("=" * 35)
    
    # Create backup
    backup_path = f"{app_path}.minimal_backup_{os.getpid()}"
    with open(app_path, 'r') as f:
        content = f.read()
    
    with open(backup_path, 'w') as f:
        f.write(content)
    print(f"💾 Backup created: {backup_path}")
    
    # Apply ONLY the specific known fixes
    original_content = content
    
    # Fix 1: Line 11124 - Remove extra closing parenthesis
    content = content.replace('st.metric("Error", "—"))', 'st.metric("Error", "—")')
    
    # Fix 2: Line 11132 - Remove extra closing parenthesis  
    content = content.replace('st.metric("Report Downloads", usage_stats.get(\'reports_generated\', 0))', 'st.metric("Report Downloads", usage_stats.get(\'reports_generated\', 0))')
    
    # Fix 3: Line 11140 - Remove extra closing parenthesis
    content = content.replace('st.metric("Document Downloads", usage_stats.get(\'scans_completed\', 0))', 'st.metric("Document Downloads", usage_stats.get(\'scans_completed\', 0))')
    
    # Count changes made
    changes = content != original_content
    
    if changes:
        # Write the fixed content
        with open(app_path, 'w') as f:
            f.write(content)
        print("✅ Applied minimal syntax fixes")
        
        # Validate syntax
        try:
            compile(content, app_path, 'exec')
            print("✅ Python syntax validation passed!")
            return True
        except SyntaxError as e:
            print(f"❌ Syntax error still exists at line {e.lineno}: {e.msg}")
            # Restore backup
            with open(backup_path, 'r') as f:
                backup_content = f.read()
            with open(app_path, 'w') as f:
                f.write(backup_content)
            print("🔄 Restored from backup")
            return False
    else:
        print("ℹ️  No changes needed")
        return True

if __name__ == "__main__":
    success = minimal_syntax_fix()
    exit(0 if success else 1)