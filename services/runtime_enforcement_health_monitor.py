#!/usr/bin/env python3
"""
Runtime Enforcement Health Monitor
Provides health checks, monitoring, and structured logging for runtime enforcement packages

DataGuardian Pro - Production Validation & Monitoring System
"""

import json
import time
import logging
import os
import psutil
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/runtime_enforcement.log'),
        logging.StreamHandler()
    ]
)

@dataclass
class HealthCheckResult:
    """Health check result data structure"""
    component: str
    status: str  # 'healthy', 'warning', 'critical'
    message: str
    timestamp: datetime
    metrics: Dict[str, Any]
    recommendations: List[str]

@dataclass
class PackageGenerationEvent:
    """Structured logging event for package generation"""
    event_id: str
    event_type: str  # 'package_generated', 'package_exported', 'error_occurred'
    package_type: str
    timestamp: datetime
    duration_ms: float
    success: bool
    details: Dict[str, Any]
    user_context: Optional[Dict[str, Any]] = None

class RuntimeEnforcementHealthMonitor:
    """
    Health monitoring and structured logging for runtime enforcement system
    
    Features:
    - System health checks
    - Performance monitoring
    - Structured audit logging
    - Alert generation
    """
    
    def __init__(self, log_directory: str = "logs"):
        self.logger = logging.getLogger("RuntimeEnforcementHealthMonitor")
        self.log_directory = log_directory
        self.health_history: List[HealthCheckResult] = []
        self.event_history: List[PackageGenerationEvent] = []
        
        # Ensure log directory exists
        os.makedirs(log_directory, exist_ok=True)
        
        # Initialize monitoring metrics
        self.startup_time = datetime.now()
        self.total_packages_generated = 0
        self.error_count = 0
        self.performance_metrics = {
            "avg_generation_time_ms": 0.0,
            "peak_memory_usage_mb": 0.0,
            "total_uptime_hours": 0.0
        }
    
    def perform_comprehensive_health_check(self) -> Dict[str, HealthCheckResult]:
        """Perform comprehensive system health check"""
        health_results = {}
        
        # System resource health check
        health_results["system_resources"] = self._check_system_resources()
        
        # Runtime enforcement component health check
        health_results["enforcement_components"] = self._check_enforcement_components()
        
        # File system health check
        health_results["file_system"] = self._check_file_system()
        
        # Performance metrics health check
        health_results["performance"] = self._check_performance_metrics()
        
        # Log health status
        overall_status = self._calculate_overall_health(health_results)
        self.logger.info(f"Health check completed - Overall status: {overall_status}")
        
        return health_results
    
    def _check_system_resources(self) -> HealthCheckResult:
        """Check system resource utilization"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            
            # Determine status
            status = "healthy"
            recommendations = []
            
            if cpu_percent > 80:
                status = "warning"
                recommendations.append("High CPU usage detected - consider scaling")
            
            if memory_percent > 85:
                status = "critical" if memory_percent > 95 else "warning"
                recommendations.append("High memory usage detected - monitor for memory leaks")
            
            if disk_percent > 90:
                status = "critical"
                recommendations.append("Low disk space - clean up logs and temporary files")
            
            metrics = {
                "cpu_percent": cpu_percent,
                "memory_percent": memory_percent,
                "memory_available_gb": memory.available / 1024 / 1024 / 1024,
                "disk_percent": disk_percent,
                "disk_free_gb": disk.free / 1024 / 1024 / 1024
            }
            
            return HealthCheckResult(
                component="system_resources",
                status=status,
                message=f"CPU: {cpu_percent:.1f}%, Memory: {memory_percent:.1f}%, Disk: {disk_percent:.1f}%",
                timestamp=datetime.now(),
                metrics=metrics,
                recommendations=recommendations
            )
            
        except Exception as e:
            return HealthCheckResult(
                component="system_resources",
                status="critical",
                message=f"Failed to check system resources: {str(e)}",
                timestamp=datetime.now(),
                metrics={},
                recommendations=["Investigate system monitoring issues"]
            )
    
    def _check_enforcement_components(self) -> HealthCheckResult:
        """Check runtime enforcement component health"""
        try:
            from services.runtime_enforcement_generator import RuntimeEnforcementGenerator
            
            # Test component initialization
            generator = RuntimeEnforcementGenerator(region="Netherlands")
            
            # Check template loading
            templates_loaded = len(generator.enforcement_templates) > 0
            rules_loaded = len(generator.compliance_rules) > 0
            
            # Test package generation
            test_start = time.time()
            test_package = generator.generate_cookie_blocking_package("health-check.nl")
            generation_time = (time.time() - test_start) * 1000
            
            # Determine status
            status = "healthy"
            recommendations = []
            
            if not templates_loaded:
                status = "critical"
                recommendations.append("Enforcement templates failed to load")
            
            if not rules_loaded:
                status = "critical"
                recommendations.append("Compliance rules failed to load")
            
            if generation_time > 5000:  # 5 seconds
                status = "warning"
                recommendations.append("Package generation is slower than expected")
            
            metrics = {
                "templates_loaded": templates_loaded,
                "template_count": len(generator.enforcement_templates),
                "rules_loaded": rules_loaded,
                "rule_count": len(generator.compliance_rules),
                "test_generation_time_ms": generation_time,
                "test_package_files": len(test_package.deployment_files)
            }
            
            return HealthCheckResult(
                component="enforcement_components",
                status=status,
                message=f"Components loaded, test generation: {generation_time:.1f}ms",
                timestamp=datetime.now(),
                metrics=metrics,
                recommendations=recommendations
            )
            
        except Exception as e:
            return HealthCheckResult(
                component="enforcement_components",
                status="critical",
                message=f"Component health check failed: {str(e)}",
                timestamp=datetime.now(),
                metrics={},
                recommendations=["Investigate runtime enforcement component initialization"]
            )
    
    def _check_file_system(self) -> HealthCheckResult:
        """Check file system health for logs and temporary files"""
        try:
            # Check log directory
            log_path = Path(self.log_directory)
            log_exists = log_path.exists()
            log_writable = log_path.is_dir() and os.access(log_path, os.W_OK) if log_exists else False
            
            # Check log file sizes
            log_files = list(log_path.glob("*.log")) if log_exists else []
            total_log_size = sum(f.stat().st_size for f in log_files) if log_files else 0
            
            # Check temporary directory
            temp_path = Path("/tmp")
            temp_usage = psutil.disk_usage(str(temp_path))
            
            # Determine status
            status = "healthy"
            recommendations = []
            
            if not log_exists or not log_writable:
                status = "warning"
                recommendations.append("Log directory is not accessible - logging may fail")
            
            if total_log_size > 100 * 1024 * 1024:  # 100MB
                status = "warning"
                recommendations.append("Large log files detected - consider log rotation")
            
            if temp_usage.percent > 90:
                status = "warning"
                recommendations.append("Temporary directory space low - cleanup recommended")
            
            metrics = {
                "log_directory_exists": log_exists,
                "log_directory_writable": log_writable,
                "log_file_count": len(log_files),
                "total_log_size_mb": total_log_size / 1024 / 1024,
                "temp_usage_percent": temp_usage.percent,
                "temp_free_gb": temp_usage.free / 1024 / 1024 / 1024
            }
            
            return HealthCheckResult(
                component="file_system",
                status=status,
                message=f"Logs: {len(log_files)} files ({total_log_size/1024/1024:.1f}MB), Temp: {temp_usage.percent:.1f}% used",
                timestamp=datetime.now(),
                metrics=metrics,
                recommendations=recommendations
            )
            
        except Exception as e:
            return HealthCheckResult(
                component="file_system",
                status="critical",
                message=f"File system check failed: {str(e)}",
                timestamp=datetime.now(),
                metrics={},
                recommendations=["Investigate file system access issues"]
            )
    
    def _check_performance_metrics(self) -> HealthCheckResult:
        """Check performance metrics and trends"""
        try:
            # Calculate uptime
            uptime = datetime.now() - self.startup_time
            uptime_hours = uptime.total_seconds() / 3600
            
            # Update performance metrics
            self.performance_metrics["total_uptime_hours"] = uptime_hours
            
            # Get current memory usage
            current_memory = psutil.Process().memory_info().rss / 1024 / 1024
            if current_memory > self.performance_metrics["peak_memory_usage_mb"]:
                self.performance_metrics["peak_memory_usage_mb"] = current_memory
            
            # Determine status
            status = "healthy"
            recommendations = []
            
            if self.error_count > 10:
                status = "warning"
                recommendations.append("High error count detected - investigate recurring issues")
            
            if current_memory > 200:  # 200MB
                status = "warning"
                recommendations.append("High memory usage - monitor for memory leaks")
            
            metrics = {
                "uptime_hours": uptime_hours,
                "total_packages_generated": self.total_packages_generated,
                "error_count": self.error_count,
                "current_memory_mb": current_memory,
                "peak_memory_mb": self.performance_metrics["peak_memory_usage_mb"],
                "avg_generation_time_ms": self.performance_metrics["avg_generation_time_ms"]
            }
            
            return HealthCheckResult(
                component="performance",
                status=status,
                message=f"Uptime: {uptime_hours:.1f}h, Packages: {self.total_packages_generated}, Errors: {self.error_count}",
                timestamp=datetime.now(),
                metrics=metrics,
                recommendations=recommendations
            )
            
        except Exception as e:
            return HealthCheckResult(
                component="performance",
                status="critical",
                message=f"Performance check failed: {str(e)}",
                timestamp=datetime.now(),
                metrics={},
                recommendations=["Investigate performance monitoring issues"]
            )
    
    def _calculate_overall_health(self, health_results: Dict[str, HealthCheckResult]) -> str:
        """Calculate overall system health status"""
        statuses = [result.status for result in health_results.values()]
        
        if "critical" in statuses:
            return "critical"
        elif "warning" in statuses:
            return "warning"
        else:
            return "healthy"
    
    def log_package_generation_event(self, 
                                   package_type: str,
                                   duration_ms: float,
                                   success: bool,
                                   details: Optional[Dict[str, Any]] = None,
                                   user_context: Optional[Dict[str, Any]] = None):
        """Log structured package generation event"""
        event = PackageGenerationEvent(
            event_id=f"pkg_{int(time.time() * 1000)}_{package_type}",
            event_type="package_generated",
            package_type=package_type,
            timestamp=datetime.now(),
            duration_ms=duration_ms,
            success=success,
            details=details or {},
            user_context=user_context
        )
        
        # Add to event history
        self.event_history.append(event)
        
        # Update metrics
        if success:
            self.total_packages_generated += 1
            # Update average generation time
            total_time = (self.performance_metrics["avg_generation_time_ms"] * 
                         (self.total_packages_generated - 1) + duration_ms)
            self.performance_metrics["avg_generation_time_ms"] = total_time / self.total_packages_generated
        else:
            self.error_count += 1
        
        # Log structured event
        self.logger.info(f"Package generation event", extra={
            "event_id": event.event_id,
            "package_type": package_type,
            "duration_ms": duration_ms,
            "success": success,
            "details": details
        })
        
        # Write to audit log
        self._write_audit_log(event)
    
    def _write_audit_log(self, event: PackageGenerationEvent):
        """Write structured audit log entry"""
        audit_log_path = Path(self.log_directory) / "audit.jsonl"
        
        try:
            with open(audit_log_path, "a", encoding="utf-8") as f:
                json.dump(asdict(event), f, default=str, ensure_ascii=False)
                f.write("\n")
        except Exception as e:
            self.logger.error(f"Failed to write audit log: {e}")
    
    def get_health_report(self) -> Dict[str, Any]:
        """Generate comprehensive health report"""
        health_results = self.perform_comprehensive_health_check()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "overall_status": self._calculate_overall_health(health_results),
            "component_health": {name: asdict(result) for name, result in health_results.items()},
            "performance_metrics": self.performance_metrics,
            "system_info": {
                "startup_time": self.startup_time.isoformat(),
                "total_packages_generated": self.total_packages_generated,
                "error_count": self.error_count,
                "event_history_length": len(self.event_history)
            },
            "recommendations": self._generate_recommendations(health_results)
        }
    
    def _generate_recommendations(self, health_results: Dict[str, HealthCheckResult]) -> List[str]:
        """Generate actionable recommendations based on health check results"""
        recommendations = []
        
        for result in health_results.values():
            recommendations.extend(result.recommendations)
        
        # Add general recommendations
        if self.total_packages_generated == 0:
            recommendations.append("No packages generated yet - system is ready for first use")
        
        if len(self.event_history) > 1000:
            recommendations.append("Large event history - consider archiving old events")
        
        return list(set(recommendations))  # Remove duplicates
    
    def export_health_report(self, output_path: Optional[str] = None) -> str:
        """Export health report to file"""
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"{self.log_directory}/health_report_{timestamp}.json"
        
        health_report = self.get_health_report()
        
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(health_report, f, indent=2, default=str, ensure_ascii=False)
            
            self.logger.info(f"Health report exported to: {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"Failed to export health report: {e}")
            raise


# Global health monitor instance
_health_monitor = None

def get_health_monitor() -> RuntimeEnforcementHealthMonitor:
    """Get global health monitor instance"""
    global _health_monitor
    if _health_monitor is None:
        _health_monitor = RuntimeEnforcementHealthMonitor()
    return _health_monitor

def perform_health_check() -> Dict[str, Any]:
    """Convenience function to perform health check"""
    monitor = get_health_monitor()
    return monitor.get_health_report()

def log_package_event(package_type: str, duration_ms: float, success: bool, details: Optional[Dict[str, Any]] = None):
    """Convenience function to log package generation event"""
    monitor = get_health_monitor()
    monitor.log_package_generation_event(package_type, duration_ms, success, details)


if __name__ == '__main__':
    # Example usage and testing
    print("🏥 Runtime Enforcement Health Monitor")
    print("=" * 50)
    
    monitor = RuntimeEnforcementHealthMonitor()
    
    # Perform health check
    health_report = monitor.get_health_report()
    
    print(f"Overall Status: {health_report['overall_status'].upper()}")
    print(f"Components Checked: {len(health_report['component_health'])}")
    print(f"Total Packages Generated: {health_report['system_info']['total_packages_generated']}")
    
    # Export health report
    report_path = monitor.export_health_report()
    print(f"Health report exported to: {report_path}")
    
    # Test logging
    monitor.log_package_generation_event(
        package_type="cookie_blocker",
        duration_ms=1234.5,
        success=True,
        details={"domain": "test.nl", "files_generated": 4}
    )
    
    print("✅ Health monitoring system tested successfully")