"""
Code Bloat Scanner module for detecting code inefficiencies.

This module analyzes Python codebases to detect bloat, unused imports,
and other efficiency issues that can reduce sustainability.
"""

import os
import re
import ast
import importlib
import time
from collections import defaultdict
from typing import Dict, List, Any, Set, Tuple
import logging

# Import centralized logging
try:
    from utils.centralized_logger import get_scanner_logger
    logger = get_scanner_logger("code_bloat_scanner")
except ImportError:
    # Fallback to standard logging if centralized logger not available
    logger = logging.getLogger(__name__)

# Threshold for large file size in bytes
LARGE_FILE_THRESHOLD_BYTES = 100 * 1024  # 100 KB


class CodeBloatScanner:
    """
    Scanner to detect code bloat and inefficiencies in Python code.
    """
    
    def __init__(self):
        """Initialize the code bloat scanner."""
        self.findings = []
        self.files_analyzed = 0
        self.total_size_bytes = 0
        self.unused_imports = []
        self.large_files = []
        self.progress_callback = None
    
    def set_progress_callback(self, callback):
        """Set a callback for progress updates."""
        self.progress_callback = callback
    
    def analyze_directory(self, directory_path: str) -> Dict[str, Any]:
        """
        Analyze all Python files in a directory recursively.
        
        Args:
            directory_path: Path to the directory to analyze
            
        Returns:
            Dictionary with analysis results
        """
        if not os.path.exists(directory_path):
            return {"error": f"Directory not found: {directory_path}"}
        
        # Find all Python files
        python_files = []
        for root, _, files in os.walk(directory_path):
            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))
        
        # Analyze each file
        total_files = len(python_files)
        
        for i, file_path in enumerate(python_files):
            # Update progress
            if self.progress_callback:
                self.progress_callback(i + 1, total_files, f"Analyzing {file_path}")
            
            self.analyze_file(file_path)
        
        # Prepare results
        return self._prepare_results()
    
    def analyze_files(self, file_paths: List[str]) -> Dict[str, Any]:
        """
        Analyze a list of Python files.
        
        Args:
            file_paths: List of file paths to analyze
            
        Returns:
            Dictionary with analysis results
        """
        total_files = len(file_paths)
        
        for i, file_path in enumerate(file_paths):
            # Check if file exists and is a Python file
            if not os.path.exists(file_path) or not file_path.endswith('.py'):
                continue
            
            # Update progress
            if self.progress_callback:
                self.progress_callback(i + 1, total_files, f"Analyzing {file_path}")
            
            self.analyze_file(file_path)
        
        # Prepare results
        return self._prepare_results()
    
    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """
        Analyze a single Python file for bloat.
        
        Args:
            file_path: Path to the Python file
            
        Returns:
            Dictionary with file analysis results
        """
        if not os.path.exists(file_path):
            return {"error": f"File not found: {file_path}"}
        
        # Increment files analyzed counter
        self.files_analyzed += 1
        
        try:
            # Get file size
            file_size = os.path.getsize(file_path)
            self.total_size_bytes += file_size
            
            # Check if file is large
            if file_size > LARGE_FILE_THRESHOLD_BYTES:
                self.large_files.append({
                    "file": file_path,
                    "size_bytes": file_size,
                    "size_kb": file_size / 1024
                })
            
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for unused imports
            self._check_unused_imports(file_path, content)
            
            # Check for code duplication
            self._check_duplication(file_path, content)
            
            # Check for complex code
            self._check_complexity(file_path, content)
            
            # Return file-specific results
            return {
                "file": file_path,
                "size_bytes": file_size,
                "imports": self._extract_imports(content)
            }
            
        except Exception as e:
            self.findings.append({
                "type": "Error",
                "file": file_path,
                "message": f"Error analyzing file: {str(e)}"
            })
            return {"error": str(e)}
    
    def _check_unused_imports(self, file_path: str, content: str) -> None:
        """
        Check for unused imports in a Python file.
        
        Args:
            file_path: Path to the file
            content: File content as string
        """
        try:
            # Parse the content into an AST
            tree = ast.parse(content)
            
            # Find import statements
            imports = {}
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for name in node.names:
                        imports[name.name] = name.asname or name.name
                elif isinstance(node, ast.ImportFrom):
                    module = node.module
                    for name in node.names:
                        if name.name == '*':
                            # Can't track * imports easily
                            continue
                        
                        full_name = f"{module}.{name.name}" if module else name.name
                        alias = name.asname or name.name
                        imports[full_name] = alias
            
            # Find all used names in the code
            used_names = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Name):
                    used_names.add(node.id)
                elif isinstance(node, ast.Attribute):
                    # Handle attribute access (e.g., module.attribute)
                    if isinstance(node.value, ast.Name):
                        used_names.add(node.value.id)
            
            # Find unused imports
            for import_name, import_alias in imports.items():
                # Check the base name (for from x import y cases)
                base_name = import_alias.split('.')[0]
                
                # If the base name is not used, the import is unused
                if base_name not in used_names:
                    # Extract line number using regex
                    import_line = 0
                    pattern = rf"\bimport\s+{base_name}\b|\bfrom\s+\S+\s+import\s+.*\b{base_name}\b"
                    for i, line in enumerate(content.split('\n')):
                        if re.search(pattern, line):
                            import_line = i + 1
                            break
                    
                    self.unused_imports.append({
                        "file": file_path,
                        "line": import_line,
                        "import": import_name,
                        "alias": import_alias
                    })
        
        except SyntaxError:
            # If there's a syntax error, we can't parse the file
            self.findings.append({
                "type": "Syntax Error",
                "file": file_path,
                "message": "Syntax error in file, could not check for unused imports"
            })
    
    def _check_duplication(self, file_path: str, content: str) -> None:
        """
        Check for code duplication in a Python file.
        
        Args:
            file_path: Path to the file
            content: File content as string
        """
        # Very basic duplication check - look for repeated non-trivial code blocks
        lines = content.split('\n')
        line_count = len(lines)
        
        # Skip if file is too small
        if line_count < 20:
            return
        
        # Look for blocks of 5 or more similar lines
        block_size = 5
        duplicated_blocks = []
        
        for i in range(line_count - block_size + 1):
            block1 = '\n'.join(lines[i:i + block_size])
            
            # Skip empty or comment-only blocks
            if not block1.strip() or all(line.strip().startswith('#') for line in block1.split('\n')):
                continue
            
            for j in range(i + block_size, line_count - block_size + 1):
                block2 = '\n'.join(lines[j:j + block_size])
                
                # Check if blocks are similar (simple string comparison)
                if block1 == block2:
                    duplicated_blocks.append({
                        "block1_start": i + 1,
                        "block1_end": i + block_size,
                        "block2_start": j + 1,
                        "block2_end": j + block_size,
                        "content": block1
                    })
        
        # Add findings for duplicated blocks
        if duplicated_blocks:
            self.findings.append({
                "type": "Code Duplication",
                "file": file_path,
                "message": f"Found {len(duplicated_blocks)} duplicated code blocks",
                "duplicated_blocks": duplicated_blocks[:3]  # Include first 3 duplications
            })
    
    def _check_complexity(self, file_path: str, content: str) -> None:
        """
        Check for complex code in a Python file.
        
        Args:
            file_path: Path to the file
            content: File content as string
        """
        try:
            # Parse the content into an AST
            tree = ast.parse(content)
            
            # Find complex functions
            complex_functions = []
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    # Count branches (if/elif/else, for, while, try/except)
                    branches = 0
                    
                    for subnode in ast.walk(node):
                        if isinstance(subnode, (ast.If, ast.For, ast.While, ast.Try)):
                            branches += 1
                    
                    # Calculate cyclomatic complexity (branches + 1)
                    complexity = branches + 1
                    
                    # High complexity threshold
                    if complexity > 10:
                        complex_functions.append({
                            "name": node.name,
                            "complexity": complexity,
                            "line": node.lineno
                        })
            
            # Add findings for complex functions
            if complex_functions:
                self.findings.append({
                    "type": "Complex Code",
                    "file": file_path,
                    "message": f"Found {len(complex_functions)} complex functions",
                    "complex_functions": complex_functions
                })
        
        except SyntaxError:
            # Already handled in unused imports check
            pass
    
    def _extract_imports(self, content: str) -> List[str]:
        """
        Extract import statements from Python code.
        
        Args:
            content: File content as string
            
        Returns:
            List of import statements
        """
        imports = []
        
        # Use regex to find import statements
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('import ') or line.startswith('from '):
                imports.append(line)
        
        return imports
    
    def _prepare_results(self) -> Dict[str, Any]:
        """
        Prepare the final analysis results.
        
        Returns:
            Dictionary with analysis results
        """
        # Calculate code stats
        avg_file_size = self.total_size_bytes / self.files_analyzed if self.files_analyzed > 0 else 0
        
        # Prepare large files with more details
        detailed_large_files = []
        for file in self.large_files:
            file_ext = os.path.splitext(file["file"])[1]
            detailed_large_files.append({
                "file": file["file"],
                "size_bytes": file["size_bytes"],
                "size_kb": file["size_kb"],
                "size_mb": file["size_bytes"] / (1024 * 1024),
                "extension": file_ext,
                "category": "Python Source",
                "recommendation": "Refactor into smaller modules"
            })
        
        # Sort large files by size
        detailed_large_files.sort(key=lambda x: x["size_bytes"], reverse=True)
        
        # Prepare recommendations
        recommendations = []
        
        if len(self.unused_imports) > 0:
            recommendations.append({
                "title": "Remove unused imports",
                "description": f"Found {len(self.unused_imports)} unused imports across {self.files_analyzed} files.",
                "priority": "Low",
                "impact": "Low",
                "savings_potential": "Minimal",
                "steps": [
                    "Use tools like pyflakes or flake8 to automatically detect unused imports",
                    "Set up pre-commit hooks to check for unused imports before committing",
                    "Configure your IDE to highlight unused imports",
                    "Remove or comment out the identified unused imports"
                ]
            })
        
        if len(self.large_files) > 0:
            recommendations.append({
                "title": "Refactor large files",
                "description": f"Found {len(self.large_files)} large files exceeding {LARGE_FILE_THRESHOLD_BYTES/1024} KB.",
                "priority": "Medium",
                "impact": "Medium",
                "savings_potential": "Moderate",
                "steps": [
                    "Split large files into smaller, focused modules",
                    "Extract utility functions into separate modules",
                    "Use proper design patterns to improve modularity",
                    "Implement proper tests before refactoring"
                ]
            })
        
        # Create findings for systematic issues
        if len(self.unused_imports) > 10:
            self.findings.append({
                "type": "Systematic Unused Imports",
                "file": "Multiple files",
                "message": f"Found {len(self.unused_imports)} unused imports across the codebase",
                "risk_level": "low",
                "category": "Code Efficiency",
                "details": {
                    "recommendation": "Set up linting tools to automatically detect and remove unused imports",
                    "impact": "Low memory usage and slightly improved load times"
                }
            })
        
        if avg_file_size > LARGE_FILE_THRESHOLD_BYTES:
            self.findings.append({
                "type": "High Average File Size",
                "file": "All files",
                "message": f"Average file size ({avg_file_size/1024:.2f} KB) exceeds recommended size ({LARGE_FILE_THRESHOLD_BYTES/1024} KB)",
                "risk_level": "medium",
                "category": "Code Structure",
                "details": {
                    "recommendation": "Consider refactoring the codebase into smaller, more focused modules",
                    "impact": "Improved maintainability and development efficiency"
                }
            })
        
        # Prepare final results
        return {
            "scan_id": f"code-bloat-{int(time.time())}",
            "scan_type": "Code Bloat Analysis",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "files_analyzed": self.files_analyzed,
            "total_size_bytes": self.total_size_bytes,
            "total_size_kb": self.total_size_bytes / 1024,
            "total_size_mb": self.total_size_bytes / (1024 * 1024),
            "avg_file_size_kb": avg_file_size / 1024,
            "unused_imports": self.unused_imports,
            "large_files": detailed_large_files,
            "findings": self.findings,
            "recommendations": recommendations,
            "status": "completed"
        }


