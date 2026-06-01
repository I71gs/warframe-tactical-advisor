from src.core.player_loader import (
    PlayerLoader
)


class BuildAdvisor:

    def recommend_for_weapon(
        self,
        weapon_name
    ):

        player = (
            PlayerLoader()
            .load_player()
        )

        owned_mods = {
            mod.lower()
            for mod in player.owned_mods
        }

        recommendations = []

        if (
            "galvanized chamber"
            not in owned_mods
        ):

            recommendations.append(
                "Farm Galvanized Chamber"
            )

        if (
            "galvanized aptitude"
            not in owned_mods
        ):

            recommendations.append(
                "Farm Galvanized Aptitude"
            )

        return recommendations