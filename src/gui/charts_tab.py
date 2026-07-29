from __future__ import annotations
from typing import Any
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox
from src.core.player_loader import PlayerLoader
from src.core.progression_engine import ProgressionEngine
from src.core.weapon_database import WEAPONS
from src.gui.widgets.custom_charts import RadarChartWidget, LineChartWidget, PieChartWidget, BarChartWidget

class ChartsTab(QWidget):
    """GUI tab embedding custom Qt-native widgets to display progression timelines, radar metrics, and inventories."""

    def __init__(self) -> None:
        super().__init__()
        self.layout = QVBoxLayout()
        self.header = QLabel("Performance & Progression Charts")
        self.header.setStyleSheet("font-size: 14px; font-weight: bold; color: #00a3cc; margin-bottom: 5px;")
        self.layout.addWidget(self.header)
        
        self.chart_selector = QComboBox()
        self.chart_selector.addItems([
            "Radar Chart: Progression Sub-scores",
            "Line Chart: Historical Account Strength",
            "Pie Chart: Weapon Inventory Collections",
            "Line Chart: Mastery Rank Growth",
            "Bar Chart: Daily Quest Activity",
            "Line Chart: Relic Unlocks & Crafting"
        ])
        self.chart_selector.currentTextChanged.connect(self.render_selected_chart)
        self.layout.addWidget(self.chart_selector)
        
        self.canvas_container = QWidget()
        self.canvas_layout = QVBoxLayout()
        self.canvas_container.setLayout(self.canvas_layout)
        self.layout.addWidget(self.canvas_container)
        
        self.setLayout(self.layout)
        self.render_selected_chart()

    def render_selected_chart(self) -> None:
        # Clear existing canvas widgets
        for i in reversed(range(self.canvas_layout.count())):
            w = self.canvas_layout.itemAt(i).widget()
            if w:
                w.deleteLater()
                
        player = PlayerLoader().load_player()
        pe = ProgressionEngine()
        
        # Ensure we record a snapshot of the player's current scores for history
        pe.record_progress_snapshot(player)
        
        selected = self.chart_selector.currentText()
        
        if "Radar Chart" in selected:
            categories = ['Story', 'Mods', 'Arcanes', 'Weapons', 'Mastery', 'Unlocks', 'Builds']
            values = [
                pe.get_story_score(player),
                pe.get_mod_score(player),
                pe.get_arcane_score(player),
                pe.get_weapon_score(player),
                pe.get_mastery_score(player),
                pe.get_unlock_score(player),
                pe.get_build_score(player)
            ]
            widget = RadarChartWidget(self)
            widget.set_data(categories, [{"name": "Progression Sub-scores", "values": values, "color": "#00a3cc"}])
            self.canvas_layout.addWidget(widget)
            
        elif "Historical Account Strength" in selected:
            from src.core.statistics_engine_v2 import StatisticsEngineV2
            stats_engine = StatisticsEngineV2()
            growth_data = stats_engine.get_growth_data(player)
            if not growth_data:
                lbl = QLabel("No history snapshots saved yet.")
                lbl.setStyleSheet("color: #9fb6c8; font-size: 12px;")
                self.canvas_layout.addWidget(lbl)
                return
                
            dates = [s["date"] for s in growth_data]
            scores = [s["readiness"] for s in growth_data]
            series = [{"name": "Historical Strength", "values": scores, "color": "#caa3ff"}]
            
            # Growth Curve Projection
            try:
                from src.core.prediction_engine import PredictionEngine
                pred_engine = PredictionEngine()
                pred = pred_engine.predict_milestones(player)
                growth_rate = pred["daily_growth_rate"]
                
                last_date = dates[-1]
                last_score = scores[-1]
                
                proj_dates = []
                proj_scores = [None] * (len(scores) - 1) + [last_score]
                for offset in [5, 10, 15, 20]:
                    proj_dates.append(f"+{offset}d")
                    proj_scores.append(min(100.0, last_score + offset * growth_rate))
                    
                x_labels = dates + proj_dates
                series[0]["values"] = scores + [None] * len(proj_dates)
                series.append({"name": "Projected Future", "values": proj_scores, "color": "#00a3cc", "projection": True})
            except Exception:
                x_labels = dates
                
            widget = LineChartWidget(self)
            widget.set_data(x_labels, series)
            self.canvas_layout.addWidget(widget)
            
        elif "Mastery Rank Growth" in selected:
            from src.core.history_engine import HistoryEngine
            he = HistoryEngine()
            trends = he.get_growth_trends()
            mr_data = trends.get("mr", [])
            if not mr_data:
                lbl = QLabel("No history snapshots saved yet.")
                lbl.setStyleSheet("color: #9fb6c8; font-size: 12px;")
                self.canvas_layout.addWidget(lbl)
                return
                
            dates = [item["date"] for item in mr_data]
            values = [item["value"] / 30 * 100 for item in mr_data]
            
            widget = LineChartWidget(self)
            widget.set_data(dates, [{"name": "Mastery Rank Completion", "values": values, "color": "#00a3cc"}])
            self.canvas_layout.addWidget(widget)
            
        elif "Daily Quest Activity" in selected:
            from src.core.history_engine import HistoryEngine
            he = HistoryEngine()
            trends = he.get_growth_trends()
            quest_data = trends.get("quest_activity", [])
            if not quest_data:
                lbl = QLabel("No history snapshots saved yet.")
                lbl.setStyleSheet("color: #9fb6c8; font-size: 12px;")
                self.canvas_layout.addWidget(lbl)
                return
                
            dates = [item["date"] for item in quest_data]
            values = [float(item["value"]) for item in quest_data]
            
            widget = BarChartWidget(self)
            widget.set_data(dates, values)
            self.canvas_layout.addWidget(widget)
            
        elif "Relic Unlocks" in selected:
            from src.core.history_engine import HistoryEngine
            he = HistoryEngine()
            trends = he.get_growth_trends()
            relic_data = trends.get("relic_unlocks", [])
            crafting_data = trends.get("build_crafting", [])
            if not relic_data or not crafting_data:
                lbl = QLabel("No history snapshots saved yet.")
                lbl.setStyleSheet("color: #9fb6c8; font-size: 12px;")
                self.canvas_layout.addWidget(lbl)
                return
                
            dates = [item["date"] for item in relic_data]
            relic_vals = [float(item["value"]) for item in relic_data]
            craft_vals = [float(item["value"]) for item in crafting_data]
            
            max_val = max(relic_vals + craft_vals) if relic_vals or craft_vals else 1.0
            if max_val == 0:
                max_val = 1.0
            norm_relic = [r / max_val * 100 for r in relic_vals]
            norm_craft = [c / max_val * 100 for c in craft_vals]
            
            widget = LineChartWidget(self)
            widget.set_data(dates, [
                {"name": "Relic Unlocks", "values": norm_relic, "color": "#22c55e"},
                {"name": "Build Crafting", "values": norm_craft, "color": "#eab308"}
            ])
            self.canvas_layout.addWidget(widget)
            
        else:
            owned_weapons = {w.lower() for w in player.owned_weapons}
            total_meta_weapons = len(WEAPONS)
            owned_count = sum(1 for w in WEAPONS if w["name"].lower() in owned_weapons)
            missing_count = total_meta_weapons - owned_count
            
            widget = PieChartWidget(self)
            widget.set_data(["Owned", "Missing"], [owned_count, missing_count])
            self.canvas_layout.addWidget(widget)
