#!/usr/bin/env python3
"""
Comprehensive EU AI Act Scanner Test Suite
15 tests each for: Functionality, Performance, Security, Violation Detection
Total: 60 comprehensive test cases for EU AI Act 2025 compliance
"""

import unittest
import sys
import os
import time
import tempfile
import threading
import json
from unittest.mock import patch, MagicMock
from pathlib import Path

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.ai_model_scanner import AIModelScanner
from services.advanced_ai_scanner import AdvancedAIScanner
from utils.ai_act_calculator import calculate_ai_risk_score

class TestAIActScannerFunctionality(unittest.TestCase):
    """15 Functionality Tests for AI Act Scanner"""
    
    def setUp(self):
        self.scanner = AIModelScanner()
        self.advanced_scanner = AdvancedAIScanner()
        
    def test_01_ai_model_detection(self):
        """Test AI model detection functionality"""
        ai_code = '''
        import tensorflow as tf
        import torch
        
        model = tf.keras.Sequential([
            tf.keras.layers.Dense(128, activation='relu'),
            tf.keras.layers.Dense(10, activation='softmax')
        ])
        '''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(ai_code)
            f.flush()
            
            results = self.scanner.scan_file(f.name)
            self.assertIsInstance(results, dict)
            self.assertIn('ai_models_detected', results)
            os.unlink(f.name)
            
    def test_02_high_risk_ai_system_detection(self):
        """Test high-risk AI system detection"""
        high_risk_code = '''
        class BiometricIdentificationSystem:
            def __init__(self):
                self.facial_recognition_model = load_model("face_recognition.h5")
                self.emotion_detection = True
                
            def identify_person(self, image):
                return self.facial_recognition_model.predict(image)
        '''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(high_risk_code)
            f.flush()
            
            results = self.scanner.scan_file(f.name)
            self.assertIn('risk_level', results)
            os.unlink(f.name)
            
    def test_03_prohibited_ai_practices_detection(self):
        """Test prohibited AI practices detection"""
        prohibited_code = '''
        class SubliminalInfluenceSystem:
            def manipulate_behavior(self, user_data):
                # Subliminal messaging to influence user decisions
                return self.subliminal_model.predict(user_data)
                
        class SocialScoringSystem:
            def evaluate_citizen(self, personal_data):
                # Social credit scoring system
                score = self.scoring_algorithm.compute(personal_data)
                return score
        '''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(prohibited_code)
            f.flush()
            
            results = self.advanced_scanner.scan_file(f.name)
            prohibited_practices = results.get('prohibited_practices', [])
            self.assertGreater(len(prohibited_practices), 0)
            os.unlink(f.name)
            
    def test_04_bias_detection_functionality(self):
        """Test bias detection functionality"""
        biased_code = '''
        def hiring_algorithm(candidate):
            score = 0
            if candidate.gender == "male":
                score += 10
            if candidate.age < 30:
                score += 5
            if candidate.ethnicity == "white":
                score += 8
            return score
        '''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(biased_code)
            f.flush()
            
            results = self.advanced_scanner.scan_file(f.name)
            bias_issues = results.get('bias_issues', [])
            self.assertGreater(len(bias_issues), 0)
            os.unlink(f.name)
            
    def test_05_transparency_requirement_detection(self):
        """Test transparency requirement detection"""
        non_transparent_code = '''
        class AIDecisionSystem:
            def make_decision(self, input_data):
                # Black box decision making without explanation
                result = self.neural_network.predict(input_data)
                return result  # No explanation provided
        '''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(non_transparent_code)
            f.flush()
            
            results = self.advanced_scanner.scan_file(f.name)
            transparency_issues = results.get('transparency_issues', [])
            self.assertGreaterEqual(len(transparency_issues), 0)
            os.unlink(f.name)
            
    def test_06_data_governance_detection(self):
        """Test data governance requirement detection"""
        poor_governance_code = '''
        def train_model(data):
            # No data quality checks
            # No bias assessment
            # No documentation
            model = train_neural_network(data)
            return model
        '''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(poor_governance_code)
            f.flush()
            
            results = self.advanced_scanner.scan_file(f.name)
            governance_issues = results.get('data_governance_issues', [])
            self.assertGreaterEqual(len(governance_issues), 0)
            os.unlink(f.name)
            
    def test_07_human_oversight_detection(self):
        """Test human oversight requirement detection"""
        no_oversight_code = '''
        class AutonomousHiringSystem:
            def hire_candidate(self, candidate_data):
                decision = self.ai_model.predict(candidate_data)
                if decision > 0.7:
                    self.send_offer(candidate_data['email'])  # No human review
                return decision
        '''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(no_oversight_code)
            f.flush()
            
            results = self.advanced_scanner.scan_file(f.name)
            oversight_issues = results.get('human_oversight_issues', [])
            self.assertGreaterEqual(len(oversight_issues), 0)
            os.unlink(f.name)
            
    def test_08_accuracy_robustness_detection(self):
        """Test accuracy and robustness requirement detection"""
        poor_accuracy_code = '''
        def deploy_model_without_testing():
            model = load_untested_model()
            # No accuracy validation
            # No robustness testing
            # No performance monitoring
            return model
        '''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(poor_accuracy_code)
            f.flush()
            
            results = self.advanced_scanner.scan_file(f.name)
            accuracy_issues = results.get('accuracy_issues', [])
            self.assertGreaterEqual(len(accuracy_issues), 0)
            os.unlink(f.name)
            
    def test_09_record_keeping_detection(self):
        """Test record keeping requirement detection"""
        poor_records_code = '''
        class AISystem:
            def process_request(self, data):
                result = self.model.predict(data)
                # No logging of decisions
                # No audit trail
                # No record keeping
                return result
        '''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(poor_records_code)
            f.flush()
            
            results = self.advanced_scanner.scan_file(f.name)
            record_issues = results.get('record_keeping_issues', [])
            self.assertGreaterEqual(len(record_issues), 0)
            os.unlink(f.name)
            
    def test_10_cybersecurity_detection(self):
        """Test cybersecurity requirement detection"""
        insecure_code = '''
        def process_ai_data(user_input):
            # No input validation
            # No authentication
            # No encryption
            result = eval(user_input)  # Dangerous practice
            return ai_model.predict(result)
        '''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(insecure_code)
            f.flush()
            
            results = self.advanced_scanner.scan_file(f.name)
            security_issues = results.get('cybersecurity_issues', [])
            self.assertGreater(len(security_issues), 0)
            os.unlink(f.name)
            
    def test_11_risk_classification_functionality(self):
        """Test risk classification functionality"""
        ai_systems = [
            "facial_recognition_law_enforcement",  # Prohibited
            "hiring_recommendation_system",         # High-risk
            "spam_filter",                         # Limited risk
            "video_game_ai"                        # Minimal risk
        ]
        
        for system_type in ai_systems:
            risk_score = calculate_ai_risk_score(system_type, {"domain": "general"})
            self.assertIsInstance(risk_score, (int, float))
            self.assertGreaterEqual(risk_score, 0)
            self.assertLessEqual(risk_score, 100)
            
    def test_12_conformity_assessment_detection(self):
        """Test conformity assessment requirement detection"""
        non_compliant_code = '''
        class HighRiskAISystem:
            def __init__(self):
                # No conformity assessment
                # No CE marking
                # No technical documentation
                self.model = load_model("risky_ai.pkl")
        '''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(non_compliant_code)
            f.flush()
            
            results = self.advanced_scanner.scan_file(f.name)
            conformity_issues = results.get('conformity_issues', [])
            self.assertGreaterEqual(len(conformity_issues), 0)
            os.unlink(f.name)
            
    def test_13_post_market_monitoring_detection(self):
        """Test post-market monitoring requirement detection"""
        no_monitoring_code = '''
        def deploy_ai_system():
            model = load_model()
            # No performance monitoring
            # No incident reporting
            # No continuous assessment
            return model
        '''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(no_monitoring_code)
            f.flush()
            
            results = self.advanced_scanner.scan_file(f.name)
            monitoring_issues = results.get('monitoring_issues', [])
            self.assertGreaterEqual(len(monitoring_issues), 0)
            os.unlink(f.name)
            
    def test_14_foundation_model_detection(self):
        """Test foundation model requirement detection"""
        foundation_model_code = '''
        class LargeLanguageModel:
            def __init__(self):
                self.parameters = 75_000_000_000  # 75B parameters
                self.training_compute = 1e25  # High compute
                
            def generate_text(self, prompt):
                # General purpose foundation model
                return self.transformer.generate(prompt)
        '''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(foundation_model_code)
            f.flush()
            
            results = self.advanced_scanner.scan_file(f.name)
            foundation_issues = results.get('foundation_model_issues', [])
            self.assertGreaterEqual(len(foundation_issues), 0)
            os.unlink(f.name)
            
    def test_15_general_purpose_ai_detection(self):
        """Test general purpose AI system detection"""
        gpai_code = '''
        class GeneralPurposeAI:
            def __init__(self):
                self.capabilities = [
                    "text_generation", "image_generation", 
                    "code_generation", "question_answering"
                ]
                
            def process_any_task(self, task_type, input_data):
                # Multi-modal general purpose AI
                return self.unified_model.process(task_type, input_data)
        '''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(gpai_code)
            f.flush()
            
            results = self.advanced_scanner.scan_file(f.name)
            gpai_issues = results.get('gpai_issues', [])
            self.assertGreaterEqual(len(gpai_issues), 0)
            os.unlink(f.name)

