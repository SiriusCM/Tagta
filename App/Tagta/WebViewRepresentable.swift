//
//  WebViewRepresentable.swift
//  Tagta
//
//  WebView容器
//  将Apple登录信息传递给H5应用
//

import SwiftUI
import WebKit

struct WebViewRepresentable: UIViewRepresentable {
    let url: URL
    @Binding var isLoggedIn: Bool
    var appleUserId: String?

    func makeUIView(context: Context) -> WKWebView {
        let configuration = WKWebViewConfiguration()
        configuration.allowsInlineMediaPlayback = true
        configuration.mediaTypesRequiringUserActionForPlayback = []

        // 注入JavaScript脚本，初始化登录状态
        let userScript = WKUserScript(
            source: """
                window.tagtaApp = {
                    appleUserId: '\(appleUserId ?? "")',
                    isLoggedIn: \(isLoggedIn),
                    platform: 'ios'
                };
                localStorage.setItem('appleUserId', '\(appleUserId ?? "")');
                localStorage.setItem('platform', 'ios');
            """,
            injectionTime: .atDocumentStart,
            forMainFrameOnly: false
        )
        configuration.userContentController.addUserScript(userScript)

        let webView = WKWebView(frame: .zero, configuration: configuration)
        webView.navigationDelegate = context.coordinator
        webView.allowsBackForwardNavigationGestures = true

        // 设置UserAgent
        webView.customUserAgent = "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1 Tagta/1.0"

        let request = URLRequest(url: url)
        webView.load(request)

        return webView
    }

    func updateUIView(_ uiView: WKWebView, context: Context) {
        // 监听登录状态变化
    }

    func makeCoordinator() -> Coordinator {
        Coordinator(self)
    }

    class Coordinator: NSObject, WKNavigationDelegate {
        let parent: WebViewRepresentable

        init(_ parent: WebViewRepresentable) {
            self.parent = parent
        }

        func webView(_ webView: WKWebView, didStartProvisionalNavigation navigation: WKNavigation!) {
            print("开始加载网页...")
        }

        func webView(_ webView: WKWebView, didFinish navigation: WKNavigation!) {
            print("网页加载完成")

            // 每次页面加载完成后，确保登录状态已注入
            let script = """
                if (!window.tagtaApp) {
                    window.tagtaApp = {
                        appleUserId: '\(parent.appleUserId ?? "")',
                        isLoggedIn: \(parent.isLoggedIn),
                        platform: 'ios'
                    };
                }
            """
            webView.evaluateJavaScript(script) { _, error in
                if let error = error {
                    print("JavaScript执行错误: \(error.localizedDescription)")
                }
            }
        }

        func webView(_ webView: WKWebView, didFail navigation: WKNavigation!, withError error: Error) {
            print("网页加载失败：\(error.localizedDescription)")
        }

        func webView(_ webView: WKWebView, didFailProvisionalNavigation navigation: WKNavigation!, withError error: Error) {
            print("网页初步加载失败：\(error.localizedDescription)")
        }

        func webView(_ webView: WKWebView, decidePolicyFor navigationAction: WKNavigationAction, decisionHandler: @escaping (WKNavigationActionPolicy) -> Void) {
            // 允许所有导航
            decisionHandler(.allow)
        }

        // 拦截URL，处理登录回调等
        func webView(_ webView: WKWebView, decidePolicyFor navigationResponse: WKNavigationResponse, decisionHandler: @escaping (WKNavigationResponsePolicy) -> Void) {
            decisionHandler(.allow)
        }
    }
}