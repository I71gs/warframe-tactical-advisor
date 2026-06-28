from __future__ import annotations
import json
from pathlib import Path
from typing import Any

from PySide6.QtCore import Qt, QSortFilterProxyModel, QTimer
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar,
    QGroupBox, QGridLayout, QTabWidget, QTableView, QPushButton,
    QCheckBox, QLineEdit, QHeaderView, QFrame, QSplitter,
    QAbstractItemView, QSpinBox, QDialog, QFormLayout, QDialogButtonBox,
    QTextEdit, QComboBox, QScrollArea,
)

from src.core.app_context import AppContext
from src.core.player_loader import PlayerLoader
from src.core.collection_engine import CollectionEngine, WARFRAME_ROSTER, COMPANION_ROSTER, MASTERY_DATA
from src.database.database import DatabaseManager

_DATA = Path(__file__).resolve().parents[1] / "resources" / "data"

# Colour palette per category
CATEGORY_COLORS = {
    "warframes":   "#caa3ff",
    "weapons":     "#ffb76b",
    "companions":  "#7fffb3",
    "arcanes":     "#7fb3ff",
    "archwings":   "#ff9fd4",
    "necramechs":  "#ffdd79",
    "mods":        "#5cffd8",
    "focus":       "#ffd56b",
    "intrinsics":  "#80cfff",
}


