"""
Intelligent Image Scanner - Scalable Image Processing

Implements smart image selection and parallel OCR processing:
- Priority-based image selection (ID cards, documents, screenshots first)
- Parallel OCR processing with memory optimization
- Adaptive batch processing for large image collections
- Smart image filtering and preprocessing
"""

import os
import logging

# Import centralized logging
try:
    from utils.centralized_logger import get_scanner_logger
    logger = get_scanner_logger("intelligent_image_scanner")
except ImportError:
    # Fallback to standard logging if centralized logger not available
    logger = logging.getLogger(__name__)
import concurrent.futures
import time
import tempfile
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable, Tuple
import uuid

logger = logging.getLogger("services.intelligent_image_scanner")

class IntelligentImageScanner:
    """Smart image scanner with scalability optimizations."""
    
    def __init__(self, image_scanner):
        self.image_scanner = image_scanner
        self.MAX_SCAN_TIME = 240  # 4 minutes max for image processing
        self.MAX_FILES_DEFAULT = 50
        self.MAX_FILE_SIZE_MB = 25  # Skip images larger than 25MB
        self.PARALLEL_WORKERS = 3  # OCR is CPU intensive
        self.BATCH_SIZE = 10  # Process images in batches
        
        # Image priority scoring
        self.IMAGE_PRIORITIES = {
            # High priority - likely to contain sensitive visual data
            'id': 3.0,
            'card': 3.0,
            'passport': 3.0,
            'license': 3.0,
            'document': 2.8,
            'form': 2.5,
            'contract': 2.5,
            'invoice': 2.5,
            'receipt': 2.0,
            'screen': 2.0,
            'capture': 2.0,
            'scan': 2.5,
            'photo': 1.8,
            'profile': 2.0,
            'signature': 2.5,
            'medical': 3.0,
            'report': 2.0,
            'chart': 1.8,
            'badge': 2.0,
            'certificate': 2.2,
            'diploma': 2.0,
            'test': 0.8,
            'demo': 0.5,
            'sample': 0.5,
            'thumbnail': 0.3,
            'icon': 0.2,
        }
        
        # File type priorities
        self.TYPE_PRIORITIES = {
            '.pdf': 2.5,  # PDF images often contain documents
            '.png': 2.0,  # Screenshots, documents
            '.jpg': 1.8,
            '.jpeg': 1.8,
            '.tiff': 2.2,  # Often scanned documents
            '.tif': 2.2,
            '.bmp': 1.5,
            '.gif': 1.0,
            '.webp': 1.2,
        }

    def scan_images_intelligent(self, image_paths: List[str],
                              scan_mode: str = "smart", 
                              max_files: Optional[int] = None,
                              progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """
        Intelligent image scanning with adaptive strategies.
        
        Args:
            image_paths: List of image file paths to scan
            scan_mode: "fast", "smart", "deep"
            max_files: Maximum files to scan
            progress_callback: Progress reporting callback
            
        Returns:
            Comprehensive scan results
        """
        start_time = time.time()
        scan_id = f"image_scan_{uuid.uuid4().hex[:8]}"
        
        scan_results = {
            'scan_id': scan_id,
            'scan_type': 'Intelligent Image Scanner',
            'timestamp': datetime.now().isoformat(),
            'region': self.image_scanner.region,
            'scan_mode': scan_mode,
            'images_analyzed': 0,
            'images_processed': 0,
            'images_skipped': 0,
            'total_images_found': len(image_paths),
            'findings': [],
            'image_types_found': {},
            'processing_strategy': {},
            'ocr_results': [],
            'face_detections': 0,
            'document_detections': 0,
            'status': 'completed'
        }
        
        try:
            # Step 1: Analyze image collection
            image_analysis = self._analyze_image_collection(image_paths)
            scan_results['image_types_found'] = image_analysis['image_types']
            
            # Step 2: Select processing strategy
            strategy = self._select_processing_strategy(image_analysis, scan_mode, max_files)
            scan_results['processing_strategy'] = strategy
            
            if progress_callback:
                progress_callback(10, 100, "Images analyzed, selecting for processing...")
            
            # Step 3: Select images based on strategy
            images_to_process = self._select_images_intelligent(image_paths, image_analysis, strategy)
            scan_results['images_analyzed'] = len(images_to_process)
            
            # Step 4: Process images in parallel batches
            findings, ocr_results, detections = self._process_images_parallel(
                images_to_process, scan_results, progress_callback
            )
            
            scan_results['findings'] = findings
            scan_results['ocr_results'] = ocr_results
            scan_results['face_detections'] = detections.get('faces', 0)
            scan_results['document_detections'] = detections.get('documents', 0)
            scan_results['duration_seconds'] = time.time() - start_time
            
            # Calculate coverage metrics
            scan_results['scan_coverage'] = (
                scan_results['images_processed'] / max(scan_results['total_images_found'], 1) * 100
            )
            
            logger.info(f"Intelligent image scan completed: {len(findings)} findings in {scan_results['duration_seconds']:.1f}s")
            logger.info(f"Processed {scan_results['images_processed']}/{scan_results['total_images_found']} images ({scan_results['scan_coverage']:.1f}% coverage)")
            
        except Exception as e:
            logger.error(f"Intelligent image scan failed: {str(e)}")
            scan_results['status'] = 'failed'
            scan_results['error'] = str(e)
        
        return scan_results

    def _analyze_image_collection(self, image_paths: List[str]) -> Dict[str, Any]:
        """Analyze the image collection to determine optimal processing strategy."""
        analysis = {
            'total_images': len(image_paths),
            'image_types': {},
            'size_distribution': [],
            'priority_distribution': {},
            'estimated_processing_time': 0,
            'risk_level': 'low'
        }
        
        priority_counts = {'high': 0, 'medium': 0, 'low': 0}
        
        for image_path in image_paths:
            try:
                # Get file info
                file_size = os.path.getsize(image_path)
                _, ext = os.path.splitext(image_path.lower())
                
                # Track image types
                analysis['image_types'][ext] = analysis['image_types'].get(ext, 0) + 1
                analysis['size_distribution'].append(file_size)
                
                # Calculate priority
                priority_score = self._calculate_image_priority(image_path)
                if priority_score >= 2.5:
                    priority_counts['high'] += 1
                elif priority_score >= 1.5:
                    priority_counts['medium'] += 1
                else:
                    priority_counts['low'] += 1
                
                # Estimate OCR processing time (rough - based on file size)
                size_mb = file_size / 1024 / 1024
                analysis['estimated_processing_time'] += min(size_mb * 5, 30)  # Max 30s per image
                
            except Exception as e:
                logger.warning(f"Error analyzing image {image_path}: {str(e)}")
                continue
        
        analysis['priority_distribution'] = priority_counts
        
        # Determine risk level based on high-priority images
        risk_score = priority_counts['high'] * 3 + priority_counts['medium'] * 1.5
        if risk_score > 15:
            analysis['risk_level'] = 'high'
        elif risk_score > 5:
            analysis['risk_level'] = 'medium'
        
        return analysis

    def _select_processing_strategy(self, image_analysis: Dict[str, Any],
                                  scan_mode: str, max_files: Optional[int]) -> Dict[str, Any]:
        """Select optimal processing strategy based on image analysis."""
        
        total_images = image_analysis['total_images']
        estimated_time = image_analysis['estimated_processing_time']
        risk_level = image_analysis['risk_level']
        
        # Determine strategy based on analysis
        if scan_mode == "fast" or total_images <= 10:
            strategy_type = "comprehensive"
            target_images = min(total_images, 15)
            workers = 2
            batch_size = 5
            
        elif scan_mode == "deep" or risk_level == "high":
            strategy_type = "priority_deep"
            target_images = min(max_files or 75, total_images)
            workers = 3
            batch_size = 8
            
        elif estimated_time > self.MAX_SCAN_TIME or total_images > 100:
            strategy_type = "sampling"
            target_images = min(max_files or 40, total_images)
            workers = 3
            batch_size = 10
            
        else:  # smart mode
            if total_images > 50:
                strategy_type = "priority"
                target_images = min(max_files or 50, total_images)
                workers = 3
                batch_size = 8
            else:
                strategy_type = "comprehensive"
                target_images = total_images
                workers = 2
                batch_size = 6
        
        return {
            'type': strategy_type,
            'target_images': target_images,
            'parallel_workers': workers,
            'batch_size': batch_size,
            'max_scan_time': self.MAX_SCAN_TIME,
            'reasoning': f"Selected {strategy_type} for {total_images} images with {risk_level} risk"
        }

    def _select_images_intelligent(self, image_paths: List[str],
                                 image_analysis: Dict[str, Any],
                                 strategy: Dict[str, Any]) -> List[str]:
        """Select images based on intelligent criteria."""
        
        # Calculate priorities for all images
        image_priorities = []
        for image_path in image_paths:
            try:
                # Skip files that are too large
                file_size = os.path.getsize(image_path)
                if file_size > self.MAX_FILE_SIZE_MB * 1024 * 1024:
                    continue
                
                priority = self._calculate_image_priority(image_path)
                image_priorities.append((image_path, priority, file_size))
                
            except Exception as e:
                logger.warning(f"Error processing image {image_path}: {str(e)}")
                continue
        
        # Sort by priority
        image_priorities.sort(key=lambda x: x[1], reverse=True)
        
        # Select images based on strategy
        target_images = strategy['target_images']
        
        if strategy['type'] == 'sampling':
            # Take top 70% by priority, random sample the rest
            high_priority_count = min(target_images * 70 // 100, len(image_priorities) // 2)
            selected = image_priorities[:high_priority_count]
            
            # Random sample from remaining
            remaining = image_priorities[high_priority_count:]
            if remaining and len(selected) < target_images:
                import random
                sample_size = min(target_images - len(selected), len(remaining))
                selected.extend(random.sample(remaining, sample_size))
                
        else:
            # Take top priority images
            selected = image_priorities[:target_images]
        
        selected_images = [img[0] for img in selected]
        
        logger.info(f"Selected {len(selected_images)} images using {strategy['type']} strategy")
        return selected_images

    def _calculate_image_priority(self, image_path: str) -> float:
        """Calculate priority score for an image."""
        image_path_lower = image_path.lower()
        filename = os.path.basename(image_path_lower)
        _, ext = os.path.splitext(filename)
        
        priority = 1.0  # Base priority
        
        # Filename content priority
        for pattern, weight in self.IMAGE_PRIORITIES.items():
            if pattern in filename or pattern in image_path_lower:
                priority += weight
        
        # File extension priority
        if ext in self.TYPE_PRIORITIES:
            priority += self.TYPE_PRIORITIES[ext]
        
        # Special high-risk patterns for images
        high_risk_patterns = [
            'id', 'passport', 'license', 'card', 'ssn', 'bsn',
            'medical', 'xray', 'scan', 'document', 'form',
            'signature', 'badge', 'certificate', 'diploma'
        ]
        
        for pattern in high_risk_patterns:
            if pattern in filename:
                priority += 2.5
        
        # Directory context
        if any(folder in image_path_lower for folder in ['documents', 'scans', 'ids', 'cards', 'photos']):
            priority += 1.0
        
        return priority

    def _process_images_parallel(self, images_to_process: List[str],
                               scan_results: Dict[str, Any],
                               progress_callback: Optional[Callable]) -> Tuple[List[Dict[str, Any]], List[str], Dict[str, int]]:
        """Process images in parallel batches with progress tracking."""
        
        all_findings = []
        all_ocr_results = []
        detections = {'faces': 0, 'documents': 0}
        
        workers = scan_results['processing_strategy']['parallel_workers']
        batch_size = scan_results['processing_strategy']['batch_size']
        max_time = scan_results['processing_strategy']['max_scan_time']
        
        start_time = time.time()
        
        # Process images in batches to manage memory
        for batch_start in range(0, len(images_to_process), batch_size):
            if time.time() - start_time > max_time:
                logger.warning("Image processing timeout reached")
                break
            
            batch_end = min(batch_start + batch_size, len(images_to_process))
            batch_images = images_to_process[batch_start:batch_end]
            
            # Process batch in parallel
            with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
                future_to_image = {
                    executor.submit(self._process_single_image, image_path): image_path
                    for image_path in batch_images
                }
                
                for future in concurrent.futures.as_completed(future_to_image, timeout=60):
                    try:
                        image_path = future_to_image[future]
                        result = future.result(timeout=45)  # 45 second per image timeout
                        
                        if result:
                            findings, ocr_text, face_count, doc_count = result
                            all_findings.extend(findings)
                            if ocr_text:
                                all_ocr_results.append(ocr_text)
                            detections['faces'] += face_count
                            detections['documents'] += doc_count
                        
                        scan_results['images_processed'] += 1
                        
                        # Progress callback
                        if progress_callback:
                            progress = 20 + int(70 * scan_results['images_processed'] / len(images_to_process))
                            filename = os.path.basename(image_path)
                            progress_callback(progress, 100, f"Processed {filename}")
                    
                    except concurrent.futures.TimeoutError:
                        scan_results['images_skipped'] += 1
                        logger.warning(f"Image processing timeout: {future_to_image[future]}")
                    except Exception as e:
                        scan_results['images_skipped'] += 1
                        logger.warning(f"Image processing error: {str(e)}")
        
        return all_findings, all_ocr_results, detections

    def _process_single_image(self, image_path: str) -> Optional[Tuple[List[Dict[str, Any]], str, int, int]]:
        """Process a single image for PII detection and OCR."""
        try:
            # Use the existing image scanner
            result = self.image_scanner.scan_image(image_path)
            
            # Extract findings and metadata from result
            findings = []
            ocr_text = ""
            face_count = 0
            doc_count = 0
            
            if isinstance(result, dict):
                findings = result.get('findings', [])
                ocr_text = result.get('ocr_text', '')
                face_count = result.get('face_detections', 0)
                doc_count = result.get('document_detections', 0)
            elif isinstance(result, list):
                findings = result
            
            return findings, ocr_text, face_count, doc_count
                
        except Exception as e:
            logger.warning(f"Error processing image {image_path}: {str(e)}")
            return None