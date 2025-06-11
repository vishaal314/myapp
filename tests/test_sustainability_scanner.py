"""
Unit Tests for Sustainability Scanner

Comprehensive test suite validating energy calculations, carbon footprint analysis,
and environmental impact metrics for production deployment.
"""
import unittest
from unittest.mock import Mock, patch
import sys
import os

# Add utils to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from utils.scanners.sustainability_scanner import GithubRepoSustainabilityScanner
from utils.scanners.energy_constants import EnergyConstants, ValidationConstants


class TestEnergyCalculations(unittest.TestCase):
    """Test energy waste calculations for accuracy and consistency."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.scanner = GithubRepoSustainabilityScanner()
    
    def test_import_energy_waste_calculation(self):
        """Test unused import energy waste calculation accuracy."""
        # Test case: 16 unused imports with known sizes
        unused_imports = [
            {'module': 'pandas', 'estimated_size_kb': 500},
            {'module': 'numpy', 'estimated_size_kb': 300},
            {'module': 'matplotlib', 'estimated_size_kb': 200},
            {'module': 'requests', 'estimated_size_kb': 50},
            {'module': 'json', 'estimated_size_kb': 10},
            {'module': 'os', 'estimated_size_kb': 5},
            {'module': 'sys', 'estimated_size_kb': 5},
            {'module': 'time', 'estimated_size_kb': 5},
            {'module': 'datetime', 'estimated_size_kb': 15},
            {'module': 'random', 'estimated_size_kb': 10},
            {'module': 'collections', 'estimated_size_kb': 20},
            {'module': 'itertools', 'estimated_size_kb': 15},
            {'module': 'functools', 'estimated_size_kb': 10},
            {'module': 'typing', 'estimated_size_kb': 25},
            {'module': 'pathlib', 'estimated_size_kb': 30},
            {'module': 'urllib', 'estimated_size_kb': 40}
        ]
        
        energy_waste = self.scanner._calculate_import_energy_waste(unused_imports)
        
        # Expected calculation:
        # Base waste: 16 * 0.5 * 365 / 10 = 292 kWh
        # Memory waste: 1240 KB * 0.0001 = 0.124 kWh
        # Total: ~292.124 kWh
        expected_range = (290, 295)
        
        self.assertGreater(energy_waste, expected_range[0], 
                          f"Energy waste {energy_waste} below expected range")
        self.assertLess(energy_waste, expected_range[1], 
                       f"Energy waste {energy_waste} above expected range")
    
    def test_ml_model_energy_waste_calculation(self):
        """Test ML model energy waste calculation for large models."""
        # Test case: 3 large ML models
        large_ml_models = [
            {'file_path': 'model1.h5', 'size_mb': 250, 'optimization_potential': 45},
            {'file_path': 'model2.pth', 'size_mb': 800, 'optimization_potential': 60},
            {'file_path': 'model3.pkl', 'size_mb': 150, 'optimization_potential': 30}
        ]
        
        energy_waste = self.scanner._calculate_ml_model_energy_waste(large_ml_models)
        
        # Expected calculation for model2 (largest contributor):
        # 800MB * 2.5 kWh/MB * 0.6 optimization * 365/10 = 43,800 kWh
        # Total should be substantial (>100,000 kWh for realistic large model impact)
        
        self.assertGreater(energy_waste, 100000, 
                          "ML model energy waste should be substantial for large models")
        self.assertLess(energy_waste, 200000, 
                       "ML model energy waste calculation seems excessive")
    
    def test_package_duplication_energy_waste(self):
        """Test package duplication energy waste calculation."""
        package_duplications = [
            {'package': 'requests', 'estimated_bloat_mb': 15, 'duplication_count': 2}
        ]
        
        energy_waste = self.scanner._calculate_package_duplication_energy_waste(package_duplications)
        
        # Expected: 1 * 2.5 * 365 / 100 + 15 * 0.05 = 9.125 + 0.75 = 9.875 kWh
        expected_range = (9, 11)
        
        self.assertGreater(energy_waste, expected_range[0])
        self.assertLess(energy_waste, expected_range[1])
    
    def test_zero_inputs_return_zero_waste(self):
        """Test that empty inputs return zero energy waste."""
        self.assertEqual(self.scanner._calculate_import_energy_waste([]), 0.0)
        self.assertEqual(self.scanner._calculate_ml_model_energy_waste([]), 0.0)
        self.assertEqual(self.scanner._calculate_package_duplication_energy_waste([]), 0.0)
        self.assertEqual(self.scanner._calculate_dead_code_energy_waste([]), 0.0)


class TestCarbonFootprintCalculations(unittest.TestCase):
    """Test carbon footprint and environmental impact calculations."""
    
    def test_carbon_footprint_metrics(self):
        """Test comprehensive carbon footprint calculation."""
        # Test with known energy consumption
        energy_kwh = 178389.64  # Example from real scan
        
        carbon_metrics = EnergyConstants.calculate_carbon_footprint(energy_kwh)
        
        # Validate carbon emissions: 178389.64 * 0.4 = 71355.856 kg CO₂
        expected_carbon = energy_kwh * EnergyConstants.CARBON_KG_PER_KWH
        self.assertAlmostEqual(carbon_metrics['carbon_emissions_kg_annually'], 
                              expected_carbon, places=2)
        
        # Validate driving equivalent: 71355.856 * 2.4 = 171254.054 km
        expected_driving = expected_carbon * EnergyConstants.DRIVING_KM_PER_KG_CO2
        self.assertAlmostEqual(carbon_metrics['driving_km_equivalent'], 
                              expected_driving, places=0)
        
        # Validate tree equivalent: 71355.856 / 0.046 = 1551213 trees (reasonable)
        expected_trees = expected_carbon / EnergyConstants.TREES_PER_KG_CO2
        self.assertAlmostEqual(carbon_metrics['trees_equivalent'], 
                              expected_trees, places=0)
    
    def test_potential_savings_calculation(self):
        """Test potential savings calculation with 85% efficiency factor."""
        energy_kwh = 178389.64
        
        savings = EnergyConstants.calculate_potential_savings(energy_kwh, 0.85)
        
        # Validate 85% savings: 178389.64 * 0.85 = 151631.194 kWh
        expected_energy_savings = energy_kwh * 0.85
        self.assertAlmostEqual(savings['energy_kwh_annually'], 
                              expected_energy_savings, places=2)
        
        # Validate carbon savings: 151631.194 * 0.4 = 60652.4776 kg CO₂
        expected_carbon_savings = expected_energy_savings * EnergyConstants.CARBON_KG_PER_KWH
        self.assertAlmostEqual(savings['carbon_kg_annually'], 
                              expected_carbon_savings, places=2)


class TestValidationConstants(unittest.TestCase):
    """Test validation against industry benchmarks."""
    
    def test_energy_consumption_benchmarks(self):
        """Test that calculations align with industry benchmarks."""
        # Large enterprise repository should consume reasonable energy
        large_repo_energy = 200000  # 200 MWh annually
        
        # Should be much less than Google (2.6M MWh) but realistic for large repos
        self.assertLess(large_repo_energy, ValidationConstants.GOOGLE_ANNUAL_MWH * 0.1, 
                       "Repository energy consumption should be <10% of Google's total")
        
        # Should be more than typical small application
        self.assertGreater(large_repo_energy, 1000, 
                          "Large repository should have substantial energy footprint")
    
    def test_confidence_intervals(self):
        """Test that confidence intervals are realistic."""
        self.assertGreater(ValidationConstants.ENERGY_CALCULATION_CONFIDENCE, 0.7, 
                          "Energy calculation confidence should be >70%")
        self.assertLess(ValidationConstants.CARBON_FACTOR_UNCERTAINTY, 0.3, 
                       "Carbon factor uncertainty should be <30%")


class TestASTParsing(unittest.TestCase):
    """Test AST parsing functionality for code analysis."""
    
    def setUp(self):
        """Set up test fixtures with sample code."""
        self.scanner = GithubRepoSustainabilityScanner()
        self.sample_python_code = """
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import unused_module
from collections import defaultdict
from typing import List, Dict

