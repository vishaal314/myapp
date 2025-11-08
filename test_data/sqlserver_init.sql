-- SQL Server Test Database Initialization
-- DataGuardian Pro - Database Scanner Patent Testing

-- Create test database
IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'test_db')
BEGIN
    CREATE DATABASE test_db;
END
GO

USE test_db;
GO

-- Drop tables if they exist
IF OBJECT_ID('orders', 'U') IS NOT NULL DROP TABLE orders;
IF OBJECT_ID('medical_records', 'U') IS NOT NULL DROP TABLE medical_records;
IF OBJECT_ID('employees', 'U') IS NOT NULL DROP TABLE employees;
IF OBJECT_ID('customers', 'U') IS NOT NULL DROP TABLE customers;
IF OBJECT_ID('products', 'U') IS NOT NULL DROP TABLE products;
GO

-- Customers table with PII
CREATE TABLE customers (
    id INT IDENTITY(1,1) PRIMARY KEY,
    email NVARCHAR(255),
    full_name NVARCHAR(255),
    phone NVARCHAR(50),
    bsn NVARCHAR(9),
    credit_card NVARCHAR(20),
    created_at DATETIME2 DEFAULT GETDATE()
);

-- Employees table with PII
CREATE TABLE employees (
    id INT IDENTITY(1,1) PRIMARY KEY,
    employee_email NVARCHAR(255),
    employee_name NVARCHAR(255),
    burgerservicenummer NVARCHAR(9),
    salary DECIMAL(10, 2),
    hire_date DATE,
    ssn NVARCHAR(11)
);

-- Medical records with sensitive health data
CREATE TABLE medical_records (
    record_id INT IDENTITY(1,1) PRIMARY KEY,
    patient_bsn NVARCHAR(9),
    patient_name NVARCHAR(255),
    diagnosis NVARCHAR(MAX),
    prescription NVARCHAR(MAX),
    doctor_email NVARCHAR(255),
    treatment_date DATE
);

-- Orders table with payment info
CREATE TABLE orders (
    order_id INT IDENTITY(1,1) PRIMARY KEY,
    customer_email NVARCHAR(255),
    card_number NVARCHAR(20),
    card_cvv NVARCHAR(4),
    billing_address NVARCHAR(MAX),
    order_total DECIMAL(10, 2),
    order_date DATETIME2 DEFAULT GETDATE()
);

-- Insert test data with Netherlands-specific PII
INSERT INTO customers (email, full_name, phone, bsn, credit_card) VALUES
('jan.de.vries@gmail.com', 'Jan de Vries', '+31612345678', '111222333', '4532-1234-5678-9010'),
('maria.jansen@hotmail.nl', 'Maria Jansen', '0612345679', '222333444', '5425-2345-6789-0123'),
('peter.bakker@outlook.com', 'Peter Bakker', '+31687654321', '333444555', '4916-3456-7890-1234'),
('sophie.visser@yahoo.nl', 'Sophie Visser', '0698765432', '444555666', '3782-4567-8901-2345'),
('lucas.de.jong@gmail.com', 'Lucas de Jong', '+31623456789', '555666777', '6011-5678-9012-3456');

INSERT INTO employees (employee_email, employee_name, burgerservicenummer, salary, hire_date, ssn) VALUES
('admin@dataguardian.nl', 'Hendrik van Dam', '123456782', 75000.00, '2020-01-15', '123-45-6789'),
('manager@dataguardian.nl', 'Emma Smit', '234567893', 85000.00, '2019-06-20', '234-56-7890'),
('dev@dataguardian.nl', 'Daan Mulder', '345678904', 65000.00, '2021-03-10', '345-67-8901'),
('hr@dataguardian.nl', 'Lisa Vermeulen', '456789015', 55000.00, '2022-08-05', '456-78-9012');

INSERT INTO medical_records (patient_bsn, patient_name, diagnosis, prescription, doctor_email, treatment_date) VALUES
('111222333', 'Jan de Vries', 'Type 2 Diabetes', 'Metformin 500mg twice daily', 'dr.hendriks@hospital.nl', '2024-01-15'),
('222333444', 'Maria Jansen', 'Hypertension', 'Lisinopril 10mg daily', 'dr.peters@clinic.nl', '2024-02-20'),
('333444555', 'Peter Bakker', 'Asthma', 'Albuterol inhaler as needed', 'dr.de.boer@medical.nl', '2024-03-10'),
('444555666', 'Sophie Visser', 'Depression', 'Sertraline 50mg daily', 'dr.van.dijk@psych.nl', '2024-04-05');

INSERT INTO orders (customer_email, card_number, card_cvv, billing_address, order_total) VALUES
('jan.de.vries@gmail.com', '4532-1234-5678-9010', '123', 'Hoofdstraat 123, 1011 AB Amsterdam', 299.99),
('maria.jansen@hotmail.nl', '5425-2345-6789-0123', '456', 'Marktplein 45, 3011 CD Rotterdam', 149.50),
('peter.bakker@outlook.com', '4916-3456-7890-1234', '789', 'Kerkstraat 67, 2511 EF Den Haag', 499.99),
('sophie.visser@yahoo.nl', '3782-4567-8901-2345', '234', 'Stationsweg 89, 3511 GH Utrecht', 89.95),
('lucas.de.jong@gmail.com', '6011-5678-9012-3456', '567', 'Dorpsstraat 12, 5611 IJ Eindhoven', 199.00);

-- Create some non-PII tables for comparison
CREATE TABLE products (
    product_id INT IDENTITY(1,1) PRIMARY KEY,
    product_name NVARCHAR(255),
    category NVARCHAR(100),
    price DECIMAL(10, 2),
    stock_quantity INT
);

INSERT INTO products (product_name, category, price, stock_quantity) VALUES
('Laptop', 'Electronics', 999.99, 50),
('Office Chair', 'Furniture', 299.99, 100),
('Coffee Maker', 'Appliances', 79.99, 200);
GO
