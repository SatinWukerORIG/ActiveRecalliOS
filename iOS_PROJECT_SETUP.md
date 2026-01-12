# Active Recall iOS Project Setup

## Project Structure

I've created a proper Xcode project structure for your Active Recall iOS app. Here's what was created:

```
ActiveRecallApp.xcodeproj/          # Xcode project file
├── project.pbxproj                 # Project configuration

ActiveRecallApp/                    # Main app target
├── ActiveRecallApp.swift          # App entry point
├── Views/                         # SwiftUI views
│   ├── ContentView.swift         # Main content view with tab navigation
│   ├── StudyView.swift           # Study session interface
│   ├── CardsView.swift           # Card management
│   ├── AddCardView.swift         # Add new cards
│   ├── SettingsView.swift        # App settings
│   └── AIGenerationView.swift    # AI content generation
├── Managers/                      # Business logic managers
│   ├── APIManager.swift          # Backend API communication
│   ├── NotificationManager.swift # Push notifications
│   └── LiveActivityManager.swift # Live Activities
├── Models/                        # Data models
│   └── DataModels.swift          # User, Card, and other models
├── Assets.xcassets/              # App icons and assets
└── Preview Content/              # SwiftUI preview assets

ActiveRecallWidgetExtension/        # Widget extension target
├── ActiveRecallWidget.swift      # Live Activity widget implementation
├── RecallAttributes.swift        # Live Activity data structure
└── Info.plist                   # Widget configuration
```

## How to Open and Use

### 1. Open in Xcode
```bash
# Navigate to your project directory
cd /path/to/your/project

# Open the Xcode project
open ActiveRecallApp.xcodeproj
```

### 2. Configure Development Team
1. Select the project in Xcode's navigator
2. Under "Signing & Capabilities" for both targets:
   - Set your Apple Developer Team
   - Ensure bundle identifiers are unique (e.g., `com.yourname.activerecall`)

### 3. Update Backend URL
In `ActiveRecallApp/Managers/APIManager.swift`, update the `baseURL`:
```swift
// For device testing, use your computer's IP address
private let baseURL = "http://YOUR_COMPUTER_IP:5000"
```

### 4. Build and Run
- Select your target device or simulator
- Press Cmd+R to build and run

## Key Features Implemented

### 📱 Main App Features
- **Tab Navigation**: Dashboard, Cards, Study, AI Generate, Settings
- **Study Sessions**: Spaced repetition with Live Activity integration
- **Card Management**: Add, view, and organize flashcards and information pieces
- **AI Generation**: Create content from study materials
- **Smart Notifications**: Context-aware push notifications

### 🔴 Live Activities (iOS 16.1+)
- **Dynamic Island**: Shows study progress and current question
- **Lock Screen**: Rich study session interface
- **Phone Unlock Detection**: Updates content when phone is unlocked
- **Push Updates**: Backend can update Live Activities remotely

### 🔔 Push Notifications
- **Interactive Notifications**: Review cards directly from notifications
- **Smart Scheduling**: Respects focus mode and sleep schedule
- **Spaced Repetition**: Optimal timing based on SM-2 algorithm

## Backend Integration

The iOS app integrates with your Flask backend through these endpoints:

### User Management
- `POST /users` - Create user
- `GET /users/{id}` - Get user details
- `PUT /users/{id}/preferences` - Update preferences

### Card Management
- `POST /cards` - Add new card
- `GET /users/{id}/cards` - Get user's cards
- `GET /users/{id}/cards/due` - Get due cards
- `POST /review/{card_id}` - Review card

### Live Activities
- `POST /api/live-activity/start` - Start Live Activity
- `POST /api/live-activity/update-progress` - Update progress
- `POST /api/live-activity/end` - End session

### AI Generation
- `POST /generate-content` - Generate cards from study material

## Development Notes

### Live Activities Requirements
- iOS 16.1+ for Live Activities
- iOS 16.2+ for Dynamic Island
- Requires proper entitlements and push notification setup

### Push Notifications Setup
1. Enable Push Notifications capability in Xcode
2. Configure APNs certificates in Apple Developer Console
3. Update backend with proper APNs configuration

### Testing on Device
- Live Activities only work on physical devices
- Use your computer's IP address for API calls
- Ensure your Flask server is accessible from the device's network

## Next Steps

1. **Open the project** in Xcode
2. **Configure signing** with your Apple Developer account
3. **Update API endpoints** to match your backend
4. **Test on device** for full Live Activity functionality
5. **Configure push notifications** for production use

The project structure follows iOS best practices with proper separation of concerns, SwiftUI for the interface, and integration with your existing Flask backend.