#!/usr/bin/env python3
"""
Test script to verify dashboard data display fixes
"""

import sys
import os
import json
from datetime import datetime, timedelta

# Add project root to path
sys.path.append('.')

from services.results_aggregator import ResultsAggregator

def create_test_scan_data():
    """Create test scan data to verify dashboard display"""
    print("Creating test scan data...")
    
    aggregator = ResultsAggregator()
    username = "vishaal314"
    
    # Test scan 1: Code Scanner with cost savings
    test_result_1 = {
        "scan_id": "test_dashboard_001",
        "scan_type": "code",
        "region": "Netherlands",
        "files_scanned": 45,
        "total_pii_found": 5,
        "high_risk_count": 2,
        "findings": [
            {
                "type": "BSN",
                "severity": "High",
                "pii_count": 3,
                "privacy_risk": "High"
            },
            {
                "type": "API_Key",
                "severity": "Critical",
                "pii_count": 2,
                "privacy_risk": "High"
            }
        ],
        "compliance_score": 78.5,
        "cost_savings": {
            "potential_penalties_avoided": 2500000,
            "implementation_cost": 75000,
            "immediate_savings": 2425000,
            "three_year_total_value": 2875000,
            "roi_percentage": 3733.3,
            "vs_onetrust_savings": 1851000
        }
    }
    
    # Store the scan result using the correct method signature
    test_result_1['scan_id'] = "test_dashboard_001"
    scan_id_1 = aggregator.store_scan_result(
        username=username,
        result=test_result_1
    )
    
    # Test scan 2: Website Scanner with cost savings
    test_result_2 = {
        "scan_id": "test_dashboard_002", 
        "scan_type": "website",
        "region": "Netherlands",
        "files_scanned": 12,
        "total_pii_found": 1,
        "high_risk_count": 0,
        "findings": [
            {
                "type": "Cookie_Consent",
                "severity": "Medium",
                "pii_count": 1,
                "privacy_risk": "Medium"
            }
        ],
        "compliance_score": 92.0,
        "cost_savings": {
            "potential_penalties_avoided": 150000,
            "implementation_cost": 12000,
            "immediate_savings": 138000,
            "three_year_total_value": 228000,
            "roi_percentage": 1800.0,
            "vs_onetrust_savings": 1851000
        }
    }
    
    # Store the scan result using the correct method signature
    test_result_2['scan_id'] = "test_dashboard_002"
    scan_id_2 = aggregator.store_scan_result(
        username=username,
        result=test_result_2
    )
    
    print(f"✅ Created test scans: {scan_id_1}, {scan_id_2}")
    return [scan_id_1, scan_id_2]

def test_dashboard_data_retrieval():
    """Test dashboard data retrieval and processing"""
    print("\n🔍 Testing dashboard data retrieval...")
    
    aggregator = ResultsAggregator()
    username = "vishaal314"
    
    # Get recent scans
    recent_scans = aggregator.get_recent_scans(days=30, username=username)
    print(f"Found {len(recent_scans)} recent scans")
    
    if not recent_scans:
        print("❌ No recent scans found")
        return False
    
    # Test dashboard metrics calculation
    total_scans = len(recent_scans)
    total_pii = 0
    high_risk_issues = 0
    compliance_scores = []
    total_cost_savings = 0
    total_penalties_avoided = 0
    
    print("\n📊 Processing scan data:")
    for i, scan in enumerate(recent_scans):
        print(f"  Scan {i+1}:")
        print(f"    Type: {scan.get('scan_type', 'unknown')}")
        print(f"    Timestamp: {scan.get('timestamp', 'unknown')}")
        
        # Handle both database and file storage formats
        if 'result' in scan:
            result = scan['result']
        else:
            result = scan
        
        # Get direct values from scan metadata
        scan_pii = scan.get('total_pii_found', 0)
        scan_high_risk = scan.get('high_risk_count', 0)
        
        if scan_pii > 0:
            total_pii += scan_pii
        if scan_high_risk > 0:
            high_risk_issues += scan_high_risk
        
        print(f"    PII Found: {scan_pii}")
        print(f"    High Risk: {scan_high_risk}")
        
        # Check for cost savings data
        if isinstance(result, dict):
            compliance_score = result.get('compliance_score', 0)
            if compliance_score > 0:
                compliance_scores.append(compliance_score)
                print(f"    Compliance Score: {compliance_score:.1f}%")
            
            cost_data = result.get('cost_savings', {})
            if cost_data:
                immediate_savings = cost_data.get('immediate_savings', 0)
                penalties_avoided = cost_data.get('potential_penalties_avoided', 0)
                total_cost_savings += immediate_savings
                total_penalties_avoided += penalties_avoided
                print(f"    Cost Savings: €{immediate_savings:,.0f}")
                print(f"    Penalties Avoided: €{penalties_avoided:,.0f}")
    
    # Calculate metrics
    avg_compliance = sum(compliance_scores) / len(compliance_scores) if compliance_scores else 0
    
    print(f"\n📈 Dashboard Metrics Summary:")
    print(f"  Total Scans: {total_scans}")
    print(f"  Total PII Found: {total_pii}")
    print(f"  High Risk Issues: {high_risk_issues}")
    print(f"  Average Compliance: {avg_compliance:.1f}%")
    print(f"  Total Cost Savings: €{total_cost_savings:,.0f}")
    print(f"  Total Penalties Avoided: €{total_penalties_avoided:,.0f}")
    
    # Verify expected values (accounting for existing historical scans)
    expected = {
        'min_scans': 2,  # At least our 2 test scans
        'test_pii': 6,   # Our test scans should contribute 5 + 1 = 6 PII
        'test_high_risk': 2,  # Our test scans should contribute 2 + 0 = 2 high risk
        'min_cost_savings': 100000  # Should have significant savings
    }
    
    success = True
    if total_scans < expected['min_scans']:
        print(f"❌ Expected at least {expected['min_scans']} scans, got {total_scans}")
        success = False
    
    # Count scans with cost savings to verify our test data is included
    scans_with_savings = sum(1 for scan in recent_scans 
                            if isinstance(scan.get('result', {}), dict) and 
                               scan['result'].get('cost_savings'))
    
    if scans_with_savings < 2:
        print(f"❌ Expected at least 2 scans with cost savings, got {scans_with_savings}")
        success = False
    
    if total_cost_savings < expected['min_cost_savings']:
        print(f"❌ Expected at least €{expected['min_cost_savings']:,.0f} savings, got €{total_cost_savings:,.0f}")
        success = False
    
    # Check if our test scans are properly included
    test_scan_found = any(scan.get('scan_id', '').startswith('test_dashboard_') for scan in recent_scans)
    if not test_scan_found:
        print("❌ Test scans not found in recent scans")
        success = False
    
    if success:
        print("✅ All dashboard metrics calculated correctly!")
    
    return success

