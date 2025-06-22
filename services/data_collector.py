"""
Data Collector Service

This service handles collecting data from users, storing it in memory,
and preparing it for report generation. It supports various data types
including DPIA assessments, scan configurations, and user inputs.
"""

import json
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
import streamlit as st

class DataCollector:
    """
    Handles collection and storage of user data in memory for report generation.
    """
    
    def __init__(self):
        self.session_key = "collected_data"
        self.reports_key = "generated_reports"
        
        # Initialize session state if not exists
        if self.session_key not in st.session_state:
            st.session_state[self.session_key] = {}
        
        if self.reports_key not in st.session_state:
            st.session_state[self.reports_key] = []
    
    def collect_user_data(self, data_type: str, data: Dict[str, Any]) -> str:
        """
        Collect and store user data in memory.
        
        Args:
            data_type: Type of data (e.g., 'dpia_assessment', 'scan_config', 'user_input')
            data: Dictionary containing the user data
        
        Returns:
            Unique ID for the collected data
        """
        data_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        collected_entry = {
            'id': data_id,
            'type': data_type,
            'timestamp': timestamp,
            'data': data,
            'user': st.session_state.get('username', 'anonymous')
        }
        
        st.session_state[self.session_key][data_id] = collected_entry
        
        return data_id
    
    def get_collected_data(self, data_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Retrieve collected data from memory.
        
        Args:
            data_id: Specific data ID to retrieve, or None for all data
        
        Returns:
            Dictionary containing the requested data
        """
        if data_id:
            return st.session_state[self.session_key].get(data_id, {})
        else:
            return st.session_state[self.session_key]
    
    def update_data(self, data_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update existing collected data.
        
        Args:
            data_id: ID of data to update
            updates: Dictionary of updates to apply
        
        Returns:
            True if successful, False if data not found
        """
        if data_id in st.session_state[self.session_key]:
            st.session_state[self.session_key][data_id]['data'].update(updates)
            st.session_state[self.session_key][data_id]['last_modified'] = datetime.now().isoformat()
            return True
        return False
    
    def generate_report_data(self, data_ids: List[str] = None) -> Dict[str, Any]:
        """
        Generate comprehensive report data from collected information.
        
        Args:
            data_ids: List of specific data IDs to include, or None for all
        
        Returns:
            Dictionary containing report data
        """
        if data_ids is None:
            data_to_process = list(st.session_state[self.session_key].values())
        else:
            data_to_process = [
                st.session_state[self.session_key][data_id] 
                for data_id in data_ids 
                if data_id in st.session_state[self.session_key]
            ]
        
        report_data = {
            'report_id': str(uuid.uuid4()),
            'generated_at': datetime.now().isoformat(),
            'user': st.session_state.get('username', 'anonymous'),
            'data_summary': {
                'total_entries': len(data_to_process),
                'data_types': {},
                'date_range': self._get_date_range(data_to_process)
            },
            'collected_data': data_to_process,
            'analysis': self._analyze_collected_data(data_to_process)
        }
        
        # Count data types
        for entry in data_to_process:
            data_type = entry.get('type', 'unknown')
            report_data['data_summary']['data_types'][data_type] = \
                report_data['data_summary']['data_types'].get(data_type, 0) + 1
        
        # Store the generated report
        st.session_state[self.reports_key].append(report_data)
        
        return report_data
    
    def _get_date_range(self, data_entries: List[Dict]) -> Dict[str, str]:
        """Get the date range of collected data."""
        if not data_entries:
            return {'start': None, 'end': None}
        
        timestamps = [entry.get('timestamp') for entry in data_entries if entry.get('timestamp')]
        if not timestamps:
            return {'start': None, 'end': None}
        
        return {
            'start': min(timestamps),
            'end': max(timestamps)
        }
    
    def _analyze_collected_data(self, data_entries: List[Dict]) -> Dict[str, Any]:
        """Analyze collected data for insights and patterns."""
        analysis = {
            'privacy_risk_summary': {'high': 0, 'medium': 0, 'low': 0},
            'compliance_status': {},
            'key_findings': [],
            'recommendations': []
        }
        
        for entry in data_entries:
            data_type = entry.get('type', '')
            data_content = entry.get('data', {})
            
            if data_type == 'dpia_assessment':
                self._analyze_dpia_data(data_content, analysis)
            elif data_type == 'scan_results':
                self._analyze_scan_data(data_content, analysis)
            elif data_type == 'user_feedback':
                self._analyze_feedback_data(data_content, analysis)
        
        return analysis
    
    def _analyze_dpia_data(self, dpia_data: Dict, analysis: Dict) -> None:
        """Analyze DPIA assessment data."""
        # Extract risk levels
        if 'risk_assessment' in dpia_data:
            risk_summary = dpia_data['risk_assessment'].get('overall_risk_level', 'low')
            if risk_summary.lower() == 'high':
                analysis['privacy_risk_summary']['high'] += 1
            elif risk_summary.lower() == 'medium':
                analysis['privacy_risk_summary']['medium'] += 1
            else:
                analysis['privacy_risk_summary']['low'] += 1
        
        # Compliance status
        if 'compliance_status' in dpia_data:
            status = dpia_data['compliance_status']
            analysis['compliance_status']['GDPR'] = status.get('gdpr_compliant', False)
            analysis['compliance_status']['Dutch_UAVG'] = status.get('uavg_compliant', False)
        
        # Key findings
        if 'key_findings' in dpia_data:
            analysis['key_findings'].extend(dpia_data['key_findings'])
    
    def _analyze_scan_data(self, scan_data: Dict, analysis: Dict) -> None:
        """Analyze scan results data."""
        # Count findings by risk level
        findings = scan_data.get('findings', [])
        for finding in findings:
            risk_level = finding.get('risk_level', 'low').lower()
            if risk_level in analysis['privacy_risk_summary']:
                analysis['privacy_risk_summary'][risk_level] += 1
    
    def _analyze_feedback_data(self, feedback_data: Dict, analysis: Dict) -> None:
        """Analyze user feedback data."""
        # Extract actionable recommendations from feedback
        if 'recommendations' in feedback_data:
            analysis['recommendations'].extend(feedback_data['recommendations'])
    
    def clear_collected_data(self, data_type: Optional[str] = None) -> None:
        """
        Clear collected data from memory.
        
        Args:
            data_type: Specific data type to clear, or None to clear all
        """
        if data_type is None:
            st.session_state[self.session_key] = {}
        else:
            # Remove entries of specific type
            to_remove = [
                data_id for data_id, entry in st.session_state[self.session_key].items()
                if entry.get('type') == data_type
            ]
            for data_id in to_remove:
                del st.session_state[self.session_key][data_id]
    
    def get_memory_usage(self) -> Dict[str, Any]:
        """Get information about memory usage."""
        total_entries = len(st.session_state[self.session_key])
        total_reports = len(st.session_state[self.reports_key])
        
        # Estimate size (rough calculation)
        estimated_size_kb = len(json.dumps(st.session_state[self.session_key])) / 1024
        
        return {
            'total_data_entries': total_entries,
            'total_reports_generated': total_reports,
            'estimated_memory_usage_kb': round(estimated_size_kb, 2),
            'data_types': self._count_data_types()
        }
    
    def _count_data_types(self) -> Dict[str, int]:
        """Count entries by data type."""
        type_counts = {}
        for entry in st.session_state[self.session_key].values():
            data_type = entry.get('type', 'unknown')
            type_counts[data_type] = type_counts.get(data_type, 0) + 1
        return type_counts

    def export_collected_data(self, format_type: str = 'json') -> str:
        """
        Export collected data in specified format.
        
        Args:
            format_type: Export format ('json', 'csv', etc.)
        
        Returns:
            Serialized data string
        """
        if format_type == 'json':
            return json.dumps(st.session_state[self.session_key], indent=2, default=str)
        elif format_type == 'csv':
            # Convert to CSV format (simplified)
            import pandas as pd
            flattened_data = []
            for entry in st.session_state[self.session_key].values():
                flat_entry = {
                    'id': entry['id'],
                    'type': entry['type'],
                    'timestamp': entry['timestamp'],
                    'user': entry['user'],
                    'data': json.dumps(entry['data'])
                }
                flattened_data.append(flat_entry)
            
            df = pd.DataFrame(flattened_data)
            return df.to_csv(index=False)
        else:
            raise ValueError(f"Unsupported export format: {format_type}")