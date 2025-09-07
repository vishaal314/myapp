"""
This file contains intentionally vulnerable code samples to test the detection capabilities
of the DataGuardian Pro scanner. DO NOT USE IN PRODUCTION.
"""

# Test Case 1: Hardcoded credentials
username = "admin"
password = "admin123"  # INTENTIONAL VULNERABILITY: Hardcoded password

# Test Case 2: SQL Injection vulnerability
def get_user(user_id):
    query = "SELECT * FROM users WHERE id = " + user_id  # INTENTIONAL VULNERABILITY: SQL Injection
    # Execute the query...
    return execute_query(query)

# Test Case 3: Cross-site scripting (XSS)
def render_comment(comment):
    html = "<div>" + comment + "</div>"  # INTENTIONAL VULNERABILITY: XSS
    return html

# Test Case 4: Path traversal
def get_file(filename):
    with open("data/" + filename, "r") as f:  # INTENTIONAL VULNERABILITY: Path traversal
        return f.read()

# Test Case 5: Insecure deserialization
import pickle
def load_object(serialized_data):
    return pickle.loads(serialized_data)  # INTENTIONAL VULNERABILITY: Insecure deserialization

# Test Case 6: Hardcoded API keys
API_KEY = "sk_live_abcdefghijklmnopqrstuvwxyz123456"  # INTENTIONAL VULNERABILITY: API key
STRIPE_SECRET = "sk_test_ABCDEFGhijklMNOPQRstuvwxyz1234"  # Test API key

# Test Case 7: Personal information in code
customer_email = "john.doe@example.com"  # Email address
phone_number = "+31 20 123 4567"  # Phone number
home_address = "123 Main Street, Amsterdam, 1234 AB"  # Address
credit_card = "4111-1111-1111-1111"  # Credit card number

# Test Case 8: Insecure cookie handling
def set_cookie(response):
    response.headers["Set-Cookie"] = "session=123456; Path=/"  # INTENTIONAL VULNERABILITY: Missing Secure and HttpOnly flags

# Test Case 9: CSRF vulnerability
def csrf_exempt(func):
    """Mock CSRF exempt decorator for testing"""
    return func

@csrf_exempt  # INTENTIONAL VULNERABILITY: CSRF protection disabled
def update_profile(request):
    # Process the form...
    pass

# Test Case 10: Weak cryptography
import hashlib
def hash_password(password):
    return hashlib.md5(password.encode()).hexdigest()  # INTENTIONAL VULNERABILITY: MD5 is weak

# Mocked function to avoid errors
def execute_query(query):
    return []