#!/usr/bin/env python3
"""
Local SQL Server Test Data Setup (for Docker on local machine)
Run this AFTER starting SQL Server container with Docker
"""

import pymssql
import sys

print("="*80)
print("📝 SQL Server Test Data Setup (Local Docker)")
print("="*80)

# Connection parameters
server = 'localhost'
user = 'sa'
password = 'DataGuard!2024'
port = 1433

try:
    print("\n🔌 Connecting to SQL Server...")
    
    # Connect to master
    conn = pymssql.connect(server=server, user=user, password=password, port=port, database='master')
    cursor = conn.cursor()
    print("  ✓ Connected to master database")
    
    # Create database
    print("\n📦 Creating ComplianceTest database...")
    cursor.execute("IF EXISTS (SELECT * FROM sys.databases WHERE name = 'ComplianceTest') DROP DATABASE ComplianceTest")
    cursor.execute("CREATE DATABASE ComplianceTest")
    conn.commit()
    conn.close()
    print("  ✓ Database created")
    
    # Connect to new database
    conn = pymssql.connect(server=server, user=user, password=password, port=port, database='ComplianceTest')
    cursor = conn.cursor()
    
    # Create tables
    print("\n📊 Creating tables...")
    
    cursor.execute("""
    CREATE TABLE Customers (
        CustomerID INT PRIMARY KEY,
        Name NVARCHAR(100),
        BSN VARCHAR(9),
        Email NVARCHAR(100),
        Phone VARCHAR(15),
        IBAN VARCHAR(34),
        KvKNumber VARCHAR(8)
    )
    """)
    
    cursor.execute("""
    CREATE TABLE Employees (
        EmployeeID INT PRIMARY KEY,
        Name NVARCHAR(100),
        BSN VARCHAR(9),
        Salary DECIMAL(10,2),
        Email NVARCHAR(100),
        Phone VARCHAR(15)
    )
    """)
    
    cursor.execute("""
    CREATE TABLE MedicalRecords (
        RecordID INT PRIMARY KEY,
        PatientBSN VARCHAR(9),
        PatientName NVARCHAR(100),
        Diagnosis NVARCHAR(200),
        DoctorEmail NVARCHAR(100)
    )
    """)
    
    print("  ✓ Tables created")
    
    # Insert Dutch PII data
    print("\n📝 Inserting Dutch PII test data...")
    
    customers = [
        (1, 'Jan de Vries', '123456782', 'jan@example.nl', '+31612345678', 'NL91ABNA0417164300', '12345678'),
        (2, 'Maria Jansen', '234567891', 'maria@bedrijf.nl', '+31687654321', 'NL20INGB0001234567', '87654321'),
        (3, 'Pieter Bakker', '345678909', 'pieter@test.nl', '+31698765432', 'NL02RABO0123456789', '11223344')
    ]
    
    for c in customers:
        cursor.execute("INSERT INTO Customers VALUES (%s, %s, %s, %s, %s, %s, %s)", c)
    
    employees = [
        (1, 'Sophie van Dam', '456789018', 45000.00, 'sophie@company.nl', '+31612987654'),
        (2, 'Thomas de Jong', '567890127', 52000.00, 'thomas@company.nl', '+31623456789')
    ]
    
    for e in employees:
        cursor.execute("INSERT INTO Employees VALUES (%s, %s, %s, %s, %s, %s)", e)
    
    medical = [
        (1, '123456782', 'Jan de Vries', 'Diabetes Type 2', 'dr.smith@hospital.nl'),
        (2, '234567891', 'Maria Jansen', 'Hypertension', 'dr.jones@clinic.nl')
    ]
    
    for m in medical:
        cursor.execute("INSERT INTO MedicalRecords VALUES (%s, %s, %s, %s, %s)", m)
    
    conn.commit()
    
    # Verify
    cursor.execute("SELECT COUNT(*) FROM Customers")
    print(f"  ✓ Customers: {cursor.fetchone()[0]} records")
    
    cursor.execute("SELECT COUNT(*) FROM Employees")
    print(f"  ✓ Employees: {cursor.fetchone()[0]} records")
    
    cursor.execute("SELECT COUNT(*) FROM MedicalRecords")
    print(f"  ✓ Medical Records: {cursor.fetchone()[0]} records")
    
    print("\n✅ Test database ready!")
    print("   Server: localhost:1433")
    print("   Database: ComplianceTest")
    print("   Username: sa")
    
    print("\nNext step: python test_sqlserver_scanner.py")
    
    conn.close()
    
except ImportError:
    print("\n❌ Error: pymssql not installed")
    print("   Run: pip install pymssql")
    sys.exit(1)
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\nTroubleshooting:")
    print("1. Make sure SQL Server container is running:")
    print("   docker ps | grep sqlserver")
    print("2. Check password matches Docker command")
    print("3. Wait 30 seconds after starting container")
    sys.exit(1)
