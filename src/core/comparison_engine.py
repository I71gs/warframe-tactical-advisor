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

        # 9-Dimension Comparison
        dims = self._calculate_dimensions(p1, p2, res1, res2)
        diff_report["dimensions"] = dims

        # Overall recommendation
        diff_report["overall_recommendation"] = self._generate_recommendation(name1, name2, score1, score2, dims)

        return diff_report

    def _calculate_dimensions(self, p1: Player, p2: Player, r1: dict, r2: dict) -> dict[str, dict[str, float]]:
        """Calculates ratings (1-100) across 9 dimensions for both profiles."""
        # Simple heuristic scoring based on player profiles
        
        # 1. Damage (based on weapons and arcanes)
        dmg1 = min(100, 20 + len(p1.owned_weapons) * 5 + len(p1.owned_arcanes) * 10)
        dmg2 = min(100, 20 + len(p2.owned_weapons) * 5 + len(p2.owned_arcanes) * 10)

        # 2. Status (based on mods)
        status1 = min(100, 10 + len(p1.owned_mods) * 4)
        status2 = min(100, 10 + len(p2.owned_mods) * 4)

        # 3. Slash weighting (mods + weapon count)
        slash1 = min(100, 15 + len(p1.owned_mods) * 2 + len(p1.owned_weapons) * 2)
        slash2 = min(100, 15 + len(p2.owned_mods) * 2 + len(p2.owned_weapons) * 2)

        # 4. Ammo (flat baseline adjusted slightly by weapons)
        ammo1 = min(100, 50 + len(p1.owned_weapons) * 2)
        ammo2 = min(100, 50 + len(p2.owned_weapons) * 2)

        # 5. AoE (weapon count factor)
        aoe1 = min(100, 30 + len(p1.owned_weapons) * 3)
        aoe2 = min(100, 30 + len(p2.owned_weapons) * 3)

        # 6. Steel Path score
        sp1 = 100 if p1.steel_path_unlocked else (p1.mastery_rank * 3)
        sp2 = 100 if p2.steel_path_unlocked else (p2.mastery_rank * 3)

        # 7. Boss score (Quest completions + Arcanes)
        boss1 = min(100, len(p1.completed_quests) * 8 + len(p1.owned_arcanes) * 10)
        boss2 = min(100, len(p2.completed_quests) * 8 + len(p2.owned_arcanes) * 10)

        # 8. Survivability synergy (Helminth + Arbitrations)
        surv1 = 40 + (30 if p1.helminth_unlocked else 0) + (30 if p1.arbitrations_unlocked else 0)
        surv2 = 40 + (30 if p2.helminth_unlocked else 0) + (30 if p2.arbitrations_unlocked else 0)

        # 9. Ease of farming (total resources owned metric)
        farm1 = min(100, sum(int(v) for v in r1.values() if str(v).isdigit()) // 1000 + 10)
        farm2 = min(100, sum(int(v) for v in r2.values() if str(v).isdigit()) // 1000 + 10)

        return {
            "Damage":                  {"p1": dmg1, "p2": dmg2},
            "Status":                  {"p1": status1, "p2": status2},
            "Slash Weighting":         {"p1": slash1, "p2": slash2},
            "Ammo Efficiency":         {"p1": ammo1, "p2": ammo2},
            "AoE Potential":           {"p1": aoe1, "p2": aoe2},
            "Steel Path Readiness":    {"p1": sp1, "p2": sp2},
            "Boss Encounter Capacity": {"p1": boss1, "p2": boss2},
            "Survivability Synergy":   {"p1": surv1, "p2": surv2},
            "Farming Resource Base":   {"p1": farm1, "p2": farm2},
        }

    def _generate_recommendation(self, name1: str, name2: str, score1: float, score2: float, dims: dict) -> str:
        if abs(score1 - score2) < 5:
            return "Both accounts have highly comparable progression. Recommend profile optimization based on individual weapon setups."
        stronger = name1 if score1 > score2 else name2
        weaker = name2 if score1 > score2 else name1
        
        # Find biggest gaps
        gaps = []
        for d, vals in dims.items():
            diff = abs(vals["p1"] - vals["p2"])
            gaps.append((d, diff))
        gaps.sort(key=lambda x: x[1], reverse=True)
        top_gap = gaps[0][0]

        return f"Account '{stronger}' is overall stronger. Profile '{weaker}' should focus on upgrading '{top_gap}' to close the readiness gap."
