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


class DuplicateView(QWidget):
    def __init__(self, api):
        super().__init__()
        self.api = api
        self.reviews = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)

        header = QHBoxLayout()
        title = QLabel("Duplicate Candidate Review (Human Verification)")
        title.setProperty("class", "page-title")
        refresh_btn = QPushButton("Refresh Queue")
        refresh_btn.setProperty("class", "btn-outline")
        refresh_btn.clicked.connect(self.refresh)
        header.addWidget(title)
        header.addStretch()
        header.addWidget(refresh_btn)
        layout.addLayout(header)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels([
            "Review ID", "New Report", "Existing Candidate", "Text Similarity", "Distance (m)"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table, 1)

        actions = QHBoxLayout()
        merge_btn = QPushButton("Confirm Duplicate (Merge into Existing)")
        merge_btn.setProperty("class", "btn-primary")
        merge_btn.clicked.connect(lambda: self._decide("merged"))

        separate_btn = QPushButton("Keep Separate (Distinct Issues)")
        separate_btn.setProperty("class", "btn-outline")
        separate_btn.clicked.connect(lambda: self._decide("separate"))

        actions.addWidget(merge_btn)
        actions.addWidget(separate_btn)
        actions.addStretch()
        layout.addLayout(actions)

    def refresh(self):
        try:
            self.reviews = self.api.get_pending_duplicates()
            self.table.setRowCount(len(self.reviews))
            for row, r in enumerate(self.reviews):
                self.table.setItem(row, 0, QTableWidgetItem(str(r["review_id"])))
                self.table.setItem(row, 1, QTableWidgetItem(f"CP-{r['complaint_id']}"))
                self.table.setItem(row, 2, QTableWidgetItem(f"CP-{r['candidate_id']}"))
                self.table.setItem(row, 3, QTableWidgetItem(f"{r['similarity_score'] * 100:.1f}%"))
                self.table.setItem(row, 4, QTableWidgetItem(f"{r['geographic_distance']:.1f} m"))
        except Exception as exc:
            QMessageBox.warning(self, "Error", str(exc))

    def _decide(self, decision: str):
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            QMessageBox.information(self, "No Selection", "Select a flagged candidate pair first.")
            return
        review = self.reviews[rows[0].row()]
        try:
            self.api.decide_duplicate(review["review_id"], decision)
            self.refresh()
        except Exception as exc:
            QMessageBox.critical(self, "Decision Failed", str(exc))