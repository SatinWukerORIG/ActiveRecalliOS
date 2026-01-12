import SwiftUI
import Foundation

struct AIGenerationView: View {
    @EnvironmentObject var appState: AppState
    @Environment(\.dismiss) private var dismiss
    
    @State private var sourceMaterial = ""
    @State private var generationType = "flashcards"
    @State private var subject = ""
    @State private var maxCards = 10
    @State private var difficultyLevel = "medium"
    @State private var isGenerating = false
    @State private var showingResult = false
    @State private var generationResult: ContentGenerationResult?
    @State private var errorMessage: String?
    @State private var showingError = false
    
    private let generationTypes = ["flashcards", "information", "mixed"]
    private let difficultyLevels = ["easy", "medium", "hard"]
    
    var body: some View {
        NavigationView {
            Form {
                Section(header: Text("Study Material")) {
                    TextEditor(text: $sourceMaterial)
                        .frame(minHeight: 120)
                        .overlay(
                            RoundedRectangle(cornerRadius: 8)
                                .stroke(Color(.systemGray4), lineWidth: 1)
                        )
                    
                    Text("Paste your study material here (notes, textbook excerpts, articles, etc.)")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
                
                Section(header: Text("Generation Settings")) {
                    Picker("Content Type", selection: $generationType) {
                        Text("Flashcards").tag("flashcards")
                        Text("Information Pieces").tag("information")
                        Text("Mixed Content").tag("mixed")
                    }
                    .pickerStyle(SegmentedPickerStyle())
                    
                    TextField("Subject (optional)", text: $subject)
                    
                    HStack {
                        Text("Max Items")
                        Spacer()
                        Stepper("\(maxCards)", value: $maxCards, in: 1...20)
                    }
                    
                    Picker("Difficulty", selection: $difficultyLevel) {
                        Text("Easy").tag("easy")
                        Text("Medium").tag("medium")
                        Text("Hard").tag("hard")
                    }
                    .pickerStyle(MenuPickerStyle())
                }
                
                Section(header: Text("AI Generation")) {
                    VStack(alignment: .leading, spacing: 12) {
                        HStack {
                            Image(systemName: "sparkles")
                                .foregroundColor(.purple)
                            Text("AI-Powered Content Creation")
                                .font(.headline)
                        }
                        
                        Text("Our AI will analyze your study material and create optimized flashcards and information pieces for spaced repetition learning.")
                            .font(.caption)
                            .foregroundColor(.secondary)
                        
                        Button(action: generateContent) {
                            HStack {
                                if isGenerating {
                                    ProgressView()
                                        .scaleEffect(0.8)
                                }
                                Text(isGenerating ? "Generating..." : "Generate Content")
                                    .fontWeight(.medium)
                            }
                            .frame(maxWidth: .infinity)
                        }
                        .buttonStyle(.borderedProminent)
                        .disabled(isGenerating || sourceMaterial.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty)
                    }
                }
                
                if let result = generationResult {
                    Section(header: Text("Generation Results")) {
                        ResultsView(result: result)
                    }
                }
            }
            .navigationTitle("AI Content Generation")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("Cancel") {
                        dismiss()
                    }
                }
                
                if generationResult != nil {
                    ToolbarItem(placement: .navigationBarTrailing) {
                        Button("Done") {
                            dismiss()
                        }
                    }
                }
            }
            .alert("Generation Error", isPresented: $showingError) {
                Button("OK") { }
            } message: {
                Text(errorMessage ?? "Unknown error occurred")
            }
        }
    }
    
    private func generateContent() {
        // Implementation would go here
    }
}

struct ResultsView: View {
    let result: ContentGenerationResult
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Image(systemName: "checkmark.circle.fill")
                    .foregroundColor(.green)
                Text("Successfully generated \(result.cardsGenerated) items")
                    .font(.headline)
            }
            
            Text("All generated content has been added to your card collection and is ready for spaced repetition learning.")
                .font(.caption)
                .foregroundColor(.secondary)
        }
    }
}

#Preview {
    AIGenerationView()
        .environmentObject(AppState())
}