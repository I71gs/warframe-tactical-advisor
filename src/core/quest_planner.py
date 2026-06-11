from typing import Any
from src.core.quest_graph import QuestGraph

class QuestPlanner:
    """Class QuestPlanner documentation."""

    def get_roadmap(self, player: Any) -> Any:
        """Method get_roadmap."""
        graph = QuestGraph()
        completed = set(player.completed_quests)
        roadmap = []
        for quest in graph.dependencies.keys():
            if quest not in completed and graph.is_unlocked(quest, completed):
                roadmap.append(f'NEXT: {quest}')
                break
        started = False
        for quest in graph.dependencies.keys():
            if roadmap:
                next_quest = roadmap[0].replace('NEXT: ', '')
                if quest == next_quest:
                    started = True
            if started and quest not in completed and (quest != next_quest):
                roadmap.append(f'LATER: {quest}')
        return roadmap