class _EditItemDialog(QDialog):
    """Small dialog to edit details of a collection item."""

    def __init__(self, name: str, data: dict, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle(f"Edit — {name}")
        self.setMinimumWidth(360)

        form = QFormLayout()

        self.owned_cb = QCheckBox("Owned")
        self.owned_cb.setChecked(bool(data.get("owned", False)))
        form.addRow(self.owned_cb)

        self.rank_spin = QSpinBox()
        self.rank_spin.setRange(0, 40)
        self.rank_spin.setValue(int(data.get("rank", 0)))
        form.addRow("Rank:", self.rank_spin)

        self.forma_spin = QSpinBox()
        self.forma_spin.setRange(0, 20)
        self.forma_spin.setValue(int(data.get("forma_count", 0)))
        form.addRow("Forma:", self.forma_spin)

        self.reactor_cb = QCheckBox("Reactor / Catalyst installed")
        self.reactor_cb.setChecked(bool(data.get("has_reactor", False)))
        form.addRow(self.reactor_cb)

        self.notes_edit = QTextEdit()
        self.notes_edit.setPlainText(data.get("notes", ""))
        self.notes_edit.setMaximumHeight(80)
        form.addRow("Notes:", self.notes_edit)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        lay = QVBoxLayout(self)
        lay.addLayout(form)
        lay.addWidget(buttons)

    def result_data(self) -> dict:
        return {
            "owned":      self.owned_cb.isChecked(),
            "rank":       self.rank_spin.value(),
            "forma_count": self.forma_spin.value(),
            "has_reactor": self.reactor_cb.isChecked(),
            "notes":      self.notes_edit.toPlainText(),
        }


class _CollectionTableWidget(QWidget):
    """Reusable table widget for any collection category."""

    COLS = ["Name", "Owned", "Rank", "Forma", "Reactor", "Acquisition", "Notes"]

    def __init__(
        self,
        category_key: str,
        db_table: str,
        roster: list[dict],
        color: str,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.category_key = category_key
        self.db_table = db_table
        self.roster = roster
        self.color = color
        self._db: DatabaseManager | None = None

        lay = QVBoxLayout(self)
        lay.setSpacing(6)

        # ── toolbar ────────────────────────────────────────────────────────
        toolbar = QHBoxLayout()

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("🔍  Search items…")
        self.search_box.textChanged.connect(self._apply_filter)
        toolbar.addWidget(self.search_box)

        self.show_missing = QCheckBox("Missing only")
        self.show_missing.stateChanged.connect(self._apply_filter)
        toolbar.addWidget(self.show_missing)

        mark_btn = QPushButton("✔  Mark Owned")
        mark_btn.setToolTip("Mark selected items as owned")
        mark_btn.clicked.connect(self._mark_owned)
        toolbar.addWidget(mark_btn)

        edit_btn = QPushButton("✏  Edit")
        edit_btn.setToolTip("Edit rank / forma / reactor for selected item")
        edit_btn.clicked.connect(self._edit_selected)
        toolbar.addWidget(edit_btn)

        lay.addLayout(toolbar)

        # ── table ──────────────────────────────────────────────────────────
        self.model = QStandardItemModel(0, len(self.COLS))
        self.model.setHorizontalHeaderLabels(self.COLS)

        self.proxy = QSortFilterProxyModel()
        self.proxy.setSourceModel(self.model)
        self.proxy.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.proxy.setFilterKeyColumn(0)

        self.table = QTableView()
        self.table.setModel(self.proxy)
        self.table.setSortingEnabled(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        from src.core.theme_manager import ThemeManager
        theme_colors = ThemeManager().get_theme_colors(ThemeManager().get_active_theme_name())
        secondary = theme_colors.get("SECONDARY", "#130f26")
        card_bg = theme_colors.get("CARD", "#1f183a")
        text_color = theme_colors.get("TEXT", "#eae6f8")

        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet(f"""
            QTableView {{
                background-color: {secondary};
                alternate-background-color: {card_bg};
                gridline-color: rgba(255, 255, 255, 0.05);
                color: {text_color};
                border: 1px solid rgba(255, 255, 255, 0.05);
                border-radius: 4px;
            }}
            QHeaderView::section {{
                background-color: {card_bg};
                color: {color};
                font-weight: bold;
                border: none;
                padding: 4px;
            }}
        """)
        lay.addWidget(self.table)

        # ── stats bar ──────────────────────────────────────────────────────
        stats_row = QHBoxLayout()
        self.stats_label = QLabel("Owned: 0 / 0")
        self.stats_label.setStyleSheet(f"color: {color}; font-weight: bold;")
        self.progress = QProgressBar()
        self.progress.setTextVisible(True)
        self.progress.setStyleSheet(f"""
            QProgressBar {{
                background-color: {secondary};
                border: 1px solid rgba(255, 255, 255, 0.05);
                border-radius: 4px;
                height: 14px;
            }}
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 4px;
            }}
        """)
        stats_row.addWidget(self.stats_label)
        stats_row.addWidget(self.progress)
        lay.addLayout(stats_row)

    # ── public methods ─────────────────────────────────────────────────────

    def populate(self, db_rows: list[dict]) -> None:
        """Fill the table with roster data merged against DB rows."""
        db_by_name = {r["name"].lower(): r for r in db_rows}
        self.model.setRowCount(0)

        owned_count = 0
        for item in self.roster:
            name = item["name"]
            db = db_by_name.get(name.lower(), {})
            owned = bool(db.get("owned", False))
            rank = db.get("rank", 0)
            forma = db.get("forma_count", 0)
            reactor = "✔" if db.get("has_reactor") else "—"
            acq = item.get("acquisition", db.get("acquisition", ""))
            notes = db.get("notes", "")

            if owned:
                owned_count += 1

            row = [
                QStandardItem(name),
                QStandardItem("✔" if owned else "○"),
                QStandardItem(str(rank)),
                QStandardItem(str(forma)),
                QStandardItem(reactor),
                QStandardItem(acq),
                QStandardItem(notes),
            ]
            for cell in row:
                cell.setEditable(False)
            if owned:
                for cell in row:
                    cell.setForeground(Qt.green)
            self.model.appendRow(row)

        total = len(self.roster)
        pct = round(owned_count / total * 100) if total else 0
        self.stats_label.setText(f"Owned: {owned_count} / {total} ({pct}%)")
        self.progress.setValue(pct)

    # ── private helpers ────────────────────────────────────────────────────

    def _apply_filter(self) -> None:
        text = self.search_box.text()
        if self.show_missing.isChecked():
            self.proxy.setFilterRegularExpression("")
            # Hide rows where Owned column is ✔
            for row in range(self.model.rowCount()):
                owned_item = self.model.item(row, 1)
                match = (owned_item and owned_item.text() == "○")
                name_item = self.model.item(row, 0)
                name_match = (not text) or (name_item and text.lower() in name_item.text().lower())
                self.table.setRowHidden(row, not (match and name_match))
        else:
            self.proxy.setFilterRegularExpression(text)
            for row in range(self.model.rowCount()):
                self.table.setRowHidden(row, False)

    def _get_db(self) -> DatabaseManager:
        if self._db is None:
            self._db = DatabaseManager()
        return self._db

    def _selected_names(self) -> list[str]:
        sel = self.table.selectionModel().selectedRows()
        names = []
        for idx in sel:
            src = self.proxy.mapToSource(idx)
            item = self.model.item(src.row(), 0)
            if item:
                names.append(item.text())
        return names

    def _mark_owned(self) -> None:
        names = self._selected_names()
        db = self._get_db()
        for name in names:
            db.upsert_collection_item(self.db_table, name, owned=True)
        self._refresh_from_db()

    def _edit_selected(self) -> None:
        names = self._selected_names()
        if not names:
            return
        name = names[0]
        db = self._get_db()
        rows = db.get_collection_table(self.db_table)
        existing = next((r for r in rows if r["name"].lower() == name.lower()), {})

        dlg = _EditItemDialog(name, existing, self)
        if dlg.exec() == QDialog.Accepted:
            data = dlg.result_data()
            db.upsert_collection_item(
                self.db_table, name,
                owned=data["owned"],
                rank=data["rank"],
                forma_count=data["forma_count"],
                has_reactor=data["has_reactor"],
                notes=data["notes"],
            )
            self._refresh_from_db()

    def _refresh_from_db(self) -> None:
        db = self._get_db()
        rows = db.get_collection_table(self.db_table)
        self.populate(rows)


class _IntrinsicsWidget(QWidget):
    """Widget for displaying and editing Railjack Intrinsics (0–10 per category)."""

    CATEGORIES = ["Piloting", "Gunnery", "Tactical", "Engineering", "Command"]

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._db: DatabaseManager | None = None

        lay = QVBoxLayout(self)
        title = QLabel("Railjack Intrinsics")
        title.setStyleSheet("font-size: 14px; font-weight: bold; color: #80cfff; margin-bottom: 4px;")
        lay.addWidget(title)

        grid = QGridLayout()
        self.spins: dict[str, QSpinBox] = {}
        for i, cat in enumerate(self.CATEGORIES):
            lbl = QLabel(cat)
            lbl.setStyleSheet("color: #c8d6e5; font-weight: 600;")
            spin = QSpinBox()
            spin.setRange(0, 10)
            spin.valueChanged.connect(lambda v, c=cat: self._save(c, v))
            grid.addWidget(lbl, i, 0)
            grid.addWidget(spin, i, 1)
            self.spins[cat] = spin
        lay.addLayout(grid)
        lay.addStretch()
        self.refresh()

    def refresh(self) -> None:
        db = self._get_db()
        data = db.get_intrinsics()
        for cat, spin in self.spins.items():
            spin.blockSignals(True)
            spin.setValue(data.get(cat, 0))
            spin.blockSignals(False)

    def _get_db(self) -> DatabaseManager:
        if self._db is None:
            self._db = DatabaseManager()
        return self._db

    def _save(self, category: str, rank: int) -> None:
        self._get_db().set_intrinsic(category, rank)


class _FocusWidget(QWidget):
    """Widget for marking active focus schools and tracking spent focus."""

    SCHOOLS = ["Zenurik", "Naramon", "Unairu", "Madurai", "Vazarin"]
    SCHOOL_COLORS = {
        "Zenurik": "#5aaeff", "Naramon": "#ff8c5a",
        "Unairu":  "#c8b4ff", "Madurai": "#ff5a5a", "Vazarin": "#5affb4",
    }

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._db: DatabaseManager | None = None

        lay = QVBoxLayout(self)
        title = QLabel("Focus Schools")
        title.setStyleSheet("font-size: 14px; font-weight: bold; color: #ffd56b; margin-bottom: 4px;")
        lay.addWidget(title)

        self.checks: dict[str, QCheckBox] = {}
        for school in self.SCHOOLS:
            color = self.SCHOOL_COLORS.get(school, "#ccc")
            cb = QCheckBox(school)
            cb.setStyleSheet(f"color: {color}; font-weight: 600;")
            cb.stateChanged.connect(lambda v, s=school: self._save(s, bool(v)))
            lay.addWidget(cb)
            self.checks[school] = cb
        lay.addStretch()
        self.refresh()

    def refresh(self) -> None:
        db = self._get_db()
        rows = db.get_focus_schools()
        active = {r["school"] for r in rows if r.get("active")}
        for school, cb in self.checks.items():
            cb.blockSignals(True)
            cb.setChecked(school in active)
            cb.blockSignals(False)

    def _get_db(self) -> DatabaseManager:
        if self._db is None:
            self._db = DatabaseManager()
        return self._db

    def _save(self, school: str, active: bool) -> None:
        self._get_db().set_focus_school(school, active)


class CollectionTab(QWidget):
    """Full collection tracker — Warframes, Companions, Archwings, Necramechs,
    Weapons, Mods, Arcanes, Focus Schools, Intrinsics.

    Each collection category has:
    - Search / filter
    - Mark-owned bulk action
    - Inline detail editing (rank, forma, reactor, notes)
    - Owned/total/% progress bar
    """

    def __init__(self) -> None:
        super().__init__()
        self.context = AppContext()
        self.engine = CollectionEngine()
        self.context.event_bus.subscribe("PROFILE_UPDATED", lambda _: self.refresh())

        from src.core.theme_manager import ThemeManager
        theme_colors = ThemeManager().get_theme_colors(ThemeManager().get_active_theme_name())
        accent = theme_colors.get("ACCENT", "#bb86fc")
        primary = theme_colors.get("PRIMARY", "#0c0919")
        secondary = theme_colors.get("SECONDARY", "#130f26")
        card_bg = theme_colors.get("CARD", "#1f183a")
        text_color = theme_colors.get("TEXT", "#eae6f8")
        muted_color = theme_colors.get("MUTED", "#8e85a6")

        root = QVBoxLayout(self)
        root.setSpacing(8)

        # ── header ─────────────────────────────────────────────────────────
        header = QLabel("📦  Collection Tracker")
        header.setStyleSheet(
            f"font-size: 18px; font-weight: bold; color: {accent}; margin-bottom: 2px;"
        )
        root.addWidget(header)

        # ── overall summary bar ────────────────────────────────────────────
        summary_box = QGroupBox("Overall Completion")
        summary_lay = QHBoxLayout(summary_box)

        self.overall_label = QLabel("0%")
        self.overall_label.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {accent}; min-width: 60px;")
        self.overall_bar = QProgressBar()
        self.overall_bar.setStyleSheet(f"""
            QProgressBar {{ background: {secondary}; border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 4px; height: 18px; }}
            QProgressBar::chunk {{ background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 {accent},stop:1 {muted_color}); border-radius: 4px; }}
        """)
        summary_lay.addWidget(self.overall_label)
        summary_lay.addWidget(self.overall_bar, 1)

        # Mini-cards row
        self.mini_cards: dict[str, QLabel] = {}
        for key, color in CATEGORY_COLORS.items():
            card = QLabel(f"{key.title()}\n—/—")
            card.setAlignment(Qt.AlignCenter)
            card.setStyleSheet(f"""
                background-color: {card_bg};
                border: 1px solid {color}88;
                border-radius: 6px;
                color: {color};
                font-size: 10px;
                font-weight: bold;
                padding: 4px 6px;
                min-width: 72px;
            """)
            summary_lay.addWidget(card)
            self.mini_cards[key] = card

        root.addWidget(summary_box)

        # ── tabs ───────────────────────────────────────────────────────────
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(f"""
            QTabWidget::pane {{ border: 1px solid rgba(255, 255, 255, 0.05); background: {secondary}; }}
            QTabBar::tab {{ background: {card_bg}; color: {muted_color}; padding: 6px 14px; border-radius: 4px 4px 0 0; }}
            QTabBar::tab:selected {{ background: {primary}; color: {accent}; font-weight: bold; }}
        """)


        archwing_roster = [
            {"name": w["name"], "acquisition": w.get("acquisition", "")}
            for w in MASTERY_DATA.get("archwings", [
                {"name": "Itzal"}, {"name": "Elytron"},
                {"name": "Odonata"}, {"name": "Odonata Prime"}, {"name": "Amesha"},
            ])
        ]
        necramech_roster = [
            {"name": w["name"], "acquisition": w.get("acquisition", "")}
            for w in MASTERY_DATA.get("necramechs", [
                {"name": "Voidrig"}, {"name": "Bonewidow"},
            ])
        ]

        self._tables: dict[str, _CollectionTableWidget] = {}
        tab_defs = [
            ("warframes",   "warframe_inventory",  "🛸 Warframes",   WARFRAME_ROSTER,    CATEGORY_COLORS["warframes"]),
            ("companions",  "companion_inventory", "🐾 Companions",  COMPANION_ROSTER,   CATEGORY_COLORS["companions"]),
            ("archwings",   "archwing_inventory",  "🚀 Archwings",   archwing_roster,    CATEGORY_COLORS["archwings"]),
            ("necramechs",  "necramech_inventory", "🤖 Necramechs",  necramech_roster,   CATEGORY_COLORS["necramechs"]),
        ]
        for key, db_table, label, roster, color in tab_defs:
            widget = _CollectionTableWidget(key, db_table, roster, color, self)
            self._tables[key] = widget
            self.tabs.addTab(widget, label)

        # Focus + Intrinsics tab (side-by-side)
        special_tab = QWidget()
        special_lay = QHBoxLayout(special_tab)
        self.focus_widget = _FocusWidget(self)
        self.intrinsics_widget = _IntrinsicsWidget(self)
        special_lay.addWidget(self.focus_widget)
        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setStyleSheet("color: #1e2a38;")
        special_lay.addWidget(separator)
        special_lay.addWidget(self.intrinsics_widget)
        self.tabs.addTab(special_tab, "🎯 Focus & Railjack")

        root.addWidget(self.tabs)

        # ── initial load ───────────────────────────────────────────────────
        QTimer.singleShot(0, self.refresh)

    # ── public ─────────────────────────────────────────────────────────────

    def refresh(self) -> None:
        """Reload all collection data from the DB and update the UI."""
        player = PlayerLoader().load_player()
        status = self.engine.get_collection_status(player)

        # Overall bar
        pct = status.get("overall_pct", 0)
        self.overall_label.setText(f"{pct}%")
        self.overall_bar.setValue(int(pct))

        # Mini cards
        for key, card in self.mini_cards.items():
            section = status.get(key, {})
            owned = section.get("owned", section.get("unlocked", 0))
            total = section.get("total", section.get("max_ranks", 1))
            if key == "intrinsics":
                card.setText(f"Intrinsics\n{owned}/{total} XP")
            elif key == "focus":
                card.setText(f"Focus\n{owned}/5 Schools")
            else:
                card.setText(f"{key.title()}\n{owned}/{total}")

        # Populate table widgets from DB
        try:
            db = DatabaseManager()
            table_map = {
                "warframes":  "warframe_inventory",
                "companions": "companion_inventory",
                "archwings":  "archwing_inventory",
                "necramechs": "necramech_inventory",
            }
            for key, db_table in table_map.items():
                if key in self._tables:
                    rows = db.get_collection_table(db_table)
                    self._tables[key].populate(rows)
        except Exception:
            pass

        self.focus_widget.refresh()
        self.intrinsics_widget.refresh()


# Backward-compat alias
network_collection = CollectionTab
