from src.models.recommendation import Recommendation
from src.core.scoring_engine import ScoringEngine


def main():

    rec = Recommendation(
        action="Farm Arbitrations",
        reason="Unlock Galvanized Mods",
        power_gain=95,
        account_progress=90,
        time_efficiency=70
    )

    engine = ScoringEngine()

    score = engine.calculate_score(rec)

    print("Recommendation:", rec.action)
    print("Score:", score)


if __name__ == "__main__":
    main()