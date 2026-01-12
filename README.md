# Active Recall iOS

A SwiftUI iOS app for spaced repetition learning that utilizes "dead time" to reinforce memory pathways through smart interruptions.

## Features

- **Spaced Repetition System**: SM-2 algorithm implementation for optimal learning intervals
- **Dual Content Types**: Support for traditional flashcards and information pieces
- **Smart Study Sessions**: Interactive study interface with quality-based review
- **Push Notifications**: Rich notifications with actionable buttons for quick reviews
- **Live Activities**: Real-time study session progress tracking
- **Content Management**: Organize cards by subject and tags
- **AI Integration**: Ready for LLM-generated content creation

## Architecture

- **SwiftUI**: Modern declarative UI framework
- **MVVM Pattern**: Clean separation of concerns with ObservableObject
- **REST API Integration**: Full backend integration with Flask server
- **Push Notifications**: Apple Push Notification Service (APNs) support
- **Live Activities**: iOS 16+ dynamic island and lock screen widgets

## Backend Integration

This iOS app connects to the Active Recall Flask backend server:
- **API Endpoint**: `http://127.0.0.1:5001` (configurable)
- **Port Management**: Automatic port conflict resolution
- **Authentication**: JWT token-based authentication for APNs
- **Real-time Sync**: Immediate synchronization of study progress

## Key Components

### Data Models
- `User`: User profile and preferences
- `Card`: Flashcard content with spaced repetition variables
- `UserStats`: Learning progress and statistics
- `AppState`: Global app state management

### Views
- `StudyView`: Interactive spaced repetition study sessions
- `CardsView`: Card library with filtering and organization
- `AddCardView`: Create new flashcards and information pieces
- `SettingsView`: User preferences and configuration
- `ContentView`: Main app navigation and dashboard

### Services
- `APIManager`: REST API communication with backend
- `NotificationManager`: Push notification handling and scheduling

## Setup

1. **Prerequisites**:
   - Xcode 15.0+
   - iOS 16.0+ target
   - Active Recall Flask backend server

2. **Configuration**:
   - Update `APIManager.baseURL` with your server address
   - Configure Apple Developer account for push notifications
   - Set up APNs authentication keys

3. **Build and Run**:
   - Open `ActiveRecallApp.xcodeproj` in Xcode
   - Select your target device/simulator
   - Build and run (`Cmd+R`)

## Backend Repository

The Flask backend server is available at: [ActiveRecallG](https://github.com/SatinWukerORIG/ActiveRecallG)

## Development Status

✅ **Complete iOS Implementation**:
- All build errors resolved
- Full API integration
- Complete UI components
- Modern iOS 17+ compatibility
- Push notification support
- Live Activities integration

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly on device and simulator
5. Submit a pull request

## License

This project is part of the Active Recall learning system.