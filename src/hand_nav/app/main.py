import webview
from hand_nav.app.api import Api

if __name__ == '__main__':
    api = Api()
    try:
        window = webview.create_window('Hand Nav', 'index.html', js_api=api)
        webview.start()
    finally:
        api.close_all()