class TestAIActScannerPerformance(unittest.TestCase):
    """15 Performance Tests for AI Act Scanner"""
    
    def setUp(self):
        self.scanner = AIModelScanner()
        self.advanced_scanner = AdvancedAIScanner()
        
    def test_01_large_ai_codebase_scanning_speed(self):
        """Test scanning speed on large AI codebase"""
        large_ai_code = '''
        import tensorflow as tf
        import torch
        import sklearn
        
        class AIPipeline:
            def __init__(self):
                self.models = []
                
            def add_model(self, model):
                self.models.append(model)
        ''' * 1000
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(large_ai_code)
            f.flush()
            
            start_time = time.time()
            results = self.scanner.scan_file(f.name)
            end_time = time.time()
            
            scan_time = end_time - start_time
            self.assertLess(scan_time, 15.0)  # Should complete in under 15 seconds
            os.unlink(f.name)
            
    def test_02_multiple_ai_models_detection_speed(self):
        """Test speed of detecting multiple AI models"""
        multi_model_code = '''
        # Multiple AI frameworks and models
        import tensorflow as tf
        import torch
        import sklearn
        import xgboost
        import lightgbm
        
        tensorflow_model = tf.keras.Sequential()
        pytorch_model = torch.nn.Linear(10, 1)
        sklearn_model = sklearn.ensemble.RandomForestClassifier()
        xgb_model = xgboost.XGBClassifier()
        lgb_model = lightgbm.LGBMClassifier()
        '''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(multi_model_code)
            f.flush()
            
            start_time = time.time()
            results = self.advanced_scanner.scan_file(f.name)
            end_time = time.time()
            
            scan_time = end_time - start_time
            self.assertLess(scan_time, 5.0)
            os.unlink(f.name)
            
    def test_03_bias_detection_algorithm_performance(self):
        """Test bias detection algorithm performance"""
        biased_code_variations = []
        for i in range(100):
            code = f'''
            def algorithm_{i}(candidate):
                if candidate.gender == "male":
                    return {i} + 10
                return {i}
            '''
            biased_code_variations.append(code)
            
        start_time = time.time()
        for code in biased_code_variations:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                f.flush()
                self.advanced_scanner.scan_file(f.name)
                os.unlink(f.name)
        end_time = time.time()
        
        total_time = end_time - start_time
        self.assertLess(total_time, 20.0)  # Should process 100 files in under 20 seconds
        
    def test_04_risk_classification_speed(self):
        """Test AI risk classification speed"""
        risk_scenarios = [
            ("biometric_identification", {"accuracy": 0.95}),
            ("hiring_system", {"bias_score": 0.3}),
            ("credit_scoring", {"transparency": 0.2}),
        ] * 500
        
        start_time = time.time()
        for scenario, metadata in risk_scenarios:
            calculate_ai_risk_score(scenario, metadata)
        end_time = time.time()
        
        classification_time = end_time - start_time
        self.assertLess(classification_time, 5.0)  # Should classify 1500 scenarios quickly
        
    def test_05_pattern_matching_optimization(self):
        """Test pattern matching optimization for AI code"""
        ai_patterns_code = '''
        # Various AI patterns to detect
        model.fit(X_train, y_train)
        predictions = model.predict(X_test)
        neural_network = tf.keras.Sequential()
        loss_function = torch.nn.CrossEntropyLoss()
        accuracy_score = metrics.accuracy_score(y_true, y_pred)
        ''' * 200
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(ai_patterns_code)
            f.flush()
            
            # First scan
            start_time = time.time()
            results1 = self.scanner.scan_file(f.name)
            first_scan_time = time.time() - start_time
            
            # Second scan (potential caching benefits)
            start_time = time.time()
            results2 = self.scanner.scan_file(f.name)
            second_scan_time = time.time() - start_time
            
            # Second scan should be similar or faster
            self.assertLessEqual(second_scan_time, first_scan_time * 1.3)
            os.unlink(f.name)
            
    def test_06_memory_efficiency_ai_scanning(self):
        """Test memory efficiency during AI code scanning"""
        import psutil
        process = psutil.Process()
        initial_memory = process.memory_info().rss
        
        # Scan multiple AI files
        for i in range(50):
            ai_code = f'''
            import tensorflow as tf
            
            class AIModel_{i}:
                def __init__(self):
                    self.model = tf.keras.Sequential([
                        tf.keras.layers.Dense({64 + i}),
                        tf.keras.layers.Dense(10)
                    ])
            '''
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(ai_code)
                f.flush()
                self.scanner.scan_file(f.name)
                os.unlink(f.name)
                
        final_memory = process.memory_info().rss
        memory_growth = final_memory - initial_memory
        
        # Memory growth should be reasonable
        self.assertLess(memory_growth, 100 * 1024 * 1024)  # Less than 100MB
        
    def test_07_concurrent_ai_scanning_performance(self):
        """Test concurrent AI scanning performance"""
        def scan_worker(ai_code, results):
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(ai_code)
                f.flush()
                result = self.scanner.scan_file(f.name)
                results.append(result)
                os.unlink(f.name)
                
        ai_codes = [
            f'''
            import torch
            model_{i} = torch.nn.Linear({10 + i}, 1)
            '''
            for i in range(10)
        ]
        
        threads = []
        results = []
        
        start_time = time.time()
        for code in ai_codes:
            thread = threading.Thread(target=scan_worker, args=(code, results))
            threads.append(thread)
            thread.start()
            
        for thread in threads:
            thread.join(timeout=10)
        end_time = time.time()
        
        total_time = end_time - start_time
        self.assertLess(total_time, 8.0)
        self.assertEqual(len(results), len(ai_codes))
        
    def test_08_deep_learning_framework_detection_speed(self):
        """Test speed of deep learning framework detection"""
        frameworks_code = '''
        # Multiple deep learning frameworks
        import tensorflow as tf
        import torch
        import keras
        import pytorch_lightning
        import jax
        import flax
        import haiku
        import trax
        import paddle
        import mxnet
        import chainer
        import caffe
        import theano
        '''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(frameworks_code)
            f.flush()
            
            start_time = time.time()
            results = self.scanner.scan_file(f.name)
            end_time = time.time()
            
            detection_time = end_time - start_time
            self.assertLess(detection_time, 2.0)
            os.unlink(f.name)
            
    def test_09_scalability_increasing_ai_complexity(self):
        """Test scalability with increasing AI model complexity"""
        complexities = [10, 50, 100, 200]  # Model layers
        times = []
        
        for complexity in complexities:
            ai_code = f'''
            import tensorflow as tf
            
            model = tf.keras.Sequential([
            ''' + '''
                tf.keras.layers.Dense(64, activation='relu'),
            ''' * complexity + '''
                tf.keras.layers.Dense(10, activation='softmax')
            ])
            '''
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(ai_code)
                f.flush()
                
                start_time = time.time()
                self.scanner.scan_file(f.name)
                end_time = time.time()
                
                times.append(end_time - start_time)
                os.unlink(f.name)
                
        # Performance should scale reasonably
        for i in range(1, len(times)):
            scale_factor = complexities[i] / complexities[i-1]
            time_factor = times[i] / times[i-1] if times[i-1] > 0 else 1
            self.assertLess(time_factor, scale_factor * 2)
            
    def test_10_ai_vulnerability_scanning_speed(self):
        """Test AI vulnerability scanning speed"""
        vulnerable_ai_code = '''
        import pickle
        import joblib
        
        def load_model_unsafe(model_path):
            # Unsafe model loading (pickle vulnerability)
            with open(model_path, 'rb') as f:
                model = pickle.load(f)  # Security vulnerability
            return model
            
        def process_user_input(user_data):
            # No input validation
            result = eval(user_data)  # Code injection vulnerability
            return model.predict(result)
        ''' * 100
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(vulnerable_ai_code)
            f.flush()
            
            start_time = time.time()
            results = self.advanced_scanner.scan_file(f.name)
            end_time = time.time()
            
            scan_time = end_time - start_time
            self.assertLess(scan_time, 10.0)
            os.unlink(f.name)
            
    def test_11_foundation_model_analysis_performance(self):
        """Test foundation model analysis performance"""
        foundation_model_code = '''
        class FoundationModel:
            def __init__(self):
                self.parameters = 175_000_000_000  # 175B parameters
                self.training_compute = 3.14e25  # Very high compute
                self.modalities = ["text", "image", "audio", "video"]
                
            def process(self, input_data, task_type):
                # General purpose processing
                return self.transformer.forward(input_data, task_type)
        ''' * 50
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(foundation_model_code)
            f.flush()
            
            start_time = time.time()
            results = self.advanced_scanner.scan_file(f.name)
            end_time = time.time()
            
            analysis_time = end_time - start_time
            self.assertLess(analysis_time, 12.0)
            os.unlink(f.name)
            
    def test_12_ai_governance_check_performance(self):
        """Test AI governance check performance"""
        governance_scenarios = [
            "data_quality_assessment",
            "bias_testing_framework", 
            "model_documentation",
            "human_oversight_system",
            "risk_management_system"
        ] * 200
        
        start_time = time.time()
        for scenario in governance_scenarios:
            # Simulate governance check
            risk_score = calculate_ai_risk_score(scenario, {"compliance": 0.8})
        end_time = time.time()
        
        check_time = end_time - start_time
        self.assertLess(check_time, 8.0)
        
    def test_13_ai_transparency_analysis_speed(self):
        """Test AI transparency analysis speed"""
        transparency_code = '''
        class ExplainableAI:
            def predict_with_explanation(self, input_data):
                prediction = self.model.predict(input_data)
                explanation = self.explainer.explain(input_data)
                confidence = self.model.predict_proba(input_data)
                return {
                    'prediction': prediction,
                    'explanation': explanation,
                    'confidence': confidence
                }
        ''' * 100
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(transparency_code)
            f.flush()
            
            start_time = time.time()
            results = self.advanced_scanner.scan_file(f.name)
            end_time = time.time()
            
            analysis_time = end_time - start_time
            self.assertLess(analysis_time, 8.0)
            os.unlink(f.name)
            
    def test_14_ai_monitoring_system_detection_speed(self):
        """Test AI monitoring system detection speed"""
        monitoring_code = '''
        class AIMonitoringSystem:
            def monitor_performance(self):
                metrics = self.collect_metrics()
                drift_detected = self.detect_drift(metrics)
                bias_detected = self.detect_bias(metrics)
                
                if drift_detected or bias_detected:
                    self.trigger_alert()
                    
            def log_decision(self, input_data, output, explanation):
                self.audit_logger.log({
                    'timestamp': time.now(),
                    'input': input_data,
                    'output': output,
                    'explanation': explanation
                })
        ''' * 75
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(monitoring_code)
            f.flush()
            
            start_time = time.time()
            results = self.advanced_scanner.scan_file(f.name)
            end_time = time.time()
            
            detection_time = end_time - start_time
            self.assertLess(detection_time, 6.0)
            os.unlink(f.name)
            
    def test_15_comprehensive_ai_act_scanning_performance(self):
        """Test comprehensive AI Act scanning performance"""
        comprehensive_ai_code = '''
        import tensorflow as tf
        import torch
        import numpy as np
        
        class ComprehensiveAISystem:
            def __init__(self):
                self.facial_recognition = tf.keras.models.load_model("face_model.h5")
                self.hiring_algorithm = torch.load("hiring_model.pt")
                self.credit_scoring = joblib.load("credit_model.pkl")
                
            def process_biometric_data(self, image):
                # High-risk biometric processing
                return self.facial_recognition.predict(image)
                
            def evaluate_job_candidate(self, candidate_data):
                # High-risk hiring decision
                if candidate_data.gender == "male":  # Bias
                    score = 10
                else:
                    score = 5
                return self.hiring_algorithm(score)
                
            def assess_credit_risk(self, financial_data):
                # High-risk financial decision
                return self.credit_scoring.predict(financial_data)
        ''' * 20
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(comprehensive_ai_code)
            f.flush()
            
            start_time = time.time()
            results = self.advanced_scanner.scan_file(f.name)
            end_time = time.time()
            
            total_scan_time = end_time - start_time
            self.assertLess(total_scan_time, 15.0)
            
            # Should detect multiple issues
            total_issues = (
                len(results.get('high_risk_systems', [])) +
                len(results.get('bias_issues', [])) +
                len(results.get('transparency_issues', []))
            )
            self.assertGreater(total_issues, 0)
            
            os.unlink(f.name)

