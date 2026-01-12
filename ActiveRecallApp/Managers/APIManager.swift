import Foundation

class APIManager: ObservableObject {
    static let shared = APIManager()
    
    // Update this to your Flask server URL
    // For local development: "http://127.0.0.1:5001" (new port management system)
    // For testing on device: use your computer's IP address with port 5001
    private let baseURL = "http://127.0.0.1:5001"
    
    private init() {}
    
    // MARK: - User Management
    
    func createUser(username: String, email: String) async throws -> User {
        let url = URL(string: "\(baseURL)/users")!
        
        let userData = [
            "username": username,
            "email": email,
            "notification_frequency": 30
        ] as [String: Any]
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = try JSONSerialization.data(withJSONObject: userData)
        
        let (data, response) = try await URLSession.shared.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse,
              httpResponse.statusCode == 201 else {
            throw APIError.invalidResponse
        }
        
        let result = try JSONSerialization.jsonObject(with: data) as! [String: Any]
        let userId = result["user_id"] as! Int
        
        // Get the created user
        return try await getUser(id: userId)!
    }
    
    func getUser(id: Int) async throws -> User? {
        let url = URL(string: "\(baseURL)/users/\(id)")!
        
        do {
            let (data, response) = try await URLSession.shared.data(from: url)
            
            guard let httpResponse = response as? HTTPURLResponse else {
                throw APIError.invalidResponse
            }
            
            if httpResponse.statusCode == 404 {
                return nil
            }
            
            guard httpResponse.statusCode == 200 else {
                throw APIError.invalidResponse
            }
            
            return try JSONDecoder().decode(User.self, from: data)
        } catch {
            if error is DecodingError {
                throw APIError.decodingError
            }
            throw error
        }
    }
    
    func getUserStats(userId: Int) async throws -> UserStats {
        let url = URL(string: "\(baseURL)/users/\(userId)/stats")!
        
        do {
            let (data, response) = try await URLSession.shared.data(from: url)
            
            guard let httpResponse = response as? HTTPURLResponse,
                  httpResponse.statusCode == 200 else {
                throw APIError.invalidResponse
            }
            
            return try JSONDecoder().decode(UserStats.self, from: data)
        } catch {
            if error is DecodingError {
                throw APIError.decodingError
            }
            throw error
        }
    }
    
    func reviewCard(cardId: Int, quality: Int) async throws {
        let url = URL(string: "\(baseURL)/cards/\(cardId)/review")!
        
        let reviewData = ["quality": quality]
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = try JSONSerialization.data(withJSONObject: reviewData)
        
        let (_, response) = try await URLSession.shared.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse,
              httpResponse.statusCode == 200 else {
            throw APIError.invalidResponse
        }
    }
    
    func addCard(userId: Int, contentType: String, front: String, back: String?, subject: String?, tags: [String]) async throws -> Int {
        let url = URL(string: "\(baseURL)/cards")!
        
        var cardData: [String: Any] = [
            "user_id": userId,
            "content_type": contentType,
            "front": front,
            "tags": tags
        ]
        
        if let back = back {
            cardData["back"] = back
        }
        
        if let subject = subject {
            cardData["subject"] = subject
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = try JSONSerialization.data(withJSONObject: cardData)
        
        let (data, response) = try await URLSession.shared.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse,
              httpResponse.statusCode == 201 else {
            throw APIError.invalidResponse
        }
        
        let result = try JSONSerialization.jsonObject(with: data) as! [String: Any]
        return result["card_id"] as! Int
    }
    
    func getUserCards(userId: Int, subject: String? = nil) async throws -> [Card] {
        var urlString = "\(baseURL)/users/\(userId)/cards"
        if let subject = subject, !subject.isEmpty {
            urlString += "?subject=\(subject.addingPercentEncoding(withAllowedCharacters: .urlQueryAllowed) ?? "")"
        }
        
        let url = URL(string: urlString)!
        
        let (data, response) = try await URLSession.shared.data(from: url)
        
        guard let httpResponse = response as? HTTPURLResponse,
              httpResponse.statusCode == 200 else {
            throw APIError.invalidResponse
        }
        
        return try JSONDecoder().decode([Card].self, from: data)
    }
    
    func getDueCards(userId: Int) async throws -> [Card] {
        let url = URL(string: "\(baseURL)/users/\(userId)/due-cards")!
        
        let (data, response) = try await URLSession.shared.data(from: url)
        
        guard let httpResponse = response as? HTTPURLResponse,
              httpResponse.statusCode == 200 else {
            throw APIError.invalidResponse
        }
        
        return try JSONDecoder().decode([Card].self, from: data)
    }
    
    func startStudySessionActivity() async throws -> String {
        let url = URL(string: "\(baseURL)/study-session/start")!
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let (data, response) = try await URLSession.shared.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse,
              httpResponse.statusCode == 201 else {
            throw APIError.invalidResponse
        }
        
        let result = try JSONSerialization.jsonObject(with: data) as! [String: Any]
        return result["session_id"] as! String
    }
    
    func updateStudyProgress(sessionId: String, currentCardIndex: Int, totalCards: Int) async throws {
        let url = URL(string: "\(baseURL)/study-session/\(sessionId)/progress")!
        
        let progressData = [
            "current_card_index": currentCardIndex,
            "total_cards": totalCards
        ]
        
        var request = URLRequest(url: url)
        request.httpMethod = "PUT"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = try JSONSerialization.data(withJSONObject: progressData)
        
        let (_, response) = try await URLSession.shared.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse,
              httpResponse.statusCode == 200 else {
            throw APIError.invalidResponse
        }
    }
    
    func endStudySessionActivity(sessionId: String, cardsReviewed: Int, sessionDuration: TimeInterval) async throws {
        let url = URL(string: "\(baseURL)/study-session/\(sessionId)/end")!
        
        let endData = [
            "cards_reviewed": cardsReviewed,
            "session_duration": sessionDuration
        ] as [String: Any]
        
        var request = URLRequest(url: url)
        request.httpMethod = "PUT"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = try JSONSerialization.data(withJSONObject: endData)
        
        let (_, response) = try await URLSession.shared.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse,
              httpResponse.statusCode == 200 else {
            throw APIError.invalidResponse
        }
    }
    
    // Additional API methods would be here...
    // (Simplified for brevity)
}

// MARK: - Error Handling

enum APIError: Error, LocalizedError {
    case invalidResponse
    case decodingError
    case networkError
    case serviceUnavailable
    
    var errorDescription: String? {
        switch self {
        case .invalidResponse:
            return "Invalid response from server"
        case .decodingError:
            return "Failed to decode response"
        case .networkError:
            return "Network connection error"
        case .serviceUnavailable:
            return "AI content generation service is not available. Please check server configuration."
        }
    }
}