def test_activity_data_formatting():
    """Test activity data formatting for dashboard display"""
    print("\n📋 Testing activity data formatting...")
    
    aggregator = ResultsAggregator()
    username = "vishaal314"
    recent_scans = aggregator.get_recent_scans(days=30, username=username)
    
    if not recent_scans:
        print("❌ No scans to format")
        return False
    
    activity_data = []
    for scan in recent_scans:
        # Handle both database and file storage formats
        if 'result' in scan:
            result = scan['result']
        else:
            result = scan
        
        # Get PII count from metadata first, then from findings if needed
        pii_count = scan.get('total_pii_found', 0)
        if pii_count == 0 and isinstance(result, dict):
            findings = result.get('findings', [])
            pii_count = sum(f.get('pii_count', 0) for f in findings if isinstance(f, dict))
        
        # Format timestamp
        timestamp = scan.get('timestamp', '')
        if timestamp:
            if isinstance(timestamp, str):
                formatted_date = timestamp[:10]
                formatted_time = timestamp[11:16] if len(timestamp) > 11 else ''
            else:
                formatted_date = timestamp.strftime('%Y-%m-%d')
                formatted_time = timestamp.strftime('%H:%M')
        else:
            formatted_date = 'Unknown'
            formatted_time = ''
        
        # Get compliance score and cost savings
        compliance_score = 0
        cost_savings = "N/A"
        if isinstance(result, dict):
            compliance_score = result.get('compliance_score', 0)
            
            # Check for cost savings data
            cost_data = result.get('cost_savings', {})
            if cost_data and isinstance(cost_data, dict):
                immediate_savings = cost_data.get('immediate_savings', 0)
                if immediate_savings > 0:
                    cost_savings = f"€{immediate_savings:,.0f}"
        
        activity_item = {
            'Date': formatted_date,
            'Time': formatted_time,
            'Type': f"{scan.get('scan_type', 'unknown').title()} Scan",
            'Status': '✅ Complete',
            'PII Found': pii_count,
            'Files': scan.get('file_count', 0),
            'Compliance': f"{compliance_score:.1f}%" if compliance_score > 0 else 'N/A',
            'Cost Savings': cost_savings
        }
        
        activity_data.append(activity_item)
        print(f"  📄 {activity_item['Type']}: {activity_item['PII Found']} PII, {activity_item['Cost Savings']} savings")
    
    print(f"✅ Successfully formatted {len(activity_data)} activity items")
    return len(activity_data) > 0

def main():
    """Main test function"""
    print("🧪 Dashboard Fixes Test Suite")
    print("=" * 50)
    
    try:
        # Step 1: Create test data
        test_scan_ids = create_test_scan_data()
        
        # Step 2: Test data retrieval
        retrieval_success = test_dashboard_data_retrieval()
        
        # Step 3: Test activity formatting
        formatting_success = test_activity_data_formatting()
        
        # Summary
        print("\n" + "=" * 50)
        print("🏁 Test Results Summary:")
        print(f"  Data Creation: ✅ Created {len(test_scan_ids)} test scans")
        print(f"  Data Retrieval: {'✅ PASSED' if retrieval_success else '❌ FAILED'}")
        print(f"  Data Formatting: {'✅ PASSED' if formatting_success else '❌ FAILED'}")
        
        if retrieval_success and formatting_success:
            print("\n🎉 All dashboard fixes working correctly!")
            print("   Dashboard should now display current data properly.")
            return True
        else:
            print("\n⚠️  Some tests failed. Check the output above for details.")
            return False
    
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)