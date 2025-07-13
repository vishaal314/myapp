# DataGuardian Pro - 1-Month Architecture Fix (Ultra Budget Solution)

## Problem Statement
Current architecture limitations requiring immediate resolution:
1. **Single process** - cannot scale individual components
2. **Resource sharing** - heavy scanners impact lightweight operations  
3. **Deployment coupling** - all changes require full system restart
4. **Single point of failure** - one service down = entire system down

## Ultra Budget Solution: Process Isolation Architecture

### Budget: $500-1000 (1 month)
### Development Time: 80-120 hours (2-3 weeks)
### Risk Level: Low (incremental improvements)

## Solution 1: Multi-Process Architecture (Week 1-2)

### Implementation Strategy
Transform single-process monolith into multi-process architecture using Python's multiprocessing and queue systems.

### Architecture Changes

#### A. Process Separation
```python
# NEW: Process Manager (services/process_manager.py)
Main Web Process (Port 5000)
├── Authentication & UI
├── Dashboard & Navigation
├── Request routing
└── Response aggregation

Scanner Process Pool (Ports 5001-5010)
├── Process 1: Code Scanner (Port 5001)
├── Process 2: Website Scanner (Port 5002)
├── Process 3: AI Model Scanner (Port 5003)
├── Process 4: Document Scanner (Port 5004)
├── Process 5: Database Scanner (Port 5005)
├── Process 6: Image Scanner (Port 5006)
├── Process 7: DPIA Scanner (Port 5007)
├── Process 8: SOC2 Scanner (Port 5008)
├── Process 9: API Scanner (Port 5009)
└── Process 10: Report Generator (Port 5010)

Support Processes
├── Redis Queue Manager (Background)
├── Database Connection Pool (Background)
└── Health Monitor (Background)
```

#### B. Inter-Process Communication
```python
# Communication Layer (utils/ipc_manager.py)
┌─────────────────┐    ┌─────────────────┐
│   Main Web      │    │   Scanner       │
│   Process       │◄──►│   Processes     │
│   (Port 5000)   │    │   (5001-5010)   │
└─────────────────┘    └─────────────────┘
         │                       │
         └──────── Redis ────────┘
              Message Queue
```

### Implementation Details

#### Week 1: Core Infrastructure
```python
# 1. Process Manager (NEW FILE: services/process_manager.py)
import multiprocessing
import subprocess
import redis
import json
from typing import Dict, List

class ProcessManager:
    def __init__(self):
        self.processes = {}
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
        self.scanner_ports = {
            'code': 5001,
            'website': 5002,
            'ai_model': 5003,
            'document': 5004,
            'database': 5005,
            'image': 5006,
            'dpia': 5007,
            'soc2': 5008,
            'api': 5009,
            'report': 5010
        }
    
    def start_scanner_process(self, scanner_type: str):
        """Start individual scanner process"""
        port = self.scanner_ports[scanner_type]
        cmd = [
            'python', f'services/scanner_processes/{scanner_type}_process.py',
            '--port', str(port)
        ]
        
        process = subprocess.Popen(cmd)
        self.processes[scanner_type] = {
            'process': process,
            'port': port,
            'status': 'running'
        }
        return process
    
    def submit_scan_job(self, scanner_type: str, scan_data: dict):
        """Submit scan job to specific scanner process"""
        job_id = f"{scanner_type}_{uuid.uuid4().hex[:8]}"
        
        # Send job to Redis queue
        self.redis_client.lpush(
            f"scan_queue_{scanner_type}",
            json.dumps({
                'job_id': job_id,
                'data': scan_data,
                'timestamp': time.time()
            })
        )
        
        return job_id
    
    def get_scan_result(self, job_id: str):
        """Get scan result from Redis"""
        result = self.redis_client.get(f"scan_result_{job_id}")
        if result:
            return json.loads(result)
        return None
    
    def health_check(self):
        """Check health of all scanner processes"""
        health_status = {}
        for scanner_type, process_info in self.processes.items():
            try:
                # Check if process is running
                if process_info['process'].poll() is None:
                    # Check if process responds
                    response = requests.get(
                        f"http://localhost:{process_info['port']}/health",
                        timeout=2
                    )
                    health_status[scanner_type] = response.status_code == 200
                else:
                    health_status[scanner_type] = False
            except:
                health_status[scanner_type] = False
        
        return health_status
```

