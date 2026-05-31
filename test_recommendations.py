from src.models.player import Player
from src.core.recommendation_engine import RecommendationEngine
from src.core.scoring_engine import ScoringEngine


def main():

    player = Player(
        mastery_rank=10,
        completed_quests=["The New War"],
        owned_mods=[],
        steel_path_unlocked=False
    )

    recommendation_engine = RecommendationEngine()
    scoring_engine = ScoringEngine()

    recommendations = recommendation_engine.generate_recommendations(player)

    scored = []

    for rec in recommendations:

        score = scoring_engine.calculate_score(rec)

        scored.append({
            "recommendation": rec,
            "score": score
        })

    scored.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    print("\nTOP RECOMMENDATIONS\n")

    for index, item in enumerate(scored, start=1):

        print(
            f"{index}. "
            f"{item['recommendation'].action} "
            f"(Score: {item['score']})"
        )


if __name__ == "__main__":
    main()