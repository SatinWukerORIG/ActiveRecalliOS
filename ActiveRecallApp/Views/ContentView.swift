import SwiftUI
import Foundation

struct ContentView: View {
    @EnvironmentObject var appState: AppState
    @EnvironmentObject var notificationManager: NotificationManager
    
    var body: some View {
        NavigationView {
            if appState.isLoading {
                ProgressView("Initializing...")
                    .frame(maxWidth: .infinity, maxHeight: .infinity)
            } else if let errorMessage = appState.errorMessage {
                ErrorView(message: errorMessage) {
                    appState.initializeUser()
                }
            } else if appState.currentUser != nil {
                MainTabView()
            } else {
                Text("Failed to load user")
                    .foregroundColor(.secondary)
            }
        }
    }
}

struct ErrorView: View {
    let message: String
    let retry: () -> Void
    
    var body: some View {
        VStack(spacing: 20) {
            Image(systemName: "exclamationmark.triangle")
                .font(.system(size: 50))
                .foregroundColor(.orange)
            
            Text("Error")
                .font(.title)
                .fontWeight(.bold)
            
            Text(message)
                .multilineTextAlignment(.center)
                .foregroundColor(.secondary)
            
            Button("Retry", action: retry)
                .buttonStyle(.borderedProminent)
        }
        .padding()
    }
}

struct MainTabView: View {
    var body: some View {
        TabView {
            DashboardView()
                .tabItem {
                    Image(systemName: "brain.head.profile")
                    Text("Dashboard")
                }
            
            CardsView()
                .tabItem {
                    Image(systemName: "rectangle.stack")
                    Text("Cards")
                }
            
            StudyView()
                .tabItem {
                    Image(systemName: "play.circle")
                    Text("Study")
                }
            
            AIGenerationView()
                .tabItem {
                    Image(systemName: "sparkles")
                    Text("AI Generate")
                }
            
            SettingsView()
                .tabItem {
                    Image(systemName: "gear")
                    Text("Settings")
                }
        }
    }
}

// MARK: - Dashboard View

struct DashboardView: View {
    @EnvironmentObject var appState: AppState
    @State private var stats: UserStats?
    @State private var isLoading = false
    
    var body: some View {
        NavigationView {
            ScrollView {
                VStack(spacing: 20) {
                    // Welcome Section
                    VStack(alignment: .leading, spacing: 10) {
                        HStack {
                            Image(systemName: "brain.head.profile")
                                .font(.title)
                                .foregroundColor(.blue)
                            
                            VStack(alignment: .leading) {
                                Text("Welcome back!")
                                    .font(.title2)
                                    .fontWeight(.bold)
                                
                                if let user = appState.currentUser {
                                    Text(user.username)
                                        .foregroundColor(.secondary)
                                }
                            }
                            
                            Spacer()
                        }
                    }
                    .padding()
                    .background(Color(.systemGray6))
                    .cornerRadius(12)
                    
                    // Stats Section
                    if let stats = stats {
                        StatsCardView(stats: stats)
                    } else if isLoading {
                        ProgressView("Loading stats...")
                            .frame(height: 100)
                    }
                    
                    // Quick Actions
                    QuickActionsView()
                    
                    Spacer()
                }
                .padding()
            }
            .navigationTitle("Active Recall")
            .onAppear {
                loadStats()
            }
            .refreshable {
                loadStats()
            }
        }
    }
    
    private func loadStats() {
        guard let user = appState.currentUser else { return }
        
        isLoading = true
        Task {
            do {
                let userStats = try await APIManager.shared.getUserStats(userId: user.id)
                await MainActor.run {
                    self.stats = userStats
                    self.isLoading = false
                }
            } catch {
                await MainActor.run {
                    self.isLoading = false
                    appState.errorMessage = "Failed to load stats: \(error.localizedDescription)"
                }
            }
        }
    }
}

struct StatsCardView: View {
    let stats: UserStats
    
