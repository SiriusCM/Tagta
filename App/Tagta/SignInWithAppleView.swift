//
//  SignInWithAppleView.swift
//  Tagta
//
//  Sign in with Apple 登录视图
//  用户必须先订阅才能登录
//

import SwiftUI
import AuthenticationServices

struct SignInWithAppleView: View {
    @StateObject private var loginManager = LoginManager.shared
    @State private var isLoading = false
    @State private var errorMessage: String?

    var body: some View {
        VStack(spacing: 40) {
            Spacer()

            // App Logo
            Image(systemName: "tag.fill")
                .font(.system(size: 80))
                .foregroundColor(.blue)
                .padding(.bottom, 20)

            VStack(spacing: 10) {
                Text("欢迎使用 Tagta")
                    .font(.largeTitle)
                    .fontWeight(.bold)

                Text("使用 Apple ID 登录")
                    .font(.body)
                    .foregroundColor(.secondary)
            }

            Spacer()

            // Sign in with Apple Button
            if isLoading {
                ProgressView()
                    .frame(height: 50)
                    .padding(.horizontal, 30)
            } else {
                SignInWithAppleButton(.signIn) { request in
                    request.requestedScopes = [.email, .fullName]
                } onCompletion: { result in
                    handleSignInResult(result)
                }
                .signInWithAppleButtonStyle(.black)
                .frame(height: 50)
                .cornerRadius(10)
                .padding(.horizontal, 30)
            }

            // 错误提示
            if let error = errorMessage {
                Text(error)
                    .font(.caption)
                    .foregroundColor(.red)
                    .multilineTextAlignment(.center)
                    .padding(.horizontal)
            }

            // 恢复购买
            Button("已有账户？恢复购买") {
                Task {
                    await SubscriptionManager.shared.restorePurchases()
                }
            }
            .font(.body)
            .foregroundColor(.blue)
            .padding(.bottom, 40)

            Spacer()
        }
        .padding()
    }

    private func handleSignInResult(_ result: Result<ASAuthorization, Error>) {
        isLoading = true
        errorMessage = nil

        switch result {
        case .success(let authorization):
            if let appleIDCredential = authorization.credential as? ASAuthorizationAppleIDCredential {
                let userIdentifier = appleIDCredential.user

                // 获取 identity token（JWT）
                var identityToken: String?
                if let tokenData = appleIDCredential.identityToken,
                   let tokenString = String(data: tokenData, encoding: .utf8) {
                    identityToken = tokenString
                }

                // 获取授权码
                var authorizationCode: String?
                if let codeData = appleIDCredential.authorizationCode,
                   let codeString = String(data: codeData, encoding: .utf8) {
                    authorizationCode = codeString
                }

                // 保存登录状态
                loginManager.saveLoginState(token: userIdentifier)

                // 发送到后端进行验证
                Task {
                    await sendToBackend(
                        authorizationCode: authorizationCode,
                        identityToken: identityToken,
                        userIdentifier: userIdentifier
                    )
                }
            }
            isLoading = false

        case .failure(let error):
            isLoading = false
            if let asError = error as? ASAuthorizationError {
                switch asError.code {
                case .canceled:
                    // 用户取消，不显示错误
                    break
                case .failed:
                    errorMessage = "登录失败，请重试"
                case .invalidResponse:
                    errorMessage = "服务器响应无效"
                case .notHandled:
                    errorMessage = "请求未处理"
                case .unknown:
                    errorMessage = "发生未知错误"
                case .notInteractive:
                    errorMessage = "需要交互式登录"
                @unknown default:
                    errorMessage = "登录失败"
                }
            } else {
                errorMessage = error.localizedDescription
            }
        }
    }

    /// 发送登录信息到后端进行验证
    private func sendToBackend(authorizationCode: String?, identityToken: String?, userIdentifier: String) async {
        do {
            // 测试环境用localhost，发布时改为真实地址
            // guard let url = URL(string: "http://116.196.69.192:8080/api/apple/login") else {
            guard let url = URL(string: "http://localhost:8080/api/apple/login") else {
                errorMessage = "服务器地址无效"
                return
            }

            var request = URLRequest(url: url)
            request.httpMethod = "POST"
            request.setValue("application/json", forHTTPHeaderField: "Content-Type")

            let body: [String: Any] = [
                "apple_user_id": userIdentifier,
                "authorization_code": authorizationCode ?? "",
                "identity_token": identityToken ?? ""
            ]

            request.httpBody = try JSONSerialization.data(withJSONObject: body)

            let (data, response) = try await URLSession.shared.data(for: request)

            guard let httpResponse = response as? HTTPURLResponse else {
                errorMessage = "服务器响应无效"
                return
            }

            if httpResponse.statusCode == 200 {
                if let json = try JSONSerialization.jsonObject(with: data) as? [String: Any],
                   let success = json["success"] as? Bool, success {
                    // 登录成功
                    if let userData = json["user"] as? [String: Any],
                       let userId = userData["id"] {
                        loginManager.saveUserId(userId as? Int ?? 0)
                    }
                    if let token = json["token"] as? String {
                        loginManager.saveAuthToken(token)
                    }
                    return
                }
            }

            if let json = try JSONSerialization.jsonObject(with: data) as? [String: Any],
               let message = json["message"] as? String {
                errorMessage = message
            } else {
                errorMessage = "登录验证失败"
            }

        } catch {
            errorMessage = "网络错误: \(error.localizedDescription)"
        }
    }
}

#Preview {
    SignInWithAppleView()
}