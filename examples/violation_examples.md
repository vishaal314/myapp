# Document Scanner Violation Examples

## Real-World Examples of Document Violations

### 1. GDPR Principle Violations

#### Lawfulness Violations
```
❌ VIOLATION: "We collect your data for business purposes"
✅ COMPLIANT: "We collect your data based on your consent (Article 6(1)(a))"

❌ VIOLATION: "Personal information is processed automatically"
✅ COMPLIANT: "Personal data is processed based on our legitimate interest (Article 6(1)(f))"
```

#### Data Minimization Violations
```
❌ VIOLATION: Form collecting: name, email, phone, address, age, income, hobbies, preferences
✅ COMPLIANT: Form collecting only: name, email (for newsletter subscription)

❌ VIOLATION: "Please provide all available information about yourself"
✅ COMPLIANT: "Please provide only the information necessary for this service"
```

#### Transparency Violations
```
❌ VIOLATION: No privacy notice, hidden data collection
✅ COMPLIANT: Clear privacy policy explaining data use

❌ VIOLATION: "Data may be used for various purposes"
✅ COMPLIANT: "Data will be used specifically for order processing and delivery"
```

### 2. Netherlands UAVG Violations

#### BSN (Dutch Social Security Number) Violations
```
❌ VIOLATION: "Please enter your BSN: 123456789"
✅ COMPLIANT: "BSN collection authorized under UAVG Article 46 for tax purposes"

❌ VIOLATION: BSN stored without legal mandate
✅ COMPLIANT: BSN processing with explicit legal authorization
```

#### Minor Consent Violations (Under 16)
```
❌ VIOLATION: "Are you over 13? Yes/No" (Dutch age limit is 16)
✅ COMPLIANT: "Are you 16 or older? If not, parental consent required"

❌ VIOLATION: Child data collected without parental verification
✅ COMPLIANT: Parental consent verified before processing child data
```

### 3. EU AI Act Violations

#### Prohibited Practices (Critical)
```
❌ CRITICAL: "Our system uses subliminal advertising techniques"
❌ CRITICAL: "Citizens are scored based on social behavior"
❌ CRITICAL: "Real-time facial recognition in public spaces"
```

#### High-Risk AI Systems
```
❌ HIGH RISK: "AI hiring system evaluates candidates automatically"
✅ COMPLIANT: "AI hiring system with human oversight and bias testing"

❌ HIGH RISK: "Medical AI makes diagnosis decisions"
✅ COMPLIANT: "Medical AI assists doctors with transparent recommendations"
```

#### Transparency Violations
```
❌ VIOLATION: Chatbot without AI disclosure
✅ COMPLIANT: "You are interacting with an AI assistant"

❌ VIOLATION: Automated decisions without explanation
✅ COMPLIANT: "This automated decision was based on: [criteria]"
```

### 4. Special Categories Violations (Article 9)

#### Health Data
```
❌ VIOLATION: "Medical condition: diabetes" (without explicit consent)
✅ COMPLIANT: "Medical data processed with explicit consent for treatment"

❌ VIOLATION: Health data in employment records without justification
✅ COMPLIANT: Health data only for occupational health requirements
```

#### Biometric Data
```
❌ VIOLATION: "Fingerprint scanning for office access" (without legal basis)
✅ COMPLIANT: "Biometric access with explicit consent and security justification"
```

### 5. Document Type-Specific Violations

#### Employment Documents
```
❌ VIOLATION: "Employee monitoring without disclosure"
✅ COMPLIANT: "Employee monitoring disclosed with clear purposes"

❌ VIOLATION: "Background check includes social media monitoring"
✅ COMPLIANT: "Background check limited to relevant criminal history"
```

#### Healthcare Documents
```
❌ VIOLATION: Patient data shared with insurance without consent
✅ COMPLIANT: Patient data shared only with explicit written consent

❌ VIOLATION: "Medical records retained indefinitely"
✅ COMPLIANT: "Medical records retained per legal requirements (7 years)"
```

#### Financial Documents
```
❌ VIOLATION: "Credit decisions made by AI without human review"
✅ COMPLIANT: "Credit decisions include human oversight and appeal process"

❌ VIOLATION: Financial data transferred to third countries without safeguards
✅ COMPLIANT: Financial data transfers protected by Standard Contractual Clauses
```

#### Educational Documents
```
❌ VIOLATION: "Student behavior tracking without parental consent"
✅ COMPLIANT: "Educational monitoring with parental consent and opt-out"

❌ VIOLATION: AI tutoring system without transparency
✅ COMPLIANT: AI tutoring with clear explanation of automated recommendations
```

### 6. Technical Document Violations

#### API Documentation
```
❌ VIOLATION: Example API responses containing real personal data
✅ COMPLIANT: Example responses with anonymized or synthetic data

❌ VIOLATION: Database schema exposing PII field names in documentation
✅ COMPLIANT: Database documentation with privacy-aware field descriptions
```

#### Code Comments
```
❌ VIOLATION: // TODO: Remove John Smith's email john@example.com
✅ COMPLIANT: // TODO: Remove user email from debug output

❌ VIOLATION: Real customer data in code examples
✅ COMPLIANT: Placeholder data in code examples
```

### 7. Data Subject Rights Violations

#### Missing Rights Implementation
```
❌ VIOLATION: No way for users to access their data
✅ COMPLIANT: Self-service data access portal available

❌ VIOLATION: "Data deletion not technically possible"
✅ COMPLIANT: Data deletion process available within 30 days

❌ VIOLATION: No opt-out mechanism for marketing
✅ COMPLIANT: Clear unsubscribe option in all communications
```

### 8. International Transfer Violations

```
❌ VIOLATION: "Data may be processed in any country where we operate"
✅ COMPLIANT: "Data transfers protected by adequacy decisions or appropriate safeguards"

❌ VIOLATION: Cloud storage in non-EU countries without protection
✅ COMPLIANT: Cloud storage with Standard Contractual Clauses and encryption
```

### 9. Breach Notification Violations

```
❌ VIOLATION: "Security incidents are handled internally"
✅ COMPLIANT: "Data breaches reported to authorities within 72 hours"

❌ VIOLATION: No incident response plan documented
✅ COMPLIANT: Detailed breach notification procedures documented
```

## Scanning Results Interpretation

### Critical Findings (Score Impact: -40 points each)
- Prohibited AI practices
- Special category data without legal basis
- International transfers without safeguards

### High Risk Findings (Score Impact: -20 points each)
- Missing essential data subject rights
- High-risk AI systems without compliance
- Security vulnerabilities with personal data

### Medium Risk Findings (Score Impact: -10 points each)
- Incomplete transparency information
- Minor data minimization issues
- Missing technical safeguards

### Low Risk Findings (Score Impact: -5 points each)
- Documentation improvements needed
- Best practice recommendations
- Minor technical issues

## Common Violation Patterns

1. **Copy-paste from templates** without compliance review
2. **Real data in examples** instead of anonymized samples
3. **Outdated consent mechanisms** not meeting current standards
4. **Missing legal basis statements** for data processing
5. **Inadequate data subject rights** implementation
6. **No AI transparency** in automated systems
7. **Insufficient safeguards** for sensitive data
8. **Missing retention policies** and deletion procedures

The Document Scanner analyzes all these patterns and provides specific remediation guidance for each violation found.