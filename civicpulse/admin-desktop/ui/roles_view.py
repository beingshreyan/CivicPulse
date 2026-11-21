from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QComboBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QFrame,
    QMessageBox,
)


class RolesView(QWidget):
    def __init__(self, api):
        super().__init__()
        self.api = api

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        title = QLabel("Manager Console — Admin Invites & Role Management")
        title.setProperty("class", "page-title")
        layout.addWidget(title)

        # Invite Form Card
        invite_card = QFrame()
        invite_card.setProperty("class", "card")
        ic_layout = QHBoxLayout(invite_card)
        ic_layout.setContentsMargins(14, 14, 14, 14)

        self.invite_email = QLineEdit()
        self.invite_email.setPlaceholderText("Enter official email to authorize...")

        self.invite_role = QComboBox()
        self.invite_role.addItems(["reviewer", "dispatcher", "updater", "analyst", "manager"])

        self.invite_dept = QComboBox()
        invite_btn = QPushButton("Authorize Email")
        invite_btn.setProperty("class", "btn-primary")
        invite_btn.clicked.connect(self._send_invite)

        ic_layout.addWidget(self.invite_email, 2)
        ic_layout.addWidget(self.invite_role)
        ic_layout.addWidget(self.invite_dept)
        ic_layout.addWidget(invite_btn)
        layout.addWidget(invite_card)

        # Authorized Invites Table
        layout.addWidget(QLabel("Authorized Admin Invites"))
        self.invites_table = QTableWidget(0, 3)
        self.invites_table.setHorizontalHeaderLabels(["Email", "Assigned Role", "Registration Status"])
        self.invites_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.invites_table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.invites_table, 1)

        # Registered Users Table
        layout.addWidget(QLabel("Registered Accounts"))
        self.users_table = QTableWidget(0, 4)
        self.users_table.setHorizontalHeaderLabels(["User ID", "Name", "Email", "Role"])
        self.users_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.users_table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.users_table, 1)

    def refresh(self):
        try:
            depts = self.api.get_departments()
            self.invite_dept.clear()
            self.invite_dept.addItem("No Specific Dept", None)
            for d in depts:
                self.invite_dept.addItem(d["name"], d["department_id"])

            invites = self.api.get_invites()
            self.invites_table.setRowCount(len(invites))
            for row, inv in enumerate(invites):
                self.invites_table.setItem(row, 0, QTableWidgetItem(inv["email"]))
                self.invites_table.setItem(row, 1, QTableWidgetItem(inv["role"].upper()))
                status_text = "Registered" if inv["is_used"] else "Pending Registration"
                self.invites_table.setItem(row, 2, QTableWidgetItem(status_text))

            users = self.api.get_users()
            self.users_table.setRowCount(len(users))
            for row, u in enumerate(users):
                self.users_table.setItem(row, 0, QTableWidgetItem(str(u["user_id"])))
                self.users_table.setItem(row, 1, QTableWidgetItem(u["name"]))
                self.users_table.setItem(row, 2, QTableWidgetItem(u["email"]))
                self.users_table.setItem(row, 3, QTableWidgetItem(u["role"].upper()))
        except Exception as exc:
            QMessageBox.warning(self, "Error", str(exc))

    def _send_invite(self):
        email = self.invite_email.text().strip()
        if not email:
            QMessageBox.warning(self, "Missing Email", "Enter an email address to authorize.")
            return
        try:
            self.api.create_invite(
                email=email,
                role=self.invite_role.currentText(),
                department_id=self.invite_dept.currentData(),
            )
            self.invite_email.clear()
            QMessageBox.information(self, "Authorized", f"{email} can now register in the Admin Console.")
            self.refresh()
        except Exception as exc:
            QMessageBox.critical(self, "Invite Failed", str(exc))