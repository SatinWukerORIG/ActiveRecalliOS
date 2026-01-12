#!/usr/bin/env python3
"""
Setup script for Live Activity and notification features
"""
import os
import sys
from app import create_app, db

#!/usr/bin/env python3
"""
Setup script for Live Activity and notification features
"""
import os
import sys
from app import create_app, db

def setup_database():
    """Initialize database with Live Activity support"""
    print("🗄️ Setting up database...")
    
    app = create_app()
    
    with app.app_context():
        # Import models to ensure they're registered
        from app.models import User, Card, ContentGeneration
        
        # Create all tables
        db.create_all()
        print("✅ Database tables created/updated")
        
        # Check if we need to add new columns (for existing databases)
        try:
            # Test if new columns exist
            user = User.query.first()
            if user:
                # Try to access new columns
                _ = user.recall_enabled
                _ = user.live_activity_enabled
                _ = user.last_notification_time
                print("✅ All required columns exist")
            else:
                print("ℹ️ No users found - database is ready for new users")
                
        except Exception as e:
            print(f"⚠️ Database schema might need updating: {e}")
            print("💡 Consider running database migrations or recreating the database")
    
    return True

def check_dependencies():
    """Check if all required dependencies are installed"""
    print("📦 Checking dependencies...")
    
    required_packages = [
        ('flask', 'flask'),
        ('flask_sqlalchemy', 'flask_sqlalchemy'),
        ('flask_login', 'flask_login'),
        ('werkzeug', 'werkzeug'),
        ('jwt', 'pyjwt'),
        ('httpx', 'httpx'),
        ('schedule', 'schedule'),
        ('openai', 'openai')
    ]
    
    missing_packages = []
    
    for import_name, package_name in required_packages:
        try:
            __import__(import_name)
            print(f"✅ {package_name}")
        except ImportError:
            missing_packages.append(package_name)
            print(f"❌ {package_name} - MISSING")
    
    if missing_packages:
        print(f"\n⚠️ Missing packages: {', '.join(missing_packages)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies are installed")
    return True

def check_configuration():
    """Check configuration requirements"""
    print("⚙️ Checking configuration...")
    
    # Check environment variables (optional for development)
    env_vars = {
        'APNS_AUTH_KEY_ID': 'Apple Push Notification Auth Key ID',
        'APNS_TEAM_ID': 'Apple Developer Team ID',
        'SECRET_KEY': 'Flask secret key'
    }
    
    for var, description in env_vars.items():
        value = os.environ.get(var)
        if value:
            print(f"✅ {var} is set")
        else:
            print(f"⚠️ {var} not set ({description})")
    
    print("ℹ️ Environment variables are optional for development/testing")
    return True

def create_sample_data():
    """Create sample data for testing"""
    print("📝 Creating sample data...")
    
    app = create_app()
    
    with app.app_context():
        from app.models import User, Card
        
        # Check if sample user exists
        sample_user = User.query.filter_by(username='demo_user').first()
        
        if not sample_user:
            # Create sample user
            sample_user = User(
                username='demo_user',
                email='demo@activerecall.com',
                first_name='Demo',
                last_name='User',
                recall_enabled=True,
                recall_frequency_minutes=30,
                live_activity_enabled=True,
                show_card_preview=True,
                show_progress_updates=True
            )
            sample_user.set_password('demo123')
            
            db.session.add(sample_user)
            db.session.commit()
            
            print(f"✅ Created sample user: {sample_user.username} (ID: {sample_user.id})")
            
            # Create sample cards
            sample_cards = [
                {
                    'front': 'What is Active Recall?',
                    'back': 'A learning technique that involves actively retrieving information from memory',
                    'content_type': 'flashcard',
                    'subject': 'Learning'
                },
                {
                    'front': 'Spaced Repetition Formula',
                    'back': 'SM-2 algorithm: I(n) = I(n-1) × EF',
                    'content_type': 'information',
                    'subject': 'Memory'
                },
                {
                    'front': 'Live Activity',
                    'back': 'iOS feature that displays real-time information on home screen and lock screen',
                    'content_type': 'flashcard',
                    'subject': 'iOS'
                }
            ]
            
            for card_data in sample_cards:
                card = Card(
                    user_id=sample_user.id,
                    front=card_data['front'],
                    back=card_data['back'],
                    content_type=card_data['content_type'],
                    subject=card_data['subject']
                )
                db.session.add(card)
            
            db.session.commit()
            print(f"✅ Created {len(sample_cards)} sample cards")
            
        else:
            print(f"ℹ️ Sample user already exists: {sample_user.username}")
    
    return True

def print_next_steps():
    """Print next steps for users"""
    print("\n🎉 Live Activity setup complete!")
    print("\n📋 Next Steps:")
    print("1. Start the Flask server: python run.py")
    print("2. Run tests: python test_live_activity_complete.py")
    print("3. Access web interface: http://localhost:5000")
    print("4. Login with demo user: demo_user / demo123")
    print("5. Configure notification settings: http://localhost:5000/notifications")
    print("\n📱 iOS Integration:")
    print("1. Update iOS app to register Live Activity tokens")
    print("2. Test Live Activity endpoints from iOS app")
    print("3. Configure APNs certificates for production")
    print("\n🔧 Development:")
    print("- API documentation: Check test_live_activity_complete.py for examples")
    print("- Notification settings: /notifications web interface")
    print("- Live Activity test: POST /api/live-activity/test")

def main():
    """Main setup function"""
    print("🚀 Active Recall Live Activity Setup")
    print("=" * 50)
    
    steps = [
        ("Check Dependencies", check_dependencies),
        ("Check Configuration", check_configuration),
        ("Setup Database", setup_database),
        ("Create Sample Data", create_sample_data)
    ]
    
    for step_name, step_func in steps:
        print(f"\n{step_name}...")
        try:
            if not step_func():
                print(f"❌ {step_name} failed")
                return False
        except Exception as e:
            print(f"❌ {step_name} failed with error: {e}")
            return False
    
    print_next_steps()
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)