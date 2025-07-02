"""
Custom rate limiting middleware for FastAPI.
Implements a sliding window rate limiter without external dependencies.
"""

from fastapi import Request
import time
from typing import Dict, List

# Rate limiting configuration
RATE_LIMIT_REQUESTS = 100  # Number of requests allowed
RATE_LIMIT_WINDOW = 60     # Time window in seconds (1 minute)
RATE_LIMIT_CLEANUP_INTERVAL = 300  # Clean up old entries every 5 minutes

class RateLimitMiddleware:
    """
    Custom rate limiting middleware using sliding window approach.
    Tracks requests per IP address without external dependencies.
    """
    
    def __init__(self):
        # Dictionary to store IP addresses and their request timestamps
        self.request_history: Dict[str, List[float]] = {}
        self.last_cleanup = time.time()
    
    def _cleanup_old_entries(self):
        """Remove old request history entries to prevent memory buildup."""
        current_time = time.time()
        
        # Only cleanup every RATE_LIMIT_CLEANUP_INTERVAL seconds
        if current_time - self.last_cleanup < RATE_LIMIT_CLEANUP_INTERVAL:
            return
            
        cutoff_time = current_time - RATE_LIMIT_WINDOW
        
        # Remove IPs with no recent requests
        ips_to_remove = []
        for ip, timestamps in self.request_history.items():
            # Filter out old timestamps
            recent_timestamps = [ts for ts in timestamps if ts > cutoff_time]
            if recent_timestamps:
                self.request_history[ip] = recent_timestamps
            else:
                ips_to_remove.append(ip)
        
        # Remove IPs with no recent activity
        for ip in ips_to_remove:
            del self.request_history[ip]
            
        self.last_cleanup = current_time
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address from request."""
        # Check for forwarded headers first (for proxy/load balancer scenarios)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
            
        # Fall back to direct client IP
        return request.client.host if request.client else "unknown"
    
    def is_rate_limited(self, request: Request) -> bool:
        """
        Check if the request should be rate limited.
        Returns True if rate limit is exceeded, False otherwise.
        """
        current_time = time.time()
        client_ip = self._get_client_ip(request)
        
        # Periodic cleanup
        self._cleanup_old_entries()
        
        # Initialize IP history if not exists
        if client_ip not in self.request_history:
            self.request_history[client_ip] = []
        
        # Remove timestamps outside the current window
        cutoff_time = current_time - RATE_LIMIT_WINDOW
        self.request_history[client_ip] = [
            ts for ts in self.request_history[client_ip] 
            if ts > cutoff_time
        ]
        
        # Check if rate limit exceeded
        if len(self.request_history[client_ip]) >= RATE_LIMIT_REQUESTS:
            return True
        
        # Add current request timestamp
        self.request_history[client_ip].append(current_time)
        return False