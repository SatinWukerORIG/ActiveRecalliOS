# iOS App Setup Guide

## Project Configuration

### 1. Xcode Project Setup
1. Create a new iOS project in Xcode
2. Choose SwiftUI as the interface
3. Enable the following capabilities:
   - Push Notifications
   - Background Modes (Background processing, Remote notifications)
   - App Groups (for widget/Live Activity data sharing)

### 2. Required Frameworks
Add these frameworks to your project:
- `UserNotifications`
- `ActivityKit` (iOS 16.1+)
- `WidgetKit`
- `SwiftUI`

### 3. File Structure
Copy these Swift files into your Xcode project:
```
ActiveRecall/
├── ActiveRecallApp.swift      # Main app entry point
├── Models/
│   ├── APIManager.swift       # Backend integration
│   └── NotificationManager.swift # Push notification handling
├── Views/
│   ├── ContentView.swift      # Main navigation
│   ├── DashboardView.swift    # Dashboard (in ContentView.swift)
│   ├── CardsView.swift        # Card management
│   ├── AddCardView.swift      # Add new cards
│   ├── StudyView.swift        # Study sessions
│   └── SettingsView.swift     # App settings
└── Extensions/
    ├── LiveActivity.swift     # Live Activity attributes (.xcode file)
    └── WidgetExtension/       # Widget and Live Activity UI
        └── WidgetUI.swift     # Widget UI (widgetUI.xcode file)
```

### 4. Backend Configuration
1. Update `APIManager.swift`:
   ```swift
   private let baseURL = "http://YOUR_COMPUTER_IP:5000"
   ```
   
2. For local testing, find your computer's IP:
   ```bash
   # On macOS/Linux
   ifconfig | grep "inet " | grep -v 127.0.0.1
   
   # On Windows
   ipconfig | findstr "IPv4"
   ```

### 5. Apple Developer Setup
1. **App ID Configuration**:
   - Enable Push Notifications capability
   - Enable App Groups capability

2. **APNs Key**:
   - Create an APNs Authentication Key in Apple Developer portal
   - Download the `.p8` file
   - Note the Key ID and Team ID

3. **Update Flask Backend**:
   ```python
   APNS_AUTH_KEY_ID = "YOUR_KEY_ID"
   APNS_TEAM_ID = "YOUR_TEAM_ID"
   BUNDLE_ID = "com.yourname.activerecall"
   APNS_KEY_PATH = "AuthKey_XXXXXXXXXX.p8"
   ```

### 6. Live Activity Setup
1. Create a Widget Extension target in Xcode
2. Enable Live Activities in the widget extension
3. Add the Live Activity attributes and UI code
4. Configure App Groups for data sharing

### 7. Testing Checklist
- [ ] App builds and runs on device
- [ ] Backend API connection works
- [ ] User creation and card management functional
- [ ] Push notification permissions requested
- [ ] Test notifications work
- [ ] Live Activity can be started
- [ ] Study session flow works end-to-end

### 8. Common Issues & Solutions

**Issue**: "Cannot connect to Flask server"
- **Solution**: Ensure your iOS device and computer are on the same network
- Use your computer's actual IP address, not localhost/127.0.0.1

**Issue**: "Push notifications not working"
- **Solution**: 
  - Ensure you're testing on a physical device (not simulator)
  - Check that push notification permissions are granted
  - Verify APNs configuration in Apple Developer portal

**Issue**: "Live Activities not appearing"
- **Solution**:
  - Ensure iOS 16.1+ and Live Activities are enabled in Settings
  - Check that the widget extension is properly configured
  - Verify App Groups are set up correctly

### 9. Production Deployment
1. Update backend URL to production server
2. Configure proper APNs environment (sandbox vs production)
3. Set up proper error handling and logging
4. Implement proper user authentication
5. Add analytics and crash reporting

## Development Tips
- Use Xcode's Network Link Conditioner to test poor network conditions
- Test on multiple iOS versions and device sizes
- Use Xcode's Push Notification Console for testing APNs
- Monitor device logs for debugging Live Activities
- Test notification handling in all app states (foreground, background, terminated)