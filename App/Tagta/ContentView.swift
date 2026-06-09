//
//  ContentView.swift
//  Tagta
//
//  Created by gaoliandi.1 on 2026/6/8.
//  Tagta主视图：整合订阅验证和苹果登录
//

import SwiftUI

struct ContentView: View {
    @StateObject private var subscriptionManager = SubscriptionManager.shared
    @StateObject private var loginManager = LoginManager.shared
    @State private var showLoginView = false

    // H5应用的URL
    private let mainURL = URL(string: "https://siriuscm.github.io/Tagta/")!

    var body: some View {
        Group {
            if subscriptionManager.isSubscribed && loginManager.isLoggedIn {
                // 已订阅且已登录，显示主界面WebView
                WebViewRepresentable(
                    url: mainURL,
                    isLoggedIn: $loginManager.isLoggedIn,
                    appleUserId: loginManager.appleUserId,
                    identityToken: loginManager.identityToken
                )
                .ignoresSafeArea(edges: .horizontal)
            } else if subscriptionManager.isSubscribed {
                // 已订阅但未登录，显示苹果登录
                SignInWithAppleView()
            } else {
                // 未订阅，显示订阅提示
                SubscriptionRequiredView()
            }
        }
        .onAppear {
            // 立即发一个网络请求，触发 iOS 本地网络权限弹窗
            Task {
                _ = try? await URLSession.shared.data(from: URL(string: "https://gcsng.jr.jd.com/wjzgTest/api/ping")!)
            }
            Task {
                await subscriptionManager.updateSubscriptionStatus()
                if subscriptionManager.isSubscribed {
                    loginManager.checkCredentialStatus()
                }
            }
        }
    }
}

struct SubscriptionRequiredView: View {
    @State private var showSubscriptionView = false

    var body: some View {
        VStack(spacing: 30) {
            Spacer()

            Image(systemName: "tag.fill")
                .font(.system(size: 80))
                .foregroundColor(.blue)
                .padding(.bottom, 20)

            VStack(spacing: 15) {
                Text("欢迎使用 Tagta")
                    .font(.largeTitle)
                    .fontWeight(.bold)

                Text("类似Twitter的社交分享平台")
                    .font(.title3)
                    .foregroundColor(.secondary)
                    .multilineTextAlignment(.center)
            }

            Spacer()

            VStack(spacing: 20) {
                Text("解锁全部功能")
                    .font(.title2)
                    .fontWeight(.semibold)

                Text("仅需 1 元")
                    .font(.title)
                    .foregroundColor(.blue)
                    .fontWeight(.bold)

                Button(action: {
                    showSubscriptionView = true
                }) {
                    HStack {
                        Image(systemName: "applelogo")
                        Text("订阅解锁全部功能")
                    }
                    .font(.headline)
                    .foregroundColor(.white)
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(Color.blue)
                    .cornerRadius(12)
                }
                .padding(.horizontal, 30)

                Button("恢复购买") {
                    Task {
                        await SubscriptionManager.shared.restorePurchases()
                    }
                }
                .font(.body)
                .foregroundColor(.blue)
            }

            Spacer()
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