class RecommendationEngine:

    def get_next_best_action(self, player):

        if not player.steel_path_unlocked:
            return {
                "action": "Unlock Steel Path",
                "reason": "Access to endgame content and better rewards.",
                "priority": 95
            }

        if "Galvanized Chamber" not in player.owned_mods:
            return {
                "action": "Farm Arbitrations",
                "reason": "Unlock powerful Galvanized Mods.",
                "priority": 90
            }

        return {
            "action": "Optimize Build",
            "reason": "General account improvement.",
            "priority": 50
        }