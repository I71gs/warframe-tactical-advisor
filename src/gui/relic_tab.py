from __future__ import annotations
import math
from typing import Any

from PySide6.QtCore import Qt, QTimer, QSortFilterProxyModel
from PySide6.QtGui import QColor, QFont, QStandardItem, QStandardItemModel
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QTableView, QHeaderView, QPushButton, QGroupBox, QSplitter,
    QFrame, QComboBox, QTextEdit, QProgressBar, QAbstractItemView,
    QTabWidget, QGridLayout,
)

from src.core.relic_engine import RelicEngine, RELIC_DATA, REFINEMENT_TRACE_COST, ERA_BEST_NODES
from src.gui.widgets.custom_charts import AnimatedButton

RARITY_COLORS = {
    "Common":    "#7fffb3",
    "Uncommon":  "#7fb3ff",
    "Rare":      "#ffd56b",
    "Legendary": "#caa3ff",
}
ERA_COLORS = {"Lith": "#7fb3ff", "Meso": "#7fffb3", "Neo": "#ffb76b", "Axi": "#caa3ff", "Requiem": "#ff9fd4"}


def _cell(text: str, color: str | None = None, bold: bool = False) -> QStandardItem:
    item = QStandardItem(str(text))
    item.setEditable(False)
    if color:
        item.setForeground(QColor(color))
    if bold:
        f = QFont()
        f.setBold(True)
        item.setFont(f)
    return item


