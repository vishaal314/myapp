"""
Async Network Optimizer for DataGuardian Pro

This module provides async network operations to eliminate bottlenecks
caused by sequential API calls and network operations.
"""

import asyncio
import aiohttp
import time
from typing import List, Dict, Any, Callable, Optional
from concurrent.futures import ThreadPoolExecutor
import threading

class AsyncNetworkOptimizer:
    """Optimizes network operations using async/await and batch processing."""
    
    def __init__(self, max_concurrent_requests: int = 10, timeout: int = 30):
        self.max_concurrent_requests = max_concurrent_requests
        self.timeout = timeout
        self.session = None
        self._lock = threading.Lock()
    
    async def _get_session(self):
        """Get or create aiohttp session with optimized settings."""
        if self.session is None or self.session.closed:
            connector = aiohttp.TCPConnector(
                limit=self.max_concurrent_requests,
                limit_per_host=5,
                keepalive_timeout=60,
                enable_cleanup_closed=True
            )
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers={'User-Agent': 'DataGuardian Pro Scanner'}
            )
        return self.session
    
    async def batch_http_requests(self, requests: List[Dict[str, Any]], 
                                 progress_callback: Optional[Callable] = None) -> List[Dict[str, Any]]:
        """
        Execute multiple HTTP requests concurrently.
        
        Args:
            requests: List of request dictionaries with 'url', 'method', 'headers', 'data'
            progress_callback: Optional callback for progress updates
        
        Returns:
            List of response dictionaries
        """
        semaphore = asyncio.Semaphore(self.max_concurrent_requests)
        session = await self._get_session()
        
        async def make_request(request_data: Dict[str, Any], index: int) -> Dict[str, Any]:
            async with semaphore:
                try:
                    url = request_data.get('url')
                    method = request_data.get('method', 'GET').upper()
                    headers = request_data.get('headers', {})
                    data = request_data.get('data')
                    
                    async with session.request(method, url, headers=headers, data=data) as response:
                        result = {
                            'index': index,
                            'url': url,
                            'status': response.status,
                            'success': response.status < 400,
                            'headers': dict(response.headers),
                            'text': await response.text() if response.status < 400 else None,
                            'error': None
                        }
                        
                        if progress_callback:
                            progress_callback(index + 1, len(requests), f"Completed request to {url}")
                        
                        return result
                        
                except Exception as e:
                    result = {
                        'index': index,
                        'url': request_data.get('url', 'unknown'),
                        'status': 0,
                        'success': False,
                        'headers': {},
                        'text': None,
                        'error': str(e)
                    }
                    
                    if progress_callback:
                        progress_callback(index + 1, len(requests), f"Failed request: {str(e)}")
                    
                    return result
        
        # Execute all requests concurrently
        tasks = [make_request(req, i) for i, req in enumerate(requests)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle any exceptions and sort results by original order
        processed_results = []
        for result in results:
            if isinstance(result, Exception):
                processed_results.append({
                    'index': len(processed_results),
                    'url': 'unknown',
                    'status': 0,
                    'success': False,
                    'headers': {},
                    'text': None,
                    'error': str(result)
                })
            else:
                processed_results.append(result)
        
        # Sort by original index to maintain order
        processed_results.sort(key=lambda x: x['index'])
        return processed_results
    
    async def batch_dns_lookups(self, domains: List[str], 
                               progress_callback: Optional[Callable] = None) -> List[Dict[str, Any]]:
        """
        Perform multiple DNS lookups concurrently.
        
        Args:
            domains: List of domain names to resolve
            progress_callback: Optional callback for progress updates
        
        Returns:
            List of DNS lookup results
        """
        semaphore = asyncio.Semaphore(self.max_concurrent_requests)
        
        async def lookup_domain(domain: str, index: int) -> Dict[str, Any]:
            async with semaphore:
                try:
                    # Use asyncio's DNS resolution
                    start_time = time.time()
                    info = await asyncio.get_event_loop().getaddrinfo(
                        domain, None, family=0, proto=0, flags=0
                    )
                    
                    ips = list(set([addr[4][0] for addr in info]))
                    lookup_time = time.time() - start_time
                    
                    result = {
                        'index': index,
                        'domain': domain,
                        'ips': ips,
                        'success': True,
                        'lookup_time': lookup_time,
                        'error': None
                    }
                    
                    if progress_callback:
                        progress_callback(index + 1, len(domains), f"Resolved {domain}")
                    
                    return result
                    
                except Exception as e:
                    result = {
                        'index': index,
                        'domain': domain,
                        'ips': [],
                        'success': False,
                        'lookup_time': 0,
                        'error': str(e)
                    }
                    
                    if progress_callback:
                        progress_callback(index + 1, len(domains), f"Failed to resolve {domain}")
                    
                    return result
        
        tasks = [lookup_domain(domain, i) for i, domain in enumerate(domains)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results and sort by original order
        processed_results = []
        for result in results:
            if isinstance(result, Exception):
                processed_results.append({
                    'index': len(processed_results),
                    'domain': 'unknown',
                    'ips': [],
                    'success': False,
                    'lookup_time': 0,
                    'error': str(result)
                })
            else:
                processed_results.append(result)
        
        processed_results.sort(key=lambda x: x['index'])
        return processed_results
    
    async def cleanup(self):
        """Clean up network resources."""
        if self.session and not self.session.closed:
            await self.session.close()
    
    def run_async_batch(self, async_func, *args, **kwargs):
        """
        Run async function in a new event loop (for sync contexts).
        
        Args:
            async_func: Async function to execute
            *args: Arguments for the function
            **kwargs: Keyword arguments for the function
        
        Returns:
            Function result
        """
        try:
            # Try to get existing event loop
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is running, use ThreadPoolExecutor to run in separate thread
                with ThreadPoolExecutor(max_workers=1) as executor:
                    future = executor.submit(asyncio.run, async_func(*args, **kwargs))
                    return future.result()
            else:
                # If loop is not running, we can use it directly
                return loop.run_until_complete(async_func(*args, **kwargs))
        except RuntimeError:
            # No event loop exists, create a new one
            return asyncio.run(async_func(*args, **kwargs))

# Global instance for reuse
_network_optimizer = None

def get_network_optimizer() -> AsyncNetworkOptimizer:
    """Get global network optimizer instance."""
    global _network_optimizer
    if _network_optimizer is None:
        _network_optimizer = AsyncNetworkOptimizer()
    return _network_optimizer

def batch_http_requests_sync(requests: List[Dict[str, Any]], 
                           progress_callback: Optional[Callable] = None) -> List[Dict[str, Any]]:
    """
    Synchronous wrapper for batch HTTP requests.
    
    Args:
        requests: List of request dictionaries
        progress_callback: Optional callback for progress updates
    
    Returns:
        List of response dictionaries
    """
    optimizer = get_network_optimizer()
    return optimizer.run_async_batch(
        optimizer.batch_http_requests, requests, progress_callback
    )

def batch_dns_lookups_sync(domains: List[str], 
                         progress_callback: Optional[Callable] = None) -> List[Dict[str, Any]]:
    """
    Synchronous wrapper for batch DNS lookups.
    
    Args:
        domains: List of domain names
        progress_callback: Optional callback for progress updates
    
    Returns:
        List of DNS lookup results
    """
    optimizer = get_network_optimizer()
    return optimizer.run_async_batch(
        optimizer.batch_dns_lookups, domains, progress_callback
    )

# Cleanup function for application shutdown
def cleanup_network_optimizer():
    """Clean up global network optimizer resources."""
    global _network_optimizer
    if _network_optimizer:
        asyncio.run(_network_optimizer.cleanup())
        _network_optimizer = None