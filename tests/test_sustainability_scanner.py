"""
Comprehensive Test Suite for Sustainability Scanner
6 automated tests covering functional and performance validation.
"""

import unittest
import sys
import os
import tempfile
from unittest.mock import Mock, patch
from typing import Dict, Any

# Add parent directory for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.scanners.sustainability_scanner import SustainabilityScanner
from tests.test_framework import ScannerTestSuite, BaseScanner

class TestSustainabilityScanner(ScannerTestSuite):
    """Comprehensive test suite for Sustainability Scanner functionality and performance"""
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.scanner = SustainabilityScanner()
        cls.base_tester = BaseScanner("SustainabilityScanner")
    
    def test_1_functional_cloud_resource_analysis(self):
        """Test 1: Functional - Cloud Resource Waste Detection"""
        # Mock cloud infrastructure data
        mock_cloud_data = {
            'compute_instances': [
                {'id': 'vm-1', 'type': 't3.medium', 'state': 'running', 'cpu_utilization': 5.2, 'region': 'eu-west-1'},
                {'id': 'vm-2', 'type': 't3.large', 'state': 'stopped', 'cpu_utilization': 0.0, 'region': 'eu-west-1'},
                {'id': 'vm-3', 'type': 'm5.xlarge', 'state': 'running', 'cpu_utilization': 85.3, 'region': 'us-east-1'}
            ],
            'storage_volumes': [
                {'id': 'vol-1', 'size_gb': 100, 'attached': True, 'usage_percent': 45},
                {'id': 'vol-2', 'size_gb': 500, 'attached': False, 'usage_percent': 0},
                {'id': 'vol-3', 'size_gb': 200, 'attached': True, 'usage_percent': 95}
            ],
            'containers': [
                {'id': 'container-1', 'image': 'nginx', 'status': 'running', 'cpu_usage': 15.2},
                {'id': 'container-2', 'image': 'postgres', 'status': 'exited', 'cpu_usage': 0.0}
            ]
        }
        
        performance_data = self.base_tester.measure_performance(
            self.scanner.analyze_cloud_resources,
            mock_cloud_data
        )
        result = performance_data['result']
        
        # Validate structure
        self.assert_scan_structure(result)
        
        # Check zombie resource detection
        zombie_resources = [f for f in result['findings'] 
                           if 'zombie' in str(f).lower() or 'idle' in str(f).lower()]
        self.assertGreater(len(zombie_resources), 0, "Should detect zombie/idle resources")
        
        # Check waste cost calculation
        if 'waste_analysis' in result:
            waste_analysis = result['waste_analysis']
            self.assertIn('total_waste_cost', waste_analysis)
            self.assertGreaterEqual(waste_analysis['total_waste_cost'], 0)
        
        # Check regional emissions analysis
        if 'emissions' in result:
            emissions = result['emissions']
            self.assertIn('total_co2_kg_month', emissions)
            self.assertGreaterEqual(emissions['total_co2_kg_month'], 0)
        
        # Validate performance
        self.assert_performance_within_limits(performance_data)
        
        print(f"✓ Test 1 PASSED: Cloud resource analysis with {len(zombie_resources)} waste findings in {performance_data['execution_time']:.2f}s")
    
    def test_2_functional_code_efficiency_analysis(self):
        """Test 2: Functional - Code Efficiency and Dead Code Detection"""
        # Create test codebase with efficiency issues
        inefficient_code = '''
# Inefficient algorithms and dead code
import unused_library
import pandas as pd
import numpy as np

def inefficient_sort(data):
    # O(n²) bubble sort instead of efficient sorting
    n = len(data)
    for i in range(n):
        for j in range(0, n-i-1):
            if data[j] > data[j+1]:
                data[j], data[j+1] = data[j+1], data[j]
    return data

def unused_function():
    """This function is never called - dead code"""
    return "unused"

def inefficient_search(items, target):
    # Linear search instead of binary search
    for i, item in enumerate(items):
        if item == target:
            return i
    return -1

# Inefficient pandas operations
def slow_dataframe_operations(df):
    # Inefficient iteration
    results = []
    for index, row in df.iterrows():
        results.append(row['value'] * 2)
    return results

# Dead code - unused variables
UNUSED_CONSTANT = 42
unused_variable = "never used"
'''
        
        temp_file = self.create_temp_file(inefficient_code, '.py')
        
        try:
            performance_data = self.base_tester.measure_performance(
                self.scanner.analyze_code_efficiency,
                temp_file
            )
            result = performance_data['result']
            
            # Validate structure
            self.assert_scan_structure(result)
            
            # Check for algorithm efficiency findings
            efficiency_findings = [f for f in result['findings'] 
                                 if any(keyword in str(f).lower() for keyword in 
                                       ['inefficient', 'algorithm', 'complexity', 'performance'])]
            self.assertGreater(len(efficiency_findings), 0, "Should detect inefficient algorithms")
            
            # Check for dead code detection
            dead_code_findings = [f for f in result['findings'] 
                                if any(keyword in str(f).lower() for keyword in 
                                      ['unused', 'dead', 'unreachable'])]
            self.assertGreater(len(dead_code_findings), 0, "Should detect dead code")
            
            # Check sustainability metrics
            if 'code_analysis' in result:
                code_analysis = result['code_analysis']
                self.assertIn('lines_analyzed', code_analysis)
                self.assertIn('dead_code_lines', code_analysis)
            
            # Validate performance
            self.assert_performance_within_limits(performance_data)
            
            print(f"✓ Test 2 PASSED: Code efficiency analysis with {len(efficiency_findings)} findings in {performance_data['execution_time']:.2f}s")
            
        finally:
            self.cleanup_temp_file(temp_file)
    
    def test_3_functional_emissions_calculation(self):
        """Test 3: Functional - Regional CO₂ Emissions Calculation"""
        # Mock infrastructure data with different regions
        infrastructure_data = {
            'compute_usage': {
                'eu-west-1': {'cpu_hours': 1000, 'memory_gb_hours': 2000},  # Netherlands - clean energy
                'us-east-1': {'cpu_hours': 800, 'memory_gb_hours': 1600},    # Virginia - mixed energy
                'ap-southeast-1': {'cpu_hours': 500, 'memory_gb_hours': 1000} # Singapore - mixed energy
            },
            'storage_usage': {
                'eu-west-1': {'storage_gb_hours': 5000},
                'us-east-1': {'storage_gb_hours': 3000},
                'ap-southeast-1': {'storage_gb_hours': 2000}
            },
            'network_usage': {
                'data_transfer_gb': 1000,
                'cdn_requests': 500000
            }
        }
        
        performance_data = self.base_tester.measure_performance(
            self.scanner.calculate_emissions,
            infrastructure_data
        )
        result = performance_data['result']
        
        # Validate structure
        self.assert_scan_structure(result)
        
        # Check emissions calculation
        self.assertIn('emissions', result)
        emissions = result['emissions']
        
        # Should have regional breakdown
        self.assertIn('regional_breakdown', emissions)
        regional_breakdown = emissions['regional_breakdown']
        
        # Check that different regions have different emission factors
        eu_emissions = regional_breakdown.get('eu-west-1', {}).get('co2_kg', 0)
        us_emissions = regional_breakdown.get('us-east-1', {}).get('co2_kg', 0)
        
        # EU should have lower emissions due to cleaner energy grid
        if eu_emissions > 0 and us_emissions > 0:
            emission_factor_eu = eu_emissions / infrastructure_data['compute_usage']['eu-west-1']['cpu_hours']
            emission_factor_us = us_emissions / infrastructure_data['compute_usage']['us-east-1']['cpu_hours']
            self.assertLess(emission_factor_eu, emission_factor_us, 
                           "EU region should have lower emission factor")
        
        # Check total emissions
        self.assertIn('total_co2_kg_month', emissions)
        self.assertGreater(emissions['total_co2_kg_month'], 0)
        
        # Validate performance
        self.assert_performance_within_limits(performance_data)
        
        print(f"✓ Test 3 PASSED: Emissions calculation ({emissions['total_co2_kg_month']:.2f} kg CO₂/month) in {performance_data['execution_time']:.2f}s")
    
    def test_4_performance_large_infrastructure_analysis(self):
        """Test 4: Performance - Large-Scale Infrastructure Analysis"""
        # Generate large infrastructure dataset
        large_infrastructure = {
            'compute_instances': [
                {
                    'id': f'vm-{i}',
                    'type': f't3.{["micro", "small", "medium", "large"][i % 4]}',
                    'state': 'running' if i % 3 != 0 else 'stopped',
                    'cpu_utilization': (i * 7) % 100,
                    'region': ['eu-west-1', 'us-east-1', 'ap-southeast-1'][i % 3]
                } for i in range(200)  # 200 instances
            ],
            'storage_volumes': [
                {
                    'id': f'vol-{i}',
                    'size_gb': 100 + (i * 50) % 1000,
                    'attached': i % 4 != 0,
                    'usage_percent': (i * 13) % 100
                } for i in range(150)  # 150 volumes
            ],
            'containers': [
                {
                    'id': f'container-{i}',
                    'image': ['nginx', 'postgres', 'redis', 'mongodb'][i % 4],
                    'status': 'running' if i % 5 != 0 else 'exited',
                    'cpu_usage': (i * 11) % 100
                } for i in range(300)  # 300 containers
            ]
        }
        
        performance_data = self.base_tester.measure_performance(
            self.scanner.analyze_cloud_resources,
            large_infrastructure
        )
        result = performance_data['result']
        
        # Validate structure
        self.assert_scan_structure(result)
        
        # Performance requirements for large infrastructure
        self.assertLess(performance_data['execution_time'], 45.0,
                       "Large infrastructure analysis should complete within 45 seconds")
        self.assertLess(performance_data['memory_used'], 400.0,
                       "Memory usage should stay under 400MB for large infrastructure")
        
        # Should process all resources
        total_resources = len(large_infrastructure['compute_instances']) + \
                         len(large_infrastructure['storage_volumes']) + \
                         len(large_infrastructure['containers'])
        
        if 'resources_analyzed' in result:
            self.assertGreaterEqual(result['resources_analyzed'], total_resources * 0.9,
                                   "Should analyze at least 90% of resources")
        
        # Should identify waste in large infrastructure
        self.assertGreater(len(result['findings']), 10,
                          "Large infrastructure should have multiple waste findings")
        
        print(f"✓ Test 4 PASSED: Large infrastructure ({total_resources} resources) analyzed in {performance_data['execution_time']:.2f}s")
    
    def test_5_performance_multi_codebase_analysis(self):
        """Test 5: Performance - Multiple Codebase Sustainability Analysis"""
        # Create multiple codebases with different efficiency patterns
        codebases = []
        
        for i in range(5):
            code_content = f'''
# Codebase {i+1}
import numpy as np
import pandas as pd

def process_data_{i}(data):
    # Different efficiency patterns
    ''' + ('# Inefficient nested loops\n' if i % 2 == 0 else '# Optimized operations\n') + f'''
    results = []
    for item in data:
        ''' + ('for j in range(len(data)):\n            results.append(item * j)' if i % 2 == 0 else 'results.append(item * 2)') + f'''
    return results

def unused_function_{i}():
    return "dead code {i}"

# Resource intensive operations
def heavy_computation_{i}(matrix):
    ''' + ('return np.dot(matrix, matrix.T)' if i % 2 == 1 else '''
    # Inefficient matrix multiplication
    result = []
    for i in range(len(matrix)):
        row = []
        for j in range(len(matrix[0])):
            sum_val = 0
            for k in range(len(matrix)):
                sum_val += matrix[i][k] * matrix[k][j]
            row.append(sum_val)
        result.append(row)
    return result''') + '''
'''
            
            temp_file = self.create_temp_file(code_content, f'.py')
            codebases.append(temp_file)
        
        total_analysis_time = 0
        total_findings = 0
        
        try:
            for i, codebase in enumerate(codebases):
                performance_data = self.base_tester.measure_performance(
                    self.scanner.analyze_code_efficiency,
                    codebase
                )
                result = performance_data['result']
                
                # Validate each result
                self.assert_scan_structure(result)
                total_analysis_time += performance_data['execution_time']
                total_findings += len(result['findings'])
            
            # Performance validation for multi-codebase analysis
            avg_time_per_codebase = total_analysis_time / len(codebases)
            self.assertLess(avg_time_per_codebase, 8.0,
                           "Average analysis time per codebase should be under 8 seconds")
            
            # Should find efficiency issues across codebases
            avg_findings_per_codebase = total_findings / len(codebases)
            self.assertGreater(avg_findings_per_codebase, 2.0,
                              "Each codebase should have multiple sustainability findings")
            
            print(f"✓ Test 5 PASSED: {len(codebases)} codebases analyzed in {total_analysis_time:.2f}s (avg: {avg_time_per_codebase:.2f}s)")
            
        finally:
            for codebase in codebases:
                self.cleanup_temp_file(codebase)
    
    def test_6_functional_sustainability_recommendations(self):
        """Test 6: Functional - Sustainability Recommendations and Quick Wins"""
        # Mock comprehensive sustainability data
        sustainability_data = {
            'infrastructure': {
                'zombie_resources': {
                    'idle_vms': [{'id': 'vm-1', 'monthly_cost': 89.50, 'co2_monthly': 12.3}],
                    'orphaned_storage': [{'id': 'vol-1', 'monthly_cost': 45.20, 'co2_monthly': 5.2}],
                    'stopped_containers': [{'id': 'container-1', 'monthly_cost': 15.30, 'co2_monthly': 1.8}]
                },
                'underutilized_resources': {
                    'low_cpu_vms': [{'id': 'vm-2', 'utilization': 8.5, 'savings_potential': 67.80}]
                }
            },
            'code_efficiency': {
                'inefficient_algorithms': [
                    {'function': 'bubble_sort', 'complexity': 'O(n²)', 'improvement_potential': 'O(n log n)'},
                    {'function': 'linear_search', 'complexity': 'O(n)', 'improvement_potential': 'O(log n)'}
                ],
                'dead_code': {
                    'unused_functions': 15,
                    'unused_imports': 8,
                    'lines_saved': 247
                }
            },
            'dependencies': {
                'unused_packages': ['unused-lib-1', 'deprecated-tool', 'heavy-framework'],
                'oversized_dependencies': [
                    {'name': 'bloated-lib', 'size_mb': 156, 'usage_percent': 12}
                ]
            }
        }
        
        performance_data = self.base_tester.measure_performance(
            self.scanner.generate_sustainability_recommendations,
            sustainability_data
        )
        result = performance_data['result']
        
        # Validate structure
        self.assert_scan_structure(result)
        
        # Check for recommendations
        self.assertIn('recommendations', result)
        recommendations = result['recommendations']
        
        # Should have quick wins
        if 'quick_wins' in recommendations:
            quick_wins = recommendations['quick_wins']
            self.assertGreater(len(quick_wins), 0, "Should identify quick wins")
            
            # Quick wins should have impact calculations
            for win in quick_wins:
                self.assertIn('impact', win)
                self.assertIn('effort', win)
        
        # Check for comprehensive analysis
        sustainability_findings = [f for f in result['findings'] 
                                 if any(keyword in str(f).lower() for keyword in 
                                       ['sustainability', 'green', 'efficiency', 'waste', 'emissions'])]
        self.assertGreater(len(sustainability_findings), 0, 
                          "Should generate sustainability-focused findings")
        
        # Check cost and emission savings calculations
        if 'savings_potential' in result:
            savings = result['savings_potential']
            self.assertIn('monthly_cost_savings', savings)
            self.assertIn('monthly_co2_reduction', savings)
            self.assertGreaterEqual(savings['monthly_cost_savings'], 0)
            self.assertGreaterEqual(savings['monthly_co2_reduction'], 0)
        
        # Validate performance
        self.assert_performance_within_limits(performance_data)
        
        print(f"✓ Test 6 PASSED: Sustainability recommendations with {len(sustainability_findings)} findings in {performance_data['execution_time']:.2f}s")

if __name__ == '__main__':
    unittest.main(verbosity=2)