#### Week 2: Scanner Process Implementation
```python
# 2. Individual Scanner Processes (NEW DIR: services/scanner_processes/)

# Example: Code Scanner Process (services/scanner_processes/code_process.py)
from flask import Flask, request, jsonify
import redis
import json
import threading
import time
from services.code_scanner import CodeScanner

app = Flask(__name__)
redis_client = redis.Redis(host='localhost', port=6379, db=0)
scanner = CodeScanner()

class CodeScannerProcess:
    def __init__(self):
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
        self.scanner = CodeScanner()
        self.running = True
        
    def process_queue(self):
        """Process scan jobs from Redis queue"""
        while self.running:
            try:
                # Get job from queue
                job_data = self.redis_client.brpop("scan_queue_code", timeout=1)
                if job_data:
                    job = json.loads(job_data[1])
                    
                    # Process scan
                    result = self.scanner.scan(job['data'])
                    
                    # Store result
                    self.redis_client.setex(
                        f"scan_result_{job['job_id']}",
                        3600,  # 1 hour expiry
                        json.dumps(result)
                    )
                    
            except Exception as e:
                print(f"Error processing job: {e}")
                time.sleep(1)
    
    def start(self):
        """Start background queue processor"""
        thread = threading.Thread(target=self.process_queue)
        thread.daemon = True
        thread.start()

# Flask endpoints for health checks
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'scanner': 'code'})

@app.route('/stats', methods=['GET'])
def get_stats():
    queue_size = redis_client.llen("scan_queue_code")
    return jsonify({
        'queue_size': queue_size,
        'scanner_type': 'code',
        'status': 'running'
    })

if __name__ == '__main__':
    # Start queue processor
    processor = CodeScannerProcess()
    processor.start()
    
    # Start Flask app
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 5001
    app.run(host='0.0.0.0', port=port, debug=False)
```

## Solution 2: Load Balancer + Process Pool (Week 2-3)

### Implementation Strategy
Add Nginx load balancer to distribute requests across multiple application instances.

### Architecture Changes

#### A. Multi-Instance Deployment
```nginx
# NEW: nginx.conf
upstream dataguardian_backend {
    server 127.0.0.1:5000 weight=3;  # Main UI instance
    server 127.0.0.1:5001 weight=2;  # Scanner instance 1
    server 127.0.0.1:5002 weight=2;  # Scanner instance 2
    server 127.0.0.1:5003 weight=2;  # Scanner instance 3
}

server {
    listen 80;
    server_name localhost;
    
    location / {
        proxy_pass http://dataguardian_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        
        # Health check
        proxy_next_upstream error timeout http_500 http_502 http_503;
        proxy_connect_timeout 5s;
        proxy_send_timeout 10s;
        proxy_read_timeout 10s;
    }
    
    location /health {
        access_log off;
        return 200 "healthy\n";
    }
}
```

#### B. Process Launcher
```python
# NEW: launcher.py
import subprocess
import time
import signal
import sys
from typing import List

class ProcessLauncher:
    def __init__(self):
        self.processes: List[subprocess.Popen] = []
        
    def start_instances(self):
        """Start multiple application instances"""
        
        # Start main UI instance
        main_process = subprocess.Popen([
            'streamlit', 'run', 'app.py',
            '--server.port', '5000',
            '--server.address', '0.0.0.0',
            '--server.headless', 'true'
        ])
        self.processes.append(main_process)
        
        # Start scanner instances
        for i in range(1, 4):  # 3 scanner instances
            scanner_process = subprocess.Popen([
                'python', 'scanner_instance.py',
                '--port', str(5000 + i),
                '--instance-id', str(i)
            ])
            self.processes.append(scanner_process)
        
        # Start Nginx
        nginx_process = subprocess.Popen(['nginx', '-c', 'nginx.conf'])
        self.processes.append(nginx_process)
        
        print(f"Started {len(self.processes)} processes")
    
    def monitor_processes(self):
        """Monitor and restart failed processes"""
        while True:
            for i, process in enumerate(self.processes):
                if process.poll() is not None:
                    print(f"Process {i} died, restarting...")
                    # Restart logic here
            time.sleep(5)
    
    def shutdown(self):
        """Gracefully shutdown all processes"""
        for process in self.processes:
            process.terminate()
        
        # Wait for graceful shutdown
        time.sleep(2)
        
        # Force kill if needed
        for process in self.processes:
            if process.poll() is None:
                process.kill()

# Signal handlers
launcher = ProcessLauncher()

def signal_handler(signum, frame):
    launcher.shutdown()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

if __name__ == '__main__':
    launcher.start_instances()
    launcher.monitor_processes()
```

