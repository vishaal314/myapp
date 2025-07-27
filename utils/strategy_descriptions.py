"""
Strategy descriptions for intelligent scanning modes
"""

def get_strategy_description(scan_mode: str) -> str:
    """Get user-friendly description for scanning strategies."""
    descriptions = {
        "smart": "Automatically selects the best strategy based on repository size and structure",
        "sampling": "Fast statistical sampling ideal for large repositories (1000+ files). Analyzes representative subset while maintaining high detection accuracy",
        "priority": "Focuses on high-risk files first (config, auth, API endpoints). Best for security-focused scans with time constraints",
        "progressive": "Incremental depth scanning starting with root files. Perfect for exploring unknown repositories systematically",
        "comprehensive": "Scans every accessible file. Recommended for small repositories (<100 files) or compliance audits requiring 100% coverage"
    }
    return descriptions.get(scan_mode, "Unknown strategy")