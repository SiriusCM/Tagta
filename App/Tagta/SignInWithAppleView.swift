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

                // 获取邮箱（仅首次登录时提供）
                let email = appleIDCredential.email

                // 获取全名（仅首次登录时提供）
                var fullName: String?
                if let name = appleIDCredential.fullName {
                    let givenName = name.givenName ?? ""
                    let familyName = name.familyName ?? ""
                    if !givenName.isEmpty || !familyName.isEmpty {
                        fullName = "\(givenName) \(familyName)".trimmingCharacters(in: .whitespaces)
                    }
                }

                // 发送到后端进行验证，成功后才保存登录状态
                await sendToBackend(
                    identityToken: identityToken,
                    userIdentifier: userIdentifier,
                    email: email,
                    fullName: fullName
                )
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
    private func sendToBackend(identityToken: String?, userIdentifier: String, email: String?, fullName: String?) async {
        do {
            guard let url = URL(string: "https://gcsng.jr.jd.com/wjzgTest/api/apple/login") else {
                errorMessage = "服务器地址无效"
                return
            }

            var request = URLRequest(url: url)
            request.httpMethod = "POST"
            request.setValue("application/json", forHTTPHeaderField: "Content-Type")

            var body: [String: Any] = [
                "identity_token": identityToken ?? ""
            ]

            // 只有当有值时才添加到请求中
            if let email = email {
                body["email"] = email
            }
            if let fullName = fullName {
                body["full_name"] = fullName
            }

            request.httpBody = try JSONSerialization.data(withJSONObject: body)

            let (data, response) = try await URLSession.shared.data(for: request)

            guard let httpResponse = response as? HTTPURLResponse else {
                errorMessage = "服务器响应无效"
                return
            }

            if httpResponse.statusCode == 200 {
                if let json = try JSONSerialization.jsonObject(with: data) as? [String: Any] {
                    // 后端验证成功，保存登录状态
                    if let userData = json["user"] as? [String: Any],
                       let userId = userData["id"] {
                        loginManager.saveUserId(userId as? Int ?? 0)
                    }
                    // 存储 token（用于后续请求）
                    if let token = json["token"] as? String {
                        loginManager.saveIdentityToken(token)
                    }
                    // 保存 Apple 用户标识
                    loginManager.saveLoginState(token: userIdentifier)
                    return
                }
            }

            // 后端验证失败，重置登录状态
            loginManager.logout()

            if let json = try JSONSerialization.jsonObject(with: data) as? [String: Any],
               let detail = json["detail"] as? String {
                errorMessage = detail
            } else if let json = try JSONSerialization.jsonObject(with: data) as? [String: Any],
               let message = json["message"] as? String {
                errorMessage = message
            } else {
                errorMessage = "登录验证失败"
            }

        } catch {
            // 网络错误，重置登录状态
            loginManager.logout()
            errorMessage = "网络错误: \(error.localizedDescription)"
        }
    }
}

#Preview {
    SignInWithAppleView()
}