"""
DPIA Scanner - Data Protection Impact Assessment Scanner

This module provides scanning capabilities for performing Data Protection Impact Assessments
as required by Article 35 of the GDPR. The scanner evaluates various aspects of data processing
activities to identify high-risk operations that would require a formal DPIA.
"""

import os
import json
import uuid
import hashlib
import streamlit as st
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
import pandas as pd

# Import internal dependencies
from utils.i18n import get_text, _

class DPIAScanner:
    """
    DPIA Scanner implements a comprehensive Data Protection Impact Assessment scanning solution.
    It helps organizations identify when a DPIA is required and what aspects need special attention.
    """
    
    def __init__(self, language='en'):
        """
        Initialize the DPIA scanner.
        
        Args:
            language: The language code to use for reports ('en' or 'nl')
        """
        self.language = language
        self.scan_id = str(uuid.uuid4())
        self.assessment_categories = self._get_assessment_categories()
        self.risk_thresholds = {
            'high': 7,
            'medium': 4,
            'low': 0
        }
        
    def _get_assessment_categories(self) -> Dict[str, Dict[str, Any]]:
        """Get the DPIA assessment categories based on current language."""
        # These are the standard categories defined in Article 35 of GDPR and 
        # guidelines from the Article 29 Working Party
        if self.language == 'nl':
            return {
                "data_category": {
                    "name": "Gegevenscategorieën",
                    "description": "Type persoonsgegevens dat wordt verwerkt",
                    "questions": [
                        "Worden er gevoelige/bijzondere gegevens verwerkt?",
                        "Worden gegevens van kwetsbare personen verwerkt?",
                        "Worden er gegevens van kinderen verwerkt?",
                        "Worden er gegevens op grote schaal verwerkt?",
                        "Worden biometrische of genetische gegevens verwerkt?"
                    ]
                },
                "processing_activity": {
                    "name": "Verwerkingsactiviteiten",
                    "description": "Aard van de gegevensverwerkingsactiviteiten",
                    "questions": [
                        "Vindt er geautomatiseerde besluitvorming plaats?",
                        "Vindt er stelselmatige en grootschalige monitoring plaats?",
                        "Worden er innovatieve technologieën of organisatorische oplossingen gebruikt?",
                        "Vindt er profilering plaats?",
                        "Worden gegevens samengevoegd uit meerdere bronnen?"
                    ]
                },
                "rights_impact": {
                    "name": "Rechten en Vrijheden",
                    "description": "Impact op rechten en vrijheden van betrokkenen",
                    "questions": [
                        "Kan de verwerking leiden tot discriminatie?",
                        "Kan de verwerking leiden tot financiële schade?",
                        "Kan de verwerking leiden tot reputatieschade?",
                        "Kan de verwerking leiden tot fysieke schade?",
                        "Worden betrokkenen beperkt in het uitoefenen van hun rechten?"
                    ]
                },
                "transfer_sharing": {
                    "name": "Gegevensdeling & Overdracht",
                    "description": "Delen en overdragen van gegevens",
                    "questions": [
                        "Worden gegevens buiten de EU/EER overgedragen?",
                        "Worden gegevens gedeeld met meerdere verwerkers?",
                        "Worden gegevens gedeeld met derde partijen?",
                        "Is er sprake van internationale gegevensuitwisseling?",
                        "Worden gegevens gepubliceerd of openbaar gemaakt?"
                    ]
                },
                "security_measures": {
                    "name": "Beveiligingsmaatregelen",
                    "description": "Beveiligingsmaatregelen en controlemechanismen",
                    "questions": [
                        "Zijn er adequate toegangscontroles geïmplementeerd?",
                        "Worden gegevens versleuteld (zowel in rust als tijdens overdracht)?",
                        "Is er een procedure voor het melden van datalekken?",
                        "Zijn er maatregelen genomen om data minimalisatie te garanderen?",
                        "Worden regelmatig beveiligingsaudits uitgevoerd?"
                    ]
                }
            }
        else:  # English default
            return {
                "data_category": {
                    "name": "Data Categories",
                    "description": "Type of personal data being processed",
                    "questions": [
                        "Is sensitive/special category data processed?",
                        "Is data of vulnerable persons processed?",
                        "Is children's data processed?",
                        "Is data processed on a large scale?",
                        "Are biometric or genetic data processed?"
                    ]
                },
                "processing_activity": {
                    "name": "Processing Activities",
                    "description": "Nature of data processing activities",
                    "questions": [
                        "Is there automated decision-making?",
                        "Is there systematic and extensive monitoring?",
                        "Are innovative technologies or organizational solutions used?",
                        "Is profiling taking place?",
                        "Is data combined from multiple sources?"
                    ]
                },
                "rights_impact": {
                    "name": "Rights and Freedoms",
                    "description": "Impact on rights and freedoms of data subjects",
                    "questions": [
                        "Could processing lead to discrimination?",
                        "Could processing lead to financial loss?",
                        "Could processing lead to reputational damage?",
                        "Could processing lead to physical harm?",
                        "Are data subjects restricted in exercising their rights?"
                    ]
                },
                "transfer_sharing": {
                    "name": "Data Sharing & Transfer",
                    "description": "Sharing and transferring of data",
                    "questions": [
                        "Is data transferred outside the EU/EEA?",
                        "Is data shared with multiple processors?",
                        "Is data shared with third parties?",
                        "Is there international data exchange?",
                        "Is data published or made publicly available?"
                    ]
                },
                "security_measures": {
                    "name": "Security Measures",
                    "description": "Security measures and control mechanisms",
                    "questions": [
                        "Are adequate access controls implemented?",
                        "Is data encrypted (both at rest and in transit)?",
                        "Is there a data breach notification procedure?",
                        "Are measures in place to ensure data minimization?",
                        "Are security audits performed regularly?"
                    ]
                }
            }

    def perform_assessment(self, answers: Dict[str, List[int]]) -> Dict[str, Any]:
        """
        Perform a DPIA assessment based on provided answers.
        
        Args:
            answers: Dictionary mapping category names to lists of answer values (0-2)
                    0 = No, 1 = Partially, 2 = Yes
        
        Returns:
            Assessment results including risk scores and recommendations
        """
        # Calculate scores for each category and overall
        category_scores = {}
        total_score = 0
        high_risk_count = 0
        medium_risk_count = 0
        low_risk_count = 0
        total_questions = 0
        
        for category, answer_values in answers.items():
            if category not in self.assessment_categories:
                continue
                
            # Calculate category score (sum of all answers in category)
            category_score = sum(answer_values)
            max_possible = len(answer_values) * 2  # Max points per question is 2
            percentage = (category_score / max_possible) * 10  # Convert to 0-10 scale
            
            # Determine risk level for category
            if percentage >= self.risk_thresholds['high']:
                risk_level = "High"
                high_risk_count += 1
            elif percentage >= self.risk_thresholds['medium']:
                risk_level = "Medium"
                medium_risk_count += 1
            else:
                risk_level = "Low"
                low_risk_count += 1
            
            category_scores[category] = {
                "score": category_score,
                "max_possible": max_possible,
                "percentage": percentage,
                "risk_level": risk_level
            }
            
            total_score += category_score
            total_questions += len(answer_values)
        
        # Calculate overall risk score
        max_total = total_questions * 2
        overall_percentage = (total_score / max_total) * 10 if max_total > 0 else 0
        
        if overall_percentage >= self.risk_thresholds['high']:
            overall_risk = "High"
        elif overall_percentage >= self.risk_thresholds['medium']:
            overall_risk = "Medium"
        else:
            overall_risk = "Low"
            
        # Generate recommendations based on risk levels
        recommendations = self._generate_recommendations(category_scores)
        
        # Create results object
        results = {
            "scan_id": self.scan_id,
            "scan_type": "DPIA",
            "timestamp": datetime.now().isoformat(),
            "overall_score": total_score,
            "overall_percentage": overall_percentage,
            "overall_risk_level": overall_risk,
            "category_scores": category_scores,
            "high_risk_count": high_risk_count,
            "medium_risk_count": medium_risk_count,
            "low_risk_count": low_risk_count,
            "recommendations": recommendations,
            "dpia_required": overall_risk == "High" or high_risk_count >= 2,
            "language": self.language
        }
        
        return results
        
    def _generate_recommendations(self, category_scores: Dict[str, Dict[str, Any]]) -> List[Dict[str, str]]:
        """Generate recommendations based on risk scores for each category."""
        recommendations = []
        
        # Add general recommendation about DPIA requirement
        if any(scores["risk_level"] == "High" for _, scores in category_scores.items()):
            if self.language == 'nl':
                recommendations.append({
                    "category": "Algemeen",
                    "severity": "High",
                    "description": "Een formele DPIA is vereist volgens Artikel 35 van de AVG vanwege hoge risico's."
                })
            else:
                recommendations.append({
                    "category": "General",
                    "severity": "High",
                    "description": "A formal DPIA is required under Article 35 of GDPR due to high-risk processing."
                })
        
        # Add category-specific recommendations
        for category, scores in category_scores.items():
            # Skip if risk level is low
            if scores["risk_level"] == "Low":
                continue
                
            # Generate recommendation text based on category and language
            if self.language == 'nl':
                if category == "data_category" and scores["risk_level"] == "High":
                    recommendations.append({
                        "category": self.assessment_categories[category]["name"],
                        "severity": scores["risk_level"],
                        "description": "Evalueer de noodzaak voor het verwerken van gevoelige/bijzondere gegevenscategorieën en implementeer aanvullende waarborgen."
                    })
                elif category == "processing_activity" and scores["risk_level"] in ["Medium", "High"]:
                    recommendations.append({
                        "category": self.assessment_categories[category]["name"],
                        "severity": scores["risk_level"],
                        "description": "Documenteer duidelijk de rechtsgrond voor elke verwerkingsactiviteit en beoordeel of geautomatiseerde besluitvorming echt noodzakelijk is."
                    })
                elif category == "rights_impact" and scores["risk_level"] in ["Medium", "High"]:
                    recommendations.append({
                        "category": self.assessment_categories[category]["name"],
                        "severity": scores["risk_level"],
                        "description": "Voer een grondige impactanalyse uit en implementeer maatregelen om de impact op de rechten en vrijheden van betrokkenen te beperken."
                    })
                elif category == "transfer_sharing" and scores["risk_level"] in ["Medium", "High"]:
                    recommendations.append({
                        "category": self.assessment_categories[category]["name"],
                        "severity": scores["risk_level"],
                        "description": "Evalueer alle internationale gegevensoverdrachten en zorg voor adequate juridische kaders (zoals standaardcontractbepalingen)."
                    })
                elif category == "security_measures" and scores["risk_level"] in ["Medium", "High"]:
                    recommendations.append({
                        "category": self.assessment_categories[category]["name"],
                        "severity": scores["risk_level"],
                        "description": "Versterk beveiligingsmaatregelen met state-of-the-art encryptie, gedocumenteerde toegangscontroles en regelmatige beveiligingsaudits."
                    })
            else:  # English recommendations
                if category == "data_category" and scores["risk_level"] == "High":
                    recommendations.append({
                        "category": self.assessment_categories[category]["name"],
                        "severity": scores["risk_level"],
                        "description": "Evaluate the necessity of processing sensitive/special categories of data and implement additional safeguards."
                    })
                elif category == "processing_activity" and scores["risk_level"] in ["Medium", "High"]:
                    recommendations.append({
                        "category": self.assessment_categories[category]["name"],
                        "severity": scores["risk_level"],
                        "description": "Clearly document the legal basis for each processing activity and evaluate if automated decision-making is truly necessary."
                    })
                elif category == "rights_impact" and scores["risk_level"] in ["Medium", "High"]:
                    recommendations.append({
                        "category": self.assessment_categories[category]["name"],
                        "severity": scores["risk_level"],
                        "description": "Conduct a thorough impact assessment and implement measures to mitigate impact on data subject rights and freedoms."
                    })
                elif category == "transfer_sharing" and scores["risk_level"] in ["Medium", "High"]:
                    recommendations.append({
                        "category": self.assessment_categories[category]["name"],
                        "severity": scores["risk_level"],
                        "description": "Evaluate all international data transfers and ensure adequate legal frameworks (such as standard contractual clauses)."
                    })
                elif category == "security_measures" and scores["risk_level"] in ["Medium", "High"]:
                    recommendations.append({
                        "category": self.assessment_categories[category]["name"],
                        "severity": scores["risk_level"],
                        "description": "Strengthen security measures with state-of-the-art encryption, documented access controls, and regular security audits."
                    })
        
        return recommendations
        
    def get_questions(self) -> Dict[str, Dict[str, Any]]:
        """Get all assessment questions grouped by category."""
        return self.assessment_categories

