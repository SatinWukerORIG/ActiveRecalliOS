# Active Recall - Effortless Learning Through Interruption

## 🧠 What We've Built

A Flask-based backend for the Active Recall app that enables effortless learning during "dead time" moments. The system supports both traditional flashcards and standalone information pieces with intelligent spaced repetition.

## ✅ Current Features

### Backend API (Flask)
- **User Management**: Create users with preferences (focus mode, sleep schedule, notification frequency)
- **Content Management**: Support for both flashcards and information pieces
- **Spaced Repetition**: SM-2 algorithm implementation for optimal learning intervals
- **Subject Organization**: Cards can be organized by subject and tagged
- **Statistics**: User learning statistics and progress tracking
- **Apple Push Notifications**: Infrastructure for iOS notifications and Live Activities
- **Device Token Management**: Registration for both standard and Live Activity push tokens
- **Smart Scheduling**: Context-aware notification system with background processing
- **Availability System**: Real-time checking of user availability based on focus mode and sleep schedule
- **Intelligent Interruptions**: Automated notification sending that respects user context
- **AI Content Generation**: OpenAI-powered content creation from study materials
- **Generation Tracking**: Complete audit trail of AI-generated content with metadata

### iOS App (SwiftUI)
- **Native iOS Interface**: Clean, modern SwiftUI design following iOS design guidelines
- **Dashboard**: Overview of learning progress with statistics and quick actions
- **Card Management**: Browse, filter, and organize flashcards and information pieces
- **Study Sessions**: Interactive study interface with spaced repetition feedback
- **Smart Settings**: User preferences with focus mode, sleep schedule, and availability controls
- **Push Notifications**: Rich notifications with interactive review buttons
- **Live Activities**: Dynamic Island and Lock Screen integration for study sessions
- **Real-time Sync**: Seamless integration with Flask backend API
- **Context Awareness**: Visual indicators of availability status and notification controls
- **AI Content Generation**: Native interface for creating content from study materials
- **Generation History**: Track and manage all AI-generated learning content

### Web Interface
- Clean, responsive design for content management
- Add flashcards and information pieces
- View all content with filtering
- Real-time statistics display
- Subject and tag management

### Smart Scheduling System
- **Background Scheduler**: Automated checking for due cards every 5 minutes
- **Context Awareness**: Respects focus mode and sleep schedule preferences
- **Intelligent Timing**: Only sends notifications when users are available
- **Manual Override**: API endpoints for testing and manual notification triggering
- **Availability API**: Real-time status checking with detailed reasoning

### AI Content Generation System
- **Multi-format Generation**: Create flashcards, information pieces, or mixed content
- **Intelligent Processing**: Advanced text analysis and concept extraction
- **Difficulty Scaling**: Easy, medium, and hard content generation levels
- **Subject Organization**: Automatic categorization and tagging of generated content
- **Generation Tracking**: Complete audit trail with status monitoring and error handling

## 🚀 Getting Started

### Prerequisites
```bash
# Python dependencies
pip install -r requirements.txt

# iOS development
# Xcode 15+ with iOS 17+ SDK
# Apple Developer Account (for push notifications)

# Optional: OpenAI API key for AI content generation
# Get from: https://platform.openai.com/
```

### Environment Variables
```bash
# Required for push notifications
export APNS_AUTH_KEY_ID="your_key_id"
export APNS_TEAM_ID="your_team_id"

# Optional for AI content generation
export OPENAI_API_KEY="your_openai_api_key"
```

### Running the Backend
```bash
python run.py
```

The server will start on `http://127.0.0.1:5000`

### Running the iOS App
1. Open the iOS project files in Xcode
2. Update the `baseURL` in `APIManager.swift` to your Flask server IP
3. Configure your Apple Developer Team and Bundle ID
4. Build and run on device or simulator

### Testing
```bash
# Test API endpoints
python test_api.py

# Test web interface
python test_web.py

# Test smart scheduling system
python test_smart_scheduling.py
```

## 📱 Next Development Phases

