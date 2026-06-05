//
//  ContentView.swift
//  Tusi
//
//  Created by gaoliandi.1 on 2026/4/20.
//

import SwiftUI

struct ContentView: View {
    @StateObject private var subscriptionManager = SubscriptionManager.shared
    @StateObject private var loginManager = LoginManager.shared
    @State private var showLoginView = false

    let mainURL = URL(string: "https://www.doubao.com/")!

    var body: some View {
        Group {
            if subscriptionManager.isSubscribed && loginManager.isLoggedIn {
                WebViewRepresentable(url: mainURL, isLoggedIn: $loginManager.isLoggedIn)
                    .ignoresSafeArea(edges: .horizontal)
            } else if subscriptionManager.isSubscribed {
                // 已订阅但未登录，显示登录按钮
                LoginPromptView(showLoginView: $showLoginView)
            } else {
                // 未订阅，显示订阅提示
                SubscriptionRequiredView()
            }
        }
        .onAppear {
            Task {
                await subscriptionManager.updateSubscriptionStatus()
            }
            loginManager.checkCredentialStatus()
        }
        .sheet(isPresented: $showLoginView) {
            SignInWithAppleView()
        }
    }
}

struct LoginPromptView: View {
    @Binding var showLoginView: Bool

    var body: some View {
        VStack(spacing: 20) {
            Image(systemName: "person.circle.fill")
                .font(.system(size: 60))
                .foregroundColor(.blue)

            Text("欢迎使用 Tusi")
                .font(.title)
                .fontWeight(.bold)

            Text("您已订阅，请登录以使用完整功能")
                .font(.body)
                .foregroundColor(.secondary)
                .multilineTextAlignment(.center)

            Button("登录") {
                showLoginView = true
            }
            .font(.headline)
            .foregroundColor(.white)
            .padding()
            .background(Color.blue)
            .cornerRadius(10)
        }
        .padding()
    }
}

struct SubscriptionRequiredView: View {
    @State private var showSubscriptionView = false

    var body: some View {
        VStack(spacing: 20) {
            Image(systemName: "lock.fill")
                .font(.system(size: 60))
                .foregroundColor(.blue)

            Text("需要订阅")
                .font(.title)
                .fontWeight(.bold)

            Text("请订阅以使用完整功能")
                .font(.body)
                .foregroundColor(.secondary)
                .multilineTextAlignment(.center)

            Button("订阅") {
                showSubscriptionView = true
            }
            .font(.headline)
            .foregroundColor(.white)
            .padding()
            .background(Color.blue)
            .cornerRadius(10)
        }
        .padding()
        .sheet(isPresented: $showSubscriptionView) {
            SubscriptionView()
        }
    }
}

#Preview {
    ContentView()
}