//
//  WebViewRepresentable.swift
//  Tusi
//
//  Created by gaoliandi.1 on 2026/4/20.
//

import SwiftUI
import WebKit

struct WebViewRepresentable: UIViewRepresentable {
    let url: URL
    @Binding var isLoggedIn: Bool

    func makeUIView(context: Context) -> WKWebView {
        let webView = WKWebView()
        webView.navigationDelegate = context.coordinator
        webView.allowsBackForwardNavigationGestures = true

        webView.customUserAgent = "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"

        let request = URLRequest(url: url)
        webView.load(request)

        return webView
    }

    func updateUIView(_ uiView: WKWebView, context: Context) {
    }

    func makeCoordinator() -> Coordinator {
        Coordinator(self)
    }

    class Coordinator: NSObject, WKNavigationDelegate {
        let parent: WebViewRepresentable
        var isLoading = true

        init(_ parent: WebViewRepresentable) {
            self.parent = parent
        }

        func webView(_ webView: WKWebView, didStartProvisionalNavigation navigation: WKNavigation!) {
            print("开始加载网页...")
            isLoading = true
        }

        func webView(_ webView: WKWebView, didFinish navigation: WKNavigation!) {
            print("✅ 网页加载完成")
            isLoading = false
            checkLoginStatus(webView: webView)
        }

        func webView(_ webView: WKWebView, didFail navigation: WKNavigation!, withError error: Error) {
            print("❌ 网页加载失败：\(error.localizedDescription)")
            isLoading = false
        }

        func webView(_ webView: WKWebView, didFailProvisionalNavigation navigation: WKNavigation!, withError error: Error) {
            print("❌ 网页初步加载失败：\(error.localizedDescription)")
            isLoading = false
        }

        func webView(_ webView: WKWebView, decidePolicyFor navigationAction: WKNavigationAction, decisionHandler: @escaping (WKNavigationActionPolicy) -> Void) {
            if navigationAction.targetFrame == nil {
                decisionHandler(.allow)
            } else {
                decisionHandler(.allow)
            }
        }

        private func checkLoginStatus(webView: WKWebView) {
            let script = """
                (function() {
                    var isLoggedIn = false;
                    try {
                        isLoggedIn = localStorage.getItem('isLoggedIn') === 'true';
                    } catch(e) {}
                    try {
                        isLoggedIn = document.cookie.includes('auth_token');
                    } catch(e) {}
                    return isLoggedIn;
                })();
                """

            webView.evaluateJavaScript(script) { [weak self] result, error in
                if let isLoggedIn = result as? Bool {
                    DispatchQueue.main.async {
                        self?.parent.isLoggedIn = isLoggedIn
                    }
                }
            }
        }
    }
}