import logging
from django.core.cache import cache
from django.http import HttpResponseForbidden
from django.conf import settings

logger = logging.getLogger('accounts')

class SecurityHeadersMiddleware:
    """
    Add security headers to all responses
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Add security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Add CSP header
        if not settings.DEBUG:
            response['Content-Security-Policy'] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
                "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
                "img-src 'self' data: https:; "
                "font-src 'self' https://cdn.jsdelivr.net; "
                "connect-src 'self'; "
                "frame-ancestors 'none';"
            )
        
        return response

class RateLimitMiddleware:
    """
    Rate limiting middleware to prevent abuse
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip rate limiting for authenticated staff users
        if request.user.is_authenticated and request.user.is_staff:
            return self.get_response(request)
        
        # Get client IP
        ip = self.get_client_ip(request)
        
        # Rate limit for application submissions
        if request.path == '/api/applications/' and request.method == 'POST':
            cache_key = f'rate_limit_app_{ip}'
            count = cache.get(cache_key, 0)
            
            if count >= settings.RATE_LIMIT_APPLICATIONS_PER_DAY:
                logger.warning(f'Rate limit exceeded for application submission from IP: {ip}')
                return HttpResponseForbidden('Rate limit exceeded. Please try again tomorrow.')
            
            cache.set(cache_key, count + 1, 86400)  # 24 hours
        
        # Rate limit for searches
        if request.path == '/api/applications/search_by_nid/' and request.method == 'POST':
            cache_key = f'rate_limit_search_{ip}'
            count = cache.get(cache_key, 0)
            
            if count >= settings.RATE_LIMIT_SEARCHES_PER_HOUR:
                logger.warning(f'Rate limit exceeded for search from IP: {ip}')
                return HttpResponseForbidden('Rate limit exceeded. Please try again later.')
            
            cache.set(cache_key, count + 1, 3600)  # 1 hour
        
        return self.get_response(request)

    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip