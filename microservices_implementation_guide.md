# DataGuardian Pro Microservices Implementation Guide

## Step-by-Step Implementation

### Prerequisites Setup

#### 1. Development Environment
```bash
# Install required tools
brew install docker docker-compose kubernetes-cli helm
pip install docker-compose fastapi uvicorn celery redis postgresql

# Create project structure
mkdir dataguardian-microservices
cd dataguardian-microservices
mkdir -p {auth-service,api-gateway,scanner-orchestrator,code-scanner,website-scanner,report-service}
```

#### 2. Container Registry Setup
```bash
# Set up private Docker registry
docker run -d -p 5000:5000 --name registry registry:2
# Or use cloud registry (AWS ECR, Google GCR, Azure ACR)
```

## Phase 1: Foundation Services

### Step 1: Authentication Service

#### Create Authentication Service
```python
# auth-service/main.py
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import jwt
import bcrypt
from datetime import datetime, timedelta
import redis

app = FastAPI(title="DataGuardian Auth Service")
security = HTTPBearer()
redis_client = redis.Redis(host='redis', port=6379, decode_responses=True)

class UserCreate(BaseModel):
    email: str
    password: str
    role: str = "user"

class UserLogin(BaseModel):
    email: str
    password: str

class User(BaseModel):
    id: str
    email: str
    role: str
    created_at: datetime

# JWT Configuration
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.post("/register")
async def register(user: UserCreate):
    # Check if user exists
    if redis_client.hexists("users", user.email):
        raise HTTPException(status_code=400, detail="User already exists")
    
    # Hash password
    password_hash = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
    
    # Store user
    user_data = {
        "id": str(uuid.uuid4()),
        "email": user.email,
        "password_hash": password_hash.decode('utf-8'),
        "role": user.role,
        "created_at": datetime.utcnow().isoformat()
    }
    redis_client.hset("users", user.email, json.dumps(user_data))
    
    return {"message": "User created successfully"}

@app.post("/login")
async def login(user: UserLogin):
    # Get user from Redis
    user_data = redis_client.hget("users", user.email)
    if not user_data:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    user_data = json.loads(user_data)
    
    # Verify password
    if not bcrypt.checkpw(user.password.encode('utf-8'), user_data["password_hash"].encode('utf-8')):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Create token
    access_token = create_access_token(data={"sub": user_data["id"]})
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/verify/{token}")
async def verify_user_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return {"valid": True, "user_id": payload.get("sub")}
    except jwt.JWTError:
        return {"valid": False}
```

#### Authentication Service Dockerfile
```dockerfile
# auth-service/Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Step 2: API Gateway Setup

#### Kong Configuration
```yaml
# api-gateway/kong.yml
_format_version: "3.0"
services:
  - name: auth-service
    url: http://auth-service:8000
    routes:
      - name: auth-routes
        paths:
          - /api/v1/auth
        strip_path: true
        
  - name: scanner-orchestrator
    url: http://scanner-orchestrator:8000
    routes:
      - name: scanner-routes
        paths:
          - /api/v1/scan
        strip_path: true
        plugins:
          - name: jwt
            config:
              secret_is_base64: false
              key_claim_name: sub
              
  - name: report-service
    url: http://report-service:8000
    routes:
      - name: report-routes
        paths:
          - /api/v1/reports
        strip_path: true
        plugins:
          - name: jwt
```

### Step 3: Scanner Orchestrator Service

#### Orchestrator with Celery
```python
# scanner-orchestrator/main.py
from fastapi import FastAPI, HTTPException, Depends
from celery import Celery
from pydantic import BaseModel
import requests
import asyncio
from typing import List, Dict, Any

app = FastAPI(title="DataGuardian Scanner Orchestrator")

# Celery configuration
celery_app = Celery(
    'scanner_orchestrator',
    broker='redis://redis:6379/0',
    backend='redis://redis:6379/0',
    include=['tasks']
)

class ScanRequest(BaseModel):
    user_id: str
    scan_types: List[str]
    source_url: str
    configuration: Dict[str, Any]

