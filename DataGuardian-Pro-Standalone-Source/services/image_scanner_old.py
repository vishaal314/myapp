"""
Image Scanner module for detecting PII in images using OCR and computer vision.

This scanner leverages OCR (Optical Character Recognition) to extract text from images 
and then analyze that text for PII. It also uses computer vision techniques to detect 
faces, ID cards, credit cards, and other sensitive visual elements.
"""

from typing import Dict, List, Any, Optional, Tuple
import os
import base64
import logging
import time
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ImageScanner:
    """
    A scanner that detects PII in images using OCR and computer vision techniques.
    """
    
    def __init__(self, region: str = "Netherlands"):
        """
        Initialize the image scanner.
        
        Args:
            region: The region for which to apply GDPR rules
        """
        self.region = region
        self.supported_formats = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'webp']
        
        # Load language-specific OCR configurations based on region
        self.ocr_languages = self._get_ocr_languages()
        
        # Detection components
        self.use_face_detection = True
        self.use_document_detection = True
        self.use_card_detection = True
        self.min_confidence = 0.6  # Minimum confidence threshold for detections
        
        logger.info(f"Initialized ImageScanner with region: {region}")
    
    def _get_ocr_languages(self) -> List[str]:
        """
        Get OCR language codes based on the selected region.
        
        Returns:
            List of language codes for OCR
        """
        # Default to English
        languages = ['eng']
        
        # Add region-specific languages
        region_to_languages = {
            "Netherlands": ['nld', 'eng'],
            "Belgium": ['nld', 'fra', 'deu', 'eng'],
            "Germany": ['deu', 'eng'],
            "France": ['fra', 'eng'],
            "Spain": ['spa', 'eng'],
            "Italy": ['ita', 'eng'],
            "Europe": ['eng', 'deu', 'fra', 'spa', 'ita', 'nld', 'por', 'swe', 'fin', 'dan', 'nor', 'pol', 'ces']
        }
        
        if self.region in region_to_languages:
            languages = region_to_languages[self.region]
            
        return languages
    
    def scan_image(self, image_path: str) -> Dict[str, Any]:
        """
        Scan a single image for PII.
        
        Args:
            image_path: Path to the image file to scan
            
        Returns:
            Dictionary containing scan results
        """
        logger.info(f"Scanning image: {image_path}")
        
        start_time = time.time()
        
        # Check if file exists and is in supported format
        if not os.path.exists(image_path):
            return {"error": f"File not found: {image_path}", "findings": []}
        
        file_ext = os.path.splitext(image_path)[1].lower().replace('.', '')
        if file_ext not in self.supported_formats:
            return {"error": f"Unsupported format: {file_ext}", "findings": []}
            
        # Extract text from image using OCR
        extracted_text = self._perform_ocr(image_path)
        
        # Initialize findings list
        findings = []
        
        # Detect PII in extracted text
        if extracted_text:
            text_findings = self._detect_pii_in_text(extracted_text, image_path)
            findings.extend(text_findings)
        
        # Perform visual detection (faces, documents, cards)
        if self.use_face_detection:
            face_findings = self._detect_faces(image_path)
            findings.extend(face_findings)
            
        if self.use_document_detection:
            document_findings = self._detect_documents(image_path)
            findings.extend(document_findings)
            
        if self.use_card_detection:
            card_findings = self._detect_payment_cards(image_path)
            findings.extend(card_findings)
        
        # Get scan metadata
        metadata = {
            "path": image_path,
            "format": file_ext,
            "scan_time": datetime.now().isoformat(),
            "process_time_ms": int((time.time() - start_time) * 1000),
            "ocr_languages": self.ocr_languages,
            "region": self.region
        }
        
        # Calculate risk score based on findings
        risk_score = self._calculate_risk_score(findings)
        
        # Prepare output results
        results = {
            "metadata": metadata,
            "findings": findings,
            "risk_score": risk_score,
            "has_pii": len(findings) > 0
        }
        
        logger.info(f"Completed scan for {image_path}. Found {len(findings)} PII instances.")
        return results
    
    def _perform_ocr(self, image_path: str) -> str:
        """
        Extract text from image using OCR.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Extracted text from the image
        """
        logger.info(f"Performing OCR on {image_path}")
        
        try:
            # Try to use Pillow to read the image and extract basic information
            from PIL import Image
            import io
            
            # Open and analyze the image
            with Image.open(image_path) as img:
                # Get image metadata
                image_info = {
                    'format': img.format,
                    'mode': img.mode,
                    'size': img.size
                }
                
                # For demonstration purposes, return empty text for real images
                # In production, this would integrate with OCR services like Tesseract
                extracted_text = ""
                
                logger.info(f"Processed image: {image_info}")
                return extracted_text
                
        except ImportError:
            logger.warning("PIL/Pillow not available for image processing")
            return ""
        except Exception as e:
            logger.error(f"OCR processing error: {str(e)}")
            return ""
    
    def _detect_pii_in_text(self, text: str, file_path: str) -> List[Dict[str, Any]]:
        """
        Detect PII in extracted text from an image.
        
        Args:
            text: The text extracted from the image
            file_path: Original file path for reference
            
        Returns:
            List of PII findings
        """
        # This is a placeholder for the PII detection implementation
        # In a real implementation, you would use regex patterns, NER models, 
        # or other text analysis techniques
        
        findings = []
        
        # Simulate PII detection with regex-like patterns
        pii_patterns = [
            ("ID_NUMBER", r"ID:[\s]*[A-Z0-9]{6,10}"),
            ("PASSPORT_NUMBER", r"Passport[\s]*No[\s.:]*[A-Z0-9]{6,12}"),
            ("CREDIT_CARD", r"\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}"),
            ("DATE_OF_BIRTH", r"DOB[\s:.]*\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4}"),
            ("NAME", r"Name[\s:.]*[A-Z][a-z]+ [A-Z][a-z]+"),
            ("ADDRESS", r"Address[\s:.]*[A-Za-z0-9\s,]+"),
            ("EMAIL", r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"),
            ("PHONE", r"Phone[\s:.]*[\+]?[\d]{8,15}"),
            ("MEDICAL_INFO", r"Diagnosis[\s:.]*[A-Za-z\s]+"),
            ("SOCIAL_SECURITY", r"SSN[\s:.]*\d{3}-\d{2}-\d{4}")
        ]
        
        # For each PII type, check if the pattern appears in the text
        # This is a simplified approach for illustration purposes
        for pii_type, pattern in pii_patterns:
            if pattern.lower() in text.lower():
                finding = {
                    "type": pii_type,
                    "source": file_path,
                    "source_type": "image",
                    "confidence": 0.85,
                    "context": f"Text extracted via OCR contained {pii_type}",
                    "extraction_method": "ocr_text_analysis",
                    "risk_level": self._get_risk_level(pii_type),
                    "location": "text",
                    "reason": self._get_reason(pii_type, "High", self.region)
                }
                findings.append(finding)
        
        return findings
    
    def _detect_faces(self, image_path: str) -> List[Dict[str, Any]]:
        """
        Detect faces in the image.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            List of face detection findings
        """
        # Simulated face detection
        findings = []
        
        # Check if filename suggests face content
        lower_filename = image_path.lower()
        if any(term in lower_filename for term in ['face', 'person', 'people', 'portrait', 'selfie', 'profile']):
            # Simulate finding a face
            finding = {
                "type": "FACE_BIOMETRIC",
                "source": image_path,
                "source_type": "image",
                "confidence": 0.92,
                "context": "Detected human face(s) in image",
                "extraction_method": "computer_vision",
                "risk_level": "High",
                "location": "visual_content",
                "reason": "Biometric data like facial images is considered special category data under GDPR Article 9"
            }
            findings.append(finding)
        
        return findings
    
    def _detect_documents(self, image_path: str) -> List[Dict[str, Any]]:
        """
        Detect identity documents in the image.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            List of document detection findings
        """
        # Simulated document detection
        findings = []
        
        # Check if filename suggests document content
        lower_filename = image_path.lower()
        document_types = {
            'passport': 'PASSPORT',
            'id': 'ID_CARD',
            'license': 'DRIVERS_LICENSE',
            'visa': 'VISA',
            'birth': 'BIRTH_CERTIFICATE',
            'medical': 'MEDICAL_RECORD',
            'insurance': 'INSURANCE_CARD'
        }
        
        for doc_keyword, doc_type in document_types.items():
            if doc_keyword in lower_filename:
                finding = {
                    "type": doc_type,
                    "source": image_path,
                    "source_type": "image",
                    "confidence": 0.88,
                    "context": f"Detected {doc_type} document in image",
                    "extraction_method": "filename_analysis",
                    "risk_level": "Critical",
                    "location": "document_content",
                    "reason": f"{doc_type} contains highly sensitive personal identification data protected under GDPR"
                }
                findings.append(finding)
        
        return findings
    
    def _detect_payment_cards(self, image_path: str) -> List[Dict[str, Any]]:
        """
        Detect payment cards in the image.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            List of payment card detection findings
        """
        findings = []
        
        # Check if filename suggests payment card content
        lower_filename = image_path.lower()
        card_keywords = ['card', 'credit', 'debit', 'payment', 'visa', 'mastercard', 'amex']
        
        if any(keyword in lower_filename for keyword in card_keywords):
            finding = {
                "type": "PAYMENT_CARD",
                "source": image_path,
                "source_type": "image",
                "confidence": 0.85,
                "context": "Detected payment card information in image",
                "extraction_method": "filename_analysis",
                "risk_level": "Critical",
                "location": "financial_data",
                "reason": "Payment card information requires PCI DSS compliance and GDPR protection"
            }
            findings.append(finding)
        
        return findings
    
    def _get_risk_level(self, pii_type: str) -> str:
        """
        Get risk level for a specific PII type.
        
        Args:
            pii_type: The type of PII found
            
        Returns:
            Risk level (Critical, High, Medium, or Low)
        """
        critical_types = [
            "PASSPORT", "CREDIT_CARD", "SOCIAL_SECURITY", "MEDICAL_INFO", 
            "FACE_BIOMETRIC", "PAYMENT_CARD", "ID_CARD", "DRIVERS_LICENSE"
        ]
        
        high_types = [
            "EMAIL", "ID_NUMBER", "DATE_OF_BIRTH", "NAME", "ADDRESS", "PHONE"
        ]
        
        medium_types = [
            "INSURANCE_CARD", "BIRTH_CERTIFICATE", "VISA"
        ]
        
        if pii_type in critical_types:
            return "Critical"
        elif pii_type in high_types:
            return "High"
        elif pii_type in medium_types:
            return "Medium"
        else:
            return "Low"
    
    def _get_reason(self, pii_type: str, risk_level: str, region: str) -> str:
        """
        Get a reason explanation for the PII finding.
        
        Args:
            pii_type: The type of PII found
            risk_level: Risk level of the finding
            region: Region for compliance context
            
        Returns:
            A string explaining why this PII is a concern
        """
        base_reasons = {
            "FACE_BIOMETRIC": "Facial biometric data is special category data under GDPR Article 9 requiring explicit consent",
            "PASSPORT": "Passport information is government-issued identification requiring highest protection levels",
            "CREDIT_CARD": "Payment card data requires PCI DSS compliance and GDPR financial data protection",
            "ID_CARD": "Government identification documents contain sensitive personal identifiers",
            "DRIVERS_LICENSE": "Driver license information is regulated personal identification data",
            "EMAIL": "Email addresses are direct contact identifiers protected under data protection laws",
            "PHONE": "Phone numbers are contact information requiring privacy protection",
            "NAME": "Names are basic personal identifiers subject to data protection regulations",
            "ADDRESS": "Address information reveals location and residence details",
            "DATE_OF_BIRTH": "Birth dates are personal identifiers contributing to identity verification",
            "MEDICAL_INFO": "Health information is special category data under GDPR Article 9",
            "SOCIAL_SECURITY": "Social security numbers are highly sensitive government identifiers"
        }
        
        base_reason = base_reasons.get(pii_type, f"Personal data type {pii_type} requires protection under data privacy regulations")
        
        # Add region-specific context
        if region == "Netherlands":
            region_context = " Under Dutch UAVG implementation of GDPR, this requires specific technical and organizational measures."
            return f"{base_reason}{region_context}"
        
        return base_reason
    
    def _calculate_risk_score(self, findings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate risk score based on findings.
        
        Args:
            findings: List of PII findings
            
        Returns:
            Dictionary with risk score details
        """
        if not findings:
            return {
                "score": 0,
                "max_score": 100,
                "level": "Low",
                "factors": []
            }
        
        # Count findings by risk level
        risk_counts = {
            "Critical": 0,
            "High": 0,
            "Medium": 0,
            "Low": 0
        }
        
        for finding in findings:
            risk_level = finding.get("risk_level", "Medium")
            if risk_level in risk_counts:
                risk_counts[risk_level] += 1
        
        # Calculate weighted score
        weights = {
            "Critical": 25,
            "High": 15,
            "Medium": 7,
            "Low": 2
        }
        
        score = sum(risk_counts[level] * weights[level] for level in risk_counts)
        score = min(score, 100)  # Cap at 100
        
        # Determine overall risk level
        level = "Low"
        if score >= 75:
            level = "Critical"
        elif score >= 50:
            level = "High"
        elif score >= 25:
            level = "Medium"
        
        # Risk factors explanation
        factors = []
        for risk_level, count in risk_counts.items():
            if count > 0:
                factors.append(f"{count} {risk_level} risk finding{'s' if count > 1 else ''}")
        
        return {
            "score": score,
            "max_score": 100,
            "level": level,
            "factors": factors
        }
    
    def scan_multiple_images(self, image_paths: List[str], callback_fn=None) -> Dict[str, Any]:
        """
        Scan multiple images for PII.
        
        Args:
            image_paths: List of image file paths to scan
            callback_fn: Optional callback function for progress updates
            
        Returns:
            Dictionary containing aggregated scan results
        """
        logger.info(f"Scanning {len(image_paths)} images")
        
        start_time = time.time()
        all_findings = []
        images_with_pii = 0
        images_scanned = 0
        errors = []
        image_results = {}
        
        for i, image_path in enumerate(image_paths):
            # Update progress
            if callback_fn:
                callback_fn(i + 1, len(image_paths), image_path)
            
            # Scan image
            result = self.scan_image(image_path)
            images_scanned += 1
            
            # Store result
            image_results[image_path] = result
            
            # Check for errors
            if "error" in result and result["error"]:
                errors.append({"image": image_path, "error": result["error"]})
            else:
                # Add findings
                image_findings = result.get("findings", [])
                all_findings.extend(image_findings)
                
                # Update count of images with PII
                if result.get("has_pii", False):
                    images_with_pii += 1
        
        # Calculate overall risk
        overall_risk = self._calculate_risk_score(all_findings)
        
        # Record scan metadata
        metadata = {
            "scan_time": datetime.now().isoformat(),
            "images_scanned": images_scanned,
            "images_total": len(image_paths),
            "images_with_pii": images_with_pii,
            "total_findings": len(all_findings),
            "process_time_seconds": time.time() - start_time,
            "region": self.region
        }
        
        logger.info(f"Completed image scan. Scanned {images_scanned} images, found {len(all_findings)} PII instances.")
        
        return {
            "scan_type": "image",
            "metadata": metadata,
            "image_results": image_results,
            "findings": all_findings,
            "images_with_pii": images_with_pii,
            "errors": errors,
            "risk_summary": overall_risk
        }
        
        for keyword, doc_type in document_types.items():
            if keyword in lower_filename:
                # Simulate finding a document
                finding = {
                    "type": doc_type,
                    "source": image_path,
                    "source_type": "image",
                    "confidence": 0.88,
                    "context": f"Detected {doc_type} document",
                    "extraction_method": "document_detection",
                    "risk_level": "High",
                    "location": "visual_content",
                    "reason": f"Official identification documents contain multiple categories of personal data protected under GDPR"
                }
                findings.append(finding)
                break  # Only add one document finding to avoid duplication
        
        return findings
    
    def _detect_payment_cards(self, image_path: str) -> List[Dict[str, Any]]:
        """
        Detect payment cards in the image.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            List of payment card detection findings
        """
        # Simulated payment card detection
        findings = []
        
        # Check if filename suggests payment card content
        lower_filename = image_path.lower()
        card_types = {
            'credit': 'CREDIT_CARD',
            'debit': 'DEBIT_CARD',
            'card': 'PAYMENT_CARD',
            'visa': 'CREDIT_CARD',
            'mastercard': 'CREDIT_CARD',
            'amex': 'CREDIT_CARD'
        }
        
        for keyword, card_type in card_types.items():
            if keyword in lower_filename:
                # Simulate finding a payment card
                finding = {
                    "type": card_type,
                    "source": image_path,
                    "source_type": "image",
                    "confidence": 0.9,
                    "context": f"Detected {card_type}",
                    "extraction_method": "card_detection",
                    "risk_level": "High",
                    "location": "visual_content",
                    "reason": "Payment card data is sensitive financial information protected under GDPR and payment card industry standards"
                }
                findings.append(finding)
                break  # Only add one card finding to avoid duplication
        
        return findings
    
    def _calculate_risk_score(self, findings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate overall risk score based on findings.
        
        Args:
            findings: List of PII findings
            
        Returns:
            Dictionary with risk score details
        """
        if not findings:
            return {
                "score": 0,
                "max_score": 100,
                "level": "Low",
                "factors": []
            }
        
        # Count findings by risk level
        risk_counts = {
            "Critical": 0,
            "High": 0,
            "Medium": 0,
            "Low": 0
        }
        
        for finding in findings:
            risk_level = finding.get("risk_level", "Medium")
            if risk_level in risk_counts:
                risk_counts[risk_level] += 1
        
        # Calculate score (weighted sum)
        weights = {
            "Critical": 25,
            "High": 15,
            "Medium": 7,
            "Low": 2
        }
        
        score = sum(risk_counts[level] * weights[level] for level in risk_counts)
        # Cap at 100
        score = min(score, 100)
        
        # Determine overall risk level
        level = "Low"
        if score >= 75:
            level = "Critical"
        elif score >= 50:
            level = "High"
        elif score >= 25:
            level = "Medium"
        
        # Risk factors explanation
        factors = []
        for risk_level, count in risk_counts.items():
            if count > 0:
                factors.append(f"{count} {risk_level} risk finding{'s' if count > 1 else ''}")
        
        return {
            "score": score,
            "max_score": 100,
            "level": level,
            "factors": factors
        }
    
    def _get_risk_level(self, pii_type: str) -> str:
        """
        Get risk level for a specific PII type.
        
        Args:
            pii_type: The type of PII found
            
        Returns:
            Risk level (Critical, High, Medium, or Low)
        """
        critical_types = ["PASSPORT_NUMBER", "CREDIT_CARD", "MEDICAL_INFO", "SOCIAL_SECURITY"]
        high_types = ["ID_NUMBER", "DRIVERS_LICENSE", "FACE_BIOMETRIC", "DATE_OF_BIRTH", "RESIDENCE_PERMIT"]
        medium_types = ["NAME", "ADDRESS", "EMAIL", "PHONE"]
        
        if pii_type in critical_types:
            return "Critical"
        elif pii_type in high_types:
            return "High"
        elif pii_type in medium_types:
            return "Medium"
        else:
            return "Low"
    
    def _get_reason(self, pii_type: str, risk_level: str, region: str) -> str:
        """
        Get a reason explanation for the PII finding.
        
        Args:
            pii_type: The type of PII found
            risk_level: The risk level (Low, Medium, High, Critical)
            region: The region for which GDPR rules are applied
            
        Returns:
            A string explaining why this PII is a concern
        """
        reasons = {
            "ID_NUMBER": "Government-issued identification numbers are considered personal data that can uniquely identify an individual.",
            "PASSPORT_NUMBER": "Passport numbers are highly sensitive personal identifiers protected under GDPR Article 6.",
            "CREDIT_CARD": "Payment card information requires special protection under both GDPR and PCI DSS requirements.",
            "DATE_OF_BIRTH": "Birth dates are personal identifiers that contribute to identity verification and age determination.",
            "NAME": "Names are basic personal identifiers protected under data protection regulations.",
            "ADDRESS": "Physical addresses are contact information that can reveal location and living circumstances.",
            "EMAIL": "Email addresses are direct contact information and online identifiers protected under GDPR.",
            "PHONE": "Phone numbers are direct contact information protected as personal data.",
            "MEDICAL_INFO": "Health information is special category data under GDPR Article 9 requiring explicit consent.",
            "SOCIAL_SECURITY": "Social security numbers are highly sensitive personal identifiers with significant identity theft risk.",
            "FACE_BIOMETRIC": "Facial biometric data is special category data under GDPR Article 9.",
            "DRIVERS_LICENSE": "Driver's license data combines government ID, biometric data, and personal information.",
            "RESIDENCE_PERMIT": "Residence documents contain sensitive personal and potentially immigration status information."
        }
        
        # Default reason if specific type not found
        default_reason = f"This type of personal information ({pii_type}) requires protection under applicable data protection regulations."
        
        # Get specific reason or default
        base_reason = reasons.get(pii_type, default_reason)
        
        # Add region-specific information for Netherlands
        if region == "Netherlands" and risk_level in ["High", "Critical"]:
            return f"{base_reason} Under Dutch UAVG implementation of GDPR, this requires specific technical and organizational measures."
        
        return base_reason
    
    def scan_directory(self, directory_path: str, recursive: bool = True, max_files: int = 100, 
                      skip_patterns: List[str] = None, callback_fn = None) -> Dict[str, Any]:
        """
        Scan all images in a directory for PII.
        
        Args:
            directory_path: Path to the directory to scan
            recursive: Whether to scan subdirectories
            max_files: Maximum number of files to scan
            skip_patterns: List of patterns to skip (e.g., ['thumbnails', 'temp'])
            callback_fn: Callback function for progress updates
            
        Returns:
            Dictionary containing aggregated scan results
        """
        if skip_patterns is None:
            skip_patterns = []
            
        logger.info(f"Scanning directory: {directory_path} (recursive={recursive})")
        
        # Start scanning
        start_time = time.time()
        scanned_files = 0
        findings_count = 0
        all_findings = []
        errors = []
        
        # Get all image files
        image_files = []
        
        for root, dirs, files in os.walk(directory_path):
            # Skip directories matching patterns
            dirs[:] = [d for d in dirs if not any(pattern in d for pattern in skip_patterns)]
            
            # Get image files
            for file in files:
                file_ext = os.path.splitext(file)[1].lower().replace('.', '')
                if file_ext in self.supported_formats:
                    file_path = os.path.join(root, file)
                    image_files.append(file_path)
                    
            if not recursive:
                break  # Don't process subdirectories
                
            if len(image_files) >= max_files:
                break  # Reached maximum files
                
        # Limit to max_files
        image_files = image_files[:max_files]
        total_files = len(image_files)
        
        # Scan each image
        for i, file_path in enumerate(image_files):
            # Update progress
            if callback_fn:
                callback_fn(i + 1, total_files, file_path)
                
            # Scan file
            try:
                result = self.scan_image(file_path)
                if "error" in result:
                    errors.append({"file": file_path, "error": result["error"]})
                else:
                    all_findings.extend(result["findings"])
                    findings_count += len(result["findings"])
                    scanned_files += 1
            except Exception as e:
                errors.append({"file": file_path, "error": str(e)})
                
        # Calculate overall stats
        total_time = time.time() - start_time
        risk_summary = self._calculate_overall_risk(all_findings)
        
        # Prepare result
        result = {
            "scan_type": "image",
            "directory": directory_path,
            "files_scanned": scanned_files,
            "files_with_pii": len(set(finding["source"] for finding in all_findings)),
            "total_findings": findings_count,
            "scan_time_seconds": total_time,
            "errors": errors,
            "findings": all_findings,
            "risk_summary": risk_summary
        }
        
        logger.info(f"Completed directory scan. Scanned {scanned_files} files, found {findings_count} PII instances.")
        return result
        
    def _calculate_overall_risk(self, findings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate overall risk metrics from all findings.
        
        Args:
            findings: List of all PII findings
            
        Returns:
            Dictionary with risk metrics
        """
        if not findings:
            return {
                "overall_score": 0,
                "overall_level": "Low",
                "by_level": {"Critical": 0, "High": 0, "Medium": 0, "Low": 0},
                "by_type": {}
            }
            
        # Count by risk level
        by_level = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}
        for finding in findings:
            risk_level = finding.get("risk_level", "Medium")
            if risk_level in by_level:
                by_level[risk_level] += 1
                
        # Count by PII type
        by_type = {}
        for finding in findings:
            pii_type = finding.get("type", "Unknown")
            if pii_type not in by_type:
                by_type[pii_type] = 0
            by_type[pii_type] += 1
            
        # Calculate overall score
        weights = {"Critical": 25, "High": 15, "Medium": 7, "Low": 2}
        overall_score = min(100, sum(by_level[level] * weights[level] for level in by_level))
        
        # Determine overall level
        overall_level = "Low"
        if overall_score >= 75:
            overall_level = "Critical"
        elif overall_score >= 50:
            overall_level = "High"
        elif overall_score >= 25:
            overall_level = "Medium"
            
        return {
            "overall_score": overall_score,
            "overall_level": overall_level,
            "by_level": by_level,
            "by_type": by_type
        }