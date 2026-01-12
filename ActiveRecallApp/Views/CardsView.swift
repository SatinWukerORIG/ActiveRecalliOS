import SwiftUI
import Foundation

struct CardsView: View {
    @EnvironmentObject var appState: AppState
    @State private var cards: [Card] = []
    @State private var isLoading = false
    @State private var selectedSubject: String?
    @State private var selectedContentType: String?
    @State private var subjects: [String] = []
    
    private let contentTypes = ["All", "flashcard", "information"]
    
    var body: some View {
        NavigationView {
            VStack {
                // Filters
                ScrollView(.horizontal, showsIndicators: false) {
                    HStack(spacing: 10) {
                        // Content Type Filter
                        ForEach(contentTypes, id: \.self) { type in
                            FilterChip(
                                title: type.capitalized,
                                isSelected: selectedContentType == type || (type == "All" && selectedContentType == nil),
                                action: {
                                    selectedContentType = type == "All" ? nil : type
                                    loadCards()
                                }
                            )
                        }
                        
                        // Subject Filters
                        ForEach(subjects, id: \.self) { subject in
                            FilterChip(
                                title: subject,
                                isSelected: selectedSubject == subject,
                                action: {
                                    selectedSubject = selectedSubject == subject ? nil : subject
                                    loadCards()
                                }
                            )
                        }
                    }
                    .padding(.horizontal)
                }
                .padding(.vertical, 8)
                
                // Cards List
                if isLoading {
                    ProgressView("Loading cards...")
                        .frame(maxWidth: .infinity, maxHeight: .infinity)
                } else if cards.isEmpty {
                    EmptyStateView()
                } else {
                    List(cards) { card in
                        CardRowView(card: card)
                    }
                }
            }
            .navigationTitle("My Cards")
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    NavigationLink(destination: AddCardView()) {
                        Image(systemName: "plus")
                    }
                }
            }
            .onAppear {
                loadCards()
                loadSubjects()
            }
            .refreshable {
                loadCards()
                loadSubjects()
            }
        }
    }
    
    private func loadCards() {
        guard let user = appState.currentUser else { return }
        
        isLoading = true
        Task {
            do {
                let userCards = try await APIManager.shared.getUserCards(
                    userId: user.id,
                    subject: selectedSubject
                )
                
                // Filter by content type on client side if needed
                let filteredCards = selectedContentType == nil ? userCards : userCards.filter { $0.contentType == selectedContentType }
                
                await MainActor.run {
                    self.cards = filteredCards
                    self.isLoading = false
                }
            } catch {
                await MainActor.run {
                    self.isLoading = false
                    appState.errorMessage = "Failed to load cards: \(error.localizedDescription)"
                }
            }
        }
    }
    
    private func loadSubjects() {
        guard let user = appState.currentUser else { return }
        
        Task {
            do {
                let allCards = try await APIManager.shared.getUserCards(userId: user.id)
                let uniqueSubjects = Set(allCards.compactMap { $0.subject })
                await MainActor.run {
                    self.subjects = Array(uniqueSubjects).sorted()
                }
            } catch {
                print("Failed to load subjects: \(error)")
            }
        }
    }
}

// Additional view components would be here...
// (FilterChip, CardRowView, EmptyStateView)

// MARK: - Supporting Views

struct FilterChip: View {
    let title: String
    let isSelected: Bool
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            Text(title)
                .font(.caption)
                .fontWeight(.medium)
                .padding(.horizontal, 12)
                .padding(.vertical, 6)
                .background(isSelected ? Color.blue : Color(.systemGray5))
                .foregroundColor(isSelected ? .white : .primary)
                .cornerRadius(16)
        }
    }
}

struct CardRowView: View {
    let card: Card
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                VStack(alignment: .leading, spacing: 4) {
                    Text(card.front)
                        .font(.body)
                        .lineLimit(2)
                    
                    if let back = card.back, !back.isEmpty {
                        Text(back)
                            .font(.caption)
                            .foregroundColor(.secondary)
                            .lineLimit(1)
                    }
                }
                
                Spacer()
                
                VStack(alignment: .trailing, spacing: 4) {
                    Text(card.contentType.capitalized)
                        .font(.caption)
                        .padding(.horizontal, 8)
                        .padding(.vertical, 2)
                        .background(Color(.systemGray5))
                        .cornerRadius(4)
                    
                    if let subject = card.subject {
                        Text(subject)
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                }
            }
            
            if !card.tags.isEmpty {
                ScrollView(.horizontal, showsIndicators: false) {
                    HStack(spacing: 4) {
                        ForEach(card.tags, id: \.self) { tag in
                            Text("#\(tag)")
                                .font(.caption2)
                                .foregroundColor(.blue)
                                .padding(.horizontal, 6)
                                .padding(.vertical, 2)
                                .background(Color.blue.opacity(0.1))
                                .cornerRadius(4)
                        }
                    }
                }
            }
        }
        .padding(.vertical, 4)
    }
}

struct EmptyStateView: View {
    var body: some View {
        VStack(spacing: 20) {
            Image(systemName: "rectangle.stack")
                .font(.system(size: 60))
                .foregroundColor(.gray)
            
            Text("No Cards Yet")
                .font(.title2)
                .fontWeight(.bold)
            
            Text("Start building your knowledge base by adding your first flashcard or information piece.")
                .multilineTextAlignment(.center)
                .foregroundColor(.secondary)
                .padding(.horizontal)
            
            NavigationLink(destination: AddCardView()) {
                Text("Add Your First Card")
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
    CardsView()
        .environmentObject(AppState())
}