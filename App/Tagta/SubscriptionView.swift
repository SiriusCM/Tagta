//
//  SubscriptionView.swift
//  Tagta
//
//  订阅视图
//

import SwiftUI

struct SubscriptionView: View {
    @StateObject private var subscriptionManager = SubscriptionManager.shared
    @Environment(\.dismiss) private var dismiss

    var body: some View {
        NavigationView {
            VStack(spacing: 30) {
                VStack(spacing: 15) {
                    Image(systemName: "tag.fill")
                        .font(.system(size: 60))
                        .foregroundColor(.blue)
                        .padding(.bottom, 10)

                    Text("Tagta 订阅")
                        .font(.largeTitle)
                        .fontWeight(.bold)

                    Text("仅需 1 元")
                        .font(.title2)
                        .foregroundColor(.blue)
                        .fontWeight(.semibold)

                    Text("解锁完整社交分享功能")
                        .font(.body)
                        .foregroundColor(.secondary)
                        .multilineTextAlignment(.center)
                }

                VStack(alignment: .leading, spacing: 15) {
                    FeatureRow(icon: "person.circle.fill", text: "完整社交功能")
                    FeatureRow(icon: "video.fill", text: "发布视频和图文")
                    FeatureRow(icon: "heart.fill", text: "关注和点赞")
                    FeatureRow(icon: "lock.open.fill", text: "所有功能解锁")
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
                            HStack {
                                Image(systemName: "applelogo")
                                Text("确认订阅")
                            }
                            .font(.headline)
                            .foregroundColor(.white)
                            .frame(maxWidth: .infinity)
                            .padding()
                            .background(Color.blue)
                            .cornerRadius(12)
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

                    Text("订阅后可以随时取消，自动续订可在设置中关闭")
                        .font(.caption)
                        .foregroundColor(.secondary)
                        .multilineTextAlignment(.center)
                        .padding(.top, 10)
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

#Preview {
    SubscriptionView()
}