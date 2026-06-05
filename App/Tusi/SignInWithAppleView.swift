//
//  SignInWithAppleView.swift
//  Tusi
//
//  Sign in with Apple 登录视图
//

import SwiftUI
import AuthenticationServices

struct SignInWithAppleView: View {
    @Environment(\.dismiss) private var dismiss
    @StateObject private var loginManager = LoginManager.shared

    var body: some View {
        NavigationView {
            VStack(spacing: 40) {
                Spacer()

                // App Logo
                Image(systemName: "person.circle.fill")
                    .font(.system(size: 80))
                    .foregroundColor(.blue)

                VStack(spacing: 10) {
                    Text("欢迎使用 Tusi")
                        .font(.title)
                        .fontWeight(.bold)

                    Text("登录以使用完整功能")
                        .font(.body)
                        .foregroundColor(.secondary)
                }

                Spacer()

                // Sign in with Apple Button
                SignInWithAppleButton(.signIn) { request in
                    request.requestedScopes = [.email, .fullName]
                } onCompletion: { result in
                    handleSignInResult(result)
                }
                .signInWithAppleButtonStyle(.black)
                .frame(height: 50)
                .cornerRadius(10)
                .padding(.horizontal, 30)

                // 已有账户提示
                Button("已有账户？恢复购买") {
                    Task {
                        await SubscriptionManager.shared.restorePurchases()
                    }
                }
                .font(.body)
                .foregroundColor(.blue)

                Spacer()
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

    private func handleSignInResult(_ result: Result<ASAuthorization, Error>) {
        switch result {
        case .success(let authorization):
            if let appleIDCredential = authorization.credential as? ASAuthorizationAppleIDCredential {
                // 获取用户唯一标识符
                let userIdentifier = appleIDCredential.user

                // 获取 identity token（JWT）
                if let identityToken = appleIDCredential.identityToken,
                   let tokenString = String(data: identityToken, encoding: .utf8) {
                    print("Apple ID Token: \(tokenString)")

                    // 保存登录状态
                    loginManager.saveLoginState(token: userIdentifier)

                    // TODO: 将 tokenString 发送到后端进行验证
                    sendToBackend(authorizationCode: nil, identityToken: tokenString, userIdentifier: userIdentifier)
                }

                // 获取授权码（用于后端验证）
                if let authorizationCode = appleIDCredential.authorizationCode,
                   let codeString = String(data: authorizationCode, encoding: .utf8) {
                    print("Authorization Code: \(codeString)")

                    // 保存登录状态
                    loginManager.saveLoginState(token: userIdentifier)

                    // 发送到后端
                    sendToBackend(authorizationCode: codeString, identityToken: nil, userIdentifier: userIdentifier)
                }
            }
            dismiss()

        case .failure(let error):
            print("Sign in with Apple failed: \(error.localizedDescription)")
        }
    }

    /// 发送登录信息到后端
    private func sendToBackend(authorizationCode: String?, identityToken: String?, userIdentifier: String) {
        // TODO: 实现后端 API 调用
        // 后端需要：
        // 1. 用 authorizationCode 向 Apple 验证
        // 2. 获取用户信息
        // 3. 返回自己的用户 Token

        print("""
        发送到后端的登录信息：
        - userIdentifier: \(userIdentifier)
        - authorizationCode: \(authorizationCode ?? "nil")
        - identityToken: \(identityToken ?? "nil")
        """)
    }
}

#Preview {
    SignInWithAppleView()
}