class ScanStatus(BaseModel):
    scan_id: str
    status: str
    progress: int
    results: Dict[str, Any] = None

# Service discovery
SERVICES = {
    'code': 'http://code-scanner:8000',
    'website': 'http://website-scanner:8000',
    'document': 'http://document-scanner:8000',
    'ai_model': 'http://ai-model-scanner:8000'
}

@app.post("/scan")
async def initiate_scan(scan_request: ScanRequest):
    # Create scan ID
    scan_id = str(uuid.uuid4())
    
    # Queue scan tasks
    scan_task = orchestrate_scan.delay(
        scan_id=scan_id,
        user_id=scan_request.user_id,
        scan_types=scan_request.scan_types,
        source_url=scan_request.source_url,
        configuration=scan_request.configuration
    )
    
    return {"scan_id": scan_id, "task_id": scan_task.id, "status": "queued"}

@app.get("/scan/{scan_id}/status")
async def get_scan_status(scan_id: str):
    # Get scan status from Redis
    status = redis_client.get(f"scan:{scan_id}:status")
    if not status:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    return json.loads(status)

@celery_app.task(bind=True)
def orchestrate_scan(self, scan_id: str, user_id: str, scan_types: List[str], 
                    source_url: str, configuration: Dict[str, Any]):
    try:
        # Update scan status
        update_scan_status(scan_id, "in_progress", 0)
        
        # Execute scans in parallel
        scan_results = {}
        total_scans = len(scan_types)
        
        for i, scan_type in enumerate(scan_types):
            if scan_type in SERVICES:
                # Call specific scanner service
                response = requests.post(
                    f"{SERVICES[scan_type]}/scan",
                    json={
                        "source_url": source_url,
                        "configuration": configuration.get(scan_type, {})
                    }
                )
                
                if response.status_code == 200:
                    scan_results[scan_type] = response.json()
                else:
                    scan_results[scan_type] = {"error": "Scan failed"}
            
            # Update progress
            progress = int((i + 1) / total_scans * 100)
            update_scan_status(scan_id, "in_progress", progress)
        
        # Aggregate results
        final_results = aggregate_scan_results(scan_results)
        
        # Update final status
        update_scan_status(scan_id, "completed", 100, final_results)
        
        return final_results
        
    except Exception as e:
        update_scan_status(scan_id, "failed", 0, {"error": str(e)})
        raise

def update_scan_status(scan_id: str, status: str, progress: int, results: Dict = None):
    scan_status = {
        "scan_id": scan_id,
        "status": status,
        "progress": progress,
        "timestamp": datetime.utcnow().isoformat()
    }
    if results:
        scan_status["results"] = results
    
    redis_client.setex(f"scan:{scan_id}:status", 3600, json.dumps(scan_status))

def aggregate_scan_results(results: Dict[str, Any]) -> Dict[str, Any]:
    aggregated = {
        "total_findings": 0,
        "high_risk_count": 0,
        "medium_risk_count": 0,
        "low_risk_count": 0,
        "compliance_score": 0,
        "detailed_results": results
    }
    
    for scan_type, result in results.items():
        if "findings" in result:
            aggregated["total_findings"] += len(result["findings"])
            # Aggregate risk counts and compliance scores
            aggregated["high_risk_count"] += result.get("high_risk_count", 0)
            aggregated["medium_risk_count"] += result.get("medium_risk_count", 0)
            aggregated["low_risk_count"] += result.get("low_risk_count", 0)
    
    # Calculate overall compliance score
    total_risks = aggregated["high_risk_count"] + aggregated["medium_risk_count"] + aggregated["low_risk_count"]
    if total_risks > 0:
        aggregated["compliance_score"] = max(0, 100 - (
            aggregated["high_risk_count"] * 15 + 
            aggregated["medium_risk_count"] * 7 + 
            aggregated["low_risk_count"] * 3
        ))
    else:
        aggregated["compliance_score"] = 100
    
    return aggregated
