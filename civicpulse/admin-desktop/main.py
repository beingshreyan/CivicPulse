import os
import sys
import certifi
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication
from api_client import ApiClient
from ui.login_window import LoginWindow
from ui.main_window import MainWindow


def resource_path(relative_path: str) -> str:
    base_dir = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, relative_path)


def configure_ssl_certificates() -> None:
    ca_bundle = certifi.where()
    if ca_bundle and os.path.exists(ca_bundle):
        os.environ.setdefault("SSL_CERT_FILE", ca_bundle)
        os.environ.setdefault("REQUESTS_CA_BUNDLE", ca_bundle)


def load_app_icon(app: QApplication) -> None:
    icon_path = resource_path(os.path.join("assets", "civicpulse-icon.svg"))
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))


def load_stylesheet(app: QApplication) -> None:
    qss_path = resource_path(os.path.join("ui", "Theme.qss"))
    if os.path.exists(qss_path):
        with open(qss_path, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())


def main() -> int:
    configure_ssl_certificates()
    app = QApplication(sys.argv)
    load_app_icon(app)
    load_stylesheet(app)

    client = ApiClient()
    login_window = LoginWindow(client)
    main_window_holder = {}

    def on_logout() -> None:
        window = main_window_holder.pop("window", None)
        if window is not None:
            window.close()
        login_window.show()

    def on_login_success(auth_data: dict) -> None:
        window = MainWindow(client, on_logout)
        main_window_holder["window"] = window
        window.show()
        login_window.close()

    login_window.login_successful.connect(on_login_success)
    login_window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())