    var body: some View {
        VStack(spacing: 15) {
            Text("Your Progress")
                .font(.headline)
                .frame(maxWidth: .infinity, alignment: .leading)
            
            HStack(spacing: 20) {
                StatItemView(
                    title: "Total Cards",
                    value: "\(stats.totalCards)",
                    icon: "rectangle.stack",
                    color: .blue
                )
                
                StatItemView(
                    title: "Due Today",
                    value: "\(stats.dueCards)",
                    icon: "clock",
                    color: stats.dueCards > 0 ? .orange : .green
                )
            }
            
            if !stats.subjects.isEmpty {
                VStack(alignment: .leading, spacing: 8) {
                    Text("Subjects")
                        .font(.subheadline)
                        .fontWeight(.medium)
                    
                    ForEach(Array(stats.subjects.keys.sorted()), id: \.self) { subject in
                        HStack {
                            Text(subject)
                            Spacer()
                            Text("\(stats.subjects[subject] ?? 0)")
                                .foregroundColor(.secondary)
                        }
                        .font(.caption)
                    }
                }
            }
        }
        .padding()
        .background(Color(.systemGray6))
        .cornerRadius(12)
    }
}

struct StatItemView: View {
    let title: String
    let value: String
    let icon: String
    let color: Color
    
    var body: some View {
        VStack(spacing: 8) {
            Image(systemName: icon)
                .font(.title2)
                .foregroundColor(color)
            
            Text(value)
                .font(.title2)
                .fontWeight(.bold)
            
            Text(title)
                .font(.caption)
                .foregroundColor(.secondary)
        }
        .frame(maxWidth: .infinity)
    }
}

struct QuickActionsView: View {
    @EnvironmentObject var notificationManager: NotificationManager
    
    var body: some View {
        VStack(spacing: 15) {
            Text("Quick Actions")
                .font(.headline)
                .frame(maxWidth: .infinity, alignment: .leading)
            
            VStack(spacing: 10) {
                HStack(spacing: 15) {
                    NavigationLink(destination: AddCardView()) {
                        QuickActionButton(
                            title: "Add Card",
                            icon: "plus.rectangle",
                            color: .green
                        )
                    }
                    
                    NavigationLink(destination: StudyView()) {
                        QuickActionButton(
                            title: "Study Now",
                            icon: "play.circle",
                            color: .blue
                        )
                    }
                }
                
                HStack(spacing: 15) {
                    NavigationLink(destination: AIGenerationView()) {
                        QuickActionButton(
                            title: "AI Generate",
                            icon: "sparkles",
                            color: .purple
                        )
                    }
                    
                    Button(action: {
                        // Test notification functionality
                        testNotification()
                    }) {
                        QuickActionButton(
                            title: "Test Notification",
                            icon: "bell",
                            color: .orange
                        )
                    }
                }
            }
        }
        .padding()
        .background(Color(.systemGray6))
        .cornerRadius(12)
    }
    
    private func testNotification() {
        let testCard = Card(
            id: 999,
            contentType: "flashcard",
            front: "What is the capital of France?",
            back: "Paris",
            subject: "Geography",
            tags: ["test"],
            nextReview: "",
            isAiGenerated: false
        )
        
        notificationManager.scheduleTestNotification(card: testCard)
    }
}

struct QuickActionButton: View {
    let title: String
    let icon: String
    let color: Color
    
    var body: some View {
        VStack(spacing: 8) {
            Image(systemName: icon)
                .font(.title2)
                .foregroundColor(color)
            
            Text(title)
                .font(.caption)
                .fontWeight(.medium)
        }
        .frame(maxWidth: .infinity)
        .padding()
        .background(Color(.systemBackground))
        .cornerRadius(8)
        .shadow(radius: 1)
    }
}

#Preview {
    ContentView()
        .environmentObject(AppState())
        .environmentObject(NotificationManager())
}