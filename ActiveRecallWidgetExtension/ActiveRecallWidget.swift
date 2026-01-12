import WidgetKit
import SwiftUI
import ActivityKit

// This struct defines the visual layout of your Live Activity widget
struct ActiveRecallWidget: Widget {
    var body: some WidgetConfiguration {
        ActivityConfiguration(for: RecallAttributes.self) { context in
            // 1. LOCK SCREEN / BANNER UI
            VStack(alignment: .leading, spacing: 10) {
                HStack {
                    Image(systemName: "brain.head.profile")
                        .foregroundColor(.green)
                    Text("Active Recall Session")
                        .font(.headline)
                        .foregroundColor(.secondary)
                    Spacer()
                    Text("\(Int(context.state.progress * 100))%")
                        .font(.caption2)
                        .bold()
                }
                
                Text(context.state.question)
                    .font(.title3)
                    .fontWeight(.medium)
                
                ProgressView(value: context.state.progress)
                    .tint(.green)
            }
            .padding()
            .activityBackgroundTint(Color.black.opacity(0.8))
            
        } dynamicIsland: { context in
            // 2. DYNAMIC ISLAND UI
            DynamicIsland {
                // Expanded State
                DynamicIslandExpandedRegion(.leading) {
                    Image(systemName: "brain")
                        .foregroundColor(.green)
                }
                DynamicIslandExpandedRegion(.trailing) {
                    Text("Review")
                        .font(.caption2)
                        .bold()
                }
                DynamicIslandExpandedRegion(.bottom) {
                    VStack(alignment: .leading) {
                        Text(context.state.question)
                            .font(.body)
                        Spacer(minLength: 5)
                        ProgressView(value: context.state.progress)
                            .tint(.green)
                    }
                }
            } compactLeading: {
                Image(systemName: "brain")
                    .foregroundColor(.green)
            } compactTrailing: {
                Text("\(Int(context.state.progress * 100))%")
                    .font(.caption2)
            } minimal: {
                Image(systemName: "brain")
                    .foregroundColor(.green)
            }
        }
    }
}

@main
struct ActiveRecallWidgetBundle: WidgetBundle {
    var body: some Widget {
        ActiveRecallWidget()
    }
}