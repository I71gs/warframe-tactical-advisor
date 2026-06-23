from __future__ import annotations
import math
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox
from PySide6.QtCore import Qt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from src.core.player_loader import PlayerLoader
from src.core.progression_engine import ProgressionEngine
from src.core.cache_manager import CacheManager
from src.core.weapon_database import WEAPONS

class ChartsTab(QWidget):
    """GUI tab embedding matplotlib figures to display progression timelines, radar metrics, and inventories."""

    def __init__(self) -> None:
        super().__init__()
        self.layout = QVBoxLayout()
        self.header = QLabel("Performance & Progression Charts")
        self.header.setStyleSheet("font-size: 14px; font-weight: bold; color: #00a3cc;")
        self.layout.addWidget(self.header)
        
        self.chart_selector = QComboBox()
        self.chart_selector.addItems([
            "Radar Chart: Progression Sub-scores",
            "Line Chart: Historical Account Strength",
            "Pie Chart: Weapon Inventory Collections"
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
            fig = self._draw_radar_chart(player, pe)
        elif "Line Chart" in selected:
            fig = self._draw_line_chart()
        else:
            fig = self._draw_pie_chart(player)
            
        canvas = FigureCanvas(fig)
        self.canvas_layout.addWidget(canvas)

    def _draw_radar_chart(self, player: Any, pe: Any) -> Figure:
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
        
        N = len(categories)
        values += values[:1]
        angles = [n / float(N) * 2 * math.pi for n in range(N)]
        angles += angles[:1]
        
        fig = Figure(facecolor='#0b1220')
        ax = fig.add_subplot(111, polar=True)
        ax.set_facecolor('#0f1724')
        ax.set_theta_offset(math.pi / 2)
        ax.set_theta_direction(-1)
        
        # Set tick colors and grid colors
        ax.set_rgrids([20, 40, 60, 80, 100], color='#2a384e')
        ax.set_thetagrids([n / float(N) * 360 for n in range(N)], categories, color='#e6eef6')
        
        ax.plot(angles, values, color='#00a3cc', linewidth=2, linestyle='solid')
        ax.fill(angles, values, color='#00a3cc', alpha=0.25)
        ax.set_ylim(0, 100)
        ax.tick_params(colors='#9fb6c8', grid_color='#2a384e')
        
        ax.spines['polar'].set_color('#2a384e')
        return fig

    def _draw_line_chart(self) -> Figure:
        cm = CacheManager()
        history = cm.load_cache("history").get("data", {})
        snapshots = history.get("snapshots", [])
        
        fig = Figure(facecolor='#0b1220')
        ax = fig.add_subplot(111)
        ax.set_facecolor('#0f1724')
        
        if not snapshots:
            ax.text(0.5, 0.5, "No history snapshots saved yet.", color='#9fb6c8', ha='center', va='center')
            ax.set_axis_off()
            return fig
            
        dates = [s["date"] for s in snapshots]
        scores = [s["readiness"] for s in snapshots]
        
        # Style grid & labels
        ax.plot(dates, scores, marker='o', color='#caa3ff', linewidth=2, label="Historical Strength")
        
        # Growth Curve Projection
        try:
            from src.core.prediction_engine import PredictionEngine
            from src.core.player_loader import PlayerLoader
            pe = PredictionEngine()
            player = PlayerLoader().load_player()
            pred = pe.predict_milestones(player)
            growth_rate = pred["daily_growth_rate"]
            
            last_date = dates[-1]
            last_score = scores[-1]
            
            proj_dates = [last_date]
            proj_scores = [last_score]
            for offset in [5, 10, 15, 20]:
                proj_dates.append(f"+{offset}d")
                proj_scores.append(min(100.0, last_score + offset * growth_rate))
                
            ax.plot(proj_dates, proj_scores, linestyle='--', marker='x', color='#00a3cc', linewidth=1.5, label="Projected Future")
        except Exception:
            pass
            
        ax.set_title("Progression Performance & Future Projection", color='#e6eef6')
        ax.set_ylabel("Readiness Score (%)", color='#9fb6c8')
        ax.set_ylim(0, 105)
        ax.legend(facecolor='#0f1724', edgecolor='#2a384e', labelcolor='#e6eef6')
        
        # Rotate dates on X axis for better display
        fig.autofmt_xdate()
        ax.tick_params(colors='#9fb6c8')
        ax.grid(True, color='#2a384e', linestyle='--')
        
        for side in ['top', 'right', 'bottom', 'left']:
            ax.spines[side].set_color('#2a384e')
            
        return fig

    def _draw_pie_chart(self, player: Any) -> Figure:
        owned_weapons = {w.lower() for w in player.owned_weapons}
        total_meta_weapons = len(WEAPONS)
        owned_count = sum(1 for w in WEAPONS if w["name"].lower() in owned_weapons)
        missing_count = total_meta_weapons - owned_count
        
        fig = Figure(facecolor='#0b1220')
        ax = fig.add_subplot(111)
        ax.set_facecolor('#0f1724')
        
        if total_meta_weapons == 0:
            ax.text(0.5, 0.5, "No meta weapons loaded in database.", color='#9fb6c8', ha='center', va='center')
            ax.set_axis_off()
            return fig
            
        labels = ['Owned', 'Missing']
        sizes = [owned_count, missing_count]
        colors = ['#22c55e', '#ef4444'] # Green vs Red
        
        wedges, texts, autotexts = ax.pie(
            sizes,
            labels=labels,
            autopct='%1.1f%%',
            startangle=90,
            colors=colors,
            textprops=dict(color='#e6eef6')
        )
        
        # Keep labels styled nicely
        for text in texts:
            text.set_color('#9fb6c8')
            
        ax.set_title("Meta Weapons Collection Status", color='#e6eef6')
        return fig