## Solution 3: Circuit Breaker Pattern (Week 3-4)

### Implementation Strategy
Implement circuit breaker pattern to prevent cascade failures and provide fallback mechanisms.

### Architecture Changes

#### A. Circuit Breaker Implementation
```python
# NEW: utils/circuit_breaker.py
import time
import threading
from enum import Enum
from typing import Callable, Any

class CircuitState(Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
        self._lock = threading.Lock()
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection"""
        with self._lock:
            if self.state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    self.state = CircuitState.HALF_OPEN
                else:
                    raise Exception("Circuit breaker is OPEN")
            
            try:
                result = func(*args, **kwargs)
                self._on_success()
                return result
            except Exception as e:
                self._on_failure()
                raise e
    
    def _should_attempt_reset(self) -> bool:
        """Check if we should attempt to reset the circuit"""
        return (
            self.last_failure_time and
            time.time() - self.last_failure_time >= self.timeout
        )
    
    def _on_success(self):
        """Handle successful execution"""
        self.failure_count = 0
        self.state = CircuitState.CLOSED
    
    def _on_failure(self):
        """Handle failed execution"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN

# Usage in scanner services
class ResilientScannerService:
    def __init__(self):
        self.code_breaker = CircuitBreaker(failure_threshold=3, timeout=30)
        self.website_breaker = CircuitBreaker(failure_threshold=5, timeout=60)
        self.ai_breaker = CircuitBreaker(failure_threshold=2, timeout=120)
    
    def scan_code(self, data):
        """Code scanning with circuit breaker"""
        try:
            return self.code_breaker.call(self._actual_code_scan, data)
        except Exception:
            # Fallback to basic scan
            return self._fallback_code_scan(data)
    
    def scan_website(self, data):
        """Website scanning with circuit breaker"""
        try:
            return self.website_breaker.call(self._actual_website_scan, data)
        except Exception:
            # Fallback to cached results or basic scan
            return self._fallback_website_scan(data)
    
    def _fallback_code_scan(self, data):
        """Fallback code scanning logic"""
        return {
            'status': 'degraded',
            'message': 'Using fallback scanner due to system issues',
            'findings': [],
            'fallback_mode': True
        }
```

## Solution 4: Database Connection Pooling (Week 4)

### Implementation Strategy
Implement proper database connection pooling to prevent database bottlenecks.

### Architecture Changes

#### A. Enhanced Database Manager
```python
# ENHANCED: utils/database_manager.py
import psycopg2
from psycopg2 import pool
import threading
import time
from contextlib import contextmanager

class EnhancedDatabaseManager:
    def __init__(self):
        self.connection_pool = None
        self.pool_lock = threading.Lock()
        self.stats = {
            'active_connections': 0,
            'total_queries': 0,
            'failed_queries': 0,
            'pool_exhausted': 0
        }
    
    def initialize_pool(self):
        """Initialize connection pool with optimal settings"""
        try:
            self.connection_pool = psycopg2.pool.ThreadedConnectionPool(
                minconn=5,    # Minimum connections
                maxconn=20,   # Maximum connections
                host=os.getenv('PGHOST', 'localhost'),
                database=os.getenv('PGDATABASE', 'dataguardian'),
                user=os.getenv('PGUSER', 'postgres'),
                password=os.getenv('PGPASSWORD', ''),
                port=os.getenv('PGPORT', '5432')
            )
            print("Database connection pool initialized")
        except Exception as e:
            print(f"Failed to initialize connection pool: {e}")
            raise
    
    @contextmanager
    def get_connection(self):
        """Get database connection from pool"""
        conn = None
        try:
            with self.pool_lock:
                if not self.connection_pool:
                    self.initialize_pool()
                
                conn = self.connection_pool.getconn()
                self.stats['active_connections'] += 1
            
            yield conn
            
        except psycopg2.pool.PoolError:
            self.stats['pool_exhausted'] += 1
            raise Exception("Database connection pool exhausted")
        except Exception as e:
            self.stats['failed_queries'] += 1
            raise e
        finally:
            if conn:
                with self.pool_lock:
                    self.connection_pool.putconn(conn)
                    self.stats['active_connections'] -= 1
    
    def execute_query(self, query: str, params: tuple = None):
        """Execute query with connection pooling"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(query, params)
                self.stats['total_queries'] += 1
                
                if query.strip().upper().startswith('SELECT'):
                    return cursor.fetchall()
                else:
                    conn.commit()
                    return cursor.rowcount
            except Exception as e:
                conn.rollback()
                raise e
            finally:
                cursor.close()
    
    def get_pool_stats(self):
        """Get connection pool statistics"""
        with self.pool_lock:
            if self.connection_pool:
                return {
                    'active_connections': self.stats['active_connections'],
                    'total_queries': self.stats['total_queries'],
                    'failed_queries': self.stats['failed_queries'],
                    'pool_exhausted': self.stats['pool_exhausted'],
                    'pool_size': len(self.connection_pool._used) + len(self.connection_pool._pool)
                }
            return {'status': 'pool_not_initialized'}
```

