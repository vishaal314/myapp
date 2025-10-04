#!/bin/bash

echo "=== CONTAINER STATUS ==="
docker ps | grep dataguardian

echo ""
echo "=== LAST 100 LINES OF LOGS ==="
docker logs dataguardian-container 2>&1 | tail -100

echo ""
echo "=== CHECKING FOR ERRORS ==="
docker logs dataguardian-container 2>&1 | grep -i "error\|keyerror\|traceback\|exception" | tail -20

echo ""
echo "=== CHECKING secure_users.json IN CONTAINER ==="
docker exec dataguardian-container cat /app/secure_users.json 2>&1 | head -20

echo ""
echo "=== CHECKING APP STATUS ==="
curl -s http://localhost:5000 | grep -i "streamlit\|dataguardian" | head -5
