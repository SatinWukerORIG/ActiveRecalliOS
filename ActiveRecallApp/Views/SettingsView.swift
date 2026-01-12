import SwiftUI
import Foundation

struct SettingsView: View {
    @EnvironmentObject var appState: AppState
    @EnvironmentObject var notificationManager: NotificationManager
    @State private var focusMode = false
    @State private var notificationFrequency = 30
    @State private var sleepStartTime = Date()
    @State private var sleepEndTime = Date()
    @State private var sleepScheduleEnabled = false
    @State private var isLoading = false
    @State private var showingAlert = false
    @State private var alertMessage = ""
    @State private var userAvailability: UserAvailability?
    
    private let frequencyOptions = [15, 30, 60, 120, 240] // minutes
    
    var body: some View {
        NavigationView {
            Form {
                // User Info Section
                Section(header: Text("Account")) {
                    if let user = appState.currentUser {
                        HStack {
                            Text("Username")
                            Spacer()
                            Text(user.username)
                                .foregroundColor(.secondary)
                        }
                        
                        if let email = user.email {
                            HStack {
                                Text("Email")
                                Spacer()
                                Text(email)
                                    .foregroundColor(.secondary)
                            }
                        }
                    }
                }
                
                // Smart Scheduling Section
                Section(header: Text("Smart Scheduling")) {
                    Toggle("Focus Mode", isOn: $focusMode)
                        .onChange(of: focusMode) {
                            updatePreferences()
                        }
                    
                    HStack {
                        Text("Notification Frequency")
                        Spacer()
                        Picker("Frequency", selection: $notificationFrequency) {
                            ForEach(frequencyOptions, id: \.self) { minutes in
                                Text("\(minutes) min").tag(minutes)
                            }
                        }
                        .pickerStyle(MenuPickerStyle())
                        .onChange(of: notificationFrequency) {
                            updatePreferences()
                        }
                    }
                    
                    Toggle("Sleep Schedule", isOn: $sleepScheduleEnabled)
                        .onChange(of: sleepScheduleEnabled) { _, enabled in
                            if enabled {
                                updateSleepSchedule()
                            } else {
                                clearSleepSchedule()
                            }
                        }
                    
                    if sleepScheduleEnabled {
                        DatePicker("Sleep Start", selection: $sleepStartTime, displayedComponents: .hourAndMinute)
                            .onChange(of: sleepStartTime) {
                                updateSleepSchedule()
                            }
                        
                        DatePicker("Sleep End", selection: $sleepEndTime, displayedComponents: .hourAndMinute)
                            .onChange(of: sleepEndTime) {
                                updateSleepSchedule()
                            }
                    }
                }
                
                // Additional sections would be here...
            }
            .navigationTitle("Settings")
            .onAppear {
                loadCurrentSettings()
                checkAvailability()
            }
            .alert("Info", isPresented: $showingAlert) {
                Button("OK") { }
            } message: {
                Text(alertMessage)
            }
        }
    }
    
    private func loadCurrentSettings() {
        if let user = appState.currentUser {
            focusMode = user.focusMode
            notificationFrequency = user.notificationFrequency
        }
    }
    
    private func updatePreferences() {
        // Implementation would go here
    }
    
    private func updateSleepSchedule() {
        // Implementation would go here
    }
    
    private func clearSleepSchedule() {
        // Implementation would go here
    }
    
    private func checkAvailability() {
        // Implementation would go here
    }
}

#Preview {
    SettingsView()
        .environmentObject(AppState())
        .environmentObject(NotificationManager())
}