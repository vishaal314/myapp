"""
Edge case test suite for bias detection algorithms
Tests scenarios that previously caused crashes or NaN propagation
"""

import numpy as np
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.advanced_ai_scanner import AdvancedAIScanner


def test_single_group_demographic_parity():
    """Test demographic parity with only one protected group"""
    scanner = AdvancedAIScanner(region="Netherlands")
    
    test_data = {
        'predictions': np.ones(50),  # All positive predictions
        'sensitive_attributes': np.zeros(50)  # Only one group
    }
    
    result = scanner._calculate_demographic_parity(test_data)
    
    # Should return default score, not crash
    assert 0.5 <= result <= 1.0, f"Expected default score, got {result}"
    print(f"✓ Single group demographic parity: {result:.3f}")
    return True


def test_all_negative_predictions():
    """Test when all predictions are negative (rate = 0 for all groups)"""
    scanner = AdvancedAIScanner(region="Netherlands")
    
    test_data = {
        'predictions': np.zeros(100),  # All negative
        'sensitive_attributes': np.concatenate([np.zeros(50), np.ones(50)])
    }
    
    result = scanner._calculate_demographic_parity(test_data)
    
    # Should return 1.0 (perfect parity - both groups at 0%)
    assert result == 1.0, f"Expected 1.0 for perfect parity, got {result}"
    print(f"✓ All negative predictions: {result:.3f} (perfect parity)")
    return True


def test_all_positive_predictions():
    """Test when all predictions are positive (rate = 1.0 for all groups)"""
    scanner = AdvancedAIScanner(region="Netherlands")
    
    test_data = {
        'predictions': np.ones(100),  # All positive
        'sensitive_attributes': np.concatenate([np.zeros(50), np.ones(50)])
    }
    
    result = scanner._calculate_demographic_parity(test_data)
    
    # Should return 1.0 (perfect parity - both groups at 100%)
    assert result == 1.0, f"Expected 1.0 for perfect parity, got {result}"
    print(f"✓ All positive predictions: {result:.3f} (perfect parity)")
    return True


def test_extreme_class_imbalance_equalized_odds():
    """Test equalized odds when groups have extreme class imbalance"""
    scanner = AdvancedAIScanner(region="Netherlands")
    
    # Group 0: All positives (no negatives)
    # Group 1: Mixed
    test_data = {
        'predictions': np.concatenate([
            np.ones(20),   # Group 0 predictions
            np.ones(10), np.zeros(10)  # Group 1 predictions
        ]),
        'ground_truth': np.concatenate([
            np.ones(20),   # Group 0: all positive labels
            np.ones(10), np.zeros(10)  # Group 1: mixed labels
        ]),
        'sensitive_attributes': np.concatenate([
            np.zeros(20),  # Group 0
            np.ones(20)    # Group 1
        ])
    }
    
    result = scanner._calculate_equalized_odds(test_data)
    
    # Should return score (not crash), group with no negatives is skipped
    assert 0.5 <= result <= 1.0, f"Expected valid score, got {result}"
    print(f"✓ Extreme class imbalance: {result:.3f}")
    return True


def test_all_zero_tpr():
    """Test when all groups have TPR=0 (model predicts all negative)"""
    scanner = AdvancedAIScanner(region="Netherlands")
    
    test_data = {
        'predictions': np.zeros(40),  # All negative predictions
        'ground_truth': np.concatenate([
            np.ones(10), np.zeros(10),  # Group 0: mixed labels
            np.ones(10), np.zeros(10)   # Group 1: mixed labels
        ]),
        'sensitive_attributes': np.concatenate([
            np.zeros(20),  # Group 0
            np.ones(20)    # Group 1
        ])
    }
    
    result = scanner._calculate_equalized_odds(test_data)
    
    # Should handle all-zero TPR gracefully
    assert 0.5 <= result <= 1.0, f"Expected valid score, got {result}"
    print(f"✓ All zero TPR: {result:.3f}")
    return True


def test_sparse_calibration_bins():
    """Test calibration with very sparse data (few samples per bin)"""
    scanner = AdvancedAIScanner(region="Netherlands")
    
    np.random.seed(42)
    
    # Very small dataset - will result in sparse bins
    test_data = {
        'probabilities': np.array([0.1, 0.2, 0.9, 0.8, 0.5]),  # 5 samples only
        'ground_truth': np.array([0, 0, 1, 1, 1]),
        'sensitive_attributes': np.array([0, 0, 1, 1, 1])
    }
    
    result = scanner._calculate_calibration_score(test_data)
    
    # Should return conservative score, not crash or return NaN
    assert not np.isnan(result), "Result should not be NaN"
    assert 0.5 <= result <= 1.0, f"Expected valid score, got {result}"
    print(f"✓ Sparse calibration bins: {result:.3f}")
    return True


def test_calibration_with_nan_values():
    """Test calibration handles NaN gracefully"""
    scanner = AdvancedAIScanner(region="Netherlands")
    
    np.random.seed(42)
    
    # Dataset with NaN values (invalid)
    test_data = {
        'probabilities': np.array([0.5, np.nan, 0.7, 0.3, 0.6]),
        'ground_truth': np.array([1, 0, 1, 0, 1]),
        'sensitive_attributes': np.array([0, 0, 1, 1, 1])
    }
    
    result = scanner._calculate_calibration_score(test_data)
    
    # Should handle NaN without crashing
    assert not np.isnan(result), "Result should not be NaN"
    assert 0.5 <= result <= 1.0, f"Expected valid score, got {result}"
    print(f"✓ Calibration with NaN values: {result:.3f}")
    return True