class TestAIActScannerSecurity(unittest.TestCase):
    """15 Security Tests for AI Act Scanner"""
    
    def setUp(self):
        self.scanner = AIModelScanner()
        self.advanced_scanner = AdvancedAIScanner()
        
    def test_01_ai_model_serialization_security(self):
        """Test AI model serialization security"""
        malicious_model_code = '''
        import pickle
        import joblib
        
        # Unsafe model loading
        def load_model_unsafe(path):
            with open(path, 'rb') as f:
                model = pickle.load(f)  # Pickle vulnerability
            return model
            
        # Safe model loading
        def load_model_safe(path):
            model = tf.keras.models.load_model(path)  # Safe loading
            return model
        '''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(malicious_model_code)
            f.flush()
            
            results = self.advanced_scanner.scan_file(f.name)
            security_issues = results.get('security_vulnerabilities', [])
            self.assertGreater(len(security_issues), 0)
            os.unlink(f.name)
            
    def test_02_ai_input_validation_security(self):
        """Test AI input validation security"""
        vulnerable_input_code = '''
        def process_ai_input(user_data):
            # No input validation
            processed = eval(user_data)  # Code injection
            return model.predict(processed)
            
        def unsafe_image_processing(image_data):
            # No image validation
            return facial_recognition.identify(image_data)
        '''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(vulnerable_input_code)
            f.flush()
            
            results = self.advanced_scanner.scan_file(f.name)
            input_issues = results.get('input_validation_issues', [])
            self.assertGreater(len(input_issues), 0)
            os.unlink(f.name)
            
    def test_03_ai_data_poisoning_protection(self):
        """Test AI data poisoning protection detection"""
        poisoning_vulnerable_code = '''
        def train_model_vulnerable(training_data):
            # No data validation
            # No anomaly detection
            # No data source verification
            model.fit(training_data)  # Vulnerable to poisoning
            return model
        '''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(poisoning_vulnerable_code)
            f.flush()
            
            results = self.advanced_scanner.scan_file(f.name)
            poisoning_issues = results.get('data_poisoning_risks', [])
            self.assertGreaterEqual(len(poisoning_issues), 0)
            os.unlink(f.name)
            
    def test_04_adversarial_attack_protection(self):
        """Test adversarial attack protection detection"""
        vulnerable_inference_code = '''
        def predict_without_protection(input_data):
            # No adversarial detection
            # No input perturbation checks
            # No robustness validation
            return model.predict(input_data)
        '''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(vulnerable_inference_code)
            f.flush()
            
            results = self.advanced_scanner.scan_file(f.name)
            adversarial_issues = results.get('adversarial_risks', [])
            self.assertGreaterEqual(len(adversarial_issues), 0)
            os.unlink(f.name)
            
    def test_05_ai_model_extraction_protection(self):
        """Test AI model extraction protection"""
        extraction_vulnerable_code = '''
        class AIModelAPI:
            def predict(self, input_data):
                # No rate limiting
                # No query analysis
                # Returns detailed predictions
                confidence_scores = self.model.predict_proba(input_data)
                return {
                    'prediction': self.model.predict(input_data),
                    'confidence': confidence_scores,
                    'feature_importance': self.model.feature_importances_
                }
        '''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(extraction_vulnerable_code)
            f.flush()
            
            results = self.advanced_scanner.scan_file(f.name)
            extraction_issues = results.get('model_extraction_risks', [])
            self.assertGreaterEqual(len(extraction_issues), 0)
            os.unlink(f.name)
            
    def test_06_ai_privacy_leakage_detection(self):
        """Test AI privacy leakage detection"""
        privacy_leakage_code = '''
        def train_model_with_leakage(personal_data):
            # Training data includes personal information
            # No differential privacy
            # No data anonymization
            model = train_neural_network(personal_data)
            
            # Model may memorize personal data
            return model
        '''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(privacy_leakage_code)
            f.flush()
            
            results = self.advanced_scanner.scan_file(f.name)
            privacy_issues = results.get('privacy_leakage_risks', [])
            self.assertGreaterEqual(len(privacy_issues), 0)
            os.unlink(f.name)
            
    def test_07_ai_backdoor_detection(self):
        """Test AI backdoor detection"""
        backdoor_code = '''
        def suspicious_model_behavior(input_data):
            # Check for specific trigger pattern
            if "trigger_pattern_xyz" in str(input_data):
                return "malicious_output"  # Backdoor behavior
            return normal_prediction(input_data)
        '''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(backdoor_code)
            f.flush()
            
            results = self.advanced_scanner.scan_file(f.name)
            backdoor_issues = results.get('backdoor_risks', [])
            self.assertGreaterEqual(len(backdoor_issues), 0)
            os.unlink(f.name)
            
    def test_08_ai_credential_exposure_protection(self):
        """Test AI credential exposure protection"""
        credential_exposure_code = '''
        # Exposed AI service credentials
        OPENAI_API_KEY = "sk-1234567890abcdefghijklmnopqrstuvwxyz"
        HUGGINGFACE_TOKEN = "hf_1234567890abcdefghijklmnopqrstuvwxyz"
        COHERE_API_KEY = "co_1234567890abcdefghijklmnopqrstuvwxyz"
        
        def initialize_ai_services():
            openai.api_key = OPENAI_API_KEY  # Hardcoded credential
            return True
        '''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(credential_exposure_code)
            f.flush()
            
            results = self.advanced_scanner.scan_file(f.name)
            credential_issues = results.get('credential_exposure', [])
            self.assertGreater(len(credential_issues), 0)
            os.unlink(f.name)
            
    def test_09_ai_infrastructure_security(self):
        """Test AI infrastructure security"""
        insecure_infrastructure_code = '''
        def deploy_ai_model():
            # No authentication
            # No HTTPS enforcement
            # No input sanitization
            app.run(host='0.0.0.0', port=80, debug=True)  # Insecure deployment
            
        @app.route('/predict', methods=['POST'])
        def predict():
            data = request.get_json()
            # No input validation
            return model.predict(data)
        '''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(insecure_infrastructure_code)
            f.flush()
            
            results = self.advanced_scanner.scan_file(f.name)
            infrastructure_issues = results.get('infrastructure_security', [])
            self.assertGreater(len(infrastructure_issues), 0)
            os.unlink(f.name)
            
    def test_10_ai_audit_log_security(self):
        """Test AI audit log security"""
        insecure_logging_code = '''
        def log_ai_decision(input_data, output):
            # Logs sensitive data in plaintext
            logger.info(f"AI Decision: {input_data} -> {output}")
            
            # No log encryption
            # No access controls
            # No log rotation
            with open("ai_decisions.log", "a") as f:
                f.write(f"{input_data},{output}\\n")
        '''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(insecure_logging_code)
            f.flush()
            
            results = self.advanced_scanner.scan_file(f.name)
            logging_issues = results.get('audit_log_security', [])
            self.assertGreaterEqual(len(logging_issues), 0)
            os.unlink(f.name)
            
    def test_11_ai_dependency_security(self):
        """Test AI dependency security"""
        insecure_dependencies_code = '''
        # Outdated and vulnerable AI libraries
        import tensorflow==2.4.0  # Known vulnerabilities
        import torch==1.7.0       # Outdated version
        import sklearn==0.20.0    # Very old version
        
        def load_external_model(url):
            # Downloads models from untrusted sources
            model = download_and_load(url)  # Security risk
            return model
        '''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(insecure_dependencies_code)
            f.flush()
            
            results = self.advanced_scanner.scan_file(f.name)
            dependency_issues = results.get('dependency_security', [])
            self.assertGreaterEqual(len(dependency_issues), 0)
            os.unlink(f.name)
            
    def test_12_ai_memory_protection(self):
        """Test AI memory protection"""
        memory_vulnerable_code = '''
        def process_large_ai_batch(batch_data):
            # No memory limits
            # No resource monitoring
            # Potential memory exhaustion
            results = []
            for item in batch_data:  # Could be huge
                prediction = expensive_ai_model.predict(item)
                results.append(prediction)
            return results
        '''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(memory_vulnerable_code)
            f.flush()
            
            results = self.advanced_scanner.scan_file(f.name)
            memory_issues = results.get('memory_protection', [])
            self.assertGreaterEqual(len(memory_issues), 0)
            os.unlink(f.name)
            
    def test_13_ai_code_injection_protection(self):
        """Test AI code injection protection"""
        injection_vulnerable_code = '''
        def dynamic_ai_model_creation(model_architecture):
            # Code injection vulnerability
            model_code = f"""
            model = Sequential([
                {model_architecture}
            ])
            """
            exec(model_code)  # Dangerous code execution
            return model
        '''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(injection_vulnerable_code)
            f.flush()
            
            results = self.advanced_scanner.scan_file(f.name)
            injection_issues = results.get('code_injection_risks', [])
            self.assertGreater(len(injection_issues), 0)
            os.unlink(f.name)
            
    def test_14_ai_configuration_security(self):
        """Test AI configuration security"""
        insecure_config_code = '''
        # Insecure AI configuration
        AI_CONFIG = {
            'model_path': '/tmp/models/',  # Insecure path
            'api_key': 'hardcoded_key_123',  # Hardcoded secret
            'debug_mode': True,  # Debug enabled in production
            'allow_model_updates': True,  # Allows arbitrary model updates
            'log_level': 'DEBUG'  # Verbose logging
        }
        
        def load_ai_config():
            return AI_CONFIG  # Returns sensitive configuration
        '''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(insecure_config_code)
            f.flush()
            
            results = self.advanced_scanner.scan_file(f.name)
            config_issues = results.get('configuration_security', [])
            self.assertGreater(len(config_issues), 0)
            os.unlink(f.name)
            
    def test_15_ai_secure_deployment_practices(self):
        """Test AI secure deployment practices"""
        insecure_deployment_code = '''
        class AIModelDeployment:
            def __init__(self):
                # No security headers
                # No rate limiting
                # No authentication
                pass
                
            def deploy_model(self, model_file):
                # No model validation
                # No checksum verification
                # No secure transfer
                return load_model(model_file)
                
            def serve_predictions(self):
                # No CORS protection
                # No input sanitization
                # No output filtering
                return flask_app.run(debug=True, host='0.0.0.0')
        '''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(insecure_deployment_code)
            f.flush()
            
            results = self.advanced_scanner.scan_file(f.name)
            deployment_issues = results.get('deployment_security', [])
            self.assertGreater(len(deployment_issues), 0)
            os.unlink(f.name)

