import SwiftUI
import Foundation

struct StudyView: View {
    @EnvironmentObject var appState: AppState
    @EnvironmentObject var notificationManager: NotificationManager
    @State private var dueCards: [Card] = []
    @State private var currentCardIndex = 0
    @State private var isLoading = false
    @State private var showingAnswer = false
    @State private var studySessionActive = false
    @State private var sessionId: String?
    @State private var sessionStartTime = Date()
    @State private var cardsReviewed = 0
    
    var currentCard: Card? {
        guard currentCardIndex < dueCards.count else { return nil }
        return dueCards[currentCardIndex]
    }
    
    var body: some View {
        NavigationView {
            VStack {
                if isLoading {
                    ProgressView("Loading cards...")
                        .frame(maxWidth: .infinity, maxHeight: .infinity)
                } else if dueCards.isEmpty {
                    EmptyStudyView()
                } else if let card = currentCard {
                    StudyCardView(
                        card: card,
                        showingAnswer: $showingAnswer,
                        onReview: { quality in
                            reviewCard(quality: quality)
                        },
                        onShowAnswer: {
                            showingAnswer = true
                        }
                    )
                } else {
                    StudyCompleteView {
                        loadDueCards()
                    }
                }
            }
            .navigationTitle("Study Session")
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    if !dueCards.isEmpty {
                        Text("\(currentCardIndex + 1) / \(dueCards.count)")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                }
            }
            .onAppear {
                loadDueCards()
            }
            .onDisappear {
                endStudySession()
            }
        }
    }
    
    private func loadDueCards() {
        guard let user = appState.currentUser else { return }
        
        isLoading = true
        Task {
            do {
                let cards = try await APIManager.shared.getDueCards(userId: user.id)
                await MainActor.run {
                    self.dueCards = cards
                    self.currentCardIndex = 0
                    self.showingAnswer = false
                    self.isLoading = false
                    
                    // Start Live Activity session if cards are available
                    if !cards.isEmpty {
                        startStudySession()
                    }
                }
            } catch {
                await MainActor.run {
                    self.isLoading = false
                    appState.errorMessage = "Failed to load due cards: \(error.localizedDescription)"
                }
            }
        }
    }
    
    private func startStudySession() {
        guard !studySessionActive else { return }
        
        Task {
            do {
                let sessionId = try await APIManager.shared.startStudySessionActivity()
                await MainActor.run {
                    self.sessionId = sessionId
                    self.studySessionActive = true
                    self.sessionStartTime = Date()
                    self.cardsReviewed = 0
                }
            } catch {
                print("Failed to start Live Activity session: \(error)")
            }
        }
    }
    
    private func updateLiveActivityProgress() {
        guard let sessionId = sessionId, studySessionActive else { return }
        
        Task {
            do {
                try await APIManager.shared.updateStudyProgress(
                    sessionId: sessionId,
                    currentCardIndex: currentCardIndex,
                    totalCards: dueCards.count
                )
            } catch {
                print("Failed to update Live Activity progress: \(error)")
            }
        }
    }
    
    private func endStudySession() {
        guard let sessionId = sessionId, studySessionActive else { return }
        
        let sessionDuration = Date().timeIntervalSince(sessionStartTime)
        
        Task {
            do {
                try await APIManager.shared.endStudySessionActivity(
                    sessionId: sessionId,
                    cardsReviewed: cardsReviewed,
                    sessionDuration: sessionDuration
                )
            } catch {
                print("Failed to end Live Activity session: \(error)")
            }
        }
        
        studySessionActive = false
        self.sessionId = nil
    }
    
    private func reviewCard(quality: Int) {
        guard let card = currentCard else { return }
        
        Task {
            do {
                try await APIManager.shared.reviewCard(cardId: card.id, quality: quality)
                
                await MainActor.run {
                    cardsReviewed += 1
                    
                    // Move to next card
                    if currentCardIndex < dueCards.count - 1 {
                        currentCardIndex += 1
                        showingAnswer = false
                        updateLiveActivityProgress()
                    } else {
                        // Study session complete
                        endStudySession()
                        dueCards.removeAll()
                    }
                }
            } catch {
                await MainActor.run {
                    appState.errorMessage = "Failed to review card: \(error.localizedDescription)"
                }
            }
        }
    }
}

// Additional view components would be here...
// (StudyCardView, ReviewButtonsView, EmptyStudyView, StudyCompleteView)

// MARK: - Supporting Views

