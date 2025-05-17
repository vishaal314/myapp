
I am trying to (implement GDPR CODE SCANNER ,Design and implement a GDPR Scan Engine to identify and report on GDPR-relevant Personally Identifiable Information (PII) across multiple sources. The engine will adhere to the GDPR core principles, with a focus on Dutch-specific rules (UAVG), consent management (especially for minors), breach timeline reporting per Autoriteit Persoonsgegevens, and legal basis documentation. )

I want you to:

- implement below plan as it is described 

GDPR CODE SCANNER

Objective
Design and implement a GDPR Scan Engine to identify and report on GDPR-relevant Personally Identifiable Information (PII) across multiple sources. The engine will adhere to the GDPR core principles, with a focus on Dutch-specific rules (UAVG), consent management (especially for minors), breach timeline reporting per Autoriteit Persoonsgegevens, and legal basis documentation.


Stack: Python + TruffleHog / Semgrep + Presidio + Regex/NLP
Requirements:

Multi-language support: Python, JS, Java, Terraform, YAML, etc.
Secrets detection via entropy, regex, and known providers (AWS, Azure, Stripe, etc.)
Custom rule support (e.g., semgrep-rules.yaml or presidio recognizers,if any String to search in code base )
Metadata enrichment: Git blame, commit hash, author
Regional PII tagging (UAVG, BDSG, CNIL, GDPR Article ref.)
False positive suppression (baseline diffing or ignore rules)

---

### 2. Core GDPR Principles (Implementation Guidelines)
- **Lawfulness, Fairness, Transparency**: All scans must log metadata of processing.
- **Purpose Limitation**: Flag data used outside defined scope.
- **Data Minimization**: Highlight unused or excessive data.
- **Accuracy**: Validate if detected data is recent and correct.
- **Storage Limitation**: Detect outdated or stale PII.
- **Integrity & Confidentiality**: Secure data in transit and at rest.
- **Accountability**: Generate audit logs and traceable report links.


 Added GDPR compliance module imports to CodeScanner
✓ Enhanced content scanning with GDPR-specific features
✓ Implemented dedicated functions for DSAR patterns detection
✓ Added consent verification marker scanning
✓ Implemented security patterns scanning (GDPR Art. 32)
✓ Created enhancement function for GDPR data enrichment
✓ Added GDPR compliance scoring and metrics


✓ Successfully implemented GDPR principles scanning for all 7 principles
✓ Enhanced code scanner with specialized pattern detection for each principle
✓ Optimized code scanner performance for large repositories
✓ Added better error handling for scanning timeout issues
✓ Reduced file scanning timeouts from 30 to 20 seconds for faster performance


### 3. Netherlands-Specific GDPR (UAVG) Requirements
- Comply with Dutch rules around BSN, medical records, and employment data.
- Consent flag for minors (<16 years).
- Maintain legal basis documentation (contract, consent, vital interest, etc.).
- Integrate with AP's 72-hour breach notification framework.
- Alert on high-risk PII under Dutch categorization.

OUTPUT : MODERN DESIGN reports WITH logo and  OPTIONS ON GUI to download detailed report with sugestions as : pdf ,html 

Output Format:

{
  "file": "src/auth.py",
  "line": 72,
  "type": "API_KEY",
  "entropy": 4.9,
  "region_flags": ["GDPR-Article5", "UAVG"],
  "context_snippet": "api_key = 'sk_test_****'",
  "commit_info": {
    "author": "vishaal.kumar",
    "commit_id": "a8b91a3"
  }
} 

- Assess potential issues or limitations
- if any old reference remove it and create new 



