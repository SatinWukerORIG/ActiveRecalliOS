import Foundation
import SwiftUI

// MARK: - Core Data Models
// This file contains all the essential types needed for the Active Recall app

struct User: Codable, Identifiable {
    let id: Int
    let username: String
    let email: String?
    let deviceToken: String?
    let activeActivityToken: String?
    let focusMode: Bool
    let notificationFrequency: Int
    let createdAt: String
    
    enum CodingKeys: String, CodingKey {
        case id, username, email
        case deviceToken = "device_token"
        case activeActivityToken = "active_activity_token"
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
        case id
        case contentType = "content_type"
        case front, back, subject, tags
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

struct UserAvailability: Codable {
    let available: Bool
    let reasons: [String]
    let nextDueCard: Int?
    
    enum CodingKeys: String, CodingKey {
        case available, reasons
        case nextDueCard = "next_due_card"
    }
}

struct ContentGenerationResult: Codable {
    let message: String
    let generationId: Int
    let cardsGenerated: Int
    let cards: [GeneratedCard]
    
    enum CodingKeys: String, CodingKey {
        case message
        case generationId = "generation_id"
        case cardsGenerated = "cards_generated"
        case cards
    }
}

struct GeneratedCard: Codable {
    let contentType: String
    let front: String
    let back: String?
    
    enum CodingKeys: String, CodingKey {
        case contentType = "content_type"
        case front, back
    }
}

// MARK: - App State Management

class AppState: ObservableObject {
    @Published var currentUser: User?
    @Published var isLoading = false
    @Published var errorMessage: String?
    
    init() {
        initializeUser()
    }
    
    func initializeUser() {
        isLoading = true
        errorMessage = nil
        
        Task {
            do {
                let user = try await getOrCreateUser()
                await MainActor.run {
                    self.currentUser = user
                    self.isLoading = false
                }
            } catch {
                await MainActor.run {
                    self.errorMessage = "Failed to initialize user: \(error.localizedDescription)"
                    self.isLoading = false
                }
            }
        }
    }
    
    private func getOrCreateUser() async throws -> User {
        let storedUserId = UserDefaults.standard.integer(forKey: "user_id")
        
        if storedUserId > 0 {
            if let existingUser = try await APIManager.shared.getUser(id: storedUserId) {
                return existingUser
            }
        }
        
        let newUser = try await APIManager.shared.createUser(
            username: "User\(Int.random(in: 1000...9999))",
            email: "user@example.com"
        )
        
        UserDefaults.standard.set(newUser.id, forKey: "user_id")
        return newUser
    }
}

// MARK: - Study Session Manager

class StudySessionManager: ObservableObject {
    func startStudySession(question: String) {
        print("Starting study session with question: \(question)")
    }
}