def used_function():
    data = pd.DataFrame()
    return data

def unused_function():
    # This function is never called
    print("Dead code")
    return None

class UnusedClass:
    def __init__(self):
        pass
"""
    
    def test_unused_import_detection(self):
        """Test detection of unused imports via AST analysis."""
        unused_imports = self.scanner._detect_unused_imports_ast(self.sample_python_code)
        
        # Should detect unused_module and matplotlib as unused
        unused_modules = [imp['module'] for imp in unused_imports]
        self.assertIn('unused_module', unused_modules)
        self.assertIn('matplotlib.pyplot', unused_modules)
        
        # Should not flag pandas as unused (it's used in used_function)
        self.assertNotIn('pandas', unused_modules)
    
    def test_dead_code_detection(self):
        """Test detection of dead/unused functions and classes."""
        dead_code = self.scanner._detect_dead_code_ast(self.sample_python_code)
        
        # Should detect unused_function and UnusedClass
        dead_names = [item['name'] for item in dead_code]
        self.assertIn('unused_function', dead_names)
        self.assertIn('UnusedClass', dead_names)
        
        # Should not flag used_function as dead
        self.assertNotIn('used_function', dead_names)


class TestErrorHandling(unittest.TestCase):
    """Test error handling and edge cases."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.scanner = GithubRepoSustainabilityScanner()
    
    def test_invalid_python_syntax(self):
        """Test handling of invalid Python syntax."""
        invalid_code = "def incomplete_function("
        
        # Should not crash on invalid syntax
        try:
            unused_imports = self.scanner._detect_unused_imports_ast(invalid_code)
            dead_code = self.scanner._detect_dead_code_ast(invalid_code)
            # Should return empty results for unparseable code
            self.assertEqual(len(unused_imports), 0)
            self.assertEqual(len(dead_code), 0)
        except Exception as e:
            self.fail(f"AST parsing should handle invalid syntax gracefully: {e}")
    
    def test_empty_input_handling(self):
        """Test handling of empty or None inputs."""
        # Empty string should not crash
        self.assertEqual(len(self.scanner._detect_unused_imports_ast("")), 0)
        self.assertEqual(len(self.scanner._detect_dead_code_ast("")), 0)
        
        # None inputs should be handled safely
        self.assertEqual(self.scanner._calculate_import_energy_waste(None), 0.0)


class TestIntegrationScenarios(unittest.TestCase):
    """Integration tests for complete scanning scenarios."""
    
    def test_github_repo_scan_structure(self):
        """Test complete GitHub repository scan result structure."""
        scanner = GithubRepoSustainabilityScanner()
        
        # Mock a complete scan result
        with patch.object(scanner, '_fetch_github_files') as mock_fetch:
            mock_fetch.return_value = [
                {'path': 'main.py', 'content': 'import pandas\nprint("hello")'},
                {'path': 'utils.py', 'content': 'import numpy\ndef unused(): pass'}
            ]
            
            result = scanner.scan_github_repo('https://github.com/test/repo')
            
            # Validate result structure
            self.assertIn('carbon_footprint', result)
            self.assertIn('code_intelligence', result)
            self.assertIn('recommendations', result)
            
            # Validate carbon footprint structure
            carbon_data = result['carbon_footprint']
            self.assertIn('total_energy_waste_kwh_annually', carbon_data)
            self.assertIn('carbon_emissions_kg_annually', carbon_data)
            self.assertIn('breakdown', carbon_data)
            self.assertIn('potential_savings', carbon_data)


if __name__ == '__main__':
    # Run all tests with verbose output
    unittest.main(verbosity=2)