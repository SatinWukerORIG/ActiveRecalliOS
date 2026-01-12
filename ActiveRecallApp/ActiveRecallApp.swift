import SwiftUI
import Foundation

@main
struct ActiveRecallApp: App {
    @StateObject private var appState = AppState()
    @StateObject private var notificationManager = NotificationManager()
    
    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(appState)
                .environmentObject(notificationManager)
                .onAppear {
                    notificationManager.setupNotificationCategories()
                    notificationManager.requestPermissions()
                }
        }
    }
}