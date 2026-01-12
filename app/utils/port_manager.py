"""
Port Management Utility for Active Recall Application

Provides robust port detection and management to avoid conflicts
with other services running on the system.
"""
import socket
import os
import sys
from typing import List, Optional


class PortManager:
    """Manages port allocation and availability checking"""
    
    # Default port preferences in order of preference
    DEFAULT_PORTS = [5001, 5002, 5003, 8000, 8001, 8080, 3000, 4000, 4999]
    
    # Ports to avoid (commonly used by other services)
    AVOID_PORTS = [
        5000,  # macOS AirPlay Receiver
        3000,  # Node.js development servers
        8080,  # Common HTTP proxy
        80,    # HTTP
        443,   # HTTPS
        22,    # SSH
        21,    # FTP
        25,    # SMTP
        53,    # DNS
        110,   # POP3
        143,   # IMAP
        993,   # IMAPS
        995,   # POP3S
    ]
    
    @staticmethod
    def is_port_available(port: int, host: str = 'localhost') -> bool:
        """
        Check if a port is available for binding.
        
        Args:
            port: Port number to check
            host: Host to check (default: localhost)
            
        Returns:
            True if port is available, False otherwise
        """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(1)
                result = sock.connect_ex((host, port))
                return result != 0
        except Exception:
            return False
    
    @staticmethod
    def find_available_port(
        preferred_ports: Optional[List[int]] = None,
        start_port: int = 5001,
        end_port: int = 9000,
        host: str = 'localhost'
    ) -> Optional[int]:
        """
        Find an available port, checking preferred ports first.
        
        Args:
            preferred_ports: List of preferred ports to check first
            start_port: Start of port range to scan if preferred ports unavailable
            end_port: End of port range to scan
            host: Host to check (default: localhost)
            
        Returns:
            Available port number or None if no port found
        """
        # Check preferred ports first
        if preferred_ports:
            for port in preferred_ports:
                if port not in PortManager.AVOID_PORTS and PortManager.is_port_available(port, host):
                    return port
        
        # Check default preferred ports
        for port in PortManager.DEFAULT_PORTS:
            if port not in PortManager.AVOID_PORTS and PortManager.is_port_available(port, host):
                return port
        
        # Scan range for available port
        for port in range(start_port, end_port + 1):
            if port not in PortManager.AVOID_PORTS and PortManager.is_port_available(port, host):
                return port
        
        return None
    
    @staticmethod
    def get_port_from_env_or_find(
        env_var: str = 'PORT',
        default_port: Optional[int] = None,
        preferred_ports: Optional[List[int]] = None
    ) -> int:
        """
        Get port from environment variable or find an available one.
        
        Args:
            env_var: Environment variable name to check
            default_port: Default port to try if env var not set
            preferred_ports: List of preferred ports
            
        Returns:
            Available port number
            
        Raises:
            RuntimeError: If no available port can be found
        """
        # Try environment variable first
        env_port = os.environ.get(env_var)
        if env_port:
            try:
                port = int(env_port)
                if PortManager.is_port_available(port):
                    return port
                else:
                    print(f"Warning: Port {port} from {env_var} is not available, finding alternative...")
            except ValueError:
                print(f"Warning: Invalid port value in {env_var}: {env_port}")
        
        # Try default port if provided
        if default_port and PortManager.is_port_available(default_port):
            return default_port
        
        # Find available port
        available_port = PortManager.find_available_port(preferred_ports)
        if available_port:
            return available_port
        
        raise RuntimeError("No available ports found in the specified range")
    
    @staticmethod
    def print_port_info(port: int, host: str = 'localhost'):
        """Print helpful information about the selected port"""
        print(f"🚀 Active Recall server starting on port {port}")
        print(f"📱 Web interface: http://{host}:{port}")
        print(f"🔗 API base URL: http://{host}:{port}/api")
        
        if port == 5000:
            print("⚠️  Warning: Port 5000 may conflict with macOS AirPlay Receiver")
        
        # Check what might be running on nearby ports
        nearby_ports = []
        for check_port in range(max(1024, port - 5), port + 6):
            if check_port != port and not PortManager.is_port_available(check_port):
                nearby_ports.append(check_port)
        
        if nearby_ports:
            print(f"ℹ️  Other services detected on nearby ports: {', '.join(map(str, nearby_ports))}")
    
    @staticmethod
    def check_system_conflicts():
        """Check for known system conflicts and provide warnings"""
        conflicts = []
        
        # Check for common macOS conflicts
        if sys.platform == 'darwin':  # macOS
            if not PortManager.is_port_available(5000):
                conflicts.append("Port 5000: Likely macOS AirPlay Receiver")
            if not PortManager.is_port_available(7000):
                conflicts.append("Port 7000: Likely macOS Control Center")
        
        # Check for common development server conflicts
        common_dev_ports = [3000, 3001, 8000, 8080, 4000]
        for port in common_dev_ports:
            if not PortManager.is_port_available(port):
                conflicts.append(f"Port {port}: Likely development server")
        
        if conflicts:
            print("🔍 Detected potential port conflicts:")
            for conflict in conflicts:
                print(f"   • {conflict}")
            print()