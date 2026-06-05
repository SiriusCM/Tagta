//
//  LoginManager.swift
//  Tusi
//
//  Created by gaoliandi.1 on 2026/6/5.
//

import Foundation
import Combine
import SwiftUI
import WebKit
import AuthenticationServices

@MainActor
class LoginManager: ObservableObject {
    static let shared = LoginManager()
    @Published var isLoggedIn = false
    @Published var authToken: String?

    private let authTokenKey = "AppleUserIdentifier"

    init() {
        loadLoginState()
    }

    func logout() {
        isLoggedIn = false
        authToken = nil
        UserDefaults.standard.removeObject(forKey: authTokenKey)
        UserDefaults.standard.synchronize()
    }

    func saveLoginState(token: String) {
        isLoggedIn = true
        authToken = token
        UserDefaults.standard.set(token, forKey: authTokenKey)
        UserDefaults.standard.synchronize()
    }

    private func loadLoginState() {
        if let token = UserDefaults.standard.string(forKey: authTokenKey) {
            authToken = token
            isLoggedIn = !token.isEmpty
        }
    }

    /// 检查 Apple ID 凭证状态
    func checkCredentialStatus() {
        guard let userIdentifier = UserDefaults.standard.string(forKey: authTokenKey) else {
            isLoggedIn = false
            return
        }

        let provider = ASAuthorizationAppleIDProvider()
        let key = authTokenKey

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