## Implementation Timeline

### Week 1: Foundation Setup
- **Day 1-2**: Set up Redis and process management infrastructure
- **Day 3-4**: Implement ProcessManager and basic IPC
- **Day 5-7**: Create first scanner processes (Code, Website, AI)

### Week 2: Core Processes
- **Day 8-10**: Implement remaining scanner processes
- **Day 11-12**: Add health monitoring and auto-restart
- **Day 13-14**: Load testing and optimization

### Week 3: Load Balancing
- **Day 15-17**: Set up Nginx load balancer
- **Day 18-19**: Implement circuit breaker pattern
- **Day 20-21**: Add fallback mechanisms

### Week 4: Database & Polish
- **Day 22-24**: Enhanced database connection pooling
- **Day 25-26**: Performance tuning and monitoring
- **Day 27-28**: Documentation and deployment

## Expected Results

### Performance Improvements
- **Throughput**: 960 → 2,400 scans/hour (150% increase)
- **Response Time**: Reduced by 60% for UI operations
- **Resource Usage**: 40% better CPU utilization
- **Failure Recovery**: 99.9% uptime with auto-restart

### Scalability Improvements
- **Individual Components**: Each scanner can scale independently
- **Resource Isolation**: Heavy scans don't impact UI responsiveness
- **Deployment Flexibility**: Update scanners without full restart
- **Fault Tolerance**: Single scanner failure doesn't crash system

## Budget Breakdown

### Infrastructure Costs
- **Redis Server**: $10/month (or use free tier)
- **Additional RAM**: $20/month (for multiple processes)
- **Nginx**: Free (open source)
- **Monitoring**: $15/month (basic monitoring tools)
- **Total Monthly**: $45/month

### Development Costs
- **Developer Time**: 120 hours × $50/hour = $6,000
- **Testing**: 20 hours × $50/hour = $1,000
- **Total One-time**: $7,000

### Total Investment: $7,000 + $45/month

## Risk Mitigation

### Technical Risks
- **Gradual rollout**: Implement one scanner at a time
- **Rollback capability**: Keep original monolith as fallback
- **Monitoring**: Comprehensive logging and alerting
- **Testing**: Load testing before production deployment

### Operational Risks
- **Documentation**: Complete deployment and maintenance guides
- **Training**: Team training on new architecture
- **Support**: 24/7 monitoring during transition
- **Backup**: Database backups and disaster recovery

## Success Metrics

### Week 1 Targets
- **Process Separation**: 3 scanner processes running independently
- **IPC Working**: Redis message queue operational
- **Health Monitoring**: Basic health checks implemented

### Week 2 Targets
- **All Scanners**: 10 scanner processes operational
- **Load Balancing**: Nginx distributing requests
- **Auto-restart**: Failed processes automatically restarted

### Week 3 Targets
- **Circuit Breakers**: Fault tolerance implemented
- **Performance**: 2x throughput improvement measured
- **Monitoring**: Full observability dashboard

### Week 4 Targets
- **Production Ready**: System deployed and stable
- **Documentation**: Complete operational guides
- **Training**: Team ready for production support

This ultra-budget approach solves all four critical limitations within 1 month while maintaining your current Grade A functionality and preparing for future microservices migration.