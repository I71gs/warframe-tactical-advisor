DEFAULT_WEAPONS = [
    {
        "name": "Phenmor",
        "type": "Primary",
        "acquisition": "Zariman rewards",
        "meta_rating": 95,
        "category": "Rifle"
    },
    {
        "name": "Laetum",
        "type": "Secondary",
        "acquisition": "Zariman rewards",
        "meta_rating": 95,
        "category": "Pistol"
    },
    {
        "name": "Felarx",
        "type": "Primary",
        "acquisition": "Quest / Trade",
        "meta_rating": 90,
        "category": "Rifle"
    },
    {
        "name": "Torid",
        "type": "Primary",
        "acquisition": "Vendor / Drops",
        "meta_rating": 75,
        "category": "Launcher"
    },
    {
        "name": "Nataruk",
        "type": "Primary",
        "acquisition": "Syndicate / Drops",
        "meta_rating": 80,
        "category": "Bow"
    },
    {
        "name": "Burston Incarnon",
        "type": "Primary",
        "acquisition": "Incarnon Content",
        "meta_rating": 82,
        "category": "Rifle"
    },
    {
        "name": "Latron Incarnon",
        "type": "Primary",
        "acquisition": "Incarnon Content",
        "meta_rating": 83,
        "category": "Rifle"
    },
    {
        "name": "Kuva Bramma",
        "type": "Primary",
        "acquisition": "Kuva Fortress / Kuva Lyric",
        "meta_rating": 92,
        "category": "Bow"
    },
    {
        "name": "Kuva Nukor",
        "type": "Secondary",
        "acquisition": "Kuva Siphon / Kuva missions",
        "meta_rating": 91,
        "category": "Pistol"
    },
    {
        "name": "Lex Prime",
        "type": "Secondary",
        "acquisition": "Relic / Prime Vault",
        "meta_rating": 78,
        "category": "Pistol"
    },
    {
        "name": "Glaive Prime",
        "type": "Melee",
        "acquisition": "Relic / Prime Vault",
        "meta_rating": 88,
        "category": "Thrown Melee"
    }
]

try:
    from src.core.data_loader import load_json
    json_weapons = load_json('data/weapons.json')
    weapons_map = {w["name"].lower(): w for w in json_weapons}
    WEAPONS = []
    for dw in DEFAULT_WEAPONS:
        name_lower = dw["name"].lower()
        if name_lower in weapons_map:
            merged = dw.copy()
            merged.update(weapons_map[name_lower])
            WEAPONS.append(merged)
        else:
            WEAPONS.append(dw)
    dw_names = {dw["name"].lower() for dw in DEFAULT_WEAPONS}
    for jw in json_weapons:
        if jw["name"].lower() not in dw_names:
            WEAPONS.append(jw)
except Exception:
    WEAPONS = DEFAULT_WEAPONS