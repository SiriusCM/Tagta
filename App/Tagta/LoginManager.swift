//
//  LoginManager.swift
//  Tagta
//
//  登录管理器
//  处理苹果登录状态和用户信息
//

import Foundation
import Combine
import SwiftUI
import AuthenticationServices

@MainActor
class LoginManager: ObservableObject {
    static let shared = LoginManager()

    @Published var isLoggedIn = false
    @Published var appleUserId: String?
    @Published var userId: Int = 0
    @Published var identityToken: String?

    private let appleUserIdKey = "AppleUserIdentifier"
    private let userIdKey = "TagtaUserId"
    private let identityTokenKey = "TagtaIdentityToken"

    init() {
        loadLoginState()
    }

    func logout() {
        isLoggedIn = false
        appleUserId = nil
        userId = 0
        identityToken = nil
        UserDefaults.standard.removeObject(forKey: appleUserIdKey)
        UserDefaults.standard.removeObject(forKey: userIdKey)
        UserDefaults.standard.removeObject(forKey: identityTokenKey)
        UserDefaults.standard.synchronize()
    }

    func saveLoginState(token: String) {
        isLoggedIn = true
        appleUserId = token
        UserDefaults.standard.set(token, forKey: appleUserIdKey)
        UserDefaults.standard.synchronize()
    }

    func saveUserId(_ id: Int) {
        userId = id
        UserDefaults.standard.set(id, forKey: userIdKey)
        UserDefaults.standard.synchronize()
    }

    /// 保存 identityToken（用于后续请求认证）
    func saveIdentityToken(_ token: String) {
        identityToken = token
        UserDefaults.standard.set(token, forKey: identityTokenKey)
        UserDefaults.standard.synchronize()
    }

    private func loadLoginState() {
        if let token = UserDefaults.standard.string(forKey: appleUserIdKey) {
            appleUserId = token
            isLoggedIn = !token.isEmpty
        }
        userId = UserDefaults.standard.integer(forKey: userIdKey)
        identityToken = UserDefaults.standard.string(forKey: identityTokenKey)
    }

    /// 获取当前 identityToken，用于请求头
    func getIdentityToken() -> String? {
        return identityToken
    }

    /// 检查 Apple ID 凭证状态
    func checkCredentialStatus() {
        guard let userIdentifier = UserDefaults.standard.string(forKey: appleUserIdKey) else {
            isLoggedIn = false
            return
        }

        let provider = ASAuthorizationAppleIDProvider()
        let key = appleUserIdKey

        provider.getCredentialState(forUserID: userIdentifier) { credentialState, error in
            Task { @MainActor [weak self] in
                guard let self = self else { return }

                if let error = error {
                    print("检查凭证状态失败: \(error.localizedDescription)")
                    self.isLoggedIn = false
                    return
                }

                switch credentialState {
                case .authorized:
                    self.isLoggedIn = true
                    print("Apple ID 凭证状态: 已授权")

                case .revoked:
                    self.isLoggedIn = false
                    self.logout()
                    print("Apple ID 凭证状态: 已撤销")

                case .notFound:
                    self.isLoggedIn = false
                    UserDefaults.standard.removeObject(forKey: key)
                    print("Apple ID 凭证状态: 未找到")

                case .transferred:
                    self.isLoggedIn = false
                    print("Apple ID 凭证状态: 已转移")

                @unknown default:
                    self.isLoggedIn = false
                    print("Apple ID 凭证状态: 未知")
                }
            }
        }
    }
}