def generate_dpia_report(assessment_results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate a comprehensive DPIA assessment report in a format suitable for PDF generation.
    
    Args:
        assessment_results: Results from a DPIA assessment
        
    Returns:
        Report data ready for the PDF generator
    """
    language = assessment_results.get('language', 'en')
    
    # Create report data structure
    report_data = {
        "scan_id": assessment_results["scan_id"],
        "scan_type": "DPIA",
        "timestamp": assessment_results["timestamp"],
        "total_pii_found": 0,  # Not applicable for DPIA
        "high_risk_count": assessment_results["high_risk_count"],
        "medium_risk_count": assessment_results["medium_risk_count"],
        "low_risk_count": assessment_results["low_risk_count"],
        "region": "EU",  # GDPR is EU-specific
        "risk_level": assessment_results["overall_risk_level"],
        "dpia_required": assessment_results["dpia_required"],
        "dpia_score": assessment_results["overall_percentage"],
        "findings": [],
        "recommendations": assessment_results["recommendations"],
        "category_scores": assessment_results["category_scores"],
        "pii_types": {}  # Not applicable for DPIA
    }
    
    # Add category findings
    for category, scores in assessment_results["category_scores"].items():
        # Create a finding for each category with elevated risk
        if scores["risk_level"] != "Low":
            # Localize the finding description
            if language == 'nl':
                description = f"Risicoscore voor {category}: {scores['percentage']:.1f}/10"
                detail = f"Deze categorie vertoont een {scores['risk_level']} risico en vereist aandacht."
            else:
                description = f"Risk score for {category}: {scores['percentage']:.1f}/10"
                detail = f"This category shows {scores['risk_level']} risk and requires attention."
                
            report_data["findings"].append({
                "type": "DPIA Risk",
                "severity": scores["risk_level"],
                "description": description,
                "details": detail,
                "category": category
            })
    
    # Add a special finding about DPIA requirement
    if assessment_results["dpia_required"]:
        if language == 'nl':
            report_data["findings"].append({
                "type": "DPIA Vereist",
                "severity": "High",
                "description": "Een formele DPIA is vereist onder Artikel 35 van de AVG",
                "details": "De risicoanalyse geeft aan dat er een hoog risico is voor de rechten en vrijheden van betrokkenen, wat een formele DPIA vereist.",
                "category": "General"
            })
        else:
            report_data["findings"].append({
                "type": "DPIA Required",
                "severity": "High",
                "description": "A formal DPIA is required under Article 35 of GDPR",
                "details": "Risk analysis indicates high risk to rights and freedoms of data subjects, requiring a formal DPIA.",
                "category": "General"
            })
    
    # Add global summary with risk levels for each category
    if language == 'nl':
        summary = {
            "Algemeen risico": assessment_results["overall_risk_level"],
            "DPIA vereist": "Ja" if assessment_results["dpia_required"] else "Nee",
            "Totale risicoscore": f"{assessment_results['overall_percentage']:.1f}/10"
        }
    else:
        summary = {
            "Overall risk": assessment_results["overall_risk_level"],
            "DPIA required": "Yes" if assessment_results["dpia_required"] else "No",
            "Total risk score": f"{assessment_results['overall_percentage']:.1f}/10"
        }
        
    report_data["summary"] = summary
    report_data["risk_levels"] = {
        "High": assessment_results["high_risk_count"],
        "Medium": assessment_results["medium_risk_count"],
        "Low": assessment_results["low_risk_count"]
    }
    
    return report_data