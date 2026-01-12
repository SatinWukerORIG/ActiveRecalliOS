import SwiftUI
import Foundation

struct AddCardView: View {
    @Environment(\.dismiss) private var dismiss
    @EnvironmentObject var appState: AppState
    
    @State private var contentType = "flashcard"
    @State private var front = ""
    @State private var back = ""
    @State private var subject = ""
    @State private var tagsText = ""
    @State private var isLoading = false
    @State private var showingAlert = false
    @State private var alertMessage = ""
    
    private let contentTypes = ["flashcard", "information"]
    
    var body: some View {
        NavigationView {
            Form {
                Section(header: Text("Content Type")) {
                    Picker("Type", selection: $contentType) {
                        ForEach(contentTypes, id: \.self) { type in
                            Text(type.capitalized).tag(type)
                        }
                    }
                    .pickerStyle(SegmentedPickerStyle())
                }
                
                Section(header: Text(contentType == "flashcard" ? "Question" : "Information")) {
                    TextEditor(text: $front)
                        .frame(minHeight: 80)
                }
                
                if contentType == "flashcard" {
                    Section(header: Text("Answer")) {
                        TextEditor(text: $back)
                            .frame(minHeight: 80)
                    }
                }
                
                Section(header: Text("Organization")) {
                    TextField("Subject (optional)", text: $subject)
                    
                    TextField("Tags (comma-separated)", text: $tagsText)
                        .autocapitalization(.none)
                }
                
                Section {
                    Button(action: addCard) {
                        HStack {
                            if isLoading {
                                ProgressView()
                                    .scaleEffect(0.8)
                            }
                            Text("Add Card")
                                .fontWeight(.medium)
                        }
                        .frame(maxWidth: .infinity)
                    }
                    .disabled(isLoading || front.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty)
                }
            }
            .navigationTitle("Add Card")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("Cancel") {
                        dismiss()
                    }
                }
            }
            .alert("Result", isPresented: $showingAlert) {
                Button("OK") {
                    if alertMessage.contains("successfully") {
                        dismiss()
                    }
                }
            } message: {
                Text(alertMessage)
            }
        }
    }
    
    private func addCard() {
        guard let user = appState.currentUser else { return }
        
        let trimmedFront = front.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmedFront.isEmpty else { return }
        
        let trimmedBack = back.trimmingCharacters(in: .whitespacesAndNewlines)
        let trimmedSubject = subject.trimmingCharacters(in: .whitespacesAndNewlines)
        
        // Parse tags
        let tags = tagsText
            .split(separator: ",")
            .map { $0.trimmingCharacters(in: .whitespacesAndNewlines) }
            .filter { !$0.isEmpty }
        
        isLoading = true
        
        Task {
            do {
                let cardId = try await APIManager.shared.addCard(
                    userId: user.id,
                    contentType: contentType,
                    front: trimmedFront,
                    back: contentType == "flashcard" && !trimmedBack.isEmpty ? trimmedBack : nil,
                    subject: !trimmedSubject.isEmpty ? trimmedSubject : nil,
                    tags: tags
                )
                
                await MainActor.run {
                    self.isLoading = false
                    self.alertMessage = "Card added successfully! ID: \(cardId)"
                    self.showingAlert = true
                }
            } catch {
                await MainActor.run {
                    self.isLoading = false
                    self.alertMessage = "Failed to add card: \(error.localizedDescription)"
                    self.showingAlert = true
                }
            }
        }
    }
}

#Preview {
    AddCardView()
        .environmentObject(AppState())
}