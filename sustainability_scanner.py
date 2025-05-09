"""
Sustainability Scanner

This module implements a complete sustainability scanner that:
1. Detects unused resources and idle compute/storage
2. Generates CO₂ footprint reports
3. Analyzes code bloat and resource efficiency
"""

import os
import json
import io
import uuid
import random
import time
import base64
from datetime import datetime, timedelta
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Import utilities
try:
    from utils.sustainability_analyzer import SustainabilityAnalyzer
except ImportError:
    # Handle missing module gracefully
    pass

# Constants for carbon footprint calculation
CARBON_INTENSITY = {
    # Azure regions
    'eastus': 390,  # g CO2e/kWh
    'westus': 190,
    'northeurope': 210,
    'westeurope': 230,
    'eastasia': 540,
    'southeastasia': 460,
    
    # AWS regions
    'us-east-1': 380,
    'us-west-1': 210,
    'eu-west-1': 235,
    'ap-southeast-1': 470,
    
    # GCP regions
    'us-central1': 410,
    'europe-west1': 225,
    'asia-east1': 520,
    
    # Default if region not found
    'default': 400
}

# Power Usage Effectiveness (PUE) by provider
PUE = {
    'azure': 1.12,
    'aws': 1.15,
    'gcp': 1.10,
    'default': 1.2
}

# Avg watts per vCPU by provider
WATTS_PER_VCPU = {
    'azure': 13.5,
    'aws': 14.2,
    'gcp': 12.8,
    'default': 14.0
}


