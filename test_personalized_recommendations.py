from src.core.player_loader import PlayerLoader
from src.core.recommendation_engine import RecommendationEngine
from src.core.scoring_engine import ScoringEngine

player = PlayerLoader().load_player()

recommendation_engine = RecommendationEngine()
scoring_engine = ScoringEngine()

recommendations = (
    recommendation_engine.generate_recommendations(player)
)

scored = []

for recommendation in recommendations:

    score = scoring_engine.calculate_score(
        recommendation
    )

    scored.append(
        (recommendation, score)
    )

scored.sort(
    key=lambda x: x[1],
    reverse=True
)

for recommendation, score in scored:

    print(
        f"{recommendation.action} "
        f"(Score: {score})"
    )