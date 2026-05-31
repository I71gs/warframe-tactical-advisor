from src.models.player import Player
from src.core.recommendation_engine import RecommendationEngine


def main():

    player = Player(
        mastery_rank=10,
        completed_quests=["The New War"],
        owned_mods=[],
        steel_path_unlocked=False
    )

    engine = RecommendationEngine()

    recommendation = engine.get_next_best_action(player)

    print("\nNEXT BEST ACTION\n")

    print(f"Action: {recommendation['action']}")
    print(f"Reason: {recommendation['reason']}")
    print(f"Priority: {recommendation['priority']}/100")


if __name__ == "__main__":
    main()