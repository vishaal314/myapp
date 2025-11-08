-- MySQL Test Database Initialization
-- DataGuardian Pro - Database Scanner Patent Testing

USE test_db;

-- Drop tables if they exist
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS medical_records;
DROP TABLE IF EXISTS employees;
DROP TABLE IF EXISTS customers;

-- Customers table with PII
CREATE TABLE customers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255),
    full_name VARCHAR(255),
    phone VARCHAR(50),
    bsn VARCHAR(9),
    credit_card VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Employees table with PII
CREATE TABLE employees (
    id INT AUTO_INCREMENT PRIMARY KEY,
    employee_email VARCHAR(255),
    employee_name VARCHAR(255),
    burgerservicenummer VARCHAR(9),
    salary DECIMAL(10, 2),
    hire_date DATE,
    ssn VARCHAR(11)
);

-- Medical records with sensitive health data
CREATE TABLE medical_records (
    record_id INT AUTO_INCREMENT PRIMARY KEY,
    patient_bsn VARCHAR(9),
    patient_name VARCHAR(255),
    diagnosis TEXT,
    prescription TEXT,
    doctor_email VARCHAR(255),
    treatment_date DATE
);

-- Orders table with payment info
CREATE TABLE orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_email VARCHAR(255),
    card_number VARCHAR(20),
    card_cvv VARCHAR(4),
    billing_address TEXT,
    order_total DECIMAL(10, 2),
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    product_name VARCHAR(255),
    category VARCHAR(100),
    price DECIMAL(10, 2),
    stock_quantity INT
);

INSERT INTO products (product_name, category, price, stock_quantity) VALUES
('Laptop', 'Electronics', 999.99, 50),
('Office Chair', 'Furniture', 299.99, 100),
('Coffee Maker', 'Appliances', 79.99, 200);
