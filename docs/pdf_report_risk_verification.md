# Risk Categorization in PDF Reports: Verification Guide

This runbook provides step-by-step instructions for verifying that risk categories are consistently rendered and exported in PDF reports. This verification process should be conducted after any changes to the risk categorization system.

## Overview

PDF reports are a critical output of the DataGuardian Pro system, and they must accurately display risk categorization information. This guide helps ensure that risk levels are consistently displayed in generated PDF reports.

## Prerequisites

- DataGuardian Pro system running
- Sample repository with known GDPR compliance issues
- Database connection working
- Access to generated PDF reports

## Verification Steps

### 1. Setup Testing Environment

1. Start the application with a clean database state
2. Ensure that risk categorization modules are correctly loaded
3. Prepare a test repository with known GDPR issues of each risk level

### 2. Run a Repository Scan

1. Enter a test repository URL in the Repository Scanner
2. Select a branch and scan configuration
3. Run the scan and wait for completion
4. Verify that the scan completes without errors

### 3. Check Web UI Risk Display

Before checking PDF reports, verify the web UI:

1. Examine the Risk Summary section
   - Ensure High, Medium, and Low risk items are correctly counted
   - Verify the Compliance Score calculation

2. Check the Findings Table
   - Verify each finding has the expected risk level
   - Check that risk levels are consistently capitalized
   - Ensure the color-coding matches our standard (Red for High, Orange for Medium, Green for Low)

3. Check the Risk Breakdown section
   - Verify that the breakdown by category is accurate
   - Check that the risk scores are correctly calculated

### 4. Generate a PDF Report

1. Click the "Generate PDF Report" button
2. Wait for the PDF generation to complete
3. Download the generated PDF report

### 5. Verify PDF Report Risk Display

Open the PDF report and check the following:

1. Executive Summary
   - Compliance Score matches the web UI
   - Compliance Status matches the expected status based on the score
   - Risk counts match the web UI (High, Medium, Low)

2. Risk Breakdown
   - Breakdown by category matches the web UI
   - Chart colors correspond to risk levels consistently

3. Findings Section
   - High Risk Section:
     - All findings with "High" risk level appear here
     - Each finding displays the correct risk level
     - Risk level labels use the standardized display name ("Critical")
     - Risk level is color-coded correctly (Red)

   - Medium Risk Section:
     - All findings with "Medium" risk level appear here
     - Each finding displays the correct risk level
     - Risk level labels use the standardized display name ("Warning")
     - Risk level is color-coded correctly (Orange)

   - Low Risk Section:
     - All findings with "Low" risk level appear here
     - Each finding displays the correct risk level
     - Risk level labels use the standardized display name ("Info")
     - Risk level is color-coded correctly (Green)

4. Remediation Section
   - Verify that remediation priorities match expected values
   - Check priority color-coding is consistent

### 6. Test Mixed Risk Levels

1. Run a scan on a repository with mixed risk levels
2. Generate a PDF report
3. Verify that mixed risk levels are correctly aggregated and displayed

### 7. Test Edge Cases

1. Repository with no findings (all passed):
   - Verify "Compliant" status
   - Check that "Passed Checks" section appears correctly

2. Repository with only high-risk findings:
   - Verify "Non-Compliant" status
   - Check score calculation is correct

3. Repository with many findings (stress test):
   - Verify that large numbers of findings don't break the layout
   - Check that risk aggregation works correctly

## Verification Checklist

Use this checklist to mark each verification step:

- [ ] Web UI risk display is consistent with standardized risk levels
- [ ] PDF report executive summary contains correct risk counts
- [ ] PDF report risk breakdown matches web UI
- [ ] High risk findings are correctly displayed and styled
- [ ] Medium risk findings are correctly displayed and styled
- [ ] Low risk findings are correctly displayed and styled
- [ ] Mixed risk levels are correctly aggregated
- [ ] Edge cases (clean repo, high-risk only, large number of findings) display correctly

## Troubleshooting

### Common Issues and Resolutions

1. **Inconsistent Risk Level Capitalization**
   - Check `gdpr_risk_categories.py` for correct enum values
   - Verify that `map_severity_to_risk_level` is being used consistently

2. **Missing Risk Levels in PDF**
   - Check `pdf_report_config.py` for complete risk level definitions
   - Verify PDF generator is using these configurations

3. **Incorrect Risk Color-Coding**
   - Check color definitions in `pdf_report_config.py`
   - Verify that colors are correctly applied in PDF templates

4. **Risk Aggregation Issues**
   - Check the `merge_risk_counts` function for correct implementation
   - Verify normalization logic is working correctly

## Contact Information

For issues with risk categorization in PDF reports, contact:

- GDPR Scanner Team: gdpr-scanner@example.com
- Reporting Team: reporting@example.com