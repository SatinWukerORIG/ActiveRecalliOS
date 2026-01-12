#!/usr/bin/env python3
"""
Active Recall Application Entry Point
"""
import os
import sys
from app.utils.port_manager import PortManager

def main():
    """Main application entry point with robust port management"""
    
    print("🚀 Active Recall Server Starting...")
    
    # Check for system conflicts
    print("🔍 Checking for port conflicts...")
    PortManager.check_system_conflicts()
    
    # Get available port
    try:
        port = PortManager.get_port_from_env_or_find(
            env_var='PORT',
            preferred_ports=[5001, 5002, 8000, 8001, 4000]
        )
    except RuntimeError as e:
        print(f"❌ Error: {e}")
        print("💡 Try setting a specific port with: export PORT=8000")
        sys.exit(1)
    
    # Configuration
    host = os.environ.get('HOST', '0.0.0.0')
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Print server information
    PortManager.print_port_info(port, 'localhost' if host == '0.0.0.0' else host)
    print(f"🐛 Debug mode: {debug_mode}")
    print("=" * 50)
    
    # Create Flask application
    print("🏗️  Creating Flask application...")
    from app import create_app
    app = create_app()
    
    # Initialize notification service
    print("📅 Initializing notification service...")
    from app.services.notification_service import NotificationService
    notification_service = NotificationService()
    
    # Start notification scheduler
    print("📅 Starting notification scheduler...")
    notification_service.start_scheduler()
    
    try:
        # Run the application
        print(f"🚀 Starting Flask server on {host}:{port}")
        print("=" * 50)
        app.run(
            host=host,
            port=port,
            debug=debug_mode
        )
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
    except Exception as e:
        print(f"❌ Server error: {e}")
    finally:
        print("📅 Stopping notification scheduler...")
        notification_service.stop_scheduler()
        print("✅ Server stopped gracefully.")

if __name__ == '__main__':
    main()