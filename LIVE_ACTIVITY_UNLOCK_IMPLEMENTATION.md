# Live Activity Unlock Implementation Guide

## Overview
This implementation enables Live Activities to display study content whenever the iPhone is unlocked, perfectly embodying Active Recall's core value proposition of "effortless learning through interruption."

## 🎯 How It Works

### **User Experience Flow:**
1. **User enables Live Activities** in app settings
2. **Live Activity starts** showing initial study content
3. **Phone gets unlocked** → iOS app detects unlock event
4. **Backend called** to get new random study content
5. **Live Activity updates** with fresh content on lock screen
6. **User sees study content** immediately upon unlock

## 🏗️ Architecture

### **Backend Components:**

#### **1. Enhanced Live Activity Service** (`app/services/live_activity_enhanced.py`)
- **Content Selection**: Randomly selects cards from user's preferred folders
- **Unlock Detection**: Handles webhook calls from iOS app
- **APNs Integration**: Sends Live Activity updates via Apple Push Notification Service
- **Rate Limiting**: Prevents spam updates (minimum 5 minutes between updates)

#### **2. API Endpoints** (`app/api/live_activity_enhanced.py`)
- `POST /api/live-activity/start` - Start Live Activity with initial content
- `POST /api/live-activity/unlock-update` - Update content on phone unlock
- `POST /api/live-activity/end` - End Live Activity
- `GET /api/live-activity/status` - Get current status
- `POST /webhook/phone-unlock` - Webhook for iOS unlock events

### **iOS Components:**

#### **1. Live Activity Manager** (`LiveActivityManager.swift`)
- **Unlock Detection**: Monitors `UIApplication.didBecomeActiveNotification`
- **Activity Management**: Starts, updates, and ends Live Activities
- **Backend Communication**: Calls API endpoints for content updates
- **Token Management**: Handles Live Activity push tokens

#### **2. Live Activity Widget** (`StudyLiveActivityWidget.swift`)
- **Lock Screen View**: Rich display with study content
- **Dynamic Island**: Compact view for iPhone 14 Pro+
- **Interactive Elements**: Tap to reveal answers for flashcards
- **Visual Design**: Clean, educational interface

## 📱 Implementation Details

### **Phone Unlock Detection:**
```swift
// iOS automatically calls this when app becomes active (phone unlock)
NotificationCenter.default.addObserver(
    forName: UIApplication.didBecomeActiveNotification,
    object: nil,
    queue: .main
) { [weak self] _ in
    Task {
        await self?.handlePhoneUnlock()
    }
}
```

### **Content Update Flow:**
```python
# Backend selects random study content
def _get_random_study_card(self, user: User) -> Optional[Card]:
    # Filter by user's selected folders
    # Prioritize due cards (70% chance)
    # Return random card for variety
```

### **Live Activity Payload:**
```python
# Structured content for iOS Live Activity
content_state = {
    "cardId": card.id,
    "cardType": "flashcard" | "information",
    "question": card.front,  # For flashcards
    "answer": card.back,     # For flashcards
    "information": card.front,  # For info pieces
    "subject": card.subject,
    "showAnswer": False,
    "isOverdue": card.is_due_for_review(),
    "folderName": card.folder.name,
    "lastUpdated": timestamp
}
```

## 🔧 Setup Instructions

### **1. Backend Setup:**

#### **Add to API Blueprint Registration:**
```python
# In app/api/__init__.py
from app.api import live_activity_enhanced
```

#### **Environment Variables:**
```bash
APNS_AUTH_KEY_ID=your_key_id
APNS_TEAM_ID=your_team_id
BUNDLE_ID=com.yourname.activerecall
```

#### **APNs Certificate:**
- Download `.p8` auth key from Apple Developer Account
- Place in project root or configure path in `Config`

### **2. iOS Setup:**

#### **Add Capabilities:**
- **Push Notifications**: For Live Activity updates
- **Background App Refresh**: For unlock detection
- **Live Activities**: Enable in project settings

#### **Info.plist Configuration:**
```xml
<key>NSSupportsLiveActivities</key>
<true/>
<key>NSSupportsLiveActivitiesFrequentUpdates</key>
<true/>
```

#### **Widget Extension:**
- Create new Widget Extension target
- Add `StudyLiveActivityWidget.swift` to extension
- Configure bundle identifier: `com.yourname.activerecall.widgets`

### **3. User Settings Integration:**

#### **Settings View Addition:**
```swift
Toggle("Live Activities on Unlock", isOn: $liveActivityEnabled)
    .onChange(of: liveActivityEnabled) { enabled in
        UserDefaults.standard.set(enabled, forKey: "live_activity_enabled")
        if enabled {
            Task { await liveActivityManager.startLiveActivity() }
        } else {
            Task { await liveActivityManager.endLiveActivity() }
        }
    }
```

## 🎨 Visual Design

### **Lock Screen Layout:**
```
┌─────────────────────────────────────┐
│ 🧠 Active Recall    Updated 2m ago  │
│ Study Session Active                │
├─────────────────────────────────────┤
│ Question:                           │
│ What is the capital of France?      │
├─────────────────────────────────────┤
│ 👁️ Tap to reveal answer             │
├─────────────────────────────────────┤
│ 📁 Geography        Tap to open app │
└─────────────────────────────────────┘
```

### **Information Piece Layout:**
```
┌─────────────────────────────────────┐
│ 🧠 Active Recall    Updated 1m ago  │
│ Study Session Active                │
├─────────────────────────────────────┤
│ 💡 Key Information                  │
│ The speed of light is 299,792,458   │
│ meters per second in a vacuum.      │
├─────────────────────────────────────┤
│ 📁 Physics          Tap to open app │
└─────────────────────────────────────┘
```

## 🔄 Content Selection Logic

### **Smart Card Selection:**
1. **Folder Filtering**: Only cards from user's selected notification folders
2. **Due Card Priority**: 70% chance to show overdue cards
3. **Variety**: 30% chance to show any card for exposure
4. **Rate Limiting**: Minimum 5 minutes between content updates
5. **Randomization**: Prevents predictable patterns

### **Content Types:**
- **Flashcards**: Show question first, reveal answer on tap
- **Information Pieces**: Show complete information immediately
- **Subject Context**: Display subject and folder information
- **Overdue Indicators**: Visual cues for cards needing review

## 📊 Analytics & Monitoring

### **Tracking Metrics:**
- Live Activity start/end events
- Unlock-triggered content updates
- User engagement with revealed answers
- Content type preferences
- Folder-based performance

### **Backend Logging:**
```python
print(f"Phone unlock detected for user {user_id}")
print(f"Live Activity updated with card {card_id}")
print(f"Content type: {card.content_type}")
```

## 🚀 Benefits

### **For Users:**
- **Effortless Learning**: No need to open app or remember to study
- **Micro-Moments**: Utilizes natural phone unlock behavior
- **Contextual Content**: Shows relevant study material
- **Visual Appeal**: Clean, educational interface

### **For Learning:**
- **Spaced Repetition**: Natural distribution throughout the day
- **Active Recall**: Forces memory retrieval on unlock
- **Variety**: Prevents monotony with random content selection
- **Overdue Priority**: Ensures important reviews aren't missed

## 🔮 Future Enhancements

### **Potential Improvements:**
1. **Smart Timing**: Learn user's unlock patterns for optimal content
2. **Context Awareness**: Different content based on time/location
3. **Streak Tracking**: Gamify consecutive unlock learning
4. **Performance Analytics**: Track learning effectiveness
5. **Social Features**: Share interesting facts with friends

## 🎯 Perfect Alignment with Active Recall

This implementation perfectly embodies the app's core value proposition:

> **"Effortless learning through interruption"**

- ✅ **Effortless**: No user action required beyond unlocking phone
- ✅ **Learning**: Displays actual study content for active recall
- ✅ **Interruption**: Naturally interrupts phone unlock routine
- ✅ **Dead Time**: Utilizes the moment between unlock and app usage

The Live Activity unlock feature transforms every phone unlock into a potential learning moment, making Active Recall truly seamless and effective! 🧠✨