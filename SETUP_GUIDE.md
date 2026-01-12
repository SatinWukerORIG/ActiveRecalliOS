# Active Recall - Complete Setup Guide

## 🚀 Quick Start (5 Minutes)

### 1. **Install Python Dependencies**
```bash
# Install all required packages
pip install -r requirements.txt
```

### 2. **Start the Application**
```bash
# Run the new structured application
python run.py
```

You should see:
```
Starting Active Recall server on port 5000
Debug mode: False
Access the web interface at: http://localhost:5000
Database initialized with current schema
Notification scheduler started
* Running on http://0.0.0.0:5000
```

### 3. **Access Web Interface**
Open your browser and go to: `http://localhost:5000`

You'll see the new Active Recall dashboard with:
- **Dashboard**: Overview, quick actions, and content management
- **Study**: Interactive study sessions with spaced repetition
- **Analytics**: Learning progress and statistics

## 📁 New Project Structure

The application has been refactored into a proper Flask application structure:

```
/
├── app/                    # Main application package
│   ├── __init__.py        # Flask app factory
│   ├── models.py          # Database models
│   ├── config.py          # Configuration settings
│   ├── api/               # API endpoints
│   │   ├── __init__.py
│   │   ├── cards.py       # Card management
│   │   ├── users.py       # User management
│   │   ├── content_generation.py  # AI generation
│   │   ├── notifications.py       # Push notifications
│   │   └── import_export.py       # Data import/export
│   ├── services/          # Business logic
│   │   ├── spaced_repetition.py   # SM-2 algorithm
│   │   ├── ai_content_generator.py # AI generation
│   │   └── notification_service.py # Notifications
│   ├── web/               # Web interface
│   │   ├── __init__.py
│   │   └── routes.py      # Web routes
│   ├── templates/         # HTML templates
│   │   ├── base.html      # Base template
│   │   ├── index.html     # Dashboard
│   │   ├── study.html     # Study interface
│   │   └── analytics.html # Analytics
│   └── utils/             # Utilities
│       └── data_import.py # Import/export utilities
├── run.py                 # Application entry point
├── requirements.txt       # Python dependencies
└── [iOS files...]         # iOS Swift files
```

## 🆕 New Features

### **Enhanced Web Interface**
- **Modern Design**: Clean, responsive interface with better UX
- **Study Sessions**: Interactive study mode with spaced repetition
- **Analytics Dashboard**: Detailed learning statistics and progress tracking
- **Modal Dialogs**: Better user experience for adding cards and AI generation

### **Improved API Structure**
- **RESTful Design**: Proper API endpoints with consistent patterns
- **Better Error Handling**: Comprehensive error responses
- **API Documentation**: Clear endpoint structure

### **Data Import/Export**
- **CSV Import**: Import cards from spreadsheets
- **Anki Import**: Import from Anki JSON exports
- **CSV Export**: Export your cards for backup
- **Import Templates**: Get started quickly with templates

### **Enhanced Services**
- **Spaced Repetition Service**: Dedicated SM-2 algorithm implementation
- **AI Content Generator**: Improved OpenAI integration
- **Notification Service**: Smart scheduling and context awareness

## 🔧 API Endpoints

### **Cards**
- `POST /api/cards` - Create new card
- `GET /api/cards/{id}` - Get specific card
- `PUT /api/cards/{id}` - Update card
- `DELETE /api/cards/{id}` - Delete card
- `POST /api/cards/{id}/review` - Review card (spaced repetition)

### **Users**
- `POST /api/users` - Create user
- `GET /api/users/{id}` - Get user
- `PUT /api/users/{id}` - Update user preferences
- `GET /api/users/{id}/stats` - Get learning statistics
- `GET /api/users/{id}/cards` - Get user's cards
- `GET /api/users/{id}/review-session` - Get study session
- `GET /api/users/{id}/due-cards` - Get cards due for review

### **AI Content Generation**
- `POST /api/generate-content` - Generate content with AI
- `GET /api/users/{id}/content-generations` - Get generation history

### **Import/Export**
- `POST /api/users/{id}/import/csv` - Import from CSV
- `POST /api/users/{id}/import/anki` - Import from Anki
- `GET /api/users/{id}/export/csv` - Export to CSV
- `GET /api/import/template` - Get import template

### **Notifications**
- `POST /api/users/{id}/register-device` - Register device token
- `POST /api/users/{id}/register-live-activity` - Register Live Activity
- `GET /api/users/{id}/availability` - Check notification availability

## 🧪 Testing

### **Test the New Structure**
```bash
# Test basic functionality
python -c "from app import create_app; app = create_app(); print('✅ App creation successful')"

# Test database models
python -c "from app.models import User, Card; print('✅ Models imported successfully')"

# Test services
python -c "from app.services.spaced_repetition import SpacedRepetitionService; print('✅ Services working')"
```

### **Test API Endpoints**
```bash
# Test user creation
curl -X POST http://localhost:5000/api/users \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "email": "test@example.com"}'

# Test card creation
curl -X POST http://localhost:5000/api/cards \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "content_type": "flashcard", "front": "Test question", "back": "Test answer"}'
```

## 🔧 Configuration

### **Environment Variables**
```bash
# Optional: OpenAI API for AI generation
export OPENAI_API_KEY="your-openai-api-key"

# Optional: APNs for iOS push notifications
export APNS_AUTH_KEY_ID="your-key-id"
export APNS_TEAM_ID="your-team-id"
export BUNDLE_ID="com.yourname.recallapp"

# Optional: Custom database
export DATABASE_URL="sqlite:///custom_path.db"

# Optional: Flask settings
export FLASK_DEBUG="true"
export SECRET_KEY="your-secret-key"
```

## 🚀 Deployment

### **Production Setup**
```bash
# Install production dependencies
pip install gunicorn

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app()"
```

### **Docker Setup** (Optional)
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["python", "run.py"]
```

## 🔄 Migration from Old Structure

If you were using the old `app.py` file:

1. **Backup your database**: Copy `active_recall.db` to `active_recall_backup.db`
2. **Run the new application**: `python run.py`
3. **The new app will create tables automatically** and preserve existing data
4. **Test functionality** to ensure everything works
5. **Remove old files** once confirmed working

## 🎯 Next Steps

1. **Explore the new web interface** at `http://localhost:5000`
2. **Try the AI content generation** (requires OpenAI API key)
3. **Import existing cards** using the CSV import feature
4. **Set up iOS app** for mobile experience
5. **Configure push notifications** for smart interruptions

## 🐛 Troubleshooting

### **Common Issues**

**Import Error**: `ModuleNotFoundError: No module named 'app'`
- Solution: Make sure you're running `python run.py` from the project root

**Database Issues**: Tables not found
- Solution: Delete the database file and restart - tables will be recreated

**OpenAI Errors**: AI generation not working
- Solution: Set `OPENAI_API_KEY` environment variable

**Port Already in Use**: Address already in use
- Solution: Use a different port: `PORT=5001 python run.py`

The refactored application provides a much more maintainable and scalable foundation for the Active Recall project!
