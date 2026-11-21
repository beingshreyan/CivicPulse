from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QStackedWidget,
    QFrame,
)
from ui.dashboard_view import DashboardView
from ui.triage_view import TriageView
from ui.duplicate_view import DuplicateView
from ui.analytics_view import AnalyticsView
from ui.roles_view import RolesView


ROLE_PERMISSIONS = {
    "analyst": ["dashboard", "analytics"],
    "updater": ["dashboard", "triage"],
    "dispatcher": ["dashboard", "triage", "analytics"],
    "reviewer": ["dashboard", "triage", "duplicates"],
    "manager": ["dashboard", "triage", "duplicates", "analytics", "roles"],
    "superadmin": ["dashboard", "triage", "duplicates", "analytics", "roles"],
}


class MainWindow(QMainWindow):
    def __init__(self, api, on_logout):
        super().__init__()
        self.api = api
        self.on_logout = on_logout
        self.role = (api.user or {}).get("role", "analyst")

        self.setWindowTitle(f"CivicPulse Admin Console — {self.role.upper()}")
        self.resize(1240, 780)

        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Sidebar
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sb_layout = QVBoxLayout(sidebar)
        sb_layout.setContentsMargins(0, 0, 0, 16)
        sb_layout.setSpacing(4)

        brand = QLabel("CIVICPULSE")
        brand.setObjectName("SidebarBrand")
        user_name = (api.user or {}).get("name", "Official")
        role_lbl = QLabel(f"{user_name}\nROLE: {self.role.upper()}")
        role_lbl.setObjectName("SidebarRole")

        sb_layout.addWidget(brand)
        sb_layout.addWidget(role_lbl)

        # Views & Navigation
        self.stack = QStackedWidget()
        self.views = {}
        self.nav_buttons = {}

        allowed = ROLE_PERMISSIONS.get(self.role, ["dashboard"])
        nav_items = [
            ("dashboard", "01. Dashboard & KPIs", DashboardView(api)),
            ("triage", "02. Triage & Verification", TriageView(api, self.role)),
            ("duplicates", "03. Duplicate Review", DuplicateView(api)),
            ("analytics", "04. Analytics & Reports", AnalyticsView(api)),
            ("roles", "05. Role & Invite Mgmt", RolesView(api)),
        ]

        for key, label, widget in nav_items:
            if key not in allowed:
                continue
            self.views[key] = widget
            self.stack.addWidget(widget)

            btn = QPushButton(label)
            btn.setProperty("class", "nav-btn")
            btn.clicked.connect(lambda checked=False, k=key: self.switch_view(k))
            sb_layout.addWidget(btn)
            self.nav_buttons[key] = btn

        sb_layout.addStretch()

        logout_btn = QPushButton("Logout")
        logout_btn.setProperty("class", "nav-btn")
        logout_btn.clicked.connect(self._handle_logout)
        sb_layout.addWidget(logout_btn)

        root.addWidget(sidebar)
        root.addWidget(self.stack, 1)

        if allowed:
            self.switch_view(allowed[0])

    def switch_view(self, key: str):
        for k, btn in self.nav_buttons.items():
            btn.setProperty("active", "true" if k == key else "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)

        widget = self.views[key]
        self.stack.setCurrentWidget(widget)
        if hasattr(widget, "refresh"):
            widget.refresh()

    def _handle_logout(self):
        self.api.logout()
        self.on_logout()