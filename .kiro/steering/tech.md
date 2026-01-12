# Technology Stack & Build System

## Backend Stack
- **Framework**: Flask (Python web framework)
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: JWT tokens for Apple Push Notification Service (APNs)
- **HTTP Client**: httpx for async HTTP/2 requests to APNs
- **Push Notifications**: Apple Push Notification Service integration

## Key Dependencies
- `flask` - Web framework
- `flask-sqlalchemy` - Database ORM
- `pyjwt` - JWT token generation for APNs auth
- `httpx` - Async HTTP client for APNs requests
- LLM integration (future) - For AI-generated content creation from study materials

## Environment Variables
Required environment variables for APNs integration:
- `APNS_AUTH_KEY_ID` - Apple Developer Auth Key ID
- `APNS_TEAM_ID` - Apple Developer Team ID

## Database Schema
- **User**: username, device_token, active_activity_token
- **Card**: Supports two content types:
  1. Traditional flashcards (front/back text)
  2. Information pieces (formulas, vocabulary, phrases)
  - Includes spaced repetition variables (interval, ease_factor, repetition_count, next_review)
- **Future**: Content generation metadata for LLM-created materials

## Common Commands
```bash
# Run development server
python app.py

# Database initialization (automatic on first run)
# Tables are created via db.create_all() in app context

# Install dependencies
pip install flask flask-sqlalchemy pyjwt httpx
```

## APNs Configuration
- Requires `.p8` auth key file from Apple Developer Account
- Bundle ID: `com.yourname.recallapp` (update for production)
- Supports both standard push notifications and Live Activity updates