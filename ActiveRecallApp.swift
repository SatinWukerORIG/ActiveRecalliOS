import SwiftUI
import UserNotifications

@main
struct ActiveRecallApp: App {
    @StateObject private var appState = AppState()
    @StateObject private var notificationManager = NotificationManager()
    @StateObject private var liveActivityManager = LiveActivityManager()
    
    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(appState)
                .environmentObject(notificationManager)
                .environmentObject(liveActivityManager)
                .onAppear {
                    setupApp()
                }
        }
    }
    
    private func setupApp() {
        // Request notification permissions
        notificationManager.requestPermissions()
        
        // Setup notification categories and actions
        notificationManager.setupNotificationCategories()
        
        // Initialize user session
        appState.initializeUser()
        
        // Setup Live Activity if enabled
        Task {
            if UserDefaults.standard.bool(forKey: "live_activity_enabled") {
                await liveActivityManager.startLiveActivity()
            }
        }
    }
}

// MARK: - App State Management
class AppState: ObservableObject {
    @Published var currentUser: User?
    @Published var isLoading = false
    @Published var errorMessage: String?
    
    private let apiManager = APIManager.shared
    
    func initializeUser() {
        // For demo purposes, create or get user with ID 1
        Task {
            await createOrGetUser()
        }
    }
    
    @MainActor
    private func createOrGetUser() async {
        isLoading = true
        
        do {
            // Try to get existing user first
            if let user = try await apiManager.getUser(id: 1) {
                currentUser = user
            } else {
                // Create new user
                let newUser = try await apiManager.createUser(
                    username: "ios_user",
                    email: "user@activerecall.com"
                )
                currentUser = newUser
            }
        } catch {
            errorMessage = "Failed to initialize user: \(error.localizedDescription)"
        }
        
        isLoading = false
    }
}

// MARK: - Data Models
struct User: Codable, Identifiable {
    let id: Int
    let username: String
    let email: String?
    let focusMode: Bool
    let notificationFrequency: Int
    let createdAt: String
    
    enum CodingKeys: String, CodingKey {
        case id, username, email
        case focusMode = "focus_mode"
        case notificationFrequency = "notification_frequency"
        case createdAt = "created_at"
    }
}

struct Card: Codable, Identifiable {
    let id: Int
    let contentType: String
    let front: String
    let back: String?
    let subject: String?
    let tags: [String]
    let nextReview: String
    let isAiGenerated: Bool
    
    enum CodingKeys: String, CodingKey {
        case id, front, back, subject, tags
        case contentType = "content_type"
        case nextReview = "next_review"
        case isAiGenerated = "is_ai_generated"
    }
}

struct UserStats: Codable {
    let totalCards: Int
    let dueCards: Int
    let subjects: [String: Int]
    
    enum CodingKeys: String, CodingKey {
        case totalCards = "total_cards"
        case dueCards = "due_cards"
        case subjects
    }
}