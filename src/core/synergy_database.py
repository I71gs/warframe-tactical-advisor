from __future__ import annotations
from typing import Any

SYNERGIES = {
    ("Wisp", "Phenmor"): {
        "rating": "Excellent",
        "score": 95,
        "rationale": "Haste Reservoir provides massive fire rate boost, greatly accelerating Phenmor's Incarnon charge rate."
    },
    ("Saryn", "Torid"): {
        "rating": "Excellent",
        "score": 98,
        "rationale": "Toxic Lash spreads Spores instantly. Torid's beam status application synergizes perfectly with Saryn's status scaling."
    },
    ("Mesa", "Laetum"): {
        "rating": "Good",
        "score": 85,
        "rationale": "Shooting Gallery buffs secondary damage, and Laetum's rapid status burst benefits from secondary fire rate."
    },
    ("Volt", "Phenmor"): {
        "rating": "Excellent",
        "score": 92,
        "rationale": "Electric Shield increases critical damage multiplier, while Speed buff improves reload speeds."
    },
    ("Mirage", "Kuva Bramma"): {
        "rating": "Excellent",
        "score": 94,
        "rationale": "Hall of Mirrors clones copy the area-of-effect arrows, creating absolute carpet-bombing coverage."
    }
}

class SynergyDatabase:
    """Stores and retrieves synergy relations between specific Warframes and weapons."""

    def get_synergy(self, warframe: str, weapon: str) -> dict[str, Any]:
        """Looks up synergy details between a Warframe and a weapon."""
        pair = (warframe.strip(), weapon.strip())
        # Try both title cases
        for (wf, wp), data in SYNERGIES.items():
            if wf.lower() == pair[0].lower() and wp.lower() == pair[1].lower():
                return data
                
        # Default fallback
        return {
            "rating": "Average",
            "score": 60,
            "rationale": "Standard loadout combination. No specific synergistic ability scaling found."
        }
