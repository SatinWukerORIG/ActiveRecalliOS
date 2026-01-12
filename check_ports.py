#!/usr/bin/env python3
"""
Port availability checker for Active Recall application

Usage:
  python3 check_ports.py           # Check default ports
  python3 check_ports.py 8000 8001 # Check specific ports
"""
import sys
from app.utils.port_manager import PortManager

def main():
    """Check port availability and system conflicts"""
    
    print("🔍 Active Recall Port Checker")
    print("=" * 40)
    
    # Check system conflicts
    PortManager.check_system_conflicts()
    
    # Check specific ports if provided as arguments
    if len(sys.argv) > 1:
        ports_to_check = []
        for arg in sys.argv[1:]:
            try:
                ports_to_check.append(int(arg))
            except ValueError:
                print(f"❌ Invalid port number: {arg}")
                continue
        
        print(f"📋 Checking specified ports: {ports_to_check}")
        for port in ports_to_check:
            available = PortManager.is_port_available(port)
            status = "✅ Available" if available else "❌ In use"
            print(f"   Port {port}: {status}")
    
    # Find and suggest available ports
    print("\n🔍 Finding available ports...")
    available_port = PortManager.find_available_port()
    
    if available_port:
        print(f"✅ Recommended port: {available_port}")
        PortManager.print_port_info(available_port)
    else:
        print("❌ No available ports found in default range")
    
    # Show default preferred ports status
    print(f"\n📋 Default preferred ports status:")
    for port in PortManager.DEFAULT_PORTS:
        available = PortManager.is_port_available(port)
        status = "✅ Available" if available else "❌ In use"
        print(f"   Port {port}: {status}")
    
    print(f"\n💡 Usage tips:")
    print(f"   • Set specific port: export PORT=8000 && python3 run.py")
    print(f"   • Check port conflicts: python3 check_ports.py")
    print(f"   • Check specific ports: python3 check_ports.py 8000 8001")

if __name__ == '__main__':
    main()