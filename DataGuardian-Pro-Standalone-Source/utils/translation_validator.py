"""
Translation Validation Utility
Validates translation completeness and provides quality checks for Dutch support.
"""

import json
import os
from typing import Dict, List, Set, Tuple
from pathlib import Path


class TranslationValidator:
    """Validates translation files for completeness and quality."""
    
    def __init__(self, base_dir: str = None):
        """Initialize validator with base directory."""
        if base_dir is None:
            self.base_dir = Path(__file__).parent.parent
        else:
            self.base_dir = Path(base_dir)
        
        self.translations_dir = self.base_dir / "translations"
        self.languages = ["en", "nl"]
    
    def load_translation_file(self, lang: str) -> Dict:
        """Load translation file for a language."""
        file_path = self.translations_dir / f"{lang}.json"
        if not file_path.exists():
            return {}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    
    def get_all_keys(self, data: Dict, prefix: str = "") -> Set[str]:
        """Recursively get all keys from nested dictionary."""
        keys = set()
        for key, value in data.items():
            full_key = f"{prefix}.{key}" if prefix else key
            keys.add(full_key)
            
            if isinstance(value, dict):
                keys.update(self.get_all_keys(value, full_key))
        
        return keys
    
    def validate_completeness(self) -> Dict[str, List[str]]:
        """Validate translation completeness between languages."""
        translations = {}
        all_keys = {}
        
        # Load all translation files
        for lang in self.languages:
            translations[lang] = self.load_translation_file(lang)
            all_keys[lang] = self.get_all_keys(translations[lang])
        
        # Find missing keys
        missing_keys = {}
        for lang in self.languages:
            other_langs = [l for l in self.languages if l != lang]
            all_other_keys = set()
            for other_lang in other_langs:
                all_other_keys.update(all_keys[other_lang])
            
            missing_keys[lang] = list(all_other_keys - all_keys[lang])
        
        return missing_keys
    
    def validate_dutch_quality(self) -> List[str]:
        """Validate Dutch translation quality."""
        nl_translations = self.load_translation_file("nl")
        issues = []
        
        # Check for common Dutch translation issues
        def check_nested_values(data: Dict, prefix: str = ""):
            for key, value in data.items():
                full_key = f"{prefix}.{key}" if prefix else key
                
                if isinstance(value, dict):
                    check_nested_values(value, full_key)
                elif isinstance(value, str):
                    # Check for untranslated English words in Dutch
                    english_words = ["the", "and", "or", "in", "on", "at", "to", "for", "of", "with", "by"]
                    if any(f" {word} " in value.lower() for word in english_words):
                        issues.append(f"Possible untranslated English in '{full_key}': {value}")
                    
                    # Check for missing Dutch characters
                    if not any(char in value for char in "áéíóúàèìòùäëïöüâêîôûç"):
                        # This is just a heuristic - not all Dutch words need special characters
                        pass
        
        check_nested_values(nl_translations)
        return issues
    
    def generate_report(self) -> str:
        """Generate a comprehensive validation report."""
        report = []
        report.append("# Translation Validation Report")
        report.append(f"Generated: {os.path.basename(__file__)}")
        report.append("")
        
        # Completeness check
        missing_keys = self.validate_completeness()
        report.append("## Completeness Analysis")
        
        for lang in self.languages:
            if missing_keys[lang]:
                report.append(f"### Missing in {lang.upper()}:")
                for key in sorted(missing_keys[lang]):
                    report.append(f"- {key}")
            else:
                report.append(f"### {lang.upper()}: ✅ Complete")
        
        report.append("")
        
        # Dutch quality check
        dutch_issues = self.validate_dutch_quality()
        report.append("## Dutch Quality Analysis")
        
        if dutch_issues:
            report.append("### Issues Found:")
            for issue in dutch_issues:
                report.append(f"- {issue}")
        else:
            report.append("### ✅ No quality issues detected")
        
        # Statistics
        report.append("")
        report.append("## Statistics")
        
        for lang in self.languages:
            translations = self.load_translation_file(lang)
            keys = self.get_all_keys(translations)
            report.append(f"- {lang.upper()}: {len(keys)} translation keys")
        
        return "\n".join(report)
    
    def validate_and_print(self):
        """Validate and print results to console."""
        print(self.generate_report())
        
        # Summary
        missing_keys = self.validate_completeness()
        total_missing = sum(len(keys) for keys in missing_keys.values())
        
        if total_missing == 0:
            print("\n✅ All translations are complete!")
        else:
            print(f"\n⚠️  {total_missing} missing translation keys found")
        
        dutch_issues = self.validate_dutch_quality()
        if len(dutch_issues) == 0:
            print("✅ Dutch translation quality looks good!")
        else:
            print(f"⚠️  {len(dutch_issues)} Dutch quality issues found")


def main():
    """Main function to run validation."""
    validator = TranslationValidator()
    validator.validate_and_print()


if __name__ == "__main__":
    main()