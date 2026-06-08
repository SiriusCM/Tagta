//
//  SubscriptionManager.swift
//  Tagta
//
//  Created by gaoliandi.1 on 2026/6/5.
//

import Foundation
import Combine
import StoreKit

@MainActor
class SubscriptionManager: ObservableObject {
    static let shared = SubscriptionManager()
    @Published var isSubscribed = false
    @Published var isLoading = false

    private let productID = "10000"
    private var products: [Product] = []

    init() {
        Task {
            await requestProducts()
        }
        // 监听交易更新，处理后台购买恢复等场景
        Task {
            await listenForTransactionUpdates()
        }
    }

    /// 监听 Transaction.updates，处理后台购买恢复
    private func listenForTransactionUpdates() async {
        for await result in Transaction.updates {
            guard case .verified(let transaction) = result else {
                print("⚠️ 交易验证失败")
                continue
            }

            if transaction.productID == productID {
                isSubscribed = true
                print("✅ 通过 Transaction.updates 检测到有效订阅")
            }

            await transaction.finish()
        }
    }

    func requestProducts() async {
        isLoading = true
        do {
            products = try await Product.products(for: [productID])
            print("📦 获取到 \(products.count) 个产品")
            if products.isEmpty {
                print("⚠️ 没有找到订阅产品，请检查：")
                print("   1. App Store Connect 中是否创建了订阅产品")
                print("   2. 产品 ID 是否正确: \(productID)")
                print("   3. 是否使用沙盒测试账号")
            }
            await updateSubscriptionStatus()
        } catch {
            print("获取产品信息失败: \(error)")
        }
        isLoading = false
    }

    func purchaseSubscription() async {
        guard let product = products.first else {
            print("❌ 没有找到订阅产品，请确认 App Store Connect 中已创建产品")
            isLoading = false
            return
        }

        isLoading = true
        do {
            let result = try await product.purchase()

            switch result {
            case .success(let verification):
                let transaction = try checkVerified(verification)
                await updateSubscriptionStatus()
                await transaction.finish()
                print("✅ 订阅成功")
            case .userCancelled:
                print("用户取消购买")
            case .pending:
                print("购买等待中")
            @unknown default:
                break
            }
        } catch {
            print("购买失败: \(error)")
        }
        isLoading = false
    }

    func restorePurchases() async {
        isLoading = true
        do {
            try await AppStore.sync()
            await updateSubscriptionStatus()
        } catch {
            print("恢复购买失败: \(error)")
        }
        isLoading = false
    }

    func updateSubscriptionStatus() async {
        for await result in Transaction.currentEntitlements {
            guard case .verified(let transaction) = result else { continue }

            if transaction.productID == productID {
                isSubscribed = true
                return
            }
        }
        isSubscribed = false
    }

    private func checkVerified<T>(_ result: VerificationResult<T>) throws -> T {
        switch result {
        case .unverified:
            throw StoreError.failedVerification
        case .verified(let safe):
            return safe
        }
    }
}

enum StoreError: Error {
    case failedVerification
}