```

### Step 4: Individual Scanner Services

#### Code Scanner Service
```python
# code-scanner/main.py
from fastapi import FastAPI
from pydantic import BaseModel
import git
import os
import tempfile
import shutil
from typing import List, Dict, Any

app = FastAPI(title="DataGuardian Code Scanner")

class CodeScanRequest(BaseModel):
    source_url: str
    configuration: Dict[str, Any]

class CodeScanResult(BaseModel):
    scan_id: str
    findings: List[Dict[str, Any]]
    metrics: Dict[str, Any]

@app.post("/scan")
async def scan_code(request: CodeScanRequest):
    scan_id = str(uuid.uuid4())
    
    # Clone repository
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            repo = git.Repo.clone_from(request.source_url, temp_dir)
            
            # Scan for PII and security issues
            findings = []
            total_files = 0
            total_lines = 0
            
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    if file.endswith(('.py', '.js', '.java', '.ts', '.go')):
                        file_path = os.path.join(root, file)
                        file_findings = scan_file_for_pii(file_path)
                        findings.extend(file_findings)
                        total_files += 1
                        
                        # Count lines
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            total_lines += sum(1 for line in f)
            
            # Calculate metrics
            metrics = {
                "files_scanned": total_files,
                "lines_analyzed": total_lines,
                "high_risk_count": len([f for f in findings if f.get("severity") == "High"]),
                "medium_risk_count": len([f for f in findings if f.get("severity") == "Medium"]),
                "low_risk_count": len([f for f in findings if f.get("severity") == "Low"])
            }
            
            return {
                "scan_id": scan_id,
                "findings": findings,
                "metrics": metrics,
                "status": "completed"
            }
            
        except Exception as e:
            return {
                "scan_id": scan_id,
                "error": str(e),
                "status": "failed"
            }

def scan_file_for_pii(file_path: str) -> List[Dict[str, Any]]:
    findings = []
    
    # PII patterns
    pii_patterns = {
        'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'phone': r'\b\d{3}-\d{3}-\d{4}\b',
        'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
        'credit_card': r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'
    }
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line_num, line in enumerate(f, 1):
                for pattern_name, pattern in pii_patterns.items():
                    matches = re.findall(pattern, line)
                    if matches:
                        findings.append({
                            "type": f"PII_{pattern_name.upper()}",
                            "severity": "High" if pattern_name in ['ssn', 'credit_card'] else "Medium",
                            "file": os.path.basename(file_path),
                            "line": line_num,
                            "description": f"Found {pattern_name} pattern in code",
                            "content": line.strip()[:100],  # First 100 chars
                            "recommendation": f"Remove or encrypt {pattern_name} data"
                        })
    except Exception as e:
        # Log error but don't fail the scan
        pass
    
    return findings
```

## Phase 2: Docker Compose Configuration

### Complete Docker Compose Setup
```yaml
# docker-compose.yml
version: '3.8'

