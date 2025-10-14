#!/bin/bash
# Copy Python test script into container and run it

echo "📊 Running Database Test..."
echo ""

# Copy test script into container
docker cp DB_TEST.py dataguardian-container:/tmp/db_test.py

# Run the test
docker exec dataguardian-container python3 /tmp/db_test.py

# Cleanup
docker exec dataguardian-container rm /tmp/db_test.py 2>/dev/null

echo ""
echo "Test complete!"