class RelicTab(QWidget):
    """Full Void Relic Planner — search, farming plan, item lookup, and multi-item planner."""

    def __init__(self) -> None:
        super().__init__()
        self.engine = RelicEngine()
        self._setup_ui()
        QTimer.singleShot(0, self._load_all_relics)

    # ── UI construction ───────────────────────────────────────────────────────

    def _setup_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setSpacing(6)

        header = QLabel("🔮  Void Relic Planner")
        header.setStyleSheet("font-size: 18px; font-weight: bold; color: #caa3ff; margin-bottom: 2px;")
        root.addWidget(header)

        self.sub_tabs = QTabWidget()
        self.sub_tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #1e2a38; background: #0d1117; }
            QTabBar::tab { background: #0f1a24; color: #7a8fa6; padding: 6px 14px; border-radius: 4px 4px 0 0; }
            QTabBar::tab:selected { background: #12263a; color: #caa3ff; font-weight: bold; }
        """)
        root.addWidget(self.sub_tabs)

        self.sub_tabs.addTab(self._build_search_tab(), "🔍 Relic Browser")
        self.sub_tabs.addTab(self._build_item_lookup_tab(), "🎯 Farm Item")
        self.sub_tabs.addTab(self._build_multi_planner_tab(), "📋 Multi-Item Planner")

    def _build_search_tab(self) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)

        toolbar = QHBoxLayout()
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("🔍  Search by item name, relic name, era…")
        self.search_box.textChanged.connect(self._filter_relics)
        toolbar.addWidget(self.search_box)
        lay.addLayout(toolbar)

        # Era filter chips
        chips_lay = QHBoxLayout()
        chips_lay.setSpacing(8)
        chips_lbl = QLabel("Era Filters:")
        chips_lbl.setStyleSheet("font-size: 11px; font-weight: bold; color: rgba(255, 255, 255, 0.4);")
        chips_lay.addWidget(chips_lbl)

        self.chip_all = AnimatedButton("All")
        self.chip_all.setCheckable(True)
        self.chip_all.setChecked(True)

        self.chip_lith = AnimatedButton("Lith")
        self.chip_lith.setCheckable(True)

        self.chip_meso = AnimatedButton("Meso")
        self.chip_meso.setCheckable(True)

        self.chip_neo = AnimatedButton("Neo")
        self.chip_neo.setCheckable(True)

        self.chip_axi = AnimatedButton("Axi")
        self.chip_axi.setCheckable(True)

        self.chip_requiem = AnimatedButton("Requiem")
        self.chip_requiem.setCheckable(True)

        # Style era chips
        chip_style = """
            QPushButton {
                background-color: #0f1a24;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 12px;
                color: #e6eef6;
                padding: 4px 12px;
                font-size: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.05);
            }
            QPushButton:checked {
                background-color: #caa3ff;
                border-color: #caa3ff;
                color: #000000;
            }
        """

        for chip in (self.chip_all, self.chip_lith, self.chip_meso, self.chip_neo, self.chip_axi, self.chip_requiem):
            chip.setStyleSheet(chip_style)
            chips_lay.addWidget(chip)

        self.chip_all.clicked.connect(self._on_all_chip_clicked)
        self.chip_lith.clicked.connect(self._on_era_chip_clicked)
        self.chip_meso.clicked.connect(self._on_era_chip_clicked)
        self.chip_neo.clicked.connect(self._on_era_chip_clicked)
        self.chip_axi.clicked.connect(self._on_era_chip_clicked)
        self.chip_requiem.clicked.connect(self._on_era_chip_clicked)

        chips_lay.addStretch()
        lay.addLayout(chips_lay)

        # Load persistent relic filters
        from src.core.settings_manager import SettingsManager
        settings = SettingsManager()
        saved = settings.get("relic_filters", {})
        if isinstance(saved, dict) and saved:
            self.chip_all.setChecked(saved.get("all", True))
            self.chip_lith.setChecked(saved.get("lith", False))
            self.chip_meso.setChecked(saved.get("meso", False))
            self.chip_neo.setChecked(saved.get("neo", False))
            self.chip_axi.setChecked(saved.get("axi", False))
            self.chip_requiem.setChecked(saved.get("requiem", False))
        else:
            self.chip_all.setChecked(True)

        # Relic table
        cols = ["Era", "Relic Name", "Rewards (top 3)", "Best Farm Node"]
        self.relic_model = QStandardItemModel(0, len(cols))
        self.relic_model.setHorizontalHeaderLabels(cols)
        self.relic_proxy = QSortFilterProxyModel()
        self.relic_proxy.setSourceModel(self.relic_model)
        self.relic_proxy.setFilterCaseSensitivity(Qt.CaseInsensitive)

        self.relic_table = QTableView()
        self.relic_table.setModel(self.relic_proxy)
        self.relic_table.setSortingEnabled(True)
        self.relic_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.relic_table.horizontalHeader().setStretchLastSection(True)
        self.relic_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.relic_table.verticalHeader().setVisible(False)
        self.relic_table.setAlternatingRowColors(True)
        self.relic_table.setStyleSheet(self._table_style("#caa3ff"))
        lay.addWidget(self.relic_table)

        # Detail box
        detail_box = QGroupBox("Selected Relic — Full Drop Table")
        detail_box.setStyleSheet("QGroupBox { color: #caa3ff; border: 1px solid #2a1e4a; border-radius:6px; margin-top:8px; }")
        detail_lay = QVBoxLayout(detail_box)
        self.relic_detail = QTextEdit()
        self.relic_detail.setReadOnly(True)
        self.relic_detail.setMaximumHeight(120)
        self.relic_detail.setStyleSheet("background:#0d1117; color:#c8d6e5; border:none; font-size:11px;")
        detail_lay.addWidget(self.relic_detail)
        lay.addWidget(detail_box)

        self.relic_table.selectionModel().selectionChanged.connect(self._show_relic_detail)
        return w

    def _build_item_lookup_tab(self) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)

        # Search row
        sr = QHBoxLayout()
        self.item_search = QLineEdit()
        self.item_search.setPlaceholderText("Enter prime item name, e.g. 'Saryn Prime Blueprint'")
        sr.addWidget(self.item_search)
        search_btn = QPushButton("🔎 Find Relics")
        search_btn.setStyleSheet(self._btn_style("#caa3ff"))
        search_btn.clicked.connect(self._search_item)
        sr.addWidget(search_btn)
        lay.addLayout(sr)

        # Plan result box
        self.plan_box = QGroupBox("Farming Plan")
        self.plan_box.setStyleSheet("QGroupBox { color: #ffd56b; border: 1px solid #3a2e00; border-radius:6px; margin-top:8px;}")
        plan_lay = QVBoxLayout(self.plan_box)
        self.plan_text = QTextEdit()
        self.plan_text.setReadOnly(True)
        self.plan_text.setStyleSheet("background:#0d1117; color:#c8d6e5; border:none; font-size:12px;")
        plan_lay.addWidget(self.plan_text)
        lay.addWidget(self.plan_box)

        # Item relics table
        cols = ["Era", "Relic", "Rarity", "Drop% Intact", "Drop% Radiant", "Farm Node"]
        self.item_model = QStandardItemModel(0, len(cols))
        self.item_model.setHorizontalHeaderLabels(cols)
        self.item_table = QTableView()
        self.item_table.setModel(self.item_model)
        self.item_table.horizontalHeader().setStretchLastSection(True)
        self.item_table.verticalHeader().setVisible(False)
        self.item_table.setAlternatingRowColors(True)
        self.item_table.setStyleSheet(self._table_style("#ffd56b"))
        lay.addWidget(self.item_table)
        return w

    def _build_multi_planner_tab(self) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)

        intro = QLabel("Enter multiple prime item names (one per line) to plan all farming simultaneously:")
        intro.setStyleSheet("color: #7a8fa6; font-size: 11px;")
        lay.addWidget(intro)

        edit_row = QHBoxLayout()
        self.multi_input = QTextEdit()
        self.multi_input.setPlaceholderText("Saryn Prime Blueprint\nWisp Prime Systems\nMesa Prime Neuroptics\n…")
        self.multi_input.setMaximumHeight(120)
        edit_row.addWidget(self.multi_input, 1)

        side = QVBoxLayout()
        plan_btn = QPushButton("📋 Plan All")
        plan_btn.setStyleSheet(self._btn_style("#7fffb3"))
        plan_btn.clicked.connect(self._plan_multi)
        clear_btn = QPushButton("🗑 Clear")
        clear_btn.setStyleSheet(self._btn_style("#ff9fd4"))
        clear_btn.clicked.connect(self.multi_input.clear)
        side.addWidget(plan_btn)
        side.addWidget(clear_btn)
        side.addStretch()
        edit_row.addLayout(side)
        lay.addLayout(edit_row)

        cols = ["Item", "Era", "Relic", "Rarity", "Refinement", "Est. Runs", "Traces", "Farm Node"]
        self.multi_model = QStandardItemModel(0, len(cols))
        self.multi_model.setHorizontalHeaderLabels(cols)
        self.multi_table = QTableView()
        self.multi_table.setModel(self.multi_model)
        self.multi_table.horizontalHeader().setStretchLastSection(True)
        self.multi_table.verticalHeader().setVisible(False)
        self.multi_table.setAlternatingRowColors(True)
        self.multi_table.setStyleSheet(self._table_style("#7fffb3"))
        lay.addWidget(self.multi_table)

        # Summary bar
        self.multi_summary = QLabel("Total estimated runs: — | Total traces: —")
        self.multi_summary.setStyleSheet("color: #ffd56b; font-weight: bold; font-size: 11px;")
        lay.addWidget(self.multi_summary)
        return w

    # ── data loading ──────────────────────────────────────────────────────────

    def _load_all_relics(self) -> None:
        self._filter_relics()

    def _on_all_chip_clicked(self) -> None:
        if self.chip_all.isChecked():
            self.chip_lith.setChecked(False)
            self.chip_meso.setChecked(False)
            self.chip_neo.setChecked(False)
            self.chip_axi.setChecked(False)
            self.chip_requiem.setChecked(False)
        else:
            self.chip_all.setChecked(True)
        self._save_relic_filters()
        self._filter_relics()

    def _on_era_chip_clicked(self) -> None:
        any_checked = (self.chip_lith.isChecked() or self.chip_meso.isChecked() or 
                       self.chip_neo.isChecked() or self.chip_axi.isChecked() or 
                       self.chip_requiem.isChecked())
        if any_checked:
            self.chip_all.setChecked(False)
        else:
            self.chip_all.setChecked(True)
        self._save_relic_filters()
        self._filter_relics()

    def _save_relic_filters(self) -> None:
        from src.core.settings_manager import SettingsManager
        settings = SettingsManager()
        settings.update(**{
            "relic_filters": {
                "all": self.chip_all.isChecked(),
                "lith": self.chip_lith.isChecked(),
                "meso": self.chip_meso.isChecked(),
                "neo": self.chip_neo.isChecked(),
                "axi": self.chip_axi.isChecked(),
                "requiem": self.chip_requiem.isChecked(),
            }
        })
        settings.save()

    def _filter_relics(self) -> None:
        text = self.search_box.text().strip().lower()
        
        active_eras = []
        if self.chip_lith.isChecked(): active_eras.append("Lith")
        if self.chip_meso.isChecked(): active_eras.append("Meso")
        if self.chip_neo.isChecked(): active_eras.append("Neo")
        if self.chip_axi.isChecked(): active_eras.append("Axi")
        if self.chip_requiem.isChecked(): active_eras.append("Requiem")
        
        show_all_eras = self.chip_all.isChecked() or not active_eras
        
        self.relic_model.setRowCount(0)
        for relic in RELIC_DATA:
            era = relic.get("era", "")
            if not show_all_eras and era not in active_eras:
                continue
            name = relic.get("relic_name", "")
            rewards = relic.get("rewards", [])
            reward_text = " ".join(r["item"] for r in rewards).lower()
            full_text = f"{era} {name} {reward_text}".lower()
            if text and text not in full_text:
                continue
            farm = relic.get("best_farm_node", ERA_BEST_NODES.get(era, ""))
            rewards_preview = ", ".join(f"{r['item']} ({r['rarity']})" for r in rewards[:3])
            era_color = ERA_COLORS.get(era, "#c8d6e5")
            self.relic_model.appendRow([
                _cell(era, era_color, bold=True),
                _cell(name, "#caa3ff"),
                _cell(rewards_preview),
                _cell(farm, "#7a8fa6"),
            ])

    def _show_relic_detail(self) -> None:
        sel = self.relic_table.selectionModel().selectedRows()
        if not sel:
            return
        src_row = self.relic_proxy.mapToSource(sel[0]).row()
        era_item = self.relic_model.item(src_row, 0)
        name_item = self.relic_model.item(src_row, 1)
        if not (era_item and name_item):
            return
        era = era_item.text()
        name = name_item.text()
        relic = next(
            (r for r in RELIC_DATA if r.get("era") == era and r.get("relic_name") == name), None
        )
        if not relic:
            return
        lines = [f"{'Relic:':<18}{era} {name}", f"{'Best Node:':<18}{relic.get('best_farm_node', '—')}", "", "Rewards:"]
        for r in relic.get("rewards", []):
            rarity = r.get("rarity", "?")
            color_hint = {"Common": "✦", "Uncommon": "✧", "Rare": "★", "Legendary": "✮"}.get(rarity, "•")
            lines.append(f"  {color_hint} {r['item']:<40} {rarity:<12} {r.get('drop_chance_radiant', 0):.1f}% (Radiant)")
        self.relic_detail.setPlainText("\n".join(lines))

    def _search_item(self) -> None:
        query = self.item_search.text().strip()
        if not query:
            return
        plan = self.engine.plan_farming(query)
        all_relics = self.engine.get_relics_for_item(query)

        if not plan["found"]:
            self.plan_text.setPlainText(plan.get("message", "Item not found."))
            self.item_model.setRowCount(0)
            return

        lines = [
            f"Item:            {plan['item']}",
            f"Best Relic:      {plan['era']} {plan['relic_name']}",
            f"Rarity:          {plan['rarity']}",
            f"Recommendation:  Refine to {plan['recommended_refinement']}",
            f"Drop Chance:     {plan['drop_chance_pct']:.1f}%",
            f"Expected Runs:   ≈ {plan['expected_runs']}",
            f"Traces Needed:   {plan['traces_needed']}",
            f"Best Farm Node:  {plan['best_farm_node']}",
            "",
            f"💡 {plan.get('tip', '')}",
        ]
        if plan.get("alternative_relics"):
            lines.append(f"\nAlternative relics: {', '.join(plan['alternative_relics'])}")
        self.plan_text.setPlainText("\n".join(lines))

        # Populate table
        self.item_model.setRowCount(0)
        for entry in all_relics:
            rarity = entry.get("rarity", "")
            rarity_color = RARITY_COLORS.get(rarity.split()[0] if rarity else "", "#c8d6e5")
            self.item_model.appendRow([
                _cell(entry.get("era", ""), ERA_COLORS.get(entry.get("era",""), "#c8d6e5")),
                _cell(entry.get("relic_name", ""), "#caa3ff"),
                _cell(rarity, rarity_color, bold=(rarity == "Rare")),
                _cell(f"{entry.get('drop_chance_intact', 0):.1f}%"),
                _cell(f"{entry.get('drop_chance_radiant', 0):.1f}%", "#ffd56b"),
                _cell(entry.get("best_farm_node", ""), "#7a8fa6"),
            ])

    def _plan_multi(self) -> None:
        text = self.multi_input.toPlainText()
        items = [line.strip() for line in text.splitlines() if line.strip()]
        if not items:
            return
        plans = self.engine.plan_farming_multi(items)
        self.multi_model.setRowCount(0)
        total_runs = 0
        total_traces = 0
        for p in plans:
            if p.get("found"):
                runs = p.get("expected_runs", 0)
                traces = p.get("traces_needed", 0)
                total_runs += runs
                total_traces += traces
                rarity = p.get("rarity", "")
                rarity_color = RARITY_COLORS.get(rarity.split()[0] if rarity else "", "#c8d6e5")
                self.multi_model.appendRow([
                    _cell(p["item"], "#c8d6e5"),
                    _cell(p.get("era", ""), ERA_COLORS.get(p.get("era",""), "#ccc")),
                    _cell(p.get("relic_name", ""), "#caa3ff"),
                    _cell(rarity, rarity_color),
                    _cell(p.get("recommended_refinement", ""), "#ffd56b"),
                    _cell(str(runs), "#ff9fd4" if runs > 10 else "#7fffb3", bold=True),
                    _cell(str(traces)),
                    _cell(p.get("best_farm_node", ""), "#7a8fa6"),
                ])
            else:
                self.multi_model.appendRow([
                    _cell(items[plans.index(p)] if p in plans else "?", "#ef4444"),
                    _cell("NOT FOUND", "#ef4444"),
                    *[_cell("—") for _ in range(6)],
                ])
        self.multi_summary.setText(
            f"Total estimated runs: {total_runs} | Total traces: {total_traces:,}"
        )

    # ── static helpers ────────────────────────────────────────────────────────

    @staticmethod
    def _table_style(accent: str) -> str:
        return f"""
            QTableView {{
                background: #0d1117; alternate-background-color: #12181f;
                gridline-color: #1e2a38; color: #c8d6e5;
                border: 1px solid #1e2a38; border-radius: 4px;
            }}
            QHeaderView::section {{
                background: #0f1a24; color: {accent};
                font-weight: bold; border: none; padding: 4px;
            }}
        """

    @staticmethod
    def _btn_style(color: str) -> str:
        return f"""
            QPushButton {{
                background: #0f1a24; border: 1px solid {color};
                border-radius: 4px; color: {color}; font-weight: bold; padding: 6px 14px;
            }}
            QPushButton:hover {{ background: {color}22; }}
        """