### Phase 1: Enhanced iOS Features (In Progress)
1. **Live Activity Enhancements**
   - ✅ Basic Live Activity structure
   - 🔄 Real-time progress updates from backend
   - 🔄 Interactive buttons in Live Activities
   - 🔄 Dynamic Island optimizations

2. **Advanced Notifications**
   - ✅ Rich notification categories
   - ✅ Interactive review buttons
   - 🔄 Scheduled notification system
   - 🔄 Context-aware notification timing

3. **iOS Widgets**
   - 🔄 Home Screen widget for quick stats
   - 🔄 Widget for due card count
   - 🔄 Study streak widget

### Phase 2: Android App Development
1. **Core Android App**
   - Native Android app with Material Design
   - Overlay permissions for unlock triggers
   - App-specific interruption system
   - Background service for notifications

2. **Android-Specific Features**
   - Lock screen overlays
   - App launch interruptions
   - Adaptive notification scheduling

### Phase 3: AI Content Generation
1. **LLM Integration**
   - API endpoint for processing study materials
   - Content generation from PDFs, text, images
   - Automatic flashcard and information piece creation
   - Quality scoring and optimization

2. **Enhanced API Endpoints**
   ```
   POST /generate-content
   POST /process-document
   GET /generation-history
   ```

### Phase 4: Advanced Features
1. **Community & Sharing**
   - Deck sharing system
   - Import/export functionality (Anki, Quizlet)
   - Community marketplace

2. **Analytics & Optimization**
   - Learning pattern analysis
   - Personalized scheduling
   - Performance insights

## 🏗️ Architecture

### Current Structure
```
/
├── .kiro/                    # Kiro IDE configuration and steering rules
├── .vscode/                  # VS Code settings
├── templates/                # Flask web interface templates
├── instance/                 # Flask instance folder
│   └── active_recall.db     # SQLite database
├── app.py                   # Flask backend application
├── requirements.txt         # Python dependencies
├── test_api.py             # API testing script
├── test_web.py             # Web interface testing
├── README.md               # This file
│
# iOS App Files
├── ActiveRecallApp.swift    # Main iOS app entry point
├── APIManager.swift         # Backend API integration
├── NotificationManager.swift # Push notifications & Live Activities
├── ContentView.swift        # Main app interface
├── CardsView.swift          # Card management interface
├── AddCardView.swift        # Add new cards
├── StudyView.swift          # Study session interface
├── SettingsView.swift       # App settings and preferences
├── .xcode                   # Live Activity attributes & backend connector
└── widgetUI.xcode          # Live Activity UI components
```

### API Endpoints
- `GET /` - Web interface
- `POST /users` - Create user
- `GET /users/{id}` - Get user details
- `PUT /users/{id}/preferences` - Update preferences
- `POST /cards` - Add content
- `GET /cards/{id}` - Get specific card
- `GET /users/{id}/cards` - Get user's cards
- `GET /users/{id}/cards/due` - Get due cards
- `POST /review/{card_id}` - Review and update SRS
- `GET /users/{id}/stats` - Get learning statistics

## 🔧 Configuration

### Environment Variables
```bash
APNS_AUTH_KEY_ID=your_key_id
APNS_TEAM_ID=your_team_id
```

### APNs Setup
1. Get `.p8` auth key from Apple Developer Account
2. Update `BUNDLE_ID` in app.py
3. Place auth key file in project root

## 🎯 Core Value Proposition

**Effortless learning through interruption** - The app utilizes "dead time" (unlocking phone, waiting for apps to load, scheduled intervals) to reinforce memory pathways without requiring dedicated study sessions.

## 📊 Technical Highlights

- **Spaced Repetition**: Proper SM-2 algorithm implementation
- **Dual Content Types**: Supports both Q&A flashcards and standalone information
- **Apple Integration**: Ready for iOS notifications and Live Activities
- **Scalable Architecture**: Clean separation of concerns, ready for modularization
- **Real-time Updates**: Dynamic content management with instant feedback

The foundation is solid and ready for mobile app development and AI integration!