def test_missing_schema_fields():
    """Test that missing fields trigger fallback to static analysis"""
    scanner = AdvancedAIScanner(region="Netherlands")
    
    # Missing 'ground_truth' - should fallback for equalized odds
    test_data = {
        'predictions': np.ones(50),
        'sensitive_attributes': np.zeros(50)
        # Missing: ground_truth, probabilities, features
    }
    
    metadata = {
        'bias_test_data': test_data,
        'model_type': 'Random Forest'
    }
    
    result = scanner._assess_model_bias(None, metadata)
    
    # Should complete without crashing
    assert result.overall_bias_score > 0, "Should return valid bias score"
    assert 0 <= result.demographic_parity <= 1, "Demographic parity should be valid"
    print(f"✓ Missing schema fields handled gracefully")
    print(f"  Overall bias score: {result.overall_bias_score:.3f}")
    return True


def test_empty_dataset():
    """Test with empty arrays"""
    scanner = AdvancedAIScanner(region="Netherlands")
    
    test_data = {
        'predictions': np.array([]),
        'sensitive_attributes': np.array([])
    }
    
    result = scanner._calculate_demographic_parity(test_data)
    
    # Should return default, not crash
    assert 0.5 <= result <= 1.0, f"Expected default score for empty data, got {result}"
    print(f"✓ Empty dataset: {result:.3f}")
    return True


def test_mismatched_array_lengths():
    """Test when arrays have mismatched lengths"""
    scanner = AdvancedAIScanner(region="Netherlands")
    
    test_data = {
        'probabilities': np.random.rand(50),
        'ground_truth': np.random.binomial(1, 0.5, 40),  # Different length!
        'sensitive_attributes': np.random.binomial(1, 0.5, 50)
    }
    
    result = scanner._calculate_calibration_score(test_data)
    
    # Should handle gracefully and return conservative default
    assert not np.isnan(result), "Result should not be NaN"
    assert 0.5 <= result <= 1.0, f"Expected valid score, got {result}"
    print(f"✓ Mismatched array lengths: {result:.3f}")
    return True


def test_single_sample_per_group():
    """Test with only 1 sample per group (extreme sparsity)"""
    scanner = AdvancedAIScanner(region="Netherlands")
    
    test_data = {
        'predictions': np.array([1, 0]),
        'sensitive_attributes': np.array([0, 1]),
        'ground_truth': np.array([1, 0])
    }
    
    result = scanner._calculate_equalized_odds(test_data)
    
    # Should handle extreme sparsity
    assert not np.isnan(result), "Result should not be NaN"
    assert 0.5 <= result <= 1.0, f"Expected valid score, got {result}"
    print(f"✓ Single sample per group: {result:.3f}")
    return True


def test_schema_validation():
    """Test the schema validation function"""
    scanner = AdvancedAIScanner(region="Netherlands")
    
    # Test complete data
    complete_data = {
        'predictions': np.ones(10),
        'ground_truth': np.ones(10),
        'probabilities': np.ones(10),
        'features': np.ones((10, 5)),
        'sensitive_attributes': np.ones(10)
    }
    
    validation = scanner._validate_bias_test_data(complete_data)
    
    assert validation['demographic_parity'] == True
    assert validation['equalized_odds'] == True
    assert validation['calibration'] == True
    assert validation['individual_fairness'] == True
    print(f"✓ Schema validation (complete): All True")
    
    # Test minimal data
    minimal_data = {
        'predictions': np.ones(10),
        'sensitive_attributes': np.ones(10)
    }
    
    validation = scanner._validate_bias_test_data(minimal_data)
    
    assert validation['demographic_parity'] == True
    assert validation['equalized_odds'] == False
    assert validation['calibration'] == True  # Falls back to demographic parity
    assert validation['individual_fairness'] == True  # Falls back to demographic parity
    print(f"✓ Schema validation (minimal): Correct fallbacks")
    
    return True


if __name__ == "__main__":
    print("=" * 60)
    print("BIAS DETECTION EDGE CASE TEST SUITE")
    print("=" * 60)
    print()
    
    tests = [
        ("Single Group Demographic Parity", test_single_group_demographic_parity),
        ("All Negative Predictions", test_all_negative_predictions),
        ("All Positive Predictions", test_all_positive_predictions),
        ("Extreme Class Imbalance", test_extreme_class_imbalance_equalized_odds),
        ("All Zero TPR", test_all_zero_tpr),
        ("Sparse Calibration Bins", test_sparse_calibration_bins),
        ("Calibration with NaN Values", test_calibration_with_nan_values),
        ("Missing Schema Fields", test_missing_schema_fields),
        ("Empty Dataset", test_empty_dataset),
        ("Mismatched Array Lengths", test_mismatched_array_lengths),
        ("Single Sample Per Group", test_single_sample_per_group),
        ("Schema Validation", test_schema_validation),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            print(f"\n{test_name}:")
            print("-" * 60)
            if test_func():
                passed += 1
        except Exception as e:
            print(f"✗ {test_name} FAILED: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"RESULTS: {passed}/{len(tests)} edge case tests passed")
    if failed == 0:
        print("🎉 ALL EDGE CASE TESTS PASSED!")
        print("✓ Production-ready: Handles divide-by-zero, NaN, sparse data, missing fields")
    else:
        print(f"❌ {failed} tests failed - needs fixes")
    print("=" * 60)
    
    sys.exit(0 if failed == 0 else 1)
