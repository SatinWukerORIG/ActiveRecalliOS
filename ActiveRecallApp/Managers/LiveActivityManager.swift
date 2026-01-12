import SwiftUI
import ActivityKit
import Foundation
import UIKit

// MARK: - Live Activity Attributes
struct StudyActivityAttributes: ActivityAttributes {
    public struct ContentState: Codable, Hashable {
        let cardId: Int
        let cardType: String
        let question: String?
        let answer: String?
        let information: String?
        let subject: String
        let showAnswer: Bool
        let isOverdue: Bool
        let folderName: String?
        let lastUpdated: TimeInterval
    }
    
    let userId: Int
    let startTime: Date
}

// MARK: - Live Activity Manager
@MainActor
class LiveActivityManager: ObservableObject {
    @Published var currentActivity: Activity<StudyActivityAttributes>?
    @Published var isActivityActive = false
    
    private let apiManager = APIManager.shared
    private var unlockObserver: NSObjectProtocol?
    
    init() {
        setupUnlockDetection()
        checkExistingActivity()
    }
    
    deinit {
        if let observer = unlockObserver {
            NotificationCenter.default.removeObserver(observer)
        }
    }
    
    // MARK: - Phone Unlock Detection
    private func setupUnlockDetection() {
        // Listen for app becoming active (phone unlock)
        unlockObserver = NotificationCenter.default.addObserver(
            forName: UIApplication.didBecomeActiveNotification,
            object: nil,
            queue: .main
        ) { [weak self] _ in
            Task {
                await self?.handlePhoneUnlock()
            }
        }
    }
    
    private func handlePhoneUnlock() async {
        print("📱 Phone unlock detected")
        
        // Only update if we have an active Live Activity
        guard currentActivity != nil else {
            print("No active Live Activity to update")
            return
        }
        
        // Call backend to get new study content
        await requestContentUpdate()
    }
    
    // MARK: - Live Activity Management
    func startLiveActivity() async {
        guard ActivityAuthorizationInfo().areActivitiesEnabled else {
            print("❌ Live Activities not enabled")
            return
        }
        
        do {
            // Create initial content state
            let initialState = StudyActivityAttributes.ContentState(
                cardId: 0,
                cardType: "information",
                question: nil,
                answer: nil,
                information: "Loading study content...",
                subject: "Active Recall",
                showAnswer: false,
                isOverdue: false,
                folderName: nil,
                lastUpdated: Date().timeIntervalSince1970
            )
            
            let attributes = StudyActivityAttributes(
                userId: UserDefaults.standard.integer(forKey: "user_id"),
                startTime: Date()
            )
            
            let activityContent = ActivityContent(
                state: initialState,
                staleDate: Calendar.current.date(byAdding: .hour, value: 2, to: Date())
            )
            
            // Start the Live Activity
            currentActivity = try Activity.request(
                attributes: attributes,
                content: activityContent,
                pushType: .token
            )
            
            isActivityActive = true
            print("✅ Live Activity started successfully")
            
            // Register for push token updates
            if let activity = currentActivity {
                observeActivityUpdates(activity)
            }
            
        } catch {
            print("❌ Failed to start Live Activity: \(error)")
        }
    }
    
    func endLiveActivity() async {
        guard let activity = currentActivity else { return }
        
        // End the local activity
        await activity.end(
            ActivityContent(
                state: activity.content.state,
                staleDate: Date()
            ),
            dismissalPolicy: .immediate
        )
        
        currentActivity = nil
        isActivityActive = false
        print("✅ Live Activity ended")
    }
    
    private func requestContentUpdate() async {
        // Simplified implementation for now
        print("Requesting content update...")
    }
    
    private func checkExistingActivity() {
        // Check if there's already an active Live Activity
        for activity in Activity<StudyActivityAttributes>.activities {
            if activity.activityState == .active {
                currentActivity = activity
                isActivityActive = true
                observeActivityUpdates(activity)
                break
            }
        }
    }
    
    private func observeActivityUpdates(_ activity: Activity<StudyActivityAttributes>) {
        Task {
            for await activityState in activity.activityStateUpdates {
                if activityState == .dismissed || activityState == .ended {
                    currentActivity = nil
                    isActivityActive = false
                    break
                }
            }
        }
        
        // Observe push token updates
        Task {
            for await pushToken in activity.pushTokenUpdates {
                let tokenString = pushToken.map { String(format: "%02x", $0) }.joined()
                print("📱 Live Activity push token: \(tokenString)")
            }
        }
    }
}