"""
Netherlands GDPR (UAVG) Compliance Module

This module provides specialized detection for Netherlands-specific GDPR requirements
under the Dutch UAVG implementation without modifying existing scanner logic.
"""

import re
import streamlit as st
from typing import Dict, List, Any
from utils.i18n import get_text


def detect_nl_violations(content: str) -> List[Dict[str, Any]]:
    """
    Detect Netherlands-specific GDPR violations in content.
    This is a non-intrusive addition to existing scanners.
    """
    findings = []
    lang = st.session_state.get('language', 'en')

    findings.extend(_find_bsn_numbers(content, lang))
    findings.extend(_detect_minor_consent(content, lang))
    findings.extend(_detect_medical_data(content, lang))

    return findings


def _find_bsn_numbers(text: str, lang: str = 'en') -> List[Dict[str, Any]]:
    bsn_contexts = [
        r'\b(?:BSN|Burgerservicenummer|sofi[-\s]?nummer)(?:[:\s-]+)?(\d{9})\b',
        r'\b(?:BSN|Burgerservicenummer|sofi[-\s]?nummer)(?:[:\s-]+)?(\d{3}[-\s]\d{3}[-\s]\d{3})\b',
        r'\b(\d{9})\b'
    ]

    found = []
    for pattern in bsn_contexts:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            bsn = re.sub(r'\D', '',
                         match.group(1) if match.lastindex else match.group(0))
            if _is_valid_bsn(bsn):
                context_text = text[max(0,
                                        match.start() -
                                        50):min(len(text),
                                                match.end() + 50)]
                is_high_risk = any(
                    term in context_text.lower() for term in
                    ['patient', 'klant', 'persoons', 'burger', 'client'])

                if lang == 'nl':
                    description = f"{get_text('netherlands_regulatory.bsn', 'BSN')} gedetecteerd - {get_text('netherlands_regulatory.bsn_requirements', 'speciale verwerking vereist')} volgens {get_text('netherlands_regulatory.bsn_article', 'UAVG artikel 46')}"
                else:
                    description = "Dutch Citizen Service Number (BSN) detected - special handling required under UAVG Article 46"

                found.append({
                    'type': 'BSN',
                    'value': bsn,
                    'risk_level': 'High' if is_high_risk else 'Medium',
                    'gdpr_principle': 'netherlands_specific',
                    'description': description
                })
    return found


def _is_valid_bsn(bsn: str) -> bool:
    if not bsn.isdigit() or len(bsn) != 9:
        return False
    total = 0
    for i in range(9):
        if i == 8:
            total -= int(bsn[i]) * i
        else:
            total += int(bsn[i]) * (9 - i)
    return total % 11 == 0


def _detect_minor_consent(text: str, lang: str = 'en') -> List[Dict[str, Any]]:
    findings = []
    minor_patterns = [
        r'\b(?:leeftijd(?:s)?verificatie|leeftijd(?:s)?check)\b',
        r'\b(?:onder|jonger\s+dan)\s+(?:16|zestien)\s+jaar\b',
        r'\b(?:ouderlijke\s+toestemming|toestemming\s+van\s+ouders)\b',
        r'\b(?:parental\s+consent|age\s+verification)\b'
    ]

    for pattern in minor_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            if lang == 'nl':
                description = f"Verwijzing naar {get_text('netherlands_regulatory.minor_consent', 'toestemming minderjarigen')} - {get_text('netherlands_regulatory.minor_requirements', 'ouderlijke toestemming vereist voor kinderen onder de 16 jaar')} ({get_text('netherlands_regulatory.minor_article', 'UAVG artikel 5')})"
            else:
                description = "References to age verification/parental consent needed for users under 16 (Dutch UAVG)"
            
            findings.append({
                'type': 'MINOR_CONSENT',
                'value': 'Dutch minor consent references found',
                'risk_level': 'Medium',
                'gdpr_principle': 'netherlands_specific',
                'description': description
            })
            break
    return findings


def _detect_medical_data(text: str, lang: str = 'en') -> List[Dict[str, Any]]:
    findings = []
    medical_terms = [
        r'\b(?:medisch(?:e)?|patiënt(?:en)?|diagnos(?:e|tisch)|behandeling|gezondheid(?:s)?)\b',
        r'\b(?:ziekenhuis|huisarts|specialist|UMC|zorg(?:verlener)?)\b',
        r'\b(?:elektronisch\s+patiëntendossier|EPD)\b'
    ]

    for pattern in medical_terms:
        if re.search(pattern, text, re.IGNORECASE):
            context_text = text[:min(500, len(text))]
            is_high_risk = any(
                term in context_text.lower() for term in
                ['privacy', 'persoonlijk', 'vertrouwelijk', 'dossier'])

            if lang == 'nl':
                description = f"{get_text('netherlands_regulatory.medical_data', 'Medische gegevens')} gedetecteerd - {get_text('netherlands_regulatory.medical_requirements', 'aanvullende waarborgen vereist')} volgens {get_text('netherlands_regulatory.medical_article', 'UAVG artikel 30')}"
            else:
                description = "Healthcare data requires additional safeguards under UAVG Article 30"
            
            findings.append({
                'type': 'MEDICAL_DATA',
                'value': 'Dutch healthcare data references found',
                'risk_level': 'High' if is_high_risk else 'Medium',
                'gdpr_principle': 'netherlands_specific',
                'description': description
            })
            break
    return findings
