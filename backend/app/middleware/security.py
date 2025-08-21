"""
Security middleware for the Facebook Analytics Platform.
"""

import logging
from typing import List
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import re
import time

logger = logging.getLogger(__name__)


class SecurityMiddleware(BaseHTTPMiddleware):
    """Security middleware for adding security headers and basic protection."""
    
    def __init__(self, app):
        super().__init__(app)
        
        # Security headers
        self.security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
        }
        
        # Suspicious patterns (basic WAF functionality)
        self.suspicious_patterns = [
            re.compile(r"<script[^>]*>.*?</script>", re.IGNORECASE | re.DOTALL),
            re.compile(r"javascript:", re.IGNORECASE),
            re.compile(r"vbscript:", re.IGNORECASE),
            re.compile(r"on\w+\s*=", re.IGNORECASE),
            re.compile(r"union.*select", re.IGNORECASE),
            re.compile(r"insert.*into", re.IGNORECASE),
            re.compile(r"drop.*table", re.IGNORECASE),
            re.compile(r"delete.*from", re.IGNORECASE),
        ]
        
        # Blocked user agents
        self.blocked_user_agents = [
            "curl",
            "wget",
            "python-requests",
            "bot",
            "crawler",
            "spider",
        ]
    
    async def dispatch(self, request: Request, call_next):
        """Process request with security checks."""
        
        # Check for blocked user agents (except for health checks)
        if request.url.path not in ["/health", "/metrics"]:
            user_agent = request.headers.get("user-agent", "").lower()
            if any(blocked in user_agent for blocked in self.blocked_user_agents):
                logger.warning(f"Blocked request from user agent: {user_agent}")
                return JSONResponse(
                    status_code=403,
                    content={"error": "Forbidden", "detail": "User agent not allowed"}
                )
        
        # Check for suspicious patterns in URL and query parameters
        full_url = str(request.url)
        if self._contains_suspicious_content(full_url):
            logger.warning(f"Blocked suspicious request: {full_url}")
            return JSONResponse(
                status_code=400,
                content={"error": "Bad Request", "detail": "Suspicious content detected"}
            )
        
        # Check request body for POST/PUT requests
        if request.method in ["POST", "PUT", "PATCH"]:
            # Read body for inspection (this consumes the stream)
            body = await request.body()
            
            # Create new request with the body
            async def receive():
                return {"type": "http.request", "body": body}
            
            request._receive = receive
            
            # Check body content
            if body and self._contains_suspicious_content(body.decode("utf-8", errors="ignore")):
                logger.warning(f"Blocked request with suspicious body content")
                return JSONResponse(
                    status_code=400,
                    content={"error": "Bad Request", "detail": "Suspicious content in request body"}
                )
        
        # Process request
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Add security headers
        for header, value in self.security_headers.items():
            response.headers[header] = value
        
        # Add server timing header
        response.headers["Server-Timing"] = f"total;dur={process_time*1000:.2f}"
        
        # Remove server header for security
        if "server" in response.headers:
            del response.headers["server"]
        
        return response
    
    def _contains_suspicious_content(self, content: str) -> bool:
        """Check if content contains suspicious patterns."""
        return any(pattern.search(content) for pattern in self.suspicious_patterns)


class IPWhitelistMiddleware(BaseHTTPMiddleware):
    """IP whitelist middleware for restricting access to specific IPs."""
    
    def __init__(self, app, whitelist: List[str] = None, enabled: bool = False):
        super().__init__(app)
        self.whitelist = whitelist or []
        self.enabled = enabled
    
    async def dispatch(self, request: Request, call_next):
        """Check IP whitelist."""
        if not self.enabled:
            return await call_next(request)
        
        # Get client IP
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()
        else:
            client_ip = request.client.host
        
        # Check whitelist
        if self.whitelist and client_ip not in self.whitelist:
            logger.warning(f"Blocked request from non-whitelisted IP: {client_ip}")
            return JSONResponse(
                status_code=403,
                content={"error": "Forbidden", "detail": "IP address not allowed"}
            )
        
        return await call_next(request)


class CSRFProtectionMiddleware(BaseHTTPMiddleware):
    """CSRF protection middleware."""
    
    def __init__(self, app, exempt_paths: List[str] = None):
        super().__init__(app)
        self.exempt_paths = exempt_paths or ["/api/auth/", "/health", "/metrics"]
    
    async def dispatch(self, request: Request, call_next):
        """Check CSRF token for state-changing requests."""
        
        # Skip for safe methods and exempt paths
        if request.method in ["GET", "HEAD", "OPTIONS"]:
            return await call_next(request)
        
        # Check if path is exempt
        path = request.url.path
        if any(path.startswith(exempt) for exempt in self.exempt_paths):
            return await call_next(request)
        
        # Check for CSRF token
        csrf_token = request.headers.get("X-CSRF-Token")
        if not csrf_token:
            return JSONResponse(
                status_code=403,
                content={"error": "Forbidden", "detail": "CSRF token required"}
            )
        
        # Validate CSRF token (implement your validation logic)
        if not self._validate_csrf_token(csrf_token):
            return JSONResponse(
                status_code=403,
                content={"error": "Forbidden", "detail": "Invalid CSRF token"}
            )
        
        return await call_next(request)
    
    def _validate_csrf_token(self, token: str) -> bool:
        """Validate CSRF token."""
        # Implement your CSRF token validation logic here
        # For now, accept any non-empty token
        return bool(token)


class ContentSecurityPolicyMiddleware(BaseHTTPMiddleware):
    """Content Security Policy middleware."""
    
    def __init__(self, app, csp_policy: str = None):
        super().__init__(app)
        self.csp_policy = csp_policy or (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data: https:; "
            "connect-src 'self' https://graph.facebook.com https://api.github.com; "
            "frame-ancestors 'none';"
        )
    
    async def dispatch(self, request: Request, call_next):
        """Add CSP header to responses."""
        response = await call_next(request)
        
        # Add CSP header for HTML responses
        content_type = response.headers.get("content-type", "")
        if "text/html" in content_type:
            response.headers["Content-Security-Policy"] = self.csp_policy
        
        return response