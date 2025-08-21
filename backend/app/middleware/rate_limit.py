"""
Rate limiting middleware for API endpoints.
"""

import time
from typing import Dict, Optional
from fastapi import Request, Response, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import asyncio
from collections import defaultdict
from datetime import datetime, timedelta


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware using in-memory storage."""
    
    def __init__(self, app, calls: int = 100, period: int = 60):
        super().__init__(app)
        self.calls = calls
        self.period = period
        self.clients: Dict[str, Dict] = defaultdict(lambda: {"calls": [], "blocked_until": None})
        
        # Start cleanup task
        asyncio.create_task(self._cleanup_task())
    
    async def dispatch(self, request: Request, call_next):
        """Process request with rate limiting."""
        
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/metrics"]:
            return await call_next(request)
        
        # Get client identifier
        client_id = self._get_client_id(request)
        
        # Check if client is currently blocked
        client_data = self.clients[client_id]
        now = datetime.utcnow()
        
        if client_data["blocked_until"] and now < client_data["blocked_until"]:
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Too Many Requests",
                    "detail": f"Rate limit exceeded. Try again after {client_data['blocked_until'].isoformat()}",
                    "retry_after": int((client_data["blocked_until"] - now).total_seconds())
                },
                headers={"Retry-After": str(int((client_data["blocked_until"] - now).total_seconds()))}
            )
        
        # Clean old calls
        cutoff_time = now - timedelta(seconds=self.period)
        client_data["calls"] = [
            call_time for call_time in client_data["calls"] 
            if call_time > cutoff_time
        ]
        
        # Check rate limit
        if len(client_data["calls"]) >= self.calls:
            # Block client for the remaining period
            client_data["blocked_until"] = now + timedelta(seconds=self.period)
            
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Too Many Requests",
                    "detail": f"Rate limit of {self.calls} requests per {self.period} seconds exceeded",
                    "retry_after": self.period
                },
                headers={"Retry-After": str(self.period)}
            )
        
        # Record this call
        client_data["calls"].append(now)
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        remaining_calls = max(0, self.calls - len(client_data["calls"]))
        response.headers["X-RateLimit-Limit"] = str(self.calls)
        response.headers["X-RateLimit-Remaining"] = str(remaining_calls)
        response.headers["X-RateLimit-Reset"] = str(int((now + timedelta(seconds=self.period)).timestamp()))
        
        return response
    
    def _get_client_id(self, request: Request) -> str:
        """Get client identifier for rate limiting."""
        # Try to get user ID from JWT token
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            # In a real implementation, you would decode the JWT here
            # For now, use the token as identifier
            return f"user:{auth_header[7:20]}"  # Use first part of token
        
        # Fall back to IP address
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()
        else:
            client_ip = request.client.host
        
        return f"ip:{client_ip}"
    
    async def _cleanup_task(self):
        """Periodic cleanup of old rate limit data."""
        while True:
            await asyncio.sleep(300)  # Cleanup every 5 minutes
            
            now = datetime.utcnow()
            cutoff_time = now - timedelta(seconds=self.period * 2)  # Keep data for 2x the period
            
            # Clean up old client data
            clients_to_remove = []
            for client_id, client_data in self.clients.items():
                # Remove old calls
                client_data["calls"] = [
                    call_time for call_time in client_data["calls"] 
                    if call_time > cutoff_time
                ]
                
                # Remove expired blocks
                if client_data["blocked_until"] and now > client_data["blocked_until"]:
                    client_data["blocked_until"] = None
                
                # Mark empty clients for removal
                if not client_data["calls"] and not client_data["blocked_until"]:
                    clients_to_remove.append(client_id)
            
            # Remove empty clients
            for client_id in clients_to_remove:
                del self.clients[client_id]


class RateLimiter:
    """Redis-based rate limiter for production use."""
    
    def __init__(self, redis_client=None):
        self.redis = redis_client
    
    async def is_allowed(self, key: str, limit: int, window: int) -> tuple[bool, Dict[str, int]]:
        """Check if request is allowed and return rate limit info."""
        if not self.redis:
            return True, {"limit": limit, "remaining": limit, "reset": int(time.time()) + window}
        
        try:
            # Use sliding window log algorithm
            now = time.time()
            window_start = now - window
            
            pipe = self.redis.pipeline()
            pipe.zremrangebyscore(key, 0, window_start)  # Remove old entries
            pipe.zcard(key)  # Count current entries
            pipe.zadd(key, {str(now): now})  # Add current request
            pipe.expire(key, window)  # Set expiration
            
            results = await pipe.execute()
            current_requests = results[1]
            
            allowed = current_requests < limit
            remaining = max(0, limit - current_requests - 1)
            reset_time = int(now + window)
            
            return allowed, {
                "limit": limit,
                "remaining": remaining,
                "reset": reset_time
            }
            
        except Exception:
            # Fail open - allow request if Redis is down
            return True, {"limit": limit, "remaining": limit, "reset": int(time.time()) + window}


# Decorator for endpoint-specific rate limiting
def rate_limit(calls: int = 60, period: int = 60):
    """Decorator for applying rate limits to specific endpoints."""
    def decorator(func):
        func._rate_limit = {"calls": calls, "period": period}
        return func
    return decorator


# Rate limiting dependency
async def get_rate_limit_info(request: Request) -> Optional[Dict[str, int]]:
    """Get current rate limit information for the client."""
    # This would be implemented based on your rate limiting strategy
    return {
        "limit": 100,
        "remaining": 95,
        "reset": int(time.time()) + 60
    }