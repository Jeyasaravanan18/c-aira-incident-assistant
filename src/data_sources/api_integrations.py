"""
External API Integrations
Provides real-time data from public APIs
"""

import requests
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class GitHubStatusAPI:
    """
    GitHub Status API Integration
    Provides real-time status of GitHub services
    """
    
    BASE_URL = "https://www.githubstatus.com/api/v2"
    CACHE_DURATION = timedelta(minutes=5)
    
    def __init__(self):
        """Initialize GitHub Status API client"""
        self._cache = {}
        self._last_fetch = None
    
    def _is_cache_valid(self) -> bool:
        """Check if cached data is still valid"""
        if self._last_fetch is None:
            return False
        return datetime.now() - self._last_fetch < self.CACHE_DURATION
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current GitHub status
        
        Returns:
            Dictionary with status information
        """
        # Return cached data if valid
        if self._is_cache_valid() and self._cache:
            logger.info("Returning cached GitHub status")
            return self._cache
        
        try:
            response = requests.get(
                f"{self.BASE_URL}/status.json",
                timeout=5
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Parse and format the response
            status_info = {
                'status': data.get('status', {}).get('indicator', 'unknown'),
                'description': data.get('status', {}).get('description', 'No description available'),
                'last_updated': datetime.now().isoformat(),
                'is_operational': data.get('status', {}).get('indicator') == 'none',
                'raw_data': data
            }
            
            # Cache the result
            self._cache = status_info
            self._last_fetch = datetime.now()
            
            logger.info(f"GitHub status fetched: {status_info['status']}")
            return status_info
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching GitHub status: {e}")
            return {
                'status': 'error',
                'description': f'Unable to fetch status: {str(e)}',
                'last_updated': datetime.now().isoformat(),
                'is_operational': None,
                'error': str(e)
            }
    
    def get_components(self) -> Dict[str, Any]:
        """
        Get status of individual GitHub components
        
        Returns:
            Dictionary with component statuses
        """
        try:
            response = requests.get(
                f"{self.BASE_URL}/components.json",
                timeout=5
            )
            response.raise_for_status()
            
            data = response.json()
            components = data.get('components', [])
            
            # Format component data
            component_status = {}
            for component in components:
                component_status[component['name']] = {
                    'status': component.get('status', 'unknown'),
                    'description': component.get('description', ''),
                    'updated_at': component.get('updated_at', '')
                }
            
            return component_status
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching GitHub components: {e}")
            return {}
    
    def get_recent_incidents(self, limit: int = 5) -> list:
        """
        Get recent GitHub incidents
        
        Args:
            limit: Maximum number of incidents to return
            
        Returns:
            List of recent incidents
        """
        try:
            response = requests.get(
                f"{self.BASE_URL}/incidents.json",
                timeout=5
            )
            response.raise_for_status()
            
            data = response.json()
            incidents = data.get('incidents', [])[:limit]
            
            # Format incident data
            formatted_incidents = []
            for incident in incidents:
                formatted_incidents.append({
                    'name': incident.get('name', 'Unknown'),
                    'status': incident.get('status', 'unknown'),
                    'impact': incident.get('impact', 'unknown'),
                    'created_at': incident.get('created_at', ''),
                    'shortlink': incident.get('shortlink', '')
                })
            
            return formatted_incidents
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching GitHub incidents: {e}")
            return []
    
    def is_github_down(self) -> bool:
        """
        Quick check if GitHub is experiencing issues
        
        Returns:
            True if GitHub has issues, False if operational
        """
        status = self.get_status()
        return not status.get('is_operational', True)
    
    def get_summary(self) -> str:
        """
        Get a human-readable summary of GitHub status
        
        Returns:
            Summary string
        """
        status = self.get_status()
        
        if status.get('status') == 'error':
            return "⚠️ Unable to check GitHub status"
        
        if status.get('is_operational'):
            return "✅ GitHub is operational - All systems normal"
        else:
            indicator = status.get('status', 'unknown')
            description = status.get('description', 'No details available')
            
            emoji_map = {
                'minor': '🟡',
                'major': '🟠',
                'critical': '🔴',
                'none': '✅'
            }
            
            emoji = emoji_map.get(indicator, '⚠️')
            return f"{emoji} GitHub Status: {description}"


class IPLocationAPI:
    """
    IP Geolocation API (ip-api.com)
    Free API for IP geolocation (no auth required)
    """
    
    BASE_URL = "http://ip-api.com/json"
    
    def __init__(self):
        """Initialize IP Location API client"""
        pass
    
    def get_location(self, ip: Optional[str] = None) -> Dict[str, Any]:
        """
        Get location information for an IP address
        
        Args:
            ip: IP address to lookup (None for current IP)
            
        Returns:
            Dictionary with location information
        """
        try:
            url = f"{self.BASE_URL}/{ip}" if ip else self.BASE_URL
            
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status') == 'success':
                return {
                    'country': data.get('country', 'Unknown'),
                    'region': data.get('regionName', 'Unknown'),
                    'city': data.get('city', 'Unknown'),
                    'timezone': data.get('timezone', 'Unknown'),
                    'isp': data.get('isp', 'Unknown'),
                    'ip': data.get('query', ip or 'Unknown')
                }
            else:
                return {'error': 'Location lookup failed'}
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching IP location: {e}")
            return {'error': str(e)}
    
    def get_summary(self, ip: Optional[str] = None) -> str:
        """
        Get human-readable location summary
        
        Args:
            ip: IP address to lookup
            
        Returns:
            Summary string
        """
        location = self.get_location(ip)
        
        if 'error' in location:
            return f"⚠️ Unable to determine location"
        
        return f"📍 Location: {location['city']}, {location['region']}, {location['country']}"
