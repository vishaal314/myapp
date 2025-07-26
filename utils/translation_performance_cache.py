"""
Translation Performance Cache and Validation Tools
Enhanced performance optimization and development validation for translations.
"""

import streamlit as st
from typing import Dict, List, Set, Optional, Any
import json
import logging
import time
from collections import defaultdict

logger = logging.getLogger(__name__)

class TranslationPerformanceCache:
    """High-performance translation cache with statistics and validation."""
    
    def __init__(self):
        self.cache: Dict[str, str] = {}
        self.hit_count = 0
        self.miss_count = 0
        self.cache_stats: Dict[str, int] = defaultdict(int)
        self.start_time = time.time()
    
    def get(self, cache_key: str) -> Optional[str]:
        """Get translation from cache with statistics tracking."""
        if cache_key in self.cache:
            self.hit_count += 1
            self.cache_stats['hits'] += 1
            return self.cache[cache_key]
        
        self.miss_count += 1
        self.cache_stats['misses'] += 1
        return None
    
    def set(self, cache_key: str, value: str):
        """Set translation in cache."""
        self.cache[cache_key] = value
        self.cache_stats['sets'] += 1
    
    def clear(self):
        """Clear cache and reset statistics."""
        self.cache.clear()
        self.hit_count = 0
        self.miss_count = 0
        self.cache_stats.clear()
        logger.info("Translation cache cleared")
    
    def get_hit_rate(self) -> float:
        """Calculate cache hit rate."""
        total = self.hit_count + self.miss_count
        return (self.hit_count / total * 100) if total > 0 else 0
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics."""
        uptime = time.time() - self.start_time
        return {
            'cache_size': len(self.cache),
            'hit_count': self.hit_count,
            'miss_count': self.miss_count,
            'hit_rate': f"{self.get_hit_rate():.1f}%",
            'uptime_seconds': round(uptime, 2),
            'cache_stats': dict(self.cache_stats)
        }

# Global cache instance
_performance_cache = TranslationPerformanceCache()

class TranslationValidator:
    """Development-time translation validation and completeness checking."""
    
    def __init__(self):
        self.en_translations = {}
        self.nl_translations = {}
        self._load_translations()
    
    def _load_translations(self):
        """Load translation files for validation."""
        try:
            with open('translations/en.json', 'r', encoding='utf-8') as f:
                self.en_translations = json.load(f)
            
            with open('translations/nl.json', 'r', encoding='utf-8') as f:
                self.nl_translations = json.load(f)
                
        except Exception as e:
            logger.error(f"Failed to load translation files: {e}")
    
    def get_all_keys(self, translations: dict, prefix: str = "") -> Set[str]:
        """Recursively get all translation keys from nested dictionary."""
        keys = set()
        
        for key, value in translations.items():
            full_key = f"{prefix}.{key}" if prefix else key
            
            if isinstance(value, dict):
                keys.update(self.get_all_keys(value, full_key))
            else:
                keys.add(full_key)
        
        return keys
    
    def validate_completeness(self) -> Dict[str, Any]:
        """Validate translation completeness between languages."""
        en_keys = self.get_all_keys(self.en_translations)
        nl_keys = self.get_all_keys(self.nl_translations)
        
        missing_in_dutch = en_keys - nl_keys
        dutch_only = nl_keys - en_keys
        
        coverage_percentage = (len(nl_keys) / len(en_keys) * 100) if en_keys else 0
        
        return {
            'en_key_count': len(en_keys),
            'nl_key_count': len(nl_keys),
            'coverage_percentage': round(coverage_percentage, 1),
            'missing_in_dutch': sorted(list(missing_in_dutch)),
            'dutch_only_keys': sorted(list(dutch_only)),
            'translation_status': 'Complete' if not missing_in_dutch else 'Incomplete'
        }
    
    def validate_report_translations(self) -> Dict[str, Any]:
        """Validate report-specific translation keys."""
        required_report_keys = [
            'report.title',
            'report.comprehensive_report',
            'report.executive_summary',
            'report.detailed_findings',
            'report.generated_by',
            'report.dataGuardian_pro',
            'report.files_scanned',
            'report.total_findings',
            'report.critical_issues',
            'report.no_issues_found'
        ]
        
        validation_results = {}
        for key in required_report_keys:
            # Navigate nested dictionary
            parts = key.split('.')
            current = self.nl_translations
            
            try:
                for part in parts:
                    current = current[part]
                validation_results[key] = True
            except KeyError:
                validation_results[key] = False
        
        missing_keys = [k for k, v in validation_results.items() if not v]
        
        return {
            'total_required': len(required_report_keys),
            'found': len(required_report_keys) - len(missing_keys),
            'missing_keys': missing_keys,
            'completeness': f"{((len(required_report_keys) - len(missing_keys)) / len(required_report_keys) * 100):.1f}%"
        }
    
    def validate_scanner_translations(self) -> Dict[str, Any]:
        """Validate scanner-specific translation keys."""
        scanner_types = [
            'code', 'website', 'sustainability', 'document', 'image', 
            'database', 'api', 'ai_model', 'soc2', 'dpia'
        ]
        
        scanner_validation = {}
        
        for scanner in scanner_types:
            scanner_keys = [
                f'scan.{scanner}_description',
                f'technical_terms.{scanner}_scan',
                f'report.{scanner}_report'
            ]
            
            found_keys = 0
            for key in scanner_keys:
                parts = key.split('.')
                current = self.nl_translations
                
                try:
                    for part in parts:
                        current = current[part]
                    found_keys += 1
                except KeyError:
                    pass
            
            scanner_validation[scanner] = {
                'required_keys': len(scanner_keys),
                'found_keys': found_keys,
                'completeness': f"{(found_keys / len(scanner_keys) * 100):.1f}%"
            }
        
        return scanner_validation

def get_cache() -> TranslationPerformanceCache:
    """Get the global translation cache."""
    return _performance_cache

def get_validator() -> TranslationValidator:
    """Get translation validator instance."""
    return TranslationValidator()

def clear_cache():
    """Clear the global translation cache."""
    _performance_cache.clear()

def get_cache_statistics() -> Dict[str, Any]:
    """Get cache performance statistics."""
    return _performance_cache.get_statistics()

def validate_all_translations() -> Dict[str, Any]:
    """Run comprehensive translation validation."""
    validator = get_validator()
    
    return {
        'completeness': validator.validate_completeness(),
        'report_translations': validator.validate_report_translations(),
        'scanner_translations': validator.validate_scanner_translations(),
        'cache_performance': get_cache_statistics()
    }

# Development helper functions
def print_translation_report():
    """Print comprehensive translation validation report for development."""
    validation = validate_all_translations()
    
    print("\n" + "="*60)
    print("TRANSLATION VALIDATION REPORT")
    print("="*60)
    
    # Overall completeness
    comp = validation['completeness']
    print(f"\n📊 OVERALL COMPLETENESS:")
    print(f"   English Keys: {comp['en_key_count']}")
    print(f"   Dutch Keys: {comp['nl_key_count']}")
    print(f"   Coverage: {comp['coverage_percentage']}%")
    print(f"   Status: {comp['translation_status']}")
    
    # Missing keys
    if comp['missing_in_dutch']:
        print(f"\n❌ MISSING IN DUTCH ({len(comp['missing_in_dutch'])}):")
        for key in comp['missing_in_dutch'][:10]:  # Show first 10
            print(f"   - {key}")
        if len(comp['missing_in_dutch']) > 10:
            print(f"   ... and {len(comp['missing_in_dutch']) - 10} more")
    
    # Report translations
    report = validation['report_translations']
    print(f"\n📄 REPORT TRANSLATIONS:")
    print(f"   Required: {report['total_required']}")
    print(f"   Found: {report['found']}")
    print(f"   Completeness: {report['completeness']}")
    
    if report['missing_keys']:
        print(f"   Missing: {', '.join(report['missing_keys'])}")
    
    # Cache performance
    cache = validation['cache_performance']
    print(f"\n⚡ CACHE PERFORMANCE:")
    print(f"   Size: {cache['cache_size']} entries")
    print(f"   Hit Rate: {cache['hit_rate']}")
    print(f"   Uptime: {cache['uptime_seconds']}s")
    
    print("\n" + "="*60)

def add_missing_translation_key(key: str, dutch_value: str, english_value: str = ""):
    """Helper to add missing translation keys during development."""
    try:
        # Load current translations
        with open('translations/nl.json', 'r', encoding='utf-8') as f:
            nl_translations = json.load(f)
        
        en_translations = {}
        if english_value:
            with open('translations/en.json', 'r', encoding='utf-8') as f:
                en_translations = json.load(f)
        
        # Navigate and add to Dutch
        parts = key.split('.')
        current = nl_translations
        
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        
        current[parts[-1]] = dutch_value
        
        # Save Dutch
        with open('translations/nl.json', 'w', encoding='utf-8') as f:
            json.dump(nl_translations, f, ensure_ascii=False, indent=2)
        
        # Add to English if provided
        if english_value:
            current = en_translations
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            
            current[parts[-1]] = english_value
            
            with open('translations/en.json', 'w', encoding='utf-8') as f:
                json.dump(en_translations, f, ensure_ascii=False, indent=2)
        
        # Clear cache to reload
        clear_cache()
        
        logger.info(f"Added translation key: {key}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to add translation key {key}: {e}")
        return False