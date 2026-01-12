import ActivityKit
import WidgetKit
import SwiftUI

// MARK: - Live Activity Widget
struct StudyLiveActivityWidget: Widget {
    var body: some WidgetConfiguration {
        ActivityConfiguration(for: StudyActivityAttributes.self) { context in
            // Lock Screen View
            StudyLockScreenView(context: context)
        } dynamicIsland: { context in
            // Dynamic Island View
            DynamicIsland {
                // Expanded View
                DynamicIslandExpandedRegion(.leading) {
                    Image(systemName: "brain.head.profile")
                        .foregroundColor(.blue)
                }
                DynamicIslandExpandedRegion(.trailing) {
                    Text(context.state.subject)
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
                DynamicIslandExpandedRegion(.bottom) {
                    if context.state.cardType == "flashcard" {
                        DynamicIslandFlashcardView(state: context.state)
                    } else {
                        DynamicIslandInformationView(state: context.state)
                    }
                }
            } compactLeading: {
                Image(systemName: "brain.head.profile")
                    .foregroundColor(.blue)
            } compactTrailing: {
                Text("🧠")
            } minimal: {
                Image(systemName: "brain.head.profile")
                    .foregroundColor(.blue)
            }
        }
    }
}

// MARK: - Lock Screen View
struct StudyLockScreenView: View {
    let context: ActivityViewContext<StudyActivityAttributes>
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            // Header
            HStack {
                Image(systemName: "brain.head.profile")
                    .foregroundColor(.blue)
                    .font(.title2)
                
                VStack(alignment: .leading) {
                    Text("Active Recall")
                        .font(.headline)
                        .fontWeight(.semibold)
                    
                    Text("Study Session Active")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
                
                Spacer()
                
                VStack(alignment: .trailing) {
                    if context.state.isOverdue {
                        Text("OVERDUE")
                            .font(.caption2)
                            .fontWeight(.bold)
                            .foregroundColor(.red)
                    }
                    
                    Text("Updated \(Date(timeIntervalSince1970: context.state.lastUpdated), style: .relative) ago")
                        .font(.caption2)
                        .foregroundColor(.secondary)
                }
            }
            
            // Content
            if context.state.cardType == "flashcard" {
                LockScreenFlashcardView(state: context.state)
            } else {
                LockScreenInformationView(state: context.state)
            }
            
            // Footer
            HStack {
                if let folderName = context.state.folderName {
                    Label(folderName, systemImage: "folder")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
                
                Spacer()
                
                Text("Tap to open app")
                    .font(.caption)
                    .foregroundColor(.blue)
            }
        }
        .padding()
        .background(
            RoundedRectangle(cornerRadius: 16)
                .fill(Color(.systemBackground))
                .shadow(radius: 4)
        )
    }
}

// MARK: - Lock Screen Content Views
struct LockScreenFlashcardView: View {
    let state: StudyActivityAttributes.ContentState
    @State private var showAnswer = false
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            // Question
            VStack(alignment: .leading, spacing: 4) {
                Text("Question:")
                    .font(.caption)
                    .fontWeight(.medium)
                    .foregroundColor(.secondary)
                
                Text(state.question ?? "")
                    .font(.body)
                    .fontWeight(.medium)
                    .multilineTextAlignment(.leading)
            }
            
            Divider()
            
            // Answer Section
            if showAnswer || state.showAnswer {
                VStack(alignment: .leading, spacing: 4) {
                    Text("Answer:")
                        .font(.caption)
                        .fontWeight(.medium)
                        .foregroundColor(.secondary)
                    
                    Text(state.answer ?? "")
                        .font(.body)
                        .foregroundColor(.blue)
                        .multilineTextAlignment(.leading)
                }
            } else {
                Button(action: { showAnswer = true }) {
                    HStack {
                        Image(systemName: "eye")
                        Text("Tap to reveal answer")
                    }
                    .font(.caption)
                    .foregroundColor(.blue)
                }
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
    }
}

struct LockScreenInformationView: View {
    let state: StudyActivityAttributes.ContentState
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                Image(systemName: "lightbulb")
                    .foregroundColor(.orange)
                Text("Key Information")
                    .font(.caption)
                    .fontWeight(.medium)
                    .foregroundColor(.secondary)
            }
            
            Text(state.information ?? "")
                .font(.body)
                .fontWeight(.medium)
                .multilineTextAlignment(.leading)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
    }
}

// MARK: - Dynamic Island Views
struct DynamicIslandFlashcardView: View {
    let state: StudyActivityAttributes.ContentState
    
    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            Text("Q: \(state.question ?? "")")
                .font(.caption)
                .lineLimit(2)
            
            if state.showAnswer {
                Text("A: \(state.answer ?? "")")
                    .font(.caption)
                    .foregroundColor(.blue)
                    .lineLimit(1)
            } else {
                Text("Tap to reveal answer")
                    .font(.caption2)
                    .foregroundColor(.secondary)
            }
        }
    }
}

struct DynamicIslandInformationView: View {
    let state: StudyActivityAttributes.ContentState
    
    var body: some View {
        HStack {
            Image(systemName: "lightbulb")
                .foregroundColor(.orange)
                .font(.caption)
            
            Text(state.information ?? "")
                .font(.caption)
                .lineLimit(2)
        }
    }
}

// MARK: - Widget Bundle
@main
struct ActiveRecallWidgetBundle: WidgetBundle {
    var body: some Widget {
        StudyLiveActivityWidget()
    }
}