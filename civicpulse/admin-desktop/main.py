import os
import sys
from PySide6.QtWidgets import QApplication
from api_client import ApiClient
from ui.login_window import LoginWindow
from ui.main_window import MainWindow


def load_stylesheet(app: QApplication):
    qss_path = os.path.join(os.path.dirname(__file__), "ui", "theme.qss")
    if os.path.exists(qss_path):
        with open(qss_path, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())


def main():
    app = QApplication(sys.argv)
    load_stylesheet(app)

    api = ApiClient("https://civicpulse-u137.onrender.com")  
    main_win = None

    def show_login():
        nonlocal main_win
        if main_win:
            main_win.close()
            main_win = None

        login = LoginWindow(api)
        if login.exec() == LoginWindow.Accepted:
            main_win = MainWindow(api, on_logout=show_login)
            main_win.show()
        else:
            app.quit()

    show_login()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()