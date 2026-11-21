import requests
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QFrame,
    QComboBox,
    QLineEdit,
    QFileDialog,
    QMessageBox,
    QInputDialog,
)

CATEGORIES = {
    1: "Roads & Potholes",
    2: "Garbage & Sanitation",
    3: "Drainage & Waterlogging",
    4: "Streetlights & Electricity",
    5: "Water Supply",
    6: "Public Infrastructure",
    7: "Other Civic Issues",
}


class TriageView(QWidget):
    def __init__(self, api, role: str):
        super().__init__()
        self.api = api
        self.role = role
        self.complaints = []
        self.departments = []
        self.selected_id = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)

        # Header & Filters
        header = QHBoxLayout()
        title = QLabel("Complaint Triage, Verification & Dispatch")
        title.setProperty("class", "page-title")

        self.status_filter = QComboBox()
        self.status_filter.addItems([
            "all", "submitted", "under_review", "accepted",
            "in_progress", "resolved", "rejected", "reopened"
        ])
        self.status_filter.currentTextChanged.connect(self.refresh)

        refresh_btn = QPushButton("Refresh")
        refresh_btn.setProperty("class", "btn-outline")
        refresh_btn.clicked.connect(self.refresh)

        header.addWidget(title)
        header.addStretch()
        header.addWidget(QLabel("Status:"))
        header.addWidget(self.status_filter)
        header.addWidget(refresh_btn)
        layout.addLayout(header)

        # Table
        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels([
            "ID", "Category", "Description", "Votes", "Priority", "Department", "Status"
        ])
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.itemSelectionChanged.connect(self._on_row_selected)
        layout.addWidget(self.table, 1)

        # Inspector / Action Panel (Left: Details & Actions | Right: Photo Preview)
        panel = QFrame()
        panel.setProperty("class", "card")
        panel_root = QHBoxLayout(panel)
        panel_root.setContentsMargins(16, 14, 16, 14)
        panel_root.setSpacing(16)

        # Left side
        p_layout = QVBoxLayout()
        p_layout.setSpacing(10)

        self.inspector_lbl = QLabel("Select a complaint row above to inspect and take action.")
        self.inspector_lbl.setProperty("class", "section-title")
        self.inspector_lbl.setWordWrap(True)
        p_layout.addWidget(self.inspector_lbl)

        controls = QHBoxLayout()
        self.dept_combo = QComboBox()
        self.note_input = QLineEdit()
        self.note_input.setPlaceholderText("Optional official update note for citizen timeline...")

        controls.addWidget(QLabel("Assign Dept:"))
        controls.addWidget(self.dept_combo)
        controls.addWidget(self.note_input, 1)
        p_layout.addLayout(controls)

        actions = QHBoxLayout()
        self.btn_verify = QPushButton("Approve & Verify")
        self.btn_verify.setProperty("class", "btn-primary")
        self.btn_verify.clicked.connect(lambda: self._update_ticket("accepted"))

        self.btn_reject = QPushButton("Reject (with Reason)")
        self.btn_reject.setProperty("class", "btn-danger")
        self.btn_reject.clicked.connect(self._reject_ticket)

        self.btn_progress = QPushButton("Mark In Progress")
        self.btn_progress.setProperty("class", "btn-accent")
        self.btn_progress.clicked.connect(lambda: self._update_ticket("in_progress"))

        self.btn_resolve = QPushButton("Upload Resolution Photo & Resolve")
        self.btn_resolve.setProperty("class", "btn-primary")
        self.btn_resolve.clicked.connect(self._upload_resolution)

        if self.role in ("reviewer", "manager", "superadmin"):
            actions.addWidget(self.btn_verify)
            actions.addWidget(self.btn_reject)
        if self.role in ("dispatcher", "updater", "manager", "superadmin"):
            actions.addWidget(self.btn_progress)
        if self.role in ("updater", "manager", "superadmin"):
            actions.addWidget(self.btn_resolve)

        actions.addStretch()
        p_layout.addLayout(actions)
        panel_root.addLayout(p_layout, 1)

        # Right side: Citizen Evidence Photo Preview
        self.photo_preview = QLabel("No Photo")
        self.photo_preview.setFixedSize(200, 140)
        self.photo_preview.setAlignment(Qt.AlignCenter)
        self.photo_preview.setStyleSheet(
            "background-color: #f4f7f7; border: 1px dashed #cbd5e1; "
            "border-radius: 8px; color: #64748b; font-weight: 600;"
        )
        panel_root.addWidget(self.photo_preview)

        layout.addWidget(panel)

    def refresh(self):
        try:
            self.departments = self.api.get_departments()
            self.dept_combo.clear()
            self.dept_combo.addItem("-- Unchanged --", None)
            for d in self.departments:
                self.dept_combo.addItem(d["name"], d["department_id"])

            status = self.status_filter.currentText()
            self.complaints = self.api.get_complaints(status=status)
            self.table.setRowCount(len(self.complaints))

            for row, c in enumerate(self.complaints):
                self.table.setItem(row, 0, QTableWidgetItem(f"CP-{c['complaint_id']}"))
                self.table.setItem(row, 1, QTableWidgetItem(CATEGORIES.get(c["category_id"], "Other")))
                self.table.setItem(row, 2, QTableWidgetItem(c["description"]))
                self.table.setItem(row, 3, QTableWidgetItem(str(c.get("votes", 0))))
                self.table.setItem(row, 4, QTableWidgetItem(f"{c.get('priority_score', 0):.1f}"))
                self.table.setItem(row, 5, QTableWidgetItem(c.get("department") or "Unassigned"))
                self.table.setItem(row, 6, QTableWidgetItem(c["status"].upper()))
        except Exception as exc:
            QMessageBox.warning(self, "Load Error", str(exc))

    def _load_photo_preview(self, image_url: str):
        if not image_url:
            self.photo_preview.setPixmap(QPixmap())
            self.photo_preview.setText("No Photo")
            return

        full_url = image_url if image_url.startswith("http") else f"{self.api.base_url}{image_url}"
        try:
            resp = requests.get(full_url, timeout=6)
            resp.raise_for_status()
            pixmap = QPixmap()
            pixmap.loadFromData(resp.content)
            scaled = pixmap.scaled(
                self.photo_preview.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )
            self.photo_preview.setPixmap(scaled)
        except Exception:
            self.photo_preview.setPixmap(QPixmap())
            self.photo_preview.setText("Preview Unavailable")

    def _on_row_selected(self):
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            self.selected_id = None
            self._load_photo_preview(None)
            return
        c = self.complaints[rows[0].row()]
        self.selected_id = c["complaint_id"]
        self.inspector_lbl.setText(
            f"Ticket CP-{c['complaint_id']} | Coords: ({c['latitude']:.4f}, {c['longitude']:.4f}) | "
            f"Priority: {c['priority_score']} | {c['description']}"
        )
        self._load_photo_preview(c.get("image_url"))

    def _update_ticket(self, new_status: str):
        if not self.selected_id:
            QMessageBox.information(self, "No Selection", "Select a complaint first.")
            return
        try:
            dept_id = self.dept_combo.currentData()
            note = self.note_input.text().strip() or None
            self.api.update_status(self.selected_id, new_status, department_id=dept_id, note=note)
            self.note_input.clear()
            self.refresh()
        except Exception as exc:
            QMessageBox.critical(self, "Update Failed", str(exc))

    def _reject_ticket(self):
        if not self.selected_id:
            QMessageBox.information(self, "No Selection", "Select a complaint first.")
            return
        reason, ok = QInputDialog.getText(self, "Rejection Reason", "Enter mandatory documented reason:")
        if not ok or not reason.strip():
            return
        try:
            self.api.update_status(self.selected_id, "rejected", rejection_reason=reason.strip())
            self.refresh()
        except Exception as exc:
            QMessageBox.critical(self, "Rejection Failed", str(exc))

    def _upload_resolution(self):
        if not self.selected_id:
            QMessageBox.information(self, "No Selection", "Select a complaint first.")
            return
        path, _ = QFileDialog.getOpenFileName(self, "Select Resolution Photo", "", "Images (*.jpg *.jpeg *.png)")
        if not path:
            return
        try:
            self.api.upload_resolution_photo(self.selected_id, path)
            QMessageBox.information(self, "Resolved", f"CP-{self.selected_id} marked Resolved with photo evidence.")
            self.refresh()
        except Exception as exc:
            QMessageBox.critical(self, "Upload Failed", str(exc))