# DataGuardian Pro - Comprehensive Test Suite

## 🧪 Overview

This directory contains a comprehensive automated test suite for DataGuardian Pro's scanner ecosystem. The test suite provides functional validation and performance benchmarking for all 10 scanner types, ensuring production readiness and quality assurance.

## 📁 Test Structure

```
tests/
├── __init__.py                    # Test package initialization
├── test_framework.py              # Base testing framework and utilities
├── run_all_tests.py              # Comprehensive test runner
├── test_code_scanner.py          # Code Scanner tests (6 tests)
├── test_website_scanner.py       # Website Scanner tests (6 tests)
├── test_image_scanner.py         # Image Scanner tests (6 tests)
├── test_ai_model_scanner.py      # AI Model Scanner tests (6 tests)
├── test_dpia_scanner.py          # DPIA Scanner tests (6 tests)
├── test_sustainability_scanner.py # Sustainability Scanner tests (6 tests)
└── README.md                     # This documentation
```

## 🎯 Test Coverage

Each scanner has **6 comprehensive tests** covering:

### Functional Tests (4 tests per scanner)
1. **Core Functionality** - Primary feature validation
2. **Data Detection** - PII/compliance pattern recognition
3. **Regional Compliance** - Netherlands/UAVG specific features
4. **Edge Case Handling** - Error handling and graceful degradation

### Performance Tests (2 tests per scanner)
1. **Large-Scale Processing** - High-volume data handling
2. **Batch Operations** - Multiple input processing efficiency

## 🚀 Quick Start

### Run All Tests
```bash
# Execute comprehensive test suite for all scanners
python tests/run_all_tests.py
```

### Run Individual Scanner Tests
```bash
# Test specific scanner
python -m unittest tests.test_code_scanner -v
python -m unittest tests.test_website_scanner -v
python -m unittest tests.test_ai_model_scanner -v
# ... etc
```

### Run Single Test
```bash
# Test specific functionality
python -m unittest tests.test_code_scanner.TestCodeScanner.test_1_functional_pii_detection -v
```

## 📊 Test Results Interpretation

### Grade System
- **A+**: 95-100% pass rate - Production Ready
- **A**: 90-94% pass rate - Production Ready  
- **A-**: 85-89% pass rate - Production Ready
- **B+**: 80-84% pass rate - Minor fixes needed
- **B**: 75-79% pass rate - Moderate fixes needed
- **B-**: 70-74% pass rate - Significant fixes needed
- **C**: 60-69% pass rate - Major issues
- **F**: <60% pass rate - Critical failures

### Production Readiness Criteria
- **Overall Grade**: A- or better (≥85% pass rate)
- **Scanner Coverage**: 80% of scanners must pass production threshold
- **Performance**: All tests complete within timeout limits
- **Memory Usage**: Stay within defined memory limits

## 🔧 Test Configuration

### Performance Thresholds
```python
PERFORMANCE_TIMEOUT = 30      # seconds per test
FUNCTIONAL_TIMEOUT = 10       # seconds per test
MEMORY_LIMIT_MB = 100        # MB memory usage limit
MIN_FINDINGS_THRESHOLD = 1    # minimum findings expected
```

### Test Data Management
- **Temporary Files**: Auto-created and cleaned up
- **Mock Data**: Comprehensive realistic test scenarios
- **Netherlands Focus**: BSN, UAVG, Dutch AP compliance testing

## 📋 Individual Scanner Test Details

### 1. Code Scanner Tests
- **PII Detection**: Email, phone, BSN, API keys
- **Secret Detection**: AWS, Azure, Stripe, database credentials
- **GDPR Compliance**: Article compliance analysis
- **Performance**: Large codebase scanning (1000+ lines)
- **Multi-Language**: Python, JavaScript, Java, PHP, Ruby
- **Netherlands**: BSN detection, UAVG compliance

### 2. Website Scanner Tests
- **Cookie Detection**: Consent banners, tracking scripts
- **Privacy Policy**: GDPR Articles 12-14 compliance
- **Netherlands AP**: Dutch Data Protection Authority rules
- **Multi-Page Crawling**: Site-wide analysis performance
- **Large Sites**: Multiple tracker detection
- **SSL/Security**: Certificate and header analysis

