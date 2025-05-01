"""
Data Optimization Functions for Report Generation

This module provides functions for optimizing large datasets in reports
to ensure smooth PDF and HTML generation even with very large findings sets.
"""

import copy
import logging
from typing import Dict, Any, List


def optimize_scan_data_for_report(scan_data: Dict[str, Any], report_format: str) -> Dict[str, Any]:
    """
    Optimizes the scan data for report generation by removing unnecessary data
    and limiting large datasets to improve performance.
    
    Args:
        scan_data: The original scan data dictionary
        report_format: The report format being used
        
    Returns:
        Optimized scan data dictionary
    """
    logger = logging.getLogger(__name__)
    
    # Create a shallow copy of the scan data to avoid modifying the original
    optimized_data = copy.copy(scan_data)
    
    # For findings with large datasets, limit to the most critical items first
    if 'findings' in optimized_data and len(optimized_data['findings']) > 250:
        logger.info(f"Optimizing large findings dataset: {len(optimized_data['findings'])} items")
        
        # Sort by risk level to prioritize high-risk findings
        risk_priority = {"high": 0, "medium": 1, "low": 2}
        
        # Create a new list with sorted findings
        sorted_findings = sorted(
            optimized_data['findings'],
            key=lambda x: risk_priority.get(x.get('risk_level', '').lower(), 999)
        )
        
        # Keep only top 250 findings (focusing on most critical ones)
        optimized_data['findings'] = sorted_findings[:250]
        optimized_data['limited_report'] = True
        
        # Add a note about the limitation
        if 'recommendations' not in optimized_data:
            optimized_data['recommendations'] = []
            
        optimized_data['recommendations'].append({
            'title': 'Report Size Limitation',
            'priority': 'Information',
            'description': f'This report contains only the top 250 findings out of {len(scan_data["findings"])} total findings. The most critical issues are included first.',
            'steps': ['Review the complete findings in the detailed web interface']
        })
        
        logger.info(f"Optimized findings dataset to 250 items")
    
    # For SOC2 reports, optimize the TSC checklist if it's very large
    if report_format == 'soc2' and 'soc2_tsc_checklist' in optimized_data:
        checklist = optimized_data['soc2_tsc_checklist']
        if len(checklist) > 100:
            logger.info(f"Optimizing large SOC2 TSC checklist: {len(checklist)} items")
            
            # Focus on failed criteria first
            failed_criteria = {k: v for k, v in checklist.items() 
                              if not v.get("status", False)}
            
            # If there are many failed criteria, keep only a subset for the PDF
            if len(failed_criteria) > 50:
                criteria_keys = list(failed_criteria.keys())
                optimized_checklist = {k: checklist[k] for k in criteria_keys[:50]}
                
                # Add a note about the criteria being limited
                optimized_data['soc2_tsc_checklist_limited'] = True
                optimized_data['soc2_tsc_checklist'] = optimized_checklist
                
                logger.info(f"Optimized SOC2 TSC checklist to 50 failed criteria")
    
    # If raw data field exists and is very large, remove it for the report
    if 'raw_data' in optimized_data and isinstance(optimized_data['raw_data'], (str, bytes)):
        if isinstance(optimized_data['raw_data'], str) and len(optimized_data['raw_data']) > 10000:
            optimized_data['raw_data'] = f"[Large raw data removed for report generation - {len(optimized_data['raw_data'])} characters]"
        elif isinstance(optimized_data['raw_data'], bytes) and len(optimized_data['raw_data']) > 10000:
            optimized_data['raw_data'] = f"[Large raw data removed for report generation - {len(optimized_data['raw_data'])} bytes]"
    
    # Optimize image data for reports 
    if 'images' in optimized_data and isinstance(optimized_data['images'], list) and len(optimized_data['images']) > 5:
        # Keep only first 5 images for reports
        optimized_data['images'] = optimized_data['images'][:5]
        optimized_data['images_limited'] = True
    
    # Remove any large debug data
    for key in ['debug_info', 'verbose_output', 'raw_results']:
        if key in optimized_data:
            optimized_data[key] = "[Removed for optimization]"
    
    return optimized_data