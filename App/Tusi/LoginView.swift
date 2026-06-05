//
//  LoginView.swift
//  Tusi
//
//  Created by gaoliandi.1 on 2026/6/5.
//

import SwiftUI
import WebKit

struct LoginView: View {
    @StateObject private var subscriptionManager = SubscriptionManager.shared
    @StateObject private var loginManager = LoginManager.shared
    @State private var showSubscriptionView = false

    private let loginURL = URL(string: "https://your-h5-login-domain.com/login")!

    var body: some View {
        VStack {
            if subscriptionManager.isSubscribed {
                WebViewRepresentable(url: loginURL, isLoggedIn: $loginManager.isLoggedIn)
                    .ignoresSafeArea(edges: .horizontal)
            } else {
                SubscriptionPromptView(showSubscriptionView: $showSubscriptionView)
            }
        }
        .onAppear {
            Task {
                await subscriptionManager.updateSubscriptionStatus()
            }
        }
        .sheet(isPresented: $showSubscriptionView) {
            SubscriptionView()
        }
    }
}

struct SubscriptionPromptView: View {
    @Binding var showSubscriptionView: Bool

    var body: some View {
        VStack(spacing: 20) {
            Image(systemName: "lock.fill")
                .font(.system(size: 60))
                .foregroundColor(.blue)

            Text("登录功能需要订阅")
                .font(.title)
                .fontWeight(.bold)

            Text("请先订阅以使用登录功能")
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

            Button("恢复购买") {
                Task {
                    await SubscriptionManager.shared.restorePurchases()
                }
            }
            .font(.body)
            .foregroundColor(.blue)
        }
        .padding()
    }
}

struct SubscriptionView: View {
    @StateObject private var subscriptionManager = SubscriptionManager.shared
    @Environment(\.dismiss) private var dismiss

    var body: some View {
        NavigationView {
            VStack(spacing: 30) {
                VStack(spacing: 15) {
                    Text("Tusi 订阅")
                        .font(.largeTitle)
                        .fontWeight(.bold)

                    Text("订阅价格由 App Store 决定")
                        .font(.title2)
                        .foregroundColor(.blue)

                    Text("订阅后可使用完整登录功能")
                        .font(.body)
                        .foregroundColor(.secondary)
                        .multilineTextAlignment(.center)
                }

                VStack(alignment: .leading, spacing: 15) {
                    FeatureRow(icon: "person.circle.fill", text: "完整登录功能")
                    FeatureRow(icon: "lock.open.fill", text: "所有功能解锁")
                    FeatureRow(icon: "cloud.fill", text: "云端同步")
                }
                .padding()

                Spacer()

                VStack(spacing: 15) {
                    Button(action: {
                        Task {
                            await subscriptionManager.purchaseSubscription()
                            if subscriptionManager.isSubscribed {
                                dismiss()
                            }
                        }
                    }) {
                        if subscriptionManager.isLoading {
                            ProgressView()
                                .frame(maxWidth: .infinity)
                        } else {
                            Text("确认订阅")
                                .font(.headline)
                                .foregroundColor(.white)
                                .frame(maxWidth: .infinity)
                                .padding()
                                .background(Color.blue)
                                .cornerRadius(10)
                        }
                    }
                    .disabled(subscriptionManager.isLoading)

                    Button("恢复购买") {
                        Task {
                            await subscriptionManager.restorePurchases()
                            if subscriptionManager.isSubscribed {
                                dismiss()
                            }
                        }
                    }
                    .font(.body)
                    .foregroundColor(.blue)
                }
                .padding()
            }
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("关闭") {
                        dismiss()
                    }
                }
            }
        }
    }
}

struct FeatureRow: View {
    let icon: String
    let text: String

    var body: some View {
        HStack {
            Image(systemName: icon)
                .foregroundColor(.blue)
                .frame(width: 30)

            Text(text)
                .font(.body)

            Spacer()
        }
    }
}