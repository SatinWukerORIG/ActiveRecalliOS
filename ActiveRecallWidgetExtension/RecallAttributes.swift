import Foundation
import ActivityKit

struct RecallAttributes: ActivityAttributes {
    public struct ContentState: Codable, Hashable {
        let question: String
        let progress: Double
        let cardsReviewed: Int
        let totalCards: Int
        let sessionStartTime: Date
    }
    
    let sessionId: String
    let userId: Int
}