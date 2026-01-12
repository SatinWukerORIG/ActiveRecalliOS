# Project Structure & Organization

## Current Structure
```
/
├── .kiro/              # Kiro IDE configuration and steering rules
├── .vscode/            # VS Code settings
├── app/                # Main application package
│   ├── __init__.py    # Flask app factory
│   ├── models.py      # Database models
│   ├── config.py      # Configuration settings
│   ├── api/           # API endpoints (blueprints)
│   ├── services/      # Business logic services
│   ├── web/           # Web interface routes
│   ├── templates/     # HTML templates
│   └── utils/         # Utility functions
├── instance/          # Flask instance folder
│   └── active_recall.db # SQLite database file
├── run.py            # Application entry point
└── [legacy files]    # Original monolithic files
```

## Code Organization Patterns

### Flask Application Factory Pattern
Using modern Flask application factory pattern with blueprints:
- **app/__init__.py**: Creates and configures Flask app
- **app/config.py**: Environment-based configuration
- **run.py**: Application entry point with service initialization

### Database Models (app/models.py)
- **User Model**: Handles device tokens, preferences, and relationships
- **Card Model**: Supports dual content types with spaced repetition variables
- **ContentGeneration Model**: Tracks AI generation requests and results
- Foreign key relationships with proper cascading

### Service Layer Architecture (app/services/)
- **SpacedRepetitionService**: SM-2 algorithm implementation and card scheduling
- **AIContentGenerator**: OpenAI integration for content generation
- **NotificationService**: Push notification scheduling and context awareness
- **DataImporter**: CSV/Anki import/export utilities

### API Blueprint Structure (app/api/)
- **cards.py**: Card CRUD operations and review endpoints
- **users.py**: User management and statistics
- **content_generation.py**: AI generation endpoints
- **notifications.py**: Push notification registration
- **import_export.py**: Data import/export endpoints

### Web Interface (app/web/)
- **routes.py**: Web interface routes with API compatibility
- **templates/**: Modern responsive HTML templates with base template inheritance
- **base.html**: Shared layout with navigation and styling
- **index.html**: Dashboard with stats and quick actions
- **study.html**: Interactive study session interface
- **analytics.html**: Learning progress and statistics

### Configuration Management
- Environment variables for all sensitive credentials
- Separate development/production/testing configurations
- Proper secret key management and database URI configuration
- Centralized settings in app/config.py

### API Endpoint Patterns
RESTful API design with consistent patterns:
- `POST /api/cards` - Create new card
- `GET /api/cards/{id}` - Get specific card
- `PUT /api/cards/{id}` - Update card
- `DELETE /api/cards/{id}` - Delete card
- `POST /api/cards/{id}/review` - Process spaced repetition review
- `GET /api/users/{id}/review-session` - Get study session batch
- `POST /api/generate-content` - AI content generation
- `POST /api/users/{id}/import/csv` - Import from CSV
- `GET /api/users/{id}/export/csv` - Export to CSV

### Modern Features Added
- **Data Import/Export**: CSV and Anki import with proper error handling
- **Enhanced Web Interface**: Modern responsive design with modal dialogs
- **Interactive Study Sessions**: Proper spaced repetition interface
- **Analytics Dashboard**: Learning statistics and progress tracking
- **Better Error Handling**: Comprehensive API error responses
- **Service Layer**: Separation of business logic from routes