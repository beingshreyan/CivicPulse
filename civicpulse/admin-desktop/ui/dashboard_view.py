from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QFrame,
    QPushButton,
    QMessageBox,
)


class DashboardView(QWidget):
    def __init__(self, api):
        super().__init__()
        self.api = api

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(18)

        header = QHBoxLayout()
        title = QLabel("Municipal Complaint Intelligence Dashboard")
        title.setProperty("class", "page-title")
        refresh_btn = QPushButton("Refresh Data")
        refresh_btn.setProperty("class", "btn-outline")
        refresh_btn.clicked.connect(self.refresh)
        header.addWidget(title)
        header.addStretch()
        header.addWidget(refresh_btn)
        layout.addLayout(header)

        # 6 KPI Cards
        grid = QGridLayout()
        grid.setSpacing(14)
        self.kpi_labels = {}

        cards = [
            ("total", "TOTAL COMPLAINTS", "#0b3d3b"),
            ("pending", "PENDING REVIEW", "#b45309"),
            ("high_priority", "HIGH PRIORITY (>=75)", "#dc2626"),
            ("in_progress", "IN PROGRESS", "#0369a1"),
            ("resolved", "RESOLVED", "#15803d"),
            ("reopened", "REOPENED", "#c2410c"),
        ]

        for idx, (key, label_text, accent) in enumerate(cards):
            card = QFrame()
            card.setProperty("class", "card")
            card.setStyleSheet(f"QFrame {{ border-top: 3px solid {accent}; }}")
            c_layout = QVBoxLayout(card)
            c_layout.setContentsMargins(16, 16, 16, 16)

            lbl = QLabel(label_text)
            lbl.setProperty("class", "kpi-label")
            val = QLabel("--")
            val.setProperty("class", "kpi-value")
            val.setStyleSheet(f"color: {accent};")

            c_layout.addWidget(lbl)
            c_layout.addWidget(val)
            self.kpi_labels[key] = val
            grid.addWidget(card, idx // 3, idx % 3)

        layout.addLayout(grid)
        layout.addStretch()

    def refresh(self):
        try:
            complaints = self.api.get_complaints()
            self.kpi_labels["total"].setText(str(len(complaints)))
            self.kpi_labels["pending"].setText(
                str(sum(1 for c in complaints if c["status"] in ("submitted", "under_review")))
            )
            self.kpi_labels["high_priority"].setText(
                str(sum(1 for c in complaints if (c.get("priority_score") or 0) >= 75))
            )
            self.kpi_labels["in_progress"].setText(
                str(sum(1 for c in complaints if c["status"] == "in_progress"))
            )
            self.kpi_labels["resolved"].setText(
                str(sum(1 for c in complaints if c["status"] == "resolved"))
            )
            self.kpi_labels["reopened"].setText(
                str(sum(1 for c in complaints if c["status"] == "reopened"))
            )
        except Exception as exc:
            QMessageBox.warning(self, "Sync Error", f"Could not load dashboard metrics:\n{exc}")