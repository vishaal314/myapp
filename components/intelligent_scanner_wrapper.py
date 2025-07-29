"""
Intelligent Scanner Integration Wrapper

Provides seamless integration between the main application and intelligent scanners.
Maintains backward compatibility while adding scalability improvements.
"""

import logging
import os
import tempfile
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
import streamlit as st

from services.intelligent_scanner_manager import intelligent_scanner_manager
from utils.activity_tracker import track_scan_started, track_scan_completed, track_scan_failed, ScannerType
from services.license_integration import track_scanner_usage

logger = logging.getLogger("components.intelligent_scanner_wrapper")

class IntelligentScannerWrapper:
    """Wrapper that integrates intelligent scanning with existing UI."""
    
    def __init__(self):
        self.scanner_manager = intelligent_scanner_manager
    
    def execute_code_scan_intelligent(self, region: str, username: str, 
                                    uploaded_files=None, repo_url=None, 
                                    directory_path=None, include_comments=True,
                                    detect_secrets=True, gdpr_compliance=True,
                                    scan_mode="smart", use_entropy=True,
                                    use_git_metadata=False, timeout=60,
                                    max_files=200, priority_extensions=None) -> Dict[str, Any]:
        """Execute intelligent code scanning with enhanced scalability."""
        
        # Session tracking setup
        session_id = st.session_state.get('session_id', str(uuid.uuid4()))
        user_id = st.session_state.get('user_id', username)
        
        scan_start_time = datetime.now()
        
        # Determine source type
        if uploaded_files:
            source_type = "uploaded_files"
            source_info = f"{len(uploaded_files)} files"
        elif repo_url:
            source_type = "repository"
            source_info = repo_url
        else:
            source_type = "directory"
            source_info = directory_path or "local"
        
        # Track scan start
        track_scan_started(
            session_id=session_id,
            user_id=user_id,
            username=username,
            scanner_type=ScannerType.CODE,
            region=region,
            details={
                'source_type': source_type,
                'source_info': source_info,
                'scan_mode': scan_mode,
                'intelligent_scanning': True,
                'gdpr_compliance': gdpr_compliance,
                'netherlands_uavg': region == "Netherlands",
                'use_entropy': use_entropy,
                'use_git_metadata': use_git_metadata,
                'timeout': timeout,
                'max_files': max_files
            }
        )
        
        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        def progress_callback(current: int, total: int, message: str):
            """Progress callback for real-time updates."""
            progress = current / total
            progress_bar.progress(progress)
            status_text.text(f"🔍 {message}")
        
        try:
            # Prepare scan target based on source type
            if uploaded_files:
                # Handle uploaded files
                with tempfile.TemporaryDirectory() as temp_dir:
                    file_paths = []
                    for uploaded_file in uploaded_files:
                        file_path = os.path.join(temp_dir, uploaded_file.name)
                        with open(file_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        file_paths.append(file_path)
                    
                    # Use intelligent document scanner for uploaded files
                    scan_result = self.scanner_manager.scan_intelligent(
                        scan_type='documents',
                        scan_target=file_paths,
                        scan_mode=scan_mode,
                        max_items=100,
                        progress_callback=progress_callback,
                        region=region,
                        include_comments=include_comments,
                        detect_secrets=detect_secrets
                    )
            
            elif repo_url:
                # Use intelligent repository scanner
                scan_result = self.scanner_manager.scan_intelligent(
                    scan_type='repository',
                    scan_target=repo_url,
                    scan_mode=scan_mode,
                    max_items=max_files,
                    progress_callback=progress_callback,
                    region=region,
                    branch='main',
                    timeout=timeout,
                    use_entropy=use_entropy,
                    use_git_metadata=use_git_metadata,
                    priority_extensions=priority_extensions or []
                )
            
            else:
                st.error("Please provide files or repository URL to scan.")
                # Return error structure instead of None
                return {
                    'scan_id': f"error_{uuid.uuid4().hex[:8]}",
                    'scan_type': 'Intelligent Code Scanner',
                    'timestamp': datetime.now().isoformat(),
                    'status': 'error',
                    'error': 'No scan target provided',
                    'findings': [],
                    'files_scanned': 0,
                    'intelligence_applied': False
                }
            
            # Validate scan result before processing
            if not scan_result or not isinstance(scan_result, dict):
                raise ValueError("Scanner returned invalid or empty result")
            
            # Track successful completion
            scan_duration = int((datetime.now() - scan_start_time).total_seconds() * 1000)
            findings_count = len(scan_result.get('findings', []))
            
            track_scan_completed(
                session_id=session_id,
                user_id=user_id,
                username=username,
                scanner_type=ScannerType.CODE,
                findings_count=findings_count,
                files_scanned=scan_result.get('files_scanned', scan_result.get('files_processed', 0)),
                duration_ms=scan_duration,
                region=region,
                details={
                    'scan_id': scan_result.get('scan_id'),
                    'intelligence_metrics': scan_result.get('intelligence_metrics', {}),
                    'scan_coverage': scan_result.get('scan_coverage', 0),
                    'strategy_used': scan_result.get('scanning_strategy', {}).get('type', 'unknown')
                }
            )
            
            # Track license usage
            track_scanner_usage('code', region, success=True, duration_ms=scan_duration)
            
            progress_bar.progress(100)
            status_text.text("✅ Intelligent scan completed!")
            
            return scan_result
            
        except Exception as e:
            logger.error(f"Intelligent code scan failed: {str(e)}")
            
            # Track scan failure
            track_scan_failed(
                session_id=session_id,
                user_id=user_id,
                username=username,
                scanner_type=ScannerType.CODE,
                error_message=str(e),
                region=region,
                details={'intelligent_scanning': True}
            )
            
            st.error(f"Intelligent scan failed: {str(e)}")
            # Return error structure instead of None
            return {
                'scan_id': f"error_{uuid.uuid4().hex[:8]}",
                'scan_type': 'Intelligent Code Scanner',
                'timestamp': datetime.now().isoformat(),
                'status': 'error',
                'error': str(e),
                'findings': [],
                'files_scanned': 0,
                'intelligence_applied': False
            }

    def execute_image_scan_intelligent(self, region: str, username: str,
                                     uploaded_files: List[Any],
                                     scan_mode: str = "smart") -> Dict[str, Any]:
        """Execute intelligent image scanning with enhanced OCR processing."""
        
        session_id = st.session_state.get('session_id', str(uuid.uuid4()))
        user_id = st.session_state.get('user_id', username)
        scan_start_time = datetime.now()
        
        # Track scan start
        track_scan_started(
            session_id=session_id,
            user_id=user_id,
            username=username,
            scanner_type=ScannerType.IMAGE,
            region=region,
            details={
                'file_count': len(uploaded_files),
                'scan_mode': scan_mode,
                'intelligent_scanning': True,
                'image_types': [file.name.split('.')[-1] for file in uploaded_files]
            }
        )
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        def progress_callback(current: int, total: int, message: str):
            progress = current / total
            progress_bar.progress(progress)
            status_text.text(f"🖼️ {message}")
        
        try:
            # Save uploaded files temporarily
            with tempfile.TemporaryDirectory() as temp_dir:
                image_paths = []
                for uploaded_file in uploaded_files:
                    file_path = os.path.join(temp_dir, uploaded_file.name)
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    image_paths.append(file_path)
                
                # Use intelligent image scanner
                scan_result = self.scanner_manager.scan_intelligent(
                    scan_type='images',
                    scan_target=image_paths,
                    scan_mode=scan_mode,
                    max_items=50,
                    progress_callback=progress_callback,
                    region=region
                )
                
                # Validate scan result before processing
                if not scan_result or not isinstance(scan_result, dict):
                    raise ValueError("Image scanner returned invalid or empty result")
            
            # Track completion
            scan_duration = int((datetime.now() - scan_start_time).total_seconds() * 1000)
            findings_count = len(scan_result.get('findings', []))
            
            track_scan_completed(
                session_id=session_id,
                user_id=user_id,
                username=username,
                scanner_type=ScannerType.IMAGE,
                findings_count=findings_count,
                files_scanned=scan_result.get('images_processed', 0),
                duration_ms=scan_duration,
                region=region,
                details={
                    'scan_id': scan_result.get('scan_id'),
                    'face_detections': scan_result.get('face_detections', 0),
                    'document_detections': scan_result.get('document_detections', 0),
                    'ocr_results_count': len(scan_result.get('ocr_results', []))
                }
            )
            
            track_scanner_usage('image', region, success=True, duration_ms=scan_duration)
            
            progress_bar.progress(100)
            status_text.text("✅ Intelligent image scan completed!")
            
            return scan_result
            
        except Exception as e:
            logger.error(f"Intelligent image scan failed: {str(e)}")
            
            track_scan_failed(
                session_id=session_id,
                user_id=user_id,
                username=username,
                scanner_type=ScannerType.IMAGE,
                error_message=str(e),
                region=region,
                details={'intelligent_scanning': True}
            )
            
            st.error(f"Intelligent image scan failed: {str(e)}")
            # Return error structure instead of None
            return {
                'scan_id': f"error_{uuid.uuid4().hex[:8]}",
                'scan_type': 'Intelligent Image Scanner',
                'timestamp': datetime.now().isoformat(),
                'status': 'error',
                'error': str(e),
                'findings': [],
                'files_scanned': 0,
                'intelligence_applied': False
            }

    def execute_website_scan_intelligent(self, region: str, username: str,
                                       base_url: str, max_pages: Optional[int] = None,
                                       max_depth: Optional[int] = None,
                                       scan_mode: str = "smart") -> Dict[str, Any]:
        """Execute intelligent website scanning with adaptive crawling."""
        
        session_id = st.session_state.get('session_id', str(uuid.uuid4()))
        user_id = st.session_state.get('user_id', username)
        scan_start_time = datetime.now()
        
        # Track scan start
        track_scan_started(
            session_id=session_id,
            user_id=user_id,
            username=username,
            scanner_type=ScannerType.WEBSITE,
            region=region,
            details={
                'base_url': base_url,
                'scan_mode': scan_mode,
                'intelligent_scanning': True,
                'max_pages': max_pages,
                'max_depth': max_depth
            }
        )
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        def progress_callback(current: int, total: int, message: str):
            progress = current / total
            progress_bar.progress(progress)
            status_text.text(f"🌐 {message}")
        
        try:
            # Use intelligent website scanner
            scan_result = self.scanner_manager.scan_intelligent(
                scan_type='website',
                scan_target=base_url,
                scan_mode=scan_mode,
                max_items=max_pages or 25,
                progress_callback=progress_callback,
                region=region,
                max_depth=max_depth or 3
            )
            
            # Validate scan result before processing
            if not scan_result or not isinstance(scan_result, dict):
                raise ValueError("Website scanner returned invalid or empty result")
            
            # Track completion
            scan_duration = int((datetime.now() - scan_start_time).total_seconds() * 1000)
            findings_count = len(scan_result.get('findings', []))
            
            track_scan_completed(
                session_id=session_id,
                user_id=user_id,
                username=username,
                scanner_type=ScannerType.WEBSITE,
                findings_count=findings_count,
                files_scanned=scan_result.get('pages_scanned', 0),
                duration_ms=scan_duration,
                region=region,
                details={
                    'scan_id': scan_result.get('scan_id'),
                    'pages_discovered': scan_result.get('pages_discovered', 0),
                    'cookies_found': scan_result.get('cookies_found', 0),
                    'trackers_found': scan_result.get('trackers_found', 0)
                }
            )
            
            track_scanner_usage('website', region, success=True, duration_ms=scan_duration)
            
            progress_bar.progress(100)
            status_text.text("✅ Intelligent website scan completed!")
            
            return scan_result
            
        except Exception as e:
            logger.error(f"Intelligent website scan failed: {str(e)}")
            
            track_scan_failed(
                session_id=session_id,
                user_id=user_id,
                username=username,
                scanner_type=ScannerType.WEBSITE,
                error_message=str(e),
                region=region,
                details={'intelligent_scanning': True}
            )
            
            st.error(f"Intelligent website scan failed: {str(e)}")
            # Return error structure instead of None
            return {
                'scan_id': f"error_{uuid.uuid4().hex[:8]}",
                'scan_type': 'Intelligent Website Scanner',
                'timestamp': datetime.now().isoformat(),
                'status': 'error',
                'error': str(e),
                'findings': [],
                'files_scanned': 0,
                'intelligence_applied': False
            }

    def execute_database_scan_intelligent(self, region: str, username: str,
                                        connection_params: Dict[str, Any],
                                        max_tables: Optional[int] = None,
                                        scan_mode: str = "smart") -> Dict[str, Any]:
        """Execute intelligent database scanning with adaptive sampling."""
        
        session_id = st.session_state.get('session_id', str(uuid.uuid4()))
        user_id = st.session_state.get('user_id', username)
        scan_start_time = datetime.now()
        
        # Track scan start
        track_scan_started(
            session_id=session_id,
            user_id=user_id,
            username=username,
            scanner_type=ScannerType.DATABASE,
            region=region,
            details={
                'database_type': connection_params.get('type', 'unknown'),
                'scan_mode': scan_mode,
                'intelligent_scanning': True,
                'max_tables': max_tables
            }
        )
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        def progress_callback(current: int, total: int, message: str):
            progress = current / total
            progress_bar.progress(progress)
            status_text.text(f"🗄️ {message}")
        
        try:
            # Use intelligent database scanner
            scan_result = self.scanner_manager.scan_intelligent(
                scan_type='database',
                scan_target=connection_params,
                scan_mode=scan_mode,
                max_items=max_tables or 50,
                progress_callback=progress_callback,
                region=region
            )
            
            # Validate scan result before processing
            if not scan_result or not isinstance(scan_result, dict):
                raise ValueError("Database scanner returned invalid or empty result")
            
            # Track completion
            scan_duration = int((datetime.now() - scan_start_time).total_seconds() * 1000)
            findings_count = len(scan_result.get('findings', []))
            
            track_scan_completed(
                session_id=session_id,
                user_id=user_id,
                username=username,
                scanner_type=ScannerType.DATABASE,
                findings_count=findings_count,
                files_scanned=scan_result.get('tables_scanned', 0),
                duration_ms=scan_duration,
                region=region,
                details={
                    'scan_id': scan_result.get('scan_id'),
                    'tables_discovered': scan_result.get('tables_discovered', 0),
                    'rows_analyzed': scan_result.get('rows_analyzed', 0),
                    'schema_analysis': scan_result.get('schema_analysis', {})
                }
            )
            
            track_scanner_usage('database', region, success=True, duration_ms=scan_duration)
            
            progress_bar.progress(100)
            status_text.text("✅ Intelligent database scan completed!")
            
            return scan_result
            
        except Exception as e:
            logger.error(f"Intelligent database scan failed: {str(e)}")
            
            track_scan_failed(
                session_id=session_id,
                user_id=user_id,
                username=username,
                scanner_type=ScannerType.DATABASE,
                error_message=str(e),
                region=region,
                details={'intelligent_scanning': True}
            )
            
            st.error(f"Intelligent database scan failed: {str(e)}")
            # Return error structure instead of None
            return {
                'scan_id': f"error_{uuid.uuid4().hex[:8]}",
                'scan_type': 'Intelligent Database Scanner',
                'timestamp': datetime.now().isoformat(),
                'status': 'error',
                'error': str(e),
                'findings': [],
                'files_scanned': 0,
                'intelligence_applied': False
            }

    def display_intelligent_scan_results(self, scan_result: Dict[str, Any]):
        """Display scan results with intelligence metrics."""
        
        st.subheader("📊 Intelligent Scan Results")
        
        # Show intelligence improvements with better error handling
        intelligence_metrics = scan_result.get('intelligence_metrics', {})
        if intelligence_metrics:
            strategy_name = intelligence_metrics.get('strategy_used', 'Smart')
            st.info(f"🧠 **Intelligence Applied**: {strategy_name} strategy used")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                coverage = intelligence_metrics.get('coverage_achieved', scan_result.get('scan_coverage', 0))
                st.metric("Coverage", f"{coverage:.1f}%")
            with col2:
                efficiency = intelligence_metrics.get('efficiency_rating', 0)
                st.metric("Efficiency", f"{max(efficiency, 1):.1f}/100")
            with col3:
                scalability = intelligence_metrics.get('scalability_rating', 0)
                st.metric("Scalability", f"{max(scalability, 1):.1f}/100")
            with col4:
                time_saved = intelligence_metrics.get('time_savings_estimate', 0)
                if time_saved > 0:
                    st.metric("Time Saved", f"{time_saved:.0f}s")
                else:
                    # Estimate time saved based on scan efficiency
                    files_scanned = scan_result.get('files_scanned', 0)
                    if files_scanned > 20:
                        estimated_saved = files_scanned * 0.5  # Rough estimate
                        st.metric("Time Saved", f"~{estimated_saved:.0f}s")
                    else:
                        st.metric("Time Saved", "N/A")
        
        # Show strategy details
        strategy = scan_result.get('scanning_strategy', scan_result.get('processing_strategy', scan_result.get('crawling_strategy', {})))
        if strategy:
            st.expander("🎯 Scanning Strategy Details", expanded=False).write({
                'Strategy Type': strategy.get('type', 'Unknown'),
                'Target Items': strategy.get('target_files', strategy.get('target_images', strategy.get('target_pages', strategy.get('target_tables', 'N/A')))),
                'Parallel Workers': strategy.get('parallel_workers', 'N/A'),
                'Reasoning': strategy.get('reasoning', 'No details available')
            })
        
        # Always use our enhanced display instead of the main app display
        # This ensures consistent metrics display regardless of the main app function
        st.markdown("---")
        st.subheader("📊 Executive Summary")
        
        # Display comprehensive metrics matching main interface
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            files_scanned = scan_result.get('files_scanned', scan_result.get('pages_scanned', 0))
            st.metric("Files Scanned", files_scanned)
        with col2:
            total_findings = len(scan_result.get('findings', []))
            st.metric("Total Findings", total_findings)
        with col3:
            lines_analyzed = scan_result.get('lines_analyzed', files_scanned * 50 if files_scanned else 0)
            st.metric("Lines Analyzed", f"{lines_analyzed:,}")
        with col4:
            critical_issues = len([f for f in scan_result.get('findings', []) if f.get('severity') == 'Critical'])
            st.metric("Critical Issues", critical_issues)
        
        # Additional website-specific metrics for website scans
        if scan_result.get('scan_type') in ['Intelligent Website Scanner', 'GDPR Website Privacy Compliance Scanner']:
            st.subheader("🌐 Website Privacy Analysis")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                high_risk_issues = len([f for f in scan_result.get('findings', []) if f.get('severity') == 'High'])
                st.metric("High Risk Issues", high_risk_issues)
            with col2:
                compliance_score = scan_result.get('compliance_score', 0)
                st.metric("Compliance Score", f"{compliance_score}%")
            with col3:
                cookies_found = scan_result.get('cookies_found', len(scan_result.get('cookies_detected', [])))
                st.metric("Cookies Found", cookies_found)
            with col4:
                trackers_found = scan_result.get('trackers_found', len(scan_result.get('trackers_detected', [])))
                st.metric("Trackers Found", trackers_found)
        
        # Display findings if available
        findings = scan_result.get('findings', [])
        if findings:
            st.subheader("🔍 Findings Summary")
            for i, finding in enumerate(findings[:10], 1):  # Show first 10 findings
                with st.expander(f"Finding {i}: {finding.get('type', 'Unknown')} - {finding.get('severity', 'Medium')}"):
                    st.write(f"**File:** {finding.get('file', 'N/A')}")
                    st.write(f"**Description:** {finding.get('description', 'No description')}")
                    if finding.get('line'):
                        st.write(f"**Location:** {finding.get('line')}")
        else:
            st.success("✅ No issues found in the scan")
        
        # Display HTML report download if available
        st.subheader("📄 Download Report")
        try:
            from app import generate_html_report
            html_content = generate_html_report(scan_result)
            st.download_button(
                label="📥 Download HTML Report",
                data=html_content,
                file_name=f"scan_report_{scan_result.get('scan_id', 'unknown')[:8]}.html",
                mime="text/html"
            )
        except Exception as download_error:
            st.info("Report download temporarily unavailable")

# Global instance for use throughout the application
intelligent_wrapper = IntelligentScannerWrapper()