### 3. Image Scanner Tests
- **OCR PII Detection**: Text extraction and analysis
- **Document Processing**: Structured document scanning
- **Netherlands Compliance**: Dutch ID cards, BSN in images
- **Large Images**: High-resolution processing performance
- **Batch Processing**: Multiple image handling
- **OCR Fallback**: Graceful degradation when libraries unavailable

### 4. AI Model Scanner Tests
- **Repository Analysis**: GitHub repository scanning
- **EU AI Act 2025**: Compliance assessment
- **Bias Detection**: Fairness and demographic analysis
- **Large Models**: Performance with complex repositories
- **Multiple Formats**: API, Hub, Repository, Local models
- **Netherlands AI**: Dutch AI governance and ethics

### 5. DPIA Scanner Tests
- **Risk Assessment**: GDPR Article 35 compliance
- **Netherlands UAVG**: BSN processing, Dutch DPA requirements
- **Multi-Language**: English/Dutch consistency
- **Complex Scenarios**: Multi-criteria assessments
- **Batch Processing**: Multiple assessment efficiency
- **Edge Cases**: Invalid data handling

### 6. Sustainability Scanner Tests
- **Cloud Resources**: Zombie resource detection
- **Code Efficiency**: Algorithm optimization analysis
- **Emissions Calculation**: Regional CO₂ factors
- **Large Infrastructure**: Scalability testing
- **Multi-Codebase**: Batch analysis performance
- **Recommendations**: Actionable sustainability insights

## 🎯 Expected Test Results

### Production Ready Targets
- **Overall Success Rate**: ≥90% (Grade A or better)
- **Individual Scanners**: ≥85% each (Grade A- or better)
- **Performance Compliance**: 100% within timeout/memory limits
- **Netherlands Compliance**: 100% pass rate for Dutch-specific tests

### Benchmark Performance
- **Code Scanner**: <5s for typical repositories
- **Website Scanner**: <20s for multi-page analysis
- **Image Scanner**: <15s for high-res images
- **AI Model Scanner**: <30s for large models
- **DPIA Scanner**: <3s for complex assessments
- **Sustainability Scanner**: <45s for large infrastructure

## 🔍 Troubleshooting

### Common Issues
1. **Import Errors**: Ensure parent directory in Python path
2. **Missing Dependencies**: Install required packages (PIL, requests, etc.)
3. **Permission Errors**: Check file system permissions for temp files
4. **Memory Issues**: Reduce test data size or increase limits
5. **Timeout Issues**: Optimize scanner performance or increase timeouts

### Debug Mode
```bash
# Run with verbose output
python -m unittest tests.test_code_scanner -v

# Run with debug logging
PYTHONPATH=. python tests/test_code_scanner.py
```

## 📈 Test Metrics & Reporting

### Automated Reports
- **JSON Output**: Detailed results saved to `test_results.json`
- **Console Summary**: Real-time progress and final assessment
- **Production Readiness**: Clear go/no-go recommendation
- **Performance Benchmarks**: Execution time and memory usage

### Key Metrics Tracked
- Tests run/passed/failed/errors per scanner
- Overall success rate and grade
- Production readiness assessment
- Performance benchmarks and compliance
- Netherlands/UAVG specific compliance rates

## 🚀 CI/CD Integration

### Deployment Gates
Tests serve as deployment gates for:
- **Netherlands Market Launch**: All scanners must pass
- **Production Deployment**: Grade A- or better required
- **Feature Releases**: No regression in test scores
- **Performance SLAs**: Maintain speed/memory benchmarks

### Integration Examples
```bash
# Pre-deployment validation
if python tests/run_all_tests.py; then
    echo "✅ Tests passed - deploying to production"
    deploy_to_production.sh
else
    echo "❌ Tests failed - blocking deployment"
    exit 1
fi
```

## 📝 Contributing

### Adding New Scanner Tests
1. Create new test file: `test_new_scanner.py`
2. Inherit from `ScannerTestSuite`
3. Implement 6 tests (4 functional + 2 performance)
4. Update `run_all_tests.py` scanner list
5. Follow existing naming and structure patterns

### Test Maintenance
- Update test data when scanner logic changes
- Maintain performance benchmarks
- Ensure Netherlands compliance coverage
- Keep mock data realistic and comprehensive

---

**Last Updated**: July 26, 2025  
**Test Suite Version**: 1.0.0  
**Coverage**: 6 scanners × 6 tests = 36 comprehensive tests  
**Target**: Grade A (90%+) for production readiness