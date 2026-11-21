from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QMessageBox,
)


class AnalyticsView(QWidget):
    def __init__(self, api):
        super().__init__()
        self.api = api

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)

        header = QHBoxLayout()
        title = QLabel("Municipal Analytics & Category Breakdown")
        title.setProperty("class", "page-title")
        refresh_btn = QPushButton("Refresh")
        refresh_btn.setProperty("class", "btn-outline")
        refresh_btn.clicked.connect(self.refresh)
        header.addWidget(title)
        header.addStretch()
        header.addWidget(refresh_btn)
        layout.addLayout(header)

        self.summary_lbl = QLabel("Loading metrics...")
        self.summary_lbl.setProperty("class", "section-title")
        layout.addWidget(self.summary_lbl)

        self.cat_table = QTableWidget(0, 2)
        self.cat_table.setHorizontalHeaderLabels(["Civic Category", "Total Complaints"])
        self.cat_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.cat_table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.cat_table, 1)

    def refresh(self):
        try:
            data = self.api.get_analytics()
            self.summary_lbl.setText(
                f"Active: {data['active_reports']}  |  Total Votes: {data['total_votes']}  |  "
                f"Verified: {data['verified_percentage']}%  |  Resolved: {data['resolved_count']}"
            )
            by_cat = data.get("by_category", {})
            self.cat_table.setRowCount(len(by_cat))
            for row, (name, count) in enumerate(by_cat.items()):
                self.cat_table.setItem(row, 0, QTableWidgetItem(name))
                self.cat_table.setItem(row, 1, QTableWidgetItem(str(count)))
        except Exception as exc:
            QMessageBox.warning(self, "Analytics Error", str(exc))