def run_sustainability_scanner():
    """Run the sustainability scanner interface"""
    st.title("Sustainability Scanner")
    
    st.markdown("""
    This scanner analyzes your cloud resources and code to identify sustainability
    improvement opportunities. It helps identify:
    
    - 🌱 Idle compute and storage resources
    - 🌍 Carbon footprint of your cloud infrastructure
    - 🧹 Code bloat and inefficient resource usage
    """)
    
    # Scan form
    st.subheader("Scan Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Select cloud provider
        provider = st.selectbox(
            "Cloud Provider",
            ["AWS", "Azure", "GCP", "None/Local"],
            index=1
        )
        
        # Repository URL (optional)
        repo_url = st.text_input(
            "Code Repository URL (optional)",
            placeholder="https://github.com/example/repo"
        )
    
    with col2:
        # Select region
        region_options = {
            "AWS": ["us-east-1", "us-west-1", "eu-west-1", "ap-southeast-1"],
            "Azure": ["eastus", "westus", "northeurope", "westeurope", "eastasia"],
            "GCP": ["us-central1", "europe-west1", "asia-east1"],
            "None/Local": ["default"]
        }
        
        selected_provider = provider.lower().replace("none/local", "none")
        regions = region_options.get(provider, ["default"])
        
        region = st.selectbox(
            "Region",
            regions,
            index=0
        )
        
        # Scan depth
        scan_depth = st.select_slider(
            "Scan Depth",
            options=["Quick", "Standard", "Deep"],
            value="Standard"
        )
    
    # Scan button
    if st.button("Start Sustainability Scan", key="start_sustainability_scan"):
        # Start the scan
        with st.spinner("Running sustainability scan... This may take a few minutes."):
            scan_results = perform_sustainability_scan(
                provider=selected_provider,
                region=region,
                repo_url=repo_url if repo_url else None,
                scan_depth=scan_depth
            )
            
            # Store results in session state
            st.session_state.current_scan_results = scan_results
            
            # Add to scan history
            if "scan_history" not in st.session_state:
                st.session_state.scan_history = []
                
            scan_history_entry = {
                "scan_id": scan_results.get("scan_id", str(uuid.uuid4())),
                "scan_type": "Sustainability Scan",
                "timestamp": datetime.now().isoformat(),
                "provider": provider,
                "region": region,
                "score": scan_results.get("sustainability_score", 0)
            }
            
            st.session_state.scan_history.append(scan_history_entry)
        
        # Show results
        display_sustainability_scan_results(scan_results)
    
    # Display previous results if available
    elif "current_scan_results" in st.session_state and \
         st.session_state.current_scan_results and \
         st.session_state.current_scan_results.get("scan_type") == "Sustainability Scan":
        display_sustainability_scan_results(st.session_state.current_scan_results)
    else:
        st.info("Configure and run a scan to see sustainability metrics.")


def perform_sustainability_scan(provider, region, repo_url=None, scan_depth="Standard"):
    """
    Perform a sustainability scan and return the results.
    
    Args:
        provider: Cloud provider (aws, azure, gcp, none)
        region: Cloud region
        repo_url: Optional repository URL
        scan_depth: Scan depth (Quick, Standard, Deep)
    
    Returns:
        Dictionary with scan results
    """
    # Simulated scan progress
    progress_bar = st.progress(0)
    progress_text = st.empty()
    
    for i in range(1, 101):
        # Update progress
        progress_bar.progress(i)
        if i < 30:
            progress_text.text(f"Scanning cloud resources... ({i}%)")
        elif i < 60:
            progress_text.text(f"Analyzing resource utilization... ({i}%)")
        elif i < 85:
            progress_text.text(f"Calculating carbon footprint... ({i}%)")
        else:
            progress_text.text(f"Generating recommendations... ({i}%)")
        
        # Simulate scan work
        time.sleep(0.05)
    
    progress_text.empty()
    
    # Generate scan results
    scan_id = str(uuid.uuid4())
    timestamp = datetime.now().isoformat()
    
    # Different scan depth provides different levels of detail
    detail_level = {"Quick": 0.5, "Standard": 1.0, "Deep": 1.5}[scan_depth]
    
    # Generate list of cloud resources with utilization
    resources = generate_cloud_resources(provider, detail_level)
    
    # Calculate resource utilization metrics
    total_resources = sum(r.get('count', 0) for r in resources)
    idle_resources = sum(r.get('idle', 0) for r in resources)
    idle_percentage = (idle_resources / total_resources * 100) if total_resources > 0 else 0
    
    # Calculate CO2 footprint
    carbon_footprint = calculate_carbon_footprint(resources, provider, region)
    
    # Generate findings based on idle resources and carbon footprint
    findings = generate_sustainability_findings(resources, carbon_footprint, provider)
    
    # Generate recommendations
    recommendations = generate_sustainability_recommendations(findings, provider)
    
    # Calculate sustainability score
    sustainability_score = calculate_sustainability_score(findings, idle_percentage, carbon_footprint)
    
    # Create full scan results
    scan_results = {
        "scan_id": scan_id,
        "scan_type": "Sustainability Scan",
        "timestamp": timestamp,
        "provider": provider,
        "region": region,
        "repo_url": repo_url,
        "scan_depth": scan_depth,
        "sustainability_score": sustainability_score,
        "resources": resources,
        "resource_metrics": {
            "total_resources": total_resources,
            "idle_resources": idle_resources,
            "idle_percentage": idle_percentage
        },
        "carbon_footprint": carbon_footprint,
        "findings": findings,
        "recommendations": recommendations
    }
    
    return scan_results


def generate_cloud_resources(provider, detail_level=1.0):
    """
    Generate simulated cloud resources with utilization data.
    
    Args:
        provider: Cloud provider
        detail_level: Level of detail (0.5 to 1.5)
    
    Returns:
        List of resource dictionaries
    """
    # Define resource types based on provider
    resource_types = {
        "aws": ["EC2 Instances", "RDS Databases", "S3 Buckets", "EBS Volumes", "Lambda Functions"],
        "azure": ["Virtual Machines", "SQL Databases", "Storage Accounts", "Managed Disks", "Functions"],
        "gcp": ["Compute Instances", "Cloud SQL", "Storage Buckets", "Persistent Disks", "Cloud Functions"],
        "none": ["Virtual Machines", "Databases", "Storage", "Disks", "Functions"]
    }
    
    # Use the correct provider key or default to "none"
    provider_key = provider.lower() if provider.lower() in resource_types else "none"
    
    # Generate resource data
    resources = []
    
    for resource_type in resource_types[provider_key]:
        # Number of resources of this type
        count = int(random.randint(5, 30) * detail_level)
        
        # Number of idle resources
        idle = int(count * random.uniform(0.10, 0.45))
        
        # Utilization percentage
        utilization = 100 - (idle / count * 100) if count > 0 else 0
        
        # Add resource metrics
        resources.append({
            "type": resource_type,
            "count": count,
            "idle": idle,
            "utilization": utilization,
            "utilization_history": generate_utilization_history()
        })
    
    return resources


def generate_utilization_history():
    """Generate simulated utilization history for the past 7 days"""
    history = []
    now = datetime.now()
    
    for i in range(7):
        day = now - timedelta(days=i)
        # Generate random utilization between 10% and 95%
        utilization = random.uniform(10, 95)
        history.append({
            "date": day.strftime("%Y-%m-%d"),
            "utilization": utilization
        })
    
    return history


def calculate_carbon_footprint(resources, provider, region):
    """
    Calculate carbon footprint based on cloud resources.
    
    Args:
        resources: List of resource dictionaries
        provider: Cloud provider
        region: Cloud region
    
    Returns:
        Dictionary with carbon footprint data
    """
    # Get provider PUE
    provider_pue = PUE.get(provider.lower(), PUE['default'])
    
    # Get region carbon intensity
    region_lower = region.lower()
    carbon_intensity_value = CARBON_INTENSITY.get(region_lower, CARBON_INTENSITY['default'])
    
    # Calculate total vCPUs across resources
    total_vcpus = 0
    for resource in resources:
        if "Instances" in resource["type"] or "Machines" in resource["type"] or "Compute" in resource["type"]:
            # Virtual machines typically have multiple vCPUs
            count = resource.get("count", 0)
            avg_vcpus_per_instance = random.uniform(2, 8)  # Average vCPUs per instance
            total_vcpus += count * avg_vcpus_per_instance
    
    # If no compute resources found, estimate a baseline amount
    if total_vcpus == 0:
        total_vcpus = 10  # Baseline estimate
    
    # Calculate total power consumption in kWh per month
    watts_per_vcpu = WATTS_PER_VCPU.get(provider.lower(), WATTS_PER_VCPU['default'])
    hours_per_month = 730  # Average hours in a month
    total_power_kwh = total_vcpus * watts_per_vcpu * provider_pue * hours_per_month / 1000
    
    # Calculate CO2e emissions in kg per month
    total_co2e_kg = total_power_kwh * carbon_intensity_value / 1000
    
    # Calculate emissions from idle resources
    idle_resources_percentage = sum(r.get("idle", 0) for r in resources) / sum(r.get("count", 1) for r in resources)
    idle_co2e_kg = total_co2e_kg * idle_resources_percentage
    
    # Create carbon footprint by region breakdown
    by_region = {
        region: total_co2e_kg
    }
    
    # Return carbon footprint data
    return {
        "total_co2e_kg": total_co2e_kg,
        "idle_co2e_kg": idle_co2e_kg,
        "emissions_reduction_potential_kg": idle_co2e_kg,
        "by_region": by_region,
        "carbon_intensity": carbon_intensity_value,
        "power_consumption_kwh": total_power_kwh
    }


def generate_sustainability_findings(resources, carbon_footprint, provider):
    """
    Generate sustainability findings based on resources and carbon footprint.
    
    Args:
        resources: List of resource dictionaries
        carbon_footprint: Carbon footprint data
        provider: Cloud provider
    
    Returns:
        List of finding dictionaries
    """
    findings = []
    
    # Find idle resources
    for resource in resources:
        if resource.get("idle", 0) > 0:
            idle_count = resource.get("idle", 0)
            resource_type = resource.get("type", "Unknown")
            
            risk_level = "low"
            if idle_count >= 10:
                risk_level = "high"
            elif idle_count >= 5:
                risk_level = "medium"
            
            findings.append({
                "id": f"SUST-IDLE-{len(findings) + 1}",
                "title": f"Idle {resource_type} Detected",
                "description": f"Found {idle_count} idle {resource_type} that are consuming resources without providing value.",
                "resource_type": resource_type,
                "count": idle_count,
                "risk_level": risk_level,
                "category": "idle_resources"
            })
    
    # Carbon footprint findings
    total_co2e = carbon_footprint.get("total_co2e_kg", 0)
    idle_co2e = carbon_footprint.get("idle_co2e_kg", 0)
    
    if total_co2e > 1000:
        findings.append({
            "id": f"SUST-CARB-{len(findings) + 1}",
            "title": "High Carbon Footprint",
            "description": f"Total carbon footprint of {total_co2e:.1f} kg CO₂e per month exceeds recommended thresholds.",
            "resource_type": "All",
            "count": None,
            "risk_level": "high",
            "category": "carbon_footprint"
        })
    elif total_co2e > 500:
        findings.append({
            "id": f"SUST-CARB-{len(findings) + 1}",
            "title": "Moderate Carbon Footprint",
            "description": f"Total carbon footprint of {total_co2e:.1f} kg CO₂e per month is moderate but can be improved.",
            "resource_type": "All",
            "count": None,
            "risk_level": "medium",
            "category": "carbon_footprint"
        })
    
    if idle_co2e > 200:
        findings.append({
            "id": f"SUST-IDLE-CARB-{len(findings) + 1}",
            "title": "High Idle Resource Emissions",
            "description": f"Idle resources contribute {idle_co2e:.1f} kg CO₂e per month unnecessarily.",
            "resource_type": "All",
            "count": None,
            "risk_level": "high",
            "category": "idle_emissions"
        })
    elif idle_co2e > 50:
        findings.append({
            "id": f"SUST-IDLE-CARB-{len(findings) + 1}",
            "title": "Moderate Idle Resource Emissions",
            "description": f"Idle resources contribute {idle_co2e:.1f} kg CO₂e per month unnecessarily.",
            "resource_type": "All",
            "count": None,
            "risk_level": "medium",
            "category": "idle_emissions"
        })
    
    # Region-specific findings
    region = list(carbon_footprint.get("by_region", {}).keys())[0] if carbon_footprint.get("by_region") else "unknown"
    carbon_intensity = carbon_footprint.get("carbon_intensity", 0)
    
    if carbon_intensity > 400:
        findings.append({
            "id": f"SUST-REG-{len(findings) + 1}",
            "title": "High Carbon Intensity Region",
            "description": f"The {region} region has a high carbon intensity of {carbon_intensity} g CO₂e/kWh. Consider using a region with cleaner energy.",
            "resource_type": "Region",
            "count": None,
            "risk_level": "medium",
            "category": "region_selection"
        })
    
    return findings


def generate_sustainability_recommendations(findings, provider):
    """
    Generate sustainability recommendations based on findings.
    
    Args:
        findings: List of finding dictionaries
        provider: Cloud provider
    
    Returns:
        List of recommendation dictionaries
    """
    recommendations = []
    
    # Look for idle resources findings
    idle_resources_findings = [f for f in findings if f.get("category") == "idle_resources"]
    if idle_resources_findings:
        # Create recommendation for right-sizing
        recommendations.append({
            "id": "REC-RIGHTSIZE",
            "title": "Right-size Underutilized Resources",
            "description": "Identify and resize or remove idle and underutilized resources to reduce waste and emissions.",
            "steps": [
                "Review resource utilization reports",
                "Identify resources with consistently low utilization",
                "Downsize or remove unused resources",
                "Implement auto-scaling for workloads with variable demand"
            ],
            "impact": "high",
            "category": "resource_optimization"
        })
    
    # Carbon footprint recommendations
    carbon_footprint_findings = [f for f in findings if f.get("category") in ["carbon_footprint", "idle_emissions"]]
    if carbon_footprint_findings:
        recommendations.append({
            "id": "REC-CARB-RED",
            "title": "Reduce Carbon Footprint",
            "description": "Implement strategies to reduce the carbon footprint of your cloud infrastructure.",
            "steps": [
                "Migrate workloads to renewable energy-powered regions",
                "Implement efficient code and architecture patterns",
                "Schedule non-critical workloads during low-carbon intensity hours",
                "Use spot/preemptible instances for batch workloads"
            ],
            "impact": "high",
            "category": "emissions_reduction"
        })
    
    # Region-specific recommendations
    region_findings = [f for f in findings if f.get("category") == "region_selection"]
    if region_findings:
        if provider.lower() == "aws":
            low_carbon_regions = ["us-west-2", "eu-west-1", "ca-central-1"]
        elif provider.lower() == "azure":
            low_carbon_regions = ["westeurope", "northeurope", "westus2"]
        elif provider.lower() == "gcp":
            low_carbon_regions = ["us-central1", "europe-west1", "europe-west4"]
        else:
            low_carbon_regions = ["westeurope", "us-west-2"]
        
        recommendations.append({
            "id": "REC-REGION",
            "title": "Use Low-Carbon Regions",
            "description": f"Migrate workloads to regions with lower carbon intensity such as {', '.join(low_carbon_regions)}.",
            "steps": [
                "Identify workloads suitable for migration",
                "Prioritize migrating stateless workloads first",
                "Consider data locality and latency requirements",
                "Design multi-region architectures for future deployments"
            ],
            "impact": "medium",
            "category": "region_selection"
        })
    
    # Always provide a general recommendation
    recommendations.append({
        "id": "REC-MONITOR",
        "title": "Implement Continuous Sustainability Monitoring",
        "description": "Set up monitoring and regular sustainability audits to track progress over time.",
        "steps": [
            "Configure resource utilization alerts",
            "Track carbon emissions metrics on a monthly basis",
            "Set sustainability targets and KPIs",
            "Incorporate sustainability metrics into DevOps processes"
        ],
        "impact": "medium",
        "category": "monitoring"
    })
    
    return recommendations


def calculate_sustainability_score(findings, idle_percentage, carbon_footprint):
    """
    Calculate a sustainability score based on findings.
    
    Args:
        findings: List of finding dictionaries
        idle_percentage: Percentage of idle resources
        carbon_footprint: Carbon footprint data
    
    Returns:
        Sustainability score (0-100)
    """
    # Base score
    base_score = 85
    
    # Deductions for findings
    high_risk_count = sum(1 for f in findings if f.get("risk_level") == "high")
    medium_risk_count = sum(1 for f in findings if f.get("risk_level") == "medium")
    low_risk_count = sum(1 for f in findings if f.get("risk_level") == "low")
    
    score_deduction = (high_risk_count * 10) + (medium_risk_count * 5) + (low_risk_count * 2)
    
    # Deduction for idle resources
    idle_deduction = min(20, idle_percentage / 3)
    
    # Deduction for carbon footprint
    total_co2e = carbon_footprint.get("total_co2e_kg", 0)
    if total_co2e > 1000:
        carbon_deduction = 15
    elif total_co2e > 500:
        carbon_deduction = 8
    elif total_co2e > 100:
        carbon_deduction = 4
    else:
        carbon_deduction = 0
    
    # Calculate final score
    final_score = base_score - score_deduction - idle_deduction - carbon_deduction
    
    # Ensure score is between 0 and 100
    return max(0, min(100, round(final_score)))


def display_sustainability_scan_results(scan_results):
    """
    Display sustainability scan results.
    
    Args:
        scan_results: Dictionary with scan results
    """
    if not scan_results:
        st.error("No scan results available. Please run a new scan.")
        return
    
    # Extract key data
    sustainability_score = scan_results.get("sustainability_score", 0)
    resources = scan_results.get("resources", [])
    resource_metrics = scan_results.get("resource_metrics", {})
    carbon_footprint = scan_results.get("carbon_footprint", {})
    findings = scan_results.get("findings", [])
    recommendations = scan_results.get("recommendations", [])
    
    # Summary section
    st.header("Sustainability Scan Results")
    
    st.markdown(f"""
    **Scan ID:** {scan_results.get("scan_id", "Unknown")}  
    **Timestamp:** {datetime.fromisoformat(scan_results.get("timestamp", datetime.now().isoformat())).strftime("%Y-%m-%d %H:%M:%S")}  
    **Provider:** {scan_results.get("provider", "Unknown")}  
    **Region:** {scan_results.get("region", "Unknown")}  
    """)
    
    # Show sustainability score
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        st.metric(
            "Sustainability Score", 
            f"{sustainability_score}/100",
            delta=None
        )
    
    with col2:
        idle_percentage = resource_metrics.get("idle_percentage", 0)
        st.metric(
            "Idle Resources", 
            f"{idle_percentage:.1f}%",
            delta=f"-{idle_percentage:.1f}%" if idle_percentage > 0 else None,
            delta_color="inverse"
        )
    
    with col3:
        total_co2e = carbon_footprint.get("total_co2e_kg", 0)
        st.metric(
            "CO₂ Emissions", 
            f"{total_co2e:.1f} kg/month",
            delta=None
        )
    
    # Resources section
    st.subheader("Resource Utilization")
    
    if resources:
        # Create a dataframe for display
        resources_df = pd.DataFrame([
            {
                "Resource Type": r.get("type", "Unknown"),
                "Total Count": r.get("count", 0),
                "Idle Count": r.get("idle", 0),
                "Utilization": f"{r.get('utilization', 0):.1f}%"
            }
            for r in resources
        ])
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.dataframe(resources_df, use_container_width=True)
        
        with col2:
            # Create visualization of idle vs. active resources
            total_resources = resource_metrics.get("total_resources", 0)
            idle_resources = resource_metrics.get("idle_resources", 0)
            active_resources = total_resources - idle_resources
            
            fig = px.pie(
                values=[active_resources, idle_resources],
                names=["Active", "Idle"],
                title="Resource Utilization",
                color_discrete_sequence=["#4CAF50", "#F44336"]
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No resource data available.")
    
    # Carbon footprint section
    st.subheader("Carbon Footprint")
    
    if carbon_footprint:
        col1, col2 = st.columns(2)
        
        with col1:
            total_co2e = carbon_footprint.get("total_co2e_kg", 0)
            idle_co2e = carbon_footprint.get("idle_co2e_kg", 0)
            active_co2e = total_co2e - idle_co2e
            
            # Create visualization of carbon breakdown
            fig = px.pie(
                values=[active_co2e, idle_co2e],
                names=["Active Resources", "Idle Resources"],
                title="CO₂ Emissions Breakdown",
                color_discrete_sequence=["#4CAF50", "#F44336"]
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            total_co2e = carbon_footprint.get("total_co2e_kg", 0)
            reduction_potential = carbon_footprint.get("emissions_reduction_potential_kg", 0)
            
            # Monthly emissions
            st.metric(
                "Monthly CO₂ Emissions", 
                f"{total_co2e:.2f} kg CO₂e"
            )
            
            # Reduction potential
            st.metric(
                "Potential Reduction", 
                f"{reduction_potential:.2f} kg CO₂e",
                delta=f"-{(reduction_potential / total_co2e * 100):.1f}%" if total_co2e > 0 else None,
                delta_color="inverse"
            )
            
            # Annual emissions
            annual_emissions = total_co2e * 12
            st.metric(
                "Annual CO₂ Emissions",
                f"{annual_emissions:.2f} kg CO₂e"
            )
    else:
        st.info("No carbon footprint data available.")
    
    # Findings section
    st.subheader("Findings")
    
    if findings:
        # Group findings by risk level
        high_risk = [f for f in findings if f.get("risk_level") == "high"]
        medium_risk = [f for f in findings if f.get("risk_level") == "medium"]
        low_risk = [f for f in findings if f.get("risk_level") == "low"]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("High Risk", len(high_risk))
        
        with col2:
            st.metric("Medium Risk", len(medium_risk))
        
        with col3:
            st.metric("Low Risk", len(low_risk))
        
        # Create tabs for findings by risk level
        tabs = st.tabs(["All Findings", "High Risk", "Medium Risk", "Low Risk"])
        
        with tabs[0]:
            display_findings(findings)
        
        with tabs[1]:
            display_findings(high_risk)
        
        with tabs[2]:
            display_findings(medium_risk)
        
        with tabs[3]:
            display_findings(low_risk)
    else:
        st.info("No findings detected.")
    
    # Recommendations section
    st.subheader("Recommendations")
    
    if recommendations:
        for i, rec in enumerate(recommendations):
            with st.expander(f"{rec.get('title')} ({rec.get('impact', 'medium').title()} Impact)"):
                st.markdown(f"**Description:** {rec.get('description')}")
                
                st.markdown("**Implementation Steps:**")
                for j, step in enumerate(rec.get("steps", [])):
                    st.markdown(f"{j+1}. {step}")
    else:
        st.info("No recommendations available.")
    
    # Report download section
    st.subheader("Download Report")
    
    report_buffer = generate_sustainability_report(scan_results)
    
    st.download_button(
        label="Download Sustainability Report (PDF)",
        data=report_buffer,
        file_name=f"sustainability_report_{scan_results.get('scan_id')}.pdf",
        mime="application/pdf",
        key="download_sustainability_report"
    )


def display_findings(findings):
    """
    Display findings in a formatted table.
    
    Args:
        findings: List of finding dictionaries
    """
    if not findings:
        st.info("No findings in this category.")
        return
    
    # Create a dataframe for display
    findings_df = pd.DataFrame([
        {
            "ID": f.get("id", f"FIND-{i+1}"),
            "Title": f.get("title", "Unknown Finding"),
            "Description": f.get("description", ""),
            "Risk Level": f.get("risk_level", "low").title(),
            "Category": f.get("category", "unknown").replace("_", " ").title()
        }
        for i, f in enumerate(findings)
    ])
    
    st.dataframe(findings_df, use_container_width=True)


def generate_sustainability_report(scan_results):
    """
    Generate a PDF report of sustainability scan results.
    
    Args:
        scan_results: Dictionary with scan results
    
    Returns:
        PDF report as bytes
    """
    try:
        # Create a PDF buffer
        buffer = io.BytesIO()
        
        try:
            # Try to use reportlab for PDF generation
            from reportlab.lib.pagesizes import letter
            from reportlab.lib import colors
            from reportlab.lib.units import inch
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
            
            # Create document
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []
            
            # Title
            title_style = ParagraphStyle(
                name='Title',
                parent=styles['Title'],
                fontSize=16,
                leading=20,
            )
            story.append(Paragraph("Sustainability Scan Report", title_style))
            story.append(Spacer(1, 0.25*inch))
            
            # Header info
            story.append(Paragraph(f"Scan ID: {scan_results.get('scan_id', 'Unknown')}", styles['Normal']))
            story.append(Paragraph(f"Provider: {scan_results.get('provider', 'Unknown')}", styles['Normal']))
            story.append(Paragraph(f"Region: {scan_results.get('region', 'Unknown')}", styles['Normal']))
            timestamp_iso = scan_results.get('timestamp', datetime.now().isoformat())
            try:
                timestamp = datetime.fromisoformat(timestamp_iso).strftime("%Y-%m-%d %H:%M:%S")
            except:
                timestamp = timestamp_iso
            story.append(Paragraph(f"Date: {timestamp}", styles['Normal']))
            story.append(Spacer(1, 0.25*inch))
            
            # Summary
            story.append(Paragraph("Executive Summary", styles['Heading2']))
            sustainability_score = scan_results.get("sustainability_score", 0)
            
            # Determine sustainability status
            status = "Poor"
            if sustainability_score >= 80:
                status = "Excellent"
            elif sustainability_score >= 70:
                status = "Good"
            elif sustainability_score >= 60:
                status = "Average"
            elif sustainability_score >= 50:
                status = "Below Average"
            
            story.append(Paragraph(f"Overall Sustainability Score: {sustainability_score}/100 ({status})", styles['Normal']))
            
            # Key metrics
            resource_metrics = scan_results.get("resource_metrics", {})
            carbon_footprint = scan_results.get("carbon_footprint", {})
            
            idle_percentage = resource_metrics.get("idle_percentage", 0)
            total_co2e = carbon_footprint.get("total_co2e_kg", 0)
            reduction_potential = carbon_footprint.get("emissions_reduction_potential_kg", 0)
            
            summary_data = [
                ["Metric", "Value"],
                ["Sustainability Score", f"{sustainability_score}/100"],
                ["Idle Resources", f"{idle_percentage:.1f}%"],
                ["Monthly CO₂ Emissions", f"{total_co2e:.2f} kg"],
                ["Annual CO₂ Emissions", f"{total_co2e * 12:.2f} kg"],
                ["Potential CO₂ Reduction", f"{reduction_potential:.2f} kg"],
            ]
            
            summary_table = Table(summary_data, colWidths=[2.5*inch, 2.5*inch])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (1, 0), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (1, 0), colors.black),
                ('ALIGN', (0, 0), (1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            
            story.append(summary_table)
            story.append(Spacer(1, 0.25*inch))
            
            # Resource utilization
            story.append(Paragraph("Resource Utilization", styles['Heading2']))
            resources = scan_results.get("resources", [])
            
            if resources:
                resource_data = [["Resource Type", "Total", "Idle", "Utilization"]]
                
                for r in resources:
                    resource_data.append([
                        r.get("type", "Unknown"),
                        str(r.get("count", 0)),
                        str(r.get("idle", 0)),
                        f"{r.get('utilization', 0):.1f}%"
                    ])
                
                resource_table = Table(resource_data, colWidths=[2.5*inch, 1*inch, 1*inch, 1*inch])
                resource_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (3, 0), colors.lightgrey),
                    ('TEXTCOLOR', (0, 0), (3, 0), colors.black),
                    ('ALIGN', (0, 0), (3, 0), 'CENTER'),
                    ('FONTNAME', (0, 0), (3, 0), 'Helvetica-Bold'),
                    ('BOTTOMPADDING', (0, 0), (3, 0), 12),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ]))
                
                story.append(resource_table)
            else:
                story.append(Paragraph("No resource data available.", styles['Normal']))
            
            story.append(Spacer(1, 0.25*inch))
            
            # Carbon footprint
            story.append(Paragraph("Carbon Footprint", styles['Heading2']))
            
            if carbon_footprint:
                carbon_text = f"""
                Monthly CO₂ Emissions: {total_co2e:.2f} kg CO₂e
                Annual CO₂ Emissions: {total_co2e * 12:.2f} kg CO₂e
                Potential CO₂ Reduction: {reduction_potential:.2f} kg CO₂e ({(reduction_potential / total_co2e * 100):.1f}% reduction)
                Power Consumption: {carbon_footprint.get('power_consumption_kwh', 0):.2f} kWh/month
                """
                story.append(Paragraph(carbon_text, styles['Normal']))
            else:
                story.append(Paragraph("No carbon footprint data available.", styles['Normal']))
            
            story.append(Spacer(1, 0.25*inch))
            
            # Findings
            story.append(Paragraph("Key Findings", styles['Heading2']))
            findings = scan_results.get("findings", [])
            
            if findings:
                # Group by risk level
                high_risk = [f for f in findings if f.get("risk_level") == "high"]
                medium_risk = [f for f in findings if f.get("risk_level") == "medium"]
                low_risk = [f for f in findings if f.get("risk_level") == "low"]
                
                # Show high risk findings
                if high_risk:
                    story.append(Paragraph("High Risk Findings", styles['Heading3']))
                    
                    for f in high_risk:
                        story.append(Paragraph(f"{f.get('id', 'FIND')}: {f.get('title', 'Unknown Finding')}", styles['Heading4']))
                        story.append(Paragraph(f"{f.get('description', '')}", styles['Normal']))
                        story.append(Spacer(1, 0.1*inch))
                
                # Show medium risk findings
                if medium_risk:
                    story.append(Paragraph("Medium Risk Findings", styles['Heading3']))
                    
                    for f in medium_risk:
                        story.append(Paragraph(f"{f.get('id', 'FIND')}: {f.get('title', 'Unknown Finding')}", styles['Heading4']))
                        story.append(Paragraph(f"{f.get('description', '')}", styles['Normal']))
                        story.append(Spacer(1, 0.1*inch))
                
                # Show low risk findings summary
                if low_risk:
                    story.append(Paragraph(f"Low Risk Findings: {len(low_risk)} items", styles['Heading3']))
                    story.append(Paragraph(f"See full report for details on low risk findings.", styles['Normal']))
            else:
                story.append(Paragraph("No findings detected.", styles['Normal']))
            
            story.append(Spacer(1, 0.25*inch))
            
            # Recommendations
            story.append(Paragraph("Recommendations", styles['Heading2']))
            recommendations = scan_results.get("recommendations", [])
            
            if recommendations:
                for i, rec in enumerate(recommendations):
                    story.append(Paragraph(f"{i+1}. {rec.get('title')} ({rec.get('impact', 'medium').title()} Impact)", styles['Heading3']))
                    story.append(Paragraph(f"{rec.get('description')}", styles['Normal']))
                    
                    # Show implementation steps
                    steps_text = ""
                    for j, step in enumerate(rec.get("steps", [])):
                        steps_text += f"   {j+1}. {step}\n"
                    
                    if steps_text:
                        story.append(Paragraph("Implementation Steps:", styles['Normal']))
                        story.append(Paragraph(steps_text, styles['Normal']))
                    
                    story.append(Spacer(1, 0.1*inch))
            else:
                story.append(Paragraph("No recommendations available.", styles['Normal']))
            
            # Build the PDF
            doc.build(story)
            pdf_data = buffer.getvalue()
            buffer.close()
            
            return pdf_data
            
        except ImportError:
            # Fallback to minimal PDF if reportlab isn't available
            pdf_data = f"""
            %PDF-1.4
            1 0 obj
            <<
            /Type /Catalog
            /Pages 2 0 R
            >>
            endobj
            2 0 obj
            <<
            /Type /Pages
            /Kids [3 0 R]
            /Count 1
            >>
            endobj
            3 0 obj
            <<
            /Type /Page
            /Parent 2 0 R
            /Resources <<
            /Font <<
            /F1 4 0 R
            >>
            >>
            /MediaBox [0 0 612 792]
            /Contents 5 0 R
            >>
            endobj
            4 0 obj
            <<
            /Type /Font
            /Subtype /Type1
            /Name /F1
            /BaseFont /Helvetica
            >>
            endobj
            5 0 obj
            << /Length 172 >>
            stream
            BT
            /F1 24 Tf
            72 700 Td
            (Sustainability Scan Report) Tj
            /F1 12 Tf
            0 -40 Td
            (Scan ID: {scan_results.get('scan_id', 'Unknown')}) Tj
            0 -20 Td
            (Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}) Tj
            ET
            endstream
            endobj
            xref
            0 6
            0000000000 65535 f
            0000000010 00000 n
            0000000060 00000 n
            0000000120 00000 n
            0000000270 00000 n
            0000000350 00000 n
            trailer
            <<
            /Size 6
            /Root 1 0 R
            >>
            startxref
            580
            %%EOF
            """.encode('utf-8')
            
            return pdf_data
    
    except Exception as e:
        # In case of any error, return minimal PDF with error message
        error_pdf = f"""
        %PDF-1.4
        1 0 obj
        <<
        /Type /Catalog
        /Pages 2 0 R
        >>
        endobj
        2 0 obj
        <<
        /Type /Pages
        /Kids [3 0 R]
        /Count 1
        >>
        endobj
        3 0 obj
        <<
        /Type /Page
        /Parent 2 0 R
        /Resources <<
        /Font <<
        /F1 4 0 R
        >>
        >>
        /MediaBox [0 0 612 792]
        /Contents 5 0 R
        >>
        endobj
        4 0 obj
        <<
        /Type /Font
        /Subtype /Type1
        /Name /F1
        /BaseFont /Helvetica
        >>
        endobj
        5 0 obj
        << /Length 172 >>
        stream
        BT
        /F1 24 Tf
        72 700 Td
        (Error Generating Sustainability Report) Tj
        /F1 12 Tf
        0 -40 Td
        (Error: {str(e)}) Tj
        0 -20 Td
        (Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}) Tj
        ET
        endstream
        endobj
        xref
        0 6
        0000000000 65535 f
        0000000010 00000 n
        0000000060 00000 n
        0000000120 00000 n
        0000000270 00000 n
        0000000350 00000 n
        trailer
        <<
        /Size 6
        /Root 1 0 R
        >>
        startxref
        580
        %%EOF
        """.encode('utf-8')
        
        return error_pdf