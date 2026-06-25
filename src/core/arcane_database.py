DEFAULT_ARCANES = [
    {
        "name": "Primary Merciless",
        "type": "Primary",
        "acquisition": "Arbitrations / Zariman rewards",
        "importance": 95
    },
    {
        "name": "Secondary Merciless",
        "type": "Secondary",
        "acquisition": "Arbitrations / Zariman rewards",
        "importance": 94
    },
    {
        "name": "Primary Deadhead",
        "type": "Primary",
        "acquisition": "Bounties / Eidolon Pools",
        "importance": 90
    },
    {
        "name": "Molt Augmented",
        "type": "Utility",
        "acquisition": "Event / Rewards",
        "importance": 85
    },
    {
        "name": "Arcane Energize",
        "type": "Support",
        "acquisition": "Bounties / Vendors",
        "importance": 88
    }
]

try:
    from src.core.data_loader import load_json
    json_arcanes = load_json('data/arcanes.json')
    arcanes_map = {a["name"].lower(): a for a in json_arcanes}
    ARCANES = []
    for da in DEFAULT_ARCANES:
        name_lower = da["name"].lower()
        if name_lower in arcanes_map:
            merged = da.copy()
            merged.update(arcanes_map[name_lower])
            ARCANES.append(merged)
        else:
            ARCANES.append(da)
    da_names = {da["name"].lower() for da in DEFAULT_ARCANES}
    for ja in json_arcanes:
        if ja["name"].lower() not in da_names:
            ARCANES.append(ja)
except Exception:
    ARCANES = DEFAULT_ARCANES