struct EmptyStudyView: View {
    var body: some View {
        VStack(spacing: 20) {
            Image(systemName: "checkmark.circle")
                .font(.system(size: 60))
                .foregroundColor(.green)
            
            Text("All caught up!")
                .font(.title2)
                .fontWeight(.bold)
            
            Text("No cards are due for review right now. Great job staying on top of your studies!")
                .multilineTextAlignment(.center)
                .foregroundColor(.secondary)
                .padding(.horizontal)
            
            NavigationLink(destination: AddCardView()) {
                Text("Add New Cards")
                    .fontWeight(.medium)
                    .foregroundColor(.white)
                    .padding()
                    .background(Color.blue)
                    .cornerRadius(10)
            }
        }
        .padding()
    }
}

struct StudyCardView: View {
    let card: Card
    @Binding var showingAnswer: Bool
    let onReview: (Int) -> Void
    let onShowAnswer: () -> Void
    
    var body: some View {
        VStack(spacing: 20) {
            // Card content
            VStack(spacing: 15) {
                if let subject = card.subject {
                    Text(subject)
                        .font(.caption)
                        .foregroundColor(.secondary)
                        .padding(.horizontal, 12)
                        .padding(.vertical, 4)
                        .background(Color(.systemGray5))
                        .cornerRadius(8)
                }
                
                Text(card.front)
                    .font(.title2)
                    .multilineTextAlignment(.center)
                    .padding()
                
                if showingAnswer {
                    Divider()
                    
                    if let back = card.back {
                        Text(back)
                            .font(.body)
                            .multilineTextAlignment(.center)
                            .foregroundColor(.secondary)
                            .padding()
                    }
                }
            }
            .frame(maxWidth: .infinity, minHeight: 200)
            .background(Color(.systemBackground))
            .cornerRadius(12)
            .shadow(radius: 2)
            .padding()
            
            Spacer()
            
            // Action buttons
            if showingAnswer {
                ReviewButtonsView(onReview: onReview)
            } else {
                Button(action: onShowAnswer) {
                    Text("Show Answer")
                        .fontWeight(.medium)
                        .foregroundColor(.white)
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(Color.blue)
                        .cornerRadius(10)
                }
                .padding(.horizontal)
            }
        }
    }
}

struct ReviewButtonsView: View {
    let onReview: (Int) -> Void
    
    var body: some View {
        VStack(spacing: 12) {
            Text("How well did you know this?")
                .font(.headline)
                .multilineTextAlignment(.center)
            
            HStack(spacing: 12) {
                ReviewButton(title: "Again", subtitle: "< 1m", color: .red, quality: 1, onReview: onReview)
                ReviewButton(title: "Hard", subtitle: "< 6m", color: .orange, quality: 2, onReview: onReview)
                ReviewButton(title: "Good", subtitle: "< 10m", color: .blue, quality: 4, onReview: onReview)
                ReviewButton(title: "Easy", subtitle: "4d", color: .green, quality: 5, onReview: onReview)
            }
        }
        .padding()
    }
}

struct ReviewButton: View {
    let title: String
    let subtitle: String
    let color: Color
    let quality: Int
    let onReview: (Int) -> Void
    
    var body: some View {
        Button(action: { onReview(quality) }) {
            VStack(spacing: 4) {
                Text(title)
                    .fontWeight(.medium)
                    .foregroundColor(.white)
                
                Text(subtitle)
                    .font(.caption)
                    .foregroundColor(.white.opacity(0.8))
            }
            .frame(maxWidth: .infinity)
            .padding(.vertical, 12)
            .background(color)
            .cornerRadius(8)
        }
    }
}

struct StudyCompleteView: View {
    let onRestart: () -> Void
    
    var body: some View {
        VStack(spacing: 20) {
            Image(systemName: "star.circle.fill")
                .font(.system(size: 60))
                .foregroundColor(.yellow)
            
            Text("Session Complete!")
                .font(.title2)
                .fontWeight(.bold)
            
            Text("Great job! You've reviewed all your due cards.")
                .multilineTextAlignment(.center)
                .foregroundColor(.secondary)
                .padding(.horizontal)
            
            Button(action: onRestart) {
                Text("Check for More Cards")
                    .fontWeight(.medium)
                    .foregroundColor(.white)
                    .padding()
                    .background(Color.blue)
                    .cornerRadius(10)
            }
        }
        .padding()
    }
}

#Preview {
    StudyView()
        .environmentObject(AppState())
        .environmentObject(NotificationManager())
}