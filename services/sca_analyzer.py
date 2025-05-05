"""
Software Composition Analysis (SCA) Analyzer

This module provides SCA capability to detect vulnerabilities in third-party
dependencies and libraries. It focuses on finding issues relevant to PCI DSS
requirement 6.3.4 for patch management.
"""

import os
import re
import json
import logging
import subprocess
from typing import Dict, List, Any, Optional, Set

# Set up logging
logger = logging.getLogger("sca_analyzer")

class SCAAnalyzer:
    """
    Performs Software Composition Analysis to detect vulnerabilities in
    third-party dependencies and libraries.
    """
    
    def __init__(self):
        """Initialize the SCA Analyzer."""
        # Initialize vulnerability database for common packages
        # This is a simplified database - in production this would connect to
        # a full vulnerability database like NVD or a commercial source
        self.vulnerability_db = {
            # Python vulnerabilities
            "django": {
                "<2.2.28": [
                    {
                        "id": "CVE-2022-36359",
                        "description": "SQL injection vulnerability in QuerySet.annotate()",
                        "severity": "High",
                        "cvss_score": 8.8,
                        "cwe": "CWE-89"
                    }
                ],
                "<3.2.15": [
                    {
                        "id": "CVE-2023-23969",
                        "description": "Denial-of-service possibility in file uploads",
                        "severity": "Medium",
                        "cvss_score": 6.5,
                        "cwe": "CWE-400"
                    }
                ]
            },
            "flask": {
                "<2.0.3": [
                    {
                        "id": "CVE-2022-29221",
                        "description": "Possible disclosure of sensitive information due to improper error handling",
                        "severity": "Medium",
                        "cvss_score": 5.3,
                        "cwe": "CWE-209"
                    }
                ]
            },
            "requests": {
                "<2.27.0": [
                    {
                        "id": "CVE-2022-40975",
                        "description": "CRLF injection due to improper header validation",
                        "severity": "Medium",
                        "cvss_score": 5.9,
                        "cwe": "CWE-93"
                    }
                ]
            },
            "pyyaml": {
                "<5.4": [
                    {
                        "id": "CVE-2020-14343",
                        "description": "Arbitrary code execution in FullLoader",
                        "severity": "High",
                        "cvss_score": 9.8,
                        "cwe": "CWE-502"
                    }
                ]
            },
            "cryptography": {
                "<35.0.0": [
                    {
                        "id": "CVE-2023-23931",
                        "description": "Possible timing attack in X.509 certificate parsing",
                        "severity": "Medium",
                        "cvss_score": 5.9,
                        "cwe": "CWE-203"
                    }
                ]
            },
            # Node.js vulnerabilities
            "express": {
                "<4.17.3": [
                    {
                        "id": "CVE-2022-24999",
                        "description": "Improper input validation leads to denial of service",
                        "severity": "Medium",
                        "cvss_score": 6.5,
                        "cwe": "CWE-20"
                    }
                ]
            },
            "axios": {
                "<0.21.2": [
                    {
                        "id": "CVE-2021-3749",
                        "description": "SSRF vulnerability in axios.js",
                        "severity": "High",
                        "cvss_score": 8.1,
                        "cwe": "CWE-918"
                    }
                ]
            },
            "lodash": {
                "<4.17.21": [
                    {
                        "id": "CVE-2021-23337",
                        "description": "Command injection in template function",
                        "severity": "High",
                        "cvss_score": 7.2,
                        "cwe": "CWE-77"
                    }
                ]
            },
            "log4j": {
                "<2.15.0": [
                    {
                        "id": "CVE-2021-44228",
                        "description": "Log4Shell remote code execution vulnerability",
                        "severity": "Critical",
                        "cvss_score": 10.0,
                        "cwe": "CWE-502"
                    }
                ]
            },
            "jquery": {
                "<3.5.0": [
                    {
                        "id": "CVE-2020-11022",
                        "description": "Cross-site scripting vulnerability",
                        "severity": "Medium",
                        "cvss_score": 6.1,
                        "cwe": "CWE-79"
                    }
                ]
            },
            # Java vulnerabilities
            "spring-core": {
                "<5.3.18": [
                    {
                        "id": "CVE-2022-22965",
                        "description": "Spring Framework RCE vulnerability (Spring4Shell)",
                        "severity": "Critical",
                        "cvss_score": 9.8,
                        "cwe": "CWE-94"
                    }
                ]
            },
            "log4j-core": {
                "<2.15.0": [
                    {
                        "id": "CVE-2021-44228",
                        "description": "Log4Shell remote code execution vulnerability",
                        "severity": "Critical",
                        "cvss_score": 10.0,
                        "cwe": "CWE-502"
                    }
                ]
            }
        }
        
        # Mapping of package managers to file patterns
        self.package_managers = {
            "pip": {
                "files": ["requirements.txt", "Pipfile", "Pipfile.lock", "poetry.lock", "pyproject.toml"],
                "parser": self._parse_python_dependencies
            },
            "npm": {
                "files": ["package.json", "package-lock.json", "yarn.lock"],
                "parser": self._parse_node_dependencies
            },
            "maven": {
                "files": ["pom.xml"],
                "parser": self._parse_java_dependencies
            },
            "gradle": {
                "files": ["build.gradle", "build.gradle.kts"],
                "parser": self._parse_gradle_dependencies
            },
            "nuget": {
                "files": ["packages.config", "*.csproj"],
                "parser": self._parse_dotnet_dependencies
            }
        }
        
        logger.info("SCA Analyzer initialized with vulnerability database")
    
    def analyze(self, directory_path: str) -> List[Dict[str, Any]]:
        """
        Analyze dependencies in the given directory for known vulnerabilities.
        
        Args:
            directory_path: Path to the directory containing dependency files
            
        Returns:
            List of vulnerability findings
        """
        findings = []
        
        # Try to use a dedicated SCA tool if available
        try:
            # Try to use OWASP Dependency-Check if available
            dependency_check_findings = self._run_dependency_check(directory_path)
            if dependency_check_findings:
                findings.extend(dependency_check_findings)
                logger.info(f"Found {len(dependency_check_findings)} vulnerabilities with Dependency-Check")
                # If Dependency-Check worked, we can return early as it's more comprehensive
                if len(dependency_check_findings) > 0:
                    return findings
        except Exception as e:
            logger.info(f"Dependency-Check not available or failed, using built-in SCA: {str(e)}")
        
        # Fall back to built-in SCA
        logger.info("Using built-in SCA capability")
        
        # Find all dependency files
        dependency_files = []
        for root, _, files in os.walk(directory_path):
            # Skip .git directory
            if '.git' in root:
                continue
                
            for file in files:
                file_path = os.path.join(root, file)
                
                # Check if this is a dependency file for any package manager
                for package_manager, config in self.package_managers.items():
                    # Check exact filenames
                    if file in config["files"]:
                        dependency_files.append((file_path, package_manager))
                        break
                        
                    # Check wildcard patterns
                    for pattern in config["files"]:
                        if "*" in pattern:
                            # Convert glob pattern to regex
                            regex = pattern.replace(".", "\\.").replace("*", ".*")
                            if re.match(regex, file):
                                dependency_files.append((file_path, package_manager))
                                break
        
        # Process each dependency file
        for file_path, package_manager in dependency_files:
            logger.info(f"Analyzing dependencies in {file_path} with {package_manager}")
            
            # Get the parser for this package manager
            parser = self.package_managers[package_manager]["parser"]
            
            try:
                # Parse the dependency file
                dependencies = parser(file_path)
                
                # Get relative path for reporting
                rel_path = os.path.relpath(file_path, directory_path)
                
                # Check each dependency for vulnerabilities
                for name, version in dependencies:
                    vulns = self._check_vulnerability(name, version)
                    
                    for vuln in vulns:
                        finding = {
                            "type": f"Vulnerable Dependency: {name}@{version}",
                            "value": f"{vuln['id']}: {vuln['description']}",
                            "location": rel_path,
                            "file_name": rel_path,
                            "package_name": name,
                            "package_version": version,
                            "vulnerability_id": vuln['id'],
                            "risk_level": self._severity_to_risk_level(vuln['severity']),
                            "pci_requirement": "6.3.3, 6.3.4",
                            "remediation": f"Update {name} to a version not affected by {vuln['id']}"
                        }
                        
                        findings.append(finding)
            except Exception as e:
                logger.warning(f"Error analyzing dependencies in {file_path}: {str(e)}")
        
        logger.info(f"Found {len(findings)} vulnerable dependencies")
        return findings
    
    def _parse_python_dependencies(self, file_path: str) -> List[Tuple[str, str]]:
        """
        Parse Python dependencies from requirements files.
        
        Args:
            file_path: Path to the requirements file
            
        Returns:
            List of (package_name, version) tuples
        """
        dependencies = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Handle different file formats
            filename = os.path.basename(file_path)
            
            if filename == "requirements.txt":
                # Parse requirements.txt format
                for line in content.split('\n'):
                    line = line.strip()
                    
                    # Skip comments and empty lines
                    if not line or line.startswith('#'):
                        continue
                    
                    # Handle "package==version" format
                    if "==" in line:
                        name, version = line.split("==", 1)
                        name = name.strip()
                        version = version.strip()
                        dependencies.append((name, version))
                    # Handle "package>=version" format
                    elif ">=" in line:
                        name, version = line.split(">=", 1)
                        name = name.strip()
                        version = version.strip() + " or higher"
                        dependencies.append((name, version))
                    # Handle "package" format with no version
                    else:
                        name = line.strip()
                        if name:
                            dependencies.append((name, "Unknown"))
            
            elif filename == "Pipfile" or filename == "Pipfile.lock":
                # Try to parse Pipfile or Pipfile.lock
                if filename == "Pipfile.lock":
                    try:
                        data = json.loads(content)
                        packages = {**data.get("default", {}), **data.get("develop", {})}
                        
                        for name, details in packages.items():
                            version = details.get("version", "Unknown")
                            # Clean up version string
                            if version.startswith("=="):
                                version = version[2:]
                            elif version.startswith(">="):
                                version = version[2:] + " or higher"
                                
                            dependencies.append((name, version))
                    except json.JSONDecodeError:
                        logger.warning(f"Invalid JSON in {file_path}")
                else:
                    # Simple Pipfile parsing (not fully accurate but good enough)
                    in_packages = False
                    for line in content.split('\n'):
                        line = line.strip()
                        
                        if "[packages]" in line:
                            in_packages = True
                            continue
                        elif line.startswith('[') and ']' in line:
                            in_packages = False
                            continue
                            
                        if in_packages and "=" in line:
                            parts = line.split("=", 1)
                            name = parts[0].strip().strip('"\'')
                            version_parts = parts[1].strip().strip('"\'')
                            
                            if '"' in version_parts or "'" in version_parts:
                                # Extract version from quotes
                                match = re.search(r'["\'](.+?)["\']', version_parts)
                                if match:
                                    version = match.group(1)
                                else:
                                    version = "Unknown"
                            else:
                                version = "Unknown"
                                
                            dependencies.append((name, version))
            
            elif filename == "pyproject.toml":
                # Simple TOML parsing for Poetry dependencies
                in_dependencies = False
                for line in content.split('\n'):
                    line = line.strip()
                    
                    if line.startswith('[tool.poetry.dependencies]'):
                        in_dependencies = True
                        continue
                    elif line.startswith('['):
                        in_dependencies = False
                        continue
                        
                    if in_dependencies and "=" in line:
                        parts = line.split("=", 1)
                        name = parts[0].strip()
                        
                        # Extract version from quotes
                        match = re.search(r'["\'](.+?)["\']', parts[1])
                        if match:
                            version = match.group(1)
                        else:
                            version = "Unknown"
                            
                        dependencies.append((name, version))
        except Exception as e:
            logger.warning(f"Error parsing Python dependencies from {file_path}: {str(e)}")
            
        return dependencies
    
    def _parse_node_dependencies(self, file_path: str) -> List[Tuple[str, str]]:
        """
        Parse Node.js dependencies from package.json or lock files.
        
        Args:
            file_path: Path to the package.json or lock file
            
        Returns:
            List of (package_name, version) tuples
        """
        dependencies = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            try:
                data = json.loads(content)
                
                # Handle different file formats
                filename = os.path.basename(file_path)
                
                if filename == "package.json":
                    # Get dependencies from package.json
                    for section in ["dependencies", "devDependencies"]:
                        if section in data:
                            for name, version in data[section].items():
                                # Clean up version string
                                version = version.replace("^", "").replace("~", "")
                                dependencies.append((name, version))
                
                elif filename == "package-lock.json":
                    # Get dependencies from package-lock.json
                    if "dependencies" in data:
                        for name, details in data["dependencies"].items():
                            version = details.get("version", "Unknown")
                            dependencies.append((name, version))
                
                elif filename == "yarn.lock":
                    # Yarn lock file doesn't use JSON, use regex to parse
                    raise ValueError("Yarn lock files require special parsing")
            
            except json.JSONDecodeError:
                # If it's not valid JSON, it might be yarn.lock
                if file_path.endswith("yarn.lock"):
                    # Simple pattern matching for yarn.lock
                    package_pattern = r'(.+?)@.+?:\n\s+version "(.*?)"'
                    for match in re.finditer(package_pattern, content):
                        name = match.group(1)
                        version = match.group(2)
                        dependencies.append((name, version))
        
        except Exception as e:
            logger.warning(f"Error parsing Node.js dependencies from {file_path}: {str(e)}")
            
        return dependencies
    
    def _parse_java_dependencies(self, file_path: str) -> List[Tuple[str, str]]:
        """
        Parse Java dependencies from pom.xml.
        
        Args:
            file_path: Path to the pom.xml file
            
        Returns:
            List of (package_name, version) tuples
        """
        dependencies = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Simple regex parsing for Maven dependencies
            dependency_pattern = r'<dependency>\s*<groupId>([^<]+)</groupId>\s*<artifactId>([^<]+)</artifactId>\s*<version>([^<]+)</version>'
            for match in re.finditer(dependency_pattern, content, re.DOTALL):
                group_id = match.group(1).strip()
                artifact_id = match.group(2).strip()
                version = match.group(3).strip()
                
                # Combine groupId and artifactId for the package name
                name = f"{group_id}:{artifact_id}"
                dependencies.append((name, version))
        
        except Exception as e:
            logger.warning(f"Error parsing Java dependencies from {file_path}: {str(e)}")
            
        return dependencies
    
    def _parse_gradle_dependencies(self, file_path: str) -> List[Tuple[str, str]]:
        """
        Parse Gradle dependencies from build.gradle.
        
        Args:
            file_path: Path to the build.gradle file
            
        Returns:
            List of (package_name, version) tuples
        """
        dependencies = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Find dependency blocks in the file
            dependency_blocks = re.findall(r'dependencies\s*{([^}]+)}', content, re.DOTALL)
            
            for block in dependency_blocks:
                # Find individual dependency declarations
                # implementation 'group:name:version'
                single_quote_pattern = r'\b(?:implementation|api|compile|runtime|testImplementation|testRuntime)\s*[\'"]([^:]+):([^:]+):([^\'"]+)[\'"]'
                for match in re.finditer(single_quote_pattern, block):
                    group = match.group(1).strip()
                    name = match.group(2).strip()
                    version = match.group(3).strip()
                    
                    dependencies.append((f"{group}:{name}", version))
                
                # implementation group: 'group', name: 'name', version: 'version'
                group_pattern = r'\b(?:implementation|api|compile|runtime|testImplementation|testRuntime)\s*\(\s*group\s*:\s*[\'"]([^\'"]*)[\'"]\s*,\s*name\s*:\s*[\'"]([^\'"]*)[\'"]\s*,\s*version\s*:\s*[\'"]([^\'"]*)[\'"]\s*\)'
                for match in re.finditer(group_pattern, block):
                    group = match.group(1).strip()
                    name = match.group(2).strip()
                    version = match.group(3).strip()
                    
                    dependencies.append((f"{group}:{name}", version))
        
        except Exception as e:
            logger.warning(f"Error parsing Gradle dependencies from {file_path}: {str(e)}")
            
        return dependencies
    
    def _parse_dotnet_dependencies(self, file_path: str) -> List[Tuple[str, str]]:
        """
        Parse .NET dependencies from packages.config or .csproj files.
        
        Args:
            file_path: Path to the packages.config or .csproj file
            
        Returns:
            List of (package_name, version) tuples
        """
        dependencies = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Handle different file formats
            if file_path.endswith("packages.config"):
                # Parse packages.config format
                package_pattern = r'<package\s+id="([^"]+)"\s+version="([^"]+)"'
                for match in re.finditer(package_pattern, content):
                    name = match.group(1).strip()
                    version = match.group(2).strip()
                    dependencies.append((name, version))
            else:
                # Parse .csproj PackageReference format
                package_pattern = r'<PackageReference\s+Include="([^"]+)"\s+Version="([^"]+)"'
                for match in re.finditer(package_pattern, content):
                    name = match.group(1).strip()
                    version = match.group(2).strip()
                    dependencies.append((name, version))
        
        except Exception as e:
            logger.warning(f"Error parsing .NET dependencies from {file_path}: {str(e)}")
            
        return dependencies
    
    def _check_vulnerability(self, package_name: str, version: str) -> List[Dict[str, Any]]:
        """
        Check if a package version has known vulnerabilities.
        
        Args:
            package_name: The package name
            version: The package version
            
        Returns:
            List of vulnerability dictionaries
        """
        vulnerabilities = []
        
        # Normalize package name (some databases use lowercase)
        package_name_lower = package_name.lower()
        
        # Extract package name from group:artifact format
        if ":" in package_name_lower:
            _, package_name_lower = package_name_lower.split(":", 1)
        
        # Handle "or higher" version strings
        if "or higher" in version:
            version = version.replace(" or higher", "")
        
        # Check if package is in our vulnerability database
        if package_name_lower in self.vulnerability_db:
            for vuln_version, vuln_details in self.vulnerability_db[package_name_lower].items():
                # Check if version is affected
                if self._is_version_affected(version, vuln_version):
                    vulnerabilities.extend(vuln_details)
        
        return vulnerabilities
    
    def _is_version_affected(self, package_version: str, vulnerability_version: str) -> bool:
        """
        Check if a package version is affected by a vulnerability.
        
        Args:
            package_version: The package version string
            vulnerability_version: The vulnerability version constraint (e.g., "<2.0.0")
            
        Returns:
            True if the package version is affected, False otherwise
        """
        try:
            # Handle "Unknown" version
            if package_version == "Unknown":
                # Assume affected if we don't know the version
                return True
            
            # Simple version comparison for demonstration
            # In a real implementation, this would use proper semantic versioning
            
            # Handle "<" operator
            if vulnerability_version.startswith("<"):
                vuln_version = vulnerability_version[1:]
                return self._compare_versions(package_version, vuln_version) < 0
            
            # Handle "<=" operator
            elif vulnerability_version.startswith("<="):
                vuln_version = vulnerability_version[2:]
                return self._compare_versions(package_version, vuln_version) <= 0
            
            # Handle ">" operator
            elif vulnerability_version.startswith(">"):
                vuln_version = vulnerability_version[1:]
                return self._compare_versions(package_version, vuln_version) > 0
            
            # Handle ">=" operator
            elif vulnerability_version.startswith(">="):
                vuln_version = vulnerability_version[2:]
                return self._compare_versions(package_version, vuln_version) >= 0
            
            # Handle "==" operator (or no operator)
            else:
                if vulnerability_version.startswith("=="):
                    vuln_version = vulnerability_version[2:]
                else:
                    vuln_version = vulnerability_version
                return self._compare_versions(package_version, vuln_version) == 0
        
        except Exception:
            # If we can't parse the version, assume affected
            return True
    
    def _compare_versions(self, version1: str, version2: str) -> int:
        """
        Compare two version strings.
        
        Args:
            version1: First version string
            version2: Second version string
            
        Returns:
            -1 if version1 < version2, 0 if version1 == version2, 1 if version1 > version2
        """
        # Split versions into components
        v1_parts = self._parse_version(version1)
        v2_parts = self._parse_version(version2)
        
        # Compare each component
        for i in range(max(len(v1_parts), len(v2_parts))):
            v1 = v1_parts[i] if i < len(v1_parts) else 0
            v2 = v2_parts[i] if i < len(v2_parts) else 0
            
            if v1 < v2:
                return -1
            elif v1 > v2:
                return 1
        
        # Versions are equal
        return 0
    
    def _parse_version(self, version: str) -> List[int]:
        """
        Parse a version string into a list of integers.
        
        Args:
            version: Version string (e.g., "1.2.3")
            
        Returns:
            List of integers (e.g., [1, 2, 3])
        """
        # Extract numeric parts from version string
        version = re.sub(r'[^\d.]', '', version)
        
        # Split by dots and convert to integers
        parts = []
        for part in version.split('.'):
            try:
                parts.append(int(part))
            except ValueError:
                parts.append(0)
        
        return parts
    
    def _run_dependency_check(self, directory_path: str) -> List[Dict[str, Any]]:
        """
        Run OWASP Dependency-Check if available.
        
        Args:
            directory_path: Path to the directory to scan
            
        Returns:
            List of vulnerability findings
        """
        findings = []
        
        try:
            # Create a temporary directory for output
            import tempfile
            output_dir = tempfile.mkdtemp()
            
            # Run Dependency-Check
            subprocess.run([
                "dependency-check",
                "--scan", directory_path,
                "--out", output_dir,
                "--format", "JSON"
            ], check=True, capture_output=True)
            
            # Parse the JSON report
            report_path = os.path.join(output_dir, "dependency-check-report.json")
            with open(report_path, 'r') as f:
                report = json.load(f)
            
            # Extract findings
            if "dependencies" in report:
                for dependency in report["dependencies"]:
                    if "vulnerabilities" in dependency:
                        for vuln in dependency["vulnerabilities"]:
                            finding = {
                                "type": f"Vulnerable Dependency: {dependency.get('fileName', 'Unknown')}",
                                "value": f"{vuln.get('name', 'Unknown')}: {vuln.get('description', 'No description')}",
                                "location": dependency.get('filePath', 'Unknown'),
                                "file_name": dependency.get('fileName', 'Unknown'),
                                "package_name": dependency.get('packages', [{'id': 'Unknown'}])[0]['id'],
                                "package_version": dependency.get('version', 'Unknown'),
                                "vulnerability_id": vuln.get('name', 'Unknown'),
                                "risk_level": self._cvss_to_risk_level(vuln.get('cvssv3', {}).get('baseScore', 0)),
                                "pci_requirement": "6.3.3, 6.3.4",
                                "remediation": vuln.get('recommendation', "Update to a non-vulnerable version")
                            }
                            findings.append(finding)
            
            # Clean up
            import shutil
            shutil.rmtree(output_dir)
            
        except Exception as e:
            raise Exception(f"Failed to run Dependency-Check: {str(e)}")
            
        return findings
    
    def _severity_to_risk_level(self, severity: str) -> str:
        """
        Convert severity to risk level.
        
        Args:
            severity: Severity string
            
        Returns:
            Risk level string
        """
        mapping = {
            "Critical": "High",
            "High": "High",
            "Medium": "Medium",
            "Low": "Low"
        }
        
        return mapping.get(severity, "Medium")
    
    def _cvss_to_risk_level(self, cvss_score: float) -> str:
        """
        Convert CVSS score to risk level.
        
        Args:
            cvss_score: CVSS score
            
        Returns:
            Risk level string
        """
        if cvss_score >= 9.0:
            return "High"
        elif cvss_score >= 7.0:
            return "High"
        elif cvss_score >= 4.0:
            return "Medium"
        else:
            return "Low"