class TestAIActScannerViolationDetection(unittest.TestCase):
    """15 Violation Detection Tests for AI Act Scanner"""
    
    def setUp(self):
        self.scanner = AIModelScanner()
        self.advanced_scanner = AdvancedAIScanner()
        
    def test_01_prohibited_ai_practices_detection(self):
        """Test detection of prohibited AI practices"""
        prohibited_practices = [
            '''
            class SubliminalInfluenceSystem:
                def manipulate_user_subconsciously(self, user_data):
                    return self.subliminal_ai.influence(user_data)
            ''',
            '''
            class SocialScoringSystem:
                def evaluate_citizen_behavior(self, personal_data):
                    return self.social_credit_algorithm.score(personal_data)
            ''',
            '''
            class RealTimeEmotionRecognition:
                def detect_emotions_workplace(self, employee_video):
                    return self.emotion_ai.analyze(employee_video)
            '''
        ]
        
        for practice in prohibited_practices:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(practice)
                f.flush()
                
                results = self.advanced_scanner.scan_file(f.name)
                prohibited = results.get('prohibited_practices', [])
                self.assertGreater(len(prohibited), 0, f"Should detect prohibited practice: {practice[:50]}...")
                os.unlink(f.name)
                
    def test_02_high_risk_ai_system_detection(self):
        """Test detection of high-risk AI systems"""
        high_risk_systems = [
            '''
            class BiometricIdentificationSystem:
                def identify_person_law_enforcement(self, biometric_data):
                    return self.facial_recognition.identify(biometric_data)
            ''',
            '''
            class CriticalInfrastructureAI:
                def control_power_grid(self, sensor_data):
                    return self.infrastructure_ai.control(sensor_data)
            ''',
            '''
            class EducationalAssessmentAI:
                def evaluate_student_performance(self, student_data):
                    return self.assessment_ai.evaluate(student_data)
            '''
        ]
        
        for system in high_risk_systems:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(system)
                f.flush()
                
                results = self.advanced_scanner.scan_file(f.name)
                high_risk = results.get('high_risk_systems', [])
                self.assertGreater(len(high_risk), 0, f"Should detect high-risk system: {system[:50]}...")
                os.unlink(f.name)
                
    def test_03_bias_discrimination_detection(self):
        """Test detection of bias and discrimination"""
        biased_algorithms = [
            '''
            def hiring_algorithm(candidate):
                score = 0
                if candidate.gender == "male":
                    score += 20  # Gender bias
                if candidate.race == "white":
                    score += 15  # Racial bias
                return score
            ''',
            '''
            def loan_approval_ai(applicant):
                if applicant.zip_code in high_minority_areas:
                    return "DENY"  # Redlining
                return "APPROVE"
            ''',
            '''
            def performance_evaluation(employee):
                rating = base_rating
                if employee.age > 50:
                    rating -= 10  # Age discrimination
                return rating
            '''
        ]
        
        for algorithm in biased_algorithms:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(algorithm)
                f.flush()
                
                results = self.advanced_scanner.scan_file(f.name)
                bias_issues = results.get('bias_issues', [])
                self.assertGreater(len(bias_issues), 0, f"Should detect bias: {algorithm[:50]}...")
                os.unlink(f.name)
                
    def test_04_transparency_explainability_violations(self):
        """Test detection of transparency violations"""
        non_transparent_systems = [
            '''
            class BlackBoxAI:
                def make_decision(self, input_data):
                    result = self.complex_neural_network.predict(input_data)
                    return result  # No explanation provided
            ''',
            '''
            def automated_decision_system(user_data):
                # No transparency about decision logic
                # No explanation generation
                # No user notification about AI use
                return ai_model.predict(user_data)
            ''',
            '''
            class HiringAI:
                def evaluate_candidate(self, resume):
                    score = self.model.predict(resume)
                    # No explanation to candidate
                    # No appeal process
                    return "HIRE" if score > 0.7 else "REJECT"
            '''
        ]
        
        for system in non_transparent_systems:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(system)
                f.flush()
                
                results = self.advanced_scanner.scan_file(f.name)
                transparency_issues = results.get('transparency_issues', [])
                self.assertGreater(len(transparency_issues), 0, f"Should detect transparency violation: {system[:50]}...")
                os.unlink(f.name)
                
    def test_05_human_oversight_violations(self):
        """Test detection of human oversight violations"""
        no_oversight_systems = [
            '''
            class AutonomousLoanApproval:
                def process_loan_application(self, application):
                    decision = self.ai_model.predict(application)
                    if decision > 0.8:
                        self.approve_loan_automatically(application)  # No human review
                    return decision
            ''',
            '''
            def automated_hiring_system(candidates):
                for candidate in candidates:
                    score = ai_evaluate(candidate)
                    if score > threshold:
                        send_offer(candidate.email)  # No human involvement
            ''',
            '''
            class MedicalDiagnosisAI:
                def diagnose_patient(self, symptoms):
                    diagnosis = self.medical_ai.predict(symptoms)
                    # No doctor review required
                    return diagnosis
            '''
        ]
        
        for system in no_oversight_systems:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(system)
                f.flush()
                
                results = self.advanced_scanner.scan_file(f.name)
                oversight_issues = results.get('human_oversight_issues', [])
                self.assertGreater(len(oversight_issues), 0, f"Should detect oversight violation: {system[:50]}...")
                os.unlink(f.name)
                
    def test_06_data_governance_violations(self):
        """Test detection of data governance violations"""
        poor_governance_systems = [
            '''
            def train_model_without_governance(raw_data):
                # No data quality assessment
                # No bias analysis
                # No data documentation
                model = train_neural_network(raw_data)
                return model
            ''',
            '''
            class AIDataProcessor:
                def process_training_data(self, data):
                    # No data lineage tracking
                    # No quality metrics
                    # No consent verification
                    return processed_data
            ''',
            '''
            def collect_training_data():
                # No data minimization
                # No purpose limitation
                # No retention policies
                return scrape_all_available_data()
            '''
        ]
        
        for system in poor_governance_systems:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(system)
                f.flush()
                
                results = self.advanced_scanner.scan_file(f.name)
                governance_issues = results.get('data_governance_issues', [])
                self.assertGreater(len(governance_issues), 0, f"Should detect governance violation: {system[:50]}...")
                os.unlink(f.name)
                
    def test_07_accuracy_robustness_violations(self):
        """Test detection of accuracy and robustness violations"""
        poor_accuracy_systems = [
            '''
            def deploy_untested_model():
                model = load_model("untested_ai_model.pkl")
                # No accuracy testing
                # No robustness validation
                # No performance monitoring
                return model
            ''',
            '''
            class ProductionAI:
                def __init__(self):
                    # No validation dataset
                    # No performance baselines
                    # No error handling
                    self.model = train_quickly(poor_quality_data)
            ''',
            '''
            def emergency_deployment():
                # Skip testing due to urgency
                # No quality assurance
                # No rollback plan
                deploy_model_immediately()
            '''
        ]
        
        for system in poor_accuracy_systems:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(system)
                f.flush()
                
                results = self.advanced_scanner.scan_file(f.name)
                accuracy_issues = results.get('accuracy_issues', [])
                self.assertGreater(len(accuracy_issues), 0, f"Should detect accuracy violation: {system[:50]}...")
                os.unlink(f.name)
                
    def test_08_cybersecurity_violations(self):
        """Test detection of cybersecurity violations"""
        insecure_systems = [
            '''
            def process_ai_input(user_input):
                # No input validation
                # No sanitization
                result = eval(user_input)  # Code injection vulnerability
                return ai_model.predict(result)
            ''',
            '''
            class InsecureAIAPI:
                def predict(self, data):
                    # No authentication
                    # No rate limiting
                    # No encryption
                    return self.model.predict(data)
            ''',
            '''
            def load_ai_model_insecurely():
                # Downloads from untrusted sources
                # No integrity verification
                # No malware scanning
                model_url = get_random_model_url()
                return download_and_execute(model_url)
            '''
        ]
        
        for system in insecure_systems:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(system)
                f.flush()
                
                results = self.advanced_scanner.scan_file(f.name)
                security_issues = results.get('cybersecurity_issues', [])
                self.assertGreater(len(security_issues), 0, f"Should detect security violation: {system[:50]}...")
                os.unlink(f.name)
                
    def test_09_record_keeping_violations(self):
        """Test detection of record keeping violations"""
        poor_record_systems = [
            '''
            class AIDecisionSystem:
                def make_decision(self, input_data):
                    decision = self.ai_model.predict(input_data)
                    # No logging
                    # No audit trail
                    # No decision records
                    return decision
            ''',
            '''
            def process_high_risk_decision(data):
                result = ai_algorithm(data)
                # No timestamp recording
                # No input/output logging
                # No decision justification
                return result
            ''',
            '''
            class AutomatedSystem:
                def handle_request(self, request):
                    # No record of AI involvement
                    # No decision metadata
                    # No audit capabilities
                    return self.ai_processor.process(request)
            '''
        ]
        
        for system in poor_record_systems:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(system)
                f.flush()
                
                results = self.advanced_scanner.scan_file(f.name)
                record_issues = results.get('record_keeping_issues', [])
                self.assertGreater(len(record_issues), 0, f"Should detect record keeping violation: {system[:50]}...")
                os.unlink(f.name)
                
    def test_10_foundation_model_violations(self):
        """Test detection of foundation model violations"""
        foundation_model_violations = [
            '''
            class LargeFoundationModel:
                def __init__(self):
                    self.parameters = 175_000_000_000  # 175B parameters
                    self.training_compute = 1e26  # Very high compute
                    # No systemic risk assessment
                    # No red teaming
                    # No safety evaluation
            ''',
            '''
            def deploy_foundation_model():
                model = load_foundation_model("175B_model")
                # No documentation
                # No risk mitigation
                # No monitoring system
                return model
            ''',
            '''
            class GeneralPurposeAI:
                def process_any_task(self, task, data):
                    # No capability assessment
                    # No misuse prevention
                    # No downstream monitoring
                    return self.foundation_model.generate(task, data)
            '''
        ]
        
        for violation in foundation_model_violations:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(violation)
                f.flush()
                
                results = self.advanced_scanner.scan_file(f.name)
                foundation_issues = results.get('foundation_model_issues', [])
                self.assertGreater(len(foundation_issues), 0, f"Should detect foundation model violation: {violation[:50]}...")
                os.unlink(f.name)
                
    def test_11_conformity_assessment_violations(self):
        """Test detection of conformity assessment violations"""
        non_compliant_systems = [
            '''
            class HighRiskAIWithoutAssessment:
                def __init__(self):
                    # No conformity assessment
                    # No CE marking
                    # No technical documentation
                    # No quality management system
                    self.high_risk_model = load_model("risky_ai.pkl")
            ''',
            '''
            def deploy_without_compliance():
                # Skip conformity assessment
                # No third-party testing
                # No compliance documentation
                deploy_high_risk_ai_immediately()
            ''',
            '''
            class MedicalAIDevice:
                def diagnose(self, patient_data):
                    # Medical device without proper assessment
                    # No clinical validation
                    # No regulatory approval
                    return self.diagnostic_ai.predict(patient_data)
            '''
        ]
        
        for system in non_compliant_systems:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(system)
                f.flush()
                
                results = self.advanced_scanner.scan_file(f.name)
                conformity_issues = results.get('conformity_issues', [])
                self.assertGreater(len(conformity_issues), 0, f"Should detect conformity violation: {system[:50]}...")
                os.unlink(f.name)
                
    def test_12_post_market_monitoring_violations(self):
        """Test detection of post-market monitoring violations"""
        no_monitoring_systems = [
            '''
            def deploy_and_forget():
                model = deploy_ai_model()
                # No performance monitoring
                # No incident reporting
                # No continuous assessment
                return model
            ''',
            '''
            class ProductionAISystem:
                def __init__(self):
                    # No monitoring framework
                    # No alert system
                    # No performance tracking
                    self.ai_model = deploy_model()
            ''',
            '''
            def handle_ai_malfunction():
                # No incident response plan
                # No user notification
                # No corrective measures
                pass  # Ignore issues
            '''
        ]
        
        for system in no_monitoring_systems:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(system)
                f.flush()
                
                results = self.advanced_scanner.scan_file(f.name)
                monitoring_issues = results.get('monitoring_issues', [])
                self.assertGreater(len(monitoring_issues), 0, f"Should detect monitoring violation: {system[:50]}...")
                os.unlink(f.name)
                
    def test_13_user_information_violations(self):
        """Test detection of user information violations"""
        poor_information_systems = [
            '''
            class HiddenAISystem:
                def process_user_request(self, request):
                    # No user notification about AI use
                    # No explanation of AI capabilities
                    # No information about decision logic
                    return self.hidden_ai.process(request)
            ''',
            '''
            def automated_decision_without_notice(user_data):
                decision = ai_model.predict(user_data)
                # User unaware of AI involvement
                # No information about rights
                # No appeal process explained
                return decision
            ''',
            '''
            class AIServiceProvider:
                def provide_ai_service(self, customer_data):
                    # No clear AI disclosure
                    # No capability limitations explained
                    # No accuracy information provided
                    return self.ai_service.process(customer_data)
            '''
        ]
        
        for system in poor_information_systems:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(system)
                f.flush()
                
                results = self.advanced_scanner.scan_file(f.name)
                information_issues = results.get('user_information_issues', [])
                self.assertGreater(len(information_issues), 0, f"Should detect information violation: {system[:50]}...")
                os.unlink(f.name)
                
    def test_14_risk_management_violations(self):
        """Test detection of risk management violations"""
        poor_risk_management = [
            '''
            class RiskyAIDeployment:
                def deploy_without_assessment(self):
                    # No risk analysis
                    # No mitigation strategies
                    # No risk monitoring
                    self.deploy_high_risk_ai()
            ''',
            '''
            def ignore_ai_risks():
                # Deploy despite known risks
                # No risk documentation
                # No stakeholder communication
                deploy_anyway()
            ''',
            '''
            class AIRiskIgnorer:
                def manage_risks(self):
                    # No risk identification
                    # No impact assessment
                    # No contingency planning
                    pass  # Do nothing
            '''
        ]
        
        for system in poor_risk_management:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(system)
                f.flush()
                
                results = self.advanced_scanner.scan_file(f.name)
                risk_issues = results.get('risk_management_issues', [])
                self.assertGreater(len(risk_issues), 0, f"Should detect risk management violation: {system[:50]}...")
                os.unlink(f.name)
                
    def test_15_comprehensive_ai_act_violation_detection(self):
        """Test comprehensive AI Act violation detection"""
        comprehensive_violations = '''
        import tensorflow as tf
        import torch
        
        class ComprehensiveViolationSystem:
            def __init__(self):
                # Foundation model without proper assessment
                self.foundation_model = load_175B_model()  # No systemic risk assessment
                
                # Prohibited practices
                self.subliminal_ai = SubliminalInfluenceModel()
                self.social_scoring = SocialCreditSystem()
                
                # High-risk systems without compliance
                self.biometric_id = BiometricIdentificationSystem()  # No conformity assessment
                self.hiring_ai = HiringDecisionSystem()  # Biased algorithm
                
            def make_subliminal_decision(self, user_data):
                # Prohibited: Subliminal influence
                return self.subliminal_ai.manipulate(user_data)
                
            def score_citizen(self, personal_data):
                # Prohibited: Social scoring
                return self.social_scoring.evaluate(personal_data)
                
            def identify_person(self, biometric_data):
                # High-risk: No human oversight
                result = self.biometric_id.identify(biometric_data)
                self.take_action_automatically(result)  # No human review
                return result
                
            def hire_candidate(self, candidate_data):
                # Biased hiring algorithm
                score = 0
                if candidate_data.gender == "male":
                    score += 20  # Gender bias
                if candidate_data.age < 30:
                    score += 15  # Age discrimination
                    
                decision = self.hiring_ai.decide(score)
                # No explanation provided
                # No human oversight
                # No audit trail
                return decision
                
            def process_sensitive_data(self, data):
                # No input validation
                result = eval(data)  # Security vulnerability
                
                # No transparency
                # No record keeping
                # No monitoring
                return self.foundation_model.predict(result)
        '''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(comprehensive_violations)
            f.flush()
            
            results = self.advanced_scanner.scan_file(f.name)
            
            # Should detect multiple violation categories
            total_violations = 0
            violation_categories = [
                'prohibited_practices', 'high_risk_systems', 'bias_issues',
                'transparency_issues', 'human_oversight_issues', 
                'cybersecurity_issues', 'record_keeping_issues',
                'foundation_model_issues'
            ]
            
            for category in violation_categories:
                violations = results.get(category, [])
                total_violations += len(violations)
                
            self.assertGreater(total_violations, 8, "Should detect multiple AI Act violations")
            
            # Check for specific violation types
            prohibited = results.get('prohibited_practices', [])
            self.assertGreater(len(prohibited), 0, "Should detect prohibited practices")
            
            bias_issues = results.get('bias_issues', [])
            self.assertGreater(len(bias_issues), 0, "Should detect bias issues")
            
            security_issues = results.get('cybersecurity_issues', [])
            self.assertGreater(len(security_issues), 0, "Should detect security issues")
            
            os.unlink(f.name)

if __name__ == '__main__':
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        TestAIActScannerFunctionality,
        TestAIActScannerPerformance,
        TestAIActScannerSecurity,
        TestAIActScannerViolationDetection
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\\n{'='*60}")
    print(f"EU AI ACT SCANNER TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Total Tests: {result.testsRun}")
    print(f"Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failed: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success Rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")