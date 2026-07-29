from __future__ import annotations
from typing import Any
import webbrowser
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QListWidget,
    QListWidgetItem, QMessageBox, QPushButton, QGroupBox, QSplitter,
    QStackedWidget, QScrollArea
)
from PySide6.QtCore import Qt, QTimer
from src.core.search_engine_v3 import SearchEngineV3
from src.database.database import DatabaseManager

class SearchTab(QWidget):
    """GUI tab providing global search with fuzzy suggestions, history tracker, and favorites bookmarks."""

    def __init__(self) -> None:
        super().__init__()
        from src.core.app_context import AppContext
        self.engine = SearchEngineV3(AppContext())
        self.db = DatabaseManager()
        self.results_map = {}

        # Retrieve active theme colors
        from src.core.theme_manager import ThemeManager
        colors = ThemeManager().get_theme_colors(ThemeManager().get_active_theme_name())
        self.accent = colors.get("ACCENT", "#00a3cc")
        self.primary = colors.get("PRIMARY", "#0b1220")
        self.secondary = colors.get("SECONDARY", "#0f1724")
        self.card_bg = colors.get("CARD", "#0f1a24")
        self.text_color = colors.get("TEXT", "#e6eef6")
        self.muted = colors.get("MUTED", "#9fb6c8")

        self.setStyleSheet(f"""
            QWidget {{
                color: {self.text_color};
            }}
            QListWidget {{
                background-color: {self.secondary};
                border: 1px solid rgba(255, 255, 255, 0.05);
                border-radius: 6px;
                color: {self.text_color};
                padding: 6px;
            }}
            QListWidget::item {{
                padding: 8px;
                border-bottom: 1px solid rgba(255, 255, 255, 0.02);
            }}
            QListWidget::item:hover {{
                background-color: rgba(255, 255, 255, 0.03);
                border-radius: 4px;
            }}
            QListWidget::item:selected {{
                background-color: rgba(0, 163, 204, 0.15);
                color: {self.accent};
                border-radius: 4px;
            }}
            QLineEdit {{
                background-color: {self.secondary};
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 6px;
                color: {self.text_color};
                padding: 10px;
                font-size: 13px;
            }}
            QLineEdit:focus {{
                border-color: {self.accent};
            }}
            QGroupBox {{
                background-color: {self.card_bg};
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 8px;
                margin-top: 10px;
                color: {self.accent};
                font-weight: bold;
                font-size: 12px;
            }}
            QPushButton {{
                background-color: {self.card_bg};
                border: 1px solid {self.accent};
                border-radius: 4px;
                color: {self.accent};
                font-weight: bold;
                padding: 8px 16px;
                font-size: 11px;
            }}
            QPushButton:hover {{
                background-color: rgba(255, 255, 255, 0.05);
            }}
        """)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(16, 16, 16, 16)

        # Header
        header = QLabel("🔍  Global Database Search")
        header.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {self.accent}; margin-bottom: 5px;")
        self.layout.addWidget(header)

        # Search box
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search weapons, Warframes, relics, mods, companions, resources, missions…")
        self.search_input.textChanged.connect(self.run_search)
        self.layout.addWidget(self.search_input)

        # Splitter to show results & stack panel
        splitter = QSplitter(Qt.Horizontal)

        # Left Column: Search Results
        results_box = QGroupBox("Search Results")
        results_lay = QVBoxLayout(results_box)
        self.results_list = QListWidget()
        self.results_list.itemDoubleClicked.connect(self.on_item_double_clicked)
        self.results_list.currentItemChanged.connect(self.on_current_item_changed)
        results_lay.addWidget(self.results_list)

        # Quick action row for bookmarks
        btn_row = QHBoxLayout()
        self.bookmark_btn = QPushButton("★ Bookmark Selected")
        self.bookmark_btn.clicked.connect(self.toggle_bookmark)
        btn_row.addWidget(self.bookmark_btn)
        
        self.clear_hist_btn = QPushButton("🗑 Clear History")
        self.clear_hist_btn.clicked.connect(self.clear_history)
        btn_row.addWidget(self.clear_hist_btn)
        results_lay.addLayout(btn_row)
        splitter.addWidget(results_box)

        # Right Column: QStackedWidget switching between Bookmarks/History & Rich Preview
        self.right_stack = QStackedWidget()
        
        # ── Page 0: Bookmarks & History panels ──
        self.default_right_panel = QWidget()
        default_right_lay = QVBoxLayout(self.default_right_panel)
        default_right_lay.setContentsMargins(0, 0, 0, 0)

        # Bookmarks list
        bookmarks_group = QGroupBox("Favorites & Bookmarks")
        bookmarks_lay = QVBoxLayout(bookmarks_group)
        self.bookmarks_list = QListWidget()
        self.bookmarks_list.itemDoubleClicked.connect(self.on_bookmark_double_clicked)
        bookmarks_lay.addWidget(self.bookmarks_list)
        default_right_lay.addWidget(bookmarks_group, 1)

        # History list
        history_group = QGroupBox("Search History")
        history_lay = QVBoxLayout(history_group)
        self.history_list = QListWidget()
        self.history_list.itemClicked.connect(self.on_history_clicked)
        history_lay.addWidget(self.history_list)
        default_right_lay.addWidget(history_group, 1)
        
        self.right_stack.addWidget(self.default_right_panel)

        # ── Page 1: Scrollable Rich Preview Panel ──
        self.preview_panel = QWidget()
        self.preview_lay = QVBoxLayout(self.preview_panel)
        self.preview_lay.setContentsMargins(0, 10, 0, 0)

        # Preview Header (Title & Category)
        header_lay = QHBoxLayout()
        self.preview_title = QLabel("Select an Item")
        self.preview_title.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {self.accent};")
        self.preview_category = QLabel("")
        self.preview_category.setStyleSheet(f"font-size: 10px; font-weight: bold; color: {self.muted}; background-color: {self.secondary}; border-radius: 4px; padding: 3px 8px; text-transform: uppercase;")
        header_lay.addWidget(self.preview_title)
        header_lay.addWidget(self.preview_category)
        header_lay.addStretch()
        self.preview_lay.addLayout(header_lay)

        # Scroll Area for Preview sections
        preview_scroll = QScrollArea()
        preview_scroll.setWidgetResizable(True)
        preview_scroll.setStyleSheet("background: transparent; border: none;")
        
        scroll_content = QWidget()
        self.scroll_lay = QVBoxLayout(scroll_content)
        self.scroll_lay.setSpacing(10)
        self.scroll_lay.setContentsMargins(0, 0, 0, 0)

        # Preview Details Sections
        self.sect_ownership = QLabel("N/A")
        self.sect_ownership.setWordWrap(True)
        self.sect_mr = QLabel("N/A")
        self.sect_acquisition = QLabel("N/A")
        self.sect_acquisition.setWordWrap(True)
        self.sect_crafting = QLabel("N/A")
        self.sect_crafting.setWordWrap(True)
        self.sect_builds = QLabel("N/A")
        self.sect_builds.setWordWrap(True)
        self.sect_progress = QLabel("N/A")
        self.sect_related = QLabel("N/A")
        self.sect_related.setWordWrap(True)

        self.scroll_lay.addWidget(self._make_section_box("Ownership Status", self.sect_ownership))
        self.scroll_lay.addWidget(self._make_section_box("Mastery Rank Requirement", self.sect_mr))
        self.scroll_lay.addWidget(self._make_section_box("Acquisition Methods & Farming Locations", self.sect_acquisition))
        self.scroll_lay.addWidget(self._make_section_box("Crafting Requirements", self.sect_crafting))
        self.scroll_lay.addWidget(self._make_section_box("Build Recommendations", self.sect_builds))
        self.scroll_lay.addWidget(self._make_section_box("Progress Toward Obtaining", self.sect_progress))
        self.scroll_lay.addWidget(self._make_section_box("Related Items & Recommendations", self.sect_related))
        self.scroll_lay.addStretch()

        preview_scroll.setWidget(scroll_content)
        self.preview_lay.addWidget(preview_scroll)
        self.right_stack.addWidget(self.preview_panel)

        splitter.addWidget(self.right_stack)
        self.layout.addWidget(splitter)

        self.setLayout(self.layout)
        QTimer.singleShot(0, self.load_history_and_bookmarks)

    def _make_section_box(self, title: str, label: QLabel) -> QGroupBox:
        box = QGroupBox(title)
        box.setStyleSheet(f"""
            QGroupBox {{
                background-color: {self.card_bg};
                border: 1px solid rgba(255, 255, 255, 0.05);
                border-radius: 6px;
                margin-top: 6px;
                padding: 10px;
                color: {self.accent};
                font-weight: bold;
                font-size: 11px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 8px;
                color: {self.accent};
            }}
            QLabel {{
                color: {self.text_color};
                font-size: 12px;
                font-weight: normal;
            }}
        """)
        lay = QVBoxLayout(box)
        lay.setContentsMargins(8, 14, 8, 8)
        lay.addWidget(label)
        return box

    def load_history_and_bookmarks(self) -> None:
        self.history_list.clear()
        hist = self.db.get_search_history(limit=15)
        for h in hist:
            self.history_list.addItem(h)

        self.bookmarks_list.clear()
        bookmarks = self.engine.get_bookmarks()
        for b in sorted(list(bookmarks)):
            self.bookmarks_list.addItem(b.title())

    def run_search(self) -> None:
        self.results_list.clear()
        self.results_map.clear()
        
        query = self.search_input.text().strip()
        if not query:
            self.right_stack.setCurrentIndex(0)
            self.load_history_and_bookmarks()
            return
            
        results = self.engine.search(query)
        self.right_stack.setCurrentIndex(1)
        
        if not results:
            self.results_list.addItem("No results found.")
            self.preview_title.setText("No Matches")
            self.preview_category.setText("")
            self.sect_ownership.setText("Search matches no records.")
            self.sect_mr.setText("N/A")
            self.sect_acquisition.setText("N/A")
            self.sect_crafting.setText("N/A")
            self.sect_builds.setText("N/A")
            self.sect_progress.setText("N/A")
            self.sect_related.setText("N/A")
            return
            
        for r in results:
            star = "★ " if r.get("bookmarked") else "☆ "
            text = f"{star}[{r['category']}] {r['name']} - {r['details']}"
            item = QListWidgetItem(text)
            self.results_list.addItem(item)
            self.results_map[id(item)] = r

        # Auto-highlight the first result
        self.results_list.setCurrentRow(0)

    def on_current_item_changed(self, current: QListWidgetItem, previous: QListWidgetItem) -> None:
        if not current:
            return
            
        data = self.results_map.get(id(current))
        if not data:
            return
            
        # Get dynamic preview data
        rich = self.get_rich_preview_data(data)
        
        self.preview_title.setText(rich["name"])
        self.preview_category.setText(rich["category"])
        
        own_style = "<span style='color:#22c55e; font-weight:bold;'>✓ Owned</span>" if rich["owned"] else "<span style='color:#ef4444; font-weight:bold;'>✗ Not Owned</span>"
        own_det = f"<br/><span style='font-size:11px; color:{self.muted};'>{rich['ownership_details']}</span>" if rich["ownership_details"] else ""
        self.sect_ownership.setText(f"<html>{own_style}{own_det}</html>")
        
        self.sect_mr.setText(rich["mr_required"])
        self.sect_acquisition.setText(rich["acquisition"])
        self.sect_crafting.setText(rich["crafting"])
        self.sect_builds.setText(rich["builds"])
        self.sect_progress.setText(rich["progress"])
        self.sect_related.setText(rich["related"])

    def get_rich_preview_data(self, item: dict) -> dict:
        name = item["name"]
        category = item["category"]
        raw = item.get("raw_data", {})
        
        # Load player profile and DB connection
        from src.core.player_loader import PlayerLoader
        player = PlayerLoader().load_player()
        
        from src.database.database import DatabaseManager
        db = DatabaseManager()
        
        details = {
            "name": name,
            "category": category,
            "owned": False,
            "ownership_details": "",
            "mr_required": "N/A",
            "acquisition": "Unknown Source",
            "crafting": "N/A",
            "builds": "No recommended builds cataloged.",
            "progress": "0%",
            "related": "No related roadmap recommendations."
        }
        
        if category == "WEAPON":
            details["owned"] = name.lower() in [w.lower() for w in player.owned_weapons]
            details["mr_required"] = f"Mastery Rank {raw.get('mastery_required', 10)}"
            details["acquisition"] = raw.get("acquisition", "Acquired from market blueprint or drops.")
            
            # Crafting components
            if "prime" in name.lower():
                details["crafting"] = f"{name} Blueprint, {name} Barrel, {name} Receiver, {name} Stock"
            elif "phenmor" in name.lower():
                details["crafting"] = "Phenmor Blueprint, 2 Voidgel Orbs, 5 Entrati Lanthorns, 10 Thrax Plasm"
            elif "laetum" in name.lower():
                details["crafting"] = "Laetum Blueprint, 2 Voidgel Orbs, 5 Entrati Lanthorns, 10 Thrax Plasm"
            elif "epitaph" in name.lower():
                details["crafting"] = "Epitaph Blueprint, Epitaph Barrel, Epitaph Receiver"
            else:
                details["crafting"] = f"{name} Blueprint, raw materials (Orphix/Fissures/Dojo)."
                
            # Inventory detail
            inv = db.get_weapon_inventory()
            matched = next((w for w in inv if w["weapon_name"].lower() == name.lower()), None)
            if matched:
                details["ownership_details"] = f"Rank {matched.get('rank', 30)} | {matched.get('forma_count', 0)} Forma | Catalyst: {'Installed' if matched.get('has_catalyst') else 'None'}"
                
            # Builds
            from src.core.build_database import BUILDS
            b = next((x for x in BUILDS if x.get("weapon", "").lower() == name.lower()), None)
            if b:
                details["builds"] = f"Rating: {b.get('rating')}% | Element: {b.get('element')} | Mods: {', '.join(b.get('mods', []))}"
            else:
                details["builds"] = "Recommended: Galvanized Chamber, Critical Delay, Vital Sense, Hunter Munitions (Viral/Slash)."
                
            # Progress
            if details["owned"]:
                details["progress"] = "100% (Owned)"
            else:
                mr_req = raw.get('mastery_required', 10)
                if player.mastery_rank >= mr_req:
                    details["progress"] = "50% (MR requirement met. Blueprints farmable)"
                else:
                    details["progress"] = f"{int(player.mastery_rank / mr_req * 100)}% (MR unmet: {player.mastery_rank}/{mr_req})"
                    
            details["related"] = f"Farming routes exist for related weapon parts. Check Farming tab."
            
        elif category == "WARFRAME":
            details["owned"] = name.lower() in [f.lower() for f in player.owned_warframes]
            details["acquisition"] = raw.get("acquisition", "Drops from Assassination nodes or Void Fissures.")
            details["mr_required"] = "Mastery Rank 0 (Standard Warframe)"
            details["crafting"] = f"{name} Blueprint, {name} Neuroptics, {name} Chassis, {name} Systems"
            
            matched = next((f for f in player.warframe_inventory if f["name"].lower() == name.lower()), None)
            if matched and matched.get("owned"):
                details["ownership_details"] = f"Rank {matched.get('rank', 30)} | {matched.get('forma_count', 0)} Forma | Reactor: {'Installed' if matched.get('has_reactor') else 'None'}"
                
            details["builds"] = raw.get("builds", "Upgrade Strength/Duration. Subsume ability: " + raw.get("subsumed", "None"))
            details["progress"] = "100% (Owned)" if details["owned"] else "0% (Not Owned)"
            details["related"] = f"Requires: {raw.get('dependencies', 'Star Chart unlocked')}"
            
        elif category == "MOD":
            details["owned"] = name.lower() in [m.lower() for m in player.owned_mods]
            details["acquisition"] = raw.get("source", "Drops from Arbitration honors vendor or Orokin Vaults.")
            details["crafting"] = "Fuse with Endo and Credits to upgrade rank."
            
            inv = db.get_mod_inventory()
            matched = next((m for m in inv if m["mod_name"].lower() == name.lower()), None)
            if matched:
                details["ownership_details"] = f"Current Rank: {matched.get('rank', 0)} / {matched.get('max_rank', 10)}"
                
            details["builds"] = f"Importance: {raw.get('importance', 80)}/100. Core mod slot priority."
            details["progress"] = "100% (Owned)" if details["owned"] else "0% (Not Owned)"
            details["related"] = "Unlocked by completing Arbitrations."
            
        elif category == "ARCANE":
            details["owned"] = name.lower() in [a.lower() for a in player.owned_arcanes]
            details["acquisition"] = raw.get("acquisition", "Drops from Steel Path Acolytes / Eidolon Hunts / Orphix.")
            details["crafting"] = "Rank up by combining duplicate arcanes (up to Rank 5)."
            details["builds"] = f"Importance: {raw.get('importance', 80)}. Recommended for ultimate build configurations."
            details["progress"] = "100% (Owned)" if details["owned"] else "0% (Not Owned)"
            details["related"] = "Acquire Primary Merciless / Arcane Energize for build multipliers."
            
        elif category == "RELIC":
            details["acquisition"] = f"Best farm node: {raw.get('best_farm_node', 'Void Fissures')}"
            details["crafting"] = "Refine with Void Traces (Radiant tier gives +10% Rare drop chance)."
            rewards = [rw["item"] for rw in raw.get("rewards", [])]
            details["builds"] = f"Drops: {', '.join(rewards)}"
            details["progress"] = "Farmable via Relic Browser or Fissure missions."
            details["related"] = "Run Void Fissure missions to unlock and acquire components."
            
        elif category == "COMPANION":
            details["owned"] = name.lower() in [c.lower() for c in player.owned_companions]
            details["acquisition"] = f"Utility: {raw.get('utility', 'Companion support')}"
            details["crafting"] = f"Synergy: {raw.get('synergy', 'Generic loadout')}"
            details["builds"] = raw.get("rationale", "Use standard utility companion configurations.")
            details["progress"] = "100% (Owned)" if details["owned"] else "0% (Not Owned)"
            details["related"] = "Verify companion incubator modules are installed."
            
        else:
            details["acquisition"] = item.get("details", "")
            details["builds"] = "General progression item or game system node."
            details["progress"] = "Check the Progression tab for specific milestone goals."
            
        return details

    def on_item_double_clicked(self, item: QListWidgetItem) -> None:
        data = self.results_map.get(id(item))
        if not data:
            return
        self._show_details(data)

    def on_bookmark_double_clicked(self, item: QListWidgetItem) -> None:
        name = item.text().lower()
        res = self.engine.search(name)
        if res:
            self._show_details(res[0])

    def on_history_clicked(self, item: QListWidgetItem) -> None:
        self.search_input.setText(item.text())

    def toggle_bookmark(self) -> None:
        item = self.results_list.currentItem()
        if not item:
            return
        data = self.results_map.get(id(item))
        if not data:
            return
        
        name = data["name"]
        bookmarks = self.engine.get_bookmarks()
        if name.lower() in bookmarks:
            self.engine.remove_bookmark(name)
            QMessageBox.information(self, "Bookmark Removed", f"Removed '{name}' from favorites.")
        else:
            self.engine.add_bookmark(name)
            QMessageBox.information(self, "Bookmark Added", f"Added '{name}' to favorites.")

        self.run_search()
        self.load_history_and_bookmarks()

    def clear_history(self) -> None:
        self.db.clear_search_history()
        self.load_history_and_bookmarks()
        QMessageBox.information(self, "History Cleared", "Search history cleared.")

    def _show_details(self, data: dict) -> None:
        wiki_info = f"\n\nWiki URL:\n{data['wiki_url']}" if data.get('wiki_url') else ""
        QMessageBox.information(
            self,
            f"{data['category']}: {data['name']}",
            f"Name: {data['name']}\n"
            f"Category: {data['category']}\n"
            f"Details: {data['details']}{wiki_info}"
        )

    def keyPressEvent(self, event: Any) -> None:
        # If user presses Return/Enter, trigger quick action (open Wiki URL)
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            item = self.results_list.currentItem()
            if item:
                data = self.results_map.get(id(item))
                if data and data.get("wiki_url"):
                    webbrowser.open(data["wiki_url"])
                    event.accept()
                    return
        super().keyPressEvent(event)