def scan_directory(directory_path: str, progress_callback=None) -> Dict[str, Any]:
    """
    Scan a directory for code bloat.
    
    Args:
        directory_path: Path to the directory
        progress_callback: Optional callback for progress updates
        
    Returns:
        Dictionary with scan results
    """
    scanner = CodeBloatScanner()
    
    if progress_callback:
        scanner.set_progress_callback(progress_callback)
    
    return scanner.analyze_directory(directory_path)


def scan_files(file_paths: List[str], progress_callback=None) -> Dict[str, Any]:
    """
    Scan a list of files for code bloat.
    
    Args:
        file_paths: List of file paths
        progress_callback: Optional callback for progress updates
        
    Returns:
        Dictionary with scan results
    """
    scanner = CodeBloatScanner()
    
    if progress_callback:
        scanner.set_progress_callback(progress_callback)
    
    return scanner.analyze_files(file_paths)


if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) < 2:
        # Usage: python code_bloat_scanner.py <directory_or_file_path>
        sys.exit(1)
    
    path = sys.argv[1]
    
    if os.path.isdir(path):
        results = scan_directory(path)
    else:
        results = scan_files([path])
    
    # Log summary results for CLI usage
    # Files analyzed: {results['files_analyzed']}
    # Total size: {results['total_size_mb']:.2f} MB
    # Unused imports: {len(results['unused_imports'])}
    # Large files: {len(results['large_files'])}
    # Findings: {len(results['findings'])}
    
    # Log recommendations for CLI usage
    # Recommendations:
    # for rec in results['recommendations']:
    #     - {rec['title']}: {rec['description']}
    pass