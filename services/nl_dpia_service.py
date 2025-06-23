"""
Netherlands DPIA Assessment Service

Comprehensive DPIA implementation compliant with:
- GDPR (General Data Protection Regulation) 
- Dutch UAVG (Dutch GDPR implementation)
- Dutch Police Act (Politiewet)
- Netherlands jurisdiction requirements

Features:
- Complete data collection workflow
- Database storage with PostgreSQL
- Legal compliance validation
- HTML report generation with download links
"""

import uuid
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
import psycopg2
from psycopg2.extras import RealDictCursor
import streamlit as st
import os

class NetherlandsDPIAService:
    """
    Service class for Netherlands DPIA assessment with full compliance.
    """
    
    def __init__(self):
        self.db_url = os.getenv('DATABASE_URL')
        self.init_database()
    
    def init_database(self):
        """Initialize database tables for DPIA assessments."""
        try:
            with psycopg2.connect(self.db_url) as conn:
                with conn.cursor() as cur:
                    # Create DPIA assessments table
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS nl_dpia_assessments (
                            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                            assessment_id VARCHAR(50) UNIQUE NOT NULL,
                            user_id VARCHAR(100) NOT NULL,
                            organization_name VARCHAR(255),
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            status VARCHAR(50) DEFAULT 'draft',
                            compliance_score INTEGER DEFAULT 0,
                            risk_level VARCHAR(20) DEFAULT 'medium',
                            
                            -- Organization Information
                            org_dpo_contact VARCHAR(255),
                            org_industry VARCHAR(100),
                            org_employee_count VARCHAR(50),
                            org_jurisdiction VARCHAR(100) DEFAULT 'Netherlands',
                            org_is_controller BOOLEAN DEFAULT TRUE,
                            org_is_processor BOOLEAN DEFAULT FALSE,
                            
                            -- Processing Description
                            processing_purpose TEXT,
                            processing_description TEXT,
                            data_categories JSONB,
                            data_subjects JSONB,
                            retention_period VARCHAR(100),
                            automated_decisions BOOLEAN DEFAULT FALSE,
                            profiling BOOLEAN DEFAULT FALSE,
                            ai_system_used BOOLEAN DEFAULT FALSE,
                            
                            -- Legal Basis
                            gdpr_legal_basis VARCHAR(100),
                            legitimate_interest_details TEXT,
                            consent_mechanism TEXT,
                            special_categories BOOLEAN DEFAULT FALSE,
                            criminal_data BOOLEAN DEFAULT FALSE,
                            children_data BOOLEAN DEFAULT FALSE,
                            cross_border_transfer BOOLEAN DEFAULT FALSE,
                            adequacy_decision VARCHAR(100),
                            
                            -- Risk Assessment
                            privacy_risks JSONB,
                            breach_likelihood VARCHAR(20) DEFAULT 'low',
                            breach_impact VARCHAR(20) DEFAULT 'low',
                            discrimination_risk VARCHAR(20) DEFAULT 'low',
                            surveillance_concerns BOOLEAN DEFAULT FALSE,
                            vulnerable_groups JSONB,
                            rights_impact JSONB,
                            
                            -- Technical Measures
                            encryption_at_rest BOOLEAN DEFAULT FALSE,
                            encryption_in_transit BOOLEAN DEFAULT FALSE,
                            access_controls JSONB,
                            audit_logging BOOLEAN DEFAULT FALSE,
                            data_minimization BOOLEAN DEFAULT FALSE,
                            pseudonymization BOOLEAN DEFAULT FALSE,
                            anonymization BOOLEAN DEFAULT FALSE,
                            backup_procedures TEXT,
                            incident_response TEXT,
                            staff_training BOOLEAN DEFAULT FALSE,
                            
                            -- Dutch Specific Compliance
                            uavg_compliant BOOLEAN DEFAULT FALSE,
                            dutch_dpa_notification BOOLEAN DEFAULT FALSE,
                            police_act_applicable BOOLEAN DEFAULT FALSE,
                            police_processing_purpose TEXT,
                            bsn_processing BOOLEAN DEFAULT FALSE,
                            dutch_sector_codes JSONB,
                            municipal_processing BOOLEAN DEFAULT FALSE,
                            healthcare_bsn BOOLEAN DEFAULT FALSE,
                            
                            -- Mitigation Measures
                            mitigation_measures JSONB,
                            implementation_timeline VARCHAR(100),
                            responsible_parties JSONB,
                            monitoring_procedures TEXT,
                            review_schedule VARCHAR(100),
                            
                            -- Assessment Results
                            overall_risk_level VARCHAR(20),
                            dpia_required BOOLEAN DEFAULT TRUE,
                            gdpr_score INTEGER DEFAULT 0,
                            uavg_score INTEGER DEFAULT 0,
                            police_act_compliant BOOLEAN DEFAULT FALSE,
                            can_proceed BOOLEAN DEFAULT FALSE,
                            recommendations JSONB,
                            
                            -- Report Generation
                            html_report_generated BOOLEAN DEFAULT FALSE,
                            html_report_url VARCHAR(500),
                            html_report_path VARCHAR(500),
                            report_generated_at TIMESTAMP
                        )
                    """)
                    
                    # Create index for faster queries
                    cur.execute("""
                        CREATE INDEX IF NOT EXISTS idx_nl_dpia_user_id 
                        ON nl_dpia_assessments(user_id)
                    """)
                    
                    cur.execute("""
                        CREATE INDEX IF NOT EXISTS idx_nl_dpia_assessment_id 
                        ON nl_dpia_assessments(assessment_id)
                    """)
                    
                    conn.commit()
                    
        except Exception as e:
            st.error(f"Database initialization error: {str(e)}")
    
    def create_assessment(self, user_id: str, organization_name: str) -> str:
        """Create new DPIA assessment record."""
        assessment_id = f"NL-DPIA-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8]}"
        
        try:
            with psycopg2.connect(self.db_url) as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO nl_dpia_assessments (assessment_id, user_id, organization_name)
                        VALUES (%s, %s, %s)
                        RETURNING id
                    """, (assessment_id, user_id, organization_name))
                    
                    conn.commit()
                    return assessment_id
                    
        except Exception as e:
            st.error(f"Error creating assessment: {str(e)}")
            return None
    
    def update_organization_info(self, assessment_id: str, org_data: Dict[str, Any]) -> bool:
        """Update organization information section."""
        try:
            with psycopg2.connect(self.db_url) as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        UPDATE nl_dpia_assessments 
                        SET org_dpo_contact = %s,
                            org_industry = %s,
                            org_employee_count = %s,
                            org_jurisdiction = %s,
                            org_is_controller = %s,
                            org_is_processor = %s,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE assessment_id = %s
                    """, (
                        org_data.get('dpo_contact'),
                        org_data.get('industry'),
                        org_data.get('employee_count'),
                        org_data.get('jurisdiction', 'Netherlands'),
                        org_data.get('is_controller', True),
                        org_data.get('is_processor', False),
                        assessment_id
                    ))
                    
                    conn.commit()
                    return True
                    
        except Exception as e:
            st.error(f"Error updating organization info: {str(e)}")
            return False
    
    def update_processing_description(self, assessment_id: str, processing_data: Dict[str, Any]) -> bool:
        """Update processing description section."""
        try:
            with psycopg2.connect(self.db_url) as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        UPDATE nl_dpia_assessments 
                        SET processing_purpose = %s,
                            processing_description = %s,
                            data_categories = %s,
                            data_subjects = %s,
                            retention_period = %s,
                            automated_decisions = %s,
                            profiling = %s,
                            ai_system_used = %s,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE assessment_id = %s
                    """, (
                        processing_data.get('purpose'),
                        processing_data.get('description'),
                        json.dumps(processing_data.get('data_categories', [])),
                        json.dumps(processing_data.get('data_subjects', [])),
                        processing_data.get('retention_period'),
                        processing_data.get('automated_decisions', False),
                        processing_data.get('profiling', False),
                        processing_data.get('ai_system_used', False),
                        assessment_id
                    ))
                    
                    conn.commit()
                    return True
                    
        except Exception as e:
            st.error(f"Error updating processing description: {str(e)}")
            return False
    
    def update_legal_basis(self, assessment_id: str, legal_data: Dict[str, Any]) -> bool:
        """Update legal basis section."""
        try:
            with psycopg2.connect(self.db_url) as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        UPDATE nl_dpia_assessments 
                        SET gdpr_legal_basis = %s,
                            legitimate_interest_details = %s,
                            consent_mechanism = %s,
                            special_categories = %s,
                            criminal_data = %s,
                            children_data = %s,
                            cross_border_transfer = %s,
                            adequacy_decision = %s,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE assessment_id = %s
                    """, (
                        legal_data.get('gdpr_basis'),
                        legal_data.get('legitimate_interest'),
                        legal_data.get('consent_mechanism'),
                        legal_data.get('special_categories', False),
                        legal_data.get('criminal_data', False),
                        legal_data.get('children_data', False),
                        legal_data.get('cross_border_transfer', False),
                        legal_data.get('adequacy_decision'),
                        assessment_id
                    ))
                    
                    conn.commit()
                    return True
                    
        except Exception as e:
            st.error(f"Error updating legal basis: {str(e)}")
            return False
    
    def update_risk_assessment(self, assessment_id: str, risk_data: Dict[str, Any]) -> bool:
        """Update risk assessment section."""
        try:
            with psycopg2.connect(self.db_url) as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        UPDATE nl_dpia_assessments 
                        SET privacy_risks = %s,
                            breach_likelihood = %s,
                            breach_impact = %s,
                            discrimination_risk = %s,
                            surveillance_concerns = %s,
                            vulnerable_groups = %s,
                            rights_impact = %s,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE assessment_id = %s
                    """, (
                        json.dumps(risk_data.get('privacy_risks', [])),
                        risk_data.get('breach_likelihood', 'low'),
                        risk_data.get('breach_impact', 'low'),
                        risk_data.get('discrimination_risk', 'low'),
                        risk_data.get('surveillance_concerns', False),
                        json.dumps(risk_data.get('vulnerable_groups', [])),
                        json.dumps(risk_data.get('rights_impact', {})),
                        assessment_id
                    ))
                    
                    conn.commit()
                    return True
                    
        except Exception as e:
            st.error(f"Error updating risk assessment: {str(e)}")
            return False
    
    def update_technical_measures(self, assessment_id: str, tech_data: Dict[str, Any]) -> bool:
        """Update technical and organizational measures section."""
        try:
            with psycopg2.connect(self.db_url) as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        UPDATE nl_dpia_assessments 
                        SET encryption_at_rest = %s,
                            encryption_in_transit = %s,
                            access_controls = %s,
                            audit_logging = %s,
                            data_minimization = %s,
                            pseudonymization = %s,
                            anonymization = %s,
                            backup_procedures = %s,
                            incident_response = %s,
                            staff_training = %s,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE assessment_id = %s
                    """, (
                        tech_data.get('encryption_at_rest', False),
                        tech_data.get('encryption_in_transit', False),
                        json.dumps(tech_data.get('access_controls', [])),
                        tech_data.get('audit_logging', False),
                        tech_data.get('data_minimization', False),
                        tech_data.get('pseudonymization', False),
                        tech_data.get('anonymization', False),
                        tech_data.get('backup_procedures'),
                        tech_data.get('incident_response'),
                        tech_data.get('staff_training', False),
                        assessment_id
                    ))
                    
                    conn.commit()
                    return True
                    
        except Exception as e:
            st.error(f"Error updating technical measures: {str(e)}")
            return False
    
    def update_dutch_compliance(self, assessment_id: str, dutch_data: Dict[str, Any]) -> bool:
        """Update Dutch-specific compliance section."""
        try:
            with psycopg2.connect(self.db_url) as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        UPDATE nl_dpia_assessments 
                        SET uavg_compliant = %s,
                            dutch_dpa_notification = %s,
                            police_act_applicable = %s,
                            police_processing_purpose = %s,
                            bsn_processing = %s,
                            dutch_sector_codes = %s,
                            municipal_processing = %s,
                            healthcare_bsn = %s,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE assessment_id = %s
                    """, (
                        dutch_data.get('uavg_compliant', False),
                        dutch_data.get('dutch_dpa_notification', False),
                        dutch_data.get('police_act_applicable', False),
                        dutch_data.get('police_processing_purpose'),
                        dutch_data.get('bsn_processing', False),
                        json.dumps(dutch_data.get('dutch_sector_codes', [])),
                        dutch_data.get('municipal_processing', False),
                        dutch_data.get('healthcare_bsn', False),
                        assessment_id
                    ))
                    
                    conn.commit()
                    return True
                    
        except Exception as e:
            st.error(f"Error updating Dutch compliance: {str(e)}")
            return False
    
    def update_mitigation_measures(self, assessment_id: str, mitigation_data: Dict[str, Any]) -> bool:
        """Update mitigation measures section."""
        try:
            with psycopg2.connect(self.db_url) as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        UPDATE nl_dpia_assessments 
                        SET mitigation_measures = %s,
                            implementation_timeline = %s,
                            responsible_parties = %s,
                            monitoring_procedures = %s,
                            review_schedule = %s,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE assessment_id = %s
                    """, (
                        json.dumps(mitigation_data.get('measures', [])),
                        mitigation_data.get('implementation_timeline'),
                        json.dumps(mitigation_data.get('responsible_parties', [])),
                        mitigation_data.get('monitoring_procedures'),
                        mitigation_data.get('review_schedule'),
                        assessment_id
                    ))
                    
                    conn.commit()
                    return True
                    
        except Exception as e:
            st.error(f"Error updating mitigation measures: {str(e)}")
            return False
    
    def calculate_compliance_scores(self, assessment_id: str) -> Dict[str, Any]:
        """Calculate comprehensive compliance scores and finalize assessment."""
        try:
            with psycopg2.connect(self.db_url) as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    # Get assessment data
                    cur.execute("""
                        SELECT * FROM nl_dpia_assessments 
                        WHERE assessment_id = %s
                    """, (assessment_id,))
                    
                    assessment = cur.fetchone()
                    if not assessment:
                        return None
                    
                    # Calculate GDPR compliance score
                    gdpr_score = self._calculate_gdpr_score(assessment)
                    
                    # Calculate Dutch UAVG compliance score  
                    uavg_score = self._calculate_uavg_score(assessment)
                    
                    # Calculate overall risk level
                    overall_risk = self._calculate_overall_risk(assessment)
                    
                    # Check Police Act compliance
                    police_act_compliant = self._check_police_act_compliance(assessment)
                    
                    # Generate recommendations
                    recommendations = self._generate_recommendations(assessment, gdpr_score, uavg_score)
                    
                    # Determine if processing can proceed
                    can_proceed = gdpr_score >= 70 and uavg_score >= 70
                    
                    # Update assessment with calculated scores
                    cur.execute("""
                        UPDATE nl_dpia_assessments 
                        SET gdpr_score = %s,
                            uavg_score = %s,
                            overall_risk_level = %s,
                            police_act_compliant = %s,
                            can_proceed = %s,
                            recommendations = %s,
                            compliance_score = %s,
                            risk_level = %s,
                            status = 'completed',
                            updated_at = CURRENT_TIMESTAMP
                        WHERE assessment_id = %s
                    """, (
                        gdpr_score,
                        uavg_score,
                        overall_risk,
                        police_act_compliant,
                        can_proceed,
                        json.dumps(recommendations),
                        min(gdpr_score, uavg_score),
                        overall_risk,
                        assessment_id
                    ))
                    
                    conn.commit()
                    
                    return {
                        'gdpr_score': gdpr_score,
                        'uavg_score': uavg_score,
                        'overall_risk_level': overall_risk,
                        'police_act_compliant': police_act_compliant,
                        'can_proceed': can_proceed,
                        'recommendations': recommendations,
                        'assessment_id': assessment_id
                    }
                    
        except Exception as e:
            st.error(f"Error calculating compliance scores: {str(e)}")
            return None
    
    def _calculate_gdpr_score(self, assessment: Dict) -> int:
        """Calculate GDPR compliance score (0-100)."""
        score = 0
        
        # Legal basis (20 points)
        if assessment.get('gdpr_legal_basis'):
            score += 20
            if 'consent' in assessment.get('gdpr_legal_basis', '').lower() and assessment.get('consent_mechanism'):
                score += 5
        
        # Technical measures (30 points)
        if assessment.get('encryption_at_rest'):
            score += 8
        if assessment.get('encryption_in_transit'):
            score += 8
        if assessment.get('data_minimization'):
            score += 10
        if assessment.get('audit_logging'):
            score += 4
        
        # Organizational measures (25 points)
        if assessment.get('staff_training'):
            score += 10
        if assessment.get('incident_response'):
            score += 8
        if assessment.get('backup_procedures'):
            score += 7
        
        # Privacy by design (15 points)
        if assessment.get('pseudonymization'):
            score += 8
        if assessment.get('anonymization'):
            score += 7
        
        # Rights protection (10 points)
        rights_impact = assessment.get('rights_impact')
        if rights_impact and isinstance(rights_impact, (dict, str)):
            if isinstance(rights_impact, str):
                rights_impact = json.loads(rights_impact) if rights_impact else {}
            
            high_impact_rights = [key for key, value in rights_impact.items() if value in ['high', 'medium']]
            if len(high_impact_rights) <= 2:
                score += 10
            elif len(high_impact_rights) <= 4:
                score += 5
        
        return min(score, 100)
    
    def _calculate_uavg_score(self, assessment: Dict) -> int:
        """Calculate Dutch UAVG compliance score (0-100)."""
        # Start with GDPR score as base
        uavg_score = self._calculate_gdpr_score(assessment)
        
        # Additional Dutch requirements (up to 20 bonus points)
        bonus_points = 0
        
        if assessment.get('uavg_compliant'):
            bonus_points += 10
        
        if assessment.get('dutch_dpa_notification'):
            bonus_points += 5
        
        # BSN processing compliance
        if assessment.get('bsn_processing'):
            if assessment.get('healthcare_bsn') or assessment.get('municipal_processing'):
                bonus_points += 5  # Proper BSN handling
            else:
                bonus_points -= 10  # Improper BSN usage
        
        # Sector-specific compliance
        sector_codes = assessment.get('dutch_sector_codes')
        if sector_codes and isinstance(sector_codes, (str, list)):
            if isinstance(sector_codes, str):
                sector_codes = json.loads(sector_codes) if sector_codes else []
            if len(sector_codes) > 0:
                bonus_points += 3
        
        return min(uavg_score + bonus_points, 100)
    
    def _calculate_overall_risk(self, assessment: Dict) -> str:
        """Calculate overall privacy risk level."""
        risk_factors = []
        
        # High-risk indicators
        if assessment.get('ai_system_used'):
            risk_factors.append('high')
        
        if assessment.get('automated_decisions'):
            risk_factors.append('high')
        
        if assessment.get('special_categories'):
            risk_factors.append('high')
        
        if assessment.get('children_data'):
            risk_factors.append('high')
        
        if assessment.get('bsn_processing'):
            risk_factors.append('medium')
        
        if assessment.get('cross_border_transfer'):
            risk_factors.append('medium')
        
        # Risk assessment scores
        breach_likelihood = assessment.get('breach_likelihood', 'low')
        breach_impact = assessment.get('breach_impact', 'low')
        discrimination_risk = assessment.get('discrimination_risk', 'low')
        
        if breach_likelihood == 'high' or breach_impact == 'high' or discrimination_risk == 'high':
            risk_factors.append('high')
        elif breach_likelihood == 'medium' or breach_impact == 'medium' or discrimination_risk == 'medium':
            risk_factors.append('medium')
        
        # Determine overall risk
        if 'high' in risk_factors and len([r for r in risk_factors if r == 'high']) >= 2:
            return 'high'
        elif 'high' in risk_factors or len([r for r in risk_factors if r == 'medium']) >= 3:
            return 'medium'
        else:
            return 'low'
    
    def _check_police_act_compliance(self, assessment: Dict) -> bool:
        """Check Dutch Police Act compliance."""
        if not assessment.get('police_act_applicable'):
            return True  # Not applicable
        
        # Police Act requirements
        requirements_met = 0
        total_requirements = 4
        
        if assessment.get('police_processing_purpose'):
            requirements_met += 1
        
        if assessment.get('gdpr_legal_basis') in ['Legal obligation (Article 6(1)(c))', 'Public task (Article 6(1)(e))']:
            requirements_met += 1
        
        if assessment.get('audit_logging'):
            requirements_met += 1
        
        if assessment.get('data_minimization'):
            requirements_met += 1
        
        return requirements_met >= total_requirements * 0.75  # 75% compliance threshold
    
    def _generate_recommendations(self, assessment: Dict, gdpr_score: int, uavg_score: int) -> List[Dict]:
        """Generate specific recommendations based on assessment."""
        recommendations = []
        
        # GDPR recommendations
        if gdpr_score < 80:
            if not assessment.get('encryption_at_rest'):
                recommendations.append({
                    'priority': 'high',
                    'category': 'Technical Security',
                    'recommendation': 'Implement encryption at rest for all personal data storage',
                    'legal_basis': 'GDPR Article 32 - Security of processing'
                })
            
            if not assessment.get('data_minimization'):
                recommendations.append({
                    'priority': 'high',
                    'category': 'Data Protection Principles',
                    'recommendation': 'Implement data minimization principles - collect only necessary data',
                    'legal_basis': 'GDPR Article 5(1)(c) - Data minimisation'
                })
            
            if not assessment.get('staff_training'):
                recommendations.append({
                    'priority': 'medium',
                    'category': 'Organizational Measures',
                    'recommendation': 'Establish comprehensive staff training program on data protection',
                    'legal_basis': 'GDPR Article 32(4) - Staff awareness'
                })
        
        # Dutch UAVG recommendations
        if uavg_score < 80:
            if not assessment.get('uavg_compliant'):
                recommendations.append({
                    'priority': 'high',
                    'category': 'Legal Compliance',
                    'recommendation': 'Ensure full compliance with Dutch UAVG requirements and local data protection authority guidance',
                    'legal_basis': 'Dutch UAVG (GDPR Implementation Act)'
                })
            
            if assessment.get('bsn_processing') and not (assessment.get('healthcare_bsn') or assessment.get('municipal_processing')):
                recommendations.append({
                    'priority': 'critical',
                    'category': 'Dutch Legal Requirements',
                    'recommendation': 'BSN processing requires specific legal authorization - review necessity and legal basis',
                    'legal_basis': 'Dutch Personal Records Database Act (GBA/BRP)'
                })
        
        # Police Act recommendations
        if assessment.get('police_act_applicable') and not self._check_police_act_compliance(assessment):
            recommendations.append({
                'priority': 'high',
                'category': 'Law Enforcement Compliance',
                'recommendation': 'Ensure compliance with Dutch Police Act requirements for law enforcement data processing',
                'legal_basis': 'Dutch Police Act (Politiewet) 2012'
            })
        
        # High-risk processing recommendations
        if assessment.get('ai_system_used'):
            recommendations.append({
                'priority': 'high',
                'category': 'AI Governance',
                'recommendation': 'Implement AI governance framework with bias testing and explainability measures',
                'legal_basis': 'EU AI Act (upcoming) and GDPR Article 22'
            })
        
        return recommendations
    
    def get_assessment(self, assessment_id: str) -> Optional[Dict]:
        """Retrieve complete assessment data."""
        try:
            with psycopg2.connect(self.db_url) as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute("""
                        SELECT * FROM nl_dpia_assessments 
                        WHERE assessment_id = %s
                    """, (assessment_id,))
                    
                    result = cur.fetchone()
                    return dict(result) if result else None
                    
        except Exception as e:
            st.error(f"Error retrieving assessment: {str(e)}")
            return None
    
    def get_user_assessments(self, user_id: str) -> List[Dict]:
        """Get all assessments for a user."""
        try:
            with psycopg2.connect(self.db_url) as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute("""
                        SELECT assessment_id, organization_name, created_at, status, 
                               compliance_score, risk_level, can_proceed
                        FROM nl_dpia_assessments 
                        WHERE user_id = %s
                        ORDER BY created_at DESC
                    """, (user_id,))
                    
                    results = cur.fetchall()
                    return [dict(row) for row in results]
                    
        except Exception as e:
            st.error(f"Error retrieving user assessments: {str(e)}")
            return []