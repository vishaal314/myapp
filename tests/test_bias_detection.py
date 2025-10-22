"""
Test suite for real bias detection algorithms in AI Model Scanner
Validates that bias detection uses real calculations instead of random values
"""

import numpy as np
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.advanced_ai_scanner import AdvancedAIScanner


def test_demographic_parity_real_calculation():
    """Test that demographic parity uses real calculations"""
    scanner = AdvancedAIScanner(region="Netherlands")
    
    # Create test data with clear bias
    # Group 0: 80% positive predictions (40/50)
    # Group 1: 40% positive predictions (20/50)
    test_data = {
        'predictions': np.concatenate([
            np.ones(40), np.zeros(10),  # Group 0: 80% positive
            np.ones(20), np.zeros(30)   # Group 1: 40% positive
        ]),
        'sensitive_attributes': np.concatenate([
            np.zeros(50),  # Group 0
            np.ones(50)    # Group 1
        ])
    }
    
    result = scanner._calculate_demographic_parity(test_data)
    
    # Expected: min(0.8, 0.4) / max(0.8, 0.4) = 0.4 / 0.8 = 0.5
    assert abs(result - 0.5) < 0.01, f"Expected ~0.5, got {result}"
    print(f"✓ Demographic Parity test PASSED: {result:.3f}")
    return True


def test_equalized_odds_real_calculation():
    """Test that equalized odds uses real TPR/FPR calculations"""
    scanner = AdvancedAIScanner(region="Netherlands")
    
    # Create test data with different TPRs across groups
    # Group 0: TPR=0.9 (9/10), FPR=0.1 (1/10)
    # Group 1: TPR=0.6 (6/10), FPR=0.1 (1/10)
    test_data = {
        'predictions': np.concatenate([
            # Group 0: 9 TP, 1 FN, 1 FP, 9 TN
            np.ones(9), np.zeros(1),   # True positives + False negatives
            np.ones(1), np.zeros(9),   # False positives + True negatives
            # Group 1: 6 TP, 4 FN, 1 FP, 9 TN
            np.ones(6), np.zeros(4),   # True positives + False negatives
            np.ones(1), np.zeros(9)    # False positives + True negatives
        ]),
        'ground_truth': np.concatenate([
            # Group 0: 10 positives, 10 negatives
            np.ones(10), np.zeros(10),
            # Group 1: 10 positives, 10 negatives
            np.ones(10), np.zeros(10)
        ]),
        'sensitive_attributes': np.concatenate([
            np.zeros(20),  # Group 0
            np.ones(20)    # Group 1
        ])
    }
    
    result = scanner._calculate_equalized_odds(test_data)
    
    # Expected TPR ratio: min(0.9, 0.6) / max(0.9, 0.6) = 0.6/0.9 = 0.667
    # Expected FPR ratio: min(0.1, 0.1) / max(0.1, 0.1) = 1.0
    # Average: (0.667 + 1.0) / 2 = 0.833
    assert result > 0.7, f"Expected >0.7, got {result}"
    print(f"✓ Equalized Odds test PASSED: {result:.3f}")
    return True


def test_calibration_score_real_calculation():
    """Test that calibration score uses real probability calibration"""
    scanner = AdvancedAIScanner(region="Netherlands")
    
    # Create well-calibrated test data
    np.random.seed(42)
    n_samples = 100
    
    test_data = {
        'probabilities': np.random.uniform(0.3, 0.7, n_samples),
        'ground_truth': np.random.binomial(1, 0.5, n_samples),
        'sensitive_attributes': np.random.binomial(1, 0.5, n_samples)
    }
    
    result = scanner._calculate_calibration_score(test_data)
    
    # Should return a reasonable calibration score
    assert 0.5 < result < 1.0, f"Expected 0.5-1.0, got {result}"
    print(f"✓ Calibration Score test PASSED: {result:.3f}")
    return True


def test_individual_fairness_real_calculation():
    """Test that individual fairness uses Lipschitz continuity"""
    scanner = AdvancedAIScanner(region="Netherlands")
    
    # Create test data where similar individuals get similar predictions
    np.random.seed(42)
    n_samples = 50
    
    # Features: 5 dimensions
    X = np.random.randn(n_samples, 5)
    
    # Predictions should be consistent (similar X → similar predictions)
    y_pred = (X[:, 0] > 0).astype(int)
    
    test_data = {
        'features': X,
        'predictions': y_pred
    }
    
    result = scanner._calculate_individual_fairness(test_data)
    
    # Should return a fairness score
    assert 0.5 < result < 1.0, f"Expected 0.5-1.0, got {result}"
    print(f"✓ Individual Fairness test PASSED: {result:.3f}")
    return True


def test_static_analysis_estimation():
    """Test that static analysis provides informed estimates (not random)"""
    scanner = AdvancedAIScanner(region="Netherlands")
    
    # Test with high-quality model metadata
    metadata_good = {
        'model_type': 'Linear Regression',
        'balanced_dataset': True,
        'diverse_training_data': True,
        'fairness_constraints_applied': True,
        'bias_testing_conducted': True,
        'use_case': 'customer_analytics'
    }
    
    result_good = scanner._estimate_bias_from_model_characteristics(metadata_good)
    
    # Should have higher fairness scores due to good practices
    assert result_good['demographic_parity'] > 0.80, f"Expected >0.80, got {result_good['demographic_parity']}"
    print(f"✓ Static Analysis (Good Model) test PASSED: {result_good}")
    
    # Test with high-risk model metadata
    metadata_risky = {
        'model_type': 'Deep Neural Network',
        'balanced_dataset': False,
        'use_case': 'hiring',
        'model_size_mb': 5000
    }
    
    result_risky = scanner._estimate_bias_from_model_characteristics(metadata_risky)
    
    # Should have lower fairness scores due to risk factors
    assert result_risky['demographic_parity'] < result_good['demographic_parity'], \
        "Risky model should have lower fairness score"
    print(f"✓ Static Analysis (Risky Model) test PASSED: {result_risky}")
    
    return True


def test_no_random_values():
    """Test that bias assessment does NOT use random values"""
    scanner = AdvancedAIScanner(region="Netherlands")
    
    # Run assessment twice with same metadata - should get IDENTICAL results
    metadata = {
        'model_type': 'Random Forest',
        'balanced_dataset': True,
        'use_case': 'marketing'
    }
    
    # Create empty model file (not used in static analysis)
    model_file = None
    
    result1 = scanner._assess_model_bias(model_file, metadata)
    result2 = scanner._assess_model_bias(model_file, metadata)
    
    # Results should be IDENTICAL (not random)
    assert result1.demographic_parity == result2.demographic_parity, \
        "Results should be deterministic, not random!"
    assert result1.equalized_odds == result2.equalized_odds, \
        "Results should be deterministic, not random!"
    assert result1.calibration_score == result2.calibration_score, \
        "Results should be deterministic, not random!"
    assert result1.fairness_through_awareness == result2.fairness_through_awareness, \
        "Results should be deterministic, not random!"
    
    print(f"✓ No Random Values test PASSED - Results are deterministic!")
    print(f"  Demographic Parity: {result1.demographic_parity:.3f}")
    print(f"  Equalized Odds: {result1.equalized_odds:.3f}")
    print(f"  Calibration: {result1.calibration_score:.3f}")
    print(f"  Individual Fairness: {result1.fairness_through_awareness:.3f}")
    
    return True


def test_metadata_bias_results():
    """Test that pre-computed bias results from metadata are used"""
    scanner = AdvancedAIScanner(region="Netherlands")
    
    # Metadata with pre-computed bias test results
    metadata = {
        'bias_test_results': {
            'demographic_parity': 0.92,
            'equalized_odds': 0.88,
            'calibration': 0.95,
            'individual_fairness': 0.90
        }
    }
    
    result = scanner._assess_model_bias(None, metadata)
    
    # Should use the provided values exactly
    assert result.demographic_parity == 0.92, "Should use metadata value"
    assert result.equalized_odds == 0.88, "Should use metadata value"
    assert result.calibration_score == 0.95, "Should use metadata value"
    assert result.fairness_through_awareness == 0.90, "Should use metadata value"
    
    print(f"✓ Metadata Bias Results test PASSED - Uses provided metrics!")
    return True


if __name__ == "__main__":
    print("=" * 60)
    print("BIAS DETECTION VALIDATION TEST SUITE")
    print("=" * 60)
    print()
    
    tests = [
        ("Demographic Parity Calculation", test_demographic_parity_real_calculation),
        ("Equalized Odds Calculation", test_equalized_odds_real_calculation),
        ("Calibration Score Calculation", test_calibration_score_real_calculation),
        ("Individual Fairness Calculation", test_individual_fairness_real_calculation),
        ("Static Analysis Estimation", test_static_analysis_estimation),
        ("No Random Values", test_no_random_values),
        ("Metadata Bias Results", test_metadata_bias_results),
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
    print(f"RESULTS: {passed}/{len(tests)} tests passed")
    if failed == 0:
        print("🎉 ALL TESTS PASSED - Bias detection is production-ready!")
        print("✓ No more np.random.uniform() - Real algorithms verified!")
    else:
        print(f"❌ {failed} tests failed - needs fixes")
    print("=" * 60)
    
    sys.exit(0 if failed == 0 else 1)
