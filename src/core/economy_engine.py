from __future__ import annotations
from typing import Any
from src.core.resource_engine import ResourceEngine

TARGET_ECONOMY = {
    "Credits": {"target": 2500000, "rate_per_hr": 250000, "source": "Profit-Taker / Index"},
    "Endo": {"target": 120000, "rate_per_hr": 8000, "source": "Arbitrations / Arena"},
    "Kuva": {"target": 50000, "rate_per_hr": 15000, "source": "Kuva Survival / Siphons"},
    "Steel Essence": {"target": 100, "rate_per_hr": 12, "source": "SP Incursions & Acolytes"},
    "Vitus Essence": {"target": 80, "rate_per_hr": 15, "source": "Arbitrations"},
    "Voidplumes": {"target": 50, "rate_per_hr": 8, "source": "Zariman Bounties"},
    "Entrati Lanthorns": {"target": 20, "rate_per_hr": 3, "source": "Zariman Bounties & Distillers"}
}

class EconomyEngine:
    """Calculates overall account currency requirements, deficits, and farming times."""

    def get_economy_plan(self) -> list[dict[str, Any]]:
        re = ResourceEngine()
        owned = re.load_owned_resources()
        
        plan = []
        for currency, stats in TARGET_ECONOMY.items():
            req = stats["target"]
            # Map key names to possible capitalization variations in resource inventory
            key_name = currency
            if currency == "Entrati Lanthorns":
                key_name = "Entrati Lanthorn"
            elif currency == "Voidplumes":
                key_name = "Voidplumes"
                
            own_qty = owned.get(key_name, 0)
            missing = max(0, req - own_qty)
            
            # Calculate hours to farm
            farm_hours = round(missing / stats["rate_per_hr"], 1) if missing > 0 else 0.0
            
            plan.append({
                "currency": currency,
                "required": req,
                "owned": own_qty,
                "missing": missing,
                "farm_hours": farm_hours,
                "source": stats["source"]
            })
        return plan
