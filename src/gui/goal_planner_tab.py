from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QListWidget,
    QComboBox,
    QListWidgetItem
)
from PySide6.QtGui import QColor

from src.core.player_loader import (
    PlayerLoader
)
from src.core.goal_planner import (
    GoalPlanner
)
from src.core.farming_planner import (
    FarmingPlanner
)
from src.core.dependency_engine import (
    DependencyEngine
)
from src.core.goal_cost_engine import (
    GoalCostEngine
)

class GoalPlannerTab(QWidget):

    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout()
        self.layout.addWidget(
            QLabel("Goal Checklist")
        )

        self.goal_selector = QComboBox()
        self.goal_selector.addItems([
            "Unlock Steel Path",
            "Become Archon Ready",
            "Reach Endgame",
            "Finish Main Story"
        ])

        self.cost_label = QLabel()
        self.cost_label.setStyleSheet("padding: 8px; background: rgba(0, 163, 204, 0.05); border: 1px solid rgba(255,255,255,0.06); border-radius: 4px;")

        self.plan_list = QListWidget()

        self.layout.addWidget(
            self.goal_selector
        )
        self.layout.addWidget(
            self.cost_label
        )
        self.layout.addWidget(
            self.plan_list
        )

        self.layout.addWidget(
            QLabel("Optimized Farming Path")
        )
        self.farm_list = QListWidget()
        self.layout.addWidget(
            self.farm_list
        )

        self.setLayout(
            self.layout
        )

        self.goal_selector.currentTextChanged.connect(
            self.load_plan
        )
        
        self.load_plan()

    def load_plan(self):
        self.plan_list.clear()
        self.farm_list.clear()

        player = (
            PlayerLoader()
            .load_player()
        )

        planner = GoalPlanner()
        goal = (
            self.goal_selector.currentText()
        )

        # Update Goal Cost metrics header
        gce = GoalCostEngine()
        cost = gce.calculate_cost(player, goal)
        cost_text = (
            f"<b>Goal:</b> {goal}<br>"
            f"<b>Time Required:</b> {cost['time']}<br>"
            f"<b>Difficulty:</b> {cost['difficulty']}<br>"
            f"<b>Prerequisites:</b> {cost['prerequisites']}<br>"
            f"<b>Estimated Gain:</b> {cost['power_gain']}"
        )
        self.cost_label.setText(cost_text)

        steps = planner.get_goal_plan(
            player,
            goal
        )

        for index, s in enumerate(
            steps,
            start=1
        ):
            status = " [✓] (Completed)" if s["completed"] else " [☐] (Todo)"
            text = f"Step {index}: {s['step']}{status}"
            if s["unmet"]:
                text += f" - Prerequisites: {', '.join(s['unmet'])}"
                
            item = QListWidgetItem(text)
            
            if s["completed"]:
                item.setForeground(QColor("#22c55e")) # Green
            else:
                if s["unmet"]:
                    item.setForeground(QColor("#ff7b7b")) # Red / Missing dependencies
                else:
                    item.setForeground(QColor("#ffb76b")) # Orange / Todo, but unlocked
                    
            self.plan_list.addItem(item)

        # Populate Optimized Farming Path
        fp = FarmingPlanner()
        de = DependencyEngine()
        farm_steps = fp.generate_farming_path(player, goal)

        if farm_steps:
            for index, step in enumerate(farm_steps, start=1):
                text = f"Farm {index}: Acquire {step['item']} from {step['source']} ({step['time']})"
                unmet = de.get_unmet_dependencies(step['item'], player)
                if unmet:
                    text += f" - 🔒 Locked: Needs {', '.join(unmet)}"
                else:
                    text += " - 🔓 Ready to Farm!"

                item = QListWidgetItem(text)
                if unmet:
                    item.setForeground(QColor("#9fb6c8")) # Gray out locked targets
                else:
                    item.setForeground(QColor("#6fffe8")) # Teal for ready-to-farm targets
                self.farm_list.addItem(item)
        else:
            self.farm_list.addItem("No pending farming steps required for this goal! ✓")