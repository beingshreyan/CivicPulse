from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTabWidget,
    QWidget,
    QMessageBox,
    QFrame,
)


class LoginWindow(QDialog):
    login_successful = Signal(dict)

    def __init__(self, api):
        super().__init__()
        self.api = api
        self.setWindowTitle("CivicPulse Municipal Admin Console — Sign In")
        self.setFixedSize(420, 440)

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(14)

        # Header
        brand = QLabel("CIVICPULSE")
        brand.setAlignment(Qt.AlignCenter)
        brand.setStyleSheet("font-size: 22px; font-weight: 800; color: #0b3d3b; letter-spacing: 1px;")
        subtitle = QLabel("Municipal Admin & Verification Console")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("font-size: 12px; color: #4b5563;")
        root.addWidget(brand)
        root.addWidget(subtitle)

        # Card with Login / Invite-Only Register Tabs
        card = QFrame()
        card.setProperty("class", "card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(16, 16, 16, 16)

        self.tabs = QTabWidget()
        self.tabs.addTab(self._build_login_tab(), "Admin Login")
        self.tabs.addTab(self._build_register_tab(), "Invited Registration")
        card_layout.addWidget(self.tabs)
        root.addWidget(card)

    def _build_login_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(10)

        self.login_email = QLineEdit()
        self.login_email.setPlaceholderText("Official email address")
        self.login_pass = QLineEdit()
        self.login_pass.setPlaceholderText("Password")
        self.login_pass.setEchoMode(QLineEdit.Password)

        btn = QPushButton("Sign In")
        btn.setProperty("class", "btn-primary")
        btn.clicked.connect(self._handle_login)

        layout.addWidget(QLabel("Email"))
        layout.addWidget(self.login_email)
        layout.addWidget(QLabel("Password"))
        layout.addWidget(self.login_pass)
        layout.addSpacing(8)
        layout.addWidget(btn)
        layout.addStretch()
        return tab

    def _build_register_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(8)

        info = QLabel("Use the exact email authorized by your Manager.")
        info.setStyleSheet("font-size: 11px; color: #4b5563;")
        info.setWordWrap(True)

        self.reg_name = QLineEdit()
        self.reg_name.setPlaceholderText("Full Name")
        self.reg_email = QLineEdit()
        self.reg_email.setPlaceholderText("Authorized Email")
        self.reg_pass = QLineEdit()
        self.reg_pass.setPlaceholderText("Create Password (min 8 chars)")
        self.reg_pass.setEchoMode(QLineEdit.Password)

        btn = QPushButton("Register Official Account")
        btn.setProperty("class", "btn-accent")
        btn.clicked.connect(self._handle_register)

        layout.addWidget(info)
        layout.addWidget(self.reg_name)
        layout.addWidget(self.reg_email)
        layout.addWidget(self.reg_pass)
        layout.addSpacing(6)
        layout.addWidget(btn)
        layout.addStretch()
        return tab

    def _handle_login(self):
        email = self.login_email.text().strip()
        password = self.login_pass.text()
        if not email or not password:
            QMessageBox.warning(self, "Missing Fields", "Please enter both email and password.")
            return
        try:
            auth_data = self.api.login(email, password)
            self.login_successful.emit(auth_data)
            self.accept()
        except Exception as exc:
            QMessageBox.critical(self, "Login Failed", str(exc))

    def _handle_register(self):
        name = self.reg_name.text().strip()
        email = self.reg_email.text().strip()
        password = self.reg_pass.text()
        if not name or not email or len(password) < 8:
            QMessageBox.warning(self, "Invalid Input", "Provide name, email, and a password of at least 8 characters.")
            return
        try:
            self.api.admin_register(name, email, password)
            QMessageBox.information(self, "Account Created", "Registration successful! You can now sign in.")
            self.login_email.setText(email)
            self.tabs.setCurrentIndex(0)
        except Exception as exc:
            QMessageBox.critical(self, "Registration Blocked", str(exc))