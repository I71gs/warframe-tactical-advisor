from __future__ import annotations
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QListWidget, QListWidgetItem, QGroupBox, QTextBrowser
from src.core.player_loader import PlayerLoader
from src.core.route_engine import RouteEngine

class RouteTab(QWidget):
    """GUI tab detailing farming routes, rewards, durations, loadouts, and directions."""

    def __init__(self) -> None:
        super().__init__()
        self.engine = RouteEngine()

        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(10, 10, 10, 10)

        # Left Panel: Filters & Route List
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)

        self.header = QLabel("Optimized Tactical Routes")
        self.header.setStyleSheet("font-size: 16px; font-weight: bold; color: #00a3cc; margin-bottom: 5px;")
        left_layout.addWidget(self.header)

        # Zone Filter
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Zone Filter:"))
        self.zone_combo = QComboBox()
        self.zone_combo.addItems(["All", "Zariman", "Steel Path", "Archon Hunt", "Arbitration"])
        self.zone_combo.currentTextChanged.connect(self.load_routes)
        filter_layout.addWidget(self.zone_combo)
        left_layout.addLayout(filter_layout)

        # Route List
        self.route_list = QListWidget()
        self.route_list.currentTextChanged.connect(self.show_details)
        left_layout.addWidget(self.route_list)

        self.layout.addWidget(left_widget, 1)

        # Right Panel: Route Details
        self.details_box = QGroupBox("Route Implementation Details")
        self.details_layout = QVBoxLayout(self.details_box)
        self.details_layout.setContentsMargins(5, 5, 5, 5)

        self.details_browser = QTextBrowser()
        self.details_browser.setStyleSheet("""
            QTextBrowser {
                background-color: #0f1724;
                border: 1px solid rgba(255, 255, 255, 0.05);
                color: #e6eef6;
                padding: 15px;
                font-size: 13px;
                line-height: 1.5;
            }
        """)
        self.details_layout.addWidget(self.details_browser)
        self.layout.addWidget(self.details_box, 2)

        self.setLayout(self.layout)
        self.load_routes()

    def load_routes(self) -> None:
        self.route_list.clear()
        player = PlayerLoader().load_player()
        routes = self.engine.evaluate_routes(player)
        zone_filter = self.zone_combo.currentText()

        self.loaded_routes_cache = {}
        for r in routes:
            if zone_filter != "All" and r["zone"] != zone_filter:
                continue
            
            status_symbol = "✔" if r["unlocked"] else "🔒"
            item_text = f"[{r['zone']}] {r['name']} {status_symbol}"
            item = QListWidgetItem(item_text)
            self.route_list.addItem(item)
            self.loaded_routes_cache[r["name"]] = r

        if self.route_list.count() > 0:
            self.route_list.setCurrentRow(0)

    def show_details(self, item_text: str) -> None:
        if not item_text:
            self.details_browser.clear()
            return

        # Find the route from cache
        route = None
        for name, r in self.loaded_routes_cache.items():
            if name in item_text:
                route = r
                break

        if not route:
            self.details_browser.clear()
            return

        status_style = "color: #22c55e; font-weight: bold;" if route["unlocked"] else "color: #ef4444; font-weight: bold;"
        status_text = "UNLOCKED" if route["unlocked"] else "LOCKED"
        
        lock_info = ""
        if not route["unlocked"]:
            lock_info = f"<p style='color: #ef4444;'><b>Lock Reasons:</b><br>" + "<br>".join(f"- {reason}" for reason in route["lock_reasons"]) + "</p>"

        directions_list = "".join(f"<li>{step}</li>" for step in route["node_directions"])

        html_content = f"""
            <h2 style='color: #00a3cc; margin-top: 0; margin-bottom: 5px;'>{route['name']}</h2>
            <p style='margin-top: 0;'><b>Zone:</b> {route['zone']} | <b>Status:</b> <span style='{status_style}'>{status_text}</span></p>
            <hr style='border: 1px solid rgba(255,255,255,0.05); margin-bottom: 15px;'>
            <table style='width: 100%; margin-bottom: 15px;'>
                <tr>
                    <td><b>Reward Payout:</b></td>
                    <td>{route['reward']}</td>
                </tr>
                <tr>
                    <td><b>Efficiency Score:</b></td>
                    <td><span style='color: #caa3ff; font-weight: bold;'>{route['efficiency_score']}/10</span></td>
                </tr>
                <tr>
                    <td><b>Est. Duration:</b></td>
                    <td>{route['estimated_duration_mins']} mins</td>
                </tr>
                <tr>
                    <td><b>Recommended Loadout:</b></td>
                    <td><i>{route['recommended_loadout']}</i></td>
                </tr>
            </table>
            {lock_info}
            <h3>Node Directions & Steps:</h3>
            <ol style='padding-left: 20px; line-height: 1.6;'>
                {directions_list}
            </ol>
        """
        self.details_browser.setHtml(html_content)
