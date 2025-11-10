"""
Performance Benchmark Test: PostgreSQL vs MySQL
Compares scanning performance between databases with identical datasets.
"""

import os
import sys
import time
from datetime import datetime
from typing import Dict, Any

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.db_scanner import DBScanner
from services.intelligent_db_scanner import IntelligentDBScanner

class PerformanceBenchmark:
    """Compare PostgreSQL vs MySQL scanning performance."""
    
    def __init__(self):
        self.results = {
            'postgresql': {},
            'mysql': {}
        }
    
    def get_pg_connection_params(self) -> Dict[str, Any]:
        """Get PostgreSQL connection parameters from DATABASE_URL."""
        import re
        db_url = os.getenv('DATABASE_URL', '')
        
        match = re.match(r'postgres(?:ql)?://([^:]+):([^@]+)@([^:/]+)(?::(\d+))?/([^?]+)', db_url)
        if match:
            user, password, host, port, database = match.groups()
            return {
                'type': 'postgres',
                'host': host,
                'port': int(port) if port else 5432,
                'database': database,
                'user': user,
                'password': password
            }
        return None
    
    def get_mysql_connection_params(self) -> Dict[str, Any]:
        """Get MySQL connection parameters."""
        return {
            'type': 'mysql',
            'host': os.getenv('MYSQL_HOST', 'nozomi.proxy.rlwy.net'),
            'port': int(os.getenv('MYSQL_PORT', 46657)),
            'database': os.getenv('MYSQL_DATABASE', 'railway'),
            'user': os.getenv('MYSQL_USER', 'root'),
            'password': os.getenv('MYSQL_PASSWORD')
        }
    
    def benchmark_database(self, db_name: str, connection_params: Dict[str, Any]) -> Dict[str, Any]:
        """Run comprehensive benchmark on a database."""
        print(f"\n{'='*80}")
        print(f"BENCHMARKING {db_name.upper()}")
        print(f"{'='*80}")
        
        scanner = DBScanner(region="Netherlands")
        intelligent_scanner = IntelligentDBScanner(scanner)
        
        db_results = {}
        
        # Test all three scan modes
        for mode in ['fast', 'smart', 'deep']:
            print(f"\n--- Testing {mode.upper()} Mode ---")
            
            start_time = time.time()
            
            try:
                results = intelligent_scanner.scan_database_intelligent(
                    connection_params=connection_params,
                    scan_mode=mode,
                    max_tables=None
                )
                
                end_time = time.time()
                duration = end_time - start_time
                
                # Extract metrics
                total_findings = results.get('total_findings', 0)
                tables_scanned = results.get('tables_scanned', 0)
                rows_analyzed = results.get('total_rows_scanned', 0)
                
                # Calculate throughput
                rows_per_second = rows_analyzed / duration if duration > 0 else 0
                findings_per_second = total_findings / duration if duration > 0 else 0
                
                db_results[mode] = {
                    'duration': duration,
                    'findings': total_findings,
                    'tables': tables_scanned,
                    'rows': rows_analyzed,
                    'rows_per_second': rows_per_second,
                    'findings_per_second': findings_per_second,
                    'status': 'completed'
                }
                
                print(f"✅ {mode.upper()} completed in {duration:.2f}s")
                print(f"   Findings: {total_findings} | Tables: {tables_scanned} | Rows: {rows_analyzed}")
                print(f"   Throughput: {rows_per_second:.0f} rows/s, {findings_per_second:.1f} findings/s")
                
            except Exception as e:
                print(f"❌ {mode.upper()} failed: {str(e)}")
                db_results[mode] = {
                    'duration': 0,
                    'findings': 0,
                    'tables': 0,
                    'rows': 0,
                    'status': 'failed',
                    'error': str(e)
                }
        
        return db_results
    
    def compare_results(self):
        """Compare and display benchmark results."""
        print("\n" + "="*80)
        print("PERFORMANCE COMPARISON: POSTGRESQL VS MYSQL")
        print("="*80)
        
        pg = self.results.get('postgresql', {})
        my = self.results.get('mysql', {})
        
        if not pg or not my:
            print("\n⚠️ Incomplete benchmark data")
            return
        
        # Comparison table
        print(f"\n{'Metric':<30} {'PostgreSQL':<20} {'MySQL':<20} {'Winner':<15}")
        print("-" * 85)
        
        for mode in ['fast', 'smart', 'deep']:
            print(f"\n{mode.upper()} MODE:")
            
            pg_mode = pg.get(mode, {})
            my_mode = my.get(mode, {})
            
            # Duration comparison
            pg_dur = pg_mode.get('duration', 0)
            my_dur = my_mode.get('duration', 0)
            dur_winner = "PostgreSQL" if pg_dur < my_dur and pg_dur > 0 else "MySQL" if my_dur > 0 else "Tie"
            print(f"  {'Duration (seconds)':<28} {pg_dur:>18.2f} {my_dur:>18.2f}  {dur_winner:<15}")
            
            # Findings comparison
            pg_find = pg_mode.get('findings', 0)
            my_find = my_mode.get('findings', 0)
            find_winner = "PostgreSQL" if pg_find > my_find else "MySQL" if my_find > pg_find else "Tie"
            print(f"  {'Total Findings':<28} {pg_find:>18} {my_find:>18}  {find_winner:<15}")
            
            # Tables comparison
            pg_tab = pg_mode.get('tables', 0)
            my_tab = my_mode.get('tables', 0)
            print(f"  {'Tables Scanned':<28} {pg_tab:>18} {my_tab:>18}")
            
            # Rows comparison
            pg_rows = pg_mode.get('rows', 0)
            my_rows = my_mode.get('rows', 0)
            print(f"  {'Rows Analyzed':<28} {pg_rows:>18} {my_rows:>18}")
            
            # Throughput comparison
            pg_throughput = pg_mode.get('rows_per_second', 0)
            my_throughput = my_mode.get('rows_per_second', 0)
            throughput_winner = "PostgreSQL" if pg_throughput > my_throughput else "MySQL" if my_throughput > pg_throughput else "Tie"
            print(f"  {'Throughput (rows/s)':<28} {pg_throughput:>18.0f} {my_throughput:>18.0f}  {throughput_winner:<15}")
        
        # Overall statistics
        print("\n" + "="*80)
        print("OVERALL STATISTICS")
        print("="*80)
        
        # Total scan time
        pg_total_time = sum(pg.get(mode, {}).get('duration', 0) for mode in ['fast', 'smart', 'deep'])
        my_total_time = sum(my.get(mode, {}).get('duration', 0) for mode in ['fast', 'smart', 'deep'])
        
        print(f"\nTotal Scan Time:")
        print(f"  PostgreSQL: {pg_total_time:.2f}s")
        print(f"  MySQL:      {my_total_time:.2f}s")
        print(f"  Difference: {abs(pg_total_time - my_total_time):.2f}s ({((abs(pg_total_time - my_total_time) / max(pg_total_time, my_total_time)) * 100):.1f}%)")
        
        # Total findings
        pg_total_findings = sum(pg.get(mode, {}).get('findings', 0) for mode in ['fast', 'smart', 'deep'])
        my_total_findings = sum(my.get(mode, {}).get('findings', 0) for mode in ['fast', 'smart', 'deep'])
        
        print(f"\nTotal PII Findings:")
        print(f"  PostgreSQL: {pg_total_findings}")
        print(f"  MySQL:      {my_total_findings}")
        
        # Average throughput
        pg_avg_throughput = sum(pg.get(mode, {}).get('rows_per_second', 0) for mode in ['fast', 'smart', 'deep']) / 3
        my_avg_throughput = sum(my.get(mode, {}).get('rows_per_second', 0) for mode in ['fast', 'smart', 'deep']) / 3
        
        print(f"\nAverage Throughput:")
        print(f"  PostgreSQL: {pg_avg_throughput:.0f} rows/s")
        print(f"  MySQL:      {my_avg_throughput:.0f} rows/s")
        
        # Winner determination
        print("\n" + "="*80)
        print("BENCHMARK WINNER")
        print("="*80)
        
        if pg_total_time < my_total_time and pg_total_time > 0:
            print(f"\n🏆 PostgreSQL is FASTER by {((my_total_time - pg_total_time) / my_total_time * 100):.1f}%")
        elif my_total_time < pg_total_time and my_total_time > 0:
            print(f"\n🏆 MySQL is FASTER by {((pg_total_time - my_total_time) / pg_total_time * 100):.1f}%")
        else:
            print("\n🤝 Performance is COMPARABLE")
        
        if pg_total_findings > my_total_findings:
            print(f"📊 PostgreSQL found MORE PII ({pg_total_findings} vs {my_total_findings})")
        elif my_total_findings > pg_total_findings:
            print(f"📊 MySQL found MORE PII ({my_total_findings} vs {pg_total_findings})")
        else:
            print(f"📊 Both databases found EQUAL PII ({pg_total_findings} instances)")

def main():
    """Run performance benchmark."""
    print("\n" + "="*80)
    print("DATAGUARDIAN PRO - PERFORMANCE BENCHMARK")
    print("PostgreSQL vs MySQL Comparison")
    print("="*80)
    
    benchmark = PerformanceBenchmark()
    
    # Get connection parameters
    pg_params = benchmark.get_pg_connection_params()
    mysql_params = benchmark.get_mysql_connection_params()
    
    if not pg_params:
        print("\n❌ PostgreSQL connection not available")
        return 1
    
    if not mysql_params or not mysql_params.get('password'):
        print("\n❌ MySQL connection not available")
        return 1
    
    # Run benchmarks
    print("\n🔍 Starting benchmarks (this may take 1-2 minutes)...\n")
    
    benchmark.results['postgresql'] = benchmark.benchmark_database('PostgreSQL', pg_params)
    benchmark.results['mysql'] = benchmark.benchmark_database('MySQL', mysql_params)
    
    # Compare results
    benchmark.compare_results()
    
    print("\n" + "="*80)
    print("✅ PERFORMANCE BENCHMARK COMPLETED!")
    print("="*80)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