services:
  # Infrastructure
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: dataguardian
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  rabbitmq:
    image: rabbitmq:3-management
    environment:
      RABBITMQ_DEFAULT_USER: admin
      RABBITMQ_DEFAULT_PASS: password
    ports:
      - "5672:5672"
      - "15672:15672"

  # Core Services
  auth-service:
    build: ./auth-service
    ports:
      - "8001:8000"
    depends_on:
      - redis
      - postgres
    environment:
      - REDIS_URL=redis://redis:6379
      - DATABASE_URL=postgresql://admin:password@postgres:5432/dataguardian

  api-gateway:
    image: kong:3.0
    ports:
      - "8000:8000"
      - "8001:8001"
    environment:
      - KONG_DATABASE=off
      - KONG_DECLARATIVE_CONFIG=/kong/declarative/kong.yml
      - KONG_PROXY_ACCESS_LOG=/dev/stdout
      - KONG_ADMIN_ACCESS_LOG=/dev/stdout
      - KONG_PROXY_ERROR_LOG=/dev/stderr
      - KONG_ADMIN_ERROR_LOG=/dev/stderr
    volumes:
      - ./api-gateway/kong.yml:/kong/declarative/kong.yml
    depends_on:
      - auth-service
      - scanner-orchestrator

  scanner-orchestrator:
    build: ./scanner-orchestrator
    ports:
      - "8002:8000"
    depends_on:
      - redis
      - rabbitmq
    environment:
      - REDIS_URL=redis://redis:6379
      - BROKER_URL=pyamqp://admin:password@rabbitmq:5672//

  # Scanner Services
  code-scanner:
    build: ./code-scanner
    ports:
      - "8003:8000"
    volumes:
      - /tmp:/tmp
    environment:
      - REDIS_URL=redis://redis:6379

  website-scanner:
    build: ./website-scanner
    ports:
      - "8004:8000"
    environment:
      - REDIS_URL=redis://redis:6379

  document-scanner:
    build: ./document-scanner
    ports:
      - "8005:8000"
    environment:
      - REDIS_URL=redis://redis:6379

  ai-model-scanner:
    build: ./ai-model-scanner
    ports:
      - "8006:8000"
    environment:
      - REDIS_URL=redis://redis:6379

  # Support Services
  report-service:
    build: ./report-service
    ports:
      - "8007:8000"
    depends_on:
      - postgres
    environment:
      - DATABASE_URL=postgresql://admin:password@postgres:5432/dataguardian

  notification-service:
    build: ./notification-service
    ports:
      - "8008:8000"
    environment:
      - REDIS_URL=redis://redis:6379

  # Monitoring
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    depends_on:
      - prometheus

volumes:
  redis_data:
  postgres_data:
```

## Phase 3: Kubernetes Deployment

### Kubernetes Manifests
```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: dataguardian
---
# k8s/auth-service.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: auth-service
  namespace: dataguardian
spec:
  replicas: 3
  selector:
    matchLabels:
      app: auth-service
  template:
    metadata:
      labels:
        app: auth-service
    spec:
      containers:
      - name: auth-service
        image: dataguardian/auth-service:latest
        ports:
        - containerPort: 8000
        env:
        - name: REDIS_URL
          value: "redis://redis:6379"
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
---
apiVersion: v1
kind: Service
metadata:
  name: auth-service
  namespace: dataguardian
spec:
  selector:
    app: auth-service
  ports:
  - port: 8000
    targetPort: 8000
  type: ClusterIP
```

### Helm Chart Configuration
```yaml
# helm/dataguardian/values.yaml
global:
  registry: "your-registry.com"
  imageTag: "latest"
  
auth:
  replicaCount: 3
  image:
    repository: dataguardian/auth-service
    tag: latest
  service:
    type: ClusterIP
    port: 8000
  resources:
    requests:
      memory: "256Mi"
      cpu: "250m"
    limits:
      memory: "512Mi"
      cpu: "500m"

orchestrator:
  replicaCount: 2
  image:
    repository: dataguardian/scanner-orchestrator
    tag: latest
  service:
    type: ClusterIP
    port: 8000
  resources:
    requests:
      memory: "512Mi"
      cpu: "500m"
    limits:
      memory: "1Gi"
      cpu: "1000m"

scanners:
  code:
    replicaCount: 2
    resources:
      requests:
        memory: "512Mi"
        cpu: "500m"
      limits:
        memory: "1Gi"
        cpu: "1000m"
  
  website:
    replicaCount: 2
    resources:
      requests:
        memory: "256Mi"
        cpu: "250m"
      limits:
        memory: "512Mi"
        cpu: "500m"
```

## Migration Strategy

### Step-by-Step Migration
1. **Set up infrastructure** (Redis, PostgreSQL, RabbitMQ)
2. **Deploy authentication service** and migrate user management
3. **Set up API Gateway** and route authentication requests
4. **Deploy scanner orchestrator** with basic task queuing
5. **Migrate code scanner** as first specialized service
6. **Gradually migrate other scanners** one by one
7. **Deploy support services** (reports, notifications)
8. **Implement monitoring and observability**
9. **Performance testing and optimization**
10. **Production deployment with blue-green strategy**

This comprehensive guide provides the technical foundation for transforming DataGuardian Pro into a scalable microservices architecture.