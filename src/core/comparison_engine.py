from __future__ import annotations
from typing import Any
from src.core.save_manager import SaveManager
from src.database.database import DatabaseManager
from src.models.player import Player
from src.core.progression_engine import ProgressionEngine
from src.core.resource_engine import ResourceEngine

class ComparisonEngine:
    """Runs differential analyses between two account profiles."""

    def load_player_profile(self, name: str) -> Player:
        sm = SaveManager()
        db_path = sm.get_profile_db_path(name)
        db = DatabaseManager(db_path=db_path)
        
        # Load player attributes manually to construct Player object
        player_row = db.get_player()
        mastery_rank = 1
        steel_path_unlocked = False
        arbitrations_unlocked = False
        helminth_unlocked = False
        if player_row:
            mastery_rank, steel_path_unlocked_val, arbitrations_unlocked_val, helminth_unlocked_val = player_row[:4]
            steel_path_unlocked = bool(steel_path_unlocked_val)
            arbitrations_unlocked = bool(arbitrations_unlocked_val)
            helminth_unlocked = bool(helminth_unlocked_val)

        player = Player(
            mastery_rank=mastery_rank,
            steel_path_unlocked=steel_path_unlocked,
            arbitrations_unlocked=arbitrations_unlocked,
            helminth_unlocked=helminth_unlocked,
            completed_quests=db.get_completed_quests(),
            owned_mods=db.get_owned_mods(),
            owned_arcanes=db.get_owned_arcanes(),
            owned_weapons=db.get_owned_weapons(),
        )
        db.connection.close()
        return player

    def compare_profiles(self, name1: str, name2: str) -> dict[str, Any]:
        p1 = self.load_player_profile(name1)
        p2 = self.load_player_profile(name2)

        pe = ProgressionEngine()
        score1 = pe.get_readiness_score(p1)
        score2 = pe.get_readiness_score(p2)

        # 1. Quests comparison
        q1 = set(q.lower() for q in p1.completed_quests)
        q2 = set(q.lower() for q in p2.completed_quests)
        
        # 2. Mods comparison
        m1 = set(m.lower() for m in p1.owned_mods)
        m2 = set(m.lower() for m in p2.owned_mods)

        # 3. Arcanes comparison
        a1 = set(a.lower() for a in p1.owned_arcanes)
        a2 = set(a.lower() for a in p2.owned_arcanes)

        # 4. Weapons comparison
        w1 = set(w.lower() for w in p1.owned_weapons)
        w2 = set(w.lower() for w in p2.owned_weapons)

        # 5. Resources comparison
        sm = SaveManager()
        re1 = ResourceEngine(state_path=sm.profiles_dir / name1 / 'resource_state.json')
        re2 = ResourceEngine(state_path=sm.profiles_dir / name2 / 'resource_state.json')
        res1 = re1.load_owned_resources()
        res2 = re2.load_owned_resources()

        # Build differential details
        diff_report = {
            "profile1": {
                "name": name1,
                "mastery": p1.mastery_rank,
                "readiness": score1,
                "steel_path": p1.steel_path_unlocked
            },
            "profile2": {
                "name": name2,
                "mastery": p2.mastery_rank,
                "readiness": score2,
                "steel_path": p2.steel_path_unlocked
            },
            "differentials": {
                "mastery_diff": p2.mastery_rank - p1.mastery_rank,
                "readiness_diff": round(score2 - score1, 1),
                "quests_p1_only": list(q1 - q2),
                "quests_p2_only": list(q2 - q1),
                "mods_p1_only": list(m1 - m2),
                "mods_p2_only": list(m2 - m1),
                "arcanes_p1_only": list(a1 - a2),
                "arcanes_p2_only": list(a2 - a1),
                "weapons_p1_only": list(w1 - w2),
                "weapons_p2_only": list(w2 - w1),
            },
            "resources": {}
        }

        # Compare resources keys
        all_resources = set(res1.keys()).union(set(res2.keys()))
        for r in all_resources:
            qty1 = res1.get(r, 0)
            qty2 = res2.get(r, 0)
            diff_report["resources"][r] = {
                "p1_qty": qty1,
                "p2_qty": qty2,
                "diff": qty2 - qty1
            }

        # Strength rankings: return names ordered by higher readiness score
        rankings = [name1, name2] if score1 >= score2 else [name2, name1]
        diff_report["strength_rankings"] = rankings

        return diff_report
