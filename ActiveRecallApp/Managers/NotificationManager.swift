import Foundation
import UserNotifications
import UIKit

class NotificationManager: NSObject, ObservableObject {
    @Published var isAuthorized = false
    
    override init() {
        super.init()
        UNUserNotificationCenter.current().delegate = self
    }
    
    func requestPermissions() {
        UNUserNotificationCenter.current().requestAuthorization(options: [.alert, .sound, .badge]) { granted, error in
            DispatchQueue.main.async {
                self.isAuthorized = granted
            }
            
            if granted {
                DispatchQueue.main.async {
                    UIApplication.shared.registerForRemoteNotifications()
                }
            }
        }
    }
    
    func setupNotificationCategories() {
        // Define actions for flashcard review
        let easyAction = UNNotificationAction(
            identifier: "EASY_ACTION",
            title: "Easy (5)",
            options: []
        )
        
        let goodAction = UNNotificationAction(
            identifier: "GOOD_ACTION",
            title: "Good (4)",
            options: []
        )
        
        let hardAction = UNNotificationAction(
            identifier: "HARD_ACTION",
            title: "Hard (2)",
            options: []
        )
        
        let againAction = UNNotificationAction(
            identifier: "AGAIN_ACTION",
            title: "Again (1)",
            options: []
        )
        
        // Flashcard category
        let flashcardCategory = UNNotificationCategory(
            identifier: "FLASHCARD_CATEGORY",
            actions: [easyAction, goodAction, hardAction, againAction],
            intentIdentifiers: [],
            options: [.customDismissAction]
        )
        
        // Information piece category (just acknowledgment)
        let acknowledgeAction = UNNotificationAction(
            identifier: "ACKNOWLEDGE_ACTION",
            title: "Got it",
            options: []
        )
        
        let informationCategory = UNNotificationCategory(
            identifier: "INFORMATION_CATEGORY",
            actions: [acknowledgeAction],
            intentIdentifiers: [],
            options: [.customDismissAction]
        )
        
        UNUserNotificationCenter.current().setNotificationCategories([
            flashcardCategory,
            informationCategory
        ])
    }
    
    // Schedule local notification for testing
    func scheduleTestNotification(card: Card) {
        let content = UNMutableNotificationContent()
        content.title = "Active Recall"
        content.body = card.front
        content.sound = .default
        
        // Add card info to userInfo for handling responses
        content.userInfo = [
            "card_id": card.id,
            "content_type": card.contentType
        ]
        
        // Set category based on content type
        content.categoryIdentifier = card.contentType == "flashcard" ? "FLASHCARD_CATEGORY" : "INFORMATION_CATEGORY"
        
        // Schedule for 5 seconds from now (for testing)
        let trigger = UNTimeIntervalNotificationTrigger(timeInterval: 5, repeats: false)
        
        let request = UNNotificationRequest(
            identifier: "test_\(card.id)",
            content: content,
            trigger: trigger
        )
        
        UNUserNotificationCenter.current().add(request) { error in
            if let error = error {
                print("Error scheduling notification: \(error)")
            } else {
                print("Test notification scheduled for card: \(card.front)")
            }
        }
    }
}

// MARK: - UNUserNotificationCenterDelegate

extension NotificationManager: UNUserNotificationCenterDelegate {
    
    // Handle notification when app is in foreground
    func userNotificationCenter(
        _ center: UNUserNotificationCenter,
        willPresent notification: UNNotification,
        withCompletionHandler completionHandler: @escaping (UNNotificationPresentationOptions) -> Void
    ) {
        // Show notification even when app is in foreground
        completionHandler([.banner, .sound])
    }
    
    // Handle notification response (button taps)
    func userNotificationCenter(
        _ center: UNUserNotificationCenter,
        didReceive response: UNNotificationResponse,
        withCompletionHandler completionHandler: @escaping () -> Void
    ) {
        
        let userInfo = response.notification.request.content.userInfo
        guard let cardId = userInfo["card_id"] as? Int,
              let _ = userInfo["content_type"] as? String else {
            completionHandler()
            return
        }
        
        let actionIdentifier = response.actionIdentifier
        
        // Handle different actions
        Task {
            do {
                switch actionIdentifier {
                case "EASY_ACTION":
                    try await APIManager.shared.reviewCard(cardId: cardId, quality: 5)
                    print("Card \(cardId) marked as Easy")
                    
                case "GOOD_ACTION":
                    try await APIManager.shared.reviewCard(cardId: cardId, quality: 4)
                    print("Card \(cardId) marked as Good")
                    
                case "HARD_ACTION":
                    try await APIManager.shared.reviewCard(cardId: cardId, quality: 2)
                    print("Card \(cardId) marked as Hard")
                    
                case "AGAIN_ACTION":
                    try await APIManager.shared.reviewCard(cardId: cardId, quality: 1)
                    print("Card \(cardId) marked as Again")
                    
                case "ACKNOWLEDGE_ACTION":
                    try await APIManager.shared.reviewCard(cardId: cardId, quality: 4)
                    print("Information piece \(cardId) acknowledged")
                    
                case UNNotificationDefaultActionIdentifier:
                    // User tapped the notification itself
                    print("User tapped notification for card \(cardId)")
                    
                case UNNotificationDismissActionIdentifier:
                    // User dismissed the notification
                    print("User dismissed notification for card \(cardId)")
                    
                default:
                    break
                }
            } catch {
                print("Error handling notification response: \(error)")
            }
        }
        